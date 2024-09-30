from setuptools import (
        setup,
        Extension
    )
from setuptools.command.build_ext import build_ext
from os import path

here = path.abspath(path.dirname(__file__))

# https://github.com/cython/cython/blob/master/docs/src/tutorial/appendix.rst#python-38
class Build(build_ext):
    def build_extensions(self):
        for extension in self.extensions:
            # https://learn.microsoft.com/en-us/cpp/build/reference/std-specify-language-standard-version?view=msvc
            # > The compiler doesn't implement several required features of C99,
            # > so it isn't possible to specify C99 conformance, either.
            if self.compiler.compiler_type != "msvc":
                extension.extra_compile_args = ["-std=c99"]
        super().build_extensions()


decrypter = Extension(
    "_zipdecrypter",
    sources=["extension/_zipdecryptermodule.c"],
    language="c"
)

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='fastzipfile',
    version='v2.3.1',
    description='Read password protected Zips 100x faster',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/kamilmahmood/fastzipfile',
    author='Kamil Mahmood',
    author_email='kamil.mahmood@outlook.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='zip zipfile fastzip',
    python_requires='>=3.8',
    py_modules=['fastzipfile'],
    ext_modules=[decrypter],
    zip_safe=False,
    cmdclass={"build_ext": Build}
)
