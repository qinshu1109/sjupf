#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试重复列名修复功能
"""

import pandas as pd
import os

def create_duplicate_column_test_files():
    """创建包含重复列名问题的测试文件"""
    
    # 创建测试目录
    if not os.path.exists('test_duplicate'):
        os.makedirs('test_duplicate')
    
    # 测试案例1：原始数据中有重复列名
    test_data_1 = {
        '商品': ['iPhone 15', '华为Mate60', '小米14'],
        '商品分类': ['手机数码', '手机数码', '手机数码'],
        '分类': ['手机数码', '手机数码', '手机数码'],  # 这会映射到同一个标准字段
        '佣金比例': ['15%', '12%', '18%'],
        '佣金': ['15%', '12%', '18%'],  # 这也会映射到同一个标准字段
        '近7天销量': ['1.2w', '8500', '2.5w']
    }
    
    df1 = pd.DataFrame(test_data_1)
    df1.to_csv('test_duplicate/duplicate_mapping_fields.csv', index=False, encoding='utf-8')
    print("✅ 创建重复映射字段测试文件: duplicate_mapping_fields.csv")
    
    # 测试案例2：直接包含重复列名的CSV
    test_data_2 = {
        '商品': ['Nike Air Max', 'Adidas Ultra Boost', 'New Balance 990'],
        '商品链接': ['https://douyin.com/1', 'https://douyin.com/2', 'https://douyin.com/3'],
        '商品分类': ['运动鞋服', '运动鞋服', '运动鞋服']
    }
    
    df2 = pd.DataFrame(test_data_2)
    # 手动添加重复列名
    df2['商品分类_duplicate'] = df2['商品分类']
    df2.columns = ['商品', '商品链接', '商品分类', '商品分类']  # 强制创建重复列名
    
    df2.to_csv('test_duplicate/direct_duplicate_columns.csv', index=False, encoding='utf-8')
    print("✅ 创建直接重复列名测试文件: direct_duplicate_columns.csv")
    
    # 测试案例3：多种别名映射到同一字段
    test_data_3 = {
        '商品名称': ['戴森吹风机', '雅诗兰黛面霜', '兰蔻精华'],
        '产品名': ['戴森吹风机', '雅诗兰黛面霜', '兰蔻精华'],  # 都会映射到product_name
        '商品': ['戴森吹风机', '雅诗兰黛面霜', '兰蔻精华'],    # 都会映射到product_name
        '一级分类': ['美妆护肤', '美妆护肤', '美妆护肤'],
        '商品分类': ['美妆护肤', '美妆护肤', '美妆护肤'],      # 都会映射到category_l1
        '分类': ['美妆护肤', '美妆护肤', '美妆护肤'],          # 都会映射到category_l1
        '佣金比例': ['25%', '30%', '28%']
    }
    
    df3 = pd.DataFrame(test_data_3)
    df3.to_csv('test_duplicate/multiple_aliases.csv', index=False, encoding='utf-8')
    print("✅ 创建多别名映射测试文件: multiple_aliases.csv")
    
    print(f"\n🎯 重复列名测试文件创建完成")
    print(f"📂 位置: test_duplicate/ 目录")
    print(f"\n💡 这些文件可以用来测试:")
    print(f"   • 字段映射时的重复列名处理")
    print(f"   • 直接重复列名的去重功能")
    print(f"   • 多个别名映射到同一标准字段的处理")

def test_smart_field_mapping():
    """测试智能字段映射函数的重复处理"""
    
    # 模拟FIELD_ALIASES
    FIELD_ALIASES = {
        'product_name': ['商品', '商品名称', '产品名', '商品标题', '名称'],
        'category_l1': ['商品分类', '分类', '一级分类', '类目'],
        'commission': ['佣金比例', '佣金', '提成比例', '分成']
    }
    
    def smart_field_mapping(columns):
        """简化版的智能字段映射函数"""
        mapping = {}
        used_std_fields = set()
        
        # 第一轮：精确匹配
        for std_field, aliases in FIELD_ALIASES.items():
            if std_field in used_std_fields:
                continue
                
            for col in columns:
                if col in aliases:
                    mapping[col] = std_field
                    used_std_fields.add(std_field)
                    break
        
        # 第二轮：模糊匹配
        for std_field, aliases in FIELD_ALIASES.items():
            if std_field in used_std_fields:
                continue
                
            for col in columns:
                if col in mapping:
                    continue
                    
                for alias in aliases:
                    if alias in col or col in alias:
                        mapping[col] = std_field
                        used_std_fields.add(std_field)
                        break
                
                if std_field in used_std_fields:
                    break
        
        return mapping
    
    # 测试重复映射场景
    test_columns = ['商品', '商品名称', '产品名', '商品分类', '分类', '佣金比例', '佣金']
    
    print("\n🧪 测试智能字段映射防重复功能")
    print(f"输入列名: {test_columns}")
    
    mapping = smart_field_mapping(test_columns)
    print(f"映射结果: {mapping}")
    
    # 检查是否有重复的标准字段
    std_fields = list(mapping.values())
    duplicates = [field for field in set(std_fields) if std_fields.count(field) > 1]
    
    if duplicates:
        print(f"❌ 发现重复映射的标准字段: {duplicates}")
    else:
        print("✅ 没有重复映射，测试通过")

if __name__ == "__main__":
    create_duplicate_column_test_files()
    test_smart_field_mapping()
