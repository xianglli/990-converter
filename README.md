# IRS Form 990 Data Extractor

## Purpose

The IRS Form 990 Data Extractor is a Python script designed to automate the process of downloading, extracting, and processing IRS Form 990 data from XML files. The script supports extracting specific variables from the XML files and consolidating them into a CSV file. This tool is useful for researchers, analysts, and organizations that need to work with IRS Form 990 data for non-profits.

## Prerequisites

To run this script, you need the following:

1. **Python 3.6+**: Ensure you have Python installed on your system.
2. **Required Python Libraries**: Install the necessary Python libraries using `pip`.

### Step-by-Step Instructions

### 1. Install Python

If you do not have Python installed on your computer, follow these steps to install it:

- **Windows**: Download Python from the official website [python.org](https://www.python.org/downloads/). Run the installer and follow the instructions. Note we do not currently support Windows since we use "unzip" command.
- **macOS**: Python 2.x is installed by default on macOS. However, you should install Python 3.x from the official website [python.org](https://www.python.org/downloads/). Alternatively, you can use Homebrew by running `brew install python3`.
- **Linux**: Python is usually pre-installed on most Linux distributions. If not, use your package manager to install it (e.g., `sudo apt-get install python3` for Debian-based distributions).

### 2. Install Required Python Libraries

Open a command prompt or terminal window and install the required libraries by running:

```bash
pip install requests pandas
```

### 3. Download the Script

Download the script files from the repository. You can do this by downloading the ZIP file from the repository and extracting it to a folder on your computer, or by using `git` if you are familiar with it:

```bash
git clone https://github.com/xianglli/irs-form-990-extractor.git
cd irs-form-990-extractor
```

### 4. Run the Script

Open a command prompt or terminal window and navigate to the folder where you downloaded the script. Run the script with the following command:

```bash
python 990-csv-generator.py --year=<year> --form=<form_type>
```

Replace `<year>` with the desired year (e.g., 2023) and `<form_type>` with `990`. For example:

```bash
python 990-csv-generator.py --year=2023 --form=990
```

### Notes:

- The script only supports IRS Form 990 for the years 2018 and later.
- The output will be saved in the `result` directory within the project folder.

## Example

To extract data for the year 2023:

1. Open a command prompt or terminal.
2. Navigate to the directory where the script is located.
3. Run the script with the appropriate parameters:

```bash
python 990-csv-generator.py --year=2023 --form=990
```

## Troubleshooting

If you encounter any issues, ensure that:

1. You have installed Python 3.6 or later.
2. You have installed the required Python libraries (`requests` and `pandas`).
3. You have correctly specified the year and form type when running the script.

For additional help, refer to the official documentation of the libraries used or seek assistance from a knowledgeable individual or community forums.

## Contributing

If you wish to contribute to this project, please fork the repository and submit pull requests. Any improvements or bug fixes are welcome!

## License

This project is licensed under the MIT License.
