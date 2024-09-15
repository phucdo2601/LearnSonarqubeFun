import requests
import pandas as pd

# Get data from SonarQube API
defaultRec = 500
defultPage = 1
baseUrl= "http://localhost:9000/api/issues/search?componentKeys=test-csharp-net-7-api-pro"
url = f'{baseUrl}&ps={defaultRec}'
token = "sqp_abeab0b371f5449d76b022eaff2c1f8b8e79ec38"

# Function to fetch issues from a specific page
def fetch_issues_from_page(page):
    print(f'{url}&page={page}')
    response = requests.get(f'{url}&page={page}', auth=(token, ''))
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}")
        return None
    
# First request to get total page
initial_response = fetch_issues_from_page(1)

#Create data list to hold the extracted data
extracted_data = []

if initial_response:
    # Get total pages from the initial response
    total_pages = initial_response['paging']['total'] // initial_response['paging']['pageSize']
    if initial_response['paging']['total'] % initial_response['paging']['pageSize'] != 0:
        total_pages += 1
    print(f'The number of pages: {total_pages} pages')

    # Loop through the remaining pages and gather all data
    for page in range(1, total_pages + 1):
        response = fetch_issues_from_page(page)
        if response:
            for issue in response['issues']:
                # Extract specific field
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
                            'Component': component,
                            'Project': project,
                            'Line': line,
                            'Warning Message': warningMessage,
                            'Severity': severity,
                            'Type': issue_type,
                            'Warning Level': warningLevel,
                            
                        })
                
                
                
    # Convert the list to a pandas Dataframe
    df = pd.DataFrame(extracted_data)
    
    # Export DataFrame to an Excel file
    df.to_excel('sonarqube_issues_summary_with_impacts01.xlsx', index=False)
    print("Data exported to 'onarqube_issues_summary_with_impacts01.xlsx'")
else:
    print(f"Failed to retrieve data: {initial_response.status_code}, {initial_response.text}")