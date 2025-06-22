# 电商数据专业知识

## 抖音电商数据生态理解

### 数据来源分类
```python
DATA_SOURCES = {
    '商品库': {
        'description': '平台商品基础信息库',
        'key_fields': ['product_name', 'product_url', 'category_l1', 'commission'],
        'update_frequency': '实时',
        'data_quality': '高'
    },
    '销量榜': {
        'description': '基于销量排名的榜单数据',
        'key_fields': ['sales_7d', 'sales_30d', 'rank_no'],
        'update_frequency': '每日',
        'data_quality': '中'
    },
    '热推榜': {
        'description': '平台推荐热度排名',
        'key_fields': ['gmv_7d', 'conv_30d', 'influencer_7d'],
        'update_frequency': '每小时',
        'data_quality': '中'
    },
    '潜力榜': {
        'description': '增长潜力商品排名',
        'key_fields': ['sales_30d', 'gmv_30d', 'conv_30d'],
        'update_frequency': '每日',
        'data_quality': '低'
    },
    '持续好货榜': {
        'description': '长期表现优秀商品',
        'key_fields': ['sales_1y', 'gmv_30d', 'live_gmv_30d'],
        'update_frequency': '每周',
        'data_quality': '高'
    },
    '同期榜': {
        'description': '同期对比数据',
        'key_fields': ['sales_30d', 'gmv_30d', 'card_gmv_30d'],
        'update_frequency': '每月',
        'data_quality': '中'
    }
}
```

### 业务指标深度理解
```python
BUSINESS_METRICS = {
    'GMV': {
        'full_name': 'Gross Merchandise Volume',
        'chinese_name': '商品交易总额',
        'calculation': '销量 × 平均客单价',
        'business_meaning': '衡量商品销售规模的核心指标',
        'data_types': ['gmv_7d', 'gmv_30d', 'live_gmv_30d', 'card_gmv_30d']
    },
    'conversion_rate': {
        'full_name': 'Conversion Rate',
        'chinese_name': '转化率',
        'calculation': '购买人数 / 访问人数',
        'business_meaning': '衡量商品吸引力和购买意愿的关键指标',
        'normal_range': '0.01-0.15'
    },
    'commission': {
        'full_name': 'Commission Rate',
        'chinese_name': '佣金比例',
        'calculation': '佣金金额 / 商品价格',
        'business_meaning': '达人推广获得的收益比例',
        'normal_range': '0.05-0.30'
    }
}
```

## 数据质量问题模式

### 常见数据异常类型
```python
DATA_ANOMALY_PATTERNS = {
    '数值格式异常': {
        'examples': ['7.5w-10w', '20%', '1.2万', '无数据'],
        'processing_strategy': 'numeric_normalizer函数处理',
        'fallback_value': 0
    },
    '字段名称不统一': {
        'examples': ['商品', '商品名称', '产品名', '商品标题'],
        'processing_strategy': '字段映射表匹配',
        'fallback_value': '使用最相似的字段名'
    },
    '缺失值模式': {
        'examples': ['', 'null', 'N/A', '无', '--'],
        'processing_strategy': '统一转换为pandas.NaN',
        'fallback_value': None
    },
    '编码问题': {
        'examples': ['乱码字符', '特殊符号'],
        'processing_strategy': '编码检测和转换',
        'fallback_value': '原始值'
    }
}
```

### 数据一致性检查规则
```python
def check_data_consistency(df):
    """检查数据一致性"""
    consistency_issues = []
    
    # 检查销量和GMV的逻辑关系
    if 'sales_7d' in df.columns and 'gmv_7d' in df.columns:
        # GMV应该大于等于销量（假设最低客单价为1元）
        inconsistent = df['gmv_7d'] < df['sales_7d']
        if inconsistent.any():
            consistency_issues.append(f"发现{inconsistent.sum()}条记录的7天GMV小于销量")
    
    # 检查时间维度数据的逻辑关系
    if 'sales_7d' in df.columns and 'sales_30d' in df.columns:
        # 30天销量应该大于等于7天销量
        inconsistent = df['sales_30d'] < df['sales_7d']
        if inconsistent.any():
            consistency_issues.append(f"发现{inconsistent.sum()}条记录的30天销量小于7天销量")
    
    # 检查佣金比例合理性
    if 'commission' in df.columns:
        unreasonable = (df['commission'] < 0) | (df['commission'] > 1)
        if unreasonable.any():
            consistency_issues.append(f"发现{unreasonable.sum()}条记录的佣金比例不在0-100%范围内")
    
    return consistency_issues
```

## 字段映射智能匹配

### 模糊匹配算法
```python
from difflib import SequenceMatcher

def smart_field_mapping(raw_columns, standard_fields):
    """智能字段映射"""
    mapping = {}
    
    # 预定义的别名字典
    FIELD_ALIASES = {
        'product_name': ['商品', '商品名称', '产品名', '商品标题', '名称'],
        'product_url': ['商品链接', '抖音商品链接', '链接', 'URL'],
        'category_l1': ['商品分类', '分类', '一级分类', '类目'],
        'commission': ['佣金比例', '佣金', '提成比例', '分成'],
        'sales_7d': ['周销量', '近7天销量', '7天销量', '7日销量'],
        'gmv_7d': ['周销售额', '近7天销售额', '7天GMV', '7日GMV'],
        'sales_30d': ['近30天销量', '30天销量', '月销量'],
        'gmv_30d': ['近30天销售额', '30天销售额', '月销售额'],
        'conv_30d': ['30天转化率', '转化率', '转换率'],
        'rank_no': ['排名', '排行', '名次'],
        'influencer_7d': ['周带货达人', '关联达人', '带货达人', '达人']
    }
    
    for std_field, aliases in FIELD_ALIASES.items():
        best_match = None
        best_score = 0
        
        for raw_col in raw_columns:
            # 精确匹配
            if raw_col in aliases:
                mapping[raw_col] = std_field
                break
            
            # 模糊匹配
            for alias in aliases:
                score = SequenceMatcher(None, raw_col, alias).ratio()
                if score > best_score and score > 0.6:  # 相似度阈值
                    best_match = raw_col
                    best_score = score
        
        if best_match and std_field not in mapping.values():
            mapping[best_match] = std_field
    
    return mapping
```

### 字段映射验证
```python
def validate_field_mapping(mapping, df):
    """验证字段映射的有效性"""
    validation_results = {}
    
    for raw_field, std_field in mapping.items():
        if raw_field not in df.columns:
            validation_results[raw_field] = {'status': 'error', 'message': '原始字段不存在'}
            continue
        
        # 检查数据质量
        non_null_ratio = df[raw_field].notna().sum() / len(df)
        unique_ratio = df[raw_field].nunique() / len(df)
        
        validation_results[raw_field] = {
            'status': 'success',
            'std_field': std_field,
            'non_null_ratio': non_null_ratio,
            'unique_ratio': unique_ratio,
            'sample_values': df[raw_field].dropna().head(3).tolist()
        }
    
    return validation_results
```

## 业务规则引擎

### 数据清洗业务规则
```python
BUSINESS_RULES = {
    'product_name_cleaning': {
        'remove_patterns': [r'\[.*?\]', r'【.*?】', r'\(.*?\)', r'（.*?）'],
        'max_length': 100,
        'required': True
    },
    'url_validation': {
        'valid_domains': ['douyin.com', 'dy.com'],
        'required_protocol': 'https',
        'required': False
    },
    'commission_normalization': {
        'min_value': 0,
        'max_value': 1,
        'default_value': 0,
        'format': 'decimal'
    },
    'sales_validation': {
        'min_value': 0,
        'max_reasonable_value': 1000000,
        'data_type': 'integer'
    }
}

def apply_business_rules(df, field_name, rules):
    """应用业务规则清洗数据"""
    if field_name not in df.columns:
        return df
    
    series = df[field_name].copy()
    
    if field_name == 'product_name' and 'product_name_cleaning' in rules:
        rule = rules['product_name_cleaning']
        # 移除特殊模式
        for pattern in rule['remove_patterns']:
            series = series.str.replace(pattern, '', regex=True)
        # 长度限制
        series = series.str[:rule['max_length']]
        # 必填检查
        if rule['required']:
            series = series.fillna('未知商品')
    
    elif field_name == 'commission' and 'commission_normalization' in rules:
        rule = rules['commission_normalization']
        # 数值范围检查
        series = pd.to_numeric(series, errors='coerce')
        series = series.clip(rule['min_value'], rule['max_value'])
        series = series.fillna(rule['default_value'])
    
    df[field_name] = series
    return df
```

## 数据血缘追踪

### 处理过程记录
```python
class DataLineage:
    """数据血缘追踪类"""
    
    def __init__(self):
        self.operations = []
    
    def record_operation(self, operation_type, details):
        """记录数据处理操作"""
        self.operations.append({
            'timestamp': datetime.now(),
            'operation': operation_type,
            'details': details
        })
    
    def get_lineage_report(self):
        """生成数据血缘报告"""
        report = {
            'total_operations': len(self.operations),
            'operations': self.operations,
            'data_flow': self._build_data_flow()
        }
        return report
    
    def _build_data_flow(self):
        """构建数据流图"""
        flow = []
        for op in self.operations:
            flow.append(f"{op['operation']}: {op['details']}")
        return " -> ".join(flow)
```

## 性能基准测试

### 处理性能指标
```python
PERFORMANCE_BENCHMARKS = {
    'small_file': {
        'size_range': '< 1MB',
        'row_count': '< 1000',
        'expected_time': '< 2秒',
        'memory_usage': '< 50MB'
    },
    'medium_file': {
        'size_range': '1-10MB',
        'row_count': '1000-10000',
        'expected_time': '< 10秒',
        'memory_usage': '< 200MB'
    },
    'large_file': {
        'size_range': '10-50MB',
        'row_count': '10000-100000',
        'expected_time': '< 60秒',
        'memory_usage': '< 500MB'
    }
}

def benchmark_processing_performance(df, start_time):
    """性能基准测试"""
    processing_time = time.time() - start_time
    memory_usage = df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
    row_count = len(df)
    
    # 确定文件大小类别
    if row_count < 1000:
        category = 'small_file'
    elif row_count < 10000:
        category = 'medium_file'
    else:
        category = 'large_file'
    
    benchmark = PERFORMANCE_BENCHMARKS[category]
    
    return {
        'category': category,
        'processing_time': processing_time,
        'memory_usage': memory_usage,
        'row_count': row_count,
        'meets_benchmark': processing_time < float(benchmark['expected_time'].split()[1])
    }
```
