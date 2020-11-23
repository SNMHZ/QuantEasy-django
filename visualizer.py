import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def visualize(standard_df, backtest_df_list):
    plt.figure(figsize = (15,8))

    standard_df['total_change'].plot(label='kospi200')

    for backtest_df in backtest_df_list:
        backtest_df['total_change'].plot(label='1month_25')

    plt.plot()
    plt.legend(loc='upper left')
    plt.savefig('savefig_default.png')