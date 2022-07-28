import os
import pandas as pd
from tools.utils import getMap
import json
import re


# 录取专业目录（专业-学院）
class ProfessMap(object):
    def __init__(self, path, sheet_name='data') -> None:
        super().__init__()
        self.map = {}
        self.filter = {}
        self.loadMap(path, sheet_name)

    # 加载专业目录
    def loadMap(self, path, sheet_name='data'):

        data = pd.read_excel(path, sheet_name=sheet_name)
        self.map = getMap(data, 'major', 'academy')

    # 加载过滤器 "MajorMethod.json"
    def loadFilter(self, path):
        with open(path, "r", encoding="utf-8") as f:
            self.filter = json.load(f)

    # 获取需要删除的括号内部字符串
    def parseStr(self, strList, testList):
        return [item for item in testList if item not in strList]

    # 专业过滤器apply
    def majorFilter(self, majorName):

        # 删除数字（tddxx时用）
        # result = re.sub("\d+", '', majorName)
        # 替换字符串
        for key, value in self.filter['filters'].items():
            majorName = majorName.replace(key, value)
        
        # 补充括号，并找到括号内所有的字符串，可能有多个在括号内部的字符串，替换不需要保留的
        if '(' in majorName and majorName[-1] != ')':
            majorName += ')'
        marryList = re.findall("\((.*?)\)", majorName)
        parseList = self.parseStr(self.filter['Reserved'], marryList)
        for item in parseList:
            majorName = majorName.replace(f"({item})", '')
        return majorName

    # 获取学院名称 apply
    def getAcademy(self, majorName):
        majorName = self.majorFilter(majorName)
        if majorName in self.map.keys():
            return self.map[majorName]
        return None
