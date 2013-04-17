from distutils.core import setup

VERSION = "0.1"

setup(
    name = "sequence", 
    version = VERSION, 
    author = "Thomas Leichtfuss", 
    author_email = "thomaslfuss@gmx.de",
    url = "https://github.com/thomst/sequence",
    download_url = "https://pypi.python.org/packages/source/t/sequence/sequence-{version}.tar.gz".format(version=VERSION),
    description = 'has to be written...',
    long_description = "has to be written as well...",
    py_modules = ["sequence"],
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
