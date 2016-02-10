#!/usr/bin/env python


import sys

import nosco

symver = nosco.Nosco()
def get_semver():
  nosco_res = symver.get_version()

  if type(nosco_res) == int:
    sys.exit(1)
  else:
    return nosco_res

if __name__ == '__main__':
  print get_semver()
