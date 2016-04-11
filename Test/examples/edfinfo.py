#!/usr/bin/env python
import numpy as np
import edflib


if __name__=='__main__':
    import sys
    if len(sys.argv) == 2:
        fn = sys.argv[1]
        e = edflib.Edfinfo(fn)
        e.file_info()
        e.file_info_long()
