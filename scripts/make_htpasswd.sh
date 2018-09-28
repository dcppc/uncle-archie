#!/bin/bash
#
# run this script and specify a password
# with the NGINX_PASSWORD env var


function usage() {
    echo ""
    echo "make_htpasswd.sh:"
    echo ""
    echo "    This script creates an .htpasswd file"
    echo "    so nginx can password-protect a directory."
    echo ""
    echo "    Set the nginx password using the NGINX_PASSWORD"
    echo "    environment variable."
    echo ""
    echo "Usage:"
    echo ""
    echo "    NGINX_PASSWORD=\"<password>\" ./make_htpasswd.sh"
    echo ""
    exit 1;
}


function copy() {
    echo ""
    echo "Successfully output .htpasswd file in current directory."
    echo "To use this file with nginx, place file at /etc/nginx/.htpasswd"
    echo "and add the following lines to the appropriate nginx conf block:"
    echo "    location / { "
    echo "        ..."
    echo "        auth_basic \"Restricted Content\";"
    echo "        auth_basic_user_file /etc/nginx/.htpasswd;"
    echo "        ..."
    echo "    }"
    echo ""
    exit 1;
}


if [[ "${NGINX_PASSWORD}" == "" ]]; then
    usage
else
    echo -n 'archie:' >> .htpasswd
    openssl passwd -apr1 >> .htpasswd
    if [ -f /etc/nginx/ ]; then
        mv .htpasswd /etc/nginx/.htpasswd
    fi
fi


