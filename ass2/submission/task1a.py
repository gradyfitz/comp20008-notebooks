"""
Replace this with your solution for task1a.
"""

import os
import random
import datetime
import pandas as pd

range_low_truth = 0.1
range_high_truth = 0.3

rows = 130
random.seed(datetime.datetime.now())

with open("amazon_google_truth_small.csv", "r") as f:
    true_data = f.read()
amazon_df = pd.read_csv("amazon_small.csv")
google_df = pd.read_csv("google_small.csv")

true_data_lines = [row.split(",") for row in true_data.split("\n")]

tdr_data = true_data_lines[1:]

true_rows = random.randrange(int(range_low_truth*rows), int(range_high_truth*rows + 1))
other_rows = rows - true_rows
if other_rows < 0:
    other_rows = 0

print("Selecting {} true data linkages and {} random pairs".format(true_rows, other_rows))
    
true_segment = random.sample(tdr_data, true_rows)

google_ids = google_df['idGoogleBase'].values
amazon_ids = amazon_df['idAmazon'].values

google_id_other = random.sample(list(google_ids),other_rows)
amazon_id_other = random.sample(list(amazon_ids),other_rows)

other_row_segment = [[aid, gid] for aid, gid in zip(amazon_id_other, google_id_other) if [aid, gid] not in true_segment]

task1a_file = []
task1a_file.append(true_data_lines[0])
task1a_file.extend(true_segment)
task1a_file.extend(other_row_segment)
task1a_file = "\n".join([ ",".join(x) for x in task1a_file ]) + "\n"

with open("task1a.csv", "w") as f:
    f.write(task1a_file)
    