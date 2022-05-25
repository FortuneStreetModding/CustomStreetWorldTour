import build
import sys
import argparse
import colorama
import platform

output_version = "1.0"
csmm_version = "1.7.5"
resources_url = ["https://nikkums.io/cswt/1.0/CSWT1Files.zip", 
                "https://drive.google.com/u/2/uc?id=1NvI7Y7o9vAC7ibBkGt1m4qozfkMm-_Jq&export=download&confirm=1"]
overwrite_extracted_directory = True
threads = 1

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        if platform.system() == "Windows":
            file = "build.bat"
            file_console = "build_console.bat"
        else:
            file = "build.sh"
            file_console = "build_console.sh"
        print("This file should not be run directly. Run {file} or {file_console} instead.")
        input("Press enter to continue...")
        sys.exit(1)

    colorama.init()
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-file', action='store', help='The input image of either Fortune Street or Boom Street in wbfs or iso format')
    parser.add_argument('--boards-list-file', action='store', help='The yaml file which contains the boards that should be used')
    args = parser.parse_args()
    build.run(args.input_file, output_version, csmm_version, resources_url, overwrite_extracted_directory, args.boards_list_file, threads)