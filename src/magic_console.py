import numpy as np
import collections
from random import randint
from numpy import genfromtxt
from scipy.stats import multivariate_normal
from sklearn.metrics import f1_score
import pymongo
from pymongo import MongoClient
from pprint import pprint
import os


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#cdb =  MongoClient('173.249.9.155', 27017)
cdb =  MongoClient('localhost', 27017)
db = cdb.excbot
data = db.data2
score = db.score
maxRes=40000
sym = "ETHUSDT"
maxSplit=25
aggregateData=5

#define way vector goes in the future (prediction)

#model
# se va su e poi va giù /dopo quanto /di quanto /continuo da prima?

def way(array,value):
  prevValue = 0
  wWay=0
  i=0

  
  for a in array:
    if a > prevValue:
      wWay=wWay+1+i

    else:
      wWay=wWay-1-i
    prevValue=a
    i=i+1
  if wWay<0:
    value=abs(value)*-1  
  else:
    value=abs(value)

  return wWay,value

def symList():
  symLi=[]
  datac= data.aggregate([{"$group": { "_id": '$sym'} }])
  for a in datac:
    symLi.append(a['_id'])
  return symLi

def getData(sym):
    datacount= data.aggregate([
      { "$match": { "sym": sym} },
      { "$project": {
          "year": { "$year": '$date'},
          "month": { "$month": '$date'},
          "day": { "$dayOfMonth": '$date'},
          "hour": { "$hour": '$date'},
          "minute": { "$minute": '$date'},
          "price": 1, 
          "date":1,
          "cfp":1
      }},
      {
          "$group": {
          "_id": { "date":"$date","cfp":"$cfp"},
          "price":{
              "$avg": "$price"
          }}
      },
      {
          "$limit":maxRes
      },
      { "$sort" : { '_id.date': 1 } }])
    score=0
    i=0
    armonica=0
    list1=[]
    b=[]
    
    for a in datacount:
     if str(a["price"]) != 'None':
       i=i+1
       tarr=[]
 
       tarr.append(i)
       tarr.append(a["price"])

       tarr.append(a["_id"]["cfp"])
       b.append(a["price"])
       list1.append(tarr)
       armonica=float(armonica)+(1/float(a["price"]))
      
    #PRINT DATE
    #pprint("Ultima data:")
    #pprint(list1)
   
    armonica=i/float(armonica)
    return list1,armonica

def feature_normalize(dataset):
    mu = np.mean(dataset,axis=0)
    sigma = np.std(dataset,axis=0)
    return (dataset - mu)/sigma

def estimateGaussian(dataset):
    mu = np.mean(dataset, axis=0)
    sigma = np.cov(dataset.T)
    return mu, sigma
    
def multivariateGaussian(dataset,mu,sigma):
    p = multivariate_normal(mean=mu, cov=sigma)
    return p.pdf(dataset)

#find normal way

#give numeric value of a number if you give the %
def perFor(value,per):
  return (value*per)/100

#sum the % at a value
def perSum(value,per):
  return value*(1+per/100)

def perRem(value,per):
  return value*(1-per/100)


def calcPer(old,new):
  #http://www.marcolazzari.it/blog/2010/08/24/come-calcolare-le-percentuali-con-excel-o-con-calc/
  diffP= (1-float(new)/old)* 100
  return diffP


def thresholdCalc(dataset,minAggregation):
    i=1
    cfp=0
    cfp2=0
    subArr=[]
    mainArr=[]
    for a in dataset:
      if i>=minAggregation:
        subArr=[]
        #somma valori e fai la media
        
        mcfp=cfp/minAggregation
        mcfp2=cfp2/minAggregation
        #pprint(a[0])
        subArr.append(a[0])
        subArr.append(mcfp)
        subArr.append(mcfp2)
        #pprint("media:"+str(mcfp))
        mainArr.append(subArr)
        cfp=0
        cfp2=0
        i=0
      #pprint(cfp)
      cfp=float(cfp)+float(a[1])
      cfp2=float(cfp2)+float(a[2])
      i=i+1
      

    return mainArr

def myround(x, base=5):
    return int(base * round(float(x)/base))

def elaborateData(dataset):
  i=1

  fullDataset=[]
  for a in dataset:
    newDataset=[]
    newDataset.append(a[0])
    standardDeviation= abs(perFor(a[1],a[2]))
    #pprint(str(standardDeviation)+"+"+str(a[1]))
    devmax=a[1]+standardDeviation
    
    newDataset.append(devmax)
    newDataset.append(a[1]-standardDeviation)
    fullDataset.append(newDataset)
  return fullDataset

def searchList(lists,index):
  v1=0
  v2=0

  for a in lists:
    if a[0]==index:
      v1=a[1]
      v2=a[2]
  return v1,v2


def anomalyDetector(dataset,limit,margin):
  fds=[]
  for a in dataset:
    index=myround(a[0])
    nds=[]
    #pprint(limit)
    v1,v2=searchList(limit,index)
    if a[1] > perSum(v1,margin) or a[1] < perRem(v2,margin):
      nds.append(a[0])
      nds.append(a[1])
      fds.append(nds)
  return fds


def startMagic(sym,enableGraph):
  #lets start
  l,arm= getData(sym)
  #pprint(l)
  
  tr_data=np.array(l)
  data = elaborateData(l)
  #pprint(data)
  data=thresholdCalc(data,aggregateData)
  #pprint(data)
  th_data=np.array(data)
  #y=np.array(arm)
  
  
  n_dim = tr_data.shape[1]
  #normal point
  x=tr_data[:,0]
  y=tr_data[:,1]
  
  #margin
  xT=th_data[:,0]
  yTp=th_data[:,1]
  yTm=th_data[:,2]
  
  #anomaly
  anmly=anomalyDetector(l,data,1)
  ta_data=np.array(anmly)
  #pprint(anmly)
  xA=ta_data[:,0]
  yA=ta_data[:,1]
  
  

    
    
    
    #normal point minute/price
    
    #anomaly with X
    
    #margin up and down outside is an anomaly
    
    
  
  n_r = np.count_nonzero(th_data)
  #pprint(n_r)
  th_data_split=np.array_split(th_data, maxSplit)
  
  futureDirection=[]
  
  #draw segment
  for c in th_data_split:
    xT2=c[:,0]
    yTp2=c[:,1]
    yTm2=c[:,2]
    m, b = np.polyfit(xT2, yTp2, 1)
    m2, b2 = np.polyfit(xT2, yTm2, 1)
    futureDirection.append(m)

      #vector data analisis divided by X minutes (max Split)

      
      
  
  
  
  
  
  #ATF 0.001 MILESTRONE (Assume The Future)
  future_data=[]
  lastInd=xT2[::-1][0]
  lastY=yTp2[::-1][0]
  nextInd=round((n_r/maxSplit),0)
  
  #pprint("Previsione nei prossimi "+ str(nextInd) +" minuti")
  
  direction,m=way(futureDirection,m)
  
  for d in range(0,int(nextInd)):
    internalArr=[]
    #se  lastY:m*(lastInd-1) + b = {FUTURE}:m*lastInd + b
  
    #quindi {FUTURE}=(lastY*(m*lastInd + b))/(m*(lastInd-1) + b)
    lastInd=lastInd+1 
    nextVal=(lastY*(m*lastInd + b))/(m*(lastInd-1) + b)
    lastY=nextVal
    #pprint(nextVal)
    internalArr.append(lastInd)
    internalArr.append(nextVal)
    future_data.append(internalArr)
  
  direction2=m
  
  #pprint(direction)
  future_data=np.array(future_data)
  xF=future_data[:,0]
  yF=future_data[:,1]
  

    
    

  return direction,nextInd,future_data,direction2

clear = lambda: os.system('cls')

#-----------------------------------------------------------------------------------------------------------------
#start the fun
clear()
print("   _______     _____ ______       _  __   ")
print("  / /  ___|   /  __ \| ___ \     | | \ \  ")
print(" / /| |____  _| /  \/| |_/ / ___ | |_ \ \ ")
print("< < |  __\ \/ / |    | ___ \/ _ \| __| > >")
print(" \ \| |___>  <| \__/\| |_/ / (_) | |_ / / ")
print("  \_\____/_/\_\\____/\____/ \___/ \__/_/  ")
print("                                          ")
print("                                          ")


print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
symbols=symList()
#symbols=["IOTAETH","TRXETH"]
for symbol in symbols:
  
  if symbol!="123456" or symbol!="VIABNB":
    #pprint(symbol)
    try:
      direction,nextInd,future_data,direction2= startMagic(symbol,0)

      if direction>0:
        stringa=bcolors.OKGREEN +"Positive" 
      else: 
        stringa=bcolors.FAIL +"Negative" 
      print(f"Prevision for {symbol} is {stringa} by {direction2} Trend:{direction} Price can go from: {future_data[0][1]} to {future_data[-1][1]} {bcolors.ENDC}")
      #print("Prevision is "+ stringa +" by "+str(direction)+" Price can go from: "+str(future_data[0][1])+" to "+str(future_data[-1][1]))
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible!!
      break
    except:
      pass
#getData()


