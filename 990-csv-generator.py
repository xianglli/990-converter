import xml.etree.ElementTree as ET
import pandas as pd
import argparse
import os
import requests
import zipfile
import subprocess

# Namespace dictionary for XPath expressions
ns = {'irs': 'http://www.irs.gov/efile'}

# Function to extract variables from XML with refined XPath expressions
def extract_variables_from_xml(xml_file, variables):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    extracted_data = {}
    for var in variables:
        xpath_expr = var.replace('/text()', '')
        element = root.find(xpath_expr, ns)
        extracted_data[var] = element.text if element is not None else None
    
    return extracted_data

# List of variables to extract
all_variables = [
    'irs:ReturnHeader/irs:Filer/irs:EIN',
    'irs:ReturnHeader/irs:Filer/irs:BusinessName/irs:BusinessNameLine1Txt',
    'irs:ReturnHeader/irs:Filer/irs:BusinessName/irs:BusinessNameLine2Txt',
    'irs:ReturnHeader/irs:TaxYr',
    'irs:ReturnData/irs:IRS990/irs:ActivityOrMissionDesc',
    'irs:ReturnData/irs:IRS990/irs:MissionDesc',
    'irs:ReturnData/irs:IRS990/irs:Desc',
    'irs:ReturnData/irs:IRS990/irs:ProgSrvcAccomActy2Grp/irs:Desc',
    'irs:ReturnData/irs:IRS990/irs:ProgSrvcAccomActy3Grp/irs:Desc',
    'irs:ReturnData/irs:IRS990/irs:ProgSrvcAccomActyOtherGrp/irs:Desc',
    'irs:ReturnData/irs:IRS990/irs:GrantsToOrganizationsInd',
    'irs:ReturnData/irs:IRS990/irs:GrantsToIndividualsInd',
    'irs:ReturnData/irs:IRS990/irs:ReportProgRelInvesInd',
    'irs:ReturnData/irs:IRS990/irs:FederatedCampaignsAmt',
    'irs:ReturnData/irs:IRS990/irs:MembershipDuesAmt',
    'irs:ReturnData/irs:IRS990/irs:FundraisingEventsAmt',
    'irs:ReturnData/irs:IRS990/irs:RelatedOrganizationsAmt',
    'irs:ReturnData/irs:IRS990/irs:GovernmentGrantsAmt',
    'irs:ReturnData/irs:IRS990/irs:NoncashContributionsAmt',
    'irs:ReturnData/irs:IRS990/irs:AllOtherContributionsAmt',
    'irs:ReturnData/irs:IRS990/irs:TotalContributionsAmt',
    'irs:ReturnData/irs:IRS990/irs:ProgramServiceRevenueGrp/irs:Desc',
    'irs:ReturnData/irs:IRS990/irs:ProgramServiceRevenueGrp/irs:BusinessCd',
    'irs:ReturnData/irs:IRS990/irs:ProgramServiceRevenueGrp/irs:TotalRevenueColumnAmt',
    'irs:ReturnData/irs:IRS990/irs:ProgramServiceRevenueGrp/irs:RelatedOrExemptFuncIncomeAmt',
    'irs:ReturnData/irs:IRS990/irs:TotalOthProgramServiceRevGrp/irs:TotalRevenueColumnAmt',
    'irs:ReturnData/irs:IRS990/irs:TotalOthProgramServiceRevGrp/irs:RelatedOrExemptFuncIncomeAmt',
    'irs:ReturnData/irs:IRS990/irs:TotalOthProgramServiceRevGrp/irs:UnrelatedBusinessRevenueAmt',
    'irs:ReturnData/irs:IRS990/irs:TotalOthProgramServiceRevGrp/irs:ExclusionAmt',
    'irs:ReturnData/irs:IRS990ScheduleD/irs:DonorAdvisedFundsHeldCnt',
    'irs:ReturnData/irs:IRS990ScheduleD/irs:FundsAndOtherAccountsHeldCnt',
    'irs:ReturnData/irs:IRS990ScheduleD/irs:DonorAdvisedFundsContriAmt',
    'irs:ReturnData/irs:IRS990ScheduleD/irs:FundsAndOtherAccountsContriAmt',
    'irs:ReturnData/irs:IRS990ScheduleD/irs:DonorAdvisedFundsGrantsAmt',
    'irs:ReturnData/irs:IRS990ScheduleD/irs:FundsAndOtherAccountsGrantsAmt',
    'irs:ReturnData/irs:IRS990ScheduleD/irs:DonorAdvisedFundsValEOYAmt',
    'irs:ReturnData/irs:IRS990ScheduleD/irs:FundsAndOtherAccountsVlEOYAmt',
    'irs:ReturnData/irs:IRS990ScheduleD/irs:CYEndwmtFundGrp/irs:BeginningYearBalanceAmt',
    'irs:ReturnData/irs:IRS990ScheduleD/irs:CYEndwmtFundGrp/irs:ContributionsAmt',
    'irs:ReturnData/irs:IRS990ScheduleD/irs:CYEndwmtFundGrp/irs:InvestmentEarningsOrLossesAmt',
    'irs:ReturnData/irs:IRS990ScheduleD/irs:CYEndwmtFundGrp/irs:GrantsOrScholarshipsAmt',
    'irs:ReturnData/irs:IRS990ScheduleD/irs:CYEndwmtFundGrp/irs:AdministrativeExpensesAmt',
    'irs:ReturnData/irs:IRS990ScheduleD/irs:CYEndwmtFundGrp/irs:OtherExpendituresAmt',
    'irs:ReturnData/irs:IRS990ScheduleD/irs:CYEndwmtFundGrp/irs:EndYearBalanceAmt',
    'irs:ReturnData/irs:IRS990ScheduleD/irs:BoardDesignatedBalanceEOYPct',
    'irs:ReturnData/irs:IRS990ScheduleD/irs:PrmnntEndowmentBalanceEOYPct',
    'irs:ReturnData/irs:IRS990ScheduleD/irs:TermEndowmentBalanceEOYPct',
    'irs:ReturnData/irs:IRS990ScheduleD/irs:EndowmentsHeldUnrelatedOrgInd',
    'irs:ReturnData/irs:IRS990ScheduleD/irs:EndowmentsHeldRelatedOrgInd',
    'irs:ReturnData/irs:IRS990ScheduleD/irs:TemporarilyRestrictedEndowment',
    'irs:ReturnData/irs:IRS990ScheduleD/irs:InvestmentsProgramRelated/irs:Description',
    'irs:ReturnData/irs:IRS990ScheduleD/irs:InvestmentsProgramRelated/irs:BookValue',
    'irs:ReturnData/irs:IRS990ScheduleI/irs:GrantRecordsMaintainedInd',
    'irs:ReturnData/irs:IRS990ScheduleI/irs:Total501c3OrgCnt',
    'irs:ReturnData/irs:IRS990ScheduleI/irs:TotalOtherOrgCnt',
    'irs:ReturnData/irs:IRS990ScheduleI/irs:SupplementalInformationDetail/irs:FormAndLineReferenceDesc',
    'irs:ReturnData/irs:IRS990ScheduleI/irs:SupplementalInformationDetail/irs:ExplanationTxt',
]

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
    
    if not os.path.exists(xml_files_path_prefix):
        os.makedirs(xml_files_path_prefix)
    
    response = requests.get(zip_url)
    response.raise_for_status()  # Check that the request was successful
    
    with open(local_zip_path, 'wb') as file:
        file.write(response.content)

    xml_files_path = f'{xml_files_path_prefix}{xml_batch_id}/'
    
    try:
        subprocess.run(['unzip', local_zip_path, '-d', xml_files_path], check=True)
    except subprocess.CalledProcessError as e:
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
        

def main(year, form_type):
    index_csv_path = f'data/index_file/index_{year}.csv'
    
    # Download the index CSV if it does not exist
    if not os.path.exists(index_csv_path):
        index_csv_path = download_index_csv(year)
    
    index_df = pd.read_csv(index_csv_path, nrows=1000)

    # Filter the index DataFrame to include only rows with the specified form type
    index_df = index_df[index_df['RETURN_TYPE'] == form_type]

    # Create a DataFrame to hold the combined data
    combined_df = index_df.copy()

    xml_files_path_prefix = f'data/xml_files/{year}/'

    if year < 2024:
        for index, row in index_df.iterrows():
            xml_folder_path = f"{xml_files_path_prefix}"
            xml_file = f"{xml_folder_path}{row['OBJECT_ID']}_public.xml"
            
            # Download and extract the ZIP file if the XML folder does not exist
            if not os.path.exists(xml_folder_path):
                download_and_extract_zip_legacy(xml_files_path_prefix, year)
            
            try:
                extracted_data = extract_variables_from_xml(xml_file, all_variables)
                for var, value in extracted_data.items():
                    combined_df.at[index, var] = value
            except ET.ParseError:
                print(f"Error parsing {xml_file}.")
            except FileNotFoundError:
                print(f"File {xml_file} not found.")
    else:
        for index, row in index_df.iterrows():
            xml_folder_path = f"{xml_files_path_prefix}{row['XML_BATCH_ID']}/"
            xml_file = f"{xml_folder_path}{row['OBJECT_ID']}_public.xml"
            
            # Download and extract the ZIP file if the XML folder does not exist
            if not os.path.exists(xml_folder_path):
                download_and_extract_zip(xml_files_path_prefix, row['XML_BATCH_ID'], year)
            
            try:
                extracted_data = extract_variables_from_xml(xml_file, all_variables)
                for var, value in extracted_data.items():
                    combined_df.at[index, var] = value
            except ET.ParseError:
                print(f"Error parsing {xml_file}.")
            except FileNotFoundError:
                print(f"File {xml_file} not found.")
    
    # Remove the "irs:" prefix from the column names
    combined_df.columns = [col.replace('irs:', '') for col in combined_df.columns]

    output_csv_path = f'result/{year}_csv_index.csv'
    if not os.path.exists(os.path.dirname(output_csv_path)):
        os.makedirs(os.path.dirname(output_csv_path))
    
    combined_df.to_csv(output_csv_path, index=False)

    print(f"Data extraction completed. Output saved to {output_csv_path}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract IRS form data from XML files.")
    parser.add_argument('--year', type=int, default=2024, help='The year of the data to process.')
    parser.add_argument('--form', type=str, default='990', help='The IRS form type to process.')

    args = parser.parse_args()

    main(args.year, args.form)
