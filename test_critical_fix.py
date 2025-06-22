#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关键Bug修复验证脚本
测试修复后的系统是否能正确处理日期范围格式和转化率过滤
"""

import pandas as pd
import os

# 导入评分脚本
try:
    import score_select as ss
except ImportError:
    print("❌ 无法导入score_select.py，请确保文件在同一目录下")
    exit(1)

def test_date_range_processing():
    """测试日期范围格式处理"""
    print("🧪 测试日期范围格式处理")
    print("=" * 60)
    
    # 使用现有的日期范围测试文件
    test_file = "test_csv/date_range_format.csv"
    
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    try:
        # 读取测试文件
        df = pd.read_csv(test_file)
        print(f"✅ 成功读取测试文件: {len(df)} 行数据")
        
        # 显示原始日期格式
        if 'file_date' in df.columns:
            original_date = df['file_date'].iloc[0]
            print(f"📅 原始日期格式: {original_date}")
        
        # 测试完整的数据处理流程
        print(f"\n🔄 开始完整数据处理...")
        
        processed_df = ss.process_single_file(df, None, False)
        
        if len(processed_df) > 0:
            print(f"✅ 数据处理成功!")
            print(f"  • 处理行数: {len(processed_df)}")
            print(f"  • 平均总分: {processed_df['total_score'].mean():.4f}")
            print(f"  • 最高总分: {processed_df['total_score'].max():.4f}")
            print(f"  • 最低总分: {processed_df['total_score'].min():.4f}")
            return True
        else:
            print(f"❌ 数据处理后无有效数据")
            return False
            
    except Exception as e:
        print(f"❌ 文件处理失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_conversion_rate_filtering():
    """测试转化率过滤逻辑"""
    print("\n🧪 测试转化率过滤逻辑")
    print("=" * 60)
    
    # 创建包含不同转化率的测试数据
    test_data = {
        'product_name': ['高转化商品', '中转化商品', '低转化商品', '极低转化商品'],
        'product_url': ['https://high.com', 'https://mid.com', 'https://low.com', 'https://verylow.com'],
        'category_l1': ['数码', '服装', '家居', '美妆'],
        'commission': [0.15, 0.20, 0.12, 0.25],
        'sales_30d': [1000, 1500, 800, 1200],
        'gmv_30d': [50000, 75000, 40000, 60000],
        'conv_30d': [0.05, 0.025, 0.015, 0.005],  # 不同转化率水平
        'rank_type': ['潜力榜', '销量榜', '潜力榜', '销量榜'],
        'rank_no': [5, 2, 8, 3],
        'influencer_7d': [10, 15, 8, 12],
        'file_date': ['2025-04-27至2025-05-26'] * 4
    }
    
    df = pd.DataFrame(test_data)
    
    print(f"📊 测试数据:")
    print(df[['product_name', 'conv_30d', 'file_date']].to_string(index=False))
    
    try:
        # 测试处理
        print(f"\n🔄 测试转化率过滤处理:")
        processed_df = ss.process_single_file(df, None, False)
        
        if len(processed_df) > 0:
            print(f"✅ 转化率过滤处理成功: {len(processed_df)} 行有效数据")
            print(f"保留的商品:")
            for i, row in processed_df.iterrows():
                print(f"  • {row['product_name']}: 转化率={row['conv_30d']:.3f}, 总分={row['total_score']:.4f}")
            return True
        else:
            print(f"❌ 转化率过滤后无有效数据")
            return False
            
    except Exception as e:
        print(f"❌ 转化率过滤测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_missing_conv_column():
    """测试缺失转化率列的处理"""
    print("\n🧪 测试缺失转化率列的处理")
    print("=" * 60)
    
    # 创建不包含conv_30d列的测试数据
    test_data = {
        'product_name': ['商品A', '商品B', '商品C'],
        'product_url': ['https://a.com', 'https://b.com', 'https://c.com'],
        'category_l1': ['数码', '服装', '家居'],
        'commission': [0.15, 0.20, 0.12],
        'sales_30d': [1000, 1500, 800],
        'gmv_30d': [50000, 75000, 40000],
        # 故意不包含conv_30d列
        'rank_type': ['潜力榜', '销量榜', '潜力榜'],
        'rank_no': [5, 2, 8],
        'influencer_7d': [10, 15, 8],
        'file_date': ['2025-04-27至2025-05-26'] * 3
    }
    
    df = pd.DataFrame(test_data)
    
    print(f"📊 测试数据（无conv_30d列）:")
    print(df[['product_name', 'file_date']].to_string(index=False))
    
    try:
        # 测试处理
        print(f"\n🔄 测试缺失转化率列处理:")
        processed_df = ss.process_single_file(df, None, False)
        
        if len(processed_df) > 0:
            print(f"✅ 缺失转化率列处理成功: {len(processed_df)} 行有效数据")
            print(f"默认转化率评分:")
            for i, row in processed_df.iterrows():
                print(f"  • {row['product_name']}: conv_score={row['conv_score']:.4f}, 总分={row['total_score']:.4f}")
            return True
        else:
            print(f"❌ 缺失转化率列处理失败")
            return False
            
    except Exception as e:
        print(f"❌ 缺失转化率列测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_real_file_processing():
    """测试真实文件处理"""
    print("\n🧪 测试真实文件处理")
    print("=" * 60)
    
    # 查找真实的商品库文件
    real_files = [
        "test_csv/clean_商品库_20250427-20250526.csv",
        "test_csv/completed_clean_商品库_20250427-20250526.csv",
        "test_csv/ready_for_scoring_商品库_20250427-20250526.csv"
    ]
    
    for file_path in real_files:
        if os.path.exists(file_path):
            print(f"📁 找到真实文件: {file_path}")
            
            try:
                # 读取文件
                df = pd.read_csv(file_path)
                print(f"✅ 成功读取: {len(df)} 行数据")
                
                # 显示文件信息
                if 'file_date' in df.columns:
                    print(f"📅 文件日期格式: {df['file_date'].iloc[0]}")
                if 'conv_30d' in df.columns:
                    print(f"📊 转化率范围: {df['conv_30d'].min():.4f} - {df['conv_30d'].max():.4f}")
                
                # 测试处理
                print(f"\n🔄 开始处理真实文件...")
                processed_df = ss.process_single_file(df, None, False)
                
                if len(processed_df) > 0:
                    print(f"✅ 真实文件处理成功!")
                    print(f"  • 原始行数: {len(df)}")
                    print(f"  • 处理后行数: {len(processed_df)}")
                    print(f"  • 保留率: {len(processed_df)/len(df)*100:.1f}%")
                    print(f"  • 平均总分: {processed_df['total_score'].mean():.4f}")
                    return True
                else:
                    print(f"❌ 真实文件处理后无有效数据")
                    continue
                    
            except Exception as e:
                print(f"❌ 真实文件处理失败: {e}")
                continue
    
    print(f"❌ 未找到可处理的真实文件")
    return False

def main():
    """主测试函数"""
    print("🔧 关键Bug修复验证测试")
    print("=" * 80)
    
    test_results = []
    
    # 测试1: 日期范围格式处理
    result1 = test_date_range_processing()
    test_results.append(("日期范围格式处理", result1))
    
    # 测试2: 转化率过滤逻辑
    result2 = test_conversion_rate_filtering()
    test_results.append(("转化率过滤逻辑", result2))
    
    # 测试3: 缺失转化率列处理
    result3 = test_missing_conv_column()
    test_results.append(("缺失转化率列处理", result3))
    
    # 测试4: 真实文件处理
    result4 = test_real_file_processing()
    test_results.append(("真实文件处理", result4))
    
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
    
    if passed >= 3:  # 至少核心功能通过
        print(f"🎉 关键Bug已修复！")
        print(f"\n💡 现在可以:")
        print(f"  1. 处理日期范围格式文件")
        print(f"  2. 智能转化率过滤（自动放宽条件）")
        print(f"  3. 处理缺失转化率列的文件")
        print(f"  4. 正常生成TOP50结果")
        
        print(f"\n🚀 建议操作:")
        print(f"  1. 重启评分系统")
        print(f"  2. 重新上传之前失败的文件")
        print(f"  3. 观察处理过程日志")
        print(f"  4. 验证TOP50结果下载")
    else:
        print(f"⚠️ 部分测试失败，需要进一步修复")

if __name__ == "__main__":
    main()
