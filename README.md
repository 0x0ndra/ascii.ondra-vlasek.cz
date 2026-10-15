# ASCII Photo Mask

Transform your photos into stunning ASCII art where the image shines through character-shaped masks on a black background.

<table>
<tr>
<td width="50%">
<img src="examples/example_original.jpg" alt="Original Photo"/>
<p align="center"><b>Original Photo</b></p>
</td>
<td width="50%">
<img src="examples/example_output.png" alt="ASCII Photo Mask Result"/>
<p align="center"><b>ASCII Photo Mask Result</b></p>
</td>
</tr>
</table>

## Features

- **Beautiful Web Interface**: Drag-and-drop UI with real-time preview (Gradio-powered)
- **Photo-Through-Characters**: Unlike traditional ASCII art converters that output text, this creates actual images where your photo is visible only through ASCII character shapes
- **Cross-Platform**: Works on macOS, Linux, and Windows with automatic font detection
- **Configurable Everything**: Control character size, density, brightness, contrast, and more
- **Organic Randomization**: Optional character size variation and position jitter for a hand-crafted look
- **Bold Characters**: Thick, prominent characters for better visibility
- **Multiple Presets**: From highly detailed small characters to large poster-style output
- **Clean Code**: Zero hardcoded paths, following DRY, KISS, and LEGO principles

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/0x0ndra/ascii-photo-mask.git
cd ascii-photo-mask

# Install dependencies
pip install -r requirements.txt
```

### Web Interface (Recommended)

Launch the web UI with drag-and-drop interface:

```bash
python web_interface.py
```

Then open your browser at `http://localhost:7860`

**Features:**
- Drag & drop image upload
- Interactive sliders for all settings
- Quick preset buttons (Detailed, Medium, Bold)
- Real-time preview
- Download results directly

### Command Line

```bash
# Generate ASCII art with default settings
python ascii_art.py photo.jpg

# Specify output file
python ascii_art.py photo.jpg -o output.png

# Small detailed characters
python ascii_art.py photo.jpg -w 120 -s 18

# Large poster-style characters
python ascii_art.py photo.jpg -w 40 -s 55

# Disable randomization for perfect grid
python ascii_art.py photo.jpg --no-random

# Adjust brightness and contrast
python ascii_art.py photo.jpg -b 2.0 -c 1.5
```

## Usage

```
usage: ascii_art.py [-h] [-o OUTPUT] [-w WIDTH] [-s SIZE] [-b BRIGHTNESS]
                    [-c CONTRAST] [--no-random] [--no-bold] [--chars CHARS]
                    input

Generate ASCII photo mask art - photos shining through ASCII characters

positional arguments:
  input                 Input image file path

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output image file path (default: <input>_ascii_art.png)
  -w WIDTH, --width WIDTH
                        Number of characters across width (default: 80)
  -s SIZE, --size SIZE  Font size in pixels (default: 25)
  -b BRIGHTNESS, --brightness BRIGHTNESS
                        Brightness multiplier (default: 1.8)
  -c CONTRAST, --contrast CONTRAST
                        Contrast multiplier (default: 1.3)
  --no-random           Disable randomization for perfect grid layout
  --no-bold             Disable bold effect on characters
  --chars CHARS         Custom character set (darkest to lightest)
```

## Presets

| Style | Parameters | Description |
|-------|------------|-------------|
| **Small Detailed** | `-w 120 -s 18` | High detail, many small characters |
| **Medium** | `-w 80 -s 25` | Balanced detail and visibility (default) |
| **Large Poster** | `-w 40 -s 55` | Bold, poster-style with large characters |
| **Perfect Grid** | `--no-random` | Disable randomization for uniform layout |
| **Clean Thin** | `--no-bold` | Thinner characters without bold effect |

## How It Works

Unlike traditional ASCII art generators that convert images to text files, ASCII Photo Mask creates a visual image file where:

1. **Black Background**: The output starts with a pure black canvas
2. **Character Mask**: ASCII characters are positioned based on image brightness
   - Dark areas → Dense characters (like `@`, `#`, `W`)
   - Light areas → Sparse characters (like `.`, `:`, `'`)
3. **Photo Shine-Through**: The original photo is visible ONLY through the character shapes
4. **Randomization** (optional): Character sizes and positions vary slightly for an organic, hand-crafted appearance

**Technical Flow:**
```
Input Image → Brightness Analysis → Character Selection → Mask Generation → Photo Compositing → Output PNG
```

## Architecture

The codebase follows SOLID principles with clear separation of concerns:

- **`Config`**: Dataclass for all configuration parameters
- **`FontManager`**: Font discovery and loading with fallback support
- **`ImageProcessor`**: Image loading, resizing, and enhancement
- **`ASCIIConverter`**: Brightness-to-character mapping
- **`ASCIIPhotoMask`**: Main generation orchestrator

### Design Principles

- **DRY** (Don't Repeat Yourself): No code duplication
- **LEGO**: Modular, composable components
- **KISS** (Keep It Simple, Stupid): Clean, readable code
- **Zero Hardcoded Paths**: All paths are discovered dynamically or configurable
- **Type Hints**: Full type annotations for better IDE support
- **Docstrings**: Comprehensive documentation for all public APIs

## Requirements

- Python 3.7+
- Pillow (PIL)
- Gradio (for web interface)

See `requirements.txt` for exact versions.

### Supported Platforms

- **macOS**: Uses system fonts (Menlo, SF Mono, Courier)
- **Linux**: Uses DejaVu Sans Mono, Liberation Mono, or Ubuntu Mono
- **Windows**: Uses Consolas, Courier New, or Lucida Console

The tool automatically detects your platform and selects appropriate fonts. If no system fonts are found, it falls back to PIL's default font.

## Examples

### Different Character Sizes

<table>
<tr>
<td width="50%">
<img src="examples/example_output.png" alt="Medium characters (80x25)"/>
<p align="center"><b>Medium (80x25)</b><br/>
<code>python ascii_art.py photo.jpg -w 80 -s 25</code></p>
</td>
<td width="50%">
<img src="examples/example_detailed.png" alt="Small detailed characters (120x18)"/>
<p align="center"><b>Small Detailed (120x18)</b><br/>
<code>python ascii_art.py photo.jpg -w 120 -s 18</code></p>
</td>
</tr>
</table>

### More Examples

**Large Poster (40x55)**
Bold, eye-catching characters perfect for posters
```bash
python ascii_art.py photo.jpg -w 40 -s 55
```

**Perfect Grid (No Randomization)**
Clean, uniform character placement
```bash
python ascii_art.py photo.jpg --no-random
```

## Advanced Usage

### Custom Character Set

Use your own characters (from darkest to lightest):
```bash
python ascii_art.py photo.jpg --chars "█▓▒░ "
```

### Maximum Brightness

For very dark photos:
```bash
python ascii_art.py photo.jpg -b 2.5 -c 1.8
```

### Minimalist Look

Thin characters, no randomization:
```bash
python ascii_art.py photo.jpg --no-bold --no-random
```

## Tips

- **For portraits**: Use medium to large characters (40-80 width)
- **For landscapes**: Smaller characters work better (100-120 width)
- **Dark photos**: Increase brightness (`-b 2.0` or higher)
- **Low contrast photos**: Increase contrast (`-c 1.5` or higher)
- **Poster prints**: Use large characters (40-60 width, 50-60 size)

## Troubleshooting

**Characters too small/large?**
- Adjust `-w` (width) and `-s` (size) together
- Lower width = fewer, larger characters
- Higher width = more, smaller characters

**Photo too dark?**
- Increase brightness: `-b 2.0` or higher
- Increase contrast: `-c 1.5`

**Characters overlapping?**
- Disable randomization: `--no-random`
- Or reduce character width: `-w 60`

**Output file not created?**
- Check input file exists
- Ensure output directory is writable
- Check error messages in console

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Inspired by classic ASCII art but with a modern, visual twist. Built with Python and Pillow.

---

**Live Demo**: [ascii.ondra-vlasek.cz](https://ascii.ondra-vlasek.cz) (deployment: [DEPLOYMENT.md](DEPLOYMENT.md), self-hosting: [DEPLOYMENT.example.md](DEPLOYMENT.example.md))

**Created by**: [0x0ndra](https://github.com/0x0ndra)
