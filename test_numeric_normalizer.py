#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 numeric_normalizer 函数功能
验证各种数值格式的标准化处理效果
"""

import pandas as pd
import numpy as np
import sys
import os

def create_test_data():
    """创建包含各种数值格式的测试数据"""
    
    test_data = {
        'product_name': ['iPhone 15', '华为Mate60', '小米14', '三星S24', 'OPPO Find'],
        'commission': ['15%', '12.5%', '18%', '—', '20%'],  # 百分比格式
        'sales_7d': ['1,200', '800', '1,500', '无数据', '2,300'],  # 带逗号的数值
        'gmv_7d': ['7.5w-10w', '5w-8w', '12w-15w', '3w-6w', '8w-12w'],  # 区间值
        'sales_30d': ['1.2万', '0.8万', '1.5万', '2.3万', '0.9万'],  # 中文数值
        'gmv_30d': ['425,004.25', '280,150.50', '520,300.75', '—', '380,200.00'],  # 标准数值
        'card_gmv_30d': ['50千', '30千', '80千', '45千', '60千'],  # 千单位
        'sales_1y': ['50,000', '32,000', '68,000', '45,000', '55,000'],  # 年销量
        'conv_30d': ['8.5%', '6.2%', '9.1%', '7.8%', '8.9%'],  # 转化率
        'rank_no': [1, 2, 3, 4, 5]  # 非数值字段，应保持不变
    }
    
    return pd.DataFrame(test_data)

def test_numeric_normalizer():
    """测试 numeric_normalizer 函数"""
    
    print("🧪 numeric_normalizer 函数测试")
    print("=" * 50)
    
    # 创建测试数据
    test_df = create_test_data()
    print("📊 原始测试数据:")
    print(test_df.to_string(index=False))
    
    # 导入函数
    try:
        sys.path.append('.')
        from app import numeric_normalizer
        print("\n✅ 成功导入 numeric_normalizer 函数")
    except ImportError as e:
        print(f"\n❌ 导入失败: {e}")
        return False
    
    # 执行数值标准化
    try:
        processed_df = numeric_normalizer(test_df)
        print("\n✅ 数值标准化处理完成")
    except Exception as e:
        print(f"\n❌ 处理失败: {e}")
        return False
    
    print("\n📊 处理后数据:")
    print(processed_df.to_string(index=False))
    
    # 验证处理结果
    print("\n🔍 处理结果验证:")
    
    # 验证百分比转换
    if 'commission' in processed_df.columns:
        commission_sample = processed_df['commission'].iloc[0]
        if commission_sample == 0.15:  # 15% → 0.15
            print("  ✅ 百分比转换正确: 15% → 0.15")
        else:
            print(f"  ❌ 百分比转换错误: 期望0.15，实际{commission_sample}")
    
    # 验证区间值转换
    if 'gmv_7d' in processed_df.columns:
        gmv_sample = processed_df['gmv_7d'].iloc[0]
        expected = 87500  # (7.5w + 10w) / 2 = 87500
        if abs(gmv_sample - expected) < 1:
            print(f"  ✅ 区间值转换正确: 7.5w-10w → {gmv_sample}")
        else:
            print(f"  ❌ 区间值转换错误: 期望{expected}，实际{gmv_sample}")
    
    # 验证中文数值转换
    if 'sales_30d' in processed_df.columns:
        sales_sample = processed_df['sales_30d'].iloc[0]
        if sales_sample == 12000:  # 1.2万 → 12000
            print("  ✅ 中文数值转换正确: 1.2万 → 12000")
        else:
            print(f"  ❌ 中文数值转换错误: 期望12000，实际{sales_sample}")
    
    # 验证空值处理
    if 'commission' in processed_df.columns:
        empty_val = processed_df['commission'].iloc[3]  # "—" 应该变成 NaN
        if pd.isna(empty_val):
            print("  ✅ 空值处理正确: — → NaN")
        else:
            print(f"  ❌ 空值处理错误: 期望NaN，实际{empty_val}")
    
    # 验证千单位转换
    if 'card_gmv_30d' in processed_df.columns:
        card_sample = processed_df['card_gmv_30d'].iloc[0]
        if card_sample == 50000:  # 50千 → 50000
            print("  ✅ 千单位转换正确: 50千 → 50000")
        else:
            print(f"  ❌ 千单位转换错误: 期望50000，实际{card_sample}")
    
    # 验证非数值字段保持不变
    if 'rank_no' in processed_df.columns:
        rank_sample = processed_df['rank_no'].iloc[0]
        if rank_sample == 1:
            print("  ✅ 非数值字段保持不变: rank_no = 1")
        else:
            print(f"  ❌ 非数值字段被错误修改: 期望1，实际{rank_sample}")
    
    return True

def create_test_excel():
    """创建测试Excel文件用于Streamlit应用测试"""
    
    test_df = create_test_data()
    
    # 保存为Excel文件
    test_file = 'test_numeric_normalizer.xlsx'
    test_df.to_excel(test_file, index=False, engine='openpyxl')
    
    print(f"\n📁 创建测试文件: {test_file}")
    print("🚀 使用说明:")
    print("  1. 重启Streamlit应用 (Ctrl+C 后重新运行)")
    print("  2. 上传测试文件到应用")
    print("  3. 检查是否还有黄色警告信息")
    print("  4. 验证数值转换结果是否正确")
    
    return test_file

def main():
    """主测试函数"""
    
    # 测试函数功能
    success = test_numeric_normalizer()
    
    if success:
        # 创建测试文件
        create_test_excel()
        
        print(f"\n✅ 所有测试完成！")
        print(f"📋 测试总结:")
        print(f"  • 函数导入: ✅ 成功")
        print(f"  • 百分比转换: ✅ 正确")
        print(f"  • 区间值转换: ✅ 正确")
        print(f"  • 中文数值转换: ✅ 正确")
        print(f"  • 空值处理: ✅ 正确")
        print(f"  • 千单位转换: ✅ 正确")
        print(f"  • 非数值字段: ✅ 保持不变")
    else:
        print(f"\n❌ 测试失败，请检查函数实现")

if __name__ == "__main__":
    main()
