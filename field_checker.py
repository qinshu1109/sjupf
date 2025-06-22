#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电商数据字段完整性检查和补全工具
用于检查和修复评分系统所需的19个标准字段
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

# 评分系统要求的19个标准字段
REQUIRED_FIELDS = [
    'product_name', 'product_url', 'category_l1', 'commission',
    'sales_7d', 'gmv_7d', 'sales_30d', 'gmv_30d',
    'live_gmv_30d', 'live_gmv_7d', 'card_gmv_30d',
    'sales_1y', 'conv_30d', 'rank_type', 'rank_no', 
    'influencer_7d', 'snapshot_tag', 'file_date', 'data_period'
]

# 字段映射表（中文字段名到标准字段名）
FIELD_MAPPING = {
    '商品': 'product_name',
    '商品名称': 'product_name',
    '商品链接': 'product_url',
    '商品URL': 'product_url',
    '商品分类': 'category_l1',
    '一级类目': 'category_l1',
    '佣金比例': 'commission',
    '佣金率': 'commission',
    '近7天销量': 'sales_7d',
    '7天销量': 'sales_7d',
    '近7天销售额': 'gmv_7d',
    '7天GMV': 'gmv_7d',
    '近30天销量': 'sales_30d',
    '30天销量': 'sales_30d',
    '近30天销售额': 'gmv_30d',
    '30天GMV': 'gmv_30d',
    '近30天直播GMV': 'live_gmv_30d',
    '30天直播GMV': 'live_gmv_30d',
    '近7天直播GMV': 'live_gmv_7d',
    '7天直播GMV': 'live_gmv_7d',
    '近30天商品卡GMV': 'card_gmv_30d',
    '30天商品卡GMV': 'card_gmv_30d',
    '近1年销量': 'sales_1y',
    '1年销量': 'sales_1y',
    '近30天转化率': 'conv_30d',
    '30天转化率': 'conv_30d',
    '转化率': 'conv_30d',
    '排名类型': 'rank_type',
    '榜单类型': 'rank_type',
    '排名': 'rank_no',
    '排名位置': 'rank_no',
    '近7天达人数': 'influencer_7d',
    '7天达人数': 'influencer_7d',
    '快照标签': 'snapshot_tag',
    '标签': 'snapshot_tag',
    '文件日期': 'file_date',
    '数据日期': 'file_date',
    '数据周期': 'data_period',
    '统计周期': 'data_period'
}

def check_file_fields(file_path):
    """检查文件字段完整性"""
    print(f"🔍 检查文件: {file_path}")
    print("=" * 60)
    
    try:
        # 读取文件
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path, encoding='utf-8')
        
        print(f"📊 文件信息:")
        print(f"  • 行数: {len(df)}")
        print(f"  • 列数: {len(df.columns)}")
        print(f"  • 文件大小: {os.path.getsize(file_path)} 字节")
        
        print(f"\n📋 当前字段列表:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")
        
        # 字段映射
        mapped_fields = {}
        for col in df.columns:
            if col in FIELD_MAPPING:
                mapped_fields[col] = FIELD_MAPPING[col]
            else:
                mapped_fields[col] = col
        
        print(f"\n🔗 字段映射结果:")
        for original, mapped in mapped_fields.items():
            if original != mapped:
                print(f"  {original} → {mapped}")
            else:
                print(f"  {original} (保持不变)")
        
        # 检查缺失字段
        mapped_values = set(mapped_fields.values())
        missing_fields = [field for field in REQUIRED_FIELDS if field not in mapped_values]
        
        print(f"\n❌ 缺失字段 ({len(missing_fields)}/19):")
        for field in missing_fields:
            print(f"  • {field}")
        
        print(f"\n✅ 已有字段 ({len(REQUIRED_FIELDS) - len(missing_fields)}/19):")
        for field in REQUIRED_FIELDS:
            if field in mapped_values:
                print(f"  • {field}")
        
        return df, mapped_fields, missing_fields
        
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return None, None, None

def add_missing_fields(df, mapped_fields, missing_fields):
    """补全缺失字段"""
    print(f"\n🔧 开始补全缺失字段...")
    
    # 重命名现有字段
    rename_dict = {}
    for original, mapped in mapped_fields.items():
        if original != mapped:
            rename_dict[original] = mapped
    
    if rename_dict:
        df = df.rename(columns=rename_dict)
        print(f"✅ 字段重命名完成: {len(rename_dict)} 个字段")
    
    # 添加缺失字段
    for field in missing_fields:
        if field == 'live_gmv_7d':
            # 基于30天直播GMV估算7天数据
            if 'live_gmv_30d' in df.columns:
                df[field] = df['live_gmv_30d'] * 0.23  # 7/30 ≈ 0.23
            else:
                df[field] = 0
        elif field == 'live_gmv_30d':
            # 基于总GMV估算直播GMV（假设30%来自直播）
            if 'gmv_30d' in df.columns:
                df[field] = df['gmv_30d'] * 0.3
            else:
                df[field] = 0
        elif field == 'card_gmv_30d':
            # 基于总GMV估算商品卡GMV（假设20%来自商品卡）
            if 'gmv_30d' in df.columns:
                df[field] = df['gmv_30d'] * 0.2
            else:
                df[field] = 0
        elif field == 'sales_1y':
            # 基于30天销量估算年销量
            if 'sales_30d' in df.columns:
                df[field] = df['sales_30d'] * 12
            else:
                df[field] = 0
        elif field == 'conv_30d':
            # 默认转化率3%
            df[field] = 0.03
        elif field == 'rank_type':
            # 默认为潜力榜
            df[field] = '潜力榜'
        elif field == 'rank_no':
            # 默认排名为行号
            df[field] = range(1, len(df) + 1)
        elif field == 'influencer_7d':
            # 默认达人数为5
            df[field] = 5
        elif field == 'snapshot_tag':
            # 默认标签
            df[field] = '数据补全'
        elif field == 'file_date':
            # 当前日期
            df[field] = datetime.now().strftime('%Y-%m-%d')
        elif field == 'data_period':
            # 默认数据周期
            df[field] = '30天'
        else:
            # 其他字段默认为0
            df[field] = 0
    
    print(f"✅ 字段补全完成: {len(missing_fields)} 个字段")
    
    # 确保字段顺序
    df = df[REQUIRED_FIELDS]
    
    return df

def save_completed_file(df, original_path):
    """保存补全后的文件"""
    # 生成新文件名
    base_name = os.path.splitext(os.path.basename(original_path))[0]
    new_name = f"completed_{base_name}.csv"
    new_path = os.path.join(os.path.dirname(original_path), new_name)
    
    # 保存文件
    df.to_csv(new_path, index=False, encoding='utf-8-sig')
    
    print(f"\n💾 文件保存完成:")
    print(f"  • 原文件: {original_path}")
    print(f"  • 新文件: {new_path}")
    print(f"  • 行数: {len(df)}")
    print(f"  • 列数: {len(df.columns)}")
    
    return new_path

def main():
    """主函数"""
    print("🔧 电商数据字段完整性检查和补全工具")
    print("=" * 60)
    
    # 检查目标文件
    target_file = "test_csv/clean_商品库_20250427-20250526.csv"
    
    if not os.path.exists(target_file):
        print(f"❌ 文件不存在: {target_file}")
        return
    
    # 1. 检查字段完整性
    df, mapped_fields, missing_fields = check_file_fields(target_file)
    
    if df is None:
        return
    
    # 2. 补全缺失字段
    if missing_fields:
        print(f"\n🚨 发现 {len(missing_fields)} 个缺失字段，开始补全...")
        completed_df = add_missing_fields(df, mapped_fields, missing_fields)
        
        # 3. 保存补全后的文件
        new_file = save_completed_file(completed_df, target_file)
        
        print(f"\n🎉 字段补全完成！")
        print(f"📋 补全后字段列表:")
        for i, col in enumerate(completed_df.columns, 1):
            print(f"  {i:2d}. {col}")
        
        print(f"\n💡 使用建议:")
        print(f"  1. 使用补全后的文件: {new_file}")
        print(f"  2. 上传到评分系统进行测试")
        print(f"  3. 根据实际业务需求调整默认值")
        
    else:
        print(f"\n✅ 字段完整性检查通过，无需补全")

if __name__ == "__main__":
    main()
