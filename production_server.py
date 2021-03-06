#!./venv/bin/python
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from pymongo import MongoClient
import datetime
import threading

from pqr import pqr
import pqr.views as pqv

# Opens the redirect file and stores in the redirect_table
# dictionary in the views.py file
with open("./pqr/server_start/redirect_file", "r") as redir:
    for line in redir:
        lineArr = line.strip().split(',')
        key = lineArr[0]
        value = lineArr[1].strip()
        pqv.redirect_table[key] = value

# Set the Molecule of the Week
def set_weeekly_mol():

    # Gets todays date, then rewinds it to the last Sunday
    # (if today is Sunday it sticks with today)
    # Then it compares each line in the file to Sunday's date
    # And when it finds a match, it changes MOLECULE_OF_THE_WEEK in views
    # Also, this thread is run once per day
    today = datetime.date.toordinal(datetime.datetime.now())
    sunday = today - ( today % 7)
    sunday = datetime.date.fromordinal(sunday)
    sunday = datetime.date.isoformat(sunday)
    with open("./pqr/server_start/mol_of_the_week", "r") as molfile:
        for line in molfile:
            if line.strip().split(",")[0] <= datetime.datetime.isoformat(datetime.datetime.now()).replace('-', ''):
                pqv.MOLECULE_OF_THE_WEEK = line.strip().split(",")[1]
                pqv.WEEKLY_MOL_NAME = line.strip().split(",")[2].title()
                print pqv.MOLECULE_OF_THE_WEEK
            if line.strip().split(",")[0] > datetime.datetime.isoformat(datetime.datetime.now()).replace('-', ''):
                break
    threading.Timer(86400, set_weeekly_mol).start()

set_weeekly_mol()

# Get number of molecules in database
client = MongoClient()
db = client.test
pqv.amount_mol = db.molecules.count()
client.close()

http_server = HTTPServer(WSGIContainer(pqr))
http_server.listen(80)
IOLoop.instance().start()
