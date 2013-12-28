#!/usr/bin/python2
import argparse, os
import shutil
import hashlib
from tempfile import mkdtemp

parser = argparse.ArgumentParser(description='Compile java files into a jar.')
parser.add_argument('-o', '--output', dest='output', metavar='FILE', help='Write the jar to FILE.', required=True)
parser.add_argument('-e', '--entry-point', dest='entry_point', metavar='CLASS', help='Entry point of the program, if you are making an executable.', default=None)
parser.add_argument('files', metavar='file', help='Input files: .java source, or .jar libraries that we depend on.', nargs='+')
args = parser.parse_args()

output = os.path.abspath(args.output)
sources = [os.path.abspath(fname) for fname in args.files if fname.endswith('.java')]
depends = [os.path.abspath(fname) for fname in args.files if fname.endswith('.jar')]
if not sources:
    exit('Error: at least one java source file expected.')

root = mkdtemp()
srcdir = os.path.join(root, 'src')
jardir = os.path.join(root, 'jar')

def digest(string):
    return hashlib.md5(string).hexdigest()

try:
    # copy source files into a temporary directory to stop javac from touching stuff it shouldn't
    os.mkdir(srcdir)
    os.chdir(srcdir)
    srclist = []
    for fname in sources:
        dirname = digest(os.path.dirname(fname))
        target = os.path.join(dirname, os.path.basename(fname))
        srclist.append(target)
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        assert not os.path.exists(target)
        shutil.copy(fname, target)

    os.mkdir(jardir)
    ret = os.spawnvp(os.P_WAIT, 'javac', ['javac', '-d', jardir, '-classpath', ':'.join(depends)] + srclist)
    if ret != 0:
        exit(ret)

    # make jar from output classfiles
    os.chdir(jardir)
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
