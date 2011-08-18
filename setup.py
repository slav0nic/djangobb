#!/usr/bin/env python
from setuptools import setup
from djangobb_forum import get_version


setup(name='djangobb_forum',
    version=get_version(),
    description='DjangoBB is a quick and simple forum which uses the Django Framework.',
    license='BSD',
    url='http://djangobb.org/',
    author='Alexey Afinogenov, Maranchuk Sergey',
    author_email='Maranchuk Sergey <slav0nic0@gmail.com>',
    package_dir = {'djangobb_forum': 'djangobb_forum'},
    packages=['djangobb_forum'],
    install_requires=['django>=1.2',
              'pil>=1.1.7',
              'django-messages==0.4.4',
              'django-haystack',
              'south',
              'postmarkup'
              ],
    keywords="django forum bb",
)
