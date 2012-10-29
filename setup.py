from distutils.core import setup

from RAIN.Version import ver

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.
files = ["RAIN/*"]

setup(name = "anrv",
    version = ver,
    description = "Autonomous Naval Robotic Vehicle OS",
    license = "GPL v3",
    author = "Hackerfleet Contributors",
    author_email = "riot@hackerfleet.org",
    url = "https://hackerfleet.org/anrv",
    packages = ['RAIN',
                'RAIN.Communication',
                'RAIN.Controls',
                'RAIN.Interface',
                'RAIN.Sensors',
                'RAIN.System',
                'RAIN.Test',
                ],
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
        'Programming Language :: Python :: 3.3',
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
    long_description = """WiP"""
) 
