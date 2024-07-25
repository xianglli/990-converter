import requests
from bs4 import BeautifulSoup
import os
import zipfile
from io import BytesIO

# Define the URL
url = "https://www.irs.gov/charities-non-profits/form-990-series-downloads"

# Create a directory to save the files
if not os.path.exists('downloaded_files'):
    os.makedirs('downloaded_files')

# Get the HTML content from the URL
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all links to the ZIP files
links = soup.find_all('a')
file_links = [url + link['href'] for link in links if link.get('href') and link['href'].endswith('.zip')]

# Download and extract each ZIP file
for file_link in file_links:
    file_name = file_link.split('/')[-1]
    file_path = os.path.join('downloaded_files', file_name)
    
    # Download the ZIP file
    zip_response = requests.get(file_link)
    

print('All files have been downloaded and extracted.')
