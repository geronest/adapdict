# -*- coding: utf-8 -*-
import sys
from bin.MainManager import MainManager

if __name__ == '__main__':
    if len(sys.argv) > 1:
        mm = MainManager(sys.argv[1])
    else:
        mm = MainManager()
    mm.mainloop()
