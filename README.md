# IRS Form 990 Data Extractor

This project extracts data from IRS Form 990 XML files, including recipient table data. It supports processing data from 2018 and onwards.

## Features

- Download index CSV files from the IRS website.
- Download and extract ZIP files containing XML data.
- Extract specific data variables from XML files.
- Extract recipient table data from XML files.
- Save extracted data to CSV files.

## Requirements

- Python 3.6+
- Required Python packages:
  - `pandas`
  - `requests`
  - `xml.etree.ElementTree`
  - `argparse`

## Setup

1. Clone this repository to your local machine.
2. Install the required Python packages using pip:

    ```bash
    pip install pandas requests
    ```

## Usage

### Extract Main Data

To extract the main data from IRS Form 990 XML files:

```bash
python your_script.py --year <YEAR> --form 990
```

### Extract Recipient Data

To extract recipient data from IRS Form 990 XML files:

```bash
python your_script.py --year <YEAR> --recipient
```

### Example

Extract main data for the year 2024:

```bash
python your_script.py --year 2024 --form 990
```

Extract recipient data for the year 2024:

```bash
python your_script.py --year 2024 --recipient
```

## Files

- `your_script.py`: Main script to run the data extraction.
- `data/index_file/`: Directory where the index CSV files will be saved.
- `data/xml_files/<YEAR>/`: Directory where the XML files will be saved and extracted.
- `result/<YEAR>/`: Directory where the extracted CSV files will be saved.

## Functions

### extract_recipient_data

Extract recipient data from IRS Form 990 XML files for a specified year.

**Parameters:**

- `year` (int): The year of the data to process.

### extract_variables_from_xml

Extract specific variables from an XML file.

**Parameters:**

- `xml_file` (str): The path to the XML file.
- `variables` (list): A list of XPath expressions to extract.

**Returns:**

- A dictionary with the extracted data.

### extract_recipient_table

Extract recipient table data from an XML file.

**Parameters:**

- `xml_file` (str): The path to the XML file.
- `object_id` (str): The OBJECT_ID of the XML file.
- `recipient_variables` (list): A list of XPath expressions to extract from the recipient table.

**Returns:**

- A list of dictionaries with the extracted recipient data.

### download_index_csv

Download the index CSV file from the IRS website for a specified year.

**Parameters:**

- `year` (int): The year of the data to download.

**Returns:**

- The path to the downloaded index CSV file.

### download_and_extract_zip

Download and extract a ZIP file containing XML data.

**Parameters:**

- `xml_files_path` (str): The path to save the extracted XML files.
- `xml_batch_id` (str): The batch ID of the XML files to download.
- `year` (int): The year of the data to download.

### download_and_extract_zip_legacy

Download and extract ZIP files containing XML data for legacy years (2018-2023).

**Parameters:**

- `xml_files_path` (str): The path to save the extracted XML files.
- `year` (int): The year of the data to download.

## Note for Windows Users

The `unzip` command is not natively available on Windows. 
## License

This project is licensed under the MIT License.
