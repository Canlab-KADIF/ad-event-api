import sys
sys.path.insert(0, "/home/smarthmdhub/api")

python_home = '/home/smarthmdhub/api/venv'
activate_this = python_home + '/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from smarthmdhub import smarthmdhub as application
