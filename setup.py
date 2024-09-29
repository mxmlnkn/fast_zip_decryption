from os import path

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


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
    language="c",
    extra_compile_args=["-std=c99"],
)
setup(ext_modules=[decrypter], cmdclass={"build_ext": Build})
