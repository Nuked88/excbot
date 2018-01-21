#show data

import json
import pymongo
from pymongo import MongoClient
from datetime import datetime

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#data di partenza per il confronto dati
start_date = datetime(2018, 1, 13, 0, 00, 00)
varn=0.000

sym = 'DNTETH'
cdb =  MongoClient('mongodb', 27017)
db = cdb.excbot
data = db.data

def col(value,ttch):
   if(ttch>=0):
     a=bcolors.OKGREEN +"+"+str(value)+"%" + bcolors.ENDC
   else:
     a=bcolors.FAIL +""+str(value)+"%" + bcolors.ENDC
   return a


def totchange(start_date):
    totlist=data.find({"$and": [{'date' : {'$gte': start_date}},{"sym": {'$eq': sym}}]}).sort([("_id",1)])
    ttch=0.000
    for a in totlist:
        ttch = ttch + float(a['cfp'])
        
    return ttch



def show():
    ttch = totchange(start_date)
    tch=0.00
    resu= data.find({"sym": {'$eq': sym}}).sort([("_id",-1)]).limit(1)[0]
    price = resu['price']
    varn = float(resu['cfp'])
    date = resu ['date']
    ttch=float(ttch)+float(varn)
    tch=format(round(ttch,4),'.5f')
       
    if varn >= 0:
      print("Price of "+str(sym)+": "+ str(price)+" ch:"+ bcolors.OKGREEN +str(varn)+"%" + bcolors.ENDC+"   Total Change:  "+col(tch,ttch)+"     " ,end="\r")
    elif varn < 0:
       print("Price of "+str(sym)+": "+ str(price)+" ch:"+ bcolors.FAIL +str(varn)+"%" + bcolors.ENDC+"   Total Change:  "+col(tch,ttch)+"     " ,end="\r")

show()