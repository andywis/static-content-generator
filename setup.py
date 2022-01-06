from setuptools import setup

setup(
    name="awcm",
    version="1.0",
)

# from distutils.core import setup
# setup(name='beam_shared',  # beam-shared in `pip list` (hyphen, not underscore)
#       version='1.0',

#       # https://docs.python.org/2/distutils/setupscript.html#listing-individual-modules
#       # The python module (beam_shared.py) doesn't _have_ to have the same name
#       # as the package, but it makes it less confusing if we can use the same
#       # word in "pip install" and python's `import ...`
#       py_modules=['beam_shared'],

#       description='Utilities shared between both Beam scripts',
#       author='Andy Watkins',
#       author_email='awatkins@ancoris.com',
#       url='https://www.ancoris.com',
# )

# WORKED FOR ME!!
#  pip install -e .
# Obtaining file:///Users/awatkins/git/github_andywis/static-content-generator
# Installing collected packages: awcm
#   Running setup.py develop for awcm
# Successfully installed awcm-1.0
# WARNING: You are using pip version 21.1.1; however, version 21.3.1 is available.
# You should consider upgrading via the '/Users/awatkins/git/github_andywis/static-content-generator/t_venv1/bin/python3 -m pip install --upgrade pip' command.


