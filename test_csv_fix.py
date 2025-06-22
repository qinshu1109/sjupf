#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试CSV文件读取修复功能
"""

import pandas as pd
import os
from io import StringIO

def smart_csv_reader(file_path, nrows=None):
    """
    智能CSV文件读取器，自动检测分隔符和编码
    """
    # 常见的分隔符列表，按优先级排序
    separators = [',', ';', '\t', '|']
    # 常见的编码列表，按优先级排序
    encodings = ['utf-8', 'gbk', 'iso-8859-1', 'cp1252']

    # 首先检查文件是否为空
    if os.path.getsize(file_path) == 0:
        raise Exception("CSV文件为空")

    best_result = None
    best_score = 0
    best_encoding = None
    best_separator = None

    # 尝试不同的编码和分隔符组合
    for encoding in encodings:
        for separator in separators:
            try:
                df = pd.read_csv(
                    file_path,
                    sep=separator,
                    encoding=encoding,
                    dtype=str,
                    nrows=nrows
                )

                # 检查是否成功解析出列
                if len(df.columns) > 0:
                    # 计算解析质量分数
                    score = len(df.columns)  # 列数越多越好

                    # 检查列名质量
                    valid_columns = [col for col in df.columns if isinstance(col, str) and len(str(col).strip()) > 0]
                    if len(valid_columns) == 0:
                        continue

                    # 如果只有一列，检查是否包含其他分隔符（说明分隔符错误）
                    if len(df.columns) == 1:
                        first_col = str(df.columns[0])
                        other_seps = [s for s in separators if s != separator]
                        if any(sep in first_col for sep in other_seps):
                            score = 0  # 降低分数

                    # 如果有数据行，检查数据质量
                    if len(df) > 0 and nrows != 0:
                        # 检查第一行数据是否合理分隔
                        first_row = df.iloc[0]
                        non_empty_cells = sum(1 for cell in first_row if pd.notna(cell) and str(cell).strip())
                        score += non_empty_cells  # 非空单元格越多越好

                    # 更新最佳结果
                    if score > best_score:
                        best_score = score
                        best_result = df
                        best_encoding = encoding
                        best_separator = separator

            except Exception:
                continue  # 尝试下一个组合

    # 返回最佳结果
    if best_result is not None and best_score > 0:
        print(f"✅ 成功读取: {file_path}")
        print(f"   编码: {best_encoding}, 分隔符: '{best_separator}'")
        print(f"   列数: {len(best_result.columns)}, 行数: {len(best_result)}")
        print(f"   列名: {list(best_result.columns)[:3]}...")
        return best_result

    # 如果所有组合都失败，提供详细的错误信息
    raise Exception(
        f"无法解析CSV文件: {file_path}\n"
        "可能的原因：\n"
        "1. 文件分隔符不是常见格式（逗号、分号、制表符、竖线）\n"
        "2. 文件编码不被支持\n"
        "3. 文件格式损坏或包含特殊字符\n"
        "建议：请确保CSV文件使用逗号分隔，UTF-8编码保存"
    )

def test_csv_files():
    """测试不同格式的CSV文件"""
    test_files = [
        'test_csv/standard_comma_utf8.csv',
        'test_csv/semicolon_utf8.csv', 
        'test_csv/tab_separated.csv',
        'test_csv/comma_gbk.csv',
        'test_csv/empty_file.csv',
        'test_csv/header_only.csv',
        'test_csv/clean_商品库_20250427-20250526.csv'
    ]
    
    print("🧪 开始测试CSV文件读取修复功能\n")
    
    success_count = 0
    total_count = len(test_files)
    
    for file_path in test_files:
        print(f"📁 测试文件: {file_path}")
        try:
            df = smart_csv_reader(file_path)
            success_count += 1
            print()
        except Exception as e:
            print(f"❌ 读取失败: {str(e)}")
            print()
    
    print(f"📊 测试结果: {success_count}/{total_count} 个文件成功读取")
    print(f"成功率: {success_count/total_count*100:.1f}%")

if __name__ == "__main__":
    test_csv_files()
