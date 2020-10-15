# This verify script checks a number of properties of your solution
# 1. That you have the correct file naming (task1b.py in the folder submission).
# 2. That your file is of the correct file type (python file).
# 3. That your program produces an output file with the right name (task1b.csv).
# 4. How well it performs with the following measures:
#        Pair Completeness
#        Reduction Ratio
#        How long your program took to run (seconds)
#    In addition, the following values are reported to you for information purposes:
#        True Positives
#        False Negatives
#        False Positives
#    Note that for practical reasons, n used in the reduction ratio calculation assumes
#        we have each key assigned to a single block, your program might not have to do
#        this, but if your program does more calculations than not performing blocking at all,
#        you'll find this reflected in the reduction ratio.
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
python_file_name = "{}/task1b.py".format(submission_folder_name)
google_block_output_name = "abt_blocks.csv"
amazon_block_output_name = "buy_blocks.csv"
solution_output_name = "abt_buy_truth.csv"

google_data_set_name = "abt.csv"
amazon_data_set_name = "buy.csv"

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


def block_in_common(blocks_amazon: pd.DataFrame, blocks_google: pd.DataFrame) -> bool:
    unique_amazon = sorted(list(set(blocks_amazon)))
    unique_google = sorted(list(set(blocks_google)))
    i, j = 0, 0
    len_amazon = len(unique_amazon)
    len_google = len(unique_google)
    while i < len_amazon and j < len_google:
        if unique_amazon[i] == unique_google[j]:
            return True
        elif unique_amazon[i] < unique_google[j]:
            i = i + 1
        else:
            j = j + 1
    return False


def calculate_statistics(student_google_df: pd.DataFrame, student_amazon_df: pd.DataFrame, solution_df: pd.DataFrame, sol_google_df: pd.DataFrame, sol_amazon_df: pd.DataFrame) -> Tuple[int, int, int, int, int, Dict[str, Union[int, str]]]:
    TP, FP, FN, TN, n, largest_block_pair = 0, 0, 0, 0, 0, {'google': 0, 'amazon': 0, 'comparisons': 0, 'key': 'N/A'}

    student_google_cols = get_cleaned_dicts(student_google_df)
    student_amazon_cols = get_cleaned_dicts(student_amazon_df)

    for index, row in solution_df.iterrows():
        amazon_row = row['idBuy']
        google_row = row['idAbt']
        blocks_amazon = list(student_amazon_df[student_amazon_df[student_amazon_cols['product_id']] == amazon_row][student_amazon_cols['block_key']].values)
        blocks_google = list(student_google_df[student_google_df[student_google_cols['product_id']] == google_row][student_google_cols['block_key']].values)
        if block_in_common(blocks_amazon, blocks_google):
            # Matched
            TP = TP + 1

    # We now work out (FP + TP), the number of comparisons we do.
    s_g_groupby = student_google_df.groupby(student_google_df[student_google_cols['block_key']]).count()
    s_a_groupby = student_amazon_df.groupby(student_amazon_df[student_amazon_cols['block_key']]).count()

    s_a_indices = set(s_a_groupby.index)

    positives = 0
    for index, count_google in s_g_groupby.iterrows():
        if index in s_a_indices:
            count_amazon = int(s_a_groupby[s_a_groupby.index == index].sum()[student_amazon_cols['product_id']])
            comparisons = int(count_google * count_amazon)
            positives += comparisons
            if comparisons > largest_block_pair['comparisons']:
                largest_block_pair['key'] = index
                largest_block_pair['amazon'] = count_amazon
                largest_block_pair['google'] = int(count_google)
                largest_block_pair['comparisons'] = comparisons

    # False positives are all the comparisons that don't match.
    # NOTE: In the construction of this, we also assume a second match is a
    #   false positive. This is in the spirit of the reduction ratio, but is not
    #   a strict following of the formula.
    FP = positives - TP

    # Calculate TP + FP + FN + TN for unique blocking
    sol_google_df_rows, _ = sol_google_df.shape
    sol_amazon_df_rows, _ = sol_amazon_df.shape
    n = (sol_google_df_rows * sol_amazon_df_rows)

    # Calculate FN
    ground_truth_positives, _ = solution_df.shape
    FN = ground_truth_positives - TP

    # TN unique.
    TN = n - (TP + FN + FP)

    return TP, FP, FN, TN, n, largest_block_pair

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

    run_time = (end_time - start_time).total_seconds()

    timelog("Program took {} seconds to run.".format(
        (end_time - start_time).total_seconds()))

    # Check file created correctly.
    timelog("Loading {}".format(google_block_output_name))

    student_google_df = pd.read_csv("{}".format(google_block_output_name))

    timelog("Loaded {}".format(google_block_output_name))

    # Check all required columns are present.
    assert clean_string('block_key') in [clean_string(col) for col in student_google_df.columns], "column block_key missing"
    assert clean_string('product_id') in [clean_string(col) for col in student_google_df.columns], "column product_id missing"
    assert len(student_google_df.columns) == 2, "Unexpected columns {}".format([col for col in student_google_df.columns if clean_string(col) not in ['block_key', 'product_id']])

    timelog("Loading {}".format(amazon_block_output_name))

    student_amazon_df = pd.read_csv("{}".format(amazon_block_output_name))

    timelog("Loaded {}".format(amazon_block_output_name))

    # Check all required columns are present.
    assert clean_string('block_key') in [clean_string(col) for col in student_amazon_df.columns], "column block_key missing"
    assert clean_string('product_id') in [clean_string(col) for col in student_amazon_df.columns], "column product_id missing"
    assert len(student_amazon_df.columns) == 2, "Unexpected columns {}".format([col for col in student_amazon_df.columns if clean_string(col) not in ['block_key', 'product_id']])

    timelog("Converting block keys to strings")
    student_google_df[get_cleaned_dicts(student_google_df)['block_key']] = student_google_df[get_cleaned_dicts(student_google_df)['block_key']].apply(str)
    student_amazon_df[get_cleaned_dicts(student_amazon_df)['block_key']] = student_amazon_df[get_cleaned_dicts(student_amazon_df)['block_key']].apply(str)
    
    timelog("Loading {}".format(solution_output_name))

    solution_df = pd.read_csv("{}".format(solution_output_name))

    timelog("Loaded {}".format(solution_output_name))

    # Use the solution's columns for both sets of rows in case the order of columns
    # differs between the two csvs.
    cleaned_solution_cols = [clean_string(col) for col in solution_df.columns]

    timelog("Calculating statistics for linkage.")
    timelog("Loading {} and {}.".format(google_data_set_name, amazon_data_set_name))
    sol_google_df = pd.read_csv(google_data_set_name, encoding='ISO-8859-1')
    sol_amazon_df = pd.read_csv(amazon_data_set_name, encoding='ISO-8859-1')

    timelog("Performing basic checking on datasets.")
    st_amazon_rows, _ = student_amazon_df.shape
    st_google_rows, _ = student_google_df.shape
    so_amazon_rows, _ = sol_amazon_df.shape
    so_google_rows, _ = sol_google_df.shape

    if not st_amazon_rows >= so_amazon_rows:
        print("Warning: Not all ids have been assigned a block in Buy dataset (amazon_blocks.csv) - {} ids in original, {} ids assigned to blocks in your solution. Ignore this warning if this is intentional.".format(so_amazon_rows, st_amazon_rows))
    if not st_google_rows >= so_google_rows: 
        print("Warning: Not all ids have been assigned a block in Abt dataset (google_blocks.csv) - {} ids in original, {} ids assigned to blocks in your solution. Ignore this warning if this is intentional.".format(so_google_rows, st_google_rows))

    TP, FP, FN, TN, n, largest_block_pair = calculate_statistics(student_google_df, student_amazon_df, solution_df, sol_google_df, sol_amazon_df)

    timelog("Results:")
    if TP == 0:
        # Analytically continue.
        print("\tPair Completeness: {}".format(0))
        print("\tReduction Ratio: {}".format(0))
        print("\tExecution time: {}s".format(run_time))
    else:
        print("\tPair Completeness: {}".format(TP/(TP + FN)))
        print("\tReduction Ratio: {}".format(1 - ((TP + FP)/n)))
        print("\tExecution time: {}s".format(run_time))
    timelog("Extra Statistics:")
    print("\tTrue Positive Count: {}".format(TP))
    print("\tFalse Positive Count: {}".format(FP))
    print("\tFalse Negative Count: {}".format(FN))
    print("\tTrue Negative Count (Assuming unique blocking): {}".format(TN))
    # Note: because non-unique blocking could have an arbitrary number of blocks,
    #       no upper bound on number of true negatives exists. Other conditions
    #       are probably reasonable, but can be synthesised as needed by
    #       subtracting (TP + FP + FN) from the maximum generated.
    print("\tn (unique blocking): {}".format(n))
    print("\tLargest paired block:")
    print("\t\tBlocking key: {}".format(largest_block_pair['key']))
    print("\t\tAbt ids in block: {}".format(largest_block_pair['google']))
    print("\t\tBuy ids in block: {}".format(largest_block_pair['amazon']))
    print("\t\tComparisons required: {}".format(largest_block_pair['comparisons']))
    timelog("Script complete.")

except Exception as e:
    error_message = "Task 1b testing failed:\n{}\n".format(str(repr(e)))
    print(error_message)
    all_tests_passed = False
    raise
