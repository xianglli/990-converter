import xml.etree.ElementTree as ET
import pandas as pd
import argparse
import os
import requests
import subprocess

# Namespace dictionary for XPath expressions
ns = {'irs': 'http://www.irs.gov/efile'}

# Function to read variables from a CSV file
def read_variables_from_csv(file_path):
    df = pd.read_csv(file_path)
    return df['Variables'].tolist()

# Load variables from CSV files without 'irs:' prefix
all_variables_file_path = './variables/all_variables.csv'
recipient_variables_file_path = './variables/recipient_variables.csv'
schedule_c_variables_file_path = './variables/schedule_c_variables.csv'

all_variables = read_variables_from_csv(all_variables_file_path)
recipient_variables = read_variables_from_csv(recipient_variables_file_path)
schedule_c_variables = read_variables_from_csv(schedule_c_variables_file_path)


def extract_variables_and_attr_from_xml(xml_file, variables):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    extracted_data = {}
    for var in variables:
        xpath_expr = var.replace('/text()', '')  
        
        # Split the XPath expression and prepend 'irs:' to each part
        xpath_parts = xpath_expr.split('/')
        # Apply the 'irs:' prefix only to the actual XML elements
        xpath_expr = '/'.join('irs:' + part for part in xpath_parts if part)

        #print(xpath_expr)  # Debugging statement to verify the XPath expression
        
        element = root.find(xpath_expr, ns)
        extracted_data[var] = element.text if element is not None else None
        if element is not None:
            for key, value in element.attrib.items():
                extracted_data[f"{var}/{key}"] = value
    
    return extracted_data



def download_index_csv(year):
    url = f'https://apps.irs.gov/pub/epostcard/990/xml/{year}/index_{year}.csv'
    local_path = f'data/index_file/index_{year}.csv'
    
    if not os.path.exists(os.path.dirname(local_path)):
        os.makedirs(os.path.dirname(local_path))
    else:
        print(f"Using existing index CSV for year {year}.")
    
    response = requests.get(url)
    response.raise_for_status()  # Check that the request was successful
    
    with open(local_path, 'wb') as file:
        file.write(response.content)
    
    print(f"Downloaded index CSV for year {year}.")
    return local_path

def download_and_extract_zip(xml_files_path_prefix, xml_batch_id, year):
    zip_url = f'https://apps.irs.gov/pub/epostcard/990/xml/{year}/{xml_batch_id}.zip'
    local_zip_path = f'{xml_files_path_prefix}{xml_batch_id}.zip'
    log_file = 'duplicate_log.txt'
    
    if not os.path.exists(xml_files_path_prefix):
        os.makedirs(xml_files_path_prefix)
    
    response = requests.get(zip_url)
    response.raise_for_status()  # Check that the request was successful
    
    with open(local_zip_path, 'wb') as file:
        file.write(response.content)

    xml_files_path = f'{xml_files_path_prefix}{xml_batch_id}/'
    
    try:
        # The '-o' option in unzip forces overwriting of files without prompting.
        # We also capture the output and error messages.
        result = subprocess.run(
            ['unzip', '-o', local_zip_path, '-d', xml_files_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )

        # Check for duplicate files in the output
        with open(log_file, 'a') as log:
            for line in result.stdout.splitlines():
                if 'replacing' in line:
                    log.write(f"Duplicate file: {line}\n")
                    log.write(f"Zip file: {local_zip_path}\n")
    
    except subprocess.CalledProcessError as e:
        with open(log_file, 'a') as log:
            log.write(f"Error extracting {local_zip_path}: {e.stderr}\n")
        print(f"Error extracting {local_zip_path}: {e}")
    
    print(f"Downloaded and extracted {xml_batch_id}.zip.")

def download_and_extract_zip_legacy(xml_files_path, year):
    zip_batches = {
        2023: [
            "https://apps.irs.gov/pub/epostcard/990/xml/2023/2023_TEOS_XML_01A.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2023/2023_TEOS_XML_02A.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2023/2023_TEOS_XML_03A.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2023/2023_TEOS_XML_04A.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2023/2023_TEOS_XML_05A.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2023/2023_TEOS_XML_05B.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2023/2023_TEOS_XML_06A.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2023/2023_TEOS_XML_07A.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2023/2023_TEOS_XML_08A.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2023/2023_TEOS_XML_09A.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2023/2023_TEOS_XML_10A.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2023/2023_TEOS_XML_11A.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2023/2023_TEOS_XML_11B.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2023/2023_TEOS_XML_11C.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2023/2023_TEOS_XML_12A.zip",
        ],
        2022: [
            "https://apps.irs.gov/pub/epostcard/990/xml/2022/2022_TEOS_XML_01A.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2022/2022_TEOS_XML_01B.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2022/2022_TEOS_XML_01C.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2022/2022_TEOS_XML_01D.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2022/2022_TEOS_XML_01E.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2022/2022_TEOS_XML_01F.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2022/2022_TEOS_XML_11A.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2022/2022_TEOS_XML_11B.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2022/2022_TEOS_XML_11C.zip",
        ],
        2021: [
            "https://apps.irs.gov/pub/epostcard/990/xml/2021/2021_TEOS_XML_01A.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2021/2021_TEOS_XML_01B.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2021/2021_TEOS_XML_01C.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2021/2021_TEOS_XML_01D.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2021/2021_TEOS_XML_01E.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2021/2021_TEOS_XML_01F.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2021/2021_TEOS_XML_01G.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2021/2021_TEOS_XML_01H.zip",
        ],
        2020: [
            "https://apps.irs.gov/pub/epostcard/990/xml/2020/2020_TEOS_XML_CT1.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2020/download990xml_2020_1.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2020/download990xml_2020_2.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2020/download990xml_2020_3.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2020/download990xml_2020_4.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2020/download990xml_2020_5.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2020/download990xml_2020_6.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2020/download990xml_2020_7.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2020/download990xml_2020_8.zip",
        ],
        2019: [
            "https://apps.irs.gov/pub/epostcard/990/xml/2019/2019_TEOS_XML_CT1.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2019/download990xml_2019_1.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2019/download990xml_2019_2.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2019/download990xml_2019_3.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2019/download990xml_2019_4.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2019/download990xml_2019_5.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2019/download990xml_2019_6.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2019/download990xml_2019_7.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2019/download990xml_2019_8.zip",
        ],
        2018: [
            "https://apps.irs.gov/pub/epostcard/990/xml/2018/2018_TEOS_XML_CT1.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2018/2018_TEOS_XML_CT2.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2018/2018_TEOS_XML_CT3.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2018/download990xml_2018_1.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2018/download990xml_2018_2.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2018/download990xml_2018_3.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2018/download990xml_2018_4.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2018/download990xml_2018_5.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2018/download990xml_2018_6.zip",
            "https://apps.irs.gov/pub/epostcard/990/xml/2018/download990xml_2018_7.zip",
        ],
    }

    if year in zip_batches:
        zip_urls = zip_batches[year]
    else:
        print(f"No ZIP batch URLs defined for the year {year}.")
        return
    
    for zip_url in zip_urls:
        local_zip_path = os.path.join(xml_files_path, os.path.basename(zip_url))
        
        if not os.path.exists(xml_files_path):
            os.makedirs(xml_files_path)
        
        response = requests.get(zip_url)
        response.raise_for_status()  # Check that the request was successful
        
        with open(local_zip_path, 'wb') as file:
            file.write(response.content)
        
        try:
            subprocess.run(['unzip', local_zip_path, '-d', xml_files_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error extracting {local_zip_path}: {e}")
        
        print(f"Downloaded and extracted {os.path.basename(zip_url)}.")

def extract_index_data(year, form_type):
    index_csv_path = f'data/index_file/index_{year}.csv'
    
    # Download the index CSV if it does not exist
    if not os.path.exists(index_csv_path):
        index_csv_path = download_index_csv(year)
    
    index_df = pd.read_csv(index_csv_path)

    # Filter the index DataFrame to include only rows with the specified form type
    index_df = index_df[index_df['RETURN_TYPE'] == form_type]

    xml_files_path_prefix = f'data/xml_files/{year}/'

    # List to hold all extracted data
    all_extracted_data = []

    if year < 2024:
        for _, row in index_df.iterrows():
            xml_folder_path = f"{xml_files_path_prefix}"
            xml_file = f"{xml_folder_path}{row['OBJECT_ID']}_public.xml"
            
            # Download and extract the ZIP file if the XML folder does not exist
            if not os.path.exists(xml_folder_path):
                download_and_extract_zip_legacy(xml_files_path_prefix, year)
            
            try:
                extracted_data = extract_variables_and_attr_from_xml(xml_file, all_variables)
                # Combine index data and extracted data
                combined_data = row.to_dict()  # Convert index row to dictionary
                combined_data.update(extracted_data)  # Add extracted data
                all_extracted_data.append(combined_data)  # Append to list
            except ET.ParseError:
                print(f"Error parsing {xml_file}.")
            except FileNotFoundError:
                print(f"File {xml_file} not found.")
    else:
        for _, row in index_df.iterrows():
            xml_folder_path = f"{xml_files_path_prefix}{row['XML_BATCH_ID']}/"
            xml_file = f"{xml_folder_path}{row['OBJECT_ID']}_public.xml"
            
            # Download and extract the ZIP file if the XML folder does not exist
            if not os.path.exists(xml_folder_path):
                download_and_extract_zip(xml_files_path_prefix, row['XML_BATCH_ID'], year)
            
            try:
                extracted_data = extract_variables_and_attr_from_xml(xml_file, all_variables)
                # Combine index data and extracted data
                combined_data = row.to_dict()  # Convert index row to dictionary
                combined_data.update(extracted_data)  # Add extracted data
                all_extracted_data.append(combined_data)  # Append to list
            except ET.ParseError:
                print(f"Error parsing {xml_file}.")
            except FileNotFoundError:
                print(f"File {xml_file} not found.")
    
    # Create a DataFrame from the list of dictionaries
    combined_df = pd.DataFrame(all_extracted_data)

    # Remove the "irs:" prefix from the column names
    combined_df.columns = [col.replace('irs:', '') for col in combined_df.columns]

    output_csv_path = f'result/{year}/{year}_csv_index.csv'
    if not os.path.exists(os.path.dirname(output_csv_path)):
        os.makedirs(os.path.dirname(output_csv_path))

    combined_df.to_csv(output_csv_path, index=False)

    print(f"Data extraction completed. Output saved to {output_csv_path}.")

    return combined_df


# Function to extract Schedule C data from XML
def extract_schedule_c_data(year):
    index_csv_path = f'data/index_file/index_{year}.csv'
    
    # Download the index CSV if it does not exist
    if not os.path.exists(index_csv_path):
        index_csv_path = download_index_csv(year)
    
    index_df = pd.read_csv(index_csv_path)

    # Filter the index DataFrame to include only rows with the specified form type
    index_df = index_df[index_df['RETURN_TYPE'] == '990']

    xml_files_path_prefix = f'data/xml_files/{year}/'

    # List to hold all extracted data that has non-empty Schedule C
    valid_schedule_c_data = []

    if year < 2024:
        for _, row in index_df.iterrows():
            xml_folder_path = f"{xml_files_path_prefix}"
            xml_file = f"{xml_folder_path}{row['OBJECT_ID']}_public.xml"
            
            # Download and extract the ZIP file if the XML folder does not exist
            if not os.path.exists(xml_folder_path):
                download_and_extract_zip_legacy(xml_files_path_prefix, year)
            
            try:
                # Extract data for each row
                extracted_data = extract_variables_and_attr_from_xml(xml_file, schedule_c_variables)
                
                # Check if all Schedule C fields are empty
                if any(value for key, value in extracted_data.items() if key in schedule_c_variables):
                    # Combine index data and non-empty Schedule C data
                    combined_data = row.to_dict()  # Convert index row to dictionary
                    combined_data.update(extracted_data)  # Add non-empty Schedule C data
                    valid_schedule_c_data.append(combined_data)  # Append to list
                else:
                    print(f"Skipping OBJECT_ID {row['OBJECT_ID']} due to empty Schedule C fields.")
            except ET.ParseError:
                print(f"Error parsing {xml_file}.")
            except FileNotFoundError:
                print(f"File {xml_file} not found.")
    else:
        for _, row in index_df.iterrows():
            xml_folder_path = f"{xml_files_path_prefix}{row['XML_BATCH_ID']}/"
            xml_file = f"{xml_folder_path}{row['OBJECT_ID']}_public.xml"
            
            # Download and extract the ZIP file if the XML folder does not exist
            if not os.path.exists(xml_folder_path):
                download_and_extract_zip(xml_files_path_prefix, row['XML_BATCH_ID'], year)
            
            try:
                # Extract data for each row
                extracted_data = extract_variables_and_attr_from_xml(xml_file, schedule_c_variables)
                
                # Check if all Schedule C fields are empty
                if any(value for key, value in extracted_data.items() if key in schedule_c_variables):
                    # Combine index data and non-empty Schedule C data
                    combined_data = row.to_dict()  # Convert index row to dictionary
                    combined_data.update(extracted_data)  # Add non-empty Schedule C data
                    valid_schedule_c_data.append(combined_data)  # Append to list
                else:
                    print(f"Skipping OBJECT_ID {row['OBJECT_ID']} due to empty Schedule C fields.")
            except ET.ParseError:
                print(f"Error parsing {xml_file}.")
            except FileNotFoundError:
                print(f"File {xml_file} not found.")
    
    # Create a DataFrame from the list of dictionaries
    valid_schedule_c_df = pd.DataFrame(valid_schedule_c_data)

    # Remove the "irs:" prefix from the column names
    valid_schedule_c_df.columns = [col.replace('irs:', '') for col in valid_schedule_c_df.columns]

    output_schedule_c_csv_path = f'result/{year}/schedule_c_{year}.csv'

    if not os.path.exists(os.path.dirname(output_schedule_c_csv_path)):
        os.makedirs(os.path.dirname(output_schedule_c_csv_path))

    valid_schedule_c_df.to_csv(output_schedule_c_csv_path, index=False)

    print(f"Schedule C data extraction completed. Output saved to {output_schedule_c_csv_path}.")



# Function to extract recipient table from XML
def extract_recipient_table(xml_file, object_id, recipient_variables):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    recipient_data = []
    # Find all elements that match the XPath for recipient tables
    recipient_elements = root.findall('.//irs:RecipientTable', ns)
    
    for element in recipient_elements:
        recipient = {'OBJECT_ID': object_id}
        for var in recipient_variables:
            # Remove '/text()' from the variable
            xpath_expr = var.replace('/text()', '')

            # Split the XPath expression and prepend 'irs:' to each part
            xpath_parts = xpath_expr.split('/')
            # Apply the 'irs:' prefix only to the actual XML elements
            xpath_expr = '/'.join('irs:' + part for part in xpath_parts if part)

            #print(xpath_expr)  # Debugging statement to verify the XPath expression
            
            recipient[var] = element.findtext(xpath_expr, default='', namespaces=ns)
        recipient_data.append(recipient)
    
    return recipient_data


def extract_recipient_data(year):
    index_csv_path = f'data/index_file/index_{year}.csv'
    
    # Download the index CSV if it does not exist
    if not os.path.exists(index_csv_path):
        index_csv_path = download_index_csv(year)
    
    index_df = pd.read_csv(index_csv_path)

    # Filter the index DataFrame to include only rows with the specified form type
    index_df = index_df[index_df['RETURN_TYPE'] == '990']

    all_recipient_data = []

    xml_files_path_prefix = f'data/xml_files/{year}/'

    if year >= 2024:
        for index, row in index_df.iterrows():
            xml_folder_path = f"{xml_files_path_prefix}{row['XML_BATCH_ID']}/"
            xml_file = f"{xml_folder_path}{row['OBJECT_ID']}_public.xml"
            
            # Download and extract the ZIP file if the XML folder does not exist
            if not os.path.exists(xml_folder_path):
                download_and_extract_zip(xml_files_path_prefix, row['XML_BATCH_ID'], year)
            
            try:
                recipient_data = extract_recipient_table(xml_file, row['OBJECT_ID'], recipient_variables)
                all_recipient_data.extend(recipient_data)
            except ET.ParseError:
                print(f"Error parsing {xml_file}.")
            except FileNotFoundError:
                print(f"File {xml_file} not found.")
    else:
        for index, row in index_df.iterrows():
            xml_folder_path = f"{xml_files_path_prefix}"
            xml_file = f"{xml_folder_path}{row['OBJECT_ID']}_public.xml"
            
            # Download and extract the ZIP file if the XML folder does not exist
            if not os.path.exists(xml_folder_path):
                download_and_extract_zip_legacy(xml_files_path_prefix, year)
            
            try:
                recipient_data = extract_recipient_table(xml_file, row['OBJECT_ID'], recipient_variables)
                all_recipient_data.extend(recipient_data)
            except ET.ParseError:
                print(f"Error parsing {xml_file}.")
            except FileNotFoundError:
                print(f"File {xml_file} not found.")
    
    recipient_df = pd.DataFrame(all_recipient_data)

    # Remove the "irs:" prefix from the column names
    recipient_df.columns = [col.replace('irs:', '') for col in recipient_df.columns]

    output_recipient_csv_path = f'result/{year}/recipient_table_{year}.csv'
    if not os.path.exists(os.path.dirname(output_recipient_csv_path)):
        os.makedirs(os.path.dirname(output_recipient_csv_path))
    
    recipient_df.to_csv(output_recipient_csv_path, index=False)

    print(f"Recipient data extraction completed. Output saved to {output_recipient_csv_path}.")


def main(year, form_type, recipient, schedule):
    if year < 2018:
        raise ValueError("Year must be 2018 or later. IRS does not have data before 2018.")
    if form_type != '990':
        raise ValueError("Only form 990 is supported in this version.")

    if recipient:
        extract_recipient_data(year)
    elif schedule == '':
        extract_index_data(year, form_type)
    elif schedule == 'C':
        extract_schedule_c_data(year)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract IRS form data from XML files.")
    parser.add_argument('--year', type=int, default=2024, help='The year of the data to process.')
    parser.add_argument('--form', type=str, default='990', help='The IRS form type to process.')
    parser.add_argument('--recipient', action='store_true', default=False, help='Extract recipient organization data.')
    parser.add_argument('--schedule', type=str, default='', help='The schedule to extract, default is the index data.')


    args = parser.parse_args()

    main(args.year, args.form, args.recipient, args.schedule)
