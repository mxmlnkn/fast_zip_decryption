# fast_zip_decryption

Read Standard Zip Encryption 2.0 encrypted Zips 100x faster with same interface as the CPython standard library's [`zipfile.ZipFile`](https://docs.python.org/3/library/zipfile.html).


# About this Fork

This is a fork of [fastzipfile](https://github.com/kamilmahmood/fastzipfile).
I created this fork in order to add automated testing, building, and uploading of wheels to my own `fast_zip_decryption` PyPI repository so that installation is more hassle-free.


# Installation

```
pip install fast_zip_decryption
```


# Usage

You just need to import `fast_zip_decryption` and that's it. It patches `zipfile` with a fast decrypter.

```python3
import fast_zip_decryption
import zipfile

with zipfile.ZipFile('path-to-file.zip', mode='r') as fz:
    f = fz.open('path-to-file-in-zip', pwd=b'password')
    content = f.read()
```


# Limitation

Currently, it only supports what `zipfile.ZipFile` supports, e.g., no AES-128 or AES-256 support.


# License

This project is licensed under the MIT license. See the [LICENSE](LICENSE) file for details.
