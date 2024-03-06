import requests

# waiting for API key from Semantic Scholar (5/3/24)
def getSemanticData():
    # Define the API endpoint URL
    url = 'https://api.semanticscholar.org/graph/v1/paper/search'

    # More specific query parameter
    query_params = {'query': 'semantic scholar platform',
                    'limit': 3}

    # Directly define the API key (Reminder: Securely handle API keys in production environments)
    api_key = 'K1V9sxPoyV8qu2JcxMx6e3FDi2x3vJVM4kLD3PJO'  

    # Define headers with API key
    headers = {'x-api-key': api_key}

    # Send the API request
    response = requests.get(url, params=query_params, headers=headers)

    # Check response status
    if response.status_code == 200:
        response_data = response.json()
        # Process and print the response data as needed
        print(response_data)
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")
        
getSemanticData()