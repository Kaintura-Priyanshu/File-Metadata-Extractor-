rom pathlib import Path
from setuptools import setup, find_packages

this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text(encoding="utf-8")

setup(
    name="file-metadata-extractor",
    version="1.0.0",
    description="Extract comprehensive metadata from images, documents, audio, and video files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Priyanshu Kaintura",
    url="https://github.com/Kaintura-Priyanshu/File-Metadata-Extractor-",
    packages=find_packages(exclude=("tests", "tests.*")),
    install_requires=[
        "Pillow>=10.1.0",
        "python-magic>=0.4.27",
        "mutagen>=1.47.0",
        "pypdf>=3.15.4",
        "python-docx>=0.8.11",
        "openpyxl>=3.1.2",
        "python-pptx>=0.6.21",
    ],
    entry_points={
        'console_scripts': [
            'metadata-extractor=main:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
    ],
    python_requires='>=3.8',
)
