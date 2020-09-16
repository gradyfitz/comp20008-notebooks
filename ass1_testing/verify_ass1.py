# Python testing script for COMP20008 Assignment 1
# Run in the form
#   python verify_ass1.py
#
# Where the private output file is the content only visible to tutors
# and student output file is the content visible to students.
import pandas as pd
from typing import Tuple, List, Dict, Optional
from scipy import misc
from matplotlib import pyplot
import sys
import re
import unicodedata


def write_to_stdout(*args, **kwargs):
    """
    Write the given msg to the stdout file.
    """
    print(*args, **kwargs)
        
def write_to_stderr(*args, **kwargs):
    """
    Write the given msg to the stderr file.
    """
    print(*args, file=sys.stderr, **kwargs)
        
def write_to_both(msg: str):
    """
    Write the given msg to the private and student files.
    """
    write_to_private(msg)
    write_to_student(msg)

pattern_bracketed = r"\([^)]*\)"
pattern_bracketed_repl = r""
pattern_multiple_spaces = r" +"
pattern_multiple_spaces_repl = r" "
pattern_url_present = r"http://"
pattern_url_end = r"([^/]*)\.html"
    
def clean_string(string: str) -> str:
    cstring = string
        
    # Normalise in case ligatures are present.
    cstring = unicodedata.normalize("NFKD", cstring)
        
    # URLs
    if re.search(pattern_url_present, cstring):
        cstring = re.search(pattern_url_end, cstring).group(0)
        
    # Drop brackets
    cstring = re.sub(pattern_bracketed, pattern_bracketed_repl, cstring)
        
    # Replace multiple spaces with single space
    cstring = re.sub(pattern_multiple_spaces, pattern_multiple_spaces_repl, cstring)
        
    # Trim white space.
    cstring = cstring.lower().strip()
        
    return cstring

private_write = ""
current_task = ""

all_tests_passed = True

private_write = private_write + "\n==== task1 ====\n"
try:
    # Evaluate task1.csv
    current_task = "evaluating task1.csv"
    task1_output = pd.read_csv('task1.csv')
    
    rows, cols = task1_output.shape
    private_write = private_write + "{}\n".format("csv has {} rows and {} columns.".format(rows, cols))
    
    assert rows >= 5, "Less than five entries in task1.csv"
    
    private_write = private_write + "{}\n".format("First five rows of task1.csv:")
    private_write = private_write + "{}\n".format(task1_output.head(5).to_string())
    
    assert 'url' in [clean_string(col) for col in task1_output.columns], "url missing"
    assert 'headline' in [clean_string(col) for col in task1_output.columns], "headline missing"
    assert len(task1_output.columns) == 2, "Unexpected columns {}".format([col for col in task1_output.columns if clean_string(col) not in ['url', 'headline']])
            
    private_write = private_write + "\nTest stage \"{}\" passed\n".format(current_task)
except Exception as e:
    write_to_stderr("Failed while {}\n{}\n".format(current_task, str(repr(e))))
    
    error_message = "Failed while {}\n{}\n".format(current_task, str(repr(e)))
    private_write = private_write + error_message
    all_tests_passed = False
    
private_write = private_write + "\n==== task2 ====\n"
try:
    # Evaluate task2.csv
    current_task = "evaluating task2.csv"
    task2_output = pd.read_csv('task2.csv')
        
    rows, cols = task2_output.shape
    private_write = private_write + "{}\n".format("csv has {} rows and {} columns.".format(rows, cols))
    
    assert rows >= 5, "Less than five entries in task2.csv"
    
    private_write = private_write + "{}\n".format("First five rows of task2.csv:")
    private_write = private_write + "{}\n".format(task2_output.head(5).to_string())    
    
    assert 'url' in [clean_string(col) for col in task2_output.columns], "url missing"
    assert 'headline' in [clean_string(col) for col in task2_output.columns], "headline missing"
    assert 'team' in [clean_string(col) for col in task2_output.columns], "team missing"
    assert 'score' in [clean_string(col) for col in task2_output.columns], "score missing"
    assert len(task2_output.columns) == 4, "Unexpected columns {}".format([col for col in task2_output.columns if clean_string(col) not in ['url', 'headline', 'team', 'score']])
    
    private_write = private_write + "\nTest stage \"{}\" passed\n".format(current_task)
except Exception as e:
    write_to_stderr("Failed while {}\n{}\n".format(current_task, str(repr(e))))
    
    error_message = "Failed while {}\n{}\n".format(current_task, str(repr(e)))
    private_write = private_write + error_message
    all_tests_passed = False
    
private_write = private_write + "\n==== task3 ====\n"
try:
    # Evaluate task3.csv
    current_task = "evaluating task3.csv"
    task3_output = pd.read_csv('task3.csv')
    
    rows, cols = task3_output.shape
    private_write = private_write + "{}\n".format("csv has {} rows and {} columns.".format(rows, cols))
    
    assert rows >= 5, "Less than five entries in task3.csv"
    
    private_write = private_write + "{}\n".format("First five rows of task3.csv:")
    private_write = private_write + "{}\n".format(task3_output.head(5).to_string())
    
    assert 'team' in [clean_string(col) for col in task3_output.columns], "team missing"
    assert 'avg_game_difference' in [clean_string(col) for col in task3_output.columns], "avg_game_difference missing"
    assert len(task3_output.columns) == 2, "Unexpected columns {}".format([col for col in task3_output.columns if clean_string(col) not in ['team', 'avg_game_difference']])
    
    private_write = private_write + "\nTest stage \"{}\" passed\n".format(current_task)
except Exception as e:
    write_to_stderr("Failed while {}\n{}\n".format(current_task, str(repr(e))))
    
    error_message = "Failed while {}\n{}\n".format(current_task, str(repr(e)))
    private_write = private_write + error_message
    all_tests_passed = False
    
private_write = private_write + "\n==== task4 ====\n"
try:
    # Evaluate task4.png
    current_task = "evaluating task4.png"
    task4_output = pyplot.imread('task4.png')
    height, width, c = task4_output.shape
    private_write = private_write + "\ntask4.png is {}px x {}px\n".format(height, width)
    assert height > 30, "Image generated was less than 30 pixels tall"
    assert width > 30, "Image generated was less than 30 pixels wide"
    
    private_write = private_write + "\nTest stage \"{}\" passed\n".format(current_task)
except Exception as e:
    write_to_stderr("Failed while {}\n{}\n".format(current_task, str(repr(e))))
    
    error_message = "Failed while {}\n{}\n".format(current_task, str(repr(e)))
    private_write = private_write + error_message
    all_tests_passed = False
    
private_write = private_write + "\n==== task5 ====\n"
try:
    # Evaluate task5.png
    current_task = "evaluating task5.png"
    task5_output = pyplot.imread('task5.png')
    height, width, c = task5_output.shape
    private_write = private_write + "\ntask5.png is {}px x {}px\n".format(height, width)
    assert height > 30, "Image generated was less than 30 pixels tall"
    assert width > 30, "Image generated was less than 30 pixels wide"
    
    private_write = private_write + "\nTest stage \"{}\" passed\n".format(current_task)

except Exception as e:
    write_to_stderr("Failed while {}\n{}\n".format(current_task, str(repr(e))))
    
    error_message = "Failed while {}\n{}\n".format(current_task, str(repr(e)))
    private_write = private_write + error_message
    all_tests_passed = False

if all_tests_passed:
    completed_msg = "\nAll tests passed.\n"
    
    private_write = private_write + completed_msg

write_to_stdout(private_write)
    