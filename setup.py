#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modernized safe setup.py for a UFONet-style research toolkit.
Paste this file as setup.py at the repository root.

NOTES (read before running):
- This is a packaging file only. It does NOT escalate privileges, run apt-get,
  or auto-install system packages.
- Always install inside a virtual environment or container:
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install .
- This project is intended for lawful research, education, and testing on
  systems you own or where you have explicit permission. Do NOT use it to
  target third-party infrastructure without consent.
"""
from pathlib import Path
from setuptools import setup, find_packages

# Basic metadata
NAME = "ufonet_reborn"
VERSION = "0.1.0"
DESCRIPTION = "UFONet Reborn — modernized research/stress-testing toolkit (for private use)"
AUTHOR = "You"
AUTHOR_EMAIL = "you@example.com"
LICENSE = "GPL-3.0-or-later"
PYTHON_REQUIRES = ">=3.10"

# Minimal, maintained dependencies. Keep this list conservative and audited.
# Replace or remove packages you don't actually use.
INSTALL_REQUIRES = [
    "requests>=2.28",
    "scapy>=2.5; platform_system!='Windows'",
    "python-whois>=0.7",
    "pycryptodome>=3.18",
    "duckduckgo-search>=2.6",
]

# Read long description from README if present
README = Path(__file__).with_name("README.md")
long_description = README.read_text(encoding="utf-8") if README.exists() else (
    DESCRIPTION + "\n\n" +
    "IMPORTANT: This software is intended for lawful research and testing only. "
    "Do not use it to attack or disrupt systems you do not own or have explicit permission to test."
)

# Classifiers (helpful metadata)
CLASSIFIERS = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Operating System :: OS Independent",
    "Topic :: Security :: Testing",
]

# Entry points: console script 'ufonet' will call ufonet.cli:main
# Make sure your package contains ufonet/cli.py with a safe main() function.
ENTRY_POINTS = {
    "console_scripts": [
        "ufonet=ufonet.cli:main",
    ],
}

# Setup call
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    python_requires=PYTHON_REQUIRES,
    packages=find_packages(exclude=("tests", "docs", "examples")),
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    entry_points=ENTRY_POINTS,
    classifiers=CLASSIFIERS,
    zip_safe=False,
)
