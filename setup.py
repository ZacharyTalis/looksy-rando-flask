#!/usr/bin/env python3

from setuptools import setup

setup(name="looksy-rando-flask",
    version="1.0",
    long_description=__doc__,
    packages=["rando"],
    include_package_data=True,
    zip_safe=False,
    install_requires=["Flask", "Pillow", "Waitress"])
