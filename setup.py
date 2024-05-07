import setuptools

setuptools.setup(
    name="aicar",
    version="1.0.0",
    author="Marcel Egle",
    author_email="info@marcel-egle.de",
    description="AI-Car Toolbox",
    url="https://github.com/check2016",
    packages=['aicar.rccontroller', 'aicar.gps', 'aicar.camera'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)