#!/usr/bin/env python3
"""
ASCII Photo Mask - Web Interface
Professional landing page for ASCII art generation.
"""

import gradio as gr
import os
import base64
from pathlib import Path
from ascii_art import ASCIIPhotoMask, Config, CharacterSets, ImageTooLargeError, restrict_decoders

# Gradio decodes uploads with Pillow itself, so limit the decoders for the whole process
restrict_decoders()


def generate_ascii_art(
    image,
    char_width: int,
    font_size: int,
    brightness: float,
    contrast: float,
    randomize: bool,
    bold: bool,
    charset: str
):
    """
    Generate ASCII photo mask from uploaded image.

    Args:
        image: Uploaded image from Gradio
        char_width: Number of characters across width
        font_size: Size of each character in pixels
        brightness: Brightness multiplier
        contrast: Contrast multiplier
        randomize: Enable randomization for organic look
        bold: Enable bold characters
        charset: Character set name (e.g., 'ascii', 'blocks', 'emoji_faces')

    Returns:
        Generated ASCII art image (PIL), cached by Gradio

    Note:
        Uploaded and returned files live in Gradio's cache, which delete_cache cleans up hourly.
    """
    if image is None:
        return None

    try:
        # Get character set
        char_sets = CharacterSets.get_all_sets()
        char_set = char_sets.get(charset, CharacterSets.ASCII_STANDARD)

        # Create configuration
        config = Config(
            char_width=char_width,
            font_size=font_size,
            brightness_multiplier=brightness,
            contrast_multiplier=contrast,
            enable_randomization=randomize,
            bold_enabled=bold,
            char_set=char_set,
            charset_name=charset,  # Set charset name for font selection
        )

        # Create generator
        generator = ASCIIPhotoMask(config)

        # Generate ASCII art in memory (no extra temp file to clean up)
        return generator.generate(Path(image))

    except ImageTooLargeError as e:
        raise gr.Error(str(e))
    except Exception as e:
        print(f"Error generating ASCII art: {e}")
        return None


# Professional Landing Page CSS
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --primary: #3b82f6;
    --primary-hover: #2563eb;
    --bg: #000000;
    --bg-elevated: #0a0a0a;
    --bg-card: #111111;
    --text: #ffffff;
    --text-muted: #a1a1a1;
    --border: #262626;
    --success: #10b981;
}

* {
    font-family: 'Inter', sans-serif !important;
}

body {
    background: var(--bg) !important;
    color: var(--text) !important;
}

.gradio-container {
    max-width: 1400px !important;
    background: var(--bg) !important;
    padding: 0 !important;
}

/* Hero Section */
.hero {
    text-align: center;
    padding: 3rem 2rem 2rem;
    background: var(--bg);
}

.hero h1 {
    font-size: 2.5rem !important;
    font-weight: 700 !important;
    line-height: 1.2 !important;
    margin: 0 0 1rem !important;
    color: var(--text);
}

.hero .subtitle {
    font-size: 1.125rem;
    color: var(--text-muted);
    max-width: 700px;
    margin: 0 auto;
    line-height: 1.5;
}

/* Step Indicators */
.steps {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
    margin: 2rem auto;
    padding: 0 2rem;
    max-width: 900px;
}

.step {
    text-align: center;
}

.step-number {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--primary);
    color: white;
    font-weight: 600;
    font-size: 1.125rem;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 0.75rem;
}

.step h3 {
    font-size: 1rem !important;
    font-weight: 600 !important;
    margin: 0 0 0.25rem !important;
}

.step p {
    color: var(--text-muted);
    font-size: 0.8125rem;
    margin: 0;
}

/* Main Section */
.main-section {
    padding: 2rem;
}

/* Settings Cards */
.settings-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 0.75rem;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.settings-card h3 {
    font-size: 1rem !important;
    font-weight: 600 !important;
    margin: 0 0 1rem !important;
}

label {
    color: var(--text) !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
}

input[type="range"] {
    accent-color: var(--primary);
}

/* Buttons */
button {
    font-weight: 600 !important;
    border-radius: 0.5rem !important;
    transition: all 0.2s ease !important;
}

.primary {
    background: var(--primary) !important;
    color: white !important;
    padding: 0.875rem 2rem !important;
    font-size: 1rem !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
}

.primary:hover {
    background: var(--primary-hover) !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4) !important;
}

.secondary {
    background: var(--bg-elevated) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    padding: 0.5rem 1rem !important;
}

.secondary:hover {
    background: var(--bg-card) !important;
    border-color: var(--primary) !important;
}

/* Presets */
.preset-buttons {
    display: flex;
    gap: 0.75rem;
    margin: 1rem 0;
}

/* Images */
.image-preview {
    border: 1px solid var(--border);
    border-radius: 0.75rem;
    overflow: hidden;
    background: var(--bg-elevated);
}

/* Accordion */
.accordion {
    background: transparent !important;
    border: none !important;
    margin: 0 !important;
}

/* Footer */
.footer {
    text-align: center;
    padding: 2rem;
    border-top: 1px solid var(--border);
    margin-top: 3rem;
}

.footer p {
    color: var(--text-muted);
    font-size: 0.8125rem;
    margin: 0.25rem 0;
}

.footer a {
    color: var(--primary);
    text-decoration: none;
    transition: color 0.2s;
}

.footer a:hover {
    color: var(--primary-hover);
}

/* Example Gallery - Before/After Slider */
.example-section {
    padding: 2rem 2rem;
    background: var(--bg-elevated);
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
}

.example-section h2 {
    text-align: center;
    font-size: 1.5rem !important;
    margin: 0 0 0.5rem !important;
}

.example-subtitle {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.875rem;
    margin: 0 0 1.5rem;
}

.comparison-container {
    position: relative;
    max-width: 400px;
    margin: 0 auto;
    border-radius: 0.5rem;
    overflow: hidden;
    border: 1px solid var(--border);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.comparison-container input[type="range"] {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
    opacity: 0;
    cursor: ew-resize;
    z-index: 3;
}

.comparison-images {
    position: relative;
    width: 100%;
    display: block;
}

.comparison-before,
.comparison-after {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}

.comparison-before {
    position: relative;
}

.comparison-before img,
.comparison-after img {
    display: block;
    width: 100%;
    height: auto;
}

.comparison-after {
    overflow: hidden;
    clip-path: polygon(0 0, var(--slider-pos, 50%) 0, var(--slider-pos, 50%) 100%, 0 100%);
}

.comparison-divider {
    position: absolute;
    top: 0;
    left: var(--slider-pos, 50%);
    width: 2px;
    height: 100%;
    background: var(--primary);
    transform: translateX(-50%);
    pointer-events: none;
    z-index: 2;
}

.comparison-handle {
    position: absolute;
    top: 50%;
    left: var(--slider-pos, 50%);
    transform: translate(-50%, -50%);
    width: 36px;
    height: 36px;
    background: var(--primary);
    border: 2px solid white;
    border-radius: 50%;
    pointer-events: none;
    z-index: 2;
    display: flex;
    align-items: center;
    justify-content: center;
}

.comparison-handle::before,
.comparison-handle::after {
    content: '';
    position: absolute;
    width: 0;
    height: 0;
    border-style: solid;
}

.comparison-handle::before {
    left: 8px;
    border-width: 5px 7px 5px 0;
    border-color: transparent white transparent transparent;
}

.comparison-handle::after {
    right: 8px;
    border-width: 5px 0 5px 7px;
    border-color: transparent transparent transparent white;
}

/* Creator Footer */
.creator-footer {
    text-align: center;
    padding: 1.5rem;
    background: var(--bg-elevated);
    border-top: 1px solid var(--border);
}

.creator-footer p {
    font-size: 0.8125rem;
    color: var(--text-muted);
    margin: 0 0 0.75rem 0;
}

.creator-footer .creator-name {
    font-weight: 600;
    color: var(--text);
}

.creator-footer .creator-links {
    display: flex;
    gap: 1.25rem;
    justify-content: center;
}

.creator-footer a {
    color: var(--primary);
    text-decoration: none;
    font-size: 0.8125rem;
    transition: color 0.2s;
}

.creator-footer a:hover {
    color: var(--primary-hover);
}

/* Responsive */
@media (max-width: 768px) {
    .hero h1 {
        font-size: 2rem !important;
    }

    .hero .subtitle {
        font-size: 1rem;
    }

    .steps {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }

    .main-section {
        padding: 1rem;
    }
}

/* Hide default Gradio footer */
footer {
    display: none !important;
}
"""

# Get paths to example images and convert to base64
examples_dir = Path(__file__).parent / "examples"
before_img_path = examples_dir / "before.jpeg"
after_img_path = examples_dir / "after.png"

def image_to_base64(image_path: Path) -> str:
    """Convert image file to base64 data URL."""
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    # Determine MIME type
    suffix = image_path.suffix.lower()
    mime_type = 'image/jpeg' if suffix in ['.jpg', '.jpeg'] else f'image/{suffix[1:]}'

    return f"data:{mime_type};base64,{image_data}"

# Convert images to base64
before_img = image_to_base64(before_img_path)
after_img = image_to_base64(after_img_path)

# Create Gradio interface
theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="slate",
    neutral_hue="slate",
).set(
    body_background_fill="#000000",
    button_primary_background_fill="#3b82f6",
)

# delete_cache: every hour remove cached uploads and results older than one hour
with gr.Blocks(title="ASCII Photo Mask - Transform Photos into Art", theme=theme, css=custom_css,
               delete_cache=(3600, 3600)) as demo:

    # Hero Section
    gr.HTML("""
        <div class="hero">
            <h1>ASCII Photo Mask</h1>
            <p class="subtitle">
                Transform your photos into visual art where the image shines through character-shaped masks.
            </p>
        </div>
    """)

    # How it Works
    gr.HTML("""
        <div class="steps">
            <div class="step">
                <div class="step-number">1</div>
                <h3>Upload Your Photo</h3>
                <p>Choose any image — portraits, landscapes, anything you like</p>
            </div>
            <div class="step">
                <div class="step-number">2</div>
                <h3>Customize Settings</h3>
                <p>Adjust character size, brightness, and style options</p>
            </div>
            <div class="step">
                <div class="step-number">3</div>
                <h3>Download Result</h3>
                <p>Get your high-resolution ASCII art ready for printing or sharing</p>
            </div>
        </div>
    """)

    # Interactive Before/After Slider
    gr.HTML("""
        <div class="example-section">
            <h2>See It In Action</h2>
            <p class="example-subtitle">Drag the slider to compare original photo with ASCII art result</p>

            <div class="comparison-container">
                <div class="comparison-images">
                    <div class="comparison-before">
                        <img src="{after_img}" alt="ASCII Art Result" />
                    </div>
                    <div class="comparison-after">
                        <img src="{before_img}" alt="Original Photo" />
                    </div>
                </div>
                <div class="comparison-divider"></div>
                <div class="comparison-handle"></div>
                <input type="range" min="0" max="100" value="50"
                       oninput="this.parentElement.style.setProperty('--slider-pos', this.value + '%')" />
            </div>
        </div>
    """.format(before_img=before_img, after_img=after_img))

    # Main Section
    with gr.Row():
        # Left Column - Upload & Settings
        with gr.Column(scale=1):
            image_input = gr.Image(
                type="filepath",
                label="Upload Photo",
                sources=["upload", "clipboard"],
                elem_classes=["image-preview"]
            )

            # Quick Presets
            gr.Markdown("### Quick Presets")
            with gr.Row():
                preset_detailed = gr.Button("Detailed", size="sm", variant="secondary")
                preset_medium = gr.Button("Medium", size="sm", variant="secondary")
                preset_bold = gr.Button("Bold", size="sm", variant="secondary")

            # Character Style Selection
            gr.Markdown("### Character Style")
            charset_choices = [(CharacterSets.get_set_description(name), name)
                             for name in sorted(CharacterSets.get_all_sets().keys())]
            charset = gr.Dropdown(
                choices=charset_choices,
                value="ascii",
                label="Character Set",
                info="Choose the characters used to create the art"
            )

            # Settings
            with gr.Accordion("Advanced Settings", open=False):
                char_width = gr.Slider(
                    minimum=20,
                    maximum=200,
                    value=80,
                    step=10,
                    label="Character Density",
                    info="More characters = finer detail"
                )

                font_size = gr.Slider(
                    minimum=8,
                    maximum=60,
                    value=25,
                    step=1,
                    label="Character Size",
                    info="Size of each character in pixels"
                )

                brightness = gr.Slider(
                    minimum=1.0,
                    maximum=3.0,
                    value=1.8,
                    step=0.1,
                    label="Brightness",
                    info="Lighter = more visible through characters"
                )

                contrast = gr.Slider(
                    minimum=1.0,
                    maximum=2.0,
                    value=1.3,
                    step=0.1,
                    label="Contrast",
                    info="Higher = more dramatic effect"
                )

                randomize = gr.Checkbox(
                    value=True,
                    label="Organic Look",
                    info="Slightly vary character positions for hand-crafted feel"
                )

                bold = gr.Checkbox(
                    value=True,
                    label="Bold Characters",
                    info="Thicker characters for better visibility"
                )

            # Generate Button
            generate_btn = gr.Button("Generate ASCII Art", variant="primary", size="lg")

        # Right Column - Result
        with gr.Column(scale=1):
            image_output = gr.Image(
                label="Result",
                type="filepath",
                format="png",
                elem_classes=["image-preview"]
            )


            # Tips
            gr.Markdown("""
                ### Tips for Best Results

                **Detailed** — Many small characters (120 density) for fine detail

                **Medium** — Balanced look (60 density) works for most photos

                **Bold** — Large characters (40 density) for striking, poster-like results

                **Dark Photos** — Increase brightness to 2.0+ for better visibility
            """)

    # Preset Handlers
    preset_detailed.click(
        fn=lambda: (120, 18),
        outputs=[char_width, font_size]
    )

    preset_medium.click(
        fn=lambda: (60, 30),
        outputs=[char_width, font_size]
    )

    preset_bold.click(
        fn=lambda: (40, 55),
        outputs=[char_width, font_size]
    )

    # Generate Handler
    generate_btn.click(
        fn=generate_ascii_art,
        inputs=[
            image_input,
            char_width,
            font_size,
            brightness,
            contrast,
            randomize,
            bold,
            charset
        ],
        outputs=image_output
    )

    # Technical Info Footer
    gr.HTML("""
        <div class="footer">
            <p><strong>Algorithm</strong> — Brightness-based character mapping with PIL composite masking</p>
            <p><strong>Privacy</strong> — Files processed server-side, automatically cleaned up periodically</p>
            <p><strong>License</strong> — MIT Open Source</p>
        </div>
    """)

    # Creator Footer
    gr.HTML("""
        <div class="creator-footer">
            <p>Created by <span class="creator-name">0x0ndra</span></p>
            <div class="creator-links">
                <a href="https://ondra-vlasek.cz" target="_blank">Website</a>
                <a href="https://github.com/0x0ndra" target="_blank">GitHub</a>
                <a href="https://github.com/0x0ndra/ascii-photo-mask" target="_blank">Source Code</a>
                <a href="https://github.com/0x0ndra/ascii-photo-mask/issues" target="_blank">Report Issues</a>
                <a href="https://btcpay.rpipay.org/api/v1/invoices?storeId=BwZszjZ5ieW6apLWoKwuh72fkBQjGNN9BjTZmFfB3eH7&currency=USD" target="_blank">Donate</a>
            </div>
        </div>
    """)


if __name__ == "__main__":
    import os
    demo.queue(max_size=20, default_concurrency_limit=1)
    demo.launch(
        share=False,
        server_name=os.getenv("SERVER_HOST", "127.0.0.1"),
        server_port=int(os.getenv("SERVER_PORT", "7860"))
    )
