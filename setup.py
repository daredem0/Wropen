import subprocess
import re
import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

_version = subprocess.run(["git", "describe"], capture_output=True, text=True)
version = _version.stdout
minmajhash = re.compile(r"(\d+).(\d+).(\d+)")
match = re.search(minmajhash, version)
if match is not None:
    major = match.group(1)
    print(f"Found major: {major}.")
    minor = match.group(2)
    print(f"Found minor: {minor}.")
    patch = match.group(3)
    print(f"Found patch: {patch}.")
parsed_version = f'{major}.{minor}.{patch}'

setuptools.setup(
    name="wropen",
    version=parsed_version,
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
