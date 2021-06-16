from Cython.Build import cythonize
from setuptools import Extension, setup

setup(
    ext_modules = cythonize([
        Extension("sunvox", sources=["src/*.pyx"],
        # Extension("sunvox", sources=["src/*.pyx", "src/functions.c"],
        
            # define_macros = [('MAJOR_VERSION', '1'),
            #                  ('MINOR_VERSION', '0')],
            include_dirs = ['./include'],
            libraries=["sunvox"],
            library_dirs = ['./lib'],
            # sources = ['demo.c'],
        )
    ], language_level = "3")
)
