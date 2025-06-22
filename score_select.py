#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电商数据智能过滤评分系统
功能：多维度评分算法 + 节日模式感知 + TOP50筛选
作者：数据过滤专家
"""

import pandas as pd
import numpy as np
import argparse
import os
import glob
import re
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def get_base_weights():
    """获取基础权重配置（支持动态调整）"""
    return {
        'sales_30d_score': 0.12,
        'gmv_30d_score': 0.08,
        'sales_7d_score': 0.08,
        'gmv_7d_score': 0.07,
        'commission_score': 0.15,
        'influencer_score': 0.10,
        'rank_score': 0.12,
        'growth_score': 0.08,
        'channel_score': 0.05,
        'conv_score': 0.05,
        'live_gmv_score': 0.05,
        'card_gmv_score': 0.05
    }

def parse_file_date(date_string):
    """
    解析file_date字段，支持多种格式：
    - 单一日期: YYYY-MM-DD → 直接返回
    - 日期范围: YYYY-MM-DD至YYYY-MM-DD → 返回中点日期
    - 无效格式 → 返回当前日期作为备用

    Args:
        date_string: file_date列的字符串值

    Returns:
        str: 解析后的标准日期格式 YYYY-MM-DD
    """
    if pd.isna(date_string):
        return pd.Timestamp.now().strftime('%Y-%m-%d')

    date_string = str(date_string).strip()

    # 处理日期范围格式: YYYY-MM-DD至YYYY-MM-DD
    range_match = re.match(r'(\d{4}-\d{2}-\d{2})至(\d{4}-\d{2}-\d{2})', date_string)
    if range_match:
        start_date, end_date = range_match.groups()
        try:
            d1 = pd.to_datetime(start_date)
            d2 = pd.to_datetime(end_date)
            midpoint = d1 + (d2 - d1) / 2
            return midpoint.strftime('%Y-%m-%d')
        except:
            return pd.Timestamp.now().strftime('%Y-%m-%d')

    # 处理单一日期格式: YYYY-MM-DD
    try:
        parsed_date = pd.to_datetime(date_string, format="%Y-%m-%d")
        return parsed_date.strftime('%Y-%m-%d')
    except:
        # 尝试其他常见格式
        try:
            parsed_date = pd.to_datetime(date_string)
            return parsed_date.strftime('%Y-%m-%d')
        except:
            return pd.Timestamp.now().strftime('%Y-%m-%d')

def calculate_days_to_next_holiday(file_date):
    """计算距离下一个节日的天数（支持解析后的标准日期格式）"""
    holidays = [
        (1, 1),   # 元旦
        (2, 14),  # 情人节
        (3, 8),   # 妇女节
        (6, 1),   # 儿童节
        (9, 15),  # 中秋
        (10, 1),  # 国庆
        (12, 25)  # 圣诞
    ]

    try:
        # file_date现在保证是YYYY-MM-DD格式
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
    except Exception as e:
        print(f"⚠️ 节日距离计算失败: {e}，使用默认值999天")
        return 999

def adjust_weights_for_available_fields(df, base_weights):
    """
    根据数据文件中实际存在的字段动态调整权重

    Args:
        df: 输入数据DataFrame
        base_weights: 基础权重字典

    Returns:
        dict: 调整后的权重字典

    Raises:
        ValueError: 当缺少所有销量/GMV字段时
    """
    weights = base_weights.copy()

    # 检查字段存在性
    has_7d_fields = all(col in df.columns for col in ['sales_7d', 'gmv_7d'])
    has_30d_fields = all(col in df.columns for col in ['sales_30d', 'gmv_30d'])

    print(f"🔍 字段检查: 7天字段={has_7d_fields}, 30天字段={has_30d_fields}")

    if has_7d_fields and has_30d_fields:
        # 场景A: 完整数据，使用默认权重
        print("✅ 场景A: 完整数据，使用默认权重配置")
        return weights

    elif has_30d_fields and not has_7d_fields:
        # 场景B: 仅有30天数据，将7天权重转移给30天
        print("⚠️ 场景B: 仅有30天数据，将7天权重转移给30天字段")
        boost_total = weights['sales_7d_score'] + weights['gmv_7d_score']
        current_30d_total = weights['sales_30d_score'] + weights['gmv_30d_score']

        # 按比例分配增加的权重
        sales_boost = boost_total * (weights['sales_30d_score'] / current_30d_total)
        gmv_boost = boost_total * (weights['gmv_30d_score'] / current_30d_total)

        weights['sales_30d_score'] += sales_boost
        weights['gmv_30d_score'] += gmv_boost
        weights['sales_7d_score'] = 0
        weights['gmv_7d_score'] = 0

        print(f"  📊 权重调整: sales_30d {weights['sales_30d_score']-sales_boost:.3f}→{weights['sales_30d_score']:.3f}")
        print(f"  📊 权重调整: gmv_30d {weights['gmv_30d_score']-gmv_boost:.3f}→{weights['gmv_30d_score']:.3f}")

    elif has_7d_fields and not has_30d_fields:
        # 场景C: 仅有7天数据，将30天权重转移给7天
        print("⚠️ 场景C: 仅有7天数据，将30天权重转移给7天字段")
        boost_total = weights['sales_30d_score'] + weights['gmv_30d_score']
        current_7d_total = weights['sales_7d_score'] + weights['gmv_7d_score']

        # 按比例分配增加的权重
        sales_boost = boost_total * (weights['sales_7d_score'] / current_7d_total)
        gmv_boost = boost_total * (weights['gmv_7d_score'] / current_7d_total)

        weights['sales_7d_score'] += sales_boost
        weights['gmv_7d_score'] += gmv_boost
        weights['sales_30d_score'] = 0
        weights['gmv_30d_score'] = 0

        print(f"  📊 权重调整: sales_7d {weights['sales_7d_score']-sales_boost:.3f}→{weights['sales_7d_score']:.3f}")
        print(f"  📊 权重调整: gmv_7d {weights['gmv_7d_score']-gmv_boost:.3f}→{weights['gmv_7d_score']:.3f}")

    else:
        # 场景D: 缺少所有销量/GMV字段
        raise ValueError("数据文件缺少必要的销量和GMV字段（sales_7d/30d, gmv_7d/30d），无法进行评分")

    # 验证权重总和
    total_weight = sum(weights.values())
    print(f"✅ 权重总和验证: {total_weight:.6f}")

    return weights

def adjust_holiday_weights(base_weights, is_holiday_mode):
    """节日模式权重动态调整"""
    if not is_holiday_mode:
        return base_weights

    adjusted = base_weights.copy()

    # 优先调整存在的7天销量权重，如果不存在则调整30天权重
    if adjusted['sales_7d_score'] > 0:
        adjusted['sales_7d_score'] += 0.02
        boost_field = 'sales_7d_score'
    elif adjusted['sales_30d_score'] > 0:
        adjusted['sales_30d_score'] += 0.02
        boost_field = 'sales_30d_score'
    else:
        # 如果都没有销量字段，则不进行节日调整
        return adjusted

    # 其他权重按比例缩放
    other_keys = [k for k in adjusted.keys() if k != boost_field]
    total_others = sum(adjusted[k] for k in other_keys)
    scale_factor = (1 - adjusted[boost_field]) / total_others

    for key in other_keys:
        adjusted[key] *= scale_factor

    print(f"🎄 节日模式: {boost_field} 权重增加0.02")

    return adjusted

def clip_and_normalize(series, percentile=99):
    """长尾截断与标准化处理"""
    if series.isna().all():
        return pd.Series(0, index=series.index)
    
    # 99分位截断
    upper_bound = series.quantile(percentile / 100)
    clipped = series.clip(upper=upper_bound)
    
    # 对数变换
    log_transformed = np.log(clipped + 1)
    
    # Min-Max标准化
    min_val = log_transformed.min()
    max_val = log_transformed.max()
    if max_val == min_val:
        return pd.Series(0, index=series.index)
    
    normalized = (log_transformed - min_val) / (max_val - min_val)
    return normalized

def score_commission(commission_series):
    """佣金分段评分算法"""
    def calc_score(c):
        if pd.isna(c):
            return 0
        if c < 0.25:
            return c / 0.25
        elif 0.25 <= c < 0.3:
            return 1.0 + 0.1
        elif 0.3 <= c < 0.35:
            return 1.0 + 0.15
        else:
            return 1.0 + 0.2
    
    return commission_series.apply(calc_score)

def cosine_decay_score(influencer_series):
    """达人影响力余弦衰减评分"""
    if influencer_series.isna().all() or influencer_series.mean() == 0:
        return pd.Series(0, index=influencer_series.index)
    
    n = influencer_series.fillna(0)
    mean_n = n.mean()
    mean_n_squared = mean_n ** 2
    
    score = n / np.sqrt(n**2 + mean_n_squared)
    return score

def rank_score_with_decay(rank_type_series, rank_no_series, is_holiday_mode=False):
    """排名指数衰减 + 类型基础分"""
    # 类型基础分
    base_scores = rank_type_series.map({
        '潜力榜': 0.4,
        '销量榜': 0.3,
        '其他': 0.2
    }).fillna(0.2)

    # 节日模式下销量榜基础分+0.02
    if is_holiday_mode:
        base_scores = base_scores.where(rank_type_series != '销量榜', base_scores + 0.02)

    # 指数衰减部分
    rank_no_filled = rank_no_series.fillna(999)
    rank_part = np.exp(-0.015 * (rank_no_filled - 1))

    # 组合得分
    final_score = base_scores * 0.4 + rank_part * 0.6
    return final_score

def growth_potential_score(sales_30d, sales_1y):
    """增长潜力评分：销售1y × 增长率"""
    # 计算月均销量
    monthly_avg = sales_1y / 12

    # 计算增长率
    growth_rate = sales_30d / (monthly_avg + 1)

    # 大商家惩罚
    penalty = np.where(sales_1y > 5e4, 0.2, 0)

    # 最终得分
    score = np.clip(growth_rate - penalty, 0, 1)
    return score

def channel_distribution_score(live_gmv_30d, live_gmv_7d, card_gmv_30d, gmv_30d, gmv_7d):
    """渠道分布评分算法（支持缺失字段）"""
    # 安全地计算各渠道占比，处理NaN和缺失值
    live_ratio_30d = np.where(
        (gmv_30d > 0) & (~pd.isna(live_gmv_30d)) & (~pd.isna(gmv_30d)),
        live_gmv_30d / gmv_30d,
        0.3  # 默认直播占比30%
    )

    live_ratio_7d = np.where(
        (gmv_7d > 0) & (~pd.isna(live_gmv_7d)) & (~pd.isna(gmv_7d)),
        live_gmv_7d / gmv_7d,
        0.3  # 默认直播占比30%
    )

    card_ratio_30d = np.where(
        (gmv_30d > 0) & (~pd.isna(card_gmv_30d)) & (~pd.isna(gmv_30d)),
        card_gmv_30d / gmv_30d,
        0.2  # 默认商品卡占比20%
    )

    # 渠道得分计算
    channel_score = (
        (1 - live_ratio_30d) * 0.03 +  # 降低直播依赖
        (1 - live_ratio_7d) * 0.02 +   # 短期直播依赖
        card_ratio_30d * 0.05           # 商品卡表现
    )

    # 确保返回值在合理范围内
    channel_score = np.clip(channel_score, 0, 1)

    return channel_score

def filter_and_score_conversion(conv_30d_series):
    """转化率阈值过滤与评分"""
    # 阈值过滤
    valid_mask = conv_30d_series >= 0.02

    # 线性映射 [0, 0.2] → [0, 1]
    clipped = conv_30d_series.clip(0, 0.2)
    normalized = clipped / 0.2

    # 应用权重
    score = normalized * 0.08

    return score, valid_mask

def read_data_file(file_path):
    """读取CSV/XLSX文件"""
    try:
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            # 尝试不同编码
            for encoding in ['utf-8', 'gbk', 'gb2312']:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except:
                    continue
            else:
                df = pd.read_csv(file_path)

        return df
    except Exception as e:
        print(f"读取文件失败 {file_path}: {e}")
        return None

def process_single_file(df, file_date, is_holiday_mode):
    """处理单个文件的评分计算（支持动态权重和日期解析）"""
    print(f"\n🔄 开始处理文件数据...")

    # 解析和标准化文件日期
    if 'file_date' in df.columns and len(df) > 0:
        raw_file_date = df['file_date'].iloc[0]
        parsed_file_date = parse_file_date(raw_file_date)
        print(f"📅 日期解析: {raw_file_date} → {parsed_file_date}")
        file_date = parsed_file_date
    else:
        file_date = datetime.now().strftime('%Y-%m-%d')
        print(f"📅 使用默认日期: {file_date}")

    # 检测节日模式
    days_to_holiday = calculate_days_to_next_holiday(file_date)
    is_holiday_mode = days_to_holiday <= 45

    if is_holiday_mode:
        print(f"🎄 启用节日模式 (距离下一节日 {days_to_holiday} 天)")
    else:
        print(f"📅 标准模式 (距离下一节日 {days_to_holiday} 天)")

    # 获取基础权重并进行动态调整
    base_weights = get_base_weights()
    try:
        adjusted_weights = adjust_weights_for_available_fields(df, base_weights)
    except ValueError as e:
        print(f"⚠️ 跳过文件: {e}")
        return pd.DataFrame()

    # 应用节日模式调整（如果启用）
    if is_holiday_mode:
        adjusted_weights = adjust_holiday_weights(adjusted_weights, is_holiday_mode)

    # 数据类型转换（先确保所有必要字段存在）
    numeric_cols = ['sales_7d', 'sales_30d', 'gmv_7d', 'gmv_30d',
                   'live_gmv_30d', 'live_gmv_7d', 'card_gmv_30d',
                   'sales_1y', 'conv_30d', 'commission', 'influencer_7d', 'rank_no']

    # 补全缺失的数值字段
    for col in numeric_cols:
        if col not in df.columns:
            df[col] = 0
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 转化率过滤（优化过滤逻辑）
    if 'conv_30d' in df.columns and df['conv_30d'].notna().any():
        # 只有当转化率列存在且有有效数据时才进行过滤
        conv_score, valid_mask = filter_and_score_conversion(df['conv_30d'])

        # 检查过滤后是否还有数据
        if valid_mask.sum() == 0:
            print("⚠️ 转化率过滤过于严格，放宽过滤条件")
            # 放宽过滤条件：转化率 >= 0.01 或使用所有数据
            relaxed_mask = df['conv_30d'] >= 0.01
            if relaxed_mask.sum() > 0:
                df = df[relaxed_mask].copy()
                # 重新计算conv_score以确保索引匹配
                conv_score = df['conv_30d'].clip(0, 0.2) / 0.2 * 0.08
                print(f"📊 使用放宽条件：转化率 >= 0.01，保留 {len(df)} 行数据")
            else:
                print("📊 使用所有数据，不进行转化率过滤")
                # 不过滤数据，重新计算conv_score
                conv_score = df['conv_30d'].clip(0, 0.2) / 0.2 * 0.08
        else:
            df = df[valid_mask].copy()
            # 重新计算conv_score以确保索引匹配
            conv_score = df['conv_30d'].clip(0, 0.2) / 0.2 * 0.08
            print(f"📊 转化率过滤：保留 {len(df)} 行数据（转化率 >= 0.02）")
    else:
        print("📊 转化率列缺失或无有效数据，使用默认转化率评分")
        conv_score = pd.Series(0.04, index=df.index)  # 默认中等转化率评分

    if len(df) == 0:
        print("⚠️ 数据过滤后无有效数据")
        return pd.DataFrame()

    # 计算各维度得分（仅计算存在的字段）
    if 'sales_7d' in df.columns and adjusted_weights['sales_7d_score'] > 0:
        df['sales_7d_score'] = clip_and_normalize(df['sales_7d'])
    else:
        df['sales_7d_score'] = 0

    if 'sales_30d' in df.columns and adjusted_weights['sales_30d_score'] > 0:
        df['sales_30d_score'] = clip_and_normalize(df['sales_30d'])
    else:
        df['sales_30d_score'] = 0

    if 'gmv_7d' in df.columns and adjusted_weights['gmv_7d_score'] > 0:
        df['gmv_7d_score'] = clip_and_normalize(df['gmv_7d'])
    else:
        df['gmv_7d_score'] = 0

    if 'gmv_30d' in df.columns and adjusted_weights['gmv_30d_score'] > 0:
        df['gmv_30d_score'] = clip_and_normalize(df['gmv_30d'])
    else:
        df['gmv_30d_score'] = 0

    df['commission_score'] = score_commission(df['commission'])
    df['influencer_score'] = cosine_decay_score(df['influencer_7d'])
    df['rank_score'] = rank_score_with_decay(df['rank_type'], df['rank_no'], is_holiday_mode)

    # 增长潜力评分需要30天数据，如果没有则使用7天数据估算
    if 'sales_30d' in df.columns and 'sales_1y' in df.columns:
        df['growth_score'] = growth_potential_score(df['sales_30d'], df['sales_1y'])
    elif 'sales_7d' in df.columns and 'sales_1y' in df.columns:
        # 使用7天数据估算30天数据
        estimated_sales_30d = df['sales_7d'] * 4.3  # 30/7 ≈ 4.3
        df['growth_score'] = growth_potential_score(estimated_sales_30d, df['sales_1y'])
    else:
        df['growth_score'] = 0.5  # 默认中等增长潜力

    # 渠道分布评分（现在支持缺失字段）
    # 确保所有渠道相关字段存在，缺失的用0填充
    for col in ['live_gmv_30d', 'live_gmv_7d', 'card_gmv_30d', 'gmv_7d']:
        if col not in df.columns:
            df[col] = 0

    df['channel_score'] = channel_distribution_score(
        df['live_gmv_30d'], df['live_gmv_7d'], df['card_gmv_30d'],
        df['gmv_30d'], df['gmv_7d']
    )

    df['conv_score'] = conv_score

    # 使用调整后的权重计算总分
    df['total_score'] = calculate_total_score(df, adjusted_weights)

    print(f"✅ 文件处理完成: {len(df)} 行有效数据")

    return df

def calculate_total_score(df, weights):
    """计算加权总分（支持动态权重）"""
    total_score = pd.Series(0.0, index=df.index)

    for col, weight in weights.items():
        if col in df.columns and weight > 0:
            total_score += df[col] * weight

    return total_score

def process_data_files(input_dir, output_dir):
    """处理所有数据文件"""
    # 扫描输入目录
    file_patterns = [
        os.path.join(input_dir, "*.csv"),
        os.path.join(input_dir, "*.xlsx")
    ]

    all_files = []
    for pattern in file_patterns:
        all_files.extend(glob.glob(pattern))

    if not all_files:
        print(f"在目录 {input_dir} 中未找到CSV或XLSX文件")
        return

    print(f"找到 {len(all_files)} 个文件待处理")

    all_results = []
    eliminated_count = 0

    for file_path in all_files:
        print(f"处理文件: {os.path.basename(file_path)}")

        # 读取数据
        df = read_data_file(file_path)
        if df is None:
            continue

        original_count = len(df)

        # 处理数据（日期解析在函数内部完成）
        processed_df = process_single_file(df, None, False)  # 临时传入None，函数内部会解析

        if len(processed_df) == 0:
            print(f"  文件处理后无有效数据")
            eliminated_count += original_count
            continue

        # 总分已在process_single_file中计算完成

        all_results.append(processed_df)
        eliminated_count += original_count - len(processed_df)

        print(f"  处理完成: {len(processed_df)}/{original_count} 行有效")

    if not all_results:
        print("没有有效数据可处理")
        return

    # 合并所有结果
    combined_df = pd.concat(all_results, ignore_index=True)

    # 按product_url去重
    before_dedup = len(combined_df)
    combined_df = combined_df.drop_duplicates(subset=['product_url'], keep='first')
    after_dedup = len(combined_df)

    print(f"去重处理: {before_dedup} → {after_dedup} 行")

    # 排序取TOP50
    top50_df = combined_df.nlargest(50, 'total_score')

    # 保持原17字段 + total_score
    original_cols = ['product_name', 'product_url', 'category_l1', 'commission',
                    'sales_7d', 'gmv_7d', 'sales_30d', 'gmv_30d',
                    'live_gmv_30d', 'live_gmv_7d', 'card_gmv_30d',
                    'sales_1y', 'conv_30d', 'rank_type', 'rank_no',
                    'influencer_7d', 'snapshot_tag', 'file_date', 'data_period']

    output_cols = [col for col in original_cols if col in top50_df.columns] + ['total_score']
    top50_df = top50_df[output_cols]

    # 输出文件
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "top50_combined.csv")
    top50_df.to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f"\n处理完成:")
    print(f"  处理文件数: {len(all_files)}")
    print(f"  淘汰行数: {eliminated_count}")
    print(f"  生成文件: {output_file}")
    print(f"  TOP50商品已保存")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='电商数据智能过滤评分系统')
    parser.add_argument('--in', dest='input_dir', required=True, help='输入清洗数据目录')
    parser.add_argument('--out', dest='output_dir', required=True, help='输出TOP50结果目录')

    args = parser.parse_args()

    if not os.path.exists(args.input_dir):
        print(f"输入目录不存在: {args.input_dir}")
        return

    process_data_files(args.input_dir, args.output_dir)

if __name__ == "__main__":
    main()
