import requests
from typing import Dict, List
import pandas as pd
from loguru import logger
import os 

def get_groups(header: Dict[str, str]) -> List[Dict[str, str]]:
    # Get all groups in tenant
    base_url=os.getenv("GRAPH_API_BASE")
    res = requests.get(url=f"{base_url}/groups", headers=header)
    res_str = res.json()
    return res_str


def group_response_to_dataframe(data: List[Dict[str, str]]) -> pd.DataFrame:
    keys = ["id", "createdDateTime", "description", "displayName", "visibility"]
    df = pd.DataFrame(columns=keys)
    for d in data:
        row = {}
        for key in keys:
            row[key] = d[key]
        df = pd.concat([df, pd.DataFrame(row, index=[0])], ignore_index=True)
    return df


def get_group_drives(header: Dict[str, str], groups: pd.DataFrame):
    sites = []
    base_url=os.getenv("GRAPH_API_BASE")
    for row in groups.iterrows():
        logger.info(row)
        id = row[1]["id"]
        logger.info(id)
        res = requests.get(
            url=f"{base_url}/groups/{id}/drive/items/root/children",
            headers=header,
        )
        logger.info(res)
        if res.status_code != 200:
            logger.info(res.json())
            logger.info(res.status_code)
            logger.info(res.text)
            continue
        res = res.json()
        res["GroupName"] = row[1]["displayName"]
        sites.append(res)

    return sites


import re
from typing import Dict, List


def flatten_group_drives(data, parent_key="", sep="."):
    items = {}
    for k, v in data.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_group_drives(v, new_key, sep=sep))
        elif isinstance(v, list):
            for idx, item in enumerate(v):
                list_key = new_key + sep + f"L{idx}"
                if isinstance(item, dict):
                    items.update(flatten_group_drives(item, list_key, sep=sep))
                else:
                    items[list_key] = item
        else:
            items[new_key] = v
    return items


def extract_group_id(odata_context: str) -> str:
    match = re.search(r"groups\('(.+?)'\)", odata_context)
    return match.group(1) if match else None


def convert_drives_to_dataframe_by_group(
    data_array: List[Dict[str, pd.DataFrame]],
) -> Dict[str, pd.DataFrame]:
    result_dict = {}
    for item in data_array:
        odata_context = item.get("@odata.context", "")
        group_name = item.get("GroupName", "")
        group_id = extract_group_id(odata_context)
        if group_id:
            value_items = item.get("value", [])
            # Filter out groups with empty values
            if not value_items:
                continue
            flattened_data = [
                flatten_group_drives(sub_item) for sub_item in value_items
            ]
            df = pd.DataFrame(flattened_data)
            date_columns = [col for col in df.columns if "DateTime" in col]
            for col in date_columns:
                df[col] = pd.to_datetime(df[col])
            df["GroupID"] = group_id
            df["GroupName"] = group_name
            new_order = ["GroupName", "name", "size"] + sorted(
                [col for col in df.columns if col not in ["GroupName", "name", "size"]]
            )
            df = df.reindex(columns=new_order)
            result_dict[group_id] = df
    return result_dict


def convert_drives_to_dataframe(
    data_array: List[Dict[str, pd.DataFrame]],
) -> (pd.DataFrame, pd.DataFrame):
    result_df = pd.DataFrame()
    for item in data_array:
        odata_context = item.get("@odata.context", "")
        group_name = item.get("GroupName", "")
        group_id = extract_group_id(odata_context)
        if group_id:
            value_items = item.get("value", [])
            # Filter out groups with empty values
            if not value_items:
                continue
            flattened_data = [
                flatten_group_drives(sub_item) for sub_item in value_items
            ]
            df = pd.DataFrame(flattened_data)
            date_columns = [col for col in df.columns if "DateTime" in col]
            for col in date_columns:
                df[col] = pd.to_datetime(df[col])
            df["GroupID"] = group_id
            df["GroupName"] = group_name

            result_df = pd.concat([result_df, df], ignore_index=True)

    # Splitting the DataFrame into two based on the "@microsoft.graph.downloadUrl" column
    result_df["Path"] = result_df["GroupName"] + "/" + result_df["name"]
    files_df = result_df[result_df["@microsoft.graph.downloadUrl"].notna()]
    result_df = result_df[result_df["@microsoft.graph.downloadUrl"].isna()]

    drop_cols = [
        "@microsoft.graph.downloadUrl",
        "parentReference.path",
        "parentReference.driveType",
        "shared.scope",
    ]
    result_df = result_df.drop(columns=drop_cols)
    result_df = result_df.query("size > 0").sort_values(by=["size"], ascending=False)

    return result_df, files_df


# Identifying information
ID_COLS = [
    "GroupID",
    "id",
    "parentReference.driveId",
    "parentReference.id",
    "parentReference.siteId",
]

# Information about changes and modifications
CHANGE_INFO = [
    "createdDateTime",
    "fileSystemInfo.createdDateTime",
    "fileSystemInfo.lastModifiedDateTime",
    "lastModifiedDateTime",
    "cTag",
    "eTag",
]

# Information related to users
USER_COLS = [
    "createdBy.user.displayName",
    "createdBy.user.email",
    "createdBy.user.id",
    "lastModifiedBy.user.displayName",
    "lastModifiedBy.user.email",
    "lastModifiedBy.user.id",
]

# Information related to applications
APP_COLS = [
    "createdBy.application.displayName",
    "createdBy.application.id",
    "lastModifiedBy.application.displayName",
    "lastModifiedBy.application.id",
]

# Additional information
ROOT_COLS = [
    "Path",
]

DIR_COLS = ["size", "folder.childCount", "webUrl", "GroupName", "name"]

FILE_INFO = ["file.hashes.quickXorHash", "file.mimeType", "specialFolder.name"]
