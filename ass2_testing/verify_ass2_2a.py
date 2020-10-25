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
#    Accuracy of decision tree: x.yyy
#    Accuracy of k-nn (k=5): x.yyy
#    Accuracy of k-nn (k=10): x.yyy
#    -------- Or in percentages --------
#    Accuracy of decision tree: xxx.yyy%
#    Accuracy of k-nn (k=5): xxx.yyy%
#    Accuracy of k-nn (k=10): xxx.yyy%
# 5. That the verification script is able to extract these from your output correctly:
#    Decision tree accuracy: x.yyy
#    k-nn (k=5)  accuracy: x.yyy
#    k-nn (k=10) accuracy: x.yyy
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
import io

def preprocess_lines(file_name: str) -> io.StringIO:
    """
    Processes a csv file which does not escape features containing commas.
    """
    with open(file_name, 'r') as f:
        lines = f.read().split("\n")
        if len(lines) < 1:
            return ""
        line_set = [lines[0]]
        for line in lines[1:]:
            cols = line.split(",")
            if len(cols) > 4:
                if cols[0][0] == "\"":
                    new_line = cols
                else:
                    new_line = ["\"" + ",".join(cols[:-3]) + "\""]
                    new_line.extend(cols[-3:])
                new_line = ",".join(new_line)
                
            else:
                new_line = ",".join(cols)
            line_set.append(new_line)
        return io.StringIO("\n".join(line_set))

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

accuracy_dt_p_re    = r'Accuracy of decision tree:\s*(\d{0,3}(\.\d+)?)\%'
accuracy_knn5_p_re  = r'Accuracy of k-nn \(k=3\):\s*(\d{0,3}(\.\d+)?)\%'
accuracy_knn10_p_re = r'Accuracy of k-nn \(k=7\):\s*(\d{0,3}(\.\d+)?)\%'
accuracy_dt_re      = r'Accuracy of decision tree:\s*(\d{0,1}(\.\d{0,3})?)'
accuracy_knn5_re    = r'Accuracy of k-nn \(k=3\):\s*(\d{0,1}(\.\d{0,3})?)'
accuracy_knn10_re   = r'Accuracy of k-nn \(k=7\):\s*(\d{0,1}(\.\d{0,3})?)'

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

    student_df = pd.read_csv(preprocess_lines("{}".format(student_output_name)))

    timelog("Loaded {}.".format(student_output_name))

    # Check all required columns are present.
    assert clean_string('feature') in [clean_string(col) for col in student_df.columns], "column feature missing."
    assert clean_string('median') in [clean_string(col) for col in student_df.columns], "column median missing."
    assert clean_string('mean') in [clean_string(col) for col in student_df.columns], "column mean missing."
    assert clean_string('variance') in [clean_string(col) for col in student_df.columns], "column variance missing."
    assert len(student_df.columns) == 4, "Unexpected columns {}.".format([col for col in student_df.columns if clean_string(col) not in ['feature', 'median', 'mean', 'variance']])

    timelog("Performing basic checking on datasets.")
    student_rows, student_columns = student_df.shape
    # 20200524 GJF - Now checks all features can be extracted instead of just the first 
    #    two.
    assert student_rows >= 20, "Solution missing rows (values should be present for all twenty features, only {} rows found).".format(student_rows)

    cleaned_rows_dict = get_cleaned_dicts(student_df)
    
    # Extract rows.
    expected_feature_rows = {
        "Access to electricity (% of population) [EG.ELC.ACCS.ZS]": {
          "short": "Access to electricity",
          "values": None
        },
        "Adjusted net national income per capita (current US$) [NY.ADJ.NNTY.PC.CD]": {
          "short": "Net national income",
          "values": None
        },
        "Age dependency ratio (% of working-age population) [SP.POP.DPND]": {
          "short": "Age dependency",
          "values": None
        },
        "Cause of death, by communicable diseases and maternal, prenatal and nutrition conditions (% of total) [SH.DTH.COMM.ZS]": {
          "short": "Death by communicable diseases",
          "values": None
        },
        "Current health expenditure per capita (current US$) [SH.XPD.CHEX.PC.CD]": {
          "short": "Health expenditure",
          "values": None
        },
        "Fertility rate, total (births per woman) [SP.DYN.TFRT.IN]": {
          "short": "Fertility rate",
          "values": None
        },
        "Fixed broadband subscriptions (per 100 people) [IT.NET.BBND.P2]": {
          "short": "Broadband subscription percentage",
          "values": None
        },
        "Fixed telephone subscriptions (per 100 people) [IT.MLT.MAIN.P2]": {
          "short": "Telephone subscription percentage",
          "values": None
        },
        "GDP per capita (constant 2010 US$) [NY.GDP.PCAP.KD]": {
          "short": "GDP per capita",
          "values": None
        },
        "GNI per capita, Atlas method (current US$) [NY.GNP.PCAP.CD]": {
          "short": "GNI per capita",
          "values": None
        },
        "Individuals using the Internet (% of population) [IT.NET.USER.ZS]": {
          "short": "Internet use percentage",
          "values": None
        },
        "Lifetime risk of maternal death (%) [SH.MMR.RISK.ZS]": {
          "short": "Lifetime risk of maternal death",
          "values": None
        },
        "People using at least basic drinking water services (% of population) [SH.H2O.BASW.ZS]": {
          "short": "People with basic water services",
          "values": None
        },
        "People using at least basic drinking water services, rural (% of rural population) [SH.H2O.BASW.RU.ZS]": {
          "short": "Rural basic drinking water services",
          "values": None
        },
        "People using at least basic drinking water services, urban (% of urban population) [SH.H2O.BASW.UR.ZS]": {
          "short": "Urban basic drinking water services",
          "values": None
        },
        "People using at least basic sanitation services, urban (% of urban population) [SH.STA.BASS.UR.ZS]": {
          "short": "Urban sanitation",
          "values": None
        },
        "Prevalence of anemia among children (% of children under 5) [SH.ANM.CHLD.ZS]": {
          "short": "Anemia among children",
          "values": None
        },
        "Secure Internet servers (per 1 million people) [IT.NET.SECR.P6]": {
          "short": "Secure Internet servers per million",
          "values": None
        },
        "Self-employed, female (% of female employment) (modeled ILO estimate) [SL.EMP.SELF.FE.ZS]": {
          "short": "Female self-employment share",
          "values": None
        },
        "Wage and salaried workers, female (% of female employment) (modeled ILO estimate) [SL.EMP.WORK.FE.ZS]": {
          "short": "Femal wage and salaried employment share",
          "values": None
        }
    }
    expected_feature_rows_list = list(expected_feature_rows.keys())
    expected_feature_rows_list.sort()

    for feature in expected_feature_rows_list:
        feature_row = student_df[student_df[cleaned_rows_dict['feature']] == feature]
        assert len(feature_row) > 0, "Couldn't find row '{}'".format(feature)
        
        feature_median = feature_row[cleaned_rows_dict['median']].iloc[0]
        feature_mean = feature_row[cleaned_rows_dict['mean']].iloc[0]
        feature_variance = feature_row[cleaned_rows_dict['variance']].iloc[0]
        values = {
          'median': feature_median,
          'mean': feature_mean,
          'variance': feature_variance,
        }
        expected_feature_rows[feature]['values'] = values

    timelog("Testing script retrieved the following values from {}:".format(student_output_name))

    maxlen = max([len(expected_feature_rows[x]['short']) for x in list(expected_feature_rows.keys())])

    for feature, data in expected_feature_rows.items():
        print("Found values for '{}'{} - median: {}, mean: {}, variance: {}.".format(data['short'], " "*(maxlen - len(data['short'])), data['values']['median'], data['values']['mean'], data['values']['variance']))

    timelog("Checking program output.")
    dt_match = re.search(accuracy_dt_re, program_output)
    dt_match_p = re.search(accuracy_dt_p_re, program_output)
    knn5_match = re.search(accuracy_knn5_re, program_output)
    knn5_match_p = re.search(accuracy_knn5_p_re, program_output)
    knn10_match = re.search(accuracy_knn10_re, program_output)
    knn10_match_p = re.search(accuracy_knn10_p_re, program_output)

    assert dt_match or dt_match_p, "Output was missing accuracy of decision tree."
    assert knn5_match or knn5_match_p, "Output was missing accuracy of k-nn (k=5)."
    assert knn10_match or knn10_match_p, "Output was missing accuracy of k-nn (k=10)."
    
    if dt_match_p:
        dt_accuracy = float(dt_match_p.group(1)) / 100.0
    else:
        dt_accuracy = float(dt_match.group(1))
        
    if knn5_match_p:
        knn5_accuracy = float(knn5_match_p.group(1)) / 100.0
    else:
        knn5_accuracy = float(knn5_match.group(1))
        
    if knn10_match_p:
        knn10_accuracy = float(knn10_match_p.group(1)) / 100.0
    else:
        knn10_accuracy = float(knn10_match.group(1))
    
    timelog("Testing retrieved the following values from program output:")
    print("Decision tree accuracy: {:.3f}".format(dt_accuracy))
    print("k-nn (k=3)    accuracy: {:.3f}".format(knn5_accuracy))
    print("k-nn (k=7)    accuracy: {:.3f}".format(knn10_accuracy))
    
    timelog("Script complete.")

except Exception as e:
    error_message = "Task 2a testing failed:\n{}\n".format(str(repr(e)))
    print(error_message)
    all_tests_passed = False
    raise
