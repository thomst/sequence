import os
from distutils.core import setup

#import sequence
#import sequence here will raise ImportError for not installed dependecies...
VERSION = '0.3.2'

setup(
    name = "sequence", 
    version = VERSION, 
    author = "Thomas Leichtfuss", 
    author_email = "thomaslfuss@gmx.de",
    url = "https://github.com/thomst/sequence",
    download_url = "https://pypi.python.org/packages/source/s/sequence/sequence-{version}.tar.gz".format(version=VERSION),
    description = 'A Python module for looping over a sequence of commands with a focus on high configurability and extensibility.',
    long_description = open('README.rst').read() if os.path.isfile('README.rst') else str(),
    py_modules = ["sequence"],
    install_requires = ['daytime'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
    ],
    license='GPL',
    keywords='loop sequence timer',
)
