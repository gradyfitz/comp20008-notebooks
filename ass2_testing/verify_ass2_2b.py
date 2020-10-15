# This verify script checks a number of properties of your solution
# 1. That you have the correct file naming (task2b.py in the folder submission).
# 2. That your file is of the correct file type (python file).
# 3. That your program prints the following output:
#    Accuracy of feature engineering: x.yyy
#    Accuracy of PCA: x.yyy
#    Accuracy of first four features: x.yyy
#    -------- Or in percentages --------
#    Accuracy of feature engineering: xxx.yyy%
#    Accuracy of PCA: xxx.yyy%
#    Accuracy of first four features: xxx.yyy%
# 4. That the verification script is able to extract these from your output correctly:
#    feature engineering accuracy: xxx.yyy%
#    PCA                 accuracy: xxx.yyy%
#    first four features accuracy: xxx.yyy%
#
#    NOTE: The correctness of these measures won't be evaluated by this testing
#          script.
#
# As part of this verification process, your python program will
#    be run.
#
import pandas as pd
import datetime
import time
import subprocess
from typing import Dict, List, Tuple, Union
import sys
import re
import unicodedata
import os
import traceback
import hashlib
import math

def relative_path(base_folder: str, full_path: str) -> str:
    """
    This takes the name of the base folder and a file inside it and returns the
    relative path of the file inside that folder.
    """
    return os.popen("realpath --relative-to=\"{}\" \"{}\"".format(base_folder, full_path)).read().splitlines()[0]

def file_list(folder: str) -> List[Dict[str, str]]:
    """
    This takes the name of a folder and returns a list of all the items in that folder
    as dictionaries containing the name of the file, the path of the file and the 
    modified timestamp in seconds and as a date-time string.
    """
    list_of_files = []
    for file in os.listdir(folder):
        # Ignore all hidden files.
        if file[0] == '.':
            continue
        new_dict = {}
        full_path = os.path.join(folder, file)
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
    return list_of_files

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

def timelog(*args, **kwargs):
    """
    Logs the message msg timestamped with the current time and date.
    """
    print("[", datetime.datetime.now(), "]", *args, **kwargs)

submission_folder_name = "submission"
python_file_name = "{}/task2b.py".format(submission_folder_name)

pattern_multiple_spaces = r" +"
pattern_multiple_spaces_repl = r" "

accuracy_fe_p_re  = r'Accuracy of feature engineering:\s*(\d{0,3}(\.\d+)?)\%'
accuracy_pca_p_re = r'Accuracy of PCA:\s*(\d{0,3}(\.\d+)?)\%'
accuracy_f4f_p_re = r'Accuracy of first four features:\s*(\d{0,3}(\.\d+)?)\%'
accuracy_fe_re    = r'Accuracy of feature engineering:\s*(\d{0,3}(\.\d{0,3})?)'
accuracy_pca_re   = r'Accuracy of PCA:\s*(\d{0,3}(\.\d{0,3})?)'
accuracy_f4f_re   = r'Accuracy of first four features:\s*(\d{0,3}(\.\d{0,3})?)'

def clean_string(string: str) -> str:
    cstring = string

    # Normalise in case ligatures are present.
    cstring = unicodedata.normalize("NFKD", cstring)

    # Replace multiple spaces with single space
    cstring = re.sub(pattern_multiple_spaces, pattern_multiple_spaces_repl, cstring)

    # Trim wite space.
    cstring = cstring.lower().strip()

    return cstring

def get_cleaned_dicts(df: pd.DataFrame) -> Dict[str, str]:
    """
    Gets a mapping from the cleaned column name to whatever column name the
    dataframe actually uses.
    """
    column_mapping = {}
    for col in df.columns:
        column_mapping[clean_string(col)] = col
    return column_mapping


try:
    timelog("Running program ({}).".format(python_file_name))
    start_time = datetime.datetime.now()
    # Run program
    program = subprocess.Popen(['python', '{}'.format(python_file_name)],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    end_time = datetime.datetime.now()
    timelog("Program output stream:")
    program_output = program.stdout.read().decode()
    print(program_output)
    timelog("Program error stream:")
    print(program.stderr.read().decode())

    run_time = (end_time - start_time).total_seconds()

    timelog("Program took {} seconds to run.".format(
        (end_time - start_time).total_seconds()))

    timelog("Checking program output.")
    fe_match    = re.search(accuracy_fe_re,    program_output)
    fe_p_match  = re.search(accuracy_fe_p_re,  program_output)
    pca_match   = re.search(accuracy_pca_re,   program_output)
    pca_p_match = re.search(accuracy_pca_p_re, program_output)
    f4f_match   = re.search(accuracy_f4f_re,   program_output)
    f4f_p_match = re.search(accuracy_f4f_p_re, program_output)

    assert fe_match or fe_p_match,   "Output was missing accuracy of Feature engineering."
    assert pca_match or pca_p_match, "Output was missing accuracy of PCA."
    assert f4f_match or f4f_p_match, "Output was missing accuracy of First four features."
    
    if fe_p_match:
        fe_accuracy  = float(fe_p_match.group(1)) / 100.0
    else:
        fe_accuracy  = float(fe_match.group(1))
        
    if pca_p_match:
        pca_accuracy = float(pca_p_match.group(1)) / 100.0
    else:
        pca_accuracy = float(pca_match.group(1))
        
    if f4f_p_match:
        f4f_accuracy = float(f4f_p_match.group(1)) / 100.0
    else:
        f4f_accuracy = float(f4f_match.group(1))

    timelog("Testing retrieved the following values from program output:")
    print("Feature engineering accuracy: {:.3f}".format(fe_accuracy))
    print("PCA                 accuracy: {:.3f}".format(pca_accuracy))
    print("First four features accuracy: {:.3f}".format(f4f_accuracy))
    
    folder_files = list(filter(lambda file: ("task2b" in file['filename'] and "submission/" not in file['filename'][:11]), file_list(".")))
    if len(folder_files) > 0:
        folder_files.sort(key=lambda x: x['modified_s'], reverse=True)
        timelog("Extra task2b files:")
        fnlist = [(file['filename'], file['timestamp'], file['raw_filesize']) for file in folder_files]
        for file, modified, size in fnlist:
            print("\t" + file + "\t" + modified + "\t" + get_friendly_size(size))
    else:
        timelog("No extra task2b files.")
    timelog("Script complete.")

except Exception as e:
    error_message = "Task 2b testing failed:\n{}\n".format(str(repr(e)))
    print(error_message)
    all_tests_passed = False
    raise
