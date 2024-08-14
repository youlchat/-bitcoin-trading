"""
邢不行 - b圈量化交易训练营
day3 - 中性策略
作者：邢不行
微信：xbx1717
"""
import matplotlib.pyplot as plt
import pandas as pd
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
pd.set_option('display.max_rows', 5000)  # 最多显示数据的行数

# 回测时间
start_date = '2021-01-01'
end_date = '2023-04-16'

# 回测参数
select_coin_num = 1  # 单边选币数量
leverage = 1  # 杠杆比例
period = '24H'  # 周期
c_rate = 2.5 / 10000  # 手续费

# 因子 False：从大到小排序，做多大的，做空小的。True：从小到大排序，做多小的，做空大的。
factor_class_dict = {'Bias_6': False,'Cci_48': True, 'Cmo_36': False,'Rsi_13': True }

# 导入数据
df = pd.read_csv(f'./all_coin_factor_data_{period}.csv', encoding='gbk', parse_dates=['time'])
df = df[['time', 'symbol', '下周期币种涨跌幅'] + list(factor_class_dict.keys())]

# 筛选日期范围
df = df[df['time'] >= pd.to_datetime(start_date)]
df = df[df['time'] <= pd.to_datetime(end_date)]


# 计算每个因子的排名
factor_rank_cols = []
for f in list(factor_class_dict.keys()):
    df[f'{f}_rank'] = df.groupby('time')[f].rank(method='first', ascending=factor_class_dict[f])

# 计算综合排名
df['因子'] = df[[i+'_rank'  for i in list(factor_class_dict.keys())]].sum(axis=1, skipna=False)

# 根据因子对比进行排名
# 从小到大排序 - 做多
df['排名1'] = df.groupby('time')['因子'].rank(method='first')
df1 = df[(df['排名1'] <= select_coin_num)]
df1['方向'] = 1
 
# 从大到小排序 - 做空
df['排名2'] = df.groupby('time')['因子'].rank(method='first', ascending=False)
df2 = df[(df['排名2'] <= select_coin_num)]
df2['方向'] = -1

# 合并排序结果
df = pd.concat([df1, df2], ignore_index=True)
df['选币'] = df['symbol'] + '(' + df['方向'].astype(str) + ')' + ' '
df = df[['time', 'symbol', '方向', '选币', '下周期币种涨跌幅']]
df.sort_values(by=['time', '方向'], ascending=[True, False], inplace=True)
df.reset_index(drop=True, inplace=True)

# 计算下周期收益 
df['下周期交易涨跌幅'] = df['下周期币种涨跌幅'] * df['方向'] * leverage / 2 - leverage / 2 * c_rate - leverage / 2 * c_rate * (1+df['下周期币种涨跌幅']) # 杠杆，多空，并且扣除手续费
select_coin = pd.DataFrame()
select_coin['当周期选币'] = df.groupby('time')['选币'].sum()
select_coin['下周期策略涨跌幅'] = df.groupby('time')['下周期交易涨跌幅'].sum() / (select_coin_num * 2)
select_coin['净值'] = (select_coin['下周期策略涨跌幅'] + 1).cumprod()
print(select_coin)

# 画图
select_coin.reset_index(inplace=True)
plt.plot(select_coin['time'], select_coin['净值'])
plt.show()
