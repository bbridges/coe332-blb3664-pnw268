#!/usr/bin/env python3

import os
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), '../project'))


from api import app


if __name__ == '__main__':
    debug = os.environ.get('DEBUG', '0') == '1'
    app.run(debug=debug, host='0.0.0.0')
