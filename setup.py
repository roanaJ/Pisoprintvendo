from setuptools import setup, find_packages

setup(
    name="pisoprint",
    version="0.1.0",
    description="A PDF printing kiosk system with coin payment functionality",
    author="IM 311 Team",
    author_email="support@pisoprint.com",
    packages=find_packages(),
    install_requires=[
        "Pillow>=9.4.0",
        "PyMuPDF>=1.21.1",
        "pyserial>=3.5",
        "pywin32>=305; platform_system=='Windows'",
        "tk>=0.1.0"
    ],
    entry_points={
        'console_scripts': [
            'pisoprint=src.main:main',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business",
    ],
    include_package_data=True,
    package_data={
        "": ["assets/*.png", "assets/*.ico"],
    },
)