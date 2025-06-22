# 电商数据智能评分系统 (SJUPF)

## 🎯 项目概述

电商数据智能评分系统是一个专业的商品筛选和评分工具，通过8大评分算法和节日模式感知技术，从海量电商数据中智能筛选出TOP50高价值商品。

## ✨ 核心特性

### 🔥 8大评分算法
- **长尾截断算法** - 99分位截断 + 对数标准化
- **Commission分段评分** - 四段式佣金激励机制
- **余弦衰减算法** - 达人影响力评分
- **指数衰减算法** - 排名位置价值评分
- **增长潜力评分** - 基于增长率的动态评估
- **渠道分布评分** - 多渠道平衡性评估
- **转化率过滤** - 质量门槛过滤机制
- **节日感知算法** - 智能权重调整

### 🎄 节日模式感知
- **自动检测** - 距离下一节日≤45天自动启用
- **权重调整** - sales_7d权重+2%，销量榜基础分+2%
- **内置节日** - 元旦、情人节、妇女节、儿童节、中秋、国庆、圣诞

### 🔧 动态权重调整
- **场景A (完整数据)** - 使用默认权重配置
- **场景B (仅30天)** - 7天权重转移给30天字段
- **场景C (仅7天)** - 30天权重转移给7天字段
- **场景D (无销量GMV)** - 自动跳过并提示

### 📅 智能日期解析
- **日期范围** - "2025-04-27至2025-05-26" → 中点日期
- **单一日期** - "2025-05-15" → 保持不变
- **容错处理** - 无效格式自动使用当前日期

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Linux/Ubuntu系统

### 安装依赖
```bash
# 创建虚拟环境
python3 -m venv douyin_cleaner_env
source douyin_cleaner_env/bin/activate

# 安装依赖包
pip install streamlit pandas numpy openpyxl
```

### 启动方式

#### 方法一：Web界面（推荐）
```bash
# 启动评分系统
./start_scoring.sh

# 访问地址
http://localhost:8510
```

#### 方法二：命令行
```bash
# 基本使用
python score_select.py --in cleaned_dir --out top50_dir

# 功能测试
python test_score_select.py
```

## 📊 使用流程

### 1. 数据准备
确保数据文件包含核心字段：
```
product_name, product_url, category_l1, commission,
conv_30d, rank_type, rank_no, influencer_7d
```

### 2. 销量/GMV数据（至少一组）
- **仅30天数据**：sales_30d, gmv_30d
- **仅7天数据**：sales_7d, gmv_7d
- **完整数据**：包含7天和30天数据

### 3. Web界面使用
1. 上传CSV/XLSX文件
2. 选择是否启用节日加权
3. 点击"开始评分"
4. 查看TOP50结果
5. 下载CSV格式结果

## 🧪 测试验证

### 功能测试
```bash
# 动态权重测试
python test_dynamic_weights.py

# 缺失字段修复测试
python test_missing_fields_fix.py

# 日期解析修复测试
python test_date_parsing_fix.py
```

### 测试数据
- `test_csv/scenario_A_完整数据.csv` - 完整数据场景
- `test_csv/scenario_B_仅30天数据.csv` - 仅30天数据场景
- `test_csv/scenario_C_仅7天数据.csv` - 仅7天数据场景
- `test_csv/missing_live_gmv_7d.csv` - 缺失字段测试
- `test_csv/date_range_format.csv` - 日期范围格式测试

## 📁 项目结构

```
sjupf/
├── score_select.py              # 核心评分算法脚本
├── scoring_app.py               # Streamlit Web应用
├── start_scoring.sh             # 启动脚本
├── field_checker.py             # 字段检查工具
├── data_processor.py            # 数据处理工具
├── test_*.py                    # 测试脚本
├── test_csv/                    # 测试数据
├── README_*.md                  # 详细文档
└── 项目交付总结.md              # 项目总结
```

## 🔧 工具集合

### 数据处理工具
- **field_checker.py** - 字段完整性检查和补全
- **data_processor.py** - 数据格式标准化
- **test_score_select.py** - 基础功能测试

### 修复验证工具
- **test_dynamic_weights.py** - 动态权重功能测试
- **test_missing_fields_fix.py** - 缺失字段修复测试
- **test_date_parsing_fix.py** - 日期解析修复测试

## 💡 业务价值

### 应用场景
- **商品选品** - 从海量商品中筛选高价值商品
- **营销决策** - 基于多维度评分制定营销策略
- **节日备货** - 节日模式自动调整选品权重
- **竞争分析** - 综合评估商品竞争力

### 核心优势
- **科学评分** - 8大算法综合评估
- **智能感知** - 节日模式自动适应
- **高效处理** - 批量文件快速处理
- **结果可靠** - 去重排序确保质量

## 🔄 系统独立性

本评分系统与其他工具完全独立：

1. **抖音电商数据清洗工具** (app.py + start_app.sh) - 端口8507-8509
2. **数据炼金工坊** (start.sh) - 独立运行
3. **电商数据智能评分系统** (scoring_app.py + start_scoring.sh) - 端口8510-8515

## 📞 技术支持

### 获取帮助
```bash
# 查看启动脚本帮助
./start_scoring.sh --help

# 查看详细文档
cat README_score_select.md
```

### 问题反馈
如遇问题请提供：
1. 错误信息截图
2. 输入数据样例
3. 系统环境信息
4. 操作步骤描述

---

**开发团队**: 数据过滤专家  
**技术栈**: Python + Streamlit + pandas + numpy  
**版本**: v1.0.0  
**更新日期**: 2024-12-22
