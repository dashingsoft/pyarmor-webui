from sys import platform
from setuptools import setup

__version__ = '1.4.1'

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='pyarmor-webui',
    version=__version__,
    description='A webui tool used to obfuscate and pack python scripts based on pyarmor',
    long_description=long_description,
    license="MIT License",
    url='https://github.com/dashingsoft/pyarmor-webui',
    author='Jondy Zhao',
    author_email='pyarmor@163.com',

    # For a list of valid classifiers, see
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Utilities',
        'Topic :: Security',
        'Topic :: System :: Software Distribution',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Support platforms
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],

    packages=['pyarmor.webui'],
    package_dir={'pyarmor.webui': '.'},
    package_data={
        'pyarmor.webui': ['README.rst', 'LICENSE', 'data/*.py',
                          'test/README.md', 'test/*.robot',
                          'static/index.html', 'static/*.js', 'static/*.ico',
                          'static/css/*.css', 'static/js/*.js',
                          'static/fonts/element-*',
                          'static/img/*.svg', 'static/img/*.png'],
    },

    entry_points={
        'console_scripts': [
            'pyarmor-webui=pyarmor.webui.server:main',
        ],
    },

    install_requires=['pyarmor~=7.6.0'] + (
        ['pywin32'] if platform == 'win32' else []),
)
