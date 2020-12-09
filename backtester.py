import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pymysql

##################데이터 DB에서 가져오기 함수###################
#######input
#stock_list -> 종목 코드 리스트(string)
#start_date -> 쿼리 시작일(당일 포함)
#start_date -> 쿼리 종료일(당일 포함)
#cursor -> pymysql 데이터베이스 커서

#######output
#시계열 주가 정보.
#( col == 종목 코드 ) && ( row == 시계열[start_date:end_date] )

################################################################
def quarry_value(stock_list, start_date, end_date, cursor):
  #stock_list_result 생성. DB관계도 때문에 미리 세팅.
  sql = "SELECT * FROM table_info WHERE"
  for i, stock_code in enumerate(stock_list):
    if i:
      sql+=' or'
    sql+=" Symbol='"+stock_code+"'"
  cursor.execute(sql)
  stock_list_result = pd.DataFrame(cursor.fetchall())

  #관계도 바탕으로 각 주가 쿼리.
  r_df=pd.DataFrame(index=pd.date_range(start_date, end_date), dtype='int64')
  for i in range(len(stock_list_result)):
    print('\rfetching '+stock_list_result.loc[i][0]+' %d/%d'%(i+1, len(stock_list_result)), end='')
    #stock_list_result.loc[i][0] #기업코드 str
    #stock_list_result.loc[i][2] #테이블넘버 int
    #쿼리문 작성
    sql = "SELECT "+stock_list_result.loc[i][0]+" FROM rsp"+str(stock_list_result.loc[i][2])+" WHERE DATE BETWEEN '"+start_date+"' and '"+end_date+"';"
    cursor.execute(sql)
    result = cursor.fetchall()
    r_df[stock_list_result.loc[i][0]]=pd.DataFrame(result, index=pd.date_range(start_date, end_date), dtype='int64')[stock_list_result.loc[i][0]].astype('int64')
  print('\rfetching end.                            ')
  return r_df

##############  기준정보 DB에서 가져오기 함수  #################
#######input
#start_date -> 쿼리 시작일(당일 포함)
#start_date -> 쿼리 종료일(당일 포함)
#cursor -> pymysql 데이터베이스 커서

#######output
#시계열 지수 정보
#( col == kospi, kospi200, kosdaq ) && ( row == 시계열[start_date:end_date] )

################################################################
def quarry_standard(start_date, end_date, cursor):
  #쿼리문 작성
  sql = "SELECT kospi, kospi200, kosdaq FROM standard_table WHERE DATE BETWEEN '"+start_date+"' and '"+end_date+"';"
  cursor.execute(sql)
  result = cursor.fetchall()
  r_df=pd.DataFrame(result, index=pd.date_range(start_date, end_date))
  for col in r_df.columns:
    r_df[col]=r_df[col].astype('float64')
  print('\rfetching end.')
  return r_df

#input  -> 위에서 쿼리한 시계열 주가 정보
#output -> 백테스트 변화율.
def backtest(value_df, seed_money=100000000):
  #지갑가치 조회
  def get_stock_wallet_price(stock_wallet, date):
    stock_wallet_value=0
    for stock_name in stock_wallet.keys():
      stock_wallet_value+=stock_wallet[stock_name]*value_df[stock_name][date]
    return stock_wallet_value

  current_money=seed_money
  screened_stock_count=len(value_df.columns)
  money_per_stock=current_money/screened_stock_count
  rebalance_date=value_df.index[0]

  #사놓을 거 지갑 만들기. (key-value)==(종목코드-구매 개수)
  stock_wallet={}
  for to_buy in value_df.columns:
    stock_wallet[to_buy] = int(money_per_stock//value_df[to_buy][rebalance_date])

  #백테스트 데이터프레임 뼈대 생성
  backtest=pd.DataFrame(index=value_df.index)

  stock_val_list=np.array([], dtype='int64')
  for date in value_df.index:
    stock_val_list = np.append(stock_val_list, get_stock_wallet_price(stock_wallet, date))
  backtest['stock_val']=stock_val_list
  cash=seed_money-get_stock_wallet_price(stock_wallet, rebalance_date)
  backtest['cash']=np.array([cash]*len(value_df), dtype='int64')
  backtest['total']=backtest['stock_val']+backtest['cash']
  backtest['total_change']=backtest['total']/backtest['total'][backtest.index[0]]-1

  return backtest

def visualize(standard_df, std_str, backtest_df_list=[], label_list=[]):
  plt.figure(figsize = (15,8))
  standard_df['total_change'].plot(linestyle='--', label=std_str)
  for i, m_df in enumerate(backtest_df_list):
    label_str=''
    if len(label_list)<=i:
      label_str=str(i)
    else:
      label_str=label_list[i]
    m_df['total_change'].plot(label=label_str)
  plt.plot()
  plt.legend(loc='upper left')
  plt.savefig('static/bt_img/savefig_default.png')
  #plt.show()