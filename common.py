import json

import pandas as pd
import re
import requests
from config import *

def open_excel_file(path):
    xl_file = pd.ExcelFile(path)

    dfs = {sheet_name: xl_file.parse(sheet_name)
           for sheet_name in xl_file.sheet_names}

    return dfs


def clean_name(name):
    return re.sub(r"[^a-z0-9]+", "", name.lower())


def get_sheet(dfs, sheet_name):
    if sheet_name in dfs:
        return dfs[sheet_name]
    else:
        new_sheet_name = clean_name(sheet_name)
        for key in dfs.keys():
            key_name = clean_name(key)

            if key_name == new_sheet_name:
                return dfs[key]

        # we have not found any sheet matching full name, lets check starts with
        for key in dfs.keys():
            key_name = clean_name(key)

            if key_name.startswith(new_sheet_name):
                return dfs[key]


def get_column_index(df, column_name):
    new_column_name = clean_name(column_name)
    for i, name in enumerate(df.columns.values.tolist()):
        new_name = clean_name(name)
        if new_name.startswith(new_column_name):
            return i


def login_egov(username, password, tenant_id, user_type="EMPLOYEE"):
    resp = requests.post(URL_LOGIN,data={
        "username": username,
        "password": password,
        "grant_type": "password",
        "scope": "read",
        "tenantId": tenant_id,
        "userType": user_type
    }, headers = {
        "Authorization": "Basic ZWdvdi11c2VyLWNsaWVudDplZ292LXVzZXItc2VjcmV0"
    })

    assert resp.status_code == 200, "Login should respond with 200: " + json.dumps(resp.json(), indent=2)
    return resp.json()


def open_google_spreadsheet(link_or_id_or_path: str, sheet_name: str=None):
    import os
    if os.path.isfile(link_or_id_or_path):
        return open_excel_file(link_or_id_or_path)

    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_AUTH_CONFIG, scope)

    gc = gspread.authorize(credentials)

    if link_or_id_or_path.startswith("http"):
        wks = gc.open_by_url(link_or_id_or_path)
    else:
        wks = gc.open_by_key(link_or_id_or_path)

    dfs = {}

    for wk in wks.worksheets():
        if sheet_name is None:
            dfs[wk.title] = pd.DataFrame(wk.get_all_records())
        elif clean_name(sheet_name) == clean_name(wk.title):
            dfs[wk.title] = pd.DataFrame(wk.get_all_records())

    return dfs, wks