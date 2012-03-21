#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software
#     - Version and compatibility information -
#    Copyright (C) 2011-2012  riot <riot@hackerfleet.org>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os


# Fallback versioning info, for when we're run off our mercurial
# repository. We need to keep these rather up to date, upon relevant changes.

_default_ver = '0.0.1'
_default_ver_num = 0,0,1
_default_ver_details = {'author': None,
               'branch': None,
               'date': None,
               'desc': None,
               'node': None,
               'parents': None,
               'rev': None,
               'tags': None}

def _ver_hgapi():
    """Tries to obtain detailed version information of the running instance via hgapi."""
    import hgapi
    repo = hgapi.Repo(os.path.abspath(os.curdir))
    ver_details = repo.revision(repo.hg_rev()).__dict__
    return ver_details


def test():
    """N/A: Should test the version information system."""
    print "No tests yet."
    print "Version: %s\nNumerical Version: %s\nDetailed Version: %s" % (ver, ver_num, ver_details)


try:
    ver_details = _ver_hgapi()
    ver = '0.0.%d' % ver_details['rev']
    ver_num = 0,0,ver_details['rev']
except:
    ver = _default_ver
    ver_num = _default_ver_num
    ver_details = _default_ver_details

if __name__ == "__main__":
    test()
