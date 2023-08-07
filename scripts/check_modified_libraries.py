import pandas as pd
import os
import subprocess
import json
from jsonschema import validate, ValidationError
import sys

# Load the file from the pull request
df_pr = pd.read_csv(os.environ["FILE_PATH"], sep="\t")

# Fetch the version of the file when the fork was created
subprocess.run(["git", "fetch", "origin", "main"])
subprocess.run(["git", "checkout", "FETCH_HEAD", "--", os.environ["FILE_PATH"]])

# Load the old file
df_fork = pd.read_csv(os.environ["FILE_PATH"], sep="\t")

new_rows = df_pr.loc[df_pr.index[len(df_fork):]]

df_fork_check = df_fork.copy()

# Drop new_rows from df_pr and save it to df_pr_check
df_pr_check = df_pr.drop(new_rows.index)

# Вывод содержимого таблиц
print('\ndf_fork_check')
print(df_fork_check)
print()
print('\ndf_pr_check')
print(df_pr_check)
print()

# Вывод содержимого new_rows
print("\nСодержимое new_rows:")
print(new_rows)