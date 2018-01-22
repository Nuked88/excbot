from binance.client import Client
import sys
from pprint import pprint
import json
import pymongo
from pymongo import MongoClient


#sym = 'DNTETH'
client = Client('U01TzZbguId4mdlf99GQt54ez9tedKQkn5RBIIqKDENbcf9eeSKGCEEEmcs5I15G','FiXFodY1J0EJKfmxToqTblR0kyoZibe2QJIqis2PMJaif3d9PNRmdv1NVLrINtDR')
prices = client.get_all_tickers()
##MONGO DB START

cdb =  MongoClient('localhost', 27017)
db = cdb.excbot
data = db.data2
import datetime




##MONGO DB END

def update():
    
    import time
    #while True:
    prices = client.get_all_tickers()
    #prices = client.get_symbol_ticker("TRXETH")
    #xt=prices['price']
    #xt = [val['price'] for val in prices if val['symbol'] == sym] 
    #pprint(prices)
    posts=[]
    for val in prices:
        sym= val['symbol']
        xt= val['price']
        datacount= data.find({"sym": {'$eq': sym}}).count()
        #pprint(xt)
        if datacount>0:
        	old_price=float(data.find({"sym": {'$eq': sym}}).sort([("_id",-1)]).limit(1)[0]['price'])
        else:
            pprint("Empty DB!")
            old_price=float(xt)
            pprint("First Price in db: "+str(old_price)+" for "+sym)
    
    
        try:
            varn = 100 * (float(xt) - old_price) / old_price
        except ZeroDivisionError:
            varn = 0.000 #or whatever

        var=format(round(varn,8),'.8f')
        #skip first
       
        #old_price = float(xt[0])
        #time.sleep(2)
        post = {"sym": sym,"price": float(xt),"cfp": float(var),"date": datetime.datetime.utcnow()}

        if float(var)!=0.00000 or datacount == 0 or old_price==0.00000:
            posts.append(post)
            #pprint("Append: "+var+ "for "+ sym)

    data.insert_many(posts,True,True)
    pprint("Ok")
update()