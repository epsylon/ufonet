#!/usr/bin/env python
import sys


if sys.version_info[0] != 2:
    sys.exit("Sorry, ufonet requires Python 2.7")
    
from setuptools import setup, find_packages


setup(
    name='ufonet',
    version='0.8',
    license='GPLv3+',
    author_email='epsylon@riseup.net',
    author='Psy',
    description='DDoS Botnet via Web Abuse ',
    url='http://ufonet.03c8.net/',
    long_description=open('docs/README.txt').read(),
    packages=find_packages(),
    install_requires=['GeoIP >= 1.3.2', 'pygeoip >= 0.3.2', 'requests', 'pycrypto >= 2.6.1', 'pycurl >= 7.19.5.1'],
    include_package_data=True,
    package_data={
        'core': ['images/*', 'js/*.css', 'js/*.js', 'js/leaflet/*.css', 'js/leaflet/*.js', 'js/leaflet/images/*', 'js/cluster/*' ],
        'server': ['*.dat', '*.txt'],
    },
    entry_points={
        'console_scripts': [
            'ufonet=UFONet:core.main',
        ],
        'gui_scripts': [
            'ufonet=UFONet:core.main',
        ],
    },
    keywords='DDoS DoS botnet WebAbuse UFONet',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        "Environment :: Web Environment",
        "Environment :: Console", 
        "Intended Audience :: System Administrators",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        'Programming Language :: Python :: 2.7',
        "Topic :: Internet", 
        "Topic :: Security", 
        "Topic :: System :: Networking",
      ],
      zip_safe=False
)
