import keras
from keras.models import load_model

from agent.agent import Agent
from functions import *
import sys
import random
import traceback

try:
    if len(sys.argv) != 3:
        print ("Usage: python evaluate.py [stock] [model]")
        exit()

    stock_name, model_name = sys.argv[1], sys.argv[2]
    model = load_model("models/" + model_name)
    window_size = model.layers[0].input.shape.as_list()[1]

    agent = Agent(window_size, True, model_name)
    ###########################
    ##### add date return #####
    ###########################
    data, dt = getStockDataVec(stock_name)
    ###########################
    ##### add date return #####
    ###########################
    l = len(data) - 1
    batch_size = 32

    state = getState(data, 0, window_size + 1)
    total_profit = 0
    agent.inventory = []
    print(l)
    stock_cnt = 0
    init_cash = 4000
    cash = init_cash

    sell_cnt = 0
    buy_cnt = 0
    sit_cnt = 0
    
    pp = open('temp/res_{}.csv'.format(stock_name), 'w')
    for t in range(l):
        action = agent.act(state)
        
        #random4 = random.randrange(0,4)
        # print("{} 보유수량: {:2d} 총평가금액: {:.2f} 현재가격: {:.2f}  {}".format(dt[t], stock_cnt, cash + data[t] * stock_cnt, data[t], action))
        pp.write("{},{:d},{:.2f},{:.2f},{:.2f}\n".format(dt[t], stock_cnt, cash, cash + data[t] * stock_cnt, data[t]))

        # sit
        next_state = getState(data, t + 1, window_size + 1)
        reward = 0

        if action == 1 and cash >= data[t]: # buy
            agent.inventory.append(data[t])
            #print ("Buy: " + formatPrice(data[t]))
            stock_cnt += 1
            cash -= data[t]


        elif action == 2 and len(agent.inventory) > 0: # sell
            bought_price = agent.inventory.pop(0)
            profit = data[t] - bought_price
            total_profit += profit
            #reward = profit*10 # this does not take value in stock into account
            #print ("Sell: " + formatPrice(data[t]) + " | Profit: " + formatPrice(profit))
            stock_cnt -= 1
            cash += data[t]
        '''
        if action == 0: # sit
            sit_cnt+=1
            sell_cnt = 0
            buy_cnt = 0
            reward -= sit_cnt

        elif action == 1: # buy
            buy_cnt+=1
            sell_cnt = 0
            sit_cnt = 0
            reward -= buy_cnt
                
        elif action == 2: # sell
            sell_cnt+=1
            sit_cnt = 0
            buy_cnt = 0
            reward -= sell_cnt
        '''
        reward += cash+data[t]*stock_cnt - init_cash


        agent.memory.append((state, action, reward, next_state, (t==l-1)))
        state = next_state

        if(t==l-1):
            print ("--------------------------------")
            print ("{} DIFF: {:.2f}, Reward: {:.2f}".format(stock_name, cash+data[t]*stock_cnt-init_cash, reward))
            print ("--------------------------------")
        
        if len(agent.memory) > batch_size:
            agent.expReplay(batch_size)
    pp.close()
finally:
    traceback.print_exc()
