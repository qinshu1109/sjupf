#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试字段映射修复效果
验证 card_gmv_30d 和 sales_1y 字段是否能正确映射
"""

import pandas as pd
import os

def create_test_excel():
    """创建包含缺失字段的测试Excel文件"""
    
    # 测试数据 - 包含之前缺失映射的字段
    test_data = {
        '商品': ['iPhone 15 Pro', '华为Mate60', '小米14 Ultra'],
        '商品链接': ['https://douyin.com/product/1', 'https://douyin.com/product/2', 'https://douyin.com/product/3'],
        '商品分类': ['手机数码', '手机数码', '手机数码'],
        '佣金比例': ['15%', '12%', '18%'],
        '7天销量': ['1,200', '800', '1,500'],
        '30天销量': ['5,000', '3,200', '6,800'],
        '商品卡销售额': ['425,004.25', '280,150.50', '520,300.75'],  # 关键测试字段1
        '近1年销量': ['50,000', '32,000', '68,000'],  # 关键测试字段2
        '30天转化率': ['8.5%', '6.2%', '9.1%'],
        '排名': [1, 2, 3]
    }
    
    df = pd.DataFrame(test_data)
    
    # 保存为Excel文件
    test_file = 'test_field_mapping_fix.xlsx'
    df.to_excel(test_file, index=False, engine='openpyxl')
    
    print(f"✅ 创建测试文件: {test_file}")
    print(f"📊 测试数据包含 {len(df)} 行，{len(df.columns)} 列")
    print("\n🔍 关键测试字段:")
    print("• 商品卡销售额 (应映射到 card_gmv_30d)")
    print("• 近1年销量 (应映射到 sales_1y)")
    
    return test_file, df

def test_field_mapping():
    """测试字段映射功能"""
    
    # 导入应用模块
    import sys
    sys.path.append('.')
    from app import smart_field_mapping, FIELD_ALIASES
    
    print("🧪 开始字段映射测试...")
    
    # 测试列名
    test_columns = [
        '商品', '商品链接', '商品分类', '佣金比例',
        '7天销量', '30天销量', '商品卡销售额', '近1年销量',
        '30天转化率', '排名'
    ]
    
    print(f"\n📋 测试列名: {test_columns}")
    
    # 执行字段映射
    mapping = smart_field_mapping(test_columns)
    
    print(f"\n🔗 映射结果:")
    for original, mapped in mapping.items():
        print(f"  {original} → {mapped}")
    
    # 验证关键字段
    print(f"\n✅ 关键字段验证:")
    
    # 验证 card_gmv_30d
    if '商品卡销售额' in mapping and mapping['商品卡销售额'] == 'card_gmv_30d':
        print("  ✅ 商品卡销售额 → card_gmv_30d (正确)")
    else:
        print(f"  ❌ 商品卡销售额 → {mapping.get('商品卡销售额', '未映射')} (错误)")
    
    # 验证 sales_1y
    if '近1年销量' in mapping and mapping['近1年销量'] == 'sales_1y':
        print("  ✅ 近1年销量 → sales_1y (正确)")
    else:
        print(f"  ❌ 近1年销量 → {mapping.get('近1年销量', '未映射')} (错误)")
    
    # 检查别名配置
    print(f"\n📚 别名配置检查:")
    print(f"  card_gmv_30d 别名: {FIELD_ALIASES.get('card_gmv_30d', '未配置')}")
    print(f"  sales_1y 别名: {FIELD_ALIASES.get('sales_1y', '未配置')}")
    
    return mapping

def main():
    """主测试函数"""
    print("🔧 字段映射修复验证测试")
    print("=" * 50)
    
    # 1. 创建测试文件
    test_file, test_df = create_test_excel()
    
    # 2. 测试字段映射
    mapping = test_field_mapping()
    
    # 3. 生成测试报告
    print(f"\n📊 测试报告:")
    print(f"  • 测试文件: {test_file}")
    print(f"  • 原始列数: {len(test_df.columns)}")
    print(f"  • 映射字段数: {len(mapping)}")
    print(f"  • 映射成功率: {len(mapping)/len(test_df.columns)*100:.1f}%")
    
    # 4. 使用说明
    print(f"\n🚀 使用说明:")
    print(f"  1. 打开浏览器访问: http://localhost:8507")
    print(f"  2. 上传测试文件: {test_file}")
    print(f"  3. 检查字段映射预览中是否包含:")
    print(f"     • 商品卡销售额 → 30天商品卡GMV")
    print(f"     • 近1年销量 → 1年销量")
    print(f"  4. 执行数据清洗并检查结果")
    
    print(f"\n✅ 测试完成！")

if __name__ == "__main__":
    main()
