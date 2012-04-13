from distutils.core import setup

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.
files = ["ANRV/*"]

setup(name = "anrv",
    version = "1",
    description = "Autonomous Naval Robotic Vehicle OS",
    author = "riot",
    author_email = "riot@hackerfleet.org",
    url = "https://hackerfleet.org/anrv",
    packages = ['ANRV'],
    #'package' package must contain files (see list above)
    #I called the package 'package' thus cleverly confusing the whole issue...
    #This dict maps the package name =to=> directories
    #It says, package *needs* these files.
    package_data = {'package' : files },
    #scripts = [""], # None yet
    long_description = """WiP""" 
    #This next part it for the Cheese Shop, look a little down the page.
    #classifiers = [] # Hmm, would we want to use the cheese shop?
) 
