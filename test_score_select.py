#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
score_select.py 测试脚本
用于验证数据过滤评分系统的功能
"""

import os
import subprocess
import pandas as pd
from datetime import datetime

def create_test_directories():
    """创建测试目录"""
    test_input_dir = "test_input"
    test_output_dir = "test_output"
    
    os.makedirs(test_input_dir, exist_ok=True)
    os.makedirs(test_output_dir, exist_ok=True)
    
    return test_input_dir, test_output_dir

def copy_test_data(input_dir):
    """复制测试数据到输入目录"""
    import shutil
    if os.path.exists("test_data_sample.csv"):
        shutil.copy("test_data_sample.csv", os.path.join(input_dir, "sample_data.csv"))
        print("✅ 测试数据已复制到输入目录")
        return True
    else:
        print("❌ 未找到测试数据文件 test_data_sample.csv")
        return False

def run_score_select(input_dir, output_dir):
    """运行score_select.py脚本"""
    try:
        cmd = ["python", "score_select.py", "--in", input_dir, "--out", output_dir]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        print("🚀 脚本执行结果:")
        print("=" * 50)
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ 错误信息:")
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 脚本执行失败: {e}")
        return False

def analyze_results(output_dir):
    """分析输出结果"""
    output_file = os.path.join(output_dir, "top50_combined.csv")
    
    if not os.path.exists(output_file):
        print("❌ 未找到输出文件")
        return False
    
    try:
        df = pd.read_csv(output_file)
        print(f"\n📊 结果分析:")
        print("=" * 50)
        print(f"输出行数: {len(df)}")
        print(f"输出列数: {len(df.columns)}")
        print(f"包含total_score列: {'total_score' in df.columns}")
        
        if 'total_score' in df.columns:
            print(f"最高分: {df['total_score'].max():.4f}")
            print(f"最低分: {df['total_score'].min():.4f}")
            print(f"平均分: {df['total_score'].mean():.4f}")
            
            # 检查是否按分数降序排列
            is_sorted = df['total_score'].is_monotonic_decreasing
            print(f"按分数降序排列: {is_sorted}")
        
        print(f"\n📋 输出列名:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")
        
        print(f"\n🏆 TOP 5 商品:")
        top5 = df.head(5)[['product_name', 'total_score']] if 'product_name' in df.columns else df.head(5)
        print(top5.to_string(index=False))
        
        # 检查是否有低转化率商品被过滤
        if 'product_name' in df.columns:
            low_conv_filtered = '低转化率商品' not in df['product_name'].values
            print(f"\n🔍 低转化率商品已过滤: {low_conv_filtered}")
            
            # 检查大商家惩罚
            big_merchant_exists = '大商家商品' in df['product_name'].values
            if big_merchant_exists:
                big_merchant_score = df[df['product_name'] == '大商家商品']['total_score'].iloc[0]
                print(f"大商家商品得分: {big_merchant_score:.4f} (应该受到惩罚)")
        
        return True
        
    except Exception as e:
        print(f"❌ 结果分析失败: {e}")
        return False

def test_holiday_mode():
    """测试节日模式"""
    print(f"\n🎄 节日模式测试:")
    print("=" * 50)
    
    # 导入score_select模块进行单元测试
    try:
        import score_select
        
        # 测试节日距离计算
        test_dates = [
            "2024-12-20",  # 距离圣诞节5天
            "2024-09-01",  # 距离中秋节14天
            "2024-08-01",  # 距离中秋节45天
            "2024-07-01",  # 距离中秋节75天
        ]
        
        for date in test_dates:
            days = score_select.calculate_days_to_next_holiday(date)
            is_holiday = days <= 45
            print(f"日期 {date}: 距离下一节日 {days} 天, 节日模式: {is_holiday}")
        
        # 测试权重调整
        base_weights = score_select.get_base_weights()
        holiday_weights = score_select.adjust_holiday_weights(base_weights, True)
        
        print(f"\n权重调整测试:")
        print(f"基础sales_7d权重: {base_weights['sales_7d_score']:.3f}")
        print(f"节日sales_7d权重: {holiday_weights['sales_7d_score']:.3f}")
        print(f"权重总和: {sum(holiday_weights.values()):.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ 节日模式测试失败: {e}")
        return False

def cleanup_test_files():
    """清理测试文件"""
    import shutil
    
    test_dirs = ["test_input", "test_output"]
    for dir_name in test_dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🧹 已清理测试目录: {dir_name}")

def main():
    """主测试函数"""
    print("🧪 score_select.py 功能测试")
    print("=" * 60)
    
    # 检查主脚本是否存在
    if not os.path.exists("score_select.py"):
        print("❌ 未找到 score_select.py 文件")
        return
    
    # 创建测试环境
    input_dir, output_dir = create_test_directories()
    
    # 复制测试数据
    if not copy_test_data(input_dir):
        return
    
    # 运行主脚本
    print(f"\n🚀 运行 score_select.py")
    print("=" * 50)
    success = run_score_select(input_dir, output_dir)
    
    if success:
        # 分析结果
        analyze_results(output_dir)
        
        # 测试节日模式
        test_holiday_mode()
        
        print(f"\n✅ 测试完成！所有功能正常")
    else:
        print(f"\n❌ 测试失败！请检查脚本")
    
    # 询问是否清理测试文件
    cleanup = input(f"\n是否清理测试文件? (y/n): ").lower().strip()
    if cleanup in ['y', 'yes', '是']:
        cleanup_test_files()
    else:
        print(f"测试文件保留在: {input_dir}, {output_dir}")

if __name__ == "__main__":
    main()
