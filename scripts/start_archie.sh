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

ARCHIE_DIR="/home/ubuntu/uncle-archie"
PYENV_BIN="/home/ubuntu/.pyenv/bin"

echo "Preparing python"
eval "$(${PYENV_BIN}/pyenv init -)"

echo "Changing directories"
cd ${ARCHIE_DIR}

echo "Installing virtualenv"
virtualenv vp
source vp/bin/activate

echo "Running Uncle Archie bare"
python ${ARCHIE_DIR}/uncle_archie.py && tail -f /nev/null

#echo "Running Uncle Archie in a screen"
##screen -S archie -d -m bash -c "python ${ARCHIE_DIR}/uncle_archie.py; tail -f /dev/null"
#screen -d -m bash -c "python ${ARCHIE_DIR}/uncle_archie.py; tail -f /dev/null"

