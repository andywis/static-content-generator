#!/bin/bash
#
# Copy this script into a newly created folder.
# If you want a theme, uncomment the last few lines, and fix the paths.
# then run this script (bash ./setup_awcm.sh) to set up.
#


echo "------------------------------------------"
echo "AWCM: Checking we've got the tools we need"
echo "------------------------------------------"
# To install these on Ubuntu: sudo apt-get install -y python3-venv git make
git --version || exit 1
python3 --version || exit 1
make --version || exit 1



echo ""
echo "----------------------------------------------"
echo "AWCM: Downloading the static content generator"
echo "----------------------------------------------"
[[ -e tools ]] || mkdir tools
cd tools || exit 1
SRC_DIR=$(pwd)/static-content-generator/
if [[ ! -d ${SRC_DIR} ]] ; then
    git clone --depth=1 https://github.com/andywis/static-content-generator.git
    rm -rf "${SRC_DIR}/.git"
else
    echo "Already downloaded to tools/static-content-generator"
fi
cd ..



echo ""
echo "------------------------------------"
echo "AWCM: Creating the Python virtualenv"
echo "------------------------------------"
if [[ ! -d tools/venv ]] ; then
    (
        cd tools || exit 1
        python3 -m  venv venv
        . venv/bin/activate
        cd "${SRC_DIR}" || exit 1
        # N.B. this installs LXML; it miight be slow
        pip install -r requirements.txt

        echo "AWCM: TEMPORARY FIX... move bits_box out of the way for now."
        mv bits_box ../
        pip install -e .
        mv ../bits_box .
    )
else
    echo "venv already created in tools/venv"
fi



echo ""
echo "--------------------------"
echo "AWCM: Installing the tools"
echo "--------------------------"
# Make the folders
[[ -e components ]] || mkdir components
[[ -e content ]] || mkdir content
[[ -e _meta ]] || mkdir  _meta
[[ -e themes ]] || mkdir themes
[[ -e output ]] || mkdir  output

# and copy the tool
cp "${SRC_DIR}"/bits_box/Makefile ./
cp "${SRC_DIR}"/bits_box/[09]* ./components/


# Install a theme
# if [[ ! -d themes/default_theme ]] ; then
#     cp -r path/to/a/theme/default_theme ./themes/
# fi

echo ""
echo "---------------------------------------"
echo "AWCM  is installed and ready to be used"
echo "---------------------------------------"
echo "      Type  make  to build your website"
