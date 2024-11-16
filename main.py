import os, importlib
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


def get_all_files_in_directory(directory, ext=''):
    all_files = []
    for root, dirs, files in os.walk(directory):
        root: str = root[len(directory):]
        root.replace(os.path.sep, '.')
        for file in files:
            if file.endswith(ext):
                file_path = root + '.' + file[:-len(ext)]
                all_files.append(file_path)
    return all_files


for _path in get_all_files_in_directory('Plugins', '.py'):
    plugin = importlib.import_module(_path, 'Plugins')
    plugin.callback(app)
