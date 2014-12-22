#!/usr/bin/env python

from distutils.core import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='dailystrips',
      version='0.0',
      description='Fetch my daily cartoons from the web',
      author='Friedrich Delgado',
      author_email='friedel@nomaden.org',
      url='https://github.com/TauPan/dailystrips.py',
      packages=['dailystrips'],
      install_requires=required)
