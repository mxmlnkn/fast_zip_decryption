from setuptools import setup
from setuptools import Extension
from os import path

decrypter = Extension('_zipdecrypter',
                      ['extension/_zipdecryptermodule.c'],
                      language='c',
                      extra_compile_args=["-std=c99"])

setup(ext_modules=[decrypter], zip_safe=False)
