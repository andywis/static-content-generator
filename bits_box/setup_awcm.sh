#!/bin/bash
#
# Copy this script into a newly created folder.
# If you want a theme, uncomment the last few lines, and fix the paths.
# then run this script (bash ./setup_awcm.sh) to set up.
#


# Check we've got the tools we need
# To install these on Ubuntu: sudo apt-get install -y python3-venv git make
git --version || echo "git is not installed"; exit 1
python3 --version || echo "python3 is not installed"; exit 1
make --version || echo "make is not installled"; exit 1


# Download the static content generator
[[ -e tools ]] || mkdir tools
cd tools || exit 1
SRC_DIR=$(pwd)/static-content-generator/
if [[ ! -d ${SRC_DIR} ]] ; then
    git clone --depth=1 https://github.com/andywis/static-content-generator.git
    rm -rf "${SRC_DIR}/.git"
fi
cd ..


# Create the Python virtualenv
if [[ ! -d tools/venv ]] ; then
    (
        cd tools || exit 1
        python3 -m  venv venv
        . venv/bin/activate
        cd "${SRC_DIR}" || exit 1
        # N.B. this installs LXML; it miight be slow
        pip install -r requirements.txt
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
cp "${SRC_DIR}"/bits_box/Makefile ./
cp "${SRC_DIR}"/bits_box/[09]* ./components/


# Install a theme
# if [[ ! -d themes/default_theme ]] ; then
#     cp -r path/to/a/theme/default_theme ./themes/
# fi
