# 数据处理专业知识体系

## 核心技术栈掌握

### pandas数据处理精通
```python
# 高效数据读取
df = pd.read_excel(file, engine='openpyxl', dtype=str)  # 避免数据类型推断错误

# 列重命名最佳实践
column_mapping = {'商品': 'product_name', '商品链接': 'product_url'}
df = df.rename(columns=column_mapping)

# 数据类型转换
df['commission'] = pd.to_numeric(df['commission'], errors='coerce')

# 缺失值处理
df['product_name'] = df['product_name'].fillna('未知商品')

# 数据验证
assert not df['product_name'].isna().all(), "产品名称列全部为空"
```

### Excel文件处理专业技能
```python
# 多sheet处理
def read_excel_sheets(file_path):
    """读取Excel文件的所有sheet"""
    with pd.ExcelFile(file_path) as xls:
        sheets = {}
        for sheet_name in xls.sheet_names:
            sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
    return sheets

# 大文件分块读取
def read_large_excel(file_path, chunk_size=1000):
    """分块读取大型Excel文件"""
    df = pd.read_excel(file_path)
    for chunk in [df[i:i+chunk_size] for i in range(0, len(df), chunk_size)]:
        yield chunk
```

### 数据清洗核心算法
```python
def clean_numeric_field(series, field_name):
    """
    清洗数值字段的通用方法
    处理：百分比、区间值、单位转换等
    """
    # 移除空白字符
    series = series.astype(str).str.strip()
    
    # 处理百分比
    percentage_mask = series.str.contains('%', na=False)
    series.loc[percentage_mask] = series.loc[percentage_mask].str.replace('%', '').astype(float) / 100
    
    # 处理区间值（如：7.5w-10w）
    range_mask = series.str.contains('-', na=False)
    # 取区间中位数
    
    return series

def extract_from_filename(filename):
    """从文件名提取业务信息"""
    import re
    
    # 提取时间范围
    date_pattern = r'(\d{8})-(\d{8})'
    date_match = re.search(date_pattern, filename)
    
    # 提取榜单类型
    rank_types = ['销量榜', '热推榜', '潜力榜', '持续好货榜', '同期榜']
    rank_type = next((rt for rt in rank_types if rt in filename), '未知榜单')
    
    return {
        'snapshot_tag': date_match.group() if date_match else '未知时间',
        'rank_type': rank_type,
        'source_table': filename.split('-')[0] if '-' in filename else filename
    }
```

## 电商数据业务理解

### 抖音电商数据特征
- **多时间维度**：7天、30天、1年等不同统计周期
- **多渠道数据**：直播、商品卡、短视频等不同来源
- **动态排名**：实时变化的榜单排名数据
- **复合指标**：GMV、转化率、带货达人等复合业务指标

### 标准字段定义
```python
STANDARD_FIELDS = {
    'product_name': '商品名称',
    'product_url': '商品链接',
    'category_l1': '一级分类',
    'commission': '佣金比例',
    'sales_7d': '7天销量',
    'gmv_7d': '7天GMV',
    'sales_30d': '30天销量',
    'gmv_30d': '30天GMV',
    'live_gmv_30d': '30天直播GMV',
    'card_gmv_30d': '30天商品卡GMV',
    'sales_1y': '1年销量',
    'conv_30d': '30天转化率',
    'rank_type': '榜单类型',
    'rank_no': '排名',
    'influencer_7d': '7天带货达人',
    'snapshot_tag': '数据快照标签',
    'source_table': '数据来源表'
}
```

### 数据质量检查规则
```python
def validate_ecommerce_data(df):
    """电商数据质量检查"""
    issues = []
    
    # 检查必填字段
    required_fields = ['product_name', 'product_url']
    for field in required_fields:
        if field in df.columns and df[field].isna().sum() > len(df) * 0.5:
            issues.append(f"{field}字段缺失率超过50%")
    
    # 检查数值字段合理性
    numeric_fields = ['commission', 'sales_7d', 'gmv_7d']
    for field in numeric_fields:
        if field in df.columns:
            if (df[field] < 0).any():
                issues.append(f"{field}存在负值")
    
    # 检查佣金比例范围
    if 'commission' in df.columns:
        if (df['commission'] > 1).any():
            issues.append("佣金比例存在大于100%的异常值")
    
    return issues
```

## 文件处理最佳实践

### 内存优化策略
```python
def optimize_dataframe_memory(df):
    """优化DataFrame内存使用"""
    # 转换数值类型
    for col in df.select_dtypes(include=['int64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='integer')
    
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='float')
    
    # 转换字符串类型
    for col in df.select_dtypes(include=['object']).columns:
        if df[col].nunique() / len(df) < 0.5:  # 重复值较多
            df[col] = df[col].astype('category')
    
    return df
```

### 错误处理模式
```python
def safe_process_file(file_path, processor_func):
    """安全的文件处理包装器"""
    try:
        result = processor_func(file_path)
        return {'success': True, 'data': result, 'error': None}
    except pd.errors.EmptyDataError:
        return {'success': False, 'data': None, 'error': '文件为空'}
    except pd.errors.ExcelFileError:
        return {'success': False, 'data': None, 'error': 'Excel文件格式错误'}
    except MemoryError:
        return {'success': False, 'data': None, 'error': '文件过大，内存不足'}
    except Exception as e:
        return {'success': False, 'data': None, 'error': f'未知错误：{str(e)}'}
```

## 性能优化技术

### 并行处理策略
```python
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

def parallel_process_files(files, process_func, max_workers=None):
    """并行处理多个文件"""
    if max_workers is None:
        max_workers = min(len(files), multiprocessing.cpu_count())
    
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(process_func, file): file for file in files}
        
        for future in concurrent.futures.as_completed(future_to_file):
            file = future_to_file[future]
            try:
                result = future.result()
                results.append({'file': file, 'result': result})
            except Exception as e:
                results.append({'file': file, 'error': str(e)})
    
    return results
```

### 缓存机制应用
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=128)
def cached_file_processor(file_hash, processing_params):
    """基于文件哈希的缓存处理"""
    # 实际的文件处理逻辑
    pass

def get_file_hash(file_content):
    """计算文件内容哈希"""
    return hashlib.md5(file_content).hexdigest()
```

## 数据输出标准

### 统一输出格式
```python
def standardize_output(df):
    """标准化输出格式"""
    # 确保所有标准字段都存在
    for field in STANDARD_FIELDS.keys():
        if field not in df.columns:
            df[field] = None
    
    # 按标准顺序排列列
    df = df[list(STANDARD_FIELDS.keys())]
    
    # 数据类型标准化
    numeric_fields = ['commission', 'sales_7d', 'gmv_7d', 'sales_30d', 'gmv_30d']
    for field in numeric_fields:
        df[field] = pd.to_numeric(df[field], errors='coerce')
    
    return df
```

### 质量报告生成
```python
def generate_quality_report(original_df, processed_df):
    """生成数据质量报告"""
    report = {
        'original_rows': len(original_df),
        'processed_rows': len(processed_df),
        'data_loss_rate': (len(original_df) - len(processed_df)) / len(original_df),
        'field_mapping': {},
        'quality_issues': []
    }
    
    # 字段映射统计
    for std_field in STANDARD_FIELDS.keys():
        if std_field in processed_df.columns:
            non_null_count = processed_df[std_field].notna().sum()
            report['field_mapping'][std_field] = {
                'coverage': non_null_count / len(processed_df),
                'non_null_count': non_null_count
            }
    
    return report
```
