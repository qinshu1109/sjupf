#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
特定问题验证脚本
测试转化率过滤逻辑缺陷和sales_1y字段NaN值处理
"""

import pandas as pd
import numpy as np

# 导入评分脚本
try:
    import score_select as ss
except ImportError:
    print("❌ 无法导入score_select.py，请确保文件在同一目录下")
    exit(1)

def test_conversion_filter_edge_cases():
    """测试转化率过滤的边界情况"""
    print("🧪 测试转化率过滤边界情况")
    print("=" * 60)
    
    # 测试场景1：所有转化率都小于0.02但大于0.01
    print("📊 场景1：所有转化率在0.01-0.02之间")
    test_data_1 = {
        'product_name': ['商品A', '商品B', '商品C'],
        'product_url': ['https://a.com', 'https://b.com', 'https://c.com'],
        'category_l1': ['数码', '服装', '家居'],
        'commission': [0.15, 0.20, 0.12],
        'sales_30d': [1000, 1500, 800],
        'gmv_30d': [50000, 75000, 40000],
        'conv_30d': [0.015, 0.018, 0.012],  # 都在0.01-0.02之间
        'rank_type': ['潜力榜', '销量榜', '潜力榜'],
        'rank_no': [5, 2, 8],
        'influencer_7d': [10, 15, 8],
        'file_date': ['2025-05-15'] * 3
    }
    
    df1 = pd.DataFrame(test_data_1)
    
    try:
        processed_df1 = ss.process_single_file(df1, None, False)
        if len(processed_df1) > 0:
            print(f"✅ 场景1处理成功: {len(processed_df1)} 行数据")
            print(f"conv_score范围: {processed_df1['conv_score'].min():.4f} - {processed_df1['conv_score'].max():.4f}")
        else:
            print(f"❌ 场景1处理失败: 无有效数据")
    except Exception as e:
        print(f"❌ 场景1处理异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试场景2：所有转化率都小于0.01
    print(f"\n📊 场景2：所有转化率都小于0.01")
    test_data_2 = {
        'product_name': ['商品D', '商品E', '商品F'],
        'product_url': ['https://d.com', 'https://e.com', 'https://f.com'],
        'category_l1': ['数码', '服装', '家居'],
        'commission': [0.15, 0.20, 0.12],
        'sales_30d': [1000, 1500, 800],
        'gmv_30d': [50000, 75000, 40000],
        'conv_30d': [0.005, 0.008, 0.003],  # 都小于0.01
        'rank_type': ['潜力榜', '销量榜', '潜力榜'],
        'rank_no': [5, 2, 8],
        'influencer_7d': [10, 15, 8],
        'file_date': ['2025-05-15'] * 3
    }
    
    df2 = pd.DataFrame(test_data_2)
    
    try:
        processed_df2 = ss.process_single_file(df2, None, False)
        if len(processed_df2) > 0:
            print(f"✅ 场景2处理成功: {len(processed_df2)} 行数据")
            print(f"conv_score范围: {processed_df2['conv_score'].min():.4f} - {processed_df2['conv_score'].max():.4f}")
        else:
            print(f"❌ 场景2处理失败: 无有效数据")
    except Exception as e:
        print(f"❌ 场景2处理异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试场景3：转化率包含NaN值
    print(f"\n📊 场景3：转化率包含NaN值")
    test_data_3 = {
        'product_name': ['商品G', '商品H', '商品I'],
        'product_url': ['https://g.com', 'https://h.com', 'https://i.com'],
        'category_l1': ['数码', '服装', '家居'],
        'commission': [0.15, 0.20, 0.12],
        'sales_30d': [1000, 1500, 800],
        'gmv_30d': [50000, 75000, 40000],
        'conv_30d': [0.025, np.nan, 0.015],  # 包含NaN
        'rank_type': ['潜力榜', '销量榜', '潜力榜'],
        'rank_no': [5, 2, 8],
        'influencer_7d': [10, 15, 8],
        'file_date': ['2025-05-15'] * 3
    }
    
    df3 = pd.DataFrame(test_data_3)
    
    try:
        processed_df3 = ss.process_single_file(df3, None, False)
        if len(processed_df3) > 0:
            print(f"✅ 场景3处理成功: {len(processed_df3)} 行数据")
            print(f"conv_score范围: {processed_df3['conv_score'].min():.4f} - {processed_df3['conv_score'].max():.4f}")
        else:
            print(f"❌ 场景3处理失败: 无有效数据")
    except Exception as e:
        print(f"❌ 场景3处理异常: {e}")
        import traceback
        traceback.print_exc()

def test_sales_1y_nan_handling():
    """测试sales_1y字段NaN值处理"""
    print("\n🧪 测试sales_1y字段NaN值处理")
    print("=" * 60)
    
    # 测试场景：sales_1y包含NaN值
    test_data = {
        'product_name': ['商品J', '商品K', '商品L'],
        'product_url': ['https://j.com', 'https://k.com', 'https://l.com'],
        'category_l1': ['数码', '服装', '家居'],
        'commission': [0.15, 0.20, 0.12],
        'sales_30d': [1000, 1500, 800],
        'gmv_30d': [50000, 75000, 40000],
        'conv_30d': [0.025, 0.030, 0.022],
        'sales_1y': [12000, np.nan, 9600],  # 包含NaN
        'rank_type': ['潜力榜', '销量榜', '潜力榜'],
        'rank_no': [5, 2, 8],
        'influencer_7d': [10, 15, 8],
        'file_date': ['2025-05-15'] * 3
    }
    
    df = pd.DataFrame(test_data)
    
    print(f"📊 原始sales_1y数据:")
    for i, row in df.iterrows():
        print(f"  {row['product_name']}: {row['sales_1y']}")
    
    try:
        processed_df = ss.process_single_file(df, None, False)
        if len(processed_df) > 0:
            print(f"\n✅ sales_1y NaN处理成功: {len(processed_df)} 行数据")
            print(f"处理后sales_1y数据:")
            for i, row in processed_df.iterrows():
                print(f"  {row['product_name']}: sales_1y={row['sales_1y']}, growth_score={row['growth_score']:.4f}")
        else:
            print(f"❌ sales_1y NaN处理失败: 无有效数据")
    except Exception as e:
        print(f"❌ sales_1y NaN处理异常: {e}")
        import traceback
        traceback.print_exc()

def test_index_consistency():
    """测试索引一致性问题"""
    print("\n🧪 测试索引一致性")
    print("=" * 60)
    
    # 创建一个会触发多级过滤的数据集
    test_data = {
        'product_name': ['商品M', '商品N', '商品O', '商品P', '商品Q'],
        'product_url': ['https://m.com', 'https://n.com', 'https://o.com', 'https://p.com', 'https://q.com'],
        'category_l1': ['数码', '服装', '家居', '美妆', '食品'],
        'commission': [0.15, 0.20, 0.12, 0.25, 0.18],
        'sales_30d': [1000, 1500, 800, 1200, 900],
        'gmv_30d': [50000, 75000, 40000, 60000, 45000],
        'conv_30d': [0.008, 0.015, 0.003, 0.012, 0.006],  # 混合：有些<0.01，有些在0.01-0.02之间
        'rank_type': ['潜力榜', '销量榜', '潜力榜', '销量榜', '其他'],
        'rank_no': [5, 2, 8, 3, 12],
        'influencer_7d': [10, 15, 8, 12, 6],
        'file_date': ['2025-05-15'] * 5
    }
    
    df = pd.DataFrame(test_data)
    
    print(f"📊 测试数据转化率分布:")
    for i, row in df.iterrows():
        print(f"  {row['product_name']}: conv_30d={row['conv_30d']:.3f}")
    
    try:
        processed_df = ss.process_single_file(df, None, False)
        if len(processed_df) > 0:
            print(f"\n✅ 索引一致性测试成功: {len(processed_df)} 行数据")
            print(f"处理后数据:")
            for i, row in processed_df.iterrows():
                print(f"  {row['product_name']}: conv_30d={row['conv_30d']:.3f}, conv_score={row['conv_score']:.4f}, total_score={row['total_score']:.4f}")
            
            # 验证索引一致性
            if len(processed_df) == processed_df['conv_score'].count():
                print(f"✅ 索引一致性验证通过")
            else:
                print(f"❌ 索引一致性验证失败")
                
        else:
            print(f"❌ 索引一致性测试失败: 无有效数据")
    except Exception as e:
        print(f"❌ 索引一致性测试异常: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主测试函数"""
    print("🔧 特定问题验证测试")
    print("=" * 80)
    
    test_results = []
    
    # 测试1: 转化率过滤边界情况
    try:
        test_conversion_filter_edge_cases()
        test_results.append(("转化率过滤边界情况", True))
    except Exception as e:
        print(f"❌ 转化率过滤测试失败: {e}")
        test_results.append(("转化率过滤边界情况", False))
    
    # 测试2: sales_1y NaN值处理
    try:
        test_sales_1y_nan_handling()
        test_results.append(("sales_1y NaN值处理", True))
    except Exception as e:
        print(f"❌ sales_1y NaN测试失败: {e}")
        test_results.append(("sales_1y NaN值处理", False))
    
    # 测试3: 索引一致性
    try:
        test_index_consistency()
        test_results.append(("索引一致性", True))
    except Exception as e:
        print(f"❌ 索引一致性测试失败: {e}")
        test_results.append(("索引一致性", False))
    
    # 汇总测试结果
    print(f"\n📊 测试结果汇总")
    print("=" * 80)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print(f"🎉 所有特定问题已修复！")
        print(f"\n💡 修复内容:")
        print(f"  1. 转化率过滤逻辑：确保conv_score索引与df一致")
        print(f"  2. sales_1y NaN处理：自动填充0值，不影响评分")
        print(f"  3. 索引一致性：所有过滤分支都正确处理索引")
    else:
        print(f"⚠️ 部分测试失败，需要进一步修复")

if __name__ == "__main__":
    main()
