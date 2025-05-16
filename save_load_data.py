import json
import os

def save_folder_data(file_path, folder_name, apps):
    data = {}

    # load file if exists
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}

    # update folder data
    data[folder_name] = {"apps": apps}

    # save file with new structure
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def load_apps_from_folder(file_path, folder_name):
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
            return data.get(folder_name, {}).get("apps", [])
        except json.JSONDecodeError:
            return []


### USAGE:

# save_folder_data("data.json","Folder",["app1","app2"])

# apps = load_apps_from_folder("data.json", "Folder")