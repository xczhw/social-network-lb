import zipfile

def unzip(path, filename):
    with zipfile.ZipFile(path / filename, 'r') as zip_ref:
        zip_ref.extractall(path / filename.strip('.zip'))