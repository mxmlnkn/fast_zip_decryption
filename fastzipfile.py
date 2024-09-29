import io
import warnings
import traceback
import zipfile

import _zipdecrypter


__all__ = ["monkeypatch"]


class FastZipExtFile(zipfile.ZipExtFile):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _read2(self, n):
        """Read n bytes from file and decrypt.

        Copied from _zipfile.ZipExtFile._read2
        This method adheres to new interface of _zipfile._ZipDecrypter because interface of
        _zipfile._ZipDecrypter changed by commit no 06e522521c06671b4559eecf9e2a185c2d62c141
        in bpo-10030.

        Old interface of decrypter accepts one int at a time while the new interface accepts
        a bytes object.
        """

        if self._compress_left <= 0:
            return b""

        n = max(n, self.MIN_READ_SIZE)
        n = min(n, self._compress_left)

        data = self._fileobj.read(n)
        self._compress_left -= len(data)
        if not data:
            raise EOFError

        if self._decrypter is not None:
            data = self._decrypter.decrypt_bytes(data)
        return data


def monkeypatch():
    # This monkey patching makes a lot of assumptions on the zipfile module that are not
    # part of the public interface and therefore might change at any time. To avoid
    # errors caused by that, do some sanity checks first. Changes can be checked in the
    # CPython repository. E.g.:
    #   git clone https://github.com/python/cpython.git
    #   git diff -w --color-moved origin/3.10:Lib/zipfile.py origin/3.11:Lib/zipfile.py
    # Note that Lib/zipfile.py was split up and moved into lib/zipfile since Python 3.12.0a3!
    # Of course, we are mostly only interested in changes to zipfile.ZipExtFile and
    # zipfile._ZipyDecrypter.
    if not hasattr(zipfile, "ZipExtFile"):
        warnings.warn("zipfile.ZipExtFile does not exist. Cannot patch faster decryption.")
        return

    if not hasattr(zipfile, "_ZipDecrypter"):
        warnings.warn("zipfile._ZipDecrypter does not exist. Cannot patch faster decryption.")
        return

    if not hasattr(zipfile.ZipExtFile, "_read2"):
        warnings.warn("zipfile.ZipExtFile._read2 does not exist. Cannot patch faster decryption.")
        return

    # File created with:
    #     rm foo.zip
    #     echo secret > foo
    #     # Several alternatives. I'd use the smallest generated file out of these.
    #     zip --encrypt --password foo foo.zip foo
    #     7z -pfoo foo.zip
    #     python3 -c 'import pyminizip; pyminizip.compress("foo", None, "foo.zip", "foo", 9)'
    # String created with: python3 -c 'data=open("foo.zip", "rb").read();
    #     print("\n".join([repr(data[i * 16:(i + 1) * 16]) for i in range((len(data) + 15) // 16)]))'
    minimal_test_file = io.BytesIO(
        b"PK\x03\x04\x14\x00\x03\x00\x08\x00\xd4\x8b=Y\x8c\xb2"
        b"\xeb\xe2\x15\x00\x00\x00\x07\x00\x00\x00\x03\x00\x00\x00fo"
        b"o\xc12|\xa2\xda\xe4\xffb\x1f\xdc\xfb\xdea%\x98"
        b")\xc2\xac;\xb8\x1bPK\x01\x02\x00\x00\x14\x00\x03\x00"
        b"\x08\x00\xd4\x8b=Y\x8c\xb2\xeb\xe2\x15\x00\x00\x00\x07\x00"
        b"\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00fooPK\x05\x06\x00\x00\x00\x00\x01"
        b"\x00\x01\x001\x00\x00\x006\x00\x00\x00\x00\x00"
    )

    OldZipExtFile = zipfile.ZipExtFile
    OldZipDecrypter = zipfile._ZipDecrypter

    zipfile.ZipExtFile = FastZipExtFile
    zipfile._ZipDecrypter = _zipdecrypter.StandardZipDecrypter

    try:
        with zipfile.ZipFile(minimal_test_file) as archive:
            archive.setpassword(b"foo")
            with archive.open(archive.infolist()[0]) as file:
                assert file.read() == b"secret\n"
    except Exception as exception:
        tb = ''.join(traceback.format_exception(exception))
        warnings.warn(f"Will not patch faster decryption because it would lead to: {type(exception)} {exception}\n{tb}")
        zipfile.ZipExtFile = OldZipExtFile
        zipfile._ZipDecrypter = OldZipDecrypter


monkeypatch()
