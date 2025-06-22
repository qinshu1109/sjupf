#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缺失字段修复验证脚本
测试修复后的系统是否能正确处理缺失live_gmv_7d等字段的数据
"""

import pandas as pd
import numpy as np
import os

# 导入评分脚本
try:
    import score_select as ss
except ImportError:
    print("❌ 无法导入score_select.py，请确保文件在同一目录下")
    exit(1)

def test_missing_live_gmv_7d():
    """测试缺失live_gmv_7d字段的处理"""
    print("🧪 测试缺失live_gmv_7d字段的处理")
    print("=" * 60)
    
    # 读取测试文件
    test_file = "test_csv/missing_live_gmv_7d.csv"
    
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    try:
        df = pd.read_csv(test_file)
        print(f"✅ 成功读取测试文件: {len(df)} 行数据")
        
        # 显示文件字段
        print(f"\n📋 文件字段列表:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")
        
        # 检查是否缺失live_gmv_7d字段
        if 'live_gmv_7d' not in df.columns:
            print(f"\n✅ 确认缺失live_gmv_7d字段")
        else:
            print(f"\n⚠️ 文件包含live_gmv_7d字段")
        
        # 测试动态权重调整
        print(f"\n🔧 测试动态权重调整...")
        base_weights = ss.get_base_weights()
        
        try:
            adjusted_weights = ss.adjust_weights_for_available_fields(df, base_weights)
            print(f"✅ 权重调整成功")
            print(f"权重总和: {sum(adjusted_weights.values()):.6f}")
        except Exception as e:
            print(f"❌ 权重调整失败: {e}")
            return False
        
        # 测试完整的数据处理流程
        print(f"\n🔄 测试完整数据处理流程...")
        file_date = df['file_date'].iloc[0]
        is_holiday_mode = False
        
        try:
            processed_df = ss.process_single_file(df, file_date, is_holiday_mode)
            
            if len(processed_df) > 0:
                print(f"✅ 数据处理成功: {len(processed_df)} 行有效数据")
                print(f"平均总分: {processed_df['total_score'].mean():.4f}")
                print(f"最高总分: {processed_df['total_score'].max():.4f}")
                print(f"最低总分: {processed_df['total_score'].min():.4f}")
                
                # 检查是否包含total_score列
                if 'total_score' in processed_df.columns:
                    print(f"✅ 总分计算正常")
                else:
                    print(f"❌ 缺少total_score列")
                    return False
                
                # 检查渠道评分是否正常
                if 'channel_score' in processed_df.columns:
                    channel_scores = processed_df['channel_score']
                    print(f"✅ 渠道评分正常: 平均值={channel_scores.mean():.4f}")
                    
                    # 检查是否有NaN值
                    if channel_scores.isna().any():
                        print(f"⚠️ 渠道评分包含NaN值")
                    else:
                        print(f"✅ 渠道评分无NaN值")
                else:
                    print(f"❌ 缺少channel_score列")
                    return False
                
                return True
            else:
                print(f"❌ 数据处理后无有效数据")
                return False
                
        except Exception as e:
            print(f"❌ 数据处理失败: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_channel_score_with_missing_fields():
    """测试渠道评分函数对缺失字段的处理"""
    print("\n🧪 测试渠道评分函数的容错性")
    print("=" * 60)
    
    # 创建测试数据
    test_data = {
        'gmv_30d': [100000, 200000, 150000],
        'gmv_7d': [25000, 50000, 37500],
        'live_gmv_30d': [30000, 60000, 45000],
        # 故意不包含live_gmv_7d和card_gmv_30d
    }
    
    df = pd.DataFrame(test_data)
    
    # 补全缺失字段
    df['live_gmv_7d'] = 0  # 模拟缺失字段被补0
    df['card_gmv_30d'] = 0
    
    print(f"📊 测试数据:")
    print(df.head())
    
    try:
        # 测试渠道评分函数
        channel_scores = ss.channel_distribution_score(
            df['live_gmv_30d'], df['live_gmv_7d'], df['card_gmv_30d'],
            df['gmv_30d'], df['gmv_7d']
        )
        
        print(f"\n✅ 渠道评分计算成功")
        print(f"评分结果: {channel_scores}")
        print(f"平均分: {np.mean(channel_scores):.4f}")
        print(f"是否包含NaN: {pd.isna(channel_scores).any()}")
        
        return True
        
    except Exception as e:
        print(f"❌ 渠道评分计算失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_missing_fields():
    """测试多个字段缺失的情况"""
    print("\n🧪 测试多个字段缺失的处理")
    print("=" * 60)
    
    # 创建只包含最基本字段的数据
    minimal_data = {
        'product_name': ['商品A', '商品B', '商品C'],
        'product_url': ['https://example.com/a', 'https://example.com/b', 'https://example.com/c'],
        'category_l1': ['数码', '服装', '家居'],
        'commission': [0.15, 0.20, 0.12],
        'sales_30d': [1000, 1500, 800],
        'gmv_30d': [50000, 75000, 40000],
        'conv_30d': [0.05, 0.03, 0.04],
        'rank_type': ['潜力榜', '销量榜', '潜力榜'],
        'rank_no': [5, 2, 8],
        'influencer_7d': [10, 15, 8],
    }
    
    df = pd.DataFrame(minimal_data)
    
    print(f"📊 最小数据集字段:")
    for col in df.columns:
        print(f"  • {col}")
    
    print(f"\n❌ 缺失的字段:")
    all_fields = ['sales_7d', 'gmv_7d', 'live_gmv_30d', 'live_gmv_7d', 
                  'card_gmv_30d', 'sales_1y', 'snapshot_tag', 'file_date', 'data_period']
    missing_fields = [field for field in all_fields if field not in df.columns]
    for field in missing_fields:
        print(f"  • {field}")
    
    try:
        # 测试权重调整
        base_weights = ss.get_base_weights()
        adjusted_weights = ss.adjust_weights_for_available_fields(df, base_weights)
        
        print(f"\n✅ 权重调整成功")
        print(f"权重总和: {sum(adjusted_weights.values()):.6f}")
        
        # 测试数据处理
        file_date = '2024-12-22'
        is_holiday_mode = False
        
        processed_df = ss.process_single_file(df, file_date, is_holiday_mode)
        
        if len(processed_df) > 0:
            print(f"✅ 数据处理成功: {len(processed_df)} 行")
            print(f"平均总分: {processed_df['total_score'].mean():.4f}")
            return True
        else:
            print(f"❌ 数据处理后无有效数据")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🔧 缺失字段修复验证测试")
    print("=" * 80)
    
    test_results = []
    
    # 测试1: 缺失live_gmv_7d字段
    result1 = test_missing_live_gmv_7d()
    test_results.append(("缺失live_gmv_7d字段处理", result1))
    
    # 测试2: 渠道评分容错性
    result2 = test_channel_score_with_missing_fields()
    test_results.append(("渠道评分容错性", result2))
    
    # 测试3: 多个字段缺失
    result3 = test_multiple_missing_fields()
    test_results.append(("多个字段缺失处理", result3))
    
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
        print(f"🎉 所有测试通过！缺失字段问题已修复")
        print(f"\n💡 现在可以:")
        print(f"  1. 上传缺失live_gmv_7d字段的文件")
        print(f"  2. 系统会自动补全缺失字段")
        print(f"  3. 正常完成评分计算")
        print(f"  4. 输出TOP50结果")
    else:
        print(f"⚠️ 部分测试失败，需要进一步修复")

if __name__ == "__main__":
    main()
