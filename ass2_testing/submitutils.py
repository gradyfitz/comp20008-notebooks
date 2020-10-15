"""
This file contains utilities to help with submission.
"""
import os
from typing import List, Dict
import time, datetime
import hashlib
import math
import redis
import os
import subprocess
import zipfile
import submitutils
import time
import datetime
import glob
import re
import subprocess

def relative_path(base_folder: str, full_path: str) -> str:
    """
    This takes the name of the base folder and a file inside it and returns the
    relative path of the file inside that folder.
    """
    return os.popen("realpath --relative-to=\"{}\" \"{}\"".format(base_folder, full_path)).read().splitlines()[0]

def file_list(folder: str, recursive: bool = False) -> List[Dict[str, str]]:
    """
    This takes the name of a folder and returns a list of all the items in that folder
    as dictionaries containing the name of the file, the path of the file and the 
    modified timestamp in seconds and as a date-time string.
    
    If recursive is true, add all children files of all folders.
    """
    list_of_files = []
    folders = [folder]
    while len(folders) > 0:
        subfolder = folders[-1]
        folders.remove(subfolder)
        for file in os.listdir(subfolder):
            # Ignore all hidden files.
            if file[0] == '.':
                continue
            new_dict = {}
            full_path = os.path.join(subfolder, file)
            # Ignore symlinks
            if os.path.islink(full_path):
                continue
            m_time = os.path.getmtime(full_path)
            new_dict['filename'] = file
            new_dict['path'] = full_path
            new_dict['relative_path'] = relative_path(folder, full_path)
            new_dict['modified_s'] = m_time
            new_dict['timestamp'] = time.ctime(m_time)
            timestamp = datetime.datetime.fromtimestamp(m_time)
            new_dict['timestampstring'] = "%d%02d%02d%02d%02d%02d" % (timestamp.year, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute, timestamp.second)
            list_of_files.append(new_dict)
            filesize = os.path.getsize(full_path)
            new_dict['raw_filesize'] = filesize
            if os.path.isdir(full_path) and recursive and not os.path.islink(full_path):
                folders.append(new_dict["path"])
                
    return list_of_files

def get_file_hash(path: str) -> str:
    """
    This takes a file path and returns the hash of the file at that
    location.
    
    Borrowed from 
    https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
    """
    sha1 = hashlib.sha1()
    with open(path, 'rb') as f:
        data = f.read()
        sha1.update(data)
    return sha1.hexdigest()

def get_friendly_size(raw_size: int, round_dp=1) -> str:
    """
    Converts the given raw size in bytes to the largest
    of KiB, MiB and GiB which does not reduce the numeric
    component to less than one.
    Rounds _up_ to the nearest value.
    """
    denominations = [' bytes', 'KiB', 'MiB', 'GiB']
    index = 0
    friendly_number = raw_size
    while index < (len(denominations) - 1):
        if friendly_number > 1024:
            index = index + 1
            friendly_number = friendly_number / 1024
        else:
            break
    if not index == 0:
        exponent = 10 ** round_dp
        friendly_number = math.ceil((friendly_number * exponent)) / exponent
    return str(friendly_number) + denominations[index]

def get_username() -> str:
    # Get the current server's name and then get the part after the
    # first dash and drop the newline.
    awk_command = "hostname -s | awk 'BEGIN { FS = \"-\" } ; { print $2 }' | tr -d '\n'"
    return os.popen(awk_command).read()
    
def submit_to_queue(submit_mode="submit", username=None, assignment=None, zip_hash=None, submit_path=None) -> bool:
    """
        Submit mode is "submit" when user disk control is used as authorization.
        Submit mode is "psubmit" when command signing is used as authorization.
        Returns false if all values correctly set.
    """
    if submit_mode == "submit":
        if username is None or assignment is None or zip_hash is None or submit_path is None:
            return False
        r = redis.Redis(host="redis")
        r.rpush(submit_mode, "{} {} {} {} {}".format(submit_mode, username, assignment, zip_hash, submit_path))
        return True
    else:
        return False

def monitor_queue(queue=None, complete_stage=None, monitor_file=None, submission_name=None) -> bool:
    """
        Returns true/false if verify is complete_stage, 
            returns true otherwise if it returns. This is in principle
            not parallel-friendly
    """
    r = redis.Redis(host="redis")
    
    while True:
        item = r.lpop(queue)
        if item is None:
            # Sleep for ten seconds.
            time.sleep(10)
        else:
            print(item.decode("utf-8"))
            if monitor_file:
                with open(monitor_file, "a+") as f:
                    f.write(item.decode("utf-8") + '\n')
            if finalise(item.decode("utf-8"), complete_stage, submission_name):
                if not complete_stage == "verify":
                    return True
                else:
                    words = item.decode("utf-8").split()
                    return words[2].strip() == "pass"
    

def finalise(message: str, complete_stage: str, submission_name: str) -> bool:
    """
    Returns true if the given message reports the stage given is
    completed for the given submission.
    
    Messages usually in format:
        job_id stage signature submission_filename
    Except for verify step which broadcasts success or failure of execution:
        job_id stage success signature submission_filename
    And the setup step which broadcasts job data:
        job_id stage <submitted message data>
    Setup is not a valid checkable as the message is, in 
        principle, ambiguous by design.
    """
    words = message.split()
    print(words)
    if len(words) > 2:
        if words[1] == complete_stage:
            if complete_stage == "verify":
                if " ".join(words[4:]) == submission_name:
                    return True
            elif complete_stage == "setup":
                return True
            else:
                if " ".join(words[3:]) == submission_name:
                    return True
    return False

def do_zip():
    user_name = os.getenv("JUPYTERHUB_USER")

    USE_USERNAME_ONLY = True
    OUTPUT_AS_USER_NAME = True

    user_folder = "submission"
    list_of_files = [file for file in submitutils.file_list(user_folder) if '.git' not in file['path']]

    list_of_files.sort(key=lambda x: x['modified_s'], reverse=True)
    list_of_filenames = [(file['filename'], file['timestamp'], file['raw_filesize']) for file in list_of_files]
    if len(list_of_files) > 0:
        last_modified_file = list_of_files[0]
    else:
        last_modified_file = {
            "timestampstring": "00000000000000"
        }
    submission_zipfile_base = "submission-" + user_name + "-" + last_modified_file['timestampstring']
    submission_zipfile_name = submission_zipfile_base + ".zip"

    print("[", datetime.datetime.now(), "]", "Storing files in zip file", submission_zipfile_name, "for submission.")
    print("[", datetime.datetime.now(), "]", "Submission contents:")
    print("\tFilename\tModified")
    BOLD_START = "\033[1m"
    END_FORMATTING = "\033[0m"
    for file, modified, size in list_of_filenames:
        if modified == list_of_filenames[0][1]:
            print(BOLD_START, end="")
        print("\t" + file + "\t" + modified + "\t" + submitutils.get_friendly_size(size))
        if modified == list_of_filenames[0][1]:
            print(END_FORMATTING, end="")

    BASE_FOLDER = "."
    submission_zipfile_folder = BASE_FOLDER
    submission_zipfile_location = submission_zipfile_folder + "/" + submission_zipfile_name
    print("[", datetime.datetime.now(), "]", "Checking if",  submission_zipfile_location, "already exists")
    if os.path.exists(submission_zipfile_location):
        print("[", datetime.datetime.now(), "]", submission_zipfile_location, "already exists, no data.")
    else:
        # Ensure the folder exists
        os.popen('mkdir -p {}'.format(submission_zipfile_folder)).read()
        with zipfile.ZipFile(submission_zipfile_location, mode="w", compression=zipfile.ZIP_LZMA) as zf:
            for file in list_of_files:
                zf.write(file['path'], arcname=file['relative_path'])

        zip_hash = submitutils.get_file_hash(submission_zipfile_location)
        print("[", datetime.datetime.now(), "]", "Zip file hash:", zip_hash)
        zip_hash_location = submission_zipfile_folder + "/" + submission_zipfile_base + ".sha1"
        with open(zip_hash_location, "w") as f:
            f.write(zip_hash)