# CV Detection Dataset Splitter

A handy desktop tool for manually splitting object-detection datasets (in YOLO/Ultralytics format) into training and testing subsets based on your own quality criteria.

![alt text](https://github.com/Ramnck/dataset-splitter/blob/master/image.jpg?raw=true)

## Features

* **Preview with Bounding Boxes**: Quickly verify that labels (in YOLO XYWH relative format) align correctly on images.
* **Custom Split Ratio**: Choose a high-quality percentage or absolute count via a slider and synchronized number input.
* **Interactive Sorting UI**:

  * Previous / Mark-Unmark / Next / Finish buttons beneath the image.
  * Keyboard shortcuts:

    * **A**: Previous image
    * **S**: Mark or unmark current image
    * **D**: Next image
    * **F**: Finish sorting early
  * Progress bar (red) + “X/Y found” status below.
  * “Image X/Y” label showing your position in the dataset.
* **Adaptive Layout**: Window-resizable Tkinter interface; images scale up or down to fill the canvas.
* **Automatic Output**:

  * Marked images and labels → `output_dir/test/{images,labels}`
  * Unmarked images and labels → `output_dir/train/{images,labels}`

## Input Format

The app expects two folders:

```text
project_folder/
├── images/       # JPEG or PNG files
│   ├── img1.jpg
│   └── img2.png
└── labels/       # Corresponding .txt files
    ├── img1.txt
    └── img2.txt
```

Each label file uses YOLO-style lines:

```
<class> <x_center> <y_center> <width> <height>
```

* `<class>`: integer class ID
* `<x_center>, <y_center>, <width>, <height>`: floats \[0.0–1.0], relative to image size

Example (`img1.txt`):

```
0 0.273782 0.728125 0.037123 0.162500
1 0.141531 0.720313 0.037123 0.178125
0 0.180974 0.721875 0.037123 0.175000
2 0.356148 0.731250 0.039443 0.143750
```

## Installation

1. **Requirements**:

   * Python 3.7+
   * [Pillow](https://pypi.org/project/Pillow/)
   * Tkinter (usually included with standard Python)

2. **Install dependencies**:

   ```bash
   pip install Pillow
   ```

3. **Download** this repository and navigate into it.

## Usage

```bash
python main.py
```

1. On the first screen, **browse** to select:

   * Images folder
   * Labels folder
   * Output folder (where `train/` and `test/` subfolders will be created)
2. **Preview** the first image with overlaid boxes to confirm label alignment.
3. Set your **high-quality split** by percentage or absolute count.
4. Click **Start Sorting**.
5. In the sorter UI:

   * Use **Previous / Mark-Unmark / Next / Finish** buttons or keyboard shortcuts.
   * Watch the progress bar and “X/Y found” status.
   * Optionally **Finish early** with the Finish button or **F** key.

Once finished, your `train/` and `test/` folders will be automatically populated.

## License

MIT © Roman
