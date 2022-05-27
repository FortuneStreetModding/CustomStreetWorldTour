import build
import sys
import colorama
import os

output_version = "1.0"
csmm_version = "1.7.5"
resources_url = ["https://nikkums.io/cswt/1.0/CSWT1Files.zip", 
                "https://drive.google.com/u/2/uc?id=1NvI7Y7o9vAC7ibBkGt1m4qozfkMm-_Jq&export=download&confirm=1"]
overwrite_extracted_directory = True
threads = 1

if __name__ == "__main__":
    colorama.init()

    input_str = input("Enter the build mode and press enter (c = console, d = default):")

    if 'c' in input_str.lower():
        boards_list_file = "CustomStreetWorldTour_console.yaml"
        print("-- Using console build mode --")
        print()
    elif 'd' in input_str.lower():
        boards_list_file = "CustomStreetWorldTour.yaml"
        print("-- Using default build mode --")
        print()
    else:
        print("Invalid input, exiting.")
        input("Press enter to continue...")
        sys.exit(1)

    try:
        if getattr(sys, 'frozen', False):
            # we are running in a bundle
            application_path = os.path.dirname(os.path.abspath(sys.executable))
            os.chdir(application_path)
        build.run(None, output_version, csmm_version, resources_url, overwrite_extracted_directory, boards_list_file, threads)
        input("Press enter to continue...")
    except Exception as e:
        print(str(e))
        input("Press enter to continue...")
        sys.exit(1)