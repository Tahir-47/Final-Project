import pyexcel as pe
import pyexcel_ods3 as pe3
import pandas as pd


# Load the LibreCalc file
data = pe.get_sheet(file_name='Test.ods')

# Get the column index for 'Name' and 'Age'
detected_column_index = 0
camera_column_index = 1
date_column_index = 2
time_column_index = 3


def insert_log(detect, camera, date, time):
    
# Define new data to be added
    new_data = [detect, camera, date, time]

    
    data.row += [new_data[detected_column_index], new_data[camera_column_index], new_data[date_column_index], new_data[time_column_index]]


    # Save the modified file
    data.save_as('Test.ods')


def list_log():
    
    # Read the LibreCalc file
    data_pd = pd.read_excel('Test.ods', sheet_name='Sheet1')

    # Extract the first row as keys
    keys = list(data_pd.columns)

    # Convert the data to a list of dictionaries
    data_list = []
    for _, row in data_pd.iterrows():
        data_dict = {key: row[key] for key in keys}
        data_list.append(data_dict)

    return data_list


