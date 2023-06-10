# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open("README.md") as f:
    long_description = f.read()


setup(
    name="prestashop",
    version="0.1.0",
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
    keywords=['prestashop','e-com','e-commerce','prestashop api','api']
)
