import jwt
import requests
import json
import urllib3
from pathlib import Path
from dateutil.parser import parse
from datetime import datetime
import unicodedata
import string
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sign_in_url = "https://gatekeeper.neat.com/signin"
get_item_url = "https://duge.neat.com/cloud/items"
get_root_url = "https://duge.neat.com/cloud/folders/root"
get_folder_url = "https://duge.neat.com/cloud/folders"

valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
char_limit = 255

USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
BASE_EXPORT_PATH = os.getenv('BASE_PATH')
LOG_LEVEL = os.getenv('LOG_LEVEL')


def neat_login():
    if LOG_LEVEL in ["Debug", "Info", "Error"]:
        print('UserName: ' + USERNAME)
    sign_in_payload = json.dumps({'username': USERNAME, 'password': PASSWORD, 'scope': 'JAWN'})

    sign_in_headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json;charset=UTF-8'
    }

    login_response = requests.request("POST", sign_in_url, headers=sign_in_headers, data=sign_in_payload, verify=False)

    json_data = login_response.json()
    global encoded_jwt
    global access_token
    global authorization
    global account_number
    encoded_jwt = json_data["token"]
    access_token = json_data["access_token"]
    authorization = 'OAuth ' + access_token
    account_number = json.dumps(jwt.decode(encoded_jwt,
                                           options={"verify_signature": False})["data"]["accountId"]).replace('"', '')

    global get_item_header
    get_item_header = {'Authorization': authorization,
                       'Pragma': 'no-cache',
                       'x-neat-account-id': account_number,
                       'Content-Type': 'application/json;charset=UTF-8',
                       'Accept': 'application/json, text/plain, */*'}
    if LOG_LEVEL in ["Debug", "Info", "Error"]:
        print("account_number : " + account_number)
    if LOG_LEVEL in ["Debug"]:
        print("authorization : " + authorization)


def get_root_folder(_base):
    get_root_response = requests.request("GET",
                                         get_root_url,
                                         headers=get_item_header,
                                         data={},
                                         verify=False)
    if LOG_LEVEL in ["Debug"]:
        print(get_root_response.json())

    for folder in get_root_response.json()["rootFolder"]["folders"]:
        get_folder(folder["webid"], _base)


def get_folder(_folder_id, _base):
    if LOG_LEVEL in ["Debug"]:
        print("Folder ID : " + _folder_id)
    get_folder_response = requests.request("POST",
                                           get_folder_url,
                                           headers=get_item_header,
                                           data=json.dumps({"folders": [_folder_id]}),
                                           verify=False)
    folder = get_folder_response.json()["folders"][0]
    _base = _base + "/" + clean_filename(folder["name"])
    if LOG_LEVEL in ["Debug"]:
        print("Folder Name : " + folder["name"])
        print("Path : " + _base)
    process_items_in_folder(_folder_id, _base)

    for folder in folder["folders"]:
        get_folder(folder, _base)


def process_items_in_folder(_folder_id, _base):
    if LOG_LEVEL in ["Debug"]:
        print("Folder ID : " + _folder_id)
    get_item_payload = json.dumps(
        {"filters": [{"parent_id": _folder_id}, {"type": "$all_item_types"}], "page": 1,
         "page_size": "25", "sort_by": [["created_at", "desc"]], "utc_offset": -4})
    get_item_response = requests.request("POST",
                                         get_item_url,
                                         headers=get_item_header,
                                         data=get_item_payload,
                                         verify=False)
    entities = get_item_response.json()

    for entity in entities["entities"]:
        item_id = entity["webid"]
        item_name = entity["name"]
        item_type = entity["type"]
        item_description = entity["description"]
        item_created_at = parse(entity["created_at"])
        item_parent_id = entity["parent_id"]
        item_download_url = entity["download_url"]
        item_file_source = entity["file_source"]
        if not item_name:
            item_name = item_type + "_" + item_file_source + "_" + item_id

        item_export_file_name = clean_filename(item_name + "_" + item_created_at.strftime("%Y_%m_%d") + ".pdf")
        item_export_full_path = _base + "/" + item_export_file_name
        if LOG_LEVEL in ["Debug"]:
            print("item_id : " + item_id)
            print("item_type : " + item_type)
            print("item_name : " + item_name)
            print("item_description : " + item_description)
            print("item_export_file_name : " + item_export_file_name)
            print("item_export_full_path : " + item_export_full_path)
            print("item_parent_id : " + item_parent_id)
        if not item_download_url:
            _log_entry = {"failure_dt": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                          "webid": item_id,
                          "error": "Not able to export", "item_object": entity}
            if LOG_LEVEL in ["Debug", "Info", "Error"]:
                print(_log_entry)
        else:
            download_file(item_download_url, item_export_full_path, _base, item_id)


def download_file(_download_url, _full_path, _base, _item_number):
    if LOG_LEVEL in ["Debug"]:
        print(_download_url)
        print(_full_path)
    Path(_base).mkdir(parents=True, exist_ok=True)
    open(_full_path, 'wb+').write(requests.get(_download_url, allow_redirects=True, verify=False).content)
    _log_entry = {"export_dt": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                  "webid": _item_number,
                  "export_full_path": _full_path}
    if LOG_LEVEL in ["Debug", "Error"]:
        print(_log_entry)


def clean_filename(filename, whitelist=valid_filename_chars, replace=' '):
    # replace spaces
    for r in replace:
        filename = filename.replace(r, '_')

    # keep only valid ascii chars
    cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()

    # keep only whitelisted chars
    cleaned_filename = ''.join(c for c in cleaned_filename if c in whitelist)
    return cleaned_filename[:char_limit]


def __main():
    print("Start Export")
    neat_login()
    get_root_folder(BASE_EXPORT_PATH)


__main()
