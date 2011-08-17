#!/usr/bin/env python
from setuptools import setup


setup(name='djangobb_forum',
    version='0.0.1a0',
    description="DjangoBB is a quick and simple forum which uses the Django Framework.",
    license="BSD",
    url='http://djangobb.org/',
    author="Alexey Afinogenov, Maranchuk Sergey", 
    author_email="Maranchuk Sergey <slav0nic0@gmail.com>",
    package_dir = {'djangobb_forum': 'djangobb_forum'},
    packages=['djangobb_forum'],
    install_requires=['django>=1.2',
              'pil>=1.1.7',
              'django-messages==0.4.4',
              'django-haystack',
              'django-authopenid',
              'south',
              'postmarkup'
              ],
    keywords="django forum bb",
)
