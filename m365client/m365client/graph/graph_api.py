import os

client_thumbprint = os.getenv("PIPELINE_THUMBPRINT")
tenant_id = os.getenv("TENANT_ID")
# PIPELINE_CLIENT_SECRET_ID
from msal import ConfidentialClientApplication, PublicClientApplication
import requests
import json
import webbrowser
from typing import Dict, Optional, List
from loguru import logger


def get_application_graph_client() -> ConfidentialClientApplication:
    client_id = os.getenv("PIPELINE_CLIENT_ID")
    authority = os.getenv("AUTHORITY_ENDPOINT")
    client_secret = os.getenv("PIPELINE_CLIENT_SECRET")
    return ConfidentialClientApplication(
        client_id=client_id,
        authority=authority,
        client_credential=client_secret,
    )


def get_deferred_graph_client() -> PublicClientApplication:
    scopes = os.getenv("DEFAULT_GRAPH_SCOPE")
    client_id = os.getenv("PIPELINE_CLIENT_ID")
    authority = os.getenv("AUTHORITY_ENDPOINT")
    client = PublicClientApplication(
        client_id=client_id,
        authority=authority,
    )
    flow = client.initiate_device_flow(scopes=scopes)
    print(flow)
    webbrowser.open(flow["verification_uri"])


def get_graph_header() -> Dict[str, str]:
    msal_app = get_application_graph_client()
    scopes_graph  = os.getenv("DEFAULT_GRAPH_SCOPE")
    logger.info(scopes_graph)
    logger.info(type(scopes_graph))
    try:
        results: Optional[
            Dict[str, str]
        ] = msal_app.acquire_token_for_client(  # type:ignore
            [scopes_graph]
        )
        logger.info(results)
        access_token: Optional[str] = results.get("access_token")
        if access_token is None:
            raise Exception("No results returned from MSAL when acquiring token")
    except Exception as e:
        raise Exception(f"Error acquiring token: {e}")

    header = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    return header


def default_graph_call():
    msal_app = get_application_graph_client()
    base_url=os.getenv("GRAPH_API_BASE")
    print(msal_app)

    graph_header = get_graph_header()

    res = requests.get(
        url=f"{base_url}/users", headers=graph_header
    )
    return json.dumps(res.json(), indent=4)
