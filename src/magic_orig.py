import pymongo
from pymongo import MongoClient
from pprint import pprint

cdb =  MongoClient('localhost', 27017)
db = cdb.excbot
data = db.data
score = db.score

def calcPer(old,new):
	#http://www.marcolazzari.it/blog/2010/08/24/come-calcolare-le-percentuali-con-excel-o-con-calc/
	diffP= (1-float(new)/old)* 100
	return diffP


def getData():
   datacount= data.aggregate([
    { "$match": { "sym": "CNDETH"} },
    { "$project": {
        "year": { "$year": '$date'},
        "month": { "$month": '$date'},
        "day": { "$dayOfMonth": '$date'},
        "hour": { "$hour": '$date'},
        "minute": { "$minute": '$date'},
        "price": 1
 
    }},

    {
        "$group": {
        "_id": { "year": '$year', "month": '$month', "day": '$day', "hour": '$hour', "minute": '$minute'},
        "price":{
            "$avg": "$price"
        }}
    },
    {
        "$limit":400
    },
    { "$sort" : { "_id" : -1 } }])
   prevPrice = 0.01
   score=0
   i=0
   armonica=0
   list1=[]
   



   for a in datacount:
   	if str(a["price"]) != 'None':
   		i=i+1
   		#pprint(i)
   		armonica=float(armonica)+(1/float(a["price"]))
   		list1.append(a["price"])


   #media armonica prezzi
   armonica=i/float(armonica)
   pprint(armonica)


   #parametri
   p1=1
   p2=5
   p3=10
   p4=50
   p5=100


   for d in list1:
     try:
       perc=round(calcPer(armonica,d),3)    
       if d>armonica:
       	  if perc>p1 and perc<p2:
       	  	score=score+1
       	  elif perc>p2 and perc<p3:
       	  	score=score+2
       	  elif perc>p3 and perc<p4:
       	  	score=score+3
       	  elif perc>p4 and perc<p5:
       	  	score=score+5
       	  elif perc>p5:
       	  	score=score+10
          #pprint(str(round(calcPer(prevPrice,d),3))+"% +++++1")         
       elif d<armonica:
       	  if perc<p1:
       	  	pprint(perc)
       	  	score=score-1
       	  elif perc<-p2 and perc>-p1:
       	  	score=score-2
       	  elif perc<-p3 and perc>-p2:
       	  	score=score-3
       	  elif perc<-p4 and perc>-p3:
       	  	score=score-5
       	  elif perc<-p5 and perc>-p4:
       	  	score=score-10 
          #pprint(str(round(calcPer(prevPrice,d),3))+"% -----1")
     except ValueError:
            print("Invalid Entry - try again")  
   pprint(score)
getData()


