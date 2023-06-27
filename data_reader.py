import numpy as np
import pandas as pd
import pymysql

# 读取CSV文件
df = pd.read_csv('data.csv')

# 增加一个Brand列
df['Brand'] = df['Name'].str.split(' ').str[0]

df = df.replace({np.nan: None})

# 创建数据库连接
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
