
import msal
from typing import List
from msal import PublicClientApplication
import requests
import os
from dotenv import load_dotenv,find_dotenv
from loguru import logger
load_dotenv(find_dotenv())
default_graph_uri = 'https://graph.microsoft.com/.default/v1.0/'
default_authority_url = 'https://login.microsoftonline.com/consumers/'

APPLICATION_ID = os.environ.get('APPLICATION_ID')
CLIENT_SECRET= os.environ.get('CLIENT_SECRET')
AZURE_TENANT_ID=os.environ.get('AZURE_TENANT_ID')

import subprocess
import json 

def get_auth_header():
    # Define the request parameters
    url = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_id": APPLICATION_ID,
        "scope": "https://graph.microsoft.com/.default",
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }

    # Make the request and capture the response
    response = requests.post(url, headers=headers, data=data)

    # Extract the access token from the response
    access_token = response.json()["access_token"]

    # Create the Authorization header with the access token as a Bearer token
    auth_header = {"Authorization": f"Bearer {access_token}"}

    # Return the Authorization header
    return auth_header

user_endpoint = default_graph_uri + "me"
response = requests.get(user_endpoint, headers=get_auth_header())
logger.info(response.json())
