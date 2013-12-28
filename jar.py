#!/usr/bin/python2
import argparse, os

parser = argparse.ArgumentParser(description='Make a jar file.')
parser.add_argument('-o', '--output', dest='output', metavar='FILE', help='Write the jar to FILE.', required=True)
parser.add_argument('-C', '--root', dest='root', metavar='DIR', help='Make paths relative to DIR.', default='.')
parser.add_argument('files', metavar='file', help='Input files', nargs='+')
args = parser.parse_args()

output = os.path.abspath(args.output)
os.chdir(args.root)
os.execvp('fastjar', ['fastjar', 'cf', output] + [os.path.relpath(fname, args.root) for fname in args.files])
