# This verify script checks a number of properties of your solution
# 1. That you have the correct file naming (task1a.py in the folder submission).
# 2. That your file is of the correct file type (python file).
# 3. That your program produces an output file with the right name (task1a.csv).
# 4. How well it performs with the following measures:
#        Recall
#        Precision
#    In addition, the following values are reported to you for information purposes:
#        True Positives
#        False Negatives
#        False Positives
#        How long your program took to run (seconds).
# As part of this verification process, your python program will
#    be run.
#
import pandas as pd
import datetime
import time
import subprocess
from typing import Dict, List, Tuple
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
python_file_name = "{}/task1a.py".format(submission_folder_name)
python_output_name = "task1a.csv"
solution_output_name = "abt_buy_truth_small.csv"

first_data_set_name = "abt_small.csv"
second_data_set_name = "buy_small.csv"

pattern_multiple_spaces = r" +"
pattern_multiple_spaces_repl = r" "
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
    

def get_rows(df: pd.DataFrame, col_mapping: Dict[str, str], column_order: List[str]) -> List[List[str]]:
    """
    Convert the dataframe given to a sorted list of row values.
    
    Note: We don't need to normalise the input data as it should have come directly
        from the same test data, whereas headings might not.
    """
    rows = []
    for index, row in df.iterrows():
        entry = []
        for col in column_order:
            entry.append(str(row[col_mapping[col]]).strip())
        rows.append(entry)
        
    rows.sort()
    
    return rows

def list_differs(first, second):
    """
    Assumes lists are the same length.
    """
    for j in range(0, len(first)):
        if not first[j] == second[j]:
             return True
    return False

def unique_rows(rows: List[List[str]]) -> int:
    """
    Count unique rows, assumes rows are sorted.
    """
    unique = 0
    i = 0
    for i in range(0, len(rows)):
        if (i <= 0 or list_differs(rows[i], rows[i - 1])) and (i >= (len(rows) - 1) or list_differs(rows[i], rows[i + 1])):
            unique += 1
    return unique

# FP, TN, errors = validate_FP(FP_rows, lf1_df, lf2_df, FP, TN)
def validate_FP(rows, lf1_df: pd.DataFrame, lf2_df: pd.DataFrame, FP: int, TN: int, columns: List[str]) -> Tuple[int, int, int]:
    # Match datasets to columns.
    if columns[0] in [clean_string(col) for col in lf1_df.columns]:
        col_0_df = lf1_df
        col_1_df = lf2_df
    else:
        col_0_df = lf2_df
        col_1_df = lf1_df
    col_0_df_map = get_cleaned_dicts(col_0_df)
    col_1_df_map = get_cleaned_dicts(col_1_df)
    errors = 0
    for row in rows:
        first_val, second_val = row[0], row[1]
        if len(col_0_df[col_0_df[col_0_df_map[columns[0]]].apply(str) == str(first_val)]) <= 0:
            errors = errors + 1
        elif len(col_1_df[col_1_df[col_1_df_map[columns[1]]].apply(str) == str(second_val)]) <= 0:
            errors = errors + 1
    # Correct statistics
    return FP - errors, TN + errors, errors
    

def calculate_statistics(pred_rows: List[List[str]], true_rows: List[List[str]], lf1_df: pd.DataFrame, lf2_df: pd.DataFrame) -> Tuple[int, int, int, int, List[List[str]]]:
    TP, FP, FN, TN = 0, 0, 0, 0
    errors = 0
    FP_rows = []
    i, j = 0, 0
    while i < len(pred_rows) and j < len(true_rows):
        if pred_rows[i] == true_rows[j]:
            TP = TP + 1
            i, j = i + 1, j + 1
        elif pred_rows[i] < true_rows[j]:
            # Row in pred_rows which is not in true_rows, FP.
            FP = FP + 1
            FP_rows.append(pred_rows[i])
            i = i + 1
        else:
            # Row in true_rows which is not in pred_rows, FN.
            FN = FN + 1
            j = j + 1
    
    while i < len(pred_rows):
        # Row in pred_rows which is not in true_rows, FP.
        FP = FP + 1
        i = i + 1
        
    while j < len(true_rows):
        # Row in true_rows which is not in pred_rows, FN.
        FN = FN + 1
        j = j + 1
    
    # Calculate TP + FP + FN + TN
    lf1_df_rows, _ = lf1_df.shape
    lf2_df_rows, _ = lf2_df.shape
    TN = (lf1_df_rows * lf2_df_rows) - (TP + FP + FN)
    
    return TP, FP, FN, TN, FP_rows

try:
    timelog("Running program ({})".format(python_file_name))
    start_time = datetime.datetime.now()
    # Run program
    program = subprocess.Popen(['python', '{}'.format(python_file_name)], 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    end_time = datetime.datetime.now()
    timelog("Program output stream:")
    print(program.stdout.read().decode())
    timelog("Program error stream:")
    print(program.stderr.read().decode())
    
    timelog("Program took {} seconds to run.".format(
        (end_time - start_time).total_seconds()))
    
    # Check file created correctly.
    timelog("Loading {}".format(python_output_name))
    
    student_df = pd.read_csv("{}".format(python_output_name))
    
    timelog("Loaded {}".format(python_output_name))
    
    # Check all required columns are present.
    assert clean_string('idAbt') in [clean_string(col) for col in student_df.columns], "column idAbt missing"
    assert clean_string('idBuy') in [clean_string(col) for col in student_df.columns], "column idBuy missing"
    assert len(student_df.columns) == 2, "Unexpected columns {}".format([col for col in student_df.columns if clean_string(col) not in ['idAbt', 'idBuy']])
    
    timelog("Loading {}".format(solution_output_name))
    
    solution_df = pd.read_csv("{}".format(solution_output_name))
    
    timelog("Loaded {}".format(solution_output_name))
    
    timelog("Running basic checking for {}".format(python_output_name))
    # Use the solution's columns for both sets of rows in case the order of columns
    # differs between the two csvs.
    cleaned_solution_cols = [clean_string(col) for col in solution_df.columns]
    student_rows = get_rows(student_df, get_cleaned_dicts(student_df), cleaned_solution_cols)
    solution_rows = get_rows(solution_df, get_cleaned_dicts(solution_df), cleaned_solution_cols)
    
    # Check if any non-unique rows are present in the student_tuple data.
    assert unique_rows(student_rows) == len(student_rows), "DataFrame {} contains duplicate entries".format(python_output_name)
    
    timelog("Calculating statistics for linkage.")
    timelog("Loading {} and {} for extra statistics.".format(first_data_set_name, second_data_set_name))
    lf1_df = pd.read_csv(first_data_set_name, encoding='ISO-8859-1')
    lf2_df = pd.read_csv(second_data_set_name, encoding='ISO-8859-1')
    TP, FP, FN, TN, FP_rows = calculate_statistics(student_rows, solution_rows, lf1_df, lf2_df)
    
    if FP > 0:
        timelog("Checking that all FP values are present in one of original datasets")
        FP, TN, errors = validate_FP(FP_rows, lf1_df, lf2_df, FP, TN, cleaned_solution_cols)
    else:
        errors = 0
        
    timelog("Results:")
    if TP == 0:
        # Analytically continue.
        print("\tRecall: {}".format(0))
        print("\tPrecision: {}".format(0))
    else:
        print("\tRecall: {}".format(TP/(TP + FN)))
        print("\tPrecision: {}".format(TP/(TP + FP)))
    timelog("Extra Statistics:")
    print("\tTrue Positive Count: {}".format(TP))
    print("\tFalse Positive Count: {}".format(FP))
    print("\tFalse Negative Count: {}".format(FN))
    print("\tTrue Negative Count: {}".format(TN))
    if errors > 0:
        print("\tRows from neither source dataset: {}".format(errors))
    timelog("Script complete.")
    
except Exception as e:
    error_message = "Task 1a testing failed:\n{}\n".format(str(repr(e)))
    print(error_message)
    all_tests_passed = False
    raise
