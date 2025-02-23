# Pixel Detector

Pixel Detector is a Python tool designed to restore and enhance pixel art images that may have been resized, compressed, or otherwise degraded. It fixes common compression issues (especially from JPEG compression) by reconstructing the original pixel grid and, if desired, reducing the color palette.

### Exaggerated example

![Example](https://github.com/Astropulse/pixeldetector/assets/61034487/f8ae2802-42c1-4dba-af56-fe849ac8915c)

## Updates

With the latest updates, you can now:
- **Select an exact number of colors** using the `--colors` option, which overrides automatic palette detection.
- **Set an exact output resolution** using the `--size` option.

The script supports both opaque and transparent images by preserving the alpha channel throughout processing.

## Features

- **Downscaling & Pixel Restoration:**  
  Automatically detects pixel boundaries using horizontal and vertical differences, or allows you to specify a custom resolution via the `--size` option.
  
- **Color Reduction:**  
  - **Automatic Mode:** Use the `--palette` flag to automatically reduce colors using an elbow method that determines the optimal color count (up to a maximum specified by `--max`).
  - **Manual Mode:** Use the `--colors` option to force a specific number of colors, overriding the automatic palette detection.
  
- **Transparency Support:**  
  The alpha channel is preserved in images with transparency (RGBA), ensuring that transparent areas remain intact.

## Requirements

- Python 3.x
- [Pillow](https://python-pillow.org/)
- [NumPy](https://numpy.org/)
- [SciPy](https://www.scipy.org/)

## Installation

It is recommended to use a virtual environment. For example:

1. Create and activate a virtual environment:
- On Unix/Mac:
 ```
 python -m venv venv
 source venv/bin/activate
 ```
- On Windows:
 ```
 python -m venv venv
 venv\Scripts\activate
 ```
2. Install the required packages:
```
pip install pillow numpy scipy
```

## Usage

Run the script with the required and optional arguments:

```
python pixeldetector.py -i <input_image> [options]
```

### Command-line Arguments

- **-i, --input**  
  *Required*  
  Path to the input image file.  
  Example: `-i input.png`

- **-o, --output**  
  *Optional*  
  Path to save the output image.  
  Default: `output.png`  
  Example: `-o restored.png`

- **-m, --max**  
  *Optional*  
  Maximum number of colors to consider during automatic palette detection (a higher number may slow processing).  
  Default: `128`  
  Example: `-m 200`

- **-p, --palette**  
  *Optional* (flag)  
  Automatically reduce the image’s colors using an elbow method. When this flag is set, the script calculates the optimal number of colors based on image distortion.  
  Example: `-p`

- **-c, --colors**  
  *Optional*  
  Specifies the exact number of colors for the output image. This option overrides the automatic palette reduction if set.  
  Example: `-c 16`

- **-s, --size**  
  *Optional*  
  Desired output dimensions specified as two integers representing width and height. If provided, the image is resized to these dimensions using the kCentroid method.  
  Example: `-s 256 256`

## How It Works

1. **Image Loading and Preparation**  
- The script opens the input image and converts it to RGB or RGBA mode, depending on whether the image has transparency.

2. **Downscaling / Pixel Restoration**  
- **Automatic Detection**  
 If no `--size` argument is provided, the script uses the `pixel_detect` function. It computes horizontal and vertical differences to detect optimal pixel boundaries and downsizes the image accordingly.
- **Custom Resolution:**  
 When the `--size` argument is provided, the image is resized to the specified width and height using the `kCentroid` method.

3. **Color Reduction**  
- **Automatic Palette Reduction:**  
 If the `--palette` flag is used, the script computes distortions for a range of colors (up to the maximum specified by `--max`) and uses an elbow method to determine the best number of colors.
- **Fixed Color Count:**  
 If the `--colors` option is provided, the image is quantized to the exact number of colors specified, overriding the automatic detection.
- **Transparency Handling:**  
 For images with transparency, special care is taken to preserve the alpha channel throughout the quantization process.

4. **Output:**  
- The processed image is saved as an optimized PNG file at the location specified by `--output`.

## Examples

Below are examples demonstrating every possible switch:

### Example 1: Using All Parameters
```
python pixeldetector.py -i input.png -o restored.png -m 150 -p -c 16 -s 512 512
```
*This command opens `input.png`, resizes it to 512x512 pixels, and forces the output to use exactly 16 colors. The maximum number of colors considered for automatic detection is set to 150 (although the `--colors` option takes precedence over `--palette`). The result is saved as `restored.png`.*

### Example 2: Automatic Pixel Detection and Palette Reduction Only
```
python pixeldetector.py -i input.png -o output.png -m 128 -p
```
*This command processes `input.png` using automatic pixel detection (without specifying an exact size) and automatically reduces the color palette using an elbow method with a maximum of 128 colors. The processed image is saved as `output.png`.*

### Example 3: Custom Resolution with Fixed Color Count
```
python pixeldetector.py -i input.png -o output.png -s 300 300 -c 32
```
*This command resizes `input.png` to 300x300 pixels using a custom resolution and forces the image to be quantized to exactly 32 colors. The result is saved as `output.png`.*

### Example 4: Custom Resolution Only
```
python pixeldetector.py -i input.png -o resized.png -s 400 400
```
*This command resizes `input.png` to 400x400 pixels using the kCentroid method for pixel detection. No color reduction is performed, and the output is saved as `resized.png`.*

### Example 5: Fixed Color Count Only
```
python pixeldetector.py -i input.png -o colors.png -c 24
```
*This command processes `input.png` without changing its resolution and forces the output to use exactly 24 colors. The processed image is saved as `colors.png`.*

### Example 6: Running in a Virtual Environment with All Options
```
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install pillow numpy scipy
python pixeldetector.py -i input.png -o output.png -m 200 -p -c 16 -s 512 512
```
*This example demonstrates setting up a virtual environment, installing dependencies, and running the script with every available option.*

## Credits

Special thanks to [Paultron](https://github.com/paultron) for the initial optimization work using NumPy, which greatly improved the performance of the downscaling process.

Test image by Skeddles: [Rock and Grass](https://lospec.com/gallery/skeddles/rock-and-grass)
