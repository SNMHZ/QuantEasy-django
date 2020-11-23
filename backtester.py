import pandas as pd
import numpy as np

def backtest(to_test_url, price_url, cutline=0, toGetSize=25, seed_money=100000000):
  #지갑가치 조회
  def get_stock_wallet_price(stock_wallet, date):
    stock_wallet_value=0
    for stock_name in stock_wallet.keys():
      stock_wallet_value+=stock_wallet[stock_name]*price[stock_name][date]
    return stock_wallet_value

  #저장된 파일 불러오기 -> SQL 쿼리로 바꾸기
  momentum=pd.read_excel(to_test_url, index_col=0)
  momentum=momentum.transpose().dropna()

  price=pd.read_excel(price_url, index_col=0)
  price=price[momentum.index.to_list()]

  #사놓을 거 표만들기
  hold_df=pd.DataFrame()
  for col in momentum.columns.to_list():
    to_add_list=0
    momt=momentum.sort_values(by=col, ascending=False)
    for i, te in enumerate(momt[col]):
      if te<=cutline:
        to_add_list=momt[col].index.to_list()[:i]
        break
    if len(to_add_list)<toGetSize:
      while len(to_add_list)<toGetSize:
        to_add_list.append(np.nan)
    hold_df[col]=to_add_list[:toGetSize]

  #백테스트 데이터프레임 뼈대 생성
  backtest=pd.DataFrame()
  backtest['stock_val']=price[price.columns.to_list()[0]]
  backtest['cash']=price[price.columns.to_list()[0]]
  date_list=backtest.index.to_list()
  for row in date_list:
    backtest.loc[row]=(0,0)
  #backtest

  #######메인 백테스트 코드
  #먼저 필요한 변수들 정의
  date_list=backtest.index.to_list()
  rebalance_dates=hold_df.columns.to_list()
  rebal_date_index=0
  rebal_date_index_next=0
  current_money=seed_money
  screened_stock_count=len(hold_df[price.index.to_list()[0]].dropna().index)
  money_per_stock=seed_money/screened_stock_count
  current_cash=0
  stock_wallet={}
  #메인 for문
  for i, rebalance_date in enumerate(rebalance_dates):
    #리밸런스 때마다 현재 가치 상태 갱신
    if i!=0:
      stock_wallet_before = stock_wallet
      current_money=get_stock_wallet_price(stock_wallet, date_list[rebal_date_index_next])+current_cash
      screened_stock_count=len(hold_df[rebalance_date].dropna().index)
      money_per_stock=current_money/screened_stock_count
    
    #얼마나 들고 있어야 되나? 리밸런싱
    stock_wallet={}
    for to_buy in hold_df[rebalance_date].dropna().to_list():
      stock_wallet[to_buy] = int(money_per_stock//price[to_buy][rebalance_date])
    current_cash=current_money-get_stock_wallet_price(stock_wallet, rebalance_date)
    
    #다음 리밸런싱 구간 세팅
    if i!=len(rebalance_dates)-1:
      while date_list[rebal_date_index_next]!=rebalance_dates[i+1]:
        rebal_date_index_next+=1
    else:
      rebal_date_index_next=len(date_list)
    rebal_date_index_next-=1
    
    #매일 주식 데이터 추가 for문
    for date in date_list[rebal_date_index:rebal_date_index_next+1]:
      stock_wallet_value=get_stock_wallet_price(stock_wallet, date)
      rebal_date_index=rebal_date_index_next+1
      backtest.loc[date]=(stock_wallet_value,current_cash)
    #가치 데이터 for문 종료
  #메인 for문 종료

  #전체 가치 데이터 및 비율 column 추가
  backtest['total']=backtest['stock_val']+backtest['cash']
  backtest['total_change']=backtest['total']/backtest['total'][backtest.index[0]]-1
  return backtest