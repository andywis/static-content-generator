#!/usr/bin/env python3
"""
Utility to upload files to a remote FTP server


History
--------
First working version: 19 Dec 2012
Updated for AWCM (Python2): 12 Dec 2017
Bugfixes: 16 Dec 2023


Usage
------
* Add some fields to config.json, as below

    "ftp_hostname": "ftp.example.com",
    "ftp_remote_path": "/public_html/test_12345",
    "ftp_username": "my_username"

* python3 upload.py


"""

import os
from ftplib import FTP, error_perm
import getpass
import json

DRY_RUN = False  # set to True to avoid making changes


def read_from_config_file():
    """ Read FTP parameters from the config.json file"""
    with open('config.json', 'r') as cfg_fh:
        config = json.load(cfg_fh)

    ftp_hostname = config['ftp_hostname']
    ftp_path = config['ftp_remote_path']
    if 'ftp_username' in list(config.keys()):
        ftp_username = config['ftp_username']
    else:
        ftp_username = input("FTP username: ")

    # Always prompt for the password. never save it in config
    ftp_password = getpass.getpass("FTP password: ")

    # Ensure there's a leading slash on the remote path.
    if ftp_path[0] != '/':
        ftp_path = '/' + ftp_path

    return ftp_hostname, ftp_path, ftp_username, ftp_password


def find_all_files(adir):
    candidates = []
    for root, dirs, files in os.walk(adir):
        for filename in files:
            f = os.path.join(root, filename)
            # Strip "adir" off the front of the path,
            # String.partition() splits on '/' or '\\' as appropriate
            _junk, _sep, output_path = f.partition(os.sep)
            candidates.append(output_path)
    return candidates


def find_all_folders(files):
    folders = []
    for f in files:
        path = os.path.dirname(f)
        if path and path not in folders:
            folders.append(path)
    return folders


def make_ftp_conn(remote_host, username, password):
    ftp = FTP(remote_host)
    ftp.login(username, password)
    return ftp


def make_folders_on_target(remote_dir, ftp, folders):
    """ Ensure all the folders are present on the target system
    under remote_dir

    """
    debug = True
    ftp.cwd(remote_dir)

    if debug:
        print("Ensure these folders exist:")
        print(json.dumps(folders, indent=4))

    for folder in folders:

        if debug:
            print(f"Testing for existence of Folder {folder} in {remote_dir}")
        try:
            previous_pwd = ftp.pwd()
            ftp.cwd(folder)
            ftp.cwd(previous_pwd)
            if ftp.pwd() != previous_pwd:
                raise Exception("FAIL: Failed to change back to previous folder")
        except error_perm:
            if debug:
                print("Currently in %s Cannot cd into %s" % (ftp.pwd(), folder))

            parent_folder = os.path.normpath(os.path.join(folder, '..'))

            if debug:
                print("Trying to make parent folders: %s" % parent_folder)

            # Recurse up the tree, trying to make parent folders
            if parent_folder != '.':
                make_folders_on_target('/' + remote_dir, ftp, [parent_folder])

            if debug:
                print("Finished mk-parent-dir. Try mkd on %s" % folder)
                print("We're currently in %s" % ftp.pwd())
            if DRY_RUN:
                print("DRY_RUN: would make folder %s" % folder)
            else:
                ftp.mkd(folder)


def ftp_files_to_target(local_dir, remote_dir, ftp, file_list):
    """
    Copy the file_list to the target system.
    Each item in file_list is a filename, potentially with path
    prefix.

    Raises an error_perm if FTP authentication fails at ftp.login()
    """
    ftp.cwd(remote_dir)
    for filename in file_list:
        if os.path.basename(filename) in ['.DS_Store']:
            continue
        localfilename = os.path.join(local_dir, filename)
        print("uploading %s" % filename)
        with open(localfilename, "rb") as fh:
            ftp.storbinary('STOR ' + filename, fh)
        print("    Done")

    print("Quitting FTP")
    ftp.quit()


def main_upload():
    debug = False
    cooked_dir = 'output'
    ftp_hostname, ftp_path, ftp_username, ftp_password = \
        read_from_config_file()

    cooked_files = find_all_files(cooked_dir)
    if not cooked_files:
        print("Nothing to upload")
    else:
        if debug:
            print("About to copy files ")
            print(cooked_files)
        else:
            print("About to copy %d files" % len(cooked_files))

        folders = find_all_folders(cooked_files)

        if debug:
            print("Folders: %r" % folders)
        ftp_handle = make_ftp_conn(ftp_hostname, ftp_username,
                                   ftp_password)

        make_folders_on_target(ftp_path, ftp_handle, folders)
        ftp_files_to_target(cooked_dir, ftp_path, ftp_handle, cooked_files)


if __name__ == '__main__':
    main_upload()
