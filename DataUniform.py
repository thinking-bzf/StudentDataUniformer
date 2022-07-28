import os
import pandas as pd
from model.CodeMap import CodeMap
from model.StudentData import StudentData
from model.ProfessMap import ProfessMap

import argparse
from tqdm import tqdm


# 数据结构
# 	学生数据表
# 	数据框架表
# 	字段可能出现字段
# 	字段字典表（所 在位置，名称列，代码列，字段名称）（class）

# 1. 加载字典表
# 2. 加载学生数据
# 3. 框架套用
# 4. 代码处理
# 5. 特殊字段修改

"""
    第一版已经解决问题：
        1. 基本字段进行匹配
        2. 专业名称过滤和学院对应
        3. 对批次和科类的名称进行对应
    
    缺点：
        1. 对于字典表无法实现动态添加，写死了
        2. 用户无法比较方便的调用
        3. 代码结构比较混乱

    解决方案：
        1. 建立一个字典表的类，并根据外部表格决定是否需要解析名称
        2. 添加参数机制
        3. 尝试重构代码结构

"""

# 解析参数
def parameter_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-root", "--root_path", type=str, 
                        default="./test")
    parser.add_argument("-save", "--save_path", type=str,
                        default="./test/result")
    parser.add_argument("-concat", "--is_concat", type=int,
                        default=0, help='Whether to concat')
    parser.add_argument("-frame", "--result_frame", type=str,
                        default='./configs/ResultFrame.xlsx', help='excel is needed')
    parser.add_argument("-profess", "--profess_dict", type=str,
                        default='./configs/ProfessionalDict.xlsx', help='excel is needed')
    parser.add_argument("-code", "--code_map", type=str,
                        default="./configs/DictSource.csv", help='csv is needed')
    parser.add_argument("-field", "--field_map", type=str,
                        default="./configs/FieldMap.json")
    parser.add_argument("-filter", "--major_filter", type=str,
                        default="./configs/MajorFilter.json")
    parser.add_argument("-sort", "--sortL_list", type=list,
                        default=['SYD', 'PCMC', 'KLMC', 'XY', 'LQZY'])

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parameter_args()
    print(args)
    # 根目录(内部含省份文件夹)
    root = args.root_path
    # 代码映射表
    codeMap = CodeMap(args.code_map, args.field_map)
    # 专业映射表
    professMap = ProfessMap(args.profess_dict)
    professMap.loadFilter(args.major_filter)
    # 结果框架
    resultFramePath = args.result_frame
    # 获取省份列表
    provinceList = os.listdir(root)
    # 获取保存路径
    savePath = args.save_path

    if not os.path.exists(savePath):
        os.makedirs(savePath)
    
    # 排序关键字列表
    sortList = ['SYD', 'PCMC', 'KLMC', 'XY', 'LQZY']
    
    # 处理每个省份
    for province in tqdm(provinceList):
        provinceDir = os.path.join(root, province)
        result = None
        # print(f"{province} 开始")
        itemList = os.listdir(provinceDir)
        for item in itemList:
            # 判断是否为文件夹
            workDir = os.path.join(provinceDir, item)
            if not os.path.isdir(workDir):
                continue

            # 加载学生数据
            studentData = StudentData(workDir, codeMap, province)
            # 加载结果框架
            studentData.LoadResultFrame(resultFramePath)
            studentData.ConcatData()        # 数据连接到框架中
            studentData.CodeMapping()       # 代码映射
            studentData.AcademyMapping(professMap)    # 学院映射
            studentData.Sort(sortList)              # 数据排序
            # 导出结果表
            if result is None:
                result = studentData.dataSet
            else:
                result = pd.concat([result, studentData.dataSet])
            # print(f"{item} 完成")
        # 导出结果
        if not result is None:
            result.to_excel(os.path.join(savePath, f"{province}.xlsx"))
