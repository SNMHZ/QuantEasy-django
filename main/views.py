from django.shortcuts import render
from django.http import HttpResponse
import pymysql
import backtester as m_bt

# Create your views here.

def index(request):
    if request.method == 'POST' and request.POST['start'] != '' and request.POST['end'] != '':
        #universe (kospi / kosdaq)
        universe=request.POST['universe']
        print(universe)

        #money (int.)
        money=int(request.POST['money'])
        print(money)

        #start_date 2020-01-01
        start=request.POST['start']
        st=start.split('/')
        start_date="%04d-%02d-%02d"%(int(st[2]), int(st[0]), int(st[1]))
        print(start_date)

        #end_date 
        end=request.POST['end']
        ed=end.split('/')
        end_date="%04d-%02d-%02d"%(int(ed[2]), int(ed[0]), int(ed[1]))
        print(end_date)

        print("**")

        f = open("dbconnect.txt", 'r')
        lines = f.read()
        line=lines.split('\n')
        f.close()
        m_db = pymysql.connect(
            user=line[0], 
            passwd=line[1], 
            host=line[2], 
            db=line[3], 
            charset=line[4]
        )
        m_cursor = m_db.cursor(pymysql.cursors.DictCursor)

        t_list = ['A005930', ]
        value_df=m_bt.quarry_value(t_list, start_date, end_date, m_cursor)
        
        bt_res = m_bt.backtest(value_df, seed_money=money)

        std_df=m_bt.quarry_standard(start_date, end_date, m_cursor)
        std_df['total_change']=std_df['kospi200']/std_df['kospi200'][std_df.index[0]]-1

        m_bt.visualize(std_df, 'kospi200', [bt_res], ['bt_res'])
        cont = { 'tested' : True}

        return render(request, 'main/index.html', cont)

    return render(request, 'main/index.html')