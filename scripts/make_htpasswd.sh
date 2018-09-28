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


function final() {
    echo ""
    echo "make_htpasswd.sh:"
    echo ""
    echo "    Successfully output .htpasswd file in current directory."
    echo ""
    echo "    To use this file with nginx, place file at /etc/nginx/.htpasswd"
    echo "    and add the following lines to the appropriate nginx conf block:"
    echo ""
    echo "        location / { "
    echo "            ..."
    echo "            auth_basic \"Restricted Content\";"
    echo "            auth_basic_user_file /etc/nginx/.htpasswd;"
    echo "            ..."
    echo "        }"
    echo ""
    exit 1;
}


## Only run this script if you are root!
#if [ "$(id -u)" != "0" ]; then
#    echo ""
#    echo ""
#    echo "This script should be run as root."
#    echo ""
#    echo ""
#    usage;
#    exit 1;
#fi


# User must set NGINX_PASSWORD using environment variable
if [[ "${NGINX_PASSWORD}" == "" ]]; then

    # User is confused
    usage

else

    echo "+---------------------------+"
    echo "Creating .htpasswd file..."
    echo "STEP 1: Preparing to set username"

    # Username is always "archie"
    echo -n 'archie:' >> .htpasswd

    echo "STEP 1: Username has been set."
    echo "STEP 2: Preparing to set password for user 'archie'."

    # Password comes from env var
    openssl passwd -apr1 ${NGINX_PASSWORD} >> .htpasswd

    echo "STEP 2: Password has been set."
    echo "STEP 3: Preparing to copy .htpasswd file into place."

    # Move the .htpasswd file into place
    if [ -f /etc/nginx/ ]; then
        sudo mv .htpasswd /etc/nginx/.htpasswd
    fi

    echo "STEP 3: .htpasswd file has been moved into place."

    final
fi


