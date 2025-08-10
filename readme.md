# OneDark Image Palette Mapper

This Python script recolors an image using a custom OneDark-inspired palette, with special handling for skin tones. It maps each pixel to the nearest palette color using the CIEDE2000 color difference and blends the result for a stylized effect.

## Disclaimer
   
   **This script was generated with assistance from AI (ChatGPT by OpenAI). Please review, test, and adjust parameters as needed before use in production or critical applications.**
   
## Features

- Maps each pixel to the nearest palette color using CIEDE2000 color difference.
- Detects skin tones and uses a separate palette for more natural results.
- Blends original and palette colors for a stylized effect.
- Adjustable blending strength for overall image and skin tones.

## Requirements

- Python 3.7+
- Pillow (`pip install pillow`)

## Usage

1. Install the required package:
    ```bash
    pip install pillow
    ```
2. Run the script from the command line, providing the path to your image:
   ```bash
    python Script.py <path_to_image> [--blend <value>] [--skin-blend <value>]</value></value>    
   ```
   - `<path_to_image>`: Path to your image file.
      - `--blend <value>`: (Optional) Blending strength for non-skin areas (0.0 to 1.0, default: 0.7). Higher values mean more palette influence.
      - `--skin-blend <value>`: (Optional) Blending strength for skin areas (0.0 to 1.0, default: 0.5). Higher values mean more palette influence on skin.
   
      **Example:**
   ```bash
    python Script.py photo.jpg --blend 0.8 --skin-blend 0.4
    ```
   This will process `photo.jpg` with stronger palette effect on non-skin areas and softer effect on skin.
   
3. The processed image will be saved as `OneDark_<original_filename>` in the same directory.
   
   ## Parameters
   
   - `--blend`: Controls how much the palette color affects non-skin pixels. `0.0` means only the original color, `1.0` means only the palette color.
   - `--skin-blend`: Controls how much the palette color affects detected skin pixels. Adjust for more natural or more stylized skin tones.
   
  ## License
   
   MIT