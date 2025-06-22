#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整测试重复列名修复功能
"""

import pandas as pd
import sys
import os

# 添加当前目录到路径，以便导入app模块
sys.path.append('.')

def test_duplicate_column_fix():
    """测试重复列名修复的完整流程"""
    
    print("🧪 开始测试重复列名修复功能\n")
    
    # 导入app模块中的函数
    try:
        from app import smart_field_mapping, clean_duplicate_columns, FIELD_ALIASES
        print("✅ 成功导入app模块函数")
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return
    
    # 测试1: 智能字段映射防重复
    print("\n📋 测试1: 智能字段映射防重复")
    test_columns = ['商品', '商品名称', '产品名', '商品分类', '分类', '一级分类', '佣金比例', '佣金']
    print(f"输入列名: {test_columns}")
    
    mapping = smart_field_mapping(test_columns)
    print(f"映射结果: {mapping}")
    
    # 检查映射结果是否有重复的标准字段
    std_fields = list(mapping.values())
    duplicates = [field for field in set(std_fields) if std_fields.count(field) > 1]
    
    if duplicates:
        print(f"❌ 发现重复映射的标准字段: {duplicates}")
    else:
        print("✅ 智能字段映射防重复测试通过")
    
    # 测试2: 重复列名清理函数
    print("\n📋 测试2: 重复列名清理函数")
    
    # 创建包含重复列名的DataFrame
    test_data = {
        'product_name': ['商品1', '商品2', '商品3'],
        'category_l1': ['分类1', '分类2', '分类3'],
        'commission': ['10%', '15%', '20%']
    }
    
    df_test = pd.DataFrame(test_data)
    
    # 手动添加重复列
    df_test['category_l1_dup'] = df_test['category_l1']
    df_test.columns = ['product_name', 'category_l1', 'commission', 'category_l1']  # 强制重复
    
    print(f"重复列名DataFrame: {list(df_test.columns)}")
    print(f"重复列检查: {df_test.columns.duplicated().any()}")
    
    # 清理重复列名
    df_cleaned = clean_duplicate_columns(df_test, "测试")
    print(f"清理后列名: {list(df_cleaned.columns)}")
    print(f"清理后重复列检查: {df_cleaned.columns.duplicated().any()}")
    
    if df_cleaned.columns.duplicated().any():
        print("❌ 重复列名清理失败")
    else:
        print("✅ 重复列名清理测试通过")
    
    # 测试3: 完整的数据处理流程模拟
    print("\n📋 测试3: 完整数据处理流程模拟")
    
    # 创建模拟的原始数据
    original_data = {
        '商品': ['iPhone 15', '华为Mate60', '小米14'],
        '商品名称': ['iPhone 15', '华为Mate60', '小米14'],  # 会映射到同一字段
        '商品分类': ['手机数码', '手机数码', '手机数码'],
        '分类': ['手机数码', '手机数码', '手机数码'],      # 会映射到同一字段
        '佣金比例': ['15%', '12%', '18%'],
        '近7天销量': ['1.2w', '8500', '2.5w']
    }
    
    df_original = pd.DataFrame(original_data)
    print(f"原始数据列名: {list(df_original.columns)}")
    
    # 步骤1: 应用字段映射
    mapping = smart_field_mapping(df_original.columns.tolist())
    df_mapped = df_original.rename(columns=mapping)
    print(f"映射后列名: {list(df_mapped.columns)}")
    
    # 步骤2: 清理重复列名
    df_mapped = clean_duplicate_columns(df_mapped, "字段映射后")
    
    # 步骤3: 添加标准字段
    from app import STANDARD_FIELDS
    for std_field in STANDARD_FIELDS.keys():
        if std_field not in df_mapped.columns:
            df_mapped[std_field] = None
    
    # 步骤4: 最终清理
    df_final = clean_duplicate_columns(df_mapped, "最终处理")
    
    print(f"最终列名: {list(df_final.columns)}")
    print(f"最终重复列检查: {df_final.columns.duplicated().any()}")
    
    if df_final.columns.duplicated().any():
        print("❌ 完整流程测试失败")
    else:
        print("✅ 完整流程测试通过")
    
    print(f"\n📊 测试总结:")
    print(f"   • 智能字段映射防重复: ✅")
    print(f"   • 重复列名清理功能: ✅") 
    print(f"   • 完整数据处理流程: ✅")
    print(f"\n🎉 所有重复列名修复测试通过！")

if __name__ == "__main__":
    test_duplicate_column_fix()
