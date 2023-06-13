# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import codecs
import os.path

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open("README.md") as f:
    long_description = f.read()

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name="prestashop",
    version= get_version('prestashop/version.py'),
    description="Prestashop is a library for Python to interact with the PrestaShop's Web Service API.",
    license="GPLv3",
    author="Aymen Jemi (AISYSNEXT)",
    author_email="jemiaymen@gmail.com",
    url="https://github.com/AiSyS-Next/prestashop",
    packages=find_packages(),
    install_requires=required,
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
    ],
    keywords=['prestashop','e-com','e-commerce','prestashop api','api','webservice']
)
