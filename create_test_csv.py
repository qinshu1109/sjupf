#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建不同格式的测试CSV文件，用于验证CSV读取修复
"""

import pandas as pd
import os

def create_test_csv_files():
    """创建不同分隔符和编码的测试CSV文件"""
    
    # 测试数据
    test_data = {
        '商品': ['iPhone 15', '华为Mate60', '小米14'],
        '商品链接': [
            'https://douyin.com/product/123456',
            'https://douyin.com/product/123457', 
            'https://douyin.com/product/123458'
        ],
        '商品分类': ['手机数码', '手机数码', '手机数码'],
        '佣金比例': ['15%', '12%', '18%'],
        '近7天销量': ['1.2w', '8500', '2.5w'],
        '近7天销售额': ['2400w', '1700w', '5000w']
    }
    
    df = pd.DataFrame(test_data)
    
    # 创建测试目录
    if not os.path.exists('test_csv'):
        os.makedirs('test_csv')
    
    # 1. 标准逗号分隔，UTF-8编码
    df.to_csv('test_csv/standard_comma_utf8.csv', index=False, encoding='utf-8')
    print("✅ 创建标准CSV文件: standard_comma_utf8.csv")
    
    # 2. 分号分隔，UTF-8编码
    df.to_csv('test_csv/semicolon_utf8.csv', index=False, sep=';', encoding='utf-8')
    print("✅ 创建分号分隔CSV文件: semicolon_utf8.csv")
    
    # 3. 制表符分隔，UTF-8编码
    df.to_csv('test_csv/tab_separated.csv', index=False, sep='\t', encoding='utf-8')
    print("✅ 创建制表符分隔CSV文件: tab_separated.csv")
    
    # 4. 逗号分隔，GBK编码
    df.to_csv('test_csv/comma_gbk.csv', index=False, encoding='gbk')
    print("✅ 创建GBK编码CSV文件: comma_gbk.csv")
    
    # 5. 创建一个空文件
    with open('test_csv/empty_file.csv', 'w', encoding='utf-8') as f:
        pass
    print("✅ 创建空CSV文件: empty_file.csv")
    
    # 6. 创建一个只有表头的文件
    df.head(0).to_csv('test_csv/header_only.csv', index=False, encoding='utf-8')
    print("✅ 创建仅表头CSV文件: header_only.csv")
    
    # 7. 创建一个包含特殊字符的文件名（模拟用户提到的文件）
    df.to_csv('test_csv/clean_商品库_20250427-20250526.csv', index=False, encoding='utf-8')
    print("✅ 创建问题文件: clean_商品库_20250427-20250526.csv")
    
    print(f"\n🎯 测试文件创建完成，共7个文件")
    print(f"📂 位置: test_csv/ 目录")
    print(f"\n💡 这些文件可以用来测试:")
    print(f"   • 不同分隔符的自动检测")
    print(f"   • 不同编码的自动识别")
    print(f"   • 空文件和异常文件的处理")

if __name__ == "__main__":
    create_test_csv_files()
