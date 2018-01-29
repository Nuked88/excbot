from __future__ import division
from itertools import count
import matplotlib.pyplot as plt
from numpy import linspace, loadtxt, ones, convolve
import numpy as np
import pandas as pd
import collections
from random import randint
from matplotlib import style
import pymongo
from pymongo import MongoClient
from pprint import pprint

#cdb =  MongoClient('173.249.9.155', 27017)
cdb =  MongoClient('localhost', 27017)
db = cdb.excbot
data = db.data2
score = db.score
maxRes=40000
sym = "ETHUSDT"


def way(array):
  prevValue = 0
  wWay=0
  for a in array:
    if a > prevValue:
      wWay=wWay+1
    else:
      wWay=wWay-1
    prevValue=a
  return wWay


def getData():
    datacount= data.aggregate([
      { "$match": { "sym": sym} },
      { "$project": {
          "year": { "$year": '$date'},
          "month": { "$month": '$date'},
          "day": { "$dayOfMonth": '$date'},
          "hour": { "$hour": '$date'},
          "minute": { "$minute": '$date'},
          "price": 1, 
          "date":1
      }},
      {
          "$group": {
          "_id": { "date":"$date"},
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
       #pprint(str(a["price"])+"-"+str(a["_id"]))
       tarr.append(i)
       tarr.append(a["price"])
       tarr.append(a["_id"]["date"])
       b.append(a["price"])
       list1.append(tarr)
       
       #list1['SunSpots'].append(a["price"])
       armonica=float(armonica)+(1/float(a["price"]))
      
    #PRINT DATE
    pprint("Ultima data:")
    pprint(list1)
    #mi dice se va su o giù 
    res=(100*way(b))/maxRes
    pprint("Guadagno/Perdita")
    pprint(str(res)+"%")

    #media armonica prezzi
    pprint("Numero risultati:")
    pprint(i)
    armonica=i/float(armonica)
    return [list1,armonica]



# 3. Lets define some use-case specific UDF(User Defined Functions)

def moving_average(data, window_size):
    """ Computes moving average using discrete linear convolution of two one dimensional sequences.
    Args:
    -----
            data (pandas.Series): independent variable
            window_size (int): rolling window size

    Returns:
    --------
            ndarray of linear convolution

    References:
    ------------
    [1] Wikipedia, "Convolution", http://en.wikipedia.org/wiki/Convolution.
    [2] API Reference: https://docs.scipy.org/doc/numpy/reference/generated/numpy.convolve.html

    """
    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(data, window, 'same')


def explain_anomalies(y, window_size, sigma=1.0):
  """ Helps in exploring the anamolies using stationary standard deviation
  Args:
  -----
      y (pandas.Series): independent variable
      window_size (int): rolling window size
      sigma (int): value for standard deviation

  Returns:
  --------
      a dict (dict of 'standard_deviation': int, 'anomalies_dict': (index: value))
      containing information about the points indentified as anomalies

  """
  avg = moving_average(y, window_size).tolist()
  residual = y - avg
  # Calculate the variation in the distribution of the residual
  std = np.std(residual)
  return {'standard_deviation': round(std, 8),
          'ad': collections.OrderedDict([(index, y_i) for
                                                     index, y_i, avg_i in zip(count(), y, avg)
            if (y_i > avg_i + (sigma*std)) | (y_i < avg_i - (sigma*std))])}


def explain_anomalies_rolling_std(y, window_size, sigma=1.0):
    """ Helps in exploring the anamolies using rolling standard deviation
    Args:
    -----
        y (pandas.Series): independent variable
        window_size (int): rolling window size
        sigma (int): value for standard deviation

    Returns:
    --------
        a dict (dict of 'standard_deviation': int, 'anomalies_dict': (index: value))
        containing information about the points indentified as anomalies
    """
    avg = moving_average(y, window_size)
    avg_list = avg.tolist()
    residual = y - avg
    # Calculate the variation in the distribution of the residual
    testing_std = pd.rolling_std(residual, window_size)
    testing_std_as_df = pd.DataFrame(testing_std)
    rolling_std = testing_std_as_df.replace(np.nan,
                                  testing_std_as_df.ix[window_size - 1]).round(3).iloc[:,0].tolist()
    std = np.std(residual)
    return {'stationary standard_deviation': round(std, 3),
            'anomalies_dict': collections.OrderedDict([(index, y_i)
                                                       for index, y_i, avg_i, rs_i in zip(count(),
                                                                                           y, avg_list, rolling_std)
              if (y_i > avg_i + (sigma * rs_i)) | (y_i < avg_i - (sigma * rs_i))])}


# This function is repsonsible for displaying how the function performs on the given dataset.
def plot_results(x, y, window_size, sigma_value=1,
                 text_xlabel="X Axis", text_ylabel="Y Axis", applying_rolling_std=False):
    """ Helps in generating the plot and flagging the anamolies.
        Supports both moving and stationary standard deviation. Use the 'applying_rolling_std' to switch
        between the two.
    Args:
    -----
        x (pandas.Series): dependent variable
        y (pandas.Series): independent variable
        window_size (int): rolling window size
        sigma_value (int): value for standard deviation
        text_xlabel (str): label for annotating the X Axis
        text_ylabel (str): label for annotatin the Y Axis
        applying_rolling_std (boolean): True/False for using rolling vs stationary standard deviation
    """
    #plt.figure(figsize=(15, 8))
    #plt.plot(x, y, "k.")
    #y_av = moving_average(y, window_size)
    #plt.plot(x, y_av, color='green')
    #plt.xlim(0, 600)
    #plt.xlabel(text_xlabel)
    #plt.ylabel(text_ylabel)

    # Query for the anomalies and plot the same
    events = {}
    if applying_rolling_std:
        events = explain_anomalies_rolling_std(y, window_size=window_size, sigma=sigma_value)
    else:
        events = explain_anomalies(y, window_size=window_size, sigma=sigma_value)

    x_anomaly = np.fromiter(events['ad'].keys(), dtype=int, count=len(events['ad']))
    y_anomaly = np.fromiter(events['ad'].values(), dtype=float,
                                            count=len(events['ad']))
    return events


def calcPer(old,new):
  #http://www.marcolazzari.it/blog/2010/08/24/come-calcolare-le-percentuali-con-excel-o-con-calc/
  diffP= (1-float(new)/old)* 100
  return diffP

# 4. Lets play with the functions

data = getData()
data_as_frame = pd.DataFrame(data[0], columns=['Months', 'SunSpots','Date'])
data_as_frame.head()
pprint("Media Armonica:")
pprint(data[1])
x = data_as_frame['Months']
Y = data_as_frame['SunSpots']

# plot the results
anomaly=plot_results(x, y=Y, window_size=10, text_xlabel="Minutes", sigma_value=2,text_ylabel="No. of Sun spots")

pprint(anomaly)

final = anomaly['ad']
rev= list(final.items())[-2]
pprint("Ultimo spike:")
pprint(rev)


#getData()


