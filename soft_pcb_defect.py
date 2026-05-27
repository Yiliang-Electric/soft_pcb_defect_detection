import numpy as np
import cv2
import time
from pypylon import pylon
from pypylon import genicam
from ultralytics import YOLO
import os


# Use this only for Basler camera emulator.
# If you are using a real Basler camera, comment this line.
# os.environ["PYLON_CAMEMU"] = "3"

maxCamerasToUse = 1
exitCode = 0

MODEL_PATH = "model/best.pt"
CONF_THRESHOLD = 0.25


class ObjectDetection():
    def __init__(self):

        # Load YOLO segmentation model
        self.model = YOLO(MODEL_PATH)

        self.tlFactory = pylon.TlFactory.GetInstance()

        # Get all attached devices
        devices = self.tlFactory.EnumerateDevices()

        if len(devices) == 0:
            raise pylon.RuntimeException("No camera present.")

        # Create camera array
        self.cameras = pylon.InstantCameraArray(
            min(len(devices), maxCamerasToUse)
        )

        # Create and attach all Pylon devices
        for i, cam in enumerate(self.cameras):

            cam.Attach(self.tlFactory.CreateDevice(devices[i]))

            self.converter = pylon.ImageFormatConverter()
            self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
            self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

            # Print camera model name
            print("Using device ", cam.GetDeviceInfo().GetModelName())

        self.cameras.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

        self.set_camera_settings()

    def set_camera_settings(self):
        for camera in self.cameras:
            device_info = camera.GetDeviceInfo()
            interface_type = device_info.GetDeviceClass()

            try:
                if interface_type == "BaslerGigE":
                    # Set settings for GigE cameras
                    camera.GainAuto.SetValue("Off")
                    camera.ExposureAuto.SetValue("Off")
                    camera.ExposureTimeAbs.SetValue(3000)
                    camera.GainRaw.SetValue(60)
                    camera.AcquisitionFrameRateEnable.SetValue(True)
                    camera.AcquisitionFrameRateAbs.SetValue(30)

                else:
                    # Set settings for USB cameras
                    camera.GainAuto.SetValue("Off")
                    camera.ExposureAuto.SetValue("Off")
                    camera.ExposureTime.SetValue(3000)
                    camera.Gain.SetValue(10)
                    camera.AcquisitionFrameRateEnable.SetValue(True)
                    camera.AcquisitionFrameRate.SetValue(30)

            except Exception as e:
                print("Camera setting warning:", e)

    def __call__(self):

        os.makedirs("detection_results", exist_ok=True)

        while self.cameras.IsGrabbing():

            grabResult = self.cameras.RetrieveResult(
                5000,
                pylon.TimeoutHandling_ThrowException
            )

            try:
                cameraContextValue = grabResult.GetCameraContext()

                if grabResult.GrabSucceeded():

                    image = self.converter.Convert(grabResult)
                    cameraContextValue = grabResult.GetCameraContext()

                    if cameraContextValue == 0:

                        img = image.GetArray()

                        # Run YOLO segmentation inference
                        results = self.model(img, conf=CONF_THRESHOLD)

                        # Draw only segmentation masks
                        output_img = self.draw_only_masks(img, results)

                        cv2.namedWindow(
                            "PCB Defect Segmentation",
                            cv2.WINDOW_NORMAL
                        )
                        cv2.imshow(
                            "PCB Defect Segmentation",
                            output_img
                        )

                    key = cv2.waitKey(1)

                    # Press "s" to save detection result
                    if key == ord("s"):
                        save_path = f"detection_results/{time.time()}.png"
                        cv2.imwrite(save_path, output_img)
                        print("Saved:", save_path)

                    # Press ESC to exit
                    if key & 0xFF == 27:
                        break

            finally:
                grabResult.Release()

        self.cameras.StopGrabbing()
        cv2.destroyAllWindows()

    def draw_only_masks(self, img, results):
       
        output_img = img.copy()

        for result in results:

            masks = result.masks

            if masks is None:
                return output_img

            mask_data = masks.data.cpu().numpy()

            for mask in mask_data:

                # Resize mask according to original image size
                resized_mask = cv2.resize(
                    mask,
                    (img.shape[1], img.shape[0])
                )

                # Convert mask into binary mask
                binary_mask = resized_mask > 0.5

                # Create overlay
                overlay = output_img.copy()

                # Red color mask region
                overlay[binary_mask] = (0, 0, 255)

                # Blend mask with original image
                output_img = cv2.addWeighted(
                    overlay,
                    0.35,
                    output_img,
                    0.65,
                    0
                )

        return output_img


detector = ObjectDetection()
detector()
