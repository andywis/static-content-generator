#!/bin/bash
#
# Copy this script into a newly created folder.
# Edit the SRC_DIR variable below to suit,
# then run this script (bash ./setup_awcm.sh) to set up.
#
SRC_DIR=$HOME/git/github/andywis/AWCM_static_content_generator/

mkdir -p components
mkdir -p content 
mkdir -p _meta
mkdir -p themes
mkdir -p output

cp ${SRC_DIR}/bits_box/Makefile .
cp ${SRC_DIR}/bits_box/000_collect_data.py ./components
cp ${SRC_DIR}/bits_box/999_mksitemap.py ./components


# Hacks to get things working ... while there are still TODOs
if [ ! -e "templates" ]; then
    ln -s themes templates
fi
# Install a theme
if [ ! -d themes/balquidhur ]; then
    cp -r ../q.wis.co.uk/templates/balquidhur ./themes/
fi
