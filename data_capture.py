import numpy as np
import cv2
import time
from pypylon import pylon
from pypylon import genicam
import os

os.environ["PYLON_CAMEMU"] = "3"

maxCamerasToUse = 1
exitCode = 0


class ObjectDetection:
    def __init__(self):
        self.tlFactory = pylon.TlFactory.GetInstance()

        # Get all attached devices
        devices = self.tlFactory.EnumerateDevices()

        if len(devices) == 0:
            raise pylon.RuntimeException("No camera present.")

        # Create camera array
        self.cameras = pylon.InstantCameraArray(
            min(len(devices), maxCamerasToUse)
        )

        # Attach cameras
        for i, cam in enumerate(self.cameras):
            cam.Attach(self.tlFactory.CreateDevice(devices[i]))

            self.converter = pylon.ImageFormatConverter()
            self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
            self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

            print("Using device:", cam.GetDeviceInfo().GetModelName())

        self.cameras.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

        self.set_camera_settings()

    def set_camera_settings(self):
        for camera in self.cameras:
            device_info = camera.GetDeviceInfo()
            interface_type = device_info.GetDeviceClass()

            if interface_type == "BaslerGigE":
                # Settings for GigE cameras
                camera.GainAuto.SetValue("Off")
                camera.ExposureAuto.SetValue("Off")
                camera.ExposureTimeAbs.SetValue(3000)
                camera.GainRaw.SetValue(60)
                camera.AcquisitionFrameRateEnable.SetValue(True)
                camera.AcquisitionFrameRateAbs.SetValue(30)
            else:
                # Settings for USB cameras
                camera.GainAuto.SetValue("Off")
                camera.ExposureAuto.SetValue("Off")
                camera.ExposureTime.SetValue(3000)
                camera.Gain.SetValue(10)
                camera.AcquisitionFrameRateEnable.SetValue(True)
                camera.AcquisitionFrameRate.SetValue(30)

    def __call__(self):
        os.makedirs("data_collection", exist_ok=True)

        while self.cameras.IsGrabbing():
            grabResult = self.cameras.RetrieveResult(
                5000,
                pylon.TimeoutHandling_ThrowException
            )

            cameraContextValue = grabResult.GetCameraContext()

            if grabResult.GrabSucceeded():
                image = self.converter.Convert(grabResult)

                if cameraContextValue == 0:
                    img = image.GetArray()

                    # Convert image to grayscale for display
                    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                    cv2.namedWindow("PCB Camera capture", cv2.WINDOW_NORMAL)
                    cv2.imshow("PCB Camera capture", gray_img)

                key = cv2.waitKey(1)

                # Press 'c' to capture and save image
                if key == ord("c"):
                    filename = f"data_collection/{time.time()}.png"
                    cv2.imwrite(filename, img)
                    print(f"Image saved: {filename}")

                # Press ESC to exit
                if key & 0xFF == 27:
                    break

            grabResult.Release()

        self.cameras.StopGrabbing()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    detector = ObjectDetection()
    detector()
