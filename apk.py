#!/usr/bin/python2
import argparse, os, shutil
from tempfile import mkdtemp

class PathAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values:
            setattr(namespace, self.dest, os.path.abspath(values))
        else:
            setattr(namespace, self.dest, None)

parser = argparse.ArgumentParser(description='Create unsigned apk file.')
parser.add_argument('-o', '--output',   dest='output',       action=PathAction, metavar='FILE', help='Write apk to FILE.', required=True)
parser.add_argument('-d', '--dex',      dest='dex',          action=PathAction, metavar='FILE', help='Dalvik vm bytecode.', required=True)
parser.add_argument('-a', '--assets',   dest='assets_jar',   action=PathAction, metavar='FILE', help='Jar file with assets.')
parser.add_argument('-P', '--aapt',     dest='aapt',         action=PathAction, metavar='FILE', help='Location of the aapt tool.', required=True)
parser.add_argument('-I', '--android',  dest='android_jar',  action=PathAction, metavar='FILE', help='Android API jar file.', required=True)
parser.add_argument('-L', '--lib',      dest='lib_jar',      action=PathAction, metavar='FILE', help='Jar file with arch-dependent shared libraries (/ARCH/*.so).')
parser.add_argument('-M', '--manifest', dest='manifest',     action=PathAction, metavar='FILE', help='Location of AndroidManifest.xml.', required=True)
parser.add_argument('-S', '--resource', dest='resource_jar', action=PathAction, metavar='FILE', help='Jar file containing resources (/res stuff).', required=True)
args = parser.parse_args()

root = mkdtemp()
resdir = os.path.join(root, 'res')
bindir = os.path.join(root, 'bin')

def spawn(command):
    ret = os.spawnvp(os.P_WAIT, command[0], command)
    if ret != 0:
        exit(ret)

try:
    # extract resources
    os.mkdir(resdir)
    os.chdir(resdir)
    spawn(['fastjar', 'xf', args.resource_jar])
    shutil.rmtree('META-INF')

    # populate /bin
    os.mkdir(bindir)
    os.chdir(bindir)

    # bin/classes.dex
    shutil.copy(args.dex, 'classes.dex')

    # bin/assets
    if args.assets_jar:
        os.mkdir('assets')
        os.chdir('assets')
        spawn(['fastjar', 'xf', args.assets_jar])
        shutil.rmtree('META-INF')
        os.chdir(bindir)

    # bin/lib
    if args.lib_jar:
        os.mkdir('lib')
        os.chdir('lib')
        spawn(['fastjar', 'xf', args.lib_jar])
        shutil.rmtree('META-INF')
        os.chdir(bindir)        

    os.chdir(root)
    ret = os.spawnv(os.P_WAIT, args.aapt,
                    [args.aapt, 'package', '-f', '-M', args.manifest, '-S', resdir,
                     '-I', args.android_jar, '-F', args.output, bindir])
    if ret != 0:
        exit(ret)
finally:
    os.chdir('/')
    shutil.rmtree(root)
