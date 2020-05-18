# This verify script checks a number of properties of your solution
# 1. That you have the correct file naming (task2b.py in the folder submission).
# 2. That your file is of the correct file type (python file).
# 3. That your program prints the following output:
#    Accuracy of feature engineering: xx.yyy%
#    Accuracy of PCA: xx.yyy%
#    Accuracy of first four features: xx.yyy%
# 4. That the verification script is able to extract these from your output correctly:
#    feature engineering accuracy: xx.yyy%
#    PCA                 accuracy: xx.yyy%
#    first four features accuracy: xx.yyy%
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

def timelog(*args, **kwargs):
    """
    Logs the message msg timestamped with the current time and date.
    """
    print("[", datetime.datetime.now(), "]", *args, **kwargs)

submission_folder_name = "submission"
python_file_name = "{}/task2b.py".format(submission_folder_name)

pattern_multiple_spaces = r" +"
pattern_multiple_spaces_repl = r" "

accuracy_fe_re  = r'Accuracy of feature engineering:\s*(\d{0,2}(\.\d{0,3})?)'
accuracy_pca_re = r'Accuracy of PCA:\s*(\d{0,2}(\.\d{0,3})?)'
accuracy_f4f_re = r'Accuracy of first four features:\s*(\d{0,2}(\.\d{0,3})?)'

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
    timelog("Running program ({})".format(python_file_name))
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

    timelog("Checking program output")
    fe_match = re.search(accuracy_fe_re, program_output)
    pca_match = re.search(accuracy_pca_re, program_output)
    f4f_match = re.search(accuracy_f4f_re, program_output)

    assert fe_match, "Output was missing accuracy of Feature engineering"
    assert pca_match, "Output was missing accuracy of PCA"
    assert f4f_match, "Output was missing accuracy of First four features"

    fe_accuracy  =  fe_match.group(1)
    pca_accuracy = pca_match.group(1)
    f4f_accuracy = f4f_match.group(1)

    timelog("Testing retrieved the following values from program output:")
    print("Feature engineering accuracy: {}%".format(fe_accuracy))
    print("PCA                 accuracy: {}%".format(pca_accuracy))
    print("First four features accuracy: {}%".format(f4f_accuracy))
    
    timelog("Script complete.")

except Exception as e:
    error_message = "Task 2b testing failed:\n{}\n".format(str(repr(e)))
    print(error_message)
    all_tests_passed = False
    raise
