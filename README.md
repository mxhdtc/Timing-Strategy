# Timing-Strategy
## 写在前面

今天是作为金融小黑工的第五天，主要的工作是复现申万宏源的研报《重塑资产配置“时钟”：经济预期与宏观流动性——数说资产配置研究系列之二》中的择时策略，
写了一个Timing类用以实现基于1年期国债收益率12月均线择时策略。
主要策略是：当1年期国债收益率低于 12 个月均线时次月持有标的资产。
把code放在这里，可以参考复用。

## Timing类介绍：

属性：Timing类目前包含7个属性，下面是各个属性的含义

        self.init_asset：期初资产的净值，默认为1.
        
        self.start_time：回测开始的时间
        
        self.end_time ：回测结束的时间
        
        self.asset_data ：资产的日净值数据
        
        self.signal_payoff ：构建信号的资产月收益率，需要提前计算好，索引为每月最后一天。
        
        self.asset_name：资产的名称，方便画图
        
        self.asset_payoff：资产每日的收益率，不需要传入，Timing类在构造的时候会利用get_asset_payoff（）函数计算好asset_payoff。
        

##### get_asset_payoff(self, asset_data, asset_name):成员函数，传入资产每日净值，计算每日收益率，

##### moving_average_strategy_signal(self, month, monthly_payoff):成员函数，给定月份，计算在12月收益率均线策略下是否在当月持有资产。

##### rate_moving_average_strategy(self, init_asset, payoff, signal_payoff):成员函数，计算12月收益率均线策略下资产的净值曲线，对于持有月份，每日的净值用前一日净值乘当日资产收益率；不持有的月份，用当月1年期国债收益率均值计算日收益。

##### none_strategy(self, init_asset, payoff):没有择时策略的净值曲线

##### plot_rate_moving_average_strategy(self):画出择时策略的净值曲线、不择时的净值曲线和给出择时信号的资产的月收益率。
