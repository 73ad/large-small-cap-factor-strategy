# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")
from copy import deepcopy
import matplotlib.pyplot as plt
plt.rcParams['font.serif'] = ['KaiTi']     #用来正常显示中文
plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号
import seaborn as sns
sns.set_style({"font.sans-serif":['KaiTi', 'Arial']},{"axes.unicode_minus":False})

#%% 交易矩阵参数设定
read_path = "/Users/ilio/Desktop/Data/"

# 收盘价
close = pd.read_excel(read_path + 'close.xlsx')
# 流通市值
mkt_cap_float = pd.read_excel(read_path + "mkt_cap_float.xlsx")
# 交易信息
ipo_listdays = pd.read_excel(read_path + 'ipo_listdays.xlsx')
trade_status = pd.read_excel(read_path + 'trade_status.xlsx')
un_st_flag = pd.read_excel(read_path + 'un_st_flag.xlsx')
# 申万一级行业分类
industry_sw = pd.read_excel(read_path + "industry_sw.xlsx")
industry_d1 = industry_sw
sec_name = pd.read_excel(read_path + "sec_name.xlsx")
# 时间和股票标签
timelist = list(close.columns)
stocklist = list(close.index)

def layer_selection(indicator,dnbound,upbound):
    flag = pd.DataFrame(index = indicator.index,columns = indicator.columns)
    temp = deepcopy(indicator)
    quantiles = temp[temp.notnull()].quantile([dnbound,upbound])
    # 将因子值位于dnbound,upbound分位数之间的flag设置为1
    flag[(temp >= quantiles.loc[dnbound,:]) & (temp <= quantiles.loc[upbound,:])] = 1
    return flag

def ma(indicator,period): #移动平均
    stocklist = indicator.index
    timelist = indicator.columns
    ma_x = pd.DataFrame(index = stocklist, columns = timelist)
    ma_0 = deepcopy(indicator)
    for t in range(period,len(timelist)):
        temp = indicator.iloc[:,t-period:t]
        ma_temp = temp.mean(axis = 1)
        ma_x.ix[:,t] = ma_temp
    return ma_x

def Calcuate_performance_indicators(dataframe,period): #策略回测函数涉及实习内容不方便透露
    #
    #
    #
    return 0

def cumr(indicator):
    cum = deepcopy(indicator.shift(1)+1)
    cum.ix[0] = 1
    for t in range(1,len(cum.index)):
        cum.ix[t] *= cum.ix[t-1]
    return cum

#市值筛选
cap_small = layer_selection(mkt_cap_float,0,0.1)
cap_large = layer_selection(mkt_cap_float,0.9,1)

close_growth = close.shift(-1,axis = 1)/close -1
cg_small = cap_small * close_growth
cg_large = cap_large * close_growth

#大小盘股平均收益率
clm = pd.DataFrame(cg_large.mean())
csm = pd.DataFrame(cg_small.mean())

wind_A_close = pd.read_excel(read_path + 'wind_A_close.xlsx')
wac_growth = wind_A_close.shift(-1,axis = 1) / wind_A_close -1
temp = pd.concat([clm,csm,wind_A_close.T,wac_growth.T],axis = 1)

#======相关强度
cum_l = cumr(clm)
cum_s = cumr(csm)
sindex_ = (np.log(cum_s)-np.log(cum_l)).T
sma_ = ma(sindex_,5)

#风格轮转判断
trendflag = deepcopy(sma_)
trendflag.ix[:] = np.nan
trendflag.ix[0,4] = 2
for t in range(5,len(sma_.columns)):
    if (sma_.ix[0,t] > sindex_.ix[0,t]):
        if sma_.ix[0,t] < sindex_.ix[0,t-1]:
            trendflag.ix[0,t] = 2
        else:
            trendflag.ix[0,t] = trendflag.ix[0,t-1]
if (sma_.ix[0,t] < sindex_.ix[0,t]):
    if sma_.ix[0,t] > sindex_.ix[0,t-1]:
        trendflag.ix[0,t] = 1
        else:
            trendflag.ix[0,t] = trendflag.ix[0,t-1]
temp1 = trendflag.iloc[0,4:162]
temp1[temp1==2]=0
temp2 = trendflag.iloc[0,4:162]
temp2 -=1
small = csm.T.iloc[0,4:162]
large = clm.T.iloc[0,4:162]

g= pd.DataFrame(small * temp1 + large *temp2).T

Calcuate_performance_indicators(g,12)
