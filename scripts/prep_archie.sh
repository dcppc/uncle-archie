#!/bin/bash
#
# prep the infrastructure and directories needed 
# for uncle archie to run everything

if [ "$(id -u)" != "0" ]; then
    echo ""
    echo ""
    echo "This script should be run as root."
    echo ""
    echo ""
    exit 1;
fi

mkdir -p /www/archie.nihdatacommons.us/htdocs/output

mkdir -p /www/archie.nihdatacommons.us/htdocs/output/log
mkdir -p /www/archie.nihdatacommons.us/htdocs/output/ucl

sudo chown -R florence:florence /www/archie.nihdatacommons.us

