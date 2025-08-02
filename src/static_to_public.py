import os
import shutil

def copy_source_dir_to_destination_dir(source: str, destination: str):
    if os.path.exists(destination):
        shutil.rmtree(destination)
    os.mkdir(destination)
    for file in os.listdir(source):
        file_path = os.path.join(source, file)
        if os.path.isfile(file_path):
            shutil.copy(file_path, os.path.join(destination, file))
        else:
            copy_source_dir_to_destination_dir(file_path, os.path.join(destination, file))