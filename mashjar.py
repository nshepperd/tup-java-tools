#!/usr/bin/python2
import argparse, os
import shutil
from tempfile import mkdtemp

parser = argparse.ArgumentParser(description='Combine jar files.')
parser.add_argument('-o', '--output', dest='output', metavar='FILE', help='Write the jar to FILE.', required=True)
parser.add_argument('-e', '--entry-point', dest='entry_point', metavar='CLASS', help='Entry point of the program, if you are making an executable.', default=None)
parser.add_argument('files', metavar='file', help='Input files', nargs='+')
args = parser.parse_args()

output = os.path.abspath(args.output)
files = [os.path.abspath(fname) for fname in args.files]

root = mkdtemp()
jardir = os.path.join(root, 'jar')

try:
    os.mkdir(jardir)
    os.chdir(jardir)
    # extract jars
    for fname in files:
        ret = os.spawnvp(os.P_WAIT, 'fastjar', ['fastjar', 'xf', fname])
        if ret != 0:
            exit(ret)

    if os.path.exists('META-INF/MANIFEST.MF'):
        os.remove('META-INF/MANIFEST.MF')

    # make new jar
    if args.entry_point:
        manifest_text = '''Manifest-Version: 1.0\nMain-Class: ''' + args.entry_point + '\n'
        with open(os.path.join(root, 'manifest.txt'), 'w') as file:
            file.write(manifest_text)
        ret = os.spawnvp(os.P_WAIT, 'fastjar', ['fastjar', 'cfm', output, os.path.join(root, 'manifest.txt'), '.'])
    else:
        ret = os.spawnvp(os.P_WAIT, 'fastjar', ['fastjar', 'cf', output, '.'])
    if ret != 0:
        exit(ret)
finally:
    os.chdir('/')
    shutil.rmtree(root)
