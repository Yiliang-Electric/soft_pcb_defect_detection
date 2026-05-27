# Soft PCB Defect Detection

## How to Run

This project provides two main functions:

1. **Data collection using Basler camera**
2. **Soft PCB defect detection using YOLO model**

---

---

## 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```


## 2. Install Required Packages

```bash
pip install -r requirements.txt
```

If you are using a Basler camera, install `pypylon`:

```bash
pip install pypylon
```
---

## 3. Check Basler Camera Connection

Before running the Python file, open **Basler pylon Viewer** and confirm that the camera is detected.

For GigE cameras, make sure:

* The camera and PC are connected through Ethernet
* The camera IP address is configured correctly
* The camera is visible in pylon Viewer
* The live image can be displayed in pylon Viewer

---

## 4. Run Data Collection

Use this command when you want to capture PCB images for training or testing:

```bash
python data_capture.py
```

After running the file, the Basler camera live window will open.

### Keyboard Controls

| Key   | Function                       |
| ----- | ------------------------------ |
| `c`   | Capture and save current image |
| `ESC` | Exit the program               |

Captured images will be saved inside:

```text
data_collection/
```

Example:

```text
data_collection/17162.png
```
---

## 5. Run Defect Detection

Make sure your trained YOLO model file is placed inside the project folder.

Example:

```text
best.pt
```

Then run:

```bash
python soft_pcb_defect.py
```

### Keyboard Controls

| Key   | Function                       |
| ----- | ------------------------------ |
| `s`   | save detected image |
| `ESC` | Exit the program               |

Captured images will be saved inside:

```text
detection_results/
```

The system will:

1. Open the Basler camera
2. Capture real-time PCB images
3. Run YOLO defect detection
4. Detect defect types
5. Display results with segmentation and labels

---

## 6. Expected Detection Classes

The system detects defect types such as:

* Smears
* Bleed out
* Voids
* Dewetted / Peeling
* Debris

---

## 7. Exit the Program

To stop the program, press:

```text
ESC
```

or close the display window.

---

## 8. Troubleshooting

### Basler Camera Not Detected

Open pylon Viewer and check if the camera is visible.

For GigE cameras, check network configuration:

```bash
ip addr
```

Make sure the camera and PC are in the same IP range.

---

### pypylon Import Error

If you get this error:

```text
ModuleNotFoundError: No module named 'pypylon'
```

Install pypylon:

```bash
pip install pypylon
```

---

### YOLO Model Not Found

If the model file is missing, check the project folder:

```bash
ls
```

Make sure the model file exists:

```text
best.pt
```

If your model file has another name, update the model path inside `soft_pcb_defect.py`.

Example:

```python
model = YOLO("best.pt")
```

---

### Low Detection Accuracy

Possible reasons:

* Poor lighting condition
* Camera is not focused correctly
* PCB position is not stable
* Training dataset is too small
* Defects are not clearly annotated
* Model was trained with insufficient defect examples

```
```
