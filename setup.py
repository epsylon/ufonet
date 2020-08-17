#!/usr/bin/env python 
# -*- coding: utf-8 -*-"
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2020 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import sys

if sys.version_info[0] != 3:
    sys.exit("Sorry, UFONet requires Python >= 3")
    
from setuptools import setup, find_packages

setup(
    name='ufonet',
    version='1.6',
    license='GPLv3',
    author_email='epsylon@riseup.net',
    author='psy',
    description='Denial of Service Toolkit',
    url='https://ufonet.03c8.net/',
    long_description=open('docs/README.txt').read(),
    packages=find_packages(),
    install_requires=['GeoIP >= 1.3.2', 'python-geoip >= 1.2', 'pygeoip >= 0.3.2', 'requests >= 2.21.0', 'pycrypto >= 2.6.1', 'pycurl >= 7.43.0', 'whois >= 0.7', 'scapy-python3 >= 0.20'],
    include_package_data=True,
    package_data={
        'core': ['js/*.css', 'js/*.js', 'js/leaflet/*.css', 'js/leaflet/*.js', 'js/cluster/*', 'txt/*.txt', 'images/crew/*', 'images/aliens/*', 'images/*.txt'],
        'data': ['*.dat', '*.txt'],
    },
    entry_points={
        'console_scripts': [
            'ufonet=UFONet:core.main',
        ],
        'gui_scripts': [
            'ufonet=UFONet:core.main',
        ],
    },
    keywords='Toolkit WebAbuse DoS DDoS Botnet Darknet UFONet',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        "Environment :: Web Environment",
        "Environment :: Console", 
        "Intended Audience :: System Administrators",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        'Programming Language :: Python :: 3',
        "Topic :: Internet", 
        "Topic :: Security", 
        "Topic :: System :: Networking",
      ],
      zip_safe=False
)
