import numpy as np
import pandas as pd
# import pymysql
import matplotlib.pyplot as plt
from pymongo import MongoClient

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

# 根据动力分类
def get_power_bins(bin_count=5):
    global df
    # 从Power字段中移除 " bhp" 后缀，并将其转换为数值
    df['Power'] = pd.to_numeric(df['Power'].str.replace(' bhp', ''), errors='coerce')

    # 移除Power字段中为NaN的行
    df = df.dropna(subset=['Power'])

    # 使用numpy的linspace函数来生成等间距的bins
    min_power = df['Power'].min()
    max_power = df['Power'].max()
    bins = np.linspace(min_power, max_power, bin_count+1)
    # 使用numpy的round函数将bins四舍五入到最近的整数
    bins = np.round(bins)

    # 将bins乘以5然后除以5，确保所有的bins都是5的倍数
    bins = np.round(bins / 5) * 5
    # 利用pd.cut函数，将Power字段划分为多个区间
    df['PowerBin'] = pd.cut(df['Power'], bins)

    # 获取每个区间的数量
    power_bin_counts = df['PowerBin'].value_counts().sort_index()


    # 将区间的数量转换为字典形式
    power_bin_counts_dict = {str(interval): count for interval, count in power_bin_counts.items()}
    # 创建新的figure和axes
    fig, ax = plt.subplots()

    # 获取区间和数量
    bins = power_bin_counts_dict.keys()
    counts = power_bin_counts_dict.values()

    # 创建条形图
    bars = ax.bar(bins, counts)

    # 在每个条形的顶部添加数量标签
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval, int(yval), ha='center', va='bottom', fontsize=8)

    # 设置标题和标签
    ax.set_title('Car Power Distribution')
    ax.set_xlabel('Power Range')
    ax.set_ylabel('Count')

    # 设置x轴标签的字体大小
    plt.xticks(fontsize=8)
    # 保存图形为图片
    plt.savefig('Power', dpi=300, bbox_inches='tight')
    # 显示图形
    plt.show()
    # 返回每个区间的数量
    return power_bin_counts_dict

# 根据年份分类
def get_year_bins():
    global df
    # 从Power字段中移除 " bhp" 后缀，并将其转换为数值
    df['Year'] = pd.to_numeric(df['Year'])

    # 移除Power字段中为NaN的行
    df = df.dropna(subset=['Year'])
    year_counts = df['Year'].value_counts().sort_index()
    # 创建新的figure和axes
    fig, ax = plt.subplots()

    # 获取年份和数量
    years = year_counts.index
    counts = year_counts.values

    # 创建折线图
    ax.plot(years, counts)

    # 设置标题和标签
    ax.set_title('Car Year Distribution')
    ax.set_xlabel('Year')
    ax.set_ylabel('Count')
    # 为每个数据点添加注解
    for i, count in enumerate(counts):
        ax.annotate(count, (years[i], count), textcoords="offset points", xytext=(0, 5), ha='center',fontsize=8)

    # 保存图形为图片
    plt.savefig('Year', dpi=300, bbox_inches='tight')
    # 设置x轴的标签与数据点一一对应
    ax.set_xticks(years)
    ax.set_xticklabels(years, rotation=45)
    # 显示图形
    plt.show()



def csv_2_mongodb():
    # 连接到 MongoDB
    client = MongoClient('mongodb://localhost:27017')

    # 选择数据库和集合
    db = client['outwork']
    collection = db['usedcar']

    # 遍历DataFrame，将数据插入到 MongoDB
    for i, row in enumerate(df.itertuples(), start=1):
        car_data = {
            'id': i,
            'Name': row.Name,
            'Location': row.Location,
            'Year': row.Year,
            'Kilometers': row.Kilometers_Driven,
            'Fuel_Type': row.Fuel_Type,
            'Transmission': row.Transmission,
            'Mileage': row.Mileage,
            'Engine': row.Engine,
            'Power': row.Power,
            'Seats': row.Seats,
            'Price': row.Price,
            'Brand': row.Brand
        }
        collection.insert_one(car_data)

    # 关闭连接
    client.close()

# csv_2_mongodb()


def brand_distribution():
    brand_counts = df['Brand'].value_counts()
    total_count = brand_counts.sum()

    # 获取大于等于1%的品牌
    main_brands = brand_counts[brand_counts / total_count >= 0.01]

    # 计算小于1%的品牌数量之和
    other_count = brand_counts[brand_counts / total_count < 0.01].sum()

    # 将小于1%的品牌归类为 "Other"
    main_brands['Other'] = other_count

    # 获取品牌和数量
    brands = main_brands.index
    counts = main_brands.values

    # 创建饼图
    fig, ax = plt.subplots()
    ax.pie(counts, labels=brands, autopct='%1.1f%%')

    # 设置标题
    ax.set_title('Brand Distribution')
    # 保存图形为图片
    plt.savefig('Brand', dpi=300, bbox_inches='tight')
    # 显示图形
    plt.show()
    brand_dict = {brand: count for brand, count in zip(brands, counts)}
    print(brand_dict)

brand_distribution()