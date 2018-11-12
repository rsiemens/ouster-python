import setuptools

import os1

with open("README.md") as f:
    long_desc = f.read()

setuptools.setup(
    name="ouster-os1",
    version=os1.__version__,
    author=os1.__author__,
    author_email=os1.__email__,
    description=os1.__doc__,
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/rsiemens/ouster-python/",
    packages=["os1"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
