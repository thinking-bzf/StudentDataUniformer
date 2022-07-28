from dbfread import DBF
import pandas as pd
import numpy as np
import json
import re

# 将pandas转换为字典映射表
def getMap(data, key, value):
    return data.set_index(key)[value].to_dict()

# 读取DBF文件 -> dataFrame
def readDBF(path):
    dbf_file = DBF(path, encoding="GBK", char_decode_errors='ignore')
    return pd.DataFrame(iter(dbf_file))


# 横向拼接两张表
# 传入key为单个字符字符串
def mergeTable(leftDF, rIghtDF, key, how='inner'):
    # 保证保留的没有重名
    col_to_use = list(set(rIghtDF.columns)-set(leftDF.columns))

    # 支持单列和多列作为主键
    if isinstance(key, str):
        col_to_use.append(key)
    elif isinstance(key, list):
        col_to_use += key

    return pd.merge(leftDF, rIghtDF[col_to_use], on=key, how=how)
