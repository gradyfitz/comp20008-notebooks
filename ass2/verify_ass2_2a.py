# This verify script checks a number of properties of your solution
# 1. That you have the correct file naming (task2a.py in the folder submission).
# 2. That your file is of the correct file type (python file).
# 3. That your program produces an output file (task2a.csv) with the right form:
#    First three lines:
#        feature, median, mean, variance
#        Access to electricity, rural (% of rural population) [EG.ELC.ACCS.RU.ZS], x, x, x
#        Adjusted savings: particulate emission damage (% of GNI) [NY.ADJ.DPEM.GN.ZS], x, x, x
#    The second line may be escaped with quotes, as you might expect and spaces
#        will be ignored.
# 4. That your program prints the following output:
#    Accuracy of decision tree: xxx.yyy%
#    Accuracy of k-nn (k=5): xxx.yyy%
#    Accuracy of k-nn (k=10): xxx.yyy%
# 5. That the verification script is able to extract these from your output correctly:
#    Decision tree accuracy: xxx.yyy%
#    k-nn (k=5)  accuracy: xxx.yyy%
#    k-nn (k=10) accuracy: xxx.yyy%
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
python_file_name = "{}/task2a.py".format(submission_folder_name)
student_output_name = "task2a.csv"
#solution_output_name = "amazon_google_truth.csv"

pattern_multiple_spaces = r" +"
pattern_multiple_spaces_repl = r" "

accuracy_dt_re    = r'Accuracy of decision tree:\s*(\d{0,3}(\.\d{0,3})?)'
accuracy_knn5_re  = r'Accuracy of k-nn \(k=5\):\s*(\d{0,3}(\.\d{0,3})?)'
accuracy_knn10_re = r'Accuracy of k-nn \(k=10\):\s*(\d{0,3}(\.\d{0,3})?)'

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

    # Check file created correctly.
    timelog("Loading {}.".format(student_output_name))

    student_df = pd.read_csv("{}".format(student_output_name))

    timelog("Loaded {}.".format(student_output_name))

    # Check all required columns are present.
    assert clean_string('feature') in [clean_string(col) for col in student_df.columns], "column feature missing."
    assert clean_string('median') in [clean_string(col) for col in student_df.columns], "column median missing."
    assert clean_string('mean') in [clean_string(col) for col in student_df.columns], "column mean missing."
    assert clean_string('variance') in [clean_string(col) for col in student_df.columns], "column variance missing."
    assert len(student_df.columns) == 4, "Unexpected columns {}.".format([col for col in student_df.columns if clean_string(col) not in ['feature', 'median', 'mean', 'variance']])

    timelog("Performing basic checking on datasets.")
    student_rows, student_columns = student_df.shape
    assert student_rows >= 2, "Solution missing rows."

    cleaned_rows_dict = get_cleaned_dicts(student_df)

    # Extract rows.
    # Determine whether the access to electricity column is escaped or not.
    if len(student_df[student_df.index == 'Access to electricity']) > 0:
        escaped = False
        ate_row = student_df[student_df.index == "Access to electricity"]
        ate_median = ate_row[cleaned_rows_dict['median']].iloc[0]
        ate_mean = ate_row[cleaned_rows_dict['mean']].iloc[0]
        ate_variance = ate_row[cleaned_rows_dict['variance']].iloc[0]

        # Adjusted savings: particulate emission damage (% of GNI) [NY.ADJ.DPEM.GN.ZS]
        #   row off by one. Has feature as index.
        asped_row = student_df[student_df.index == 'Adjusted savings: particulate emission damage (% of GNI) [NY.ADJ.DPEM.GN.ZS]']
        assert len(asped_row) > 0, "Couldn't find row 'Adjusted savings: particulate emission damage (% of GNI) [NY.ADJ.DPEM.GN.ZS]'"
        asped_median = asped_row[cleaned_rows_dict['feature']].iloc[0]
        asped_mean = asped_row[cleaned_rows_dict['median']].iloc[0]
        asped_variance = asped_row[cleaned_rows_dict['mean']].iloc[0]
    else:
        escaped = True
        ate_row = student_df[student_df[cleaned_rows_dict['feature']] == 'Access to electricity, rural (% of rural population) [EG.ELC.ACCS.RU.ZS]']
        assert len(ate_row) > 0, "Couldn't find row 'Access to electricity, rural (% of rural population) [EG.ELC.ACCS.RU.ZS]'."
        ate_median = ate_row[cleaned_rows_dict['median']].iloc[0]
        ate_mean = ate_row[cleaned_rows_dict['mean']].iloc[0]
        ate_variance = ate_row[cleaned_rows_dict['variance']].iloc[0]

        asped_row = student_df[student_df[cleaned_rows_dict['feature']] == 'Adjusted savings: particulate emission damage (% of GNI) [NY.ADJ.DPEM.GN.ZS]']
        assert len(asped_row) > 0, "Couldn't find row 'Adjusted savings: particulate emission damage (% of GNI) [NY.ADJ.DPEM.GN.ZS]'."
        asped_median = asped_row[cleaned_rows_dict['median']].iloc[0]
        asped_mean = asped_row[cleaned_rows_dict['mean']].iloc[0]
        asped_variance = asped_row[cleaned_rows_dict['variance']].iloc[0]

    timelog("Testing script retrieved the following values from {}:".format(student_output_name))
    print("Found values for 'access to electricity' - median: {}, mean: {}, variance: {}.".format(ate_median, ate_mean, ate_variance))
    print("Found values for 'adjusted savings'      - median: {}, mean: {}, variance: {}.".format(asped_median, asped_mean, asped_variance))

    timelog("Checking program output.")
    dt_match = re.search(accuracy_dt_re, program_output)
    knn5_match = re.search(accuracy_knn5_re, program_output)
    knn10_match = re.search(accuracy_knn10_re, program_output)

    assert dt_match, "Output was missing accuracy of decision tree."
    assert knn5_match, "Output was missing accuracy of k-nn (k=5)."
    assert knn10_match, "Output was missing accuracy of k-nn (k=10)."

    dt_accuracy = dt_match.group(1)
    knn5_accuracy = knn5_match.group(1)
    knn10_accuracy = knn10_match.group(1)

    timelog("Testing retrieved the following values from program output:")
    print("Decision tree accuracy: {}%".format(dt_accuracy))
    print("k-nn (k=5)    accuracy: {}%".format(knn5_accuracy))
    print("k-nn (k=10)   accuracy: {}%".format(knn10_accuracy))
    
    timelog("Script complete.")

except Exception as e:
    error_message = "Task 2a testing failed:\n{}\n".format(str(repr(e)))
    print(error_message)
    all_tests_passed = False
    raise
