import os
import shutil
import subprocess
import sys
import time
import tempfile
import zipfile

import fast_zip_decryption

try:
    import pyminizip
except ImportError:
    pyminizip = None  # type: ignore

password = "foo"


def create_encrypted_test_file(path):
    old_working_directory = os.getcwd()

    files = {
        "random-8MiB": os.urandom(8 * 1024 * 1024),
        "digits-8MiB": b'01234567' * (1024 * 1024),
    }

    folder = None
    try:
        folder = tempfile.TemporaryDirectory()
        os.chdir(folder.name)
        for name, contents in files.items():
            with open(name, "wb") as file:
                file.write(contents)

        if os.path.exists(path):
            os.remove(path)

        command = []
        if shutil.which("zip"):
            command = ["zip", "--encrypt", "--password", password, str(path)] + list(files.keys())
        elif shutil.which("7z") or shutil.which("7z.exe"):
            binary = "7z" if shutil.which("7z") else "7z.exe"
            command = [binary, "a", "-p" + password, str(path)] + list(files.keys())
        elif 'pyminizip' in sys.modules:
            print("Create zip file with pyminizip.")
            pyminizip.compress_multiple(list(files.keys()), [], str(path), password, 3)

        if command:
            print("Create zip file with:", " ".join(command))
            subprocess.run(command, check=True)
    finally:
        os.chdir(old_working_directory)
        if folder is not None:
            shutil.rmtree(folder.name)
    return files


def test_decompression():
    with tempfile.NamedTemporaryFile(suffix=".zip") as archive_path:
        files = create_encrypted_test_file(archive_path.name)
        with zipfile.ZipFile(archive_path.name) as archive:
            archive.setpassword(password.encode())
            assert set(archive.namelist()) == set(files.keys())

            t0 = time.time()
            for name, contents in files.items():
                with archive.open(name, "r") as file:
                    assert file.read() == contents
            t1 = time.time()
            duration = t1 - t0

            # On my local system: 6.2 s with Python, 0.1 s with this fix
            # On Github Actions: 7.6 s with Python, 0.1 s with this fix
            # Thanks to the huge performance difference, this check should be sufficiently stable.
            print(f"Decryption took: {duration:.2e} s")
            assert duration < 1.0


if __name__ == '__main__':
    test_decompression()
