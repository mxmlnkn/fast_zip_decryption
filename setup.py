from os import path

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from wheel.bdist_wheel import bdist_wheel


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


class bdist_wheel_abi3(bdist_wheel):
    def get_tag(self):
        python, abi, plat = super().get_tag()
        if python.startswith("cp"):
            # On CPython, our wheels are abi3 and compatible back to 3.6.
            return "cp38", "abi3", plat
        return python, abi, plat


decrypter = Extension(
    "_zipdecrypter",
    sources=["extension/_zipdecryptermodule.c"],
    language="c",
    extra_compile_args=["-std=c99"],
    # https://docs.python.org/3/c-api/stable.html#c.Py_LIMITED_API
    # https://docs.python.org/3/c-api/apiabiversion.html#c.Py_Version
    define_macros=[("Py_LIMITED_API", "0x030800f0")],
    py_limited_api=True,
)
setup(ext_modules=[decrypter], cmdclass={"build_ext": Build, "bdist_wheel": bdist_wheel_abi3})
