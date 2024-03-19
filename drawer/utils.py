import zipfile

def unzip(path, filename):
    try:
        with zipfile.ZipFile(path / filename, 'r') as zip_ref:
            zip_ref.extractall(path / filename.strip('.zip'))
    except Exception as e:
        print(e)
        print('Error unzipping', path, filename)
        pass