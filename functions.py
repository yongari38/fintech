import numpy as np
import math
import os
import urllib.request
import traceback
from html.parser import HTMLParser
import time

# prints formatted price
def formatPrice(n):
    return ("-$" if n < 0 else "$") + "{0:.2f}".format(abs(n))

class Parser(HTMLParser):
    dt = []
    def handle_startendtag(self, tag, attrs):
        Parser.dt.append(attrs[0][1].split('|'))

# returns the vector containing stock data from a fixed file
###########################
##### add date return #####
###########################
def getStockDataVec(key):
    vec = []
    dt = []

    filename = "data/" + key + ".csv"
    if not os.path.isfile(filename):
        print('Downloading New Data')
        url = 'http://fchart.stock.naver.com/sise.nhn?symbol={}&timeframe=day&count=1825&requestType=0'.format(key)
        print(url)
        try:
            u = urllib.request.urlopen(url)
            r = u.read().decode('euc-kr')
            ps = Parser()
            ps.feed(r)
            f = open(filename, 'w')
            f.write('Date,Open,High,Low,Close,Adj Close,Volume\n')
            for item in ps.dt:
                if item[1] == '0':
                    continue
                f.write('{},{},{},{},{},{},{}\n'.format('{}-{}-{}'.format(item[0][0:4], item[0][4:6], item[0][6:8]), item[1], item[2], item[3], item[4], item[4], item[5]))
            f.close()

        except:
            traceback.print_exc()

    lines = open(filename, "r").read().splitlines()

    # data regularization (won => dollar) (might be leaky)
    first_line = lines[1]
    first_number = float(first_line.split(",")[4])
    cnt = 0
    while first_number>1000:
        first_number/=10
        cnt+=1
    
    for line in lines[1:]:
        temp = float(line.split(",")[4])
        for i in range(cnt):
            temp/=10
        vec.append(temp)
        #vec.append(float(line.split(",")[4]))
        dt.append(line.split(",")[0])
    return vec, dt
    
########################### 
##### add date return #####
###########################

# returns the sigmoid
def sigmoid(x):
    try:
        if x < 0:
            return 1 - 1 / (1 + math.exp(x))
        return 1 / (1 + math.exp(-x))
    except OverflowError as err:
        print("Overflow err: {0} - Val of x: {1}".format(err, x))
    except ZeroDivisionError:
        print("division by zero!")
    except Exception as err:
        print("Error in sigmoid: " + err)
    

# returns an an n-day state representation ending at time t
def getState(data, t, n):
    d = t - n + 1
    block = data[d:t + 1] if d >= 0 else -d * [data[0]] + data[0:t + 1] # pad with t0
    res = []
    for i in range(n - 1):
        res.append(sigmoid(block[i + 1] - block[i]))

    return np.array([res])

