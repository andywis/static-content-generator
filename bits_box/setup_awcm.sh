#!/bin/bash
#
# Copy this script into a newly created folder.
# If you want a theme, uncomment the last few lines, and fix the paths.
# then run this script (bash ./setup_awcm.sh) to set up.
#

# Check we've got the tools we need
git --version
python3 --version


# Download the static content generator
[[ -e _tmp ]] || mkdir _tmp
cd _tmp
SRC_DIR=$(pwd)/static-content-generator/
if [[ ! -d ${SRC_DIR} ]] ; then
    git clone --depth=1 https://github.com/andywis/static-content-generator.git
    rm -rf ${SRC_DIR}/.git
fi
cd ..


# Create the venv
if [[ ! -d _tmp/venv ]] ; then
    (
        cd _tmp
        python3 -m  venv venv
        source venv/bin/activate
        cd ${SRC_DIR}
        pip install -e .
    )
fi


# Make the folders
[[ -e components ]] || mkdir components
[[ -e content ]] || mkdir content
[[ -e _meta ]] || mkdir  _meta
[[ -e themes ]] || mkdir themes
[[ -e output ]] || mkdir  output


# Install the tools
cp ${SRC_DIR}/bits_box/Makefile ./
cp ${SRC_DIR}/bits_box/[09]* ./components/


# Install a theme
# if [[ ! -d themes/default_theme ]] ; then
#     cp -r path/to/a/theme/default_theme ./themes/
# fi
