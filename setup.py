from setuptools import setup
import os.path

from cape.system.version import ver

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.
files = ["cape/*"]

setup(name = "cape",
    version = ver,
    description = "Component Architecture for Python Environments",
    license = "GPL v3",
    author = "Hackerfleet Contributors",
    author_email = "riot@hackerfleet.org",
    url = "https://hackerfleet.org/cape",
    packages = ['cape',
                'cape.system',
                ],
    package_data = {'cape': ['cape']},
    scripts = ['cape.py'],
    entry_points="""
    [cape.components]
    cape.system.loggercomponent=cape.system.loggercomponent:LoggerComponent
    cape.system.registrycomponent=cape.system.registrycomponent:RegistryComponent
    cape.system.mongocomponent=cape.system.mongocomponent:MongoComponent
    cape.system.webgate=cape.system.webgate:WebGate
    cape.system.idler=cape.system.idler:Idler
    """,
    zip_safe = False,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Environment :: X11 Applications',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Home Automation',
        'Topic :: Software Development :: Embedded Systems',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Hardware :: Hardware Drivers',
        'Topic :: System :: Logging',
        'Topic :: System :: Power (UPS)',
        'Topic :: System :: Networking'
    ],

    #package_data = {'package' : files },
    #scripts = [""], # None yet
    long_description = read('README'),
    # Dependencies
    #
    # Note: Those are proven to work, older versions might work, 
    # but have never been tested.
    #
    dependency_links = [
        'https://www.hackerfleet.org/redist/Kamaelia-1.1.2.0.tar.gz',
        'https://www.hackerfleet.org/redist/Axon-1.7.0.tar.gz',
        'https://www.hackerfleet.org/redist/Pmw-1.3.3.tar.gz',
    ],
    install_requires=['jsonpickle>=0.4.0',
                      'pyserial>=2.6',
                      'hgapi>=1.1.0',
                      'pillow>=1.7.8',
                      'Axon>=1.7.0',
                      'Kamaelia>=1.1.2.0',
                      'pynmea>=0.3.0',
                      'configobj>=4.7.2',
                      'Pmw>=1.3.2',
                      'pymongo>=2.4.1',
                      'pyzmq>=2.2.0.1',
                      'CherryPy>=3.2.2'
                      ]
    # OPTIONALS, currently setup only works by hard deactivating (removal) of modules, sorry.
    #extras_require={'mapnik2': 'mapnik2>=2.0.0',
    #                'smbus': 'smbus>=1.1',
    #                'pymongo': 'pymongo>=2.2'}
)
