import sys
from os.path import join, dirname
keyname = 'pyarmor.rkey'
with open(join(dirname(sys.executable), keyname), 'rb') as fs:
    with open(join(sys._MEIPASS, keyname), 'wb') as fd:
        fd.write(fs.read())

