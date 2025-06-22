#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音电商数据清洗工具
专业的Excel数据标准化处理应用

技术栈：Streamlit + pandas + openpyxl
作者：数据清洗工程师
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import zipfile
import tempfile
import re
from io import BytesIO
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import traceback

# 页面配置
st.set_page_config(
    page_title="抖音数据清洗工具",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 标准字段定义
STANDARD_FIELDS = {
    'product_name': '商品名称',
    'product_url': '商品链接',
    'category_l1': '一级分类',
    'commission': '佣金比例',
    'sales_7d': '7天销量',
    'gmv_7d': '7天GMV',
    'sales_30d': '30天销量',
    'gmv_30d': '30天GMV',
    'live_gmv_30d': '30天直播GMV',
    'card_gmv_30d': '30天商品卡GMV',
    'sales_1y': '1年销量',
    'conv_30d': '30天转化率',
    'rank_type': '榜单类型',
    'rank_no': '排名',
    'influencer_7d': '7天带货达人',
    'snapshot_tag': '数据快照标签',
    'source_table': '数据来源表',
    'file_date': '文件日期',
    'data_period': '数据周期'
}

# 字段别名映射
FIELD_ALIASES = {
    'product_name': ['商品', '商品名称', '产品名', '商品标题', '名称'],
    'product_url': ['商品链接', '抖音商品链接', '链接', 'URL'],
    'category_l1': ['商品分类', '分类', '一级分类', '类目'],
    'commission': ['佣金比例', '佣金', '提成比例', '分成'],
    'sales_7d': ['周销量', '近7天销量', '7天销量', '7日销量'],
    'gmv_7d': ['周销售额', '近7天销售额', '7天GMV', '7日GMV'],
    'sales_30d': ['近30天销量', '30天销量', '月销量'],
    'gmv_30d': ['近30天销售额', '30天销售额', '月销售额'],
    'live_gmv_30d': ['30天直播GMV', '直播GMV', '直播销售额', '近30天直播销售额'],
    'card_gmv_30d': ['30天商品卡GMV', '商品卡GMV', '商品卡销售额', '近30天商品卡销售额'],  # 修复：添加缺失的字段映射
    'sales_1y': ['1年销量', '近1年销量', '年销量', '1年销售量'],  # 修复：添加缺失的字段映射
    'conv_30d': ['30天转化率', '转化率', '转换率'],
    'rank_no': ['排名', '排行', '名次'],
    'influencer_7d': ['周带货达人', '关联达人', '带货达人', '达人']
}


def numeric_normalizer(df: pd.DataFrame) -> pd.DataFrame:
    """
    数值格式标准化处理函数

    处理各种数值格式并转换为标准数值：
    - 区间值："7.5w-10w" → 87500 (取中位数)
    - 百分比："20%" → 0.2
    - 中文数值："1.2万" → 12000
    - 空值标记："—"、"无数据" → NaN

    参数:
        df: 待处理的DataFrame

    返回:
        处理后的DataFrame
    """
    import re

    # 需要处理的数值字段
    numeric_fields = ['commission', 'sales_7d', 'gmv_7d', 'sales_30d', 'gmv_30d',
                     'live_gmv_30d', 'card_gmv_30d', 'sales_1y', 'conv_30d']

    df_processed = df.copy()

    for field in numeric_fields:
        if field not in df_processed.columns:
            continue

        # 创建新的Series用于存储处理结果
        processed_series = df_processed[field].copy()

        for idx in processed_series.index:
            val = str(processed_series.iloc[idx])

            # 跳过已经是NaN的值
            if val in ['nan', 'None', ''] or pd.isna(processed_series.iloc[idx]):
                processed_series.iloc[idx] = pd.NA
                continue

            # 处理空值标记
            if val in ['—', '无数据']:
                processed_series.iloc[idx] = pd.NA
                continue

            # 处理百分比格式 (如: "20%" → 0.2)
            if '%' in val:
                try:
                    num_val = float(val.replace('%', '').replace(',', ''))
                    processed_series.iloc[idx] = num_val / 100
                    continue
                except:
                    pass

            # 处理区间值 (如: "7.5w-10w" → 87500)
            if '-' in val and re.search(r'\d+\.?\d*[wW万千]?-\d+\.?\d*[wW万千]?', val):
                try:
                    numbers = re.findall(r'(\d+\.?\d*)([wW万千]?)', val)
                    if len(numbers) >= 2:
                        vals = []
                        for num, unit in numbers[:2]:
                            num_val = float(num)
                            if unit.lower() in ['w', '万']:
                                num_val *= 10000
                            elif unit in ['千']:
                                num_val *= 1000
                            vals.append(num_val)
                        processed_series.iloc[idx] = sum(vals) / 2
                        continue
                except:
                    pass

            # 处理中文数值单位 (如: "1.2万" → 12000)
            if re.search(r'\d+\.?\d*[万千wW]', val):
                try:
                    match = re.search(r'(\d+\.?\d*)([万千wW])', val)
                    if match:
                        num, unit = match.groups()
                        num_val = float(num)
                        if unit in ['万', 'w', 'W']:
                            num_val *= 10000
                        elif unit == '千':
                            num_val *= 1000
                        processed_series.iloc[idx] = num_val
                        continue
                except:
                    pass

            # 处理普通数值（清理逗号）
            try:
                clean_val = val.replace(',', '')
                processed_series.iloc[idx] = float(clean_val)
            except:
                # 无法转换的保持原值
                pass

        # 更新DataFrame
        df_processed[field] = processed_series

    return df_processed


def smart_csv_reader(uploaded_file, nrows=None) -> pd.DataFrame:
    """
    智能CSV文件读取器，自动检测分隔符和编码

    参数:
        uploaded_file: 上传的CSV文件
        nrows: 读取的行数，None表示读取全部

    返回:
        成功解析的DataFrame

    异常:
        抛出详细的CSV解析错误信息
    """
    # 常见的分隔符列表，按优先级排序
    separators = [',', ';', '\t', '|']
    # 常见的编码列表，按优先级排序
    encodings = ['utf-8', 'gbk', 'iso-8859-1', 'cp1252']

    # 重置文件指针
    uploaded_file.seek(0)

    # 首先检查文件是否为空
    file_content = uploaded_file.read()
    if len(file_content) == 0:
        raise Exception("CSV文件为空")

    # 重置文件指针
    uploaded_file.seek(0)

    best_result = None
    best_score = 0

    # 尝试不同的编码和分隔符组合
    for encoding in encodings:
        for separator in separators:
            try:
                uploaded_file.seek(0)  # 重置文件指针
                df = pd.read_csv(
                    uploaded_file,
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

            except Exception:
                continue  # 尝试下一个组合

    # 返回最佳结果
    if best_result is not None and best_score > 0:
        return best_result

    # 如果所有组合都失败，提供详细的错误信息
    raise Exception(
        "无法解析CSV文件。可能的原因：\n"
        "1. 文件分隔符不是常见格式（逗号、分号、制表符、竖线）\n"
        "2. 文件编码不被支持\n"
        "3. 文件格式损坏或包含特殊字符\n"
        "建议：请确保CSV文件使用逗号分隔，UTF-8编码保存"
    )


def clean_duplicate_columns(df: pd.DataFrame, context: str = "") -> pd.DataFrame:
    """
    清理DataFrame中的重复列名

    参数:
        df: 待清理的DataFrame
        context: 上下文信息，用于日志记录

    返回:
        清理后的DataFrame
    """
    if df.columns.duplicated().any():
        duplicated_cols = df.columns[df.columns.duplicated()].tolist()
        print(f"警告: {context} 发现重复列名 {duplicated_cols}，将保留第一个出现的列")

        # 去除重复列，保留第一个
        df_cleaned = df.loc[:, ~df.columns.duplicated()]

        print(f"去重前列数: {len(df.columns)}, 去重后列数: {len(df_cleaned.columns)}")
        return df_cleaned

    return df


def smart_field_mapping(columns: List[str]) -> Dict[str, str]:
    """
    智能字段映射：自动匹配原始字段名到标准字段名，防止重复映射

    参数:
        columns: 原始列名列表

    返回:
        映射字典 {原始字段名: 标准字段名}
    """
    mapping = {}
    used_std_fields = set()  # 跟踪已使用的标准字段

    # 第一轮：精确匹配（优先级最高）
    for std_field, aliases in FIELD_ALIASES.items():
        if std_field in used_std_fields:
            continue

        for col in columns:
            if col in aliases:
                mapping[col] = std_field
                used_std_fields.add(std_field)
                break

    # 第二轮：模糊匹配（优先级较低）
    for std_field, aliases in FIELD_ALIASES.items():
        if std_field in used_std_fields:
            continue

        for col in columns:
            if col in mapping:  # 跳过已映射的原始字段
                continue

            # 模糊匹配
            for alias in aliases:
                if alias in col or col in alias:
                    mapping[col] = std_field
                    used_std_fields.add(std_field)
                    break

            if std_field in used_std_fields:
                break

    return mapping


def extract_metadata_from_filename(filename: str) -> Dict[str, str]:
    """
    从文件名提取元数据信息，支持多种时间格式

    支持的时间格式：
    - 日期区间: YYYYMMDD-YYYYMMDD (如: 20250622-20250630)
    - 单日期: YYYYMMDD (如: 20250622)
    - 相对时间: 数字+时间单位 (如: 30d, 7d, 1y)

    参数:
        filename: 文件名

    返回:
        包含元数据的字典
    """
    file_date = '未知时间'
    data_period = '未知周期'

    # 1. 优先匹配日期区间格式 (YYYYMMDD-YYYYMMDD)
    date_range_pattern = r'(\d{8})-(\d{8})'
    date_range_match = re.search(date_range_pattern, filename)
    if date_range_match:
        start_date = date_range_match.group(1)
        end_date = date_range_match.group(2)
        # 格式化为可读的日期区间
        file_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}至{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
        # 计算天数差作为数据周期
        from datetime import datetime
        try:
            start = datetime.strptime(start_date, '%Y%m%d')
            end = datetime.strptime(end_date, '%Y%m%d')
            days_diff = (end - start).days + 1
            data_period = f"{days_diff}天"
        except:
            data_period = "区间周期"

    # 2. 匹配单日期格式 (YYYYMMDD)
    elif not date_range_match:
        single_date_pattern = r'(\d{8})'
        single_date_match = re.search(single_date_pattern, filename)
        if single_date_match:
            date_str = single_date_match.group(1)
            file_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            data_period = "单日数据"

    # 3. 匹配相对时间格式 (数字+时间单位)
    if file_date == '未知时间':
        relative_time_pattern = r'(\d+)([dmy])'
        relative_match = re.search(relative_time_pattern, filename.lower())
        if relative_match:
            number = relative_match.group(1)
            unit = relative_match.group(2)
            unit_map = {'d': '天', 'm': '月', 'y': '年'}
            data_period = f"{number}{unit_map.get(unit, '天')}"
            file_date = f"相对时间({data_period})"

    # 4. 特殊格式兼容 (保持向后兼容)
    if file_date == '未知时间':
        if '30d' in filename.lower():
            file_date = '相对时间(30天)'
            data_period = '30天'
        elif '7d' in filename.lower():
            file_date = '相对时间(7天)'
            data_period = '7天'
        elif '1y' in filename.lower():
            file_date = '相对时间(1年)'
            data_period = '1年'

    # 提取榜单类型
    rank_types = ['销量榜', '热推榜', '潜力榜', '持续好货榜', '同期榜']
    rank_type = '未知榜单'
    for rt in rank_types:
        if rt in filename:
            rank_type = rt
            break

    # 提取数据来源表
    source_table = filename.split('-')[0] if '-' in filename else filename.split('.')[0]

    return {
        'snapshot_tag': file_date,  # 保持向后兼容
        'rank_type': rank_type,
        'source_table': source_table,
        'file_date': file_date,
        'data_period': data_period
    }


def validate_file(uploaded_file) -> Tuple[bool, str]:
    """
    验证上传的文件，支持Excel和CSV格式

    参数:
        uploaded_file: Streamlit上传的文件对象

    返回:
        (是否有效, 错误信息)
    """
    if uploaded_file is None:
        return False, "文件为空"

    # 检查文件扩展名
    supported_extensions = ('.xlsx', '.xls', '.csv')
    if not uploaded_file.name.lower().endswith(supported_extensions):
        return False, f"不支持的文件格式: {uploaded_file.name}。支持的格式: Excel(.xlsx, .xls) 和 CSV(.csv)"

    # 检查文件大小 (50MB限制)
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > 50:
        return False, f"文件过大: {file_size_mb:.1f}MB (限制50MB)。建议压缩文件或分批处理"

    # 对CSV文件进行额外的格式检查
    if uploaded_file.name.lower().endswith('.csv'):
        try:
            # 尝试读取CSV文件的前几行进行格式验证
            uploaded_file.seek(0)
            test_df = smart_csv_reader(uploaded_file, nrows=1)
            if len(test_df.columns) == 0:
                return False, "CSV文件格式错误：无法识别列结构。请检查文件分隔符和编码"
        except Exception as e:
            return False, f"CSV文件格式验证失败：{str(e)}"
        finally:
            uploaded_file.seek(0)  # 重置文件指针

    # 检查文件名时间格式并提供建议
    filename = uploaded_file.name
    metadata = extract_metadata_from_filename(filename)
    if metadata['file_date'] == '未知时间':
        suggestion = "建议文件名包含时间信息，如: 销量榜-20250622-20250630.xlsx 或 数据-30d.csv"
        return True, f"提示: 未能从文件名提取时间信息。{suggestion}"

    return True, ""


def process_single_file(uploaded_file, field_mapping: Dict[str, str]) -> Dict:
    """
    处理单个数据文件，支持Excel和CSV格式

    参数:
        uploaded_file: 上传的文件
        field_mapping: 字段映射字典

    返回:
        处理结果字典
    """
    try:
        # 根据文件扩展名选择读取方式
        filename = uploaded_file.name.lower()
        if filename.endswith('.csv'):
            # 使用智能CSV读取器
            try:
                df = smart_csv_reader(uploaded_file)
            except Exception as e:
                # CSV文件读取的其他错误
                raise Exception(f"CSV文件读取失败: {str(e)}")
        else:
            # 读取Excel文件
            try:
                df = pd.read_excel(uploaded_file, engine='openpyxl', dtype=str)
            except Exception as e:
                # Excel文件读取错误
                raise Exception(f"Excel文件读取失败: {str(e)}")
        
        if df.empty:
            return {
                'success': False,
                'filename': uploaded_file.name,
                'error': '文件为空',
                'data': None
            }
        
        # 应用字段映射
        df_mapped = df.rename(columns=field_mapping)

        # 清理重复列名
        df_mapped = clean_duplicate_columns(df_mapped, "字段映射后")

        # 提取文件名元数据
        metadata = extract_metadata_from_filename(uploaded_file.name)

        # 添加派生字段，检查是否与现有列名冲突
        for field, value in metadata.items():
            if field not in df_mapped.columns:
                df_mapped[field] = value
            else:
                # 如果字段已存在，更新值（优先使用元数据）
                df_mapped[field] = value
        
        # 调用用户的数值标准化函数
        df_normalized = numeric_normalizer(df_mapped)

        # 清理数值标准化后的重复列名
        df_normalized = clean_duplicate_columns(df_normalized, "数值标准化后")

        # 确保所有标准字段都存在
        for std_field in STANDARD_FIELDS.keys():
            if std_field not in df_normalized.columns:
                df_normalized[std_field] = None

        # 清理添加标准字段后的重复列名
        df_normalized = clean_duplicate_columns(df_normalized, "添加标准字段后")

        # 只保留标准字段，确保列顺序一致
        available_fields = [field for field in STANDARD_FIELDS.keys() if field in df_normalized.columns]
        df_final = df_normalized[available_fields].copy()

        # 最终清理：确保没有重复列名
        df_final = clean_duplicate_columns(df_final, "最终输出")
        
        return {
            'success': True,
            'filename': uploaded_file.name,
            'data': df_final,
            'original_rows': len(df),
            'processed_rows': len(df_final),
            'mapped_fields': len(field_mapping),
            'final_columns': len(df_final.columns),
            'has_duplicates': False  # 经过处理后应该没有重复列
        }
        
    except Exception as e:
        return {
            'success': False,
            'filename': uploaded_file.name,
            'error': f"处理错误: {str(e)}",
            'data': None
        }


def create_download_zip(processed_results: List[Dict]) -> BytesIO:
    """
    创建包含所有处理结果的ZIP文件
    
    参数:
        processed_results: 处理结果列表
    
    返回:
        ZIP文件的BytesIO对象
    """
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for result in processed_results:
            if result['success'] and result['data'] is not None:
                # 生成输出文件名，支持CSV文件
                original_name = result['filename']
                clean_name = original_name.replace('.xlsx', '').replace('.xls', '').replace('.csv', '')
                output_filename = f"cleaned_{clean_name}.xlsx"

                # 确保数据没有重复列名
                data_to_save = result['data'].copy()
                if data_to_save.columns.duplicated().any():
                    print(f"警告: 在保存 {original_name} 时发现重复列名，正在去重")
                    data_to_save = data_to_save.loc[:, ~data_to_save.columns.duplicated()]

                # 将DataFrame保存到内存中的Excel文件
                excel_buffer = BytesIO()
                data_to_save.to_excel(excel_buffer, index=False, engine='openpyxl')
                excel_buffer.seek(0)

                # 添加到ZIP文件
                zip_file.writestr(output_filename, excel_buffer.getvalue())
    
    zip_buffer.seek(0)
    return zip_buffer


def render_sidebar():
    """渲染侧边栏控制区"""
    st.sidebar.title("🧹 数据清洗工具")
    st.sidebar.markdown("---")
    
    # 文件上传
    st.sidebar.subheader("📁 上传文件")
    uploaded_files = st.sidebar.file_uploader(
        "选择数据文件",
        type=['xlsx', 'xls', 'csv'],
        accept_multiple_files=True,
        help="支持Excel文件(.xlsx, .xls)和CSV文件(.csv)的批量上传"
    )
    
    # 字段映射预览
    if uploaded_files:
        st.sidebar.subheader("🔗 字段映射预览")
        
        # 分析第一个文件的字段
        first_file = uploaded_files[0]
        try:
            # 根据文件类型读取表头
            filename = first_file.name.lower()
            if filename.endswith('.csv'):
                # 使用智能CSV读取器读取表头
                sample_df = smart_csv_reader(first_file, nrows=0)
            else:
                # 读取Excel文件表头
                sample_df = pd.read_excel(first_file, nrows=0)

            auto_mapping = smart_field_mapping(sample_df.columns.tolist())

            # 显示时间信息提取预览
            metadata = extract_metadata_from_filename(first_file.name)

            if auto_mapping:
                st.sidebar.success(f"✅ 自动识别到 {len(auto_mapping)} 个字段")
                with st.sidebar.expander("查看映射详情"):
                    for raw, std in auto_mapping.items():
                        st.write(f"**{raw}** → {STANDARD_FIELDS[std]}")

                    # 显示时间信息提取结果
                    st.write("---")
                    st.write("**📅 时间信息提取:**")
                    st.write(f"• **文件日期**: {metadata['file_date']}")
                    st.write(f"• **数据周期**: {metadata['data_period']}")
                    st.write(f"• **榜单类型**: {metadata['rank_type']}")
            else:
                st.sidebar.warning("⚠️ 未能自动识别字段，请检查文件格式")

        except Exception as e:
            st.sidebar.error(f"❌ 文件预览失败: {str(e)}")
    
    return uploaded_files


def render_main_content(uploaded_files):
    """渲染主内容区"""
    st.title("🧹 抖音电商数据清洗工具")
    st.markdown("**专业的Excel数据标准化处理平台**")
    
    if not uploaded_files:
        # 显示使用说明
        st.info("👈 请在左侧上传Excel文件开始数据清洗")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 支持的标准字段")
            for i, (field, desc) in enumerate(STANDARD_FIELDS.items()):
                if i < len(STANDARD_FIELDS) // 2:
                    st.write(f"• **{desc}** (`{field}`)")
        
        with col2:
            st.subheader("📋 支持的标准字段（续）")
            for i, (field, desc) in enumerate(STANDARD_FIELDS.items()):
                if i >= len(STANDARD_FIELDS) // 2:
                    st.write(f"• **{desc}** (`{field}`)")
        
        st.subheader("🚀 功能特点")
        st.write("""
        - ✅ **多格式支持**：支持Excel(.xlsx, .xls)和CSV(.csv)文件
        - ✅ **智能字段映射**：自动识别和匹配19个标准字段
        - ✅ **智能时间提取**：支持多种文件名时间格式识别
        - ✅ **批量处理**：支持同时处理多个数据文件
        - ✅ **数值标准化**：处理百分比、区间值、单位转换
        - ✅ **元数据提取**：从文件名自动提取榜单类型和时间信息
        - ✅ **ZIP打包下载**：一键下载所有处理结果
        - ✅ **友好提示**：详细的处理进度和错误信息
        """)
        
        return
    
    # 显示文件信息
    st.subheader(f"📁 已上传 {len(uploaded_files)} 个文件")
    
    # 文件列表
    file_info = []
    total_size = 0
    
    for file in uploaded_files:
        is_valid, error_msg = validate_file(file)
        file_size_mb = file.size / (1024 * 1024)
        total_size += file_size_mb
        
        file_info.append({
            '文件名': file.name,
            '大小(MB)': f"{file_size_mb:.2f}",
            '状态': "✅ 有效" if is_valid else f"❌ {error_msg}"
        })
    
    # 显示文件信息表格
    df_files = pd.DataFrame(file_info)
    st.dataframe(df_files, use_container_width=True)
    
    # 大文件警告
    if total_size > 50:
        st.warning(f"⚠️ 总文件大小 {total_size:.1f}MB 较大，处理可能需要更多时间")
    
    # 开始处理按钮
    if st.button("🚀 开始清洗", type="primary", use_container_width=True):
        process_files(uploaded_files)


def process_files(uploaded_files):
    """处理文件的主要逻辑"""
    # 初始化进度显示
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 存储处理结果
    if 'processing_results' not in st.session_state:
        st.session_state.processing_results = []
    
    st.session_state.processing_results = []
    
    # 处理每个文件
    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"正在处理文件 {i+1}/{len(uploaded_files)}: {uploaded_file.name}")
        
        # 验证文件
        is_valid, error_msg = validate_file(uploaded_file)
        if not is_valid:
            st.session_state.processing_results.append({
                'success': False,
                'filename': uploaded_file.name,
                'error': error_msg,
                'data': None
            })
            continue
        
        # 获取字段映射
        try:
            # 根据文件类型选择正确的读取方式
            filename = uploaded_file.name.lower()
            if filename.endswith('.csv'):
                # 使用智能CSV读取器读取表头
                sample_df = smart_csv_reader(uploaded_file, nrows=0)
            else:
                # 读取Excel文件表头
                sample_df = pd.read_excel(uploaded_file, nrows=0)

            field_mapping = smart_field_mapping(sample_df.columns.tolist())
        except Exception as e:
            # 提供更详细的错误信息，区分文件类型
            file_type = "CSV" if uploaded_file.name.lower().endswith('.csv') else "Excel"
            st.session_state.processing_results.append({
                'success': False,
                'filename': uploaded_file.name,
                'error': f"读取{file_type}文件失败: {str(e)}",
                'data': None
            })
            continue
        
        # 处理文件
        result = process_single_file(uploaded_file, field_mapping)
        st.session_state.processing_results.append(result)
        
        # 更新进度
        progress_bar.progress((i + 1) / len(uploaded_files))
    
    # 处理完成
    status_text.text("✅ 处理完成！")
    
    # 显示处理结果
    show_processing_results()


def show_processing_results():
    """显示处理结果"""
    if 'processing_results' not in st.session_state or not st.session_state.processing_results:
        return
    
    results = st.session_state.processing_results
    
    # 统计信息
    successful_count = sum(1 for r in results if r['success'])
    failed_count = len(results) - successful_count

    # 计算时间信息提取成功率
    time_extraction_success = 0
    for r in results:
        if r['success'] and r.get('data') is not None:
            # 检查是否成功提取时间信息
            if 'file_date' in r['data'].columns:
                time_info = r['data']['file_date'].iloc[0] if len(r['data']) > 0 else '未知时间'
                if time_info != '未知时间':
                    time_extraction_success += 1

    time_extraction_rate = (time_extraction_success / successful_count * 100) if successful_count > 0 else 0

    st.subheader("📊 处理结果统计")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总文件数", len(results))
    with col2:
        st.metric("成功处理", successful_count, delta=None)
    with col3:
        st.metric("处理失败", failed_count, delta=None)
    with col4:
        st.metric("时间提取成功率", f"{time_extraction_rate:.1f}%", delta=None)
    
    # 详细结果
    if successful_count > 0:
        st.subheader("✅ 处理成功的文件")
        
        # 显示第一个成功文件的预览
        first_success = next(r for r in results if r['success'])
        if first_success['data'] is not None:
            st.write("**数据预览（前10行）：**")

            # 创建预览数据，突出显示时间字段
            preview_data = first_success['data'].head(10).copy()

            # 最终检查：确保预览数据没有重复列名
            if preview_data.columns.duplicated().any():
                st.warning("⚠️ 检测到重复列名，正在自动修复...")
                duplicated_cols = preview_data.columns[preview_data.columns.duplicated()].tolist()
                st.write(f"重复的列名: {duplicated_cols}")
                preview_data = clean_duplicate_columns(preview_data, "数据预览")
                st.success("✅ 重复列名已自动去除")

            # 如果存在时间字段，在列名前添加特殊标记
            if 'file_date' in preview_data.columns and 'data_period' in preview_data.columns:
                st.info("💡 **时间字段说明**: 📅 file_date(文件日期) 和 ⏱️ data_period(数据周期) 为自动提取的时间信息")

            # 显示列信息
            st.write(f"**列信息**: 共 {len(preview_data.columns)} 列")

            try:
                st.dataframe(preview_data, use_container_width=True)
            except Exception as e:
                st.error(f"数据预览显示失败: {str(e)}")
                st.write("**列名列表:**")
                st.write(list(preview_data.columns))

            # 显示时间提取详情
            if len(preview_data) > 0:
                st.write("**📅 时间信息提取详情：**")
                col1, col2 = st.columns(2)
                with col1:
                    file_date_value = preview_data['file_date'].iloc[0] if 'file_date' in preview_data.columns else '未提取'
                    st.write(f"• **文件日期**: {file_date_value}")
                with col2:
                    data_period_value = preview_data['data_period'].iloc[0] if 'data_period' in preview_data.columns else '未提取'
                    st.write(f"• **数据周期**: {data_period_value}")
        
        # 创建下载链接
        zip_data = create_download_zip([r for r in results if r['success']])
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cleaned_data_{timestamp}.zip"
        
        st.download_button(
            label="📥 下载所有结果 (ZIP)",
            data=zip_data,
            file_name=filename,
            mime="application/zip",
            type="primary",
            use_container_width=True
        )
    
    # 失败文件列表
    if failed_count > 0:
        st.subheader("❌ 处理失败的文件")
        failed_files = [r for r in results if not r['success']]
        
        for failed in failed_files:
            st.error(f"**{failed['filename']}**: {failed['error']}")


def main():
    """主应用入口"""
    # 渲染侧边栏并获取上传的文件
    uploaded_files = render_sidebar()
    
    # 渲染主内容区
    render_main_content(uploaded_files)
    
    # 页脚信息
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "🧹 抖音电商数据清洗工具 | 专业数据处理解决方案"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
