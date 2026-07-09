from setuptools import setup, find_packages

setup(
    name="file-metadata-extractor",
    version="1.0.0",
    description="Extract comprehensive metadata from various file types",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "Pillow>=10.1.0",
        "python-magic>=0.4.27",
        "mutagen>=1.47.0",
        "pypdf>=3.15.4",
        "python-docx>=0.8.11",
        "openpyxl>=3.1.2",
        "python-pptx>=0.6.21",
    ],
    extras_require={
        'video': ['ffmpeg-python>=0.2.0'],
        'full': ['ffmpeg-python>=0.2.0']
    },
    entry_points={
        'console_scripts': [
            'metadata-extractor=main:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
