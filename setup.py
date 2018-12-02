#!/usr/bin/env python3
"""Modbus slave emulator.
Email: yuriy@vlasov.pro
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    url='https://gitlab.com/vlasov-y/modbus-slave-emulator',
    name='modbus-slave',
    version='1.0',
    description='Emulator of Modbus slave - see https://bit.ly/2AHnbHK',
    author='Yuriy Vlasov',
    author_email='yuriy@vlasov.pro',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7'
    ],
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'modbus-slave = main.main:entrypoint',
        ],
    },
    zip_safe=False
)
