#coding = utf-8
import pandas as pd
import  numpy as np
from dateutil.relativedelta import relativedelta
import os
import matplotlib.pyplot as plt
import calendar
from math import *

#参数设置
init_asset = 1#初识资产的净值
start_time = '2009-01-01'  # 起始时间，输入格式为YYYY-MM-DD
end_time = '2020-05-31'  # 结束时间，输入格式为YYYY-MM-DD
path = '/Users/maxiaohang/指数数据/'  # 资产数据存放的文件夹路径
path_macro = '/Users/maxiaohang/宏观数据.xlsx'  # 宏观数据的存放路径
path_rate = '/Users/maxiaohang/利率数据.xlsx'  # 利率数据的存放路径

class Timing():
    def __init__(self, asset_data, asset_name, signal_payoff, start_time=start_time, end_time=end_time, init_asset = init_asset):
        #asset_data 资产的净值数据
        #asset_name 基金的名称
        #signal_payoff 用于构造信号的资产的,需要提前计算好
        self.init_asset = init_asset
        self.start_time = start_time
        self.end_time = end_time
        self.asset_data = asset_data
        self.signal_payoff = signal_payoff
        self.asset_name = asset_name
        self.asset_payoff = self.get_asset_payoff(self.asset_data, asset_name=asset_name)

    def get_asset_payoff(self, asset_data, asset_name):
        # 获取资产的日收益率
        asset_data = asset_data[(asset_data[asset_data.columns[1]] != '--')]
        asset_data = asset_data.rename(index=asset_data[asset_data.columns[0]],
                                       columns={asset_data.columns[1]: asset_name})
        asset_data.index = pd.to_datetime(asset_data.index)
        return asset_data[asset_data.columns[1]].pct_change().iloc[1:]

    def moving_average_strategy_signal(self, month, monthly_payoff):
        #按照1年期国债均线择时策略判断当前月份是否选择持有资产
        # monthly_payoff是月收益率，其索引为每月的最后一天
        month = pd.to_datetime(month)
        mean_payoff = monthly_payoff[(monthly_payoff.index > month - relativedelta(months=11)) &
                                     (monthly_payoff.index < month + relativedelta(months=1))].mean()
        month_payoff = monthly_payoff[month]
        return month_payoff < mean_payoff

    def rate_moving_average_strategy(self, init_asset, payoff, signal_payoff):
        #计算1年期国债均线择时策略下资产每日的净值
        #payoff是资产的日收益率，索引是每个交易日
        #返回策略每个交易日的净值
        cumulative_income = init_asset
        net_value = []
        payoff = payoff[(payoff.index >= self.start_time) &
                        (payoff.index <= self.end_time)]
        index = payoff.resample('M').apply(lambda x: x[-1]).index#取每月最后一天
        for month in index:
            if self.moving_average_strategy_signal(month, signal_payoff):
                flag = 1
            else:
                flag = 0
            for day_payoff in payoff[(payoff.index >= str(month)[0:7]) &
                                     (payoff.index <= month)]:
                cumulative_income = cumulative_income * np.power(1 + day_payoff, flag) *\
                                    np.power(1 + (signal_payoff[month]/100.0)*(1/365), 1-flag)
                #当月持有资产择按日资产收益率计算净值；不持有资产则按照当月1年期国债收益率计算当日净值
                net_value.append(cumulative_income)
        return pd.DataFrame({payoff.name: net_value}, index=payoff.index)

    def none_strategy(self, init_asset, payoff):#没有择时策略的净值曲线
        # payoff是资产的日收益率，索引是每个交易日
        cumulative_income = init_asset
        net_value = []
        payoff = payoff[(payoff.index >= start_time) &
                        (payoff.index <= end_time)]
        index = payoff.resample('M').apply(lambda x: x[-1]).index
        for month in index:
            for day_payoff in payoff[(payoff.index >= str(month)[0:7]) &
                                     (payoff.index <= month)]:
                cumulative_income = cumulative_income * (1 + day_payoff)
                net_value.append(cumulative_income)
        return pd.DataFrame({payoff.name: net_value}, index=payoff.index)

    def plot_rate_moving_average_strategy(self):
        #画出1年期国债收益率择时的净值曲线和标的资产的净值曲线
        timing_payoff = self.rate_moving_average_strategy(self.init_asset,self.asset_payoff, self.signal_payoff)
        non_timing_payoff = self.none_strategy(self.init_asset, self.asset_payoff)
        plt.rcParams['font.sans-serif'] = ['SimHei']  ###解决中文乱码
        plt.rcParams['axes.unicode_minus'] = False
        plt.plot(timing_payoff.index, timing_payoff[timing_payoff.columns[0]], 'b',
        non_timing_payoff.index, non_timing_payoff[non_timing_payoff.columns[0]], 'r',
                 self.signal_payoff.index, self.signal_payoff)
        plt.legend(labels=['timing '+self.asset_name, self.asset_name, '1-year-rate payoff'], loc='best')
        plt.show()
