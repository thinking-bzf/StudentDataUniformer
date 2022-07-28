import os
import pandas as pd
from tools.utils import getMap
from tools.utils import readDBF
from tools.utils import mergeTable
from .CodeMap import CodeMap

# 学生信息(一个省份加载一次)


class StudentData(object):
    def __init__(self, workDir, codeMap, province):
        self.dataSet = None     # 数据集
        self.isNew = 0          # 是否是新高考
        self.codeMap = codeMap  # 当前省份+全局代码映射表
        self.workDir = workDir  # 当前工作目录
        self.FieldMap = {}      # 字段映射表
        self.resultFrame = None  # 结果框架
        self.loadData()
        self.province = province

    # 加载数据并映射

    def loadData(self):
        self.loadStudentData()
        self.FiledMapping()

    # 记载学生数据
    def loadStudentData(self):
        DataList = os.listdir(self.workDir)

        if 'T_TDD.dbf' not in DataList:
            self.dataSet = pd.DataFrame()

        sourceData = readDBF(os.path.join(self.workDir, 'T_TDD.dbf'))

        # 如果存在BMK，则是新高考
        if "T_BMK.dbf" in DataList:
            self.isNew = 1
            # 导入BMK
            BMK = readDBF(os.path.join(self.workDir, 'T_BMK.dbf'))
            # 合并TDD和BMK
            sourceData = mergeTable(sourceData, BMK, 'KSH')

        self.dataSet = sourceData
        

    # 加载代码库和字段解析
    def FiledMapping(self):
        # 加载当前省份的代码库
        self.codeMap.loadMapList(self.workDir, self.isNew)

        # 成绩项解析
        scoreFieldMap = self.codeMap.ScoreFieldMap
        # index: GKCJX01  probList: []
        for index, probList in scoreFieldMap.items():
            parseResult = self.parseScoreField(probList)
            if len(parseResult) != 0:
                # 实际编号: 最终编号
                self.FieldMap.update({f'GKCJX{parseResult[0]}': index})

        # 通用字段解析
        commonFieldMap = self.codeMap.CommonFieldMap
        for field, probList in commonFieldMap.items():
            probNameList = [
                probName for probName in probList if probName in self.dataSet.columns]
            # 实际字段名: 最终字段名
            if len(probNameList) != 0:
                self.FieldMap.update({probNameList[0]: field})
        # 字段映射
        self.dataSet = self.dataSet[self.FieldMap.keys()].rename(
            columns=self.FieldMap)

    # 解析成绩项
    def parseScoreField(self, proList):
        # 获取成绩项映射表
        scoreMap = self.codeMap.curMaps['CJX']
        # 寻找匹配的成绩项名称
        for item in proList:
            return [key for key, value in scoreMap.map.items() if item == value]

    # 代码名称映射
    def CodeMapping(self):
        # 获取当前需要映射的代码库
        curMaps = {key: mapSource for key, mapSource in self.codeMap.curMaps.items()
                   if mapSource.mappable == 1}
        for _, mapSource in curMaps.items():
            self.dataSet[mapSource.origin] = self.dataSet[mapSource.origin].fillna(value='')
            self.dataSet[mapSource.target] = self.dataSet[mapSource.origin].apply(
                lambda code: mapSource.map[code] if code in mapSource.map.keys() else '')

    # 专业规范化 -> 学院映射
    def AcademyMapping(self, professMap):
        # 专业归一化
        self.dataSet['LQZY'] = self.dataSet['LQZY'].apply(lambda major: professMap.majorFilter(major))
        self.dataSet['XY'] = self.dataSet['LQZY'].apply(lambda major: professMap.getAcademy(major))
    
    # 加载结果框架
    def LoadResultFrame(self, path):
        self.resultFrame = pd.read_excel(path)

    # 经过过滤器之后，拼接数据和框架
    def ConcatData(self):
        self.FieldFilter()
        self.dataSet = pd.concat([self.resultFrame, self.dataSet])
        self.dataSet['SYD'] = self.province
    
    # 最终过滤器
    def FieldFilter(self):
        if 'GKCJX02X' in self.dataSet.columns:
            self.dataSet['GKCJX02'] = self.dataSet[['GKCJX02', 'GKCJX02X']].max(axis=1)
        if 'GKCJX12X' in self.dataSet.columns:
            self.dataSet['GKCJX12'] = self.dataSet[['GKCJX12', 'GKCJX12X']].max(axis=1)
    
    # 数据排序
    def Sort(self, sorList):
        self.dataSet = self.dataSet.sort_values(by=sorList)

    # 导出结果
    def Export(self, fileName):
        self.dataSet.to_excel(fileName)

