import pandas as pd
import numpy as np
import os, sys, re, json, subprocess
from jsonschema import validate, ValidationError

# Read the common_libraries.tsv from the pull request into a DataFrame to compare
df_pr = pd.read_csv(os.environ["LIBRARIES_PATH"], sep="\t")

# Read the common_libraries.tsv from the pull request into a DataFrame to validate
# Параметр keep_default_na указывает pandas не использовать список стандартных значений для преобразования в NaN
df_pr_ = pd.read_csv(os.environ["LIBRARIES_PATH"], sep="\t", 
                     dtype={"publication_year": str, 
                            "strand_type": str,
                            "library_polymerase": str,
                            "library_concentration": str,
                            "library_treatment": str,
                            "PCR_cycle_count": str,
                            "read_count": str,
                            "download_sizes": str},
                            keep_default_na=False)

# Fetch the main branch from the repository
subprocess.run(["git", "fetch", "origin", "main"])

# Checkout the common_libraries.tsv from the main branch
subprocess.run(["git", "checkout", "FETCH_HEAD", "--", os.environ["LIBRARIES_PATH"]])

# Read the common_libraries.tsv from the main branch into a DataFrame
df_fork = pd.read_csv(os.environ["LIBRARIES_PATH"], sep="\t")

# Create a copy of the df_fork and df_pr for checking
df_fork_check = df_fork.copy()
df_pr_check = df_pr.drop(df_pr.loc[df_pr.index[len(df_fork):]].index)

# Compare the DataFrames of the pull request and the main branch
comparison_result = df_pr_check.compare(df_fork_check)
if comparison_result.empty:
    print("\033[38;5;40mThe old rows haven't been changed, now let's validate new rows\033[0m")
else:
    print("\033[31mThe old rows have been changed:\033[0m")
    print(comparison_result)
    sys.exit(1)

# Extract the new rows that have been added in the pull request
new_rows = df_pr_.loc[df_pr_.index[len(df_fork):]]

# Print the content of the new rows added in the pull request
print("\nContent of new_rows:")
print(new_rows)
print()

schemas_path = os.path.join(os.environ["GITHUB_WORKSPACE"], 'schemas_libraries')
columns = new_rows.columns
validation_results = {}

for column in columns:
    json_file = [file for file in os.listdir(schemas_path) if file.endswith('.json') and os.path.splitext(file)[0] == column]
    json_file_path = os.path.join(schemas_path, json_file[0])
    
    with open(json_file_path, 'r') as file:
        schema = json.load(file)
    column_results = []
    for value in new_rows[column]:
        try:
            validate(instance=value, schema=schema)
            column_results.append("Valid")
        except ValidationError as e:
            # из-за экранирования необходима замена '\\\\' на '\\'
            error_message = e.message.replace('\\\\', '\\')
            column_results.append(f"Invalid: {error_message}")
            error_value = True
    validation_results[column] = column_results

formatted_output = json.dumps(validation_results, indent=2, ensure_ascii=False)
print(formatted_output)

if error_value:
    print("\033[31mInvalid values found\033[0m")
    exit(1)