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
parser.add_argument('-o', '--output',   dest='output',       action=PathAction, metavar='FILE', help='Write R.java to FILE.', required=True)
parser.add_argument('-P', '--aapt',     dest='aapt',         action=PathAction, metavar='FILE', help='Location of the aapt tool.', required=True)
parser.add_argument('-I', '--android',  dest='android_jar',  action=PathAction, metavar='FILE', help='Android API jar file.', required=True)
parser.add_argument('-M', '--manifest', dest='manifest',     action=PathAction, metavar='FILE', help='Location of AndroidManifest.xml.', required=True)
parser.add_argument('-S', '--resource', dest='resource_jar', action=PathAction, metavar='FILE', help='Jar file containing resources (/res stuff).', required=True)
args = parser.parse_args()

root = mkdtemp()
resdir = os.path.join(root, 'res')

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

    os.chdir(root)
    ret = os.spawnv(os.P_WAIT, args.aapt,
                    [args.aapt, 'package', '-f', '-S', resdir, '-M', args.manifest,
                     '-I', args.android_jar, '-J', '.'])
    if ret != 0:
        exit(ret)

    shutil.copy('R.java', args.output)
finally:
    os.chdir('/')
    shutil.rmtree(root)
