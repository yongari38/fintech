from agent.agent import Agent
from functions import *
import sys


from keras.callbacks import TensorBoard, EarlyStopping

try:
    if len(sys.argv) != 4:
        print ("Usage: python train.py [stock] [window] [episodes]")
        exit()

    stock_name, window_size, episode_count = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])

    agent = Agent(window_size)
    data, dt = getStockDataVec(stock_name)
    
    batch_size = 32
    
    l = len(data) - 1
    print(l)

    epoch_f = open("epoch_result.txt", 'a')
    line = "===case: python3 train.py %s %s %s===\n"%(stock_name, window_size, episode_count)
    epoch_f.write(line)
    for e in range(episode_count + 1):
        print ("Episode " + str(e) + "/" + str(episode_count))
        state = getState(data, 0, window_size + 1)

        stock_cnt = 0
        init_cash = 10000
        cash = init_cash
        
        total_profit = 0
        agent.inventory = []

        sell_cnt = 0
        buy_cnt = 0
        sit_cnt = 0
        
        reward = 0 # declare outside loop for epoch_result usage
        for t in range(l):
            action = agent.act(state)
            print("{} 보유수량: {:2} 총평가금액: {:.2f} 현재가격: {:.2f}  {}".format(dt[t], stock_cnt, cash + data[t] * stock_cnt, data[t], action))
            
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
                stock_cnt-=1
                cash+=data[t]
            
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

            reward += cash+data[t]*stock_cnt - init_cash

            agent.memory.append((state, action, reward, next_state, (t==l-1)))
            state = next_state

            if (t==l-1):
                print ("-------------------------------------------")
                print ("DIFF: {:.2f}, Reward: {:.2f}".format(cash+data[t]*stock_cnt-init_cash, reward))
                print ("-------------------------------------------")

            if len(agent.memory) > batch_size:
                agent.expReplay(batch_size)

        if e % 20 == 0:
            agent.model.save("models/model_ep" + str(e))

            line = "Epoch: %d, DIFF: %2f, Reward: %2f\n"%(e,(cash+data[t]*stock_cnt-init_cash),reward)
            epoch_f.write(line)


except Exception as e:
    print("Error occured: {0}".format(e))
finally:
    epoch_f.close()
    exit()
