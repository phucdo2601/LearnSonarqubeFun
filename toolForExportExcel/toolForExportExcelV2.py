import requests
import pandas as pd
import configparser

# Create a ConfigParser object
config = configparser.ConfigParser()

#Read the 'env.ini' file
config.read('env.ini')

#Get data from SonarQube API
port = config['SONARQUBE_INFO']['port']
componentKeys = config['SONARQUBE_INFO']['componentKeys']
defaultRec = config['SONARQUBE_INFO']['defaultRec']
defultPage = config['SONARQUBE_INFO']['defaultPage']
baseUrl= f'http://localhost:{port}/api/issues/search?componentKeys={componentKeys}'
url = f'{baseUrl}&ps={defaultRec}'
token = config['SONARQUBE_INFO']['token']

# Output values
print(f'The value of the default record: {defaultRec}')
print(f'The value of the default page: {defultPage}')
print(f'The value of the base url: {baseUrl}')
print(f'The value of the calling url: {url}')
print(f'The value of the token: {token}')

# Function to fetch issues from a specific page
def fetch_issues_from_page(page):
    response =  requests.get(f'{url}&page={page}', auth=(token, ''))
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}")
        return None
    


# First request to get total page
initial_response = fetch_issues_from_page(1)

# Create data list to hold the extracted data
extracted_data = []

if initial_response:
    # Get total pages from the initial response
    total_pages = initial_response['paging']['total'] // initial_response['paging']['pageSize']
    if initial_response['paging']['total'] % initial_response['paging']['pageSize']!= 0:
        total_pages += 1
    print(f'The number of pages: {total_pages} pages')

    # Loop through the remaining pages and gather all data
    for page in range(1, total_pages + 1):
        response = fetch_issues_from_page(page)
        if response:
            for issue in response['issues']:
                # Extract specific field
                key = issue['key']
                component = issue.get('component', 'N/A')
                line = issue.get('textRange', {}).get('startLine', 'N/A')
                project = issue.get('project', 'N/A')
                warningMessage = issue.get('message', 'N/A')
                severity = issue.get('severity', 'N/A')
                issue_type = issue.get('type', 'N/A')
                impactsList = issue['impacts']
                for impact in impactsList:
                    if impact.get('severity') == 'MEDIUM' or impact.get('severity') == 'HIGH':
                        warningLevel = impact.get('severity')
                        # Append the data to the list
                        extracted_data.append({
                            'Key': key,
                            'Component': component,
                            'Project': project,
                            'Line': line,
                            'Warning Message': warningMessage,
                            'Severity': severity,
                            'Type': issue_type,
                            'Warning Level': warningLevel,
                            
                        })

    # Convert the list to a pandas DataFrame
    df = pd.DataFrame(extracted_data)

    # Export DataFrame to an Excel file
    df.to_excel('sonarqube_issues_summary_with_impacts02.xlsx', index=False)
    print("Data exported to 'sonarqube_issues_summary_with_impacts02.xlsx'")

