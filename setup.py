import os

import setuptools

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

VERSION = "0.2.3"
ROOT_DIR = os.path.dirname(__file__)

REQUIREMENTS = [
    line.strip() for line in open(os.path.join(ROOT_DIR, "requirements.txt")).readlines()
]


setuptools.setup(
    name="python-logging",
    version=VERSION,
    author="Asistobe AS",
    include_package_data=True,
    description="Provides common log setup for python projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["asistobe_logsetup"],
    install_requires=REQUIREMENTS,
)
