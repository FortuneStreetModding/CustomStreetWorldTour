#!/usr/bin/env python
import sys
MIN_PYTHON = (3, 9)
if sys.version_info < MIN_PYTHON:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

from subprocess import check_output
from pathlib import Path
from dataclasses import dataclass

import os
import json
import urllib.request
import csv
import yaml
import gdown
import platform
import tempfile

EXECUTABLE_EXTENSION = ".exe" if platform.system() == "Windows" else ""
DOWNLOAD_URL_CSMM = "https://api.github.com/repos/FortuneStreetModding/csmm-qt/releases/latest"

@dataclass
class ArcPatch:
    arcFilePath: str
    fileReplacements: list[str]

@dataclass
class FileTypeInfo:
    type: str
    id6: str
    fileSize: int
    region: str
    filePath: str

def downloadLatestReleaseFromGithub(executable : str, url : str):
    _json = json.loads(urllib.request.urlopen(urllib.request.Request(url,
        headers={'Accept': 'application/vnd.github.v3+json'},
    )).read())
    for asset in _json['assets']:
        if platform.system().lower() in asset['name']:
            print(f'downloading {executable} from {asset["browser_download_url"]}...')
            zipFileDownload = urllib.request.urlretrieve(asset['browser_download_url'], asset['name'])[0]
            print(f'extracting {zipFileDownload}...')
            gdown.extractall(zipFileDownload)
            os.remove(zipFileDownload)

def findExecutable(executable : str, downloadUrl : str = "", searchPath : Path = None) -> str:
    if searchPath:
        candidate = f'{str(searchPath.as_posix())}/{executable}{EXECUTABLE_EXTENSION}'
        try:
            check_output(f'{candidate} --help', encoding="utf-8")
            return candidate
        except OSError:
            pass
    candidates = list(Path().glob('**/' + executable + EXECUTABLE_EXTENSION))
    for candidate in candidates:
        try:
            candidate = str(candidate)
            check_output(f'{candidate} --help', encoding="utf-8")
            return candidate
        except OSError:
            pass
    try:
        check_output(f'{executable} --help', encoding="utf-8")
        return executable
    except OSError:
        if downloadUrl:
            if 'github' in downloadUrl:
                try:
                    downloadLatestReleaseFromGithub(executable, downloadUrl)
                    return findExecutable(executable)
                except Exception as err:
                    print(f'failed downloading {executable}: {str(err)}')
            else:
                try:
                    download(".", downloadUrl)
                    return findExecutable(executable)
                except Exception as err:
                    print(f'failed downloading {executable}: {str(err)}')
    return ""

def download(path : str, url : str):
    print(f'downloading {url}...')
    if 'drive.google.com' in url:
        zipFileDownload = gdown.download(url, quiet=False)
    else:
        lastUrlPart = url.rsplit('/', 1)[-1]
        zipFileDownload = urllib.request.urlretrieve(url, lastUrlPart)[0]
    print(f'extracting {zipFileDownload} to {path}...')
    gdown.extractall(zipFileDownload, path)
    os.remove(zipFileDownload)

def getValidCandidates(wit : str) -> list[FileTypeInfo]:
    validCandidates = []
    output = check_output(f'{wit} filetype . --long --long --ignore-fst', encoding="utf-8")
    print(output)
    a,b,c = output.partition("---\n")
    candidates = filter(None, c.splitlines())
    for candidate in candidates:
        attributes = candidate.split(maxsplit = 5)
        type = attributes[0]
        id6 = attributes[1]
        fileSize = attributes[2]
        region = attributes[3]
        filePath = attributes[5]
        if id6.startswith("ST7") and id6.endswith("01") and (type.startswith("ISO") or type.startswith("WBFS")):
            validCandidates.append(FileTypeInfo(type, id6, int(fileSize), region, filePath))
    return validCandidates

def fetchLastLineOfString(string : str):
    lines = string.splitlines()
    nonEmptyLines = list(filter(None, lines))
    return nonEmptyLines[-1]

def getInputFortuneStreetFile(argv : list, wit : str) -> str:
    if len(argv) < 1:
        validCandidates = getValidCandidates(wit)
        if len(validCandidates) == 0:
            print("Provide the path to the Fortune Street iso/wbfs file or put such a file into the same directory as this script")
            sys.exit()
        elif len(validCandidates) == 1:
            file = Path(validCandidates[0].filePath)
            print(f'Using {file} as input')
            return file
        else:
            print("There are multiple Fortune Street iso/wbfs in this directory. Either remove them so that only one remains or provide the path to the Fortune Street iso/wbfs file")
            sys.exit()
    else:
        file = Path(argv[0])
        if not file.is_file():
            print(f'{argv[0]} does not exist or is not a file')
            sys.exit()
        return file

def downloadBackgroundsAndMusic(yamlMaps : list[Path]):
    backgrounds = dict()
    with open('fortunestreetmodding.github.io/_data/backgrounds.yml', "r", encoding='utf8') as stream:
        try:
            backgrounds = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    for yamlMap in yamlMaps:
        print(f'Scanning {yamlMap.parent.name}')
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

def createMapListFile(yamlMaps : list[Path], outputCsvFilePath : Path) -> int:
    mapsConfig = dict()
    with open('customStreetWorldTour.yml', "r", encoding='utf8') as stream:
        try:
            mapsConfig = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    id = 0
    with open(outputCsvFilePath, 'w+', newline='', encoding='utf8') as csvfile:
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
    return id

def resolveAll(path : Path, isLocalizeType : bool) -> list[Path]:
    paths = []
    if "all" in path.with_suffix('').suffix.lower():
        baseName = path.with_suffix('').with_suffix('').name
        lang = ""
        for lang in ["JP", "DE", "EN", "ES", "FR", "IT", "UK"]:
            if isLocalizeType:
                langDir = ""
                if lang == "ES":
                    lang = "su"
                suffix = "." + lang.lower()
            else:
                if lang == "JP":
                    lang = ""
                langDir = f'lang{lang}/'
                suffix = ""
                if lang:
                    suffix = f'_{lang}'
                else:
                    langDir = ''
            paths.append(Path(path.parent / Path(langDir + baseName + suffix + path.suffix)))
        return paths
    paths.append(path)
    return paths

def patchArcs(dir : str, wszst : str, wimgt : str):
    pngPaths = list(Path().glob('files/**/*.png'))
    arcsToBePatched = {}
    for pngPath in pngPaths:
        arcPaths = resolveAll(pngPath.parent, False)
        for arcPath in arcPaths:
            arcPath = Path(dir) / arcPath
            arcPathStr = arcPath.as_posix()
            if arcPathStr not in arcsToBePatched:
                arcsToBePatched[arcPathStr] = []
            arcsToBePatched[arcPathStr].append(pngPath)
    for arcToBePatched in arcsToBePatched:
        with tempfile.TemporaryDirectory() as tmpdirname:
            print(check_output(f'{wszst} EXTRACT {arcToBePatched} --dest {tmpdirname} --overwrite', encoding="utf-8"))
            for pngPath in arcsToBePatched[arcToBePatched]:
                pngPath = Path(pngPath)
                basename_tpl_0 = Path(pngPath.stem)
                basename_tpl = basename_tpl_0.with_suffix(".tpl")
                tplPath = Path(tmpdirname) / Path(f'arc/timg/{basename_tpl}')
                print(check_output(f'{wimgt} ENCODE {pngPath.as_posix()} --dest {tplPath.as_posix()} --overwrite', encoding="utf-8"))
            print(check_output(f'{wszst} CREATE {tmpdirname} --dest {arcToBePatched} --overwrite', encoding="utf-8"))

def patchLocalize(dir : str):
    csvDeltas = list(Path().glob('files/localize/*.csv'))
    csvsToBePatched = {}
    for csvDelta in csvDeltas:
        csvPaths = resolveAll(csvDelta, True)
        for csvPath in csvPaths:
            csvPath = Path(dir) / csvPath
            csvPathStr = csvPath.as_posix()
            if csvPathStr not in csvsToBePatched:
                csvsToBePatched[csvPathStr] = []
            csvsToBePatched[csvPathStr].append(csvDelta)
    for csvToBePatched in csvsToBePatched:
        for csvDelta in csvsToBePatched[csvToBePatched]:
            with open(csvDelta, mode='r', encoding='utf-8') as deltafile:
                reader = csv.reader(deltafile)
                delta = {rows[0]:rows[1] for rows in reader}
            with open(csvToBePatched, mode='r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                csvOutput = {rows[0]:rows[1] for rows in reader}
            csvOutput.update(delta)
            with open(csvToBePatched, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(csvOutput.items())

def main(argv : list):
    csmm = findExecutable("csmm", downloadUrl=DOWNLOAD_URL_CSMM)
    if not csmm:
        print("Could not find csmm executable")
        sys.exit()

    searchPath = Path(fetchLastLineOfString(check_output(f'{csmm} download-tools', encoding="utf-8")))

    wit = findExecutable("wit", searchPath=searchPath)
    if not wit:
        print("Could not find wit executable")
        sys.exit()

    wszst = findExecutable("wszst", searchPath=searchPath)
    if not wszst:
        print("Could not find wszst executable")
        sys.exit()

    wimgt = findExecutable("wimgt", searchPath=searchPath)
    if not wimgt:
        print("Could not find wimgt executable")
        sys.exit()

    yamlMaps = list(Path().glob('fortunestreetmodding.github.io/_maps/*/*.yaml'))
    downloadBackgroundsAndMusic(yamlMaps)

    file = getInputFortuneStreetFile(argv, wit)
    if(Path(file.stem).is_dir() and Path(file.stem).exists()):
        print(f'Would extract {str(file)} to {file.stem} but it already exists. The directory is reused.')
    else:
        print(f'Extracting {str(file)} to {file.stem}...')
        check_output(f'{csmm} extract "{str(file)}" "{file.stem}"', encoding="utf-8")

    print(f'Patching arc files...')
    patchArcs(file.stem, wszst, wimgt)

    print(f'Patching localization files...')
    patchLocalize(file.stem)

    mapCount = createMapListFile(yamlMaps, Path(file.stem + '/csmm_pending_changes.csv'))

    print(f'Saving {str(mapCount)} maps to {file.stem}...')
    output = check_output(f'{csmm} save "{file.stem}"', encoding="utf-8")
    print(output)

    if 'error' in output.lower():
        sys.exit(1)
    
    print(f'Packing {file.stem} to WBFS file...')
    print(check_output(f'{csmm} pack "{file.stem}" --force', encoding="utf-8"))

if __name__ == "__main__":
    main(sys.argv[1:])