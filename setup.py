from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="ascii-photo-mask",
    version="1.1.0",
    author="0x0ndra",
    author_email="ondra.vlasek@gmail.com",
    description="Transform photos into stunning ASCII art where images shine through character-shaped masks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/0x0ndra/ascii-photo-mask",
    py_modules=["ascii_art", "web_interface"],
    python_requires=">=3.7",
    install_requires=[
        "Pillow>=12.3.0",
        "gradio>=6.30.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ascii-photo-mask=ascii_art:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Artistic Software",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="ascii art photo image mask generator",
)
