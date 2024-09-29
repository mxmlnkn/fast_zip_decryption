# fastzipfile

Read Standard Zip Encryption 2.0 encrypted Zips 100x faster with same interface as the CPython standard library's [`zipfile.ZipFile`](https://docs.python.org/3/library/zipfile.html).


# Installation

```
pip install fastzipfile
```


# Usage

You just need to import `fastzipfile` and that's it. It patches `zipfile` with a fast decrypter.

```python3
import fastzipfile
import zipfile

with zipfile.ZipFile('path-to-file.zip', mode='r') as fz:
    f = fz.open('path-to-file-in-zip', pwd=b'password')
    content = f.read()
```


# Limitation

Currently, it only supports what `zipfile.ZipFile` supports, e.g., no AES-128 or AES-256 support.


# License

This project is licensed under the MIT license. See the [LICENSE](LICENSE) file for details.
