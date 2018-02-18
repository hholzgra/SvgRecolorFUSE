#!/usr/bin/env python

#    Copyright (C) 2006  Andrew Straw  <strawman@astraw.com>
#
#    This program can be distributed under the terms of the GNU LGPL.
#    See the file COPYING.
#

import os, os.path, stat, errno, glob, re, logging
from colour import Color

try:
    import _find_fuse_parts
except ImportError:
    pass
import fuse
from fuse import Fuse


if not hasattr(fuse, '__version__'):
    raise RuntimeError, \
        "your fuse-py doesn't know of fuse.__version__, probably it's too old."

fuse.fuse_python_api = (0, 2)

class MyStat(fuse.Stat):
    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 1000 # os.getuid()
        self.st_gid = 1000 # os.getgid()
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

class SvgRecolorFS(Fuse):
    def __init__(self, *args, **kw):

        Fuse.__init__(self, *args, **kw)

        self.svgdir = './svg'

    def getattr(self, path):
        st = MyStat()
        if path == '/':
            st.st_mode = stat.S_IFDIR | 0755
            st.st_nlink = 2
        else:
            (p1, p2) = os.path.split(path)
            if p1 == '/' or p2 == '':
                st.st_mode = stat.S_IFDIR | 0755
                st.st_nlink = 1
            else:
                svg_path = self.svgdir + p1 +'.svg'
                mystat = os.stat(svg_path)
                st.st_mode = stat.S_IFREG | 0444
                st.st_nlink = 1
                st.st_size = mystat.st_size
        return st

    def readdir(self, path, offset):
        yield fuse.Direntry('.')
        yield fuse.Direntry('..')
        if path == '/':
            for path in glob.glob(self.svgdir + '/*.svg'):
                file = os.path.basename(path)
                (base, ext) = os.path.splitext(file)
                if ext == '.svg':
                    yield fuse.Direntry(base)
        else:
            (p1, p2) = os.path.split(path)
            if p1 == '/' or p2 == '':
                yield fuse.Direntry('red')
                yield fuse.Direntry('green')
                yield fuse.Direntry('blue')


    def open(self, path, flags):
        (p1, p2) = os.path.split(path)

        svg_path = self.svgdir + p1 +'.svg'

        color = re.sub(r"\.svg$", "", p2)
        
        try:
            hexl = Color(color).hex_l
        except ValueError:
            return -errno.ENOENT
                        
        if os.path.isfile(svg_path):
            accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
            if (flags & accmode) != os.O_RDONLY:
                return -errno.EACCES
        else:
            return -errno.ENOENT
        
        
    def read(self, path, size, offset):
        (p1, p2) = os.path.split(path)
        data = ''

        svg_path = self.svgdir + p1 +'.svg'

        color = re.sub(r"\.svg$", "", p2)

        try:
            hexl = Color(color).hex_l
        except ValueError:
            return -errno.ENOENT
                        
        if os.path.isfile(svg_path):
            with open(svg_path, 'r') as myfile:
                svgdata = myfile.read();
                svgdata = svgdata.replace('#ff0000', hexl)
        else:
            return -errno.ENOENT

        slen = len(svgdata)
        if offset < slen:
            if offset + size > slen:
                size = slen - offset
            buf = svgdata[offset:offset+size]
        else:
            buf = ''

        return buf

def main():
    usage="""
Userspace hello example
""" + Fuse.fusage
    logging.basicConfig(filename='SvgRecolorFS.log',level=logging.DEBUG)
    logging.info("SygRecolorFS starting");
    
    server = SvgRecolorFS(version="%prog " + fuse.__version__,
                     usage=usage,
                     dash_s_do='setsingle')

    server.parser.add_option(mountopt="svgdir", metavar="PATH", default=os.getcwd()+'/svg/',
                             help="directory to look for base SVGs in [default: %default]")
    server.parse(values=server, errex=1)

    server.main()

if __name__ == '__main__':
    main()
