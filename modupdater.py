#!/usr/bin/env python3
import sys
import json
import os
import requests
import re
from bs4 import BeautifulSoup

url_base = "https://mods.factorio.com"

def getModUrl(mod_name):
    return url_base + "/?q=" + mod_name

def getOnlineVersion(mod_name):
    url = getModUrl(mod_name)
    site = requests.get(url)
    soup = BeautifulSoup(site.text, 'html.parser')
    for data in soup.findAll('script'):
        json_str = data.string
        if not json_str:
            continue
        #Clean String
        json_str = json_str.lstrip()
        json_str = json_str.lstrip("window.__INITIAL_STATE__ = ")
        json_str = json_str.rstrip()
        json_str = json_str.rstrip(";")
        # Transform to dict
        json_data = json.loads(json_str)
        version = json_data["mods"]["modsPages"][0][0]["latest_release"]["info_json"]["version"]
        download_url = json_data["mods"]["modsPages"][0][0]["latest_release"]["download_url"]
        download = url_base + download_url
        return (mod_name, version, download)

def getMods(path):
    mods = []
    scan = os.listdir(path)
    for obj in scan:
        mod = splitNameVersion(obj)
        if mod:
            mods.append(mod)
    return mods
    
def splitNameVersion(string):
    pattern = re.compile(r'^([^_]*)_(\d+.\d+.\d+)') # Everything except _ and then number
    match = pattern.search(string)
    if match:
        return (match.group(1), match.group(2))

def main():
    try:
        if len(sys.argv) <= 1: # Parsing arguments
            raise Exception("NotEnoughArguments")
    except Exception as e:
        print("An Exception occured: {}".format(e))
        print("Usage:\n{} PATHTOMODS <USER> <PASSWORD>".format(sys.argv[0]))
        sys.exit()

    if not os.path.exists(sys.argv[1]):
        print("Error: {} does not exist".format(sys.argv[1]))
        

    existing_mods = getMods(sys.argv[1])
    online_mods = []
    for mod in existing_mods:
        print("Checking {}".format(mod[0]))
        online_mods.append(getOnlineVersion(mod[0]))

    if len(existing_mods) != len(online_mods):
        print("Something is wrong!")
        sys.exit()

    for index in range(len(existing_mods)):
        if online_mods[index][1] != existing_mods[index][1]:
            print("Newer version of \"{}\" is avaliable under {}\ninstalled: {}, current: {}".format(existing_mods[index][0], online_mods[index][2], existing_mods[index][1], online_mods[index][1]))
            print()

if __name__ == "__main__":
    main()
