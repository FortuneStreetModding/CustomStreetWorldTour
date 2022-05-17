#!/usr/bin/env python
import shutil
import sys
MIN_PYTHON = (3, 9)
if sys.version_info < MIN_PYTHON:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

from subprocess import check_output
from subprocess import CalledProcessError
from pathlib import Path
from dataclasses import dataclass
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from multiprocessing import Pool
from termcolor import cprint
from tempfile import TemporaryDirectory

# import exceptions
from urllib.error import URLError
from zipfile import BadZipFile
from zlib import error as zlibError

import argparse
import functools
import os
import json
import urllib.request
import csv
import yaml
import gdown
import platform
import addressTranslator
import struct
import logging
import colorama
import requests
import configparser

logger = logging.Logger('catch_all')

EXECUTABLE_EXTENSION = ".exe" if platform.system() == "Windows" else ""
DOWNLOAD_URL_CSMM = "https://api.github.com/repos/FortuneStreetModding/csmm-qt/releases"

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

def downloadReleaseFromGithub(executable : str, url : str, version : str):
    assets = []
    if version:
        _json = json.loads(urllib.request.urlopen(urllib.request.Request(url,
            headers={'Accept': 'application/vnd.github.v3+json'},
        )).read())
        for release in _json:
            if 'tag_name' in release and version in release['tag_name']:
                assets = release['assets']
                break
            elif 'name' in release and version in release['name']:
                assets = release['assets']
                break
    else:
        url = f'{url}/latest'
        _json = json.loads(urllib.request.urlopen(urllib.request.Request(url,
            headers={'Accept': 'application/vnd.github.v3+json'},
        )).read())
        assets = _json['assets']

    for asset in assets:
        if platform.system().lower() in asset['name']:
            filename = asset['name']
            with TemporaryDirectory(prefix="CSWT_", ignore_cleanup_errors=True) as tempDir:
                zipFileDownload = gdown.download(asset["browser_download_url"], Path(tempDir).as_posix() + os.path.sep)
                if zipFileDownload == None:
                    raise Exception(f'{filename}: Failed!')
                zipFileName = Path(zipFileDownload).name
                print(f'Extracting {zipFileName}...')
                gdown.extractall(zipFileDownload, Path())
                os.remove(zipFileDownload)

def findExecutable(executable : str, downloadUrl : str = "", searchPath : Path = None, version : str = None) -> str:
    if searchPath:
        candidate = f'{str(searchPath.as_posix())}/{executable}{EXECUTABLE_EXTENSION}'
        try:
            check_output([candidate, '--help'], encoding="utf-8")
            return candidate
        except OSError:
            pass
    candidates = list(Path().glob('**/' + executable + EXECUTABLE_EXTENSION))
    if platform.system() == 'Darwin' and executable == 'csmm':
        candidates.append('/Applications/csmm.app/Contents/MacOS/csmm')
    for candidate in candidates:
        try:
            #print(candidate)
            candidate = str(candidate)
            help_output = check_output([candidate, '--help'], encoding="utf-8")
            if not version or version in help_output:
                return candidate
        except OSError as e:
            #print(e)
            pass
    if downloadUrl:
        if 'github' in downloadUrl:
            try:
                downloadReleaseFromGithub(executable, downloadUrl, version)
                return findExecutable(executable)
            except Exception as err:
                cprint(f'Failed downloading {executable}: {str(err)}', 'red')
        else:
            raise NotImplementedError
    return ""

def config_update_file_size(config : configparser.ConfigParser, section : str, file_size : int):
    config[section] = {'file.size': file_size}

def check_update_available(config : configparser.ConfigParser, section : str, mirrors):
    file_size = config.getint(section, 'file.size', fallback=-1)
    server_file_size = get_filesize(mirrors)
    if server_file_size == -1 or file_size != server_file_size:
        return True
    return False

def get_filesize(mirrors):
    if type(mirrors) == str:
        url = mirrors
    elif len(mirrors) == 1:
        url = mirrors[0]
    else:
        for mirror in mirrors:
            try:
                file_size = get_filesize(mirror)
                if file_size != -1:
                    return file_size
            except Exception as e:
                logger.error(e, exc_info=True)
        return -1

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"  # NOQA
    }
    try:
        sess = requests.session()
        size = -1
        if 'drive.google.com' in url:
            headers["Accept"] = "application/json"
            fileId = url.split("id=")[1].split("&")[0]
            res = sess.get(f'https://www.googleapis.com/drive/v3/files/{fileId}?alt=json&fields=size&key=AIzaSyDQB22BQtznFe85nOyok2U9qO5HSr3Z5u4')
            data = res.json()
            if 'error' in data:
                cprint('google drive error', 'red')
                if 'message' in data['error']:
                    print(data['error']['message'])
            else:
                size = int(data["size"])
        else:
            res = sess.head(url, headers=headers, stream=True, verify=True, allow_redirects=True)
            size = int(res.headers.get("Content-Length", 0))
        return size
    except IOError as e:
        print(e, file=sys.stderr)
        return -1
    finally:
        sess.close()

def download(path : str, mirrors, label : str = None, config : configparser.ConfigParser = None, config_section : str = None, update : bool = False, print_failure : bool = True):
    if label:
        label = f'{label:30}'
        gdown_quiet = True
    else:
        label = ""
        gdown_quiet = False
    if type(mirrors) == str:
        url = mirrors
    elif len(mirrors) == 1:
        url = mirrors[0]
    else:
        for mirror in mirrors:
            try:
                if download(path, mirror, label, config, config_section, update, False):
                    return True
            except URLError as e:
                cprint(f'{label}Download error: {str(e.reason)}', 'yellow')
            except BadZipFile as e:
                cprint(f'{label}Extraction error: {str(e)}', 'yellow')
            except zlibError as e:
                cprint(f'{label}Extraction error: {str(e)}', 'yellow')
        if print_failure:
            cprint(f'{label}Failed!', 'red')
        return False
    if gdown_quiet:
        if update:
            print(f'{label}Updating {url}...')
        else:
            print(f'{label}Downloading {url}...')

    with TemporaryDirectory(prefix="CSWT_", ignore_cleanup_errors=True) as tempDir:
        zipFileDownload = gdown.download(url, Path(tempDir).as_posix() + os.path.sep, quiet=gdown_quiet)
        if zipFileDownload == None:
            if print_failure:
                cprint(f'{label}Failed!', 'red')
            return False

        zipFileName = Path(zipFileDownload).name
        print(f'{label}Extracting {zipFileName}...')
        gdown.extractall(zipFileDownload, path)
        if config:
            # remember the filesize
            file_size = os.path.getsize(zipFileDownload)
            config_update_file_size(config, config_section, file_size)
        # remove the zip file
        os.remove(zipFileDownload)
        if update:
            cprint(f'{label}Update Complete!', 'green')
        else:
            cprint(f'{label}Download Complete!', 'green')
        return True

def getValidCandidates(wit : str, path : Path) -> list[FileTypeInfo]:
    validCandidates = []
    try:
        output = check_output([wit, 'filetype', path.as_posix(), '--long', '--long', '--ignore-fst'], encoding="utf-8")
    except CalledProcessError as err:
        if err.returncode == 8: # wit returns error code 8 if it doesnt find any wii images at all
            return []
        else:
            raise err
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

def getInputFortuneStreetFilePath(input_file : str, wit : str) -> Path:
    if not input_file:
        validCandidates = getValidCandidates(wit, Path("."))
        if len(validCandidates) == 0:
            validCandidates = getValidCandidates(wit, Path(".."))
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
        file = Path(input_file)
        if not file.is_file():
            print(f'{input_file} does not exist or is not a file')
            sys.exit()
        return file

def downloadBackgroundAndMusic(yamlMap : Path, backgrounds : dict, resourcesDirectory : str):
    with open(yamlMap, "r", encoding='utf8') as stream:
        try:
            yamlContent = yaml.safe_load(stream)
            downloadedSomething = False

            configpath = Path(yamlMap.parent) / Path(f'{str(yamlMap.parent.name)}.cfg')
            config = configparser.ConfigParser()
            if configpath.exists() and configpath.is_file():
                config.read(configpath)

            if 'background' in yamlContent:
                # find the background in the backgrounds.yml
                background = yamlContent['background']
                definedBackground = next((item for item in backgrounds if item["background"] == background), None)
                if definedBackground and 'download' in definedBackground and definedBackground['download']:
                    # check if all files are available
                    filesAvailable = list(Path().glob(str(yamlMap.parent) + '/*.*'))
                    filesAvailable = list(map(lambda x: x.name, filesAvailable))
                    filesRequired = list()
                    filesRequired.append(background + '.cmpres')
                    filesRequired.append(background + '.scene')
                    filesRequired.append(f"ui_menu_{background}_a.png")
                    filesRequired.append(f"ui_menu_{background}_b.png")
                    filesRequired.append(f"ui_menu_{background}_c.png")
                    if 'music' in definedBackground:
                        for musicType in definedBackground['music']:
                            if musicType != 'download' and definedBackground['music'][musicType]:
                                filesRequired.append(definedBackground['music'][musicType] + '.brstm')

                    # try to get the required files from the resources directory
                    if resourcesDirectory:
                        for fileRequired in filesRequired:
                            if not fileRequired in filesAvailable:
                                fileInResourcesDirectoryPath = Path(resourcesDirectory) / Path(fileRequired)
                                if fileInResourcesDirectoryPath.exists():
                                    shutil.copy(fileInResourcesDirectoryPath, yamlMap.parent)
                                    filesAvailable.append(fileRequired)

                    # download is required if not all required files are available
                    downloadRequired = not all(item in filesAvailable for item in filesRequired)
                    
                    mirrors = definedBackground['download']
                    config_section = "background"
                    label = f'{yamlMap.parent.name}_bg'
                    # download is also required when the filesize does not match the server (but we only try to update if we did not have an all-in-one resources zip file provided)
                    update = False
                    if not downloadRequired and not resourcesDirectory:
                        update = check_update_available(config, config_section, mirrors)
                        if update:
                            downloadRequired = True
                    if downloadRequired:
                        download(str(yamlMap.parent), mirrors, label, config, config_section, update)
                        downloadedSomething = True
            if 'music' in yamlContent and 'download' in yamlContent['music'] and yamlContent['music']['download']:
                # check if all brstm files are available
                filesAvailable = list(Path().glob(str(yamlMap.parent) + '/*.brstm'))
                filesAvailable = list(map(lambda x: x.name, filesAvailable))
                filesRequired = list()
                for musicType in yamlContent['music']:
                    if musicType != 'download' and yamlContent['music'][musicType]:
                        filesRequired.append(yamlContent['music'][musicType] + '.brstm')

                # try to get the required files from the resources directory
                if resourcesDirectory:
                    for fileRequired in filesRequired:
                        if not fileRequired in filesAvailable:
                            fileInResourcesDirectoryPath = Path(resourcesDirectory) / Path(fileRequired)
                            if fileInResourcesDirectoryPath.exists():
                                shutil.copy(fileInResourcesDirectoryPath, yamlMap.parent)
                                filesAvailable.append(fileRequired)

                # download is required if not all required files are available
                downloadRequired = not all(item in filesAvailable for item in filesRequired)
                    
                mirrors = yamlContent['music']['download']
                config_section = "music"
                label = f'{yamlMap.parent.name}_music'
                # download is also required when the filesize does not match the server (but we only try to update if we did not have an all-in-one resources zip file provided)
                update = False
                if not downloadRequired and not resourcesDirectory:
                    update = check_update_available(config, config_section, mirrors)
                    if update:
                        downloadRequired = True
                if downloadRequired:
                    download(str(yamlMap.parent), mirrors, label, config, config_section, update)
                    downloadedSomething = True
            if downloadedSomething:
                with open(configpath, 'w') as configfile:
                    config.write(configfile)
            else:
                print(f'{yamlMap.parent.name}: OK')
        except yaml.YAMLError as exc:
            print(exc)

def downloadBackgroundsAndMusic(yamlMaps : list[Path], resourcesDirectory : str = None):
    backgrounds = dict()
    with open('fortunestreetmodding.github.io/_data/backgrounds.yml', "r", encoding='utf8') as stream:
        try:
            backgrounds = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    threads = 4
    if threads == 1:
        for yamlMap in yamlMaps:
            downloadBackgroundAndMusic(yamlMap, backgrounds, resourcesDirectory)
    else:
        with Pool(threads) as p:
            p.map(functools.partial(downloadBackgroundAndMusic, backgrounds=backgrounds, resourcesDirectory=resourcesDirectory), yamlMaps)
        

def createMapListFile(yamlFile : str, yamlMaps : list[Path], outputCsvFilePath : Path) -> int:
    mapsConfig = dict()
    with open(yamlFile, "r", encoding='utf8') as stream:
        try:
            mapsConfig = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    id = 0
    mapList = []
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
                    if yamlFile == None:
                        raise ValueError(f'No yaml file was found for the map {mapDir}')
                    yamlPath = '../fortunestreetmodding.github.io/_maps/' + mapDir + '/' + yamlFile.name
                    writer.writerow({'id': id, 'mapSet': mapSet, 'zone': zone, 'order': order, 'practiceBoard': practiceBoard, 'name': mapDir, 'yaml': yamlPath})
                    id += 1
                    order += 1
                    mapList.append(mapDir)
    return mapList

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

def drawVersionOnTitleImage(imageInputPath : Path, version : str, imageOutputPath : Path):
    pattern = Image.open(imageInputPath, "r").convert('RGBA')
    draw = ImageDraw.Draw(pattern,'RGBA')
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)
    draw.text((469,204), version, (22, 42, 136, 255) ,font=font, stroke_width=2, stroke_fill=(22, 42, 136, 255))
    draw.text((469,204), version, (255, 255, 70, 255),font=font)
    pattern.save(imageOutputPath)

def patchArcs(dir : str, wszst : str, wimgt : str, version : str):
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
        with TemporaryDirectory(prefix="CSWT_", ignore_cleanup_errors=True) as tmpdirname:
            print(check_output([wszst, 'EXTRACT', arcToBePatched, '--dest', tmpdirname, '--overwrite'], encoding="utf-8"))
            for pngPath in arcsToBePatched[arcToBePatched]:
                pngPath = Path(pngPath)
                basename_tpl_0 = Path(pngPath.stem)
                basename_tpl = basename_tpl_0.with_suffix(".tpl")
                tplPath = Path(tmpdirname) / Path(f'arc/timg/{basename_tpl}')
                # draw version onto the title screen image
                if version and "ui_itasuto_logo_ja" in pngPath.name:
                    newPngPath = Path(tmpdirname) / Path(pngPath.name)
                    drawVersionOnTitleImage(pngPath, version, newPngPath)
                    pngPath = newPngPath
                print(check_output([wimgt, 'ENCODE', pngPath.as_posix(), '--dest', tplPath.as_posix(), '--overwrite'], encoding="utf-8"))
            print(check_output([wszst, 'CREATE', tmpdirname, '--dest', arcToBePatched, '--overwrite'], encoding="utf-8"))

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

def applyHexEdits(mainDol : str):
    # check if boom street or fortune street
    with open(mainDol, "rb") as stream:
        stream.seek(0x756b4)
        b = stream.read(4)
        v = struct.unpack(">I", b)[0]
        print(hex(v))
        if v == 0x800dab84:
            boom = True
        else:
            boom = False

    patchFiles = list(Path().glob('patches/*.y*ml'))
    patchLists = {}
    for patchFile in patchFiles:
        patch = dict()
        with open(patchFile, "r", encoding='utf8') as stream:
            try:
                patch = yaml.safe_load(stream)
                if "patches" in patch:
                    patchLists[patchFile.name] = patch["patches"]
            except yaml.YAMLError as exc:
                print(exc)
    with open(mainDol, "r+b") as stream:
        for patchListFile in patchLists.keys():
            patchList = patchLists[patchListFile]
            print(f'Applying patch {patchListFile}...')
            for patch in patchList:
                boomAddress = patch["boomAddress"]
                format = patch["format"]
                originalValue = patch["originalValue"]
                patchValue = patch["patchValue"]
                if boom:
                    fileAddress = addressTranslator.bsvirt_to_bsfile.map(boomAddress)
                else:
                    fileAddress = addressTranslator.fsvirt_to_fsfile.map(addressTranslator.bsvirt_to_fsvirt.map(boomAddress))
                stream.seek(fileAddress)
                if format=='hex':
                    stream.write(bytes.fromhex(patchValue))
                else:
                    stream.write(struct.pack(format, patchValue))
                print(f'  {hex(fileAddress)}: {originalValue} -> {patchValue}')

def main(argv : list):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-file', action='store', help='The input image of either Fortune Street or Boom Street in wbfs or iso format')
    parser.add_argument('--csmm-version', action='store', help='CSMM version to use')
    parser.add_argument('--output-version', action='store', help='Output CSWT version')
    parser.add_argument('--resources-mirror', action='append', help='Specify a download URL where this script will download all required resources')
    parser.add_argument('--overwrite-extracted-directory', action='store_true', help='Avoids reusing an old extracted directory which can be a cause for errors')
    parser.add_argument('--boards-list-file', default="CustomStreetWorldTour.yaml", action='store', help='The yaml file which contains the boards that should be used')
    args = parser.parse_args(argv)

    colorama.init()

    if args.csmm_version:
        print(f"Fetching CSMM {args.csmm_version}...")
    else:
        print(f"Fetching CSMM")
    csmm = findExecutable("csmm", downloadUrl=DOWNLOAD_URL_CSMM, version=args.csmm_version)
    if csmm:
        print(f'csmm: {Path(csmm).absolute().as_posix()}')
    else:
        print("Could not find csmm executable")
        sys.exit()

    print(f"Fetching CSMM required tools...")
    output = check_output([csmm, 'download-tools', '--force'], encoding="utf-8")
    print(output)
    searchPath = Path(fetchLastLineOfString(output))

    print(f"wit: ", end='')
    wit = findExecutable("wit", searchPath=searchPath)
    if wit:
        print(Path(wit).absolute().as_posix())
    else:
        print("Could not find wit executable")
        sys.exit()

    print(f"wszst: ", end='')
    wszst = findExecutable("wszst", searchPath=searchPath)
    if wszst:
        print(Path(wszst).absolute().as_posix())
    else:
        print("Could not find wszst executable")
        sys.exit()

    print(f"wimgt: ", end='')
    wimgt = findExecutable("wimgt", searchPath=searchPath)
    if wimgt:
        print(Path(wimgt).absolute().as_posix())
    else:
        print("Could not find wimgt executable")
        sys.exit()

    if args.output_version:
        version = args.output_version
    else:
        import pygit2
        from pygit2 import GitError
        try:
            repo = pygit2.Repository('.git')
            head = repo.revparse_single('HEAD')
            version = head.short_id
            for ref in repo.references:
                if ref.startswith("refs/tags/"):
                    commit = repo.revparse_single(ref)
                    if commit == head:
                        version = ref.replace("refs/tags/", "")
                        break
            print(f'Using version {version}')
        except GitError as err:
            version = None
            print(f'Unable to determine version: {err.args[0]}')

    file = getInputFortuneStreetFilePath(args.input_file, wit)

    if Path(file.stem).is_dir() and Path(file.stem).exists() and args.overwrite_extracted_directory:
        print(f'Deleting the folder {Path(file.stem).as_posix()}...')
        shutil.rmtree(Path(file.stem))

    if Path(file.stem).is_dir() and Path(file.stem).exists():
        print(f'Would extract {str(file)} to {file.stem} but it already exists. The directory is reused.')
    else:
        print(f'Extracting {str(file)} to {file.stem}...')
        check_output([csmm, 'extract', str(file), file.stem], encoding="utf-8")

    # glob all yaml files in the maps directory
    yamlMaps = list(Path().glob('fortunestreetmodding.github.io/_maps/*/*.y*ml'))

    # create the csmm_pending_changes.csv file which is required by csmm
    mapList = createMapListFile(args.boards_list_file, yamlMaps, Path(file.stem + '/csmm_pending_changes.csv'))

    # filter the maps out which are not in the boards_configuration
    yamlMaps = list(filter(lambda yamlMap: yamlMap.parent.name in mapList, yamlMaps))

    resources_dir = Path("resources")
    if args.resources_mirror:
        if not resources_dir.exists():
            resources_dir.mkdir()
        if not any(os.scandir(resources_dir)):
            print(f'Downloading resources package...')
            download(resources_dir, args.resources_mirror)
        downloadBackgroundsAndMusic(yamlMaps, resources_dir.as_posix())
        print("All maps checked")
    else:
        downloadBackgroundsAndMusic(yamlMaps)

    print(f'Patching arc files...')
    patchArcs(file.stem, wszst, wimgt, version)

    print(f'Patching localization files...')
    patchLocalize(file.stem)

    print(f'Saving {str(len(mapList))} maps to {file.stem}...')
    output = check_output([csmm, 'save', '--addAuthorToDescription', '1', file.stem], encoding="utf-8")
    print(output)

    if 'error' in output.lower():
        sys.exit(1)

    print(f'Applying hex edits to main.dol...')
    applyHexEdits(Path(Path(file.stem) / Path("sys/main.dol")))

    if version:
        outputFile = Path(file.parent) / Path(f"CustomStreetWorldTour_{version}.wbfs")
    else:
        outputFile = Path(file.parent) / Path(f"CustomStreetWorldTour.wbfs")
    print(f'Packing {file.stem} to {outputFile}...')
    msg = check_output([csmm, 'pack', file.stem, outputFile.as_posix(), '--force'], encoding="utf-8")
    print(msg)

    # dirty hack to check if the packing has been successful
    nlines = len(msg.strip().splitlines())
    if msg.startswith('Creating') and nlines == 1 or msg.startswith('Overwriting') and nlines == 2:
        msg = f'{outputFile.as_posix()} has been built sucessfully!'
        count = len(msg)+4
        cprint(count*'*', 'green')
        cprint(f'* {msg} *', 'green')
        cprint(count*'*', 'green')
        if resources_dir.exists():
            shutil.rmtree(resources_dir)

if __name__ == "__main__":
    main(sys.argv[1:])
