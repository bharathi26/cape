from distutils.core import setup

from ANRV.Version import ver

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.
files = ["ANRV/*"]

setup(name = "anrv",
    version = ver,
    description = "Autonomous Naval Robotic Vehicle OS",
    license = "GPL v3",
    platform = "Linux",
    author = "Hackerfleet Contributors",
    author_email = "riot@hackerfleet.org",
    url = "https://hackerfleet.org/anrv",
    packages = ['ANRV',
                'ANRV.Communication',
                'ANRV.Controls',
                'ANRV.Interface',
                'ANRV.Sensors',
                'ANRV.System',
                'ANRV.Test',
                ],
    #package_data = {'package' : files },
    #scripts = [""], # None yet
    long_description = """WiP""" 
    #This next part it for the Cheese Shop, look a little down the page.
    #classifiers = [] # Hmm, would we want to use the cheese shop?
) 
