import numpy as np
import pandas as pd
import pymysql
import matplotlib.pyplot as plt


# 读取CSV文件
df = pd.read_csv('data.csv')

# 删除重复行
df = df.drop_duplicates()

# 增加一个Brand列
df['Brand'] = df['Name'].str.split(' ').str[0]

# 去除nan
df = df.replace({np.nan: None})

# 定义
columns = ['Year', 'Kilometers_Driven', 'Fuel_Type', 'Transmission', 'Mileage', 'Engine', 'Power', 'Seats', 'Price', 'Brand']
def ana_total_data():
    def get_counts(columns):
        counts = {}
        for col in columns:
            col_counts = df[col].value_counts()
            counts[col] = col_counts
        return counts

    counts = get_counts(columns)

    for col, col_counts in counts.items():
        print(f"{col} counts:")
        print(col_counts)
        print()

# 数据写入数据库
def csv_2_mysql():
    conn = pymysql.connect(host='localhost', user='root', password='123456', db='outwork', charset='utf8')

    # 创建游标对象
    cursor = conn.cursor()

    # 遍历DataFrame，将数据写入MySQL
    for row in df.itertuples():
        sql = """
        INSERT INTO usedcar (Name, Location, Year, Kilometers, Fuel_Type, Transmission, Mileage, Engine, Power, Seats, Price,Brand)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (row.Name, row.Location, row.Year, row.Kilometers_Driven, row.Fuel_Type, row.Transmission, row.Mileage, row.Engine, row.Power, row.Seats, row.Price, row.Brand))

    # 提交事务
    conn.commit()

    # 关闭游标和连接
    cursor.close()
    conn.close()


def get_power_bins(bin_count):
    global df
    # 从Power字段中移除 " bhp" 后缀，并将其转换为数值
    df['Power'] = pd.to_numeric(df['Power'].str.replace(' bhp', ''), errors='coerce')

    # 移除Power字段中为NaN的行
    df = df.dropna(subset=['Power'])

    # 使用numpy的linspace函数来生成等间距的bins
    min_power = df['Power'].min()
    max_power = df['Power'].max()
    bins = np.linspace(min_power, max_power, bin_count+1)
    bins = np.round(bins)
    # 利用pd.cut函数，将Power字段划分为多个区间
    df['PowerBin'] = pd.cut(df['Power'], bins)

    # 获取每个区间的数量
    power_bin_counts = df['PowerBin'].value_counts().sort_index()

    # 返回每个区间的数量
    return power_bin_counts
# 指定要划分的区间数量
bin_count = 5

# 获取每个Power区间的数量
power_bin_counts = get_power_bins(bin_count)

# 打印每个区间的数量
print(power_bin_counts)

