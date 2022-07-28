import os
import pandas as pd
from tools.utils import getMap
from tools.utils import readDBF
from tools.utils import mergeTable
from CodeMap import CodeMap

# 结果
class Result(object):
    def __init__(self, path) -> None:
        super().__init__()
        self.DataFrame = None
        self.ResultFrame = None
        self.dataSet = None
        self.loadFrame(path)

    def loadFrame(self, FramePath):
        self.dataSet = pd.read_excel(FramePath).drop(index=[0])
    
    # 拼接当前批次和原有批次
    def concat(self, rightData):
        self.dataSet = pd.concat(
            [self.dataSet, rightData], ignore_index=True).drop_duplicates()

    
    def finalfilter(self):
        self.dataSet['GKCJX02'] = self.dataSet[[
            'GKCJX02', 'GKCJX02X']].max(axis=1)
        self.dataSet['GKCJX12'] = self.dataSet[[
            'GKCJX12', 'GKCJX12X']].max(axis=1)

    def sort(self, sorList):
        self.dataSet = self.dataSet.sort_values(by=sorList)

    def export(self, fileName):
        self.dataSet = pd.concat(
            [self.ResultFrame, self.dataSet], ignore_index=True).drop_duplicates()
        self.dataSet.to_excel(fileName)


class TempResult(object):
    def __init__(self, path, province) -> None:
        super().__init__()
        self.province = province
        self.Frame = None
        self.dataSet = None
        self.count = 0
        self.loadFrame(path)

    def loadFrame(self, path):
        self.Frame = pd.read_excel(path)

    # 写整列
    def writeColumns(self, field, value):
        self.dataSet[field] = value

    # 根据列名进行复制
    def copyFromSource(self, field, dataset):
        self.dataSet[field] = dataset

    # 两个表的合并，字段整合
    def merge(self, rightData):
        self.count = rightData.shape[0]
        self.dataSet = pd.merge(self.Frame.T, rightData.T,
                                how='left', left_index=True, right_index=True).T
        self.dataSet['SYD'] = self.province

    # 录取专业处理
    def marjorDeal(self, parseDict):
        self.dataSet['LQZY'] = self.dataSet['LQZY'].apply(
            lambda item: parseDict.majorFilter(item))
        for index in range(0, self.dataSet.shape[0]):
            self.dataSet['XY'].at[index] = parseDict.getAcademy(
                self.dataSet['LQZY'].at[index])

    # 对文科数学和文科综合过滤
    def finalfilter(self):
        self.dataSet['GKCJX02'] = self.dataSet[[
            'GKCJX02', 'GKCJX02X']].max(axis=1)
        self.dataSet['GKCJX12'] = self.dataSet[[
            'GKCJX12', 'GKCJX12X']].max(axis=1)

        self.dataSet = self.dataSet.drop(columns=['GKCJX02X', 'GKCJX12X'])
