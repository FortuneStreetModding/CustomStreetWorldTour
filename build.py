#!/usr/bin/env python
import sys
MIN_PYTHON = (3, 9)
if sys.version_info < MIN_PYTHON:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

from subprocess import check_output
from pathlib import Path

import os
import json
import urllib.request
import csv
import yaml
import gdown

def downloadLatestReleaseFromGithub(executable : str, url : str):
    _json = json.loads(urllib.request.urlopen(urllib.request.Request(url,
        headers={'Accept': 'application/vnd.github.v3+json'},
    )).read())
    for asset in _json['assets']:
        if asset['name'].endswith(".zip"):
            print("downloading " + executable + " from " + asset['browser_download_url'] + "...")
            zipFileDownload = urllib.request.urlretrieve(asset['browser_download_url'], asset['name'])[0]
            print("extracting " + zipFileDownload+ "...")
            gdown.extractall(zipFileDownload)
            os.remove(zipFileDownload)
            

def findExecutable(executable : str, githubLatestUrl : str = "") -> str:
    try:
        check_output(executable + " --help", encoding="utf-8")
        return executable
    except OSError:
        candidates = list(Path().glob('**/' + executable + "*"))
        for candidate in candidates:
            try:
                check_output(str(candidate) + " --help", encoding="utf-8")
                return str(candidate)
            except OSError:
                pass
    if githubLatestUrl:
        try:
            downloadLatestReleaseFromGithub(executable, githubLatestUrl)
            return findExecutable(executable)
        except Exception:
            print("failed downloading " + executable)
    return ""

def download(path : str, url : str):
    print("downloading " + url + "...")
    if 'drive.google.com' in url:
        zipFileDownload = gdown.download(url, quiet=False)
    else:
        zipFileDownload = urllib.request.urlretrieve(url)[0]
    print("extracting " + zipFileDownload + " to " + path +"...")
    gdown.extractall(zipFileDownload, path)
    os.remove(zipFileDownload)

def main(argv : list):
    argv.append("ST7P01.wbfs")
    if len(argv) < 1:
        print("Provide the path to the Fortune Street iso/wbfs file")
        sys.exit()
    file = Path(argv[0])
    
    if not file.is_file():
        print(argv[0] + " does not exist or is not a file")
        sys.exit()
    
    csmm = findExecutable("csmm", "https://api.github.com/repos/FortuneStreetModding/csmm-qt/releases/latest")
    if not csmm:
        print("Could not find csmm executable")
        sys.exit()

    backgrounds = dict()
    with open('fortunestreetmodding.github.io/_data/backgrounds.yml', "r", encoding='utf8') as stream:
        try:
            backgrounds = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    yamlMaps = list(Path().glob('fortunestreetmodding.github.io/_maps/*/*.yaml'))
    for yamlMap in yamlMaps:
        # print("Scanning " + yamlMap.name + "...")
        print("Scanning " + yamlMap.parent.name)
        with open(yamlMap, "r", encoding='utf8') as stream:
            try:
                yamlContent = yaml.safe_load(stream)
                if 'background' in yamlContent:
                    # find the background in the backgrounds.yml
                    background = yamlContent['background']
                    definedBackground = next((item for item in backgrounds if item["background"] == background), None)
                    if definedBackground:
                        if 'download' in definedBackground:
                            # check if all files are available
                            filesAvailable = list(Path().glob(str(yamlMap.parent) + '/*.*'))
                            filesAvailable = list(map(lambda x: x.name, filesAvailable))
                            filesRequired = list()
                            filesRequired.append(background + '.cmpres')
                            filesRequired.append(background + '.scene')
                            if 'music' in definedBackground:
                                for musicType in definedBackground['music']:
                                    if musicType != 'download' and definedBackground['music'][musicType]:
                                        filesRequired.append(definedBackground['music'][musicType] + '.brstm')
                            # download is required if not all required files are available
                            downloadRequired = not all(item in filesAvailable for item in filesRequired)
                            if downloadRequired:
                                download(str(yamlMap.parent), definedBackground['download'])
                if 'music' in yamlContent:
                    # check if all brstm files are available
                    filesAvailable = list(Path().glob(str(yamlMap.parent) + '/*.brstm'))
                    filesAvailable = list(map(lambda x: x.name, filesAvailable))
                    filesRequired = list()
                    for musicType in yamlContent['music']:
                        if musicType != 'download' and yamlContent['music'][musicType]:
                            filesRequired.append(yamlContent['music'][musicType] + '.brstm')
                    # download is required if not all required files are available
                    downloadRequired = not all(item in filesAvailable for item in filesRequired)
                    if 'download' in yamlContent['music'] and downloadRequired:
                        download(str(yamlMap.parent), yamlContent['music']['download'])
            except yaml.YAMLError as exc:
                print(exc)
    
    print("Extracting "+str(file)+" to "+file.stem+"...")
    check_output(csmm + ' extract "' + str(file) + '" "' + file.stem + '"', encoding="utf-8")
    #status = check_output(csmm + ' status "' + file.stem + '"', encoding="utf-8")

    mapsConfig = dict()
    with open('defsFortuneStreetFun.yml', "r", encoding='utf8') as stream:
        try:
            mapsConfig = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    csvFilePath = Path(file.stem + '/csmm_pending_changes.csv')
    id = 0
    with open(csvFilePath, 'w+', newline='', encoding='utf8') as csvfile:
        fieldnames = ['id', 'mapSet', 'zone', 'order', 'practiceBoard', 'name', 'yaml']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for mapSet in mapsConfig:
            practiceBoardName = ""
            for zone in mapsConfig[mapSet]:
                if 'practiceBoard' == zone:
                    practiceBoardName = mapsConfig[mapSet]['practiceBoard']
                    continue
                order = 0
                for mapDir in mapsConfig[mapSet][zone]:
                    practiceBoard = 0
                    if mapDir == practiceBoardName:
                        practiceBoard = 1
                    yamlFile = next((item for item in yamlMaps if item.parent.name == mapDir), None)
                    yamlPath = '../fortunestreetmodding.github.io/_maps/' + mapDir + '/' + yamlFile.name
                    writer.writerow({'id': id, 'mapSet': mapSet, 'zone': zone, 'order': order, 'practiceBoard': practiceBoard, 'name': mapDir, 'yaml': yamlPath})
                    id += 1
                    order += 1

    print("Saving " + str(id) + " maps to " + file.stem + "...")
    print(check_output(csmm + ' save "' + file.stem + '"', encoding="utf-8"))

    print("Packing " + file.stem + " to WBFS file...")
    print(check_output(csmm + ' pack "' + file.stem + '" --force', encoding="utf-8"))

if __name__ == "__main__":
    main(sys.argv[1:])