## 全国录取子系统数据归一化

#### 一、前言

各高校秋季招生需要在全国的录取子系统实现投档调剂等操作，当所有的省份录取结束之后，需要从这些子系统中提取出自己需要的字段作为自己学校的新生数据库，但是各省份没有把数据格式统一，导致在制作新生数据库时会造成一定的混乱。在制作了多次该数据后，我追溯其中的规律，并优化之前的代码结构，最终得到该工具，作为统一录取系统数据的一个解决方案。

#### 二、结果框架

根据自己学校的要求，本工具整合了50多个字段，具体的数据结构见`DataStructure.csv`，这些字段的数据都来自每个省份录取系统导出的DBF文件中，有些字段可以直接与我们的框架结构对应，但是有些字段需要进行一定的转义才能和我们的框架进行对应，本文档从省份的录取数据开始，对这些字段进行说明。

#### 三、原始数据

当一个省的某一个批次投档结束并确定录取结果时，会导出该省份该批次的录取数据，这些是录取总表数据库制作的数据来源。这些录取数据的形式为多个DBF，即DBF文件夹，这些DBF中包含的是学生的基本信息，以及基本信息中某些字段的字典表。具体数据结构见`新生数据库结构说明`的`一、各省份录取数据说明` 

#### 四、制作方式

当了解了所有原始数据之后，可以可以大概清楚每个省份的数据有哪几部分组成以及需要从哪边寻找总数据库的各个字段。对于数据库结构中的字段，有一部分是可以直接在数据源中查找字段名称获取数据，但还是有部分无法做到一一对应，需要特殊处理，经过对所有字段总结，可以分为以下几个字段。

1.  简单字段

    简单情况是指字段名可以直接从DBF中获取到该字段，从人工手段来讲其实就是可以把DBF中的字段直接复制过来。

2.  特殊情况是指新高考省份和非新高考省份的有些字段的叫法是不一样的，根据2020年和2021的经验，如下几个字段的名称存在多种叫法。处理时可以先判断是否为新高考省份，再去DBF文件中查找对应的字段。

3.  录取专业

    录取专业是学生最重要的信息，它的获取方式与该省是否为新高考省份有一定联系，但是区别不大，录取专业对应的都是T_TDD 中的LQZY字段，其存放的时候该学生被录取的专业代码，但新高考和非新高考在诠释专业代码方面有一定的区别。

4.  成绩项分析

    成绩对于所有省份来说都是一个难题，因为数据源中记录的科目顺序和我们数据库中的科目顺序是完全不一样的，所以需要进行一一映射,因此我们需要知道T_TDD中存放的GKCJX??到底是什么科目。

以上的具体制作方式见`新生数据库结构说明`的`二、数据库结构制作` 

#### 五、如何使用

1.  Install

```
pip install -r requirement.txt
```

2.  Usage

```
usage:python DataUniform.py [-h] [-root ROOT_PATH] [-save SAVE_PATH] [-concat IS_CONCAT] 
                            [-profess PROFESS_DICT] [-code CODE_MAP] [-field FIELD_MAP] 
                            [-sort SORTL_LIST][-frame RESULT_FRAME][-filter MAJOR_FILTER]

optional arguments:
      -h, --help            show this help message and exit
      -root ROOT_PATH, --root_path ROOT_PATH     原始数据路径
      -save SAVE_PATH, --save_path SAVE_PATH     保存路径
      -concat IS_CONCAT, --is_concat IS_CONCAT   
                            是否需要连接
      -frame RESULT_FRAME, --result_frame RESULT_FRAME
                            结果框架，xlsx文件
      -profess PROFESS_DICT, --profess_dict PROFESS_DICT
                            专业目录，xlsx文件
      -code CODE_MAP, --code_map CODE_MAP
                            代码映射规则，csv
      -field FIELD_MAP, --field_map FIELD_MAP  字段映射json
      -filter MAJOR_FILTER, --major_filter MAJOR_FILTER  专业过滤器json
      -sort SORTL_LIST, --sortL_list SORTL_LIST 排序列表
```

#### 五、数据存放

原始数据存放在`root_path`下，每个省份下存放每个批次的DBF文件夹，注意不能文件夹嵌套。

#### 六、配置文件

1.  ResultFrame.xlsx

    最终确定的数据结构，只能有一行，即最后的表格中的标题

2.  ProfessionalDict.xlsx

    专业目录，表中包含两个字段，专业和学院，如下表

    | major    | academy    |
    | -------- | ---------- |
    | 软件工程 | 计算机学院 |

3.  DictSource.csv

    该表格记录了所有需要映射代码的元数据，用于映射代码到名称

    | 字段   | 涵义                                                         |
    | ------ | ------------------------------------------------------------ |
    | origin | 待映射的字段                                                 |
    | target | 映射目标                                                     |
    | isNew  | 是否为新高考（-1为普遍字段，1为新高考特有字段，2为非新高考） |
    | source | 代码表源文件                                                 |
    | key    | 代码所在的列名                                               |
    | value  | 名称所在的列名                                               |
    | static | 是否为静态，每个省份是否需要更新                             |
    | map    | 是否需要映射                                                 |

4.  FieldMap.json

    该配置文件记录需要筛选的字段在dbf中可能出现的字段名称，主要分为通常字段和成绩项字段

5.  MajorFilter.json

    专业过滤器，由于专业名称可能不符合学校规定的专业名称，需要进行过滤和替换，它以两个字典的形式存放在该文件中，如下：

    ```json
    {
    	// 在括号内部需要删除一些内容，此处存放需要保留的字符串
        "Reserved": [
            "xxx"
        ],
        // 存放key-value，把字符串中的key替换为value
        "filters": {
            "（": "(",
            "）": ")"
        }
    }
    ```

    

