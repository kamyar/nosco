#!/usr/bin/env python


import sys
import argparse

import nosco

parser = argparse.ArgumentParser(description='Nosco Wrapper for SemVer')
parser.add_argument('--write', dest='read_only', action='store_false')
parser.set_defaults(read_only=True)
args = parser.parse_args()

symver = nosco.Nosco()
def get_semver():
  nosco_res = symver.get_version(read_only=args.read_only)

  if type(nosco_res) == int:
    sys.exit(1)
  else:
    return nosco_res

if __name__ == '__main__':
  print get_semver()
  sys.exit(0)
