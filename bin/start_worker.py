#!/usr/bin/env python3

import os
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), '../project'))


from worker import start_worker


if __name__ == '__main__':
    start_worker()
