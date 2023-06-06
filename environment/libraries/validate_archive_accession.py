import csv
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Open and read the JSON file
with open('enviromental_libraries.json', 'r') as jsonfile:
    # Load the JSON data as a dictionary object
    data = json.loads(jsonfile.read())

# Create a set of all values in the "archive_sample_accession" column
all_accessions = set()
accession_dict = {}
for index, item in enumerate(data):
    archive_accession = item['archive_sample_accession']
    if archive_accession:
        accession_list = [value.strip() for value in archive_accession.split(',') if value.strip()]
        for accession in accession_list:
            if accession in all_accessions:
                logging.info(f'Duplicate value {accession} found in rows {accession_dict[accession]+2} and {index+2}')
            else:
                all_accessions.add(accession)
                accession_dict[accession] = index

# Check if the number of unique values in the set is equal to the total number of values in the "archive_sample_accession" column
if len(all_accessions) != sum(1 for item in data if item['archive_sample_accession']):
    logging.error('Error: Duplicate values found in "archive_sample_accession"')
    exit(1)
else:
    logging.info('All archive_sample_accession are unique')
