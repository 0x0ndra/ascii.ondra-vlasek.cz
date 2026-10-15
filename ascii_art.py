#!/usr/bin/env python3
"""
ASCII Photo Mask Generator
Create stunning ASCII art where photos shine through character-shaped masks.
"""

import sys
import random
import argparse
import platform
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont, ImageEnhance

# Only decode common photo formats (exotic decoders such as PSD or FITS have a history of memory bugs)
ALLOWED_FORMATS = ("JPEG", "PNG", "WEBP")
# Pillow refuses images above 2x this value (decompression bomb protection)
Image.MAX_IMAGE_PIXELS = 25_000_000
# Output limits: keep a single render well below the service memory limit
MAX_OUTPUT_PIXELS = 40_000_000
MAX_CHAR_ROWS = 600


class ImageTooLargeError(ValueError):
    """Requested output exceeds the allowed size."""


def restrict_decoders() -> None:
    """Limit Pillow process-wide to ALLOWED_FORMATS, also for code that calls Image.open without formats."""
    Image.init()
    Image.ID[:] = [fmt for fmt in Image.ID if fmt in ALLOWED_FORMATS]


class CharacterSets:
    """Collection of Unicode character sets for different visual styles."""

    # Default ASCII set (darkest to lightest)
    ASCII_STANDARD = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

    # Block characters (darkest to lightest)
    BLOCKS = "█▓▒░ "

    # Box drawing characters
    BOX_DRAWING = "╋╬╪╫┼═║│─┌┐└┘├┤┬┴╔╗╚╝╠╣╦╩ "

    # Cyrillic (Russian alphabet)
    CYRILLIC = "ЖФЮЯБВГДЕЁЗИЙКЛМНОПРСТУХЦЧШЩЪЫЬЭ "

    # Chinese characters (selected for visual variety)
    CHINESE = "龍鳳馬書畫花山水木林森田目耳手足心月日星雲雨風雪 "

    # Japanese Hiragana
    HIRAGANA = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん "

    # Japanese Katakana
    KATAKANA = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン "

    # Mathematical symbols
    MATH = "∮∯∰∱∲∳∫∬∭∑∏∐√∛∜∝∞∟∠∡∢∴∵∶∷ "

    # Arrows
    ARROWS = "⇐⇑⇒⇓⇔⇕⇖⇗⇘⇙←↑→↓↔↕↖↗↘↙↚↛↜↝↞↟↠↡↢↣ "

    # Geometric shapes (darkest to lightest)
    SHAPES = "●◆■▲▼◀▶◉◈◇○◊□△▽◁▷☆★ "

    # Playing cards
    CARDS = "♠♣♥♦ "

    # Music notes
    MUSIC = "♪♫♬♭♮♯𝄞𝄢𝄡𝄠 "

    # Stars and sparkles
    STARS = "✦✧✨✩✪✫✬✭✮✯✰★☆⋆∗∘∙ "

    @staticmethod
    def get_all_sets() -> dict:
        """
        Get all available character sets.

        Returns:
            Dictionary mapping set names to character strings
        """
        return {
            "ascii": CharacterSets.ASCII_STANDARD,
            "blocks": CharacterSets.BLOCKS,
            "box": CharacterSets.BOX_DRAWING,
            "cyrillic": CharacterSets.CYRILLIC,
            "chinese": CharacterSets.CHINESE,
            "hiragana": CharacterSets.HIRAGANA,
            "katakana": CharacterSets.KATAKANA,
            "math": CharacterSets.MATH,
            "arrows": CharacterSets.ARROWS,
            "shapes": CharacterSets.SHAPES,
            "cards": CharacterSets.CARDS,
            "music": CharacterSets.MUSIC,
            "stars": CharacterSets.STARS,
        }

    @staticmethod
    def get_set_description(name: str) -> str:
        """Get human-readable description of a character set."""
        descriptions = {
            "ascii": "Standard ASCII characters (default)",
            "blocks": "Unicode block elements █▓▒░",
            "box": "Box-drawing characters ╔═╗║",
            "cyrillic": "Cyrillic alphabet АБВГД",
            "chinese": "Chinese characters 龍鳳馬",
            "hiragana": "Japanese Hiragana あいうえお",
            "katakana": "Japanese Katakana アイウエオ",
            "math": "Mathematical symbols ∫∑∏√",
            "arrows": "Arrow symbols ←↑→↓",
            "shapes": "Geometric shapes ●◆■",
            "cards": "Playing card suits ♠♣♥♦",
            "music": "Musical notation ♪♫♬",
            "stars": "Stars and sparkles ✨★☆",
        }
        return descriptions.get(name, name)


@dataclass
class Config:
    """Configuration for ASCII art generation."""

    # Character settings
    char_set: str = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
    charset_name: str = "ascii"  # Name of the character set (for font selection)
    char_width: int = 80
    font_size: int = 25

    # Randomization settings (for organic look)
    random_size_range: Tuple[float, float] = (0.6, 1.4)  # Min/max size multipliers
    random_position_offset: float = 0.15  # Max offset as fraction of font_size
    enable_randomization: bool = True

    # Visual enhancement
    brightness_multiplier: float = 1.8
    contrast_multiplier: float = 1.3

    # Character rendering
    bold_enabled: bool = True
    bold_offset_range: List[int] = None  # Auto-set to [-1, 0, 1]

    # Background
    background_color: str = "black"

    def __post_init__(self):
        """Initialize computed values."""
        if self.bold_offset_range is None:
            self.bold_offset_range = [-1, 0, 1]


class FontManager:
    """Manages font loading with fallback support across platforms."""

    @staticmethod
    def get_font_for_charset(charset_name: str) -> Tuple[Optional[str], dict]:
        """
        Get the optimal font for a specific character set.

        Args:
            charset_name: Name of the character set (e.g., 'chinese', 'hiragana')

        Returns:
            Tuple of (font_path, font_kwargs) or (None, {}) if no font found
        """
        # Special fonts for CJK character sets
        cjk_fonts = {
            "chinese": [
                ("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", {}),
                ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", {}),
            ],
            "hiragana": [
                ("/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf", {}),
                ("/usr/share/fonts/truetype/fonts-japanese-gothic.ttf", {}),
            ],
            "katakana": [
                ("/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf", {}),
                ("/usr/share/fonts/truetype/fonts-japanese-gothic.ttf", {}),
            ],
        }

        # Check if this charset needs a special font
        if charset_name in cjk_fonts:
            for font_path, kwargs in cjk_fonts[charset_name]:
                if Path(font_path).exists():
                    return font_path, kwargs

        # Fall back to default font candidates
        return FontManager.find_available_font()

    @staticmethod
    def get_font_candidates() -> List[Tuple[str, str, dict]]:
        """
        Get platform-specific font candidates.

        Returns:
            List of (name, path, kwargs) tuples
        """
        system = platform.system()

        if system == "Darwin":  # macOS
            return [
                ("Menlo Bold", "/System/Library/Fonts/Menlo.ttc", {"index": 1}),
                ("Arial Bold", "/Library/Fonts/Arial Bold.ttf", {}),
                ("SF Mono", "/System/Library/Fonts/SFNSMono.ttf", {}),
                ("Courier", "/System/Library/Fonts/Courier.ttc", {}),
            ]
        elif system == "Windows":
            return [
                ("Consolas Bold", "C:/Windows/Fonts/consolab.ttf", {}),
                ("Courier New Bold", "C:/Windows/Fonts/courbd.ttf", {}),
                ("Lucida Console", "C:/Windows/Fonts/lucon.ttf", {}),
                ("Arial Bold", "C:/Windows/Fonts/arialbd.ttf", {}),
            ]
        else:  # Linux and others
            return [
                ("DejaVu Sans Mono Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", {}),
                ("Liberation Mono Bold", "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf", {}),
                ("Ubuntu Mono Bold", "/usr/share/fonts/truetype/ubuntu/UbuntuMono-B.ttf", {}),
                ("Courier Bold", "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf", {}),
                # Fallback to user fonts
                (f"User fonts", str(Path.home() / ".local/share/fonts"), {}),
            ]

    @staticmethod
    def find_available_font() -> Tuple[Optional[str], dict]:
        """
        Find first available font from platform-specific candidates.

        Returns:
            Tuple of (font_path, font_kwargs) or (None, {}) if no font found
        """
        for name, path, kwargs in FontManager.get_font_candidates():
            if Path(path).exists():
                return path, kwargs
        return None, {}

    @staticmethod
    def load_fonts(
        base_size: int,
        size_range: Tuple[float, float] = (1.0, 1.0),
        font_path: Optional[str] = None,
        font_kwargs: Optional[dict] = None
    ) -> List[ImageFont.FreeTypeFont]:
        """
        Load multiple font sizes for variation.

        Args:
            base_size: Base font size in pixels
            size_range: Tuple of (min_multiplier, max_multiplier) for size variation
            font_path: Optional specific font path (if None, auto-detect)
            font_kwargs: Optional font kwargs (if None, use empty dict)

        Returns:
            List of loaded fonts (at least one)
        """
        # Use provided font or auto-detect
        if font_path is None:
            font_path, font_kwargs = FontManager.find_available_font()
        elif font_kwargs is None:
            font_kwargs = {}

        if not font_path:
            return [ImageFont.load_default()]

        fonts = []
        min_mult, max_mult = size_range

        # Generate 5 sizes evenly distributed in range
        num_sizes = 5
        for i in range(num_sizes):
            multiplier = min_mult + (max_mult - min_mult) * (i / (num_sizes - 1))
            size = int(base_size * multiplier)

            try:
                fonts.append(ImageFont.truetype(font_path, size, **font_kwargs))
            except Exception:
                continue

        return fonts if fonts else [ImageFont.load_default()]


class ImageProcessor:
    """Handles image loading and preprocessing."""

    @staticmethod
    def load_and_resize(image_path: Path, target_size: Tuple[int, int]) -> Image.Image:
        """
        Load image and resize to target dimensions.

        Args:
            image_path: Path to source image
            target_size: (width, height) tuple

        Returns:
            Resized RGB image
        """
        img = Image.open(image_path, formats=ALLOWED_FORMATS).convert('RGB')
        return img.resize(target_size, Image.Resampling.LANCZOS)

    @staticmethod
    def enhance_image(img: Image.Image, brightness: float, contrast: float) -> Image.Image:
        """
        Enhance image brightness and contrast.

        Args:
            img: Source image
            brightness: Brightness multiplier (1.0 = no change)
            contrast: Contrast multiplier (1.0 = no change)

        Returns:
            Enhanced image
        """
        # Brightness
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(brightness)

        # Contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast)

        return img

    @staticmethod
    def get_average_brightness(img: Image.Image, x: int, y: int, width: int, height: int) -> float:
        """
        Calculate average brightness of image region.

        Args:
            img: Source image
            x, y: Top-left corner of region
            width, height: Region dimensions

        Returns:
            Average brightness (0-255)
        """
        region = img.crop((x, y, x + width, y + height))
        grayscale = region.convert('L')
        pixels = list(grayscale.getdata())
        return sum(pixels) / len(pixels) if pixels else 0


class ASCIIConverter:
    """Converts brightness values to ASCII characters."""

    def __init__(self, char_set: str):
        """
        Initialize converter with character set.

        Args:
            char_set: String of characters from darkest to lightest
        """
        self.char_set = char_set

    def brightness_to_char(self, brightness: float) -> str:
        """
        Convert brightness value to ASCII character.

        Args:
            brightness: Brightness value (0-255)

        Returns:
            Corresponding ASCII character
        """
        index = int((brightness / 255) * (len(self.char_set) - 1))
        index = max(0, min(index, len(self.char_set) - 1))  # Clamp
        return self.char_set[index]


class ASCIIPhotoMask:
    """Main class for generating ASCII photo masks."""

    def __init__(self, config: Config):
        """
        Initialize generator with configuration.

        Args:
            config: Configuration object
        """
        self.config = config
        self.converter = ASCIIConverter(config.char_set)

    def generate(self, input_path: Path, output_path: Optional[Path] = None) -> Image.Image:
        """
        Generate ASCII photo mask art.

        Args:
            input_path: Path to source image
            output_path: Path to save output image (None: only return it)

        Returns:
            Generated image
        """
        # Load source image
        source_img = Image.open(input_path, formats=ALLOWED_FORMATS).convert('RGB')
        img_width, img_height = source_img.size

        # Calculate grid dimensions
        cell_width = img_width / self.config.char_width
        char_height = int((img_height / cell_width))
        if not 1 <= char_height <= MAX_CHAR_ROWS:
            raise ImageTooLargeError(
                f"Unsupported aspect ratio: {char_height} character rows (allowed 1 to {MAX_CHAR_ROWS})"
            )
        cell_height = img_height / char_height

        # Calculate output dimensions
        output_width = self.config.char_width * self.config.font_size
        output_height = char_height * self.config.font_size
        if output_width * output_height > MAX_OUTPUT_PIXELS:
            raise ImageTooLargeError(
                f"Output {output_width}x{output_height} px is too large, "
                "use fewer characters or a smaller character size"
            )

        print(f"Creating ASCII art: {self.config.char_width}x{char_height} characters")
        print(f"Output size: {output_width}x{output_height} pixels")

        # Get appropriate font for this character set
        font_path, font_kwargs = FontManager.get_font_for_charset(self.config.charset_name)

        # Load fonts
        size_range = self.config.random_size_range if self.config.enable_randomization else (1.0, 1.0)
        fonts = FontManager.load_fonts(self.config.font_size, size_range, font_path, font_kwargs)

        # Prepare base image
        img_resized = ImageProcessor.load_and_resize(
            input_path,
            (output_width, output_height)
        )

        # Enhance image
        img_resized = ImageProcessor.enhance_image(
            img_resized,
            self.config.brightness_multiplier,
            self.config.contrast_multiplier
        )

        # Create black background and mask
        output_img = Image.new('RGB', (output_width, output_height), self.config.background_color)
        mask = Image.new('L', (output_width, output_height), 0)
        mask_draw = ImageDraw.Draw(mask)

        # Generate character mask
        for row in range(char_height):
            for col in range(self.config.char_width):
                self._draw_character(
                    source_img, mask_draw, fonts,
                    row, col, cell_width, cell_height,
                    img_width, img_height
                )

            # Progress indicator
            if (row + 1) % 10 == 0:
                print(f"Progress: {row + 1}/{char_height} rows")

        print("Compositing image with character masks...")

        # Composite: show photo only through character mask
        output_img = Image.composite(img_resized, output_img, mask)

        # Save output
        if output_path is not None:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_img.save(output_path)

            print(f"\n✓ ASCII photo art saved to: {output_path}")
            print(f"  View with: open '{output_path}'")

        return output_img

    def _draw_character(
        self,
        source_img: Image.Image,
        mask_draw: ImageDraw.Draw,
        fonts: List[ImageFont.FreeTypeFont],
        row: int,
        col: int,
        cell_width: float,
        cell_height: float,
        img_width: int,
        img_height: int
    ):
        """Draw a single character on the mask."""
        # Get cell position in source image
        x = int(col * cell_width)
        y = int(row * cell_height)

        # Calculate brightness and select character
        brightness = ImageProcessor.get_average_brightness(
            source_img,
            x, y,
            min(int(cell_width), img_width - x),
            min(int(cell_height), img_height - y)
        )
        char = self.converter.brightness_to_char(brightness)

        # Calculate base position in output
        base_x = col * self.config.font_size
        base_y = row * self.config.font_size

        # Apply random offset if enabled
        if self.config.enable_randomization:
            offset_range = int(self.config.font_size * self.config.random_position_offset)
            random_offset_x = random.randint(-offset_range, offset_range)
            random_offset_y = random.randint(-offset_range, offset_range)
            paste_x = base_x + random_offset_x
            paste_y = base_y + random_offset_y
        else:
            paste_x, paste_y = base_x, base_y

        # Select font (random if variation enabled)
        font = random.choice(fonts) if len(fonts) > 1 else fonts[0]

        # Draw character (with bold effect if enabled)
        if self.config.bold_enabled:
            for dx in self.config.bold_offset_range:
                for dy in self.config.bold_offset_range:
                    mask_draw.text((paste_x + dx, paste_y + dy), char, font=font, fill=255)
        else:
            mask_draw.text((paste_x, paste_y), char, font=font, fill=255)


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Generate ASCII photo mask art - photos shining through ASCII characters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s photo.jpg                          # Basic usage with defaults
  %(prog)s photo.jpg -o output.png            # Specify output file
  %(prog)s photo.jpg -w 120 -s 18             # Small detailed characters
  %(prog)s photo.jpg -w 40 -s 55              # Large poster characters
  %(prog)s photo.jpg --no-random              # Disable randomization for perfect grid
  %(prog)s photo.jpg -b 2.0 -c 1.5            # Extra bright and contrasty

Presets:
  Small detailed:  -w 120 -s 18
  Medium:          -w 80 -s 25
  Large poster:    -w 40 -s 55
        """
    )

    # Required arguments
    parser.add_argument(
        'input',
        type=str,
        nargs='?',  # Make optional for --list-charsets
        help='Input image file path'
    )

    # Optional arguments
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output image file path (default: <input>_ascii_art.png)'
    )

    parser.add_argument(
        '-w', '--width',
        type=int,
        default=80,
        help='Number of characters across width (default: 80)'
    )

    parser.add_argument(
        '-s', '--size',
        type=int,
        default=25,
        help='Font size in pixels (default: 25)'
    )

    parser.add_argument(
        '-b', '--brightness',
        type=float,
        default=1.8,
        help='Brightness multiplier (default: 1.8)'
    )

    parser.add_argument(
        '-c', '--contrast',
        type=float,
        default=1.3,
        help='Contrast multiplier (default: 1.3)'
    )

    parser.add_argument(
        '--no-random',
        action='store_true',
        help='Disable randomization for perfect grid layout'
    )

    parser.add_argument(
        '--no-bold',
        action='store_true',
        help='Disable bold effect on characters'
    )

    # Character set selection
    available_sets = list(CharacterSets.get_all_sets().keys())
    parser.add_argument(
        '--charset',
        type=str,
        choices=available_sets,
        help='Character set preset (e.g., blocks, emoji_faces, chinese). Use --list-charsets to see all.'
    )

    parser.add_argument(
        '--list-charsets',
        action='store_true',
        help='List all available character sets with descriptions and exit'
    )

    parser.add_argument(
        '--chars',
        type=str,
        help='Custom character set string (darkest to lightest). Overrides --charset.'
    )

    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Handle --list-charsets
    if args.list_charsets:
        print("Available character sets:\n")
        for name in sorted(CharacterSets.get_all_sets().keys()):
            desc = CharacterSets.get_set_description(name)
            print(f"  {name:20s} - {desc}")
        print("\nUsage: --charset <name>")
        sys.exit(0)

    # Validate input file is provided
    if not args.input:
        print("Error: Input file is required", file=sys.stderr)
        print("Run with --help for usage information", file=sys.stderr)
        sys.exit(1)

    # Validate input file exists
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"{input_path.stem}_ascii_art.png"

    # Create configuration
    config = Config(
        char_width=args.width,
        font_size=args.size,
        brightness_multiplier=args.brightness,
        contrast_multiplier=args.contrast,
        enable_randomization=not args.no_random,
        bold_enabled=not args.no_bold,
    )

    # Set character set (priority: --chars > --charset > default)
    if args.chars:
        config.char_set = args.chars
        # Custom chars use default font (charset_name stays "ascii")
    elif args.charset:
        char_sets = CharacterSets.get_all_sets()
        config.char_set = char_sets[args.charset]
        config.charset_name = args.charset  # Set charset name for font selection
        print(f"Using character set: {args.charset} - {CharacterSets.get_set_description(args.charset)}")

    # Generate ASCII art
    generator = ASCIIPhotoMask(config)

    try:
        generator.generate(input_path, output_path)
    except Exception as e:
        print(f"Error generating ASCII art: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
