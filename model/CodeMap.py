import os
import pandas as pd
import json
from tools.utils import getMap
from tools.utils import readDBF

# 代码解析映射表


class CodeMap(object):

    def __init__(self, sourcePath, fieldMapPath) -> None:
        super().__init__()
        self.MapList = {}
        self.curMaps = {}
        self.ScoreFieldMap = {}
        self.CommonFieldMap = {}

        self.loadStruct(sourcePath)
        self.loadFieldMap(fieldMapPath)

    # 存储每一个map的元信息和内容
    class MapSource(object):
        def __init__(self) -> None:
            self.origin = None      # 原字段名称
            self.target = None      # 映射目标字段名称
            self.isNew = None       # 是否是新高考
            self.source = None      # 数据源 .dbf
            self.key = None         # 代码所在字段
            self.value = None       # 名称所在字段
            self.static = None      # 是否是静态的
            self.mappable = None    # 是否可以映射（针对成绩项）

            self.map = {}      # 字段映射

        # 清除原来的字典 用于之后的更新
        def flush(self):
            if not self.static:
                self.map = {}

        # 加载字典映射
        def loadMap(self, workDir):
            sourcePath = os.path.join(workDir, self.source)
            data = readDBF(sourcePath)
            # 去除空格等杂项字符
            data[self.key] = data[self.key].apply(lambda x: x.strip())
            data[self.value] = data[self.value].apply(lambda x: x.strip())
            # 映射转换
            if not self.static:
                self.map = getMap(data, self.key, self.value)
            else:
                self.map.update(getMap(data, self.key, self.value))

        # 获取键值
        def get(self, key):
            if key not in self.map.keys():
                return None

            return self.map[key]

    def loadStruct(self, sourcePath):
        # 读取字典源
        mapSourceList = pd.read_csv(sourcePath, sep=",")

        for _, row in mapSourceList.iterrows():
            # 构造每个字典的元信息
            mapSource = self.MapSource()
            mapSource.origin = row['origin']
            mapSource.target = row['target']
            mapSource.isNew = row['isNew']
            mapSource.source = row['source']
            mapSource.key = row['key']
            mapSource.value = row['value']
            mapSource.mappable = row['map']
            mapSource.static = row['static']
            
            # 字典表重复项处理
            key = row['origin']
            if key in self.MapList:
                key += '_copy'
            self.MapList.update({key: mapSource})

    # 加载每个成绩项可能出现的名称
    def loadFieldMap(self, path):
        FieldMap = {}
        with open(path, 'r', encoding="utf-8") as f:
            FieldMap = json.load(f)
        # 设置成绩项和通常字段的映射表
        self.CommonFieldMap = FieldMap['CommonFiled']
        self.ScoreFieldMap = FieldMap['CJXDIC']

    # 加载当前省份的字典源数据
    def loadMapList(self, workDir, isNew):
        # 判别是否是新高考
        self.curMaps = {filed: map for filed, map in self.MapList.items()
                        if map.isNew == -1 or map.isNew == isNew}

        for map in self.curMaps.values():
            map.loadMap(workDir)

    # 刷写所有映射表，并回到MapList（针对地区代码的静态刷写）
    def flush(self):
        for _, value in self.curMaps.item():
            value.flush()

        self.MapList.update(self.curMaps)
