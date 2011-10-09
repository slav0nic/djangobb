#!/bin/bash
TOOLS=`dirname $0`
VENV=$TOOLS/../.djangobb-venv
source $VENV/bin/activate && $@

