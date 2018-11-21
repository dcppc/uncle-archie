#!/bin/bash
#
# To test-run:
# 
#       sudo -H -u ubuntu ./start_archie.sh
# 
# To actually run:
# 
#       (install archie.service startup service)
#
# Shell script used to start up uncle archie
# so uncle archie can run as a startup service.
# 
# This is reliant on having pyenv set up already
# on beavo, the server that runs archie.

ARCHIE_DIR="/home/florence/uncle-archie"
PYENV_BIN="/home/florence/.pyenv/bin"

echo "Preparing python"
eval "$(${PYENV_BIN}/pyenv init -)"

echo "Changing directories"
cd ${ARCHIE_DIR}

echo "Installing virtualenv"
virtualenv vp
source vp/bin/activate
vp/bin/pip install -r requirements.txt

echo "Running Uncle Archie bare"
vp/bin/python ${ARCHIE_DIR}/uncle_archie.py && tail -f /nev/null

