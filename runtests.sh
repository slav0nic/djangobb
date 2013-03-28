#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$PWD
django-admin.py  test --settings=djangobb_forum.tests.settings djangobb_forum