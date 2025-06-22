#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据生成器
为抖音数据清洗工具生成测试用的Excel文件
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def create_test_data():
    """创建测试用的抖音电商数据"""
    
    # 模拟不同的字段名称（用户实际遇到的各种别名）
    test_data_1 = {
        '商品': ['iPhone 15 Pro Max', '华为Mate60', '小米14 Ultra', '三星Galaxy S24', 'OPPO Find X7'],
        '商品链接': [
            'https://douyin.com/product/123456',
            'https://douyin.com/product/123457', 
            'https://douyin.com/product/123458',
            'https://douyin.com/product/123459',
            'https://douyin.com/product/123460'
        ],
        '商品分类': ['手机数码', '手机数码', '手机数码', '手机数码', '手机数码'],
        '佣金比例': ['15%', '12%', '18%', '10%', '20%'],
        '近7天销量': ['1.2w', '8500', '2.5w', '5600', '1.8w'],
        '近7天销售额': ['2400w', '1700w', '5000w', '1120w', '3600w'],
        '近30天销量': ['5.2w', '3.5w', '10.8w', '2.3w', '7.2w'],
        '近30天销售额': ['1.04亿', '7000w', '2.16亿', '4600w', '1.44亿'],
        '排名': [1, 2, 3, 4, 5],
        '关联达人': ['李佳琦', '薇娅', '辛巴', '罗永浩', '董宇辉']
    }
    
    # 创建第一个测试文件
    df1 = pd.DataFrame(test_data_1)
    
    # 模拟另一种字段命名方式
    test_data_2 = {
        '产品名': ['戴森吹风机', '雅诗兰黛面霜', '兰蔻精华', '海蓝之谜面膜', 'SK-II神仙水'],
        '抖音商品链接': [
            'https://dy.com/item/234567',
            'https://dy.com/item/234568',
            'https://dy.com/item/234569', 
            'https://dy.com/item/234570',
            'https://dy.com/item/234571'
        ],
        '一级分类': ['美妆护肤', '美妆护肤', '美妆护肤', '美妆护肤', '美妆护肤'],
        '佣金': ['25%', '30%', '28%', '35%', '32%'],
        '7天销量': ['3200', '2800', '4100', '1900', '3600'],
        '7天GMV': ['960w', '840w', '1230w', '570w', '1080w'],
        '30天销量': ['1.5w', '1.2w', '1.8w', '8500', '1.6w'],
        '30天销售额': ['4500w', '3600w', '5400w', '2550w', '4800w'],
        '转化率': ['8.5%', '12.3%', '9.8%', '15.2%', '11.7%'],
        '名次': [1, 2, 3, 4, 5],
        '带货达人': ['张大奕', '雪梨', '林珊珊', '陈洁kiki', '张沫凡']
    }
    
    df2 = pd.DataFrame(test_data_2)
    
    # 创建输出目录
    if not os.path.exists('test_data'):
        os.makedirs('test_data')
    
    # 创建第三个测试数据集（CSV格式）
    test_data_3 = {
        '商品名称': ['Nike Air Max', 'Adidas Ultra Boost', 'New Balance 990', 'Converse Chuck Taylor', 'Vans Old Skool'],
        '链接': [
            'https://douyin.com/shoes/345678',
            'https://douyin.com/shoes/345679',
            'https://douyin.com/shoes/345680',
            'https://douyin.com/shoes/345681',
            'https://douyin.com/shoes/345682'
        ],
        '类目': ['运动鞋服', '运动鞋服', '运动鞋服', '运动鞋服', '运动鞋服'],
        '分成': ['22%', '25%', '20%', '18%', '24%'],
        '7日销量': ['2.1w', '1.8w', '1.5w', '3.2w', '2.7w'],
        '周GMV': ['1260w', '1080w', '900w', '1920w', '1620w'],
        '月销量': ['8.5w', '7.2w', '6.0w', '12.8w', '10.8w'],
        '月GMV': ['5100w', '4320w', '3600w', '7680w', '6480w'],
        '转换率': ['6.8%', '9.2%', '7.5%', '11.3%', '8.9%'],
        '排行': [1, 2, 3, 4, 5],
        '达人': ['潮流小王子', '运动达人', '街头风尚', '球鞋收藏家', '时尚博主']
    }

    df3 = pd.DataFrame(test_data_3)

    # 保存测试文件 - 测试不同的时间格式
    timestamp = datetime.now().strftime("%Y%m%d")

    # 文件名包含不同的时间格式，用于测试时间提取功能
    filenames = [
        # 日期区间格式
        f'test_data/销量榜-手机数码-{timestamp}-20250630.xlsx',
        # 相对时间格式
        f'test_data/热推榜-美妆护肤-30d.xlsx',
        # 单日期格式 + CSV
        f'test_data/潜力榜-运动鞋服-{timestamp}.csv',
        # 混合格式
        f'test_data/持续好货榜-数码配件-7d-{timestamp}.xlsx',
        # 年度格式
        f'test_data/同期榜-家居用品-1y.csv'
    ]

    # 保存不同格式的文件
    df1.to_excel(filenames[0], index=False, engine='openpyxl')
    df2.to_excel(filenames[1], index=False, engine='openpyxl')
    df3.to_csv(filenames[2], index=False, encoding='utf-8')
    df1.to_excel(filenames[3], index=False, engine='openpyxl')
    df2.to_csv(filenames[4], index=False, encoding='utf-8')

    print(f"✅ 测试数据已生成 (包含多种时间格式):")
    for i, filename in enumerate(filenames):
        print(f"   📁 {filename}")

    print(f"\n🎯 测试功能覆盖:")
    print(f"   ✅ 不同字段命名方式的智能映射")
    print(f"   ✅ Excel(.xlsx) 和 CSV(.csv) 格式支持")
    print(f"   ✅ 多种时间格式提取:")
    print(f"      • 日期区间: YYYYMMDD-YYYYMMDD")
    print(f"      • 相对时间: 30d, 7d, 1y")
    print(f"      • 单日期: YYYYMMDD")
    print(f"      • 混合格式: 7d-YYYYMMDD")
    print(f"   ✅ 榜单类型和数据来源提取")

if __name__ == "__main__":
    create_test_data()
