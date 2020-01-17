import sys
from os.path import join, dirname
with open(join(dirname(sys.executable), 'license.lic'), 'rb') as fs:
    with open(join(sys._MEIPASS, 'license.lic'), 'wb') as fd:
        fd.write(fs.read())

