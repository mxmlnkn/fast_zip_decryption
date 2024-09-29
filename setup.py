from setuptools import (
        setup,
        Extension
    )
from setuptools.command.build_ext import build_ext
from os import path

decrypter = Extension('_zipdecrypter',
                      ['extension/_zipdecryptermodule.c'],
                      language='c',
                      extra_compile_args=["-std=c99"])

setup(ext_modules=[decrypter], zip_safe=False)
