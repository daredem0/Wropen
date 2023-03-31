import subprocess

import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

version = subprocess.run(["git", "describe"], capture_output=True, text=True)

setuptools.setup(
    name="wropen",
    version=version.stdout,
    author="Florian Leuze",
    author_email="f.leuze@outlook.de",
    description="Minimal package to intercept Popen.communicate.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
