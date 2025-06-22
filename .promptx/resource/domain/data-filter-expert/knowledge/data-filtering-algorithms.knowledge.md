# 数据过滤算法知识库

## 核心评分算法详解

### 1. 长尾截断与标准化算法

```python
def clip_and_normalize(series, percentile=99):
    """
    长尾截断与标准化处理
    
    Args:
        series: 输入数据序列
        percentile: 截断分位数，默认99%
        
    Returns:
        标准化后的[0,1]区间数据
    """
    # Step 1: 99分位截断
    upper_bound = series.quantile(percentile / 100)
    clipped = series.clip(upper=upper_bound)
    
    # Step 2: 对数变换
    log_transformed = np.log(clipped + 1)
    
    # Step 3: Min-Max标准化
    min_val = log_transformed.min()
    max_val = log_transformed.max()
    normalized = (log_transformed - min_val) / (max_val - min_val)
    
    return normalized
```

**算法原理**：
- 99分位截断消除极值影响
- 对数变换平滑数据分布
- Min-Max归一化统一量纲

### 2. Commission分段评分算法

```python
def score_commission(commission_series):
    """
    佣金分段评分算法
    
    分段规则：
    - <0.25: 线性评分 c/0.25
    - [0.25,0.3): 基础分1.0 + 奖励0.1
    - [0.3,0.35): 基础分1.0 + 奖励0.15  
    - >=0.35: 基础分1.0 + 奖励0.2
    """
    def calc_score(c):
        if c < 0.25:
            return c / 0.25
        elif 0.25 <= c < 0.3:
            return 1.0 + 0.1
        elif 0.3 <= c < 0.35:
            return 1.0 + 0.15
        else:
            return 1.0 + 0.2
    
    return commission_series.apply(calc_score)
```

**业务逻辑**：
- 低佣金线性评分，鼓励基础参与
- 中高佣金阶梯奖励，激励优质合作
- 分段设计平衡商家和平台利益

### 3. 余弦衰减算法

```python
def cosine_decay_score(influencer_series):
    """
    达人影响力余弦衰减评分
    
    公式：s = n / sqrt(n² + mean_n²)
    其中 n 为达人数量，mean_n 为列均值
    """
    n = influencer_series
    mean_n = influencer_series.mean()
    mean_n_squared = mean_n ** 2
    
    score = n / np.sqrt(n**2 + mean_n_squared)
    return score
```

**数学特性**：
- 余弦函数特性，平滑衰减
- 相对评分，避免绝对数值主导
- 自适应均值，动态调整基准

### 4. 指数衰减 + 类型基础分

```python
def rank_score_with_decay(rank_type_series, rank_no_series):
    """
    排名指数衰减 + 类型基础分
    
    Args:
        rank_type_series: 排名类型（潜力榜/销量榜/其他）
        rank_no_series: 排名位置（从1开始）
    """
    # 类型基础分
    base_scores = rank_type_series.map({
        '潜力榜': 0.4,
        '销量榜': 0.3,
        '其他': 0.2
    }).fillna(0.2)
    
    # 指数衰减部分
    rank_part = np.exp(-0.015 * (rank_no_series - 1))
    
    # 组合得分
    final_score = base_scores * 0.4 + rank_part * 0.6
    return final_score
```

**设计思路**：
- 潜力榜基础分最高，体现成长价值
- 指数衰减反映排名重要性
- 组合评分平衡类型和位置因素

### 5. 增长潜力评分算法

```python
def growth_potential_score(sales_30d, sales_1y):
    """
    增长潜力评分：销售1y × 增长率
    
    Args:
        sales_30d: 近30天销量
        sales_1y: 近1年销量
    """
    # 计算月均销量
    monthly_avg = sales_1y / 12
    
    # 计算增长率
    growth_rate = sales_30d / (monthly_avg + 1)
    
    # 大商家惩罚
    penalty = np.where(sales_1y > 5e4, 0.2, 0)
    
    # 最终得分
    score = np.clip(growth_rate - penalty, 0, 1)
    return score
```

**业务考量**：
- 增长率反映商品动态表现
- 大商家惩罚避免马太效应
- 区间限制保持评分合理性

### 6. 渠道分布评分算法

```python
def channel_distribution_score(live_gmv_30d, live_gmv_7d, 
                              card_gmv_30d, gmv_30d, gmv_7d):
    """
    渠道分布评分算法
    
    评分逻辑：
    - 降低直播依赖度奖励
    - 提升商品卡表现奖励
    """
    # 计算各渠道占比
    live_ratio_30d = live_gmv_30d / (gmv_30d + 1e-9)
    live_ratio_7d = live_gmv_7d / (gmv_7d + 1e-9)
    card_ratio_30d = card_gmv_30d / (gmv_30d + 1e-9)
    
    # 渠道得分计算
    channel_score = (
        (1 - live_ratio_30d) * 0.03 +  # 降低直播依赖
        (1 - live_ratio_7d) * 0.02 +   # 短期直播依赖
        card_ratio_30d * 0.05           # 商品卡表现
    )
    
    return channel_score
```

**策略意图**：
- 鼓励多元化销售渠道
- 降低对直播的过度依赖
- 提升商品卡等稳定渠道

## 节日感知算法

### 节日距离计算

```python
def calculate_days_to_next_holiday(file_date):
    """
    计算距离下一个节日的天数
    
    Args:
        file_date: 文件日期 (YYYY-MM-DD)
        
    Returns:
        int: 距离下一节日的天数
    """
    holidays = [
        (1, 1),   # 元旦
        (2, 14),  # 情人节
        (3, 8),   # 妇女节
        (6, 1),   # 儿童节
        (9, 15),  # 中秋（农历近似）
        (10, 1),  # 国庆
        (12, 25)  # 圣诞
    ]
    
    current_date = pd.to_datetime(file_date)
    current_year = current_date.year
    
    min_days = float('inf')
    
    for month, day in holidays:
        # 当年节日
        holiday_date = pd.to_datetime(f"{current_year}-{month:02d}-{day:02d}")
        if holiday_date >= current_date:
            days = (holiday_date - current_date).days
            min_days = min(min_days, days)
        
        # 下一年节日
        next_year_holiday = pd.to_datetime(f"{current_year+1}-{month:02d}-{day:02d}")
        days = (next_year_holiday - current_date).days
        min_days = min(min_days, days)
    
    return min_days
```

### 动态权重调整算法

```python
def adjust_weights_for_holiday(base_weights, is_holiday_mode):
    """
    节日模式权重动态调整
    
    调整规则：
    - sales_7d权重 +0.02
    - 销量榜基础分 +0.02（在rank_score中体现）
    - 其他权重按比例缩放保持总和=1
    """
    if not is_holiday_mode:
        return base_weights
    
    adjusted = base_weights.copy()
    
    # sales_7d权重增加
    adjusted['sales_7d'] += 0.02
    
    # 计算需要缩放的其他权重
    other_keys = [k for k in adjusted.keys() if k != 'sales_7d']
    total_others = sum(adjusted[k] for k in other_keys)
    
    # 计算缩放因子
    remaining_weight = 1.0 - adjusted['sales_7d']
    scale_factor = remaining_weight / total_others
    
    # 应用缩放
    for key in other_keys:
        adjusted[key] *= scale_factor
    
    return adjusted
```

## 数据质量控制算法

### 转化率阈值过滤

```python
def filter_and_score_conversion(conv_30d_series):
    """
    转化率阈值过滤与评分
    
    规则：
    - conv_30d < 0.02 → 整行淘汰
    - 其余线性映射 [0, 0.2] → [0, 1]
    - 最终权重 × 0.08
    """
    # 阈值过滤
    valid_mask = conv_30d_series >= 0.02
    
    # 线性映射
    clipped = conv_30d_series.clip(0, 0.2)
    normalized = clipped / 0.2
    
    # 应用权重
    score = normalized * 0.08
    
    return score, valid_mask
```

### 异常值检测与处理

```python
def detect_and_handle_outliers(df, columns, method='iqr'):
    """
    异常值检测与处理
    
    Args:
        df: 输入DataFrame
        columns: 需要检测的列名列表
        method: 检测方法 ('iqr', 'zscore', 'percentile')
    """
    cleaned_df = df.copy()
    
    for col in columns:
        if method == 'iqr':
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            cleaned_df[col] = df[col].clip(lower_bound, upper_bound)
        
        elif method == 'percentile':
            lower_bound = df[col].quantile(0.01)
            upper_bound = df[col].quantile(0.99)
            cleaned_df[col] = df[col].clip(lower_bound, upper_bound)
    
    return cleaned_df
```

## 性能优化技术

### 向量化计算优化

```python
# 避免循环，使用向量化操作
# 错误示例
scores = []
for idx, row in df.iterrows():
    score = calculate_score(row)
    scores.append(score)

# 正确示例  
scores = df.apply(lambda row: calculate_score(row), axis=1)
# 或更好的向量化
scores = vectorized_calculate_score(df)
```

### 内存优化策略

```python
def process_large_file_in_chunks(file_path, chunk_size=10000):
    """
    分块处理大文件，优化内存使用
    """
    results = []
    
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        processed_chunk = process_data_chunk(chunk)
        results.append(processed_chunk)
    
    return pd.concat(results, ignore_index=True)
```

这些算法构成了数据过滤系统的核心技术基础，确保评分的准确性、公平性和高效性。
