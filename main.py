from flask import Flask, request, render_template, redirect
import math
import pickle
import os.path
import sys
import json
import numpy

app = Flask(__name__, static_folder='static/', static_url_path='')

id_list = [{'item1': 'https://datastudio.google.com/embed/reporting/1BPUO86dh2Kdu5jNIdVepIh-73ACGDkr7/page/jr4s',
            'item2': 'https://datastudio.google.com/embed/reporting/18UA4eqZiruDn02J0mR2cLICn9bZImgQK/page/144s'}]
#     삼성전자,    현대차,    POSCO,    현대모비스,  LG화학,    한국전력,   SK하이닉스, 신한지주, NAVER, KB
cc = ['005930', '005380', '005490', '012330', '051910', '015760', '000660', '055550', '035420', '105560']
invest = [{'name': '투자한 모델이 이렇게 시각화됨', 'current': 10500, 'diff': 4554}, {'name': 'KOSPI200','current': 20500, 'diff': 1703}]

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/user_model_list.html')
def backtest():
    if request.args.get('id') is None:
        return render_template('user_model_list.html')
    id = int(request.args.get('id')) - 1
    return render_template('user_model_list.html', item1=id_list[id]['item1'], item2=id_list[id]['item2'])

@app.route('/investor', methods=['GET', 'POST'])
def investor():
    if request.method == 'POST':
        # model. invest
        invest.append({'name': request.form['model'], 'current': int(request.form['invest']), 'diff': 0})
    return render_template('investor.html', invest=invest)

@app.route('/model', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        f.save('models/' + f.filename)


        # produce history
        history = {}
        history['description'] = request.form['description']
        for c in cc:
            os.system('python evaluate.py {} {}'.format(c, f.filename))
            csv = open('temp/res_{}.csv'.format(c), 'r')
            lines = csv.readlines()
            for line in lines:
                # date, count, cash, portfolio ,current price
                dt, ct, ch, pd, cp = line.strip().split(',')
                if not dt in history:
                    history[dt] = {}
                history[dt][c] = [ct, ch, pd, cp]
            csv.close()
        pi = open('result/{}.pickle'.format(f.filename), 'wb')
        pickle.dump(history, pi, protocol=pickle.HIGHEST_PROTOCOL)
        pi.close()
        l = open('result/list.txt', 'a+')
        l.write('{}\n'.format(f.filename))
        l.close()
        return redirect('/model_result.html?model={}'.format(f.filename))
        # return app.send_static_file('model_result.html')
    return 'fail'

@app.route('/history')
def history():
    import functions
    KPI200, t1 = functions.getStockDataVec('KPI200')
    KOSPI, t2 = functions.getStockDataVec('KOSPI')

    mdl = request.args.get('model')
    pi = open('result/{}.pickle'.format(mdl), 'rb')
    history = pickle.load(pi)
    del history['description']
    pi.close()
    pf = {}
    scale = {
        '000660': 100,
        '005380': 1000,
        '005490': 1000,
        '005930': 100,
        '012330': 1000,
        '015760': 100,
        '035420': 100,
        '051910': 1000,
        '055550': 100,
        '105560': 100
    }
    order_queue = {}
    
    for c in cc:
        pf[c] = {}
        order_queue[c] = {'cnt': 0, 'queue': []}
    li = []
    transaction = []
    dates = sorted(history.keys())

    history_sum = []
    for i in range(len(dates)):
        history_sum.append(0)
    
    for i,d in enumerate(dates):  # date
        cur_day = 0
        for c in history[d]: # code
            pf[c]['cnt'] = history[d][c][0]
            pf[c]['cash'] = history[d][c][1]
            pf[c]['pf'] = history[d][c][2]

            history_sum[cur_day] += float(history[d][c][2])

            if int(history[d][c][0]) > order_queue[c]['cnt']:
                transaction.append({
                    'date': d,
                    'code': c,
                    'cnt': int(history[d][c][0]) - order_queue[c]['cnt'],
                    'price': float(history[d][c][3]) * scale[c],
                    'profit': '-'})
                order_queue[c]['queue'].append(float(history[d][c][3]) * scale[c])
            if int(history[d][c][0]) < order_queue[c]['cnt']:
                transaction.append({
                    'date': d,
                    'code': c,
                    'cnt': int(history[d][c][0]) - order_queue[c]['cnt'],
                    'price': float(history[d][c][3]) * scale[c],
                    'profit': (float(history[d][c][3]) * scale[c] - order_queue[c]['queue'].pop(0)) * (order_queue[c]['cnt'] - int(history[d][c][0]))})
            order_queue[c]['cnt'] = int(history[d][c][0])
        
        daily_pf = 0
        for c in pf:
            daily_pf += float(pf[c]['pf'])
        li.append(daily_pf)

        cur_day+=1
    
    # added to compute Sharpe and danger ratio
    diff = []
    for i in range(1,len(history_sum)):
        diff.append(history_sum[i]-history_sum[i-1])
      
    #diff_avg = sum(diff,0)/len(diff)
    diff_avg = numpy.mean(diff)
    diff_std = numpy.std(diff)
    
    R_f = history_sum[len(history_sum)-1]-history_sum[0]

    sharpe = (diff_avg-R_f)/diff_std/math.sqrt(len(history_sum))
    
    today = []
    cash = 0
    for c in pf:
        cash += float(pf[c]['cash'])
        today.append(float(pf[c]['pf']) - float(pf[c]['cash']))
        # today[c] = float(pf[c]['pf']) - float(pf[c]['cash'])
    today.append(cash)
    #today['cash'] = cash
    
    return json.dumps({'li': li, 'KPI200': KPI200, 'KOSPI': KOSPI, 'xlabel': sorted(history.keys()), 'today': today, 'transaction': transaction, 'sharpe': sharpe})
    # f = open('history/{}.csv', )

@app.route('/model_list')
def model_list():
    f = open('result/list.txt', 'r')
    models = f.readlines()
    res = []

    for model in models:
        pi = open('result/{}.pickle'.format(model.strip()), 'rb')
        history = pickle.load(pi)
        desc = history['description']
        del history['description']
        pi.close()

        dates = sorted(history.keys())
        last_pf = 0
        for c in history[dates[-1]]:
            last_pf += float(history[dates[-1]][c][2])
        first_pf = 0
        for c in history[dates[0]]:
            first_pf += float(history[dates[0]][c][2])
        
        import datetime
        ee = datetime.datetime.strptime(dates[-1], '%Y-%m-%d')
        ss = datetime.datetime.strptime(dates[0], '%Y-%m-%d')
        yy = (ee - ss).days / 365
        rate = math.log(last_pf / first_pf) / yy * 10000
        res.append({'name': model, 'rate': round(rate) / 100, 'description': desc})
    f.close()
    res.sort(key=lambda item: item['rate'], reverse=True)
    return render_template('user_model_list.html', model_list=res)
