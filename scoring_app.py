#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电商数据智能过滤评分系统 - Streamlit Web应用
基于score_select.py的Web界面版本
"""

import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 导入现有的评分脚本
try:
    import score_select as ss
except ImportError:
    st.error("❌ 无法导入score_select.py，请确保文件在同一目录下")
    st.stop()

def configure_page():
    """配置页面设置"""
    st.set_page_config(
        page_title="电商数据智能评分系统",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def display_header():
    """显示页面标题和说明"""
    st.title("🎯 电商数据智能过滤评分系统")
    st.markdown("""
    **功能说明**：通过8大评分算法和节日模式感知，从电商数据中智能筛选TOP50高价值商品
    
    **支持格式**：CSV、XLSX文件 | **输出**：TOP50商品排行榜 + 评分详情
    """)
    st.divider()

def create_sidebar():
    """创建侧边栏控件"""
    st.sidebar.header("📁 数据上传与配置")
    
    # 文件上传器
    uploaded_files = st.sidebar.file_uploader(
        "上传清洗后的数据文件",
        type=['csv', 'xlsx'],
        accept_multiple_files=True,
        help="支持同时上传多个CSV或XLSX文件"
    )
    
    # 节日模式开关
    holiday_mode = st.sidebar.checkbox(
        "🎄 节日加权 (Holiday Boost)",
        value=True,
        help="启用后将在距离节日45天内自动调整权重"
    )
    
    # 开始评分按钮
    start_scoring = st.sidebar.button(
        "🚀 开始评分",
        type="primary",
        use_container_width=True
    )
    
    # 显示算法说明
    with st.sidebar.expander("📊 评分算法说明"):
        st.markdown("""
        **8大评分维度**：
        - 📈 销量/GMV表现 (长尾截断)
        - 💰 佣金激励 (分段评分)
        - 👥 达人影响力 (余弦衰减)
        - 🏆 排名表现 (指数衰减)
        - 📊 增长潜力 (动态评估)
        - 🔄 渠道分布 (多元化)
        - ✅ 转化效率 (质量门槛)
        - 🎄 节日感知 (智能调权)
        """)
    
    return uploaded_files, holiday_mode, start_scoring

def read_uploaded_file(uploaded_file):
    """读取上传的文件"""
    try:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            # 尝试不同编码读取CSV
            content = uploaded_file.read()
            for encoding in ['utf-8', 'gbk', 'gb2312']:
                try:
                    df = pd.read_csv(io.StringIO(content.decode(encoding)))
                    break
                except:
                    continue
            else:
                df = pd.read_csv(io.StringIO(content.decode('utf-8', errors='ignore')))
        
        return df
    except Exception as e:
        st.error(f"❌ 读取文件 {uploaded_file.name} 失败: {str(e)}")
        return None

def validate_data_format(df, filename):
    """验证数据格式（支持动态字段检查）"""
    # 核心必需字段（绝对不能缺少）
    core_required_columns = [
        'product_name', 'product_url', 'category_l1', 'commission',
        'conv_30d', 'rank_type', 'rank_no', 'influencer_7d'
    ]

    # 销量/GMV字段组（至少需要一组完整的7天或30天数据）
    sales_gmv_7d = ['sales_7d', 'gmv_7d']
    sales_gmv_30d = ['sales_30d', 'gmv_30d']

    # 可选字段（缺失时会警告但不阻断处理）
    optional_columns = [
        'live_gmv_30d', 'live_gmv_7d', 'card_gmv_30d',
        'sales_1y', 'snapshot_tag', 'file_date', 'data_period'
    ]

    # 检查核心必需字段
    missing_core = [col for col in core_required_columns if col not in df.columns]
    if missing_core:
        st.error(f"❌ 文件 {filename} 缺少核心必需字段: {', '.join(missing_core)}")
        return False

    # 检查销量/GMV字段组
    has_7d_data = all(col in df.columns for col in sales_gmv_7d)
    has_30d_data = all(col in df.columns for col in sales_gmv_30d)

    if not has_7d_data and not has_30d_data:
        st.error(f"❌ 文件 {filename} 缺少销量/GMV数据：需要至少一组完整的7天或30天数据")
        return False

    # 检查可选字段并给出警告
    missing_optional = [col for col in optional_columns if col not in df.columns]
    if missing_optional:
        st.warning(f"⚠️ 文件 {filename} 缺少可选字段: {', '.join(missing_optional)}（将使用默认值）")

    # 显示数据完整性信息
    if has_7d_data and has_30d_data:
        st.success(f"✅ 文件 {filename} 包含完整的7天和30天数据")
    elif has_30d_data:
        st.info(f"ℹ️ 文件 {filename} 仅包含30天数据，将启用动态权重调整")
    elif has_7d_data:
        st.info(f"ℹ️ 文件 {filename} 仅包含7天数据，将启用动态权重调整")

    return True

def preprocess_missing_fields(df):
    """预处理缺失字段，补全必要的数值列"""
    df = df.copy()

    # 定义所有可能需要的数值字段及其默认值
    numeric_fields_defaults = {
        'sales_7d': 0,
        'gmv_7d': 0,
        'sales_30d': 0,
        'gmv_30d': 0,
        'live_gmv_30d': 0,
        'live_gmv_7d': 0,
        'card_gmv_30d': 0,
        'sales_1y': 0,
        'rank_no': 999,  # 默认排名很低
    }

    # 定义文本字段及其默认值
    text_fields_defaults = {
        'snapshot_tag': '数据补全',
        'file_date': datetime.now().strftime('%Y-%m-%d'),
        'data_period': '30天'
    }

    # 补全缺失的数值字段
    for field, default_value in numeric_fields_defaults.items():
        if field not in df.columns:
            df[field] = default_value
            st.info(f"📝 补全缺失字段 {field}，使用默认值: {default_value}")

    # 补全缺失的文本字段
    for field, default_value in text_fields_defaults.items():
        if field not in df.columns:
            df[field] = default_value

    # 智能估算：基于现有数据补全相关字段
    if 'live_gmv_7d' not in df.columns or df['live_gmv_7d'].sum() == 0:
        if 'gmv_7d' in df.columns and df['gmv_7d'].sum() > 0:
            df['live_gmv_7d'] = df['gmv_7d'] * 0.3  # 假设30%来自直播
            st.info("📊 基于7天GMV估算live_gmv_7d（30%比例）")
        elif 'live_gmv_30d' in df.columns and df['live_gmv_30d'].sum() > 0:
            df['live_gmv_7d'] = df['live_gmv_30d'] * 0.23  # 7/30 ≈ 0.23
            st.info("📊 基于30天直播GMV估算live_gmv_7d")

    if 'card_gmv_30d' not in df.columns or df['card_gmv_30d'].sum() == 0:
        if 'gmv_30d' in df.columns and df['gmv_30d'].sum() > 0:
            df['card_gmv_30d'] = df['gmv_30d'] * 0.2  # 假设20%来自商品卡
            st.info("📊 基于30天GMV估算card_gmv_30d（20%比例）")

    if 'sales_1y' not in df.columns or df['sales_1y'].sum() == 0:
        if 'sales_30d' in df.columns and df['sales_30d'].sum() > 0:
            df['sales_1y'] = df['sales_30d'] * 12
            st.info("📊 基于30天销量估算年销量")
        elif 'sales_7d' in df.columns and df['sales_7d'].sum() > 0:
            df['sales_1y'] = df['sales_7d'] * 52
            st.info("📊 基于7天销量估算年销量")

    return df

def score_dataframe(df, holiday_mode=True):
    """对DataFrame进行评分处理（支持缺失字段）"""
    try:
        # 数据预处理：补全缺失的数值字段
        df = preprocess_missing_fields(df)

        # 处理数据（日期解析和节日模式检测在process_single_file内部完成）
        processed_df = ss.process_single_file(df, None, False)

        if len(processed_df) == 0:
            return processed_df, False, 999

        # 从处理后的数据中获取节日模式信息（通过重新解析日期）
        if 'file_date' in df.columns and len(df) > 0:
            raw_file_date = df['file_date'].iloc[0]
            parsed_file_date = ss.parse_file_date(raw_file_date)
            days_to_holiday = ss.calculate_days_to_next_holiday(parsed_file_date)
            is_holiday_mode = holiday_mode and days_to_holiday <= 45
        else:
            days_to_holiday = 999
            is_holiday_mode = False

        return processed_df, is_holiday_mode, days_to_holiday

    except Exception as e:
        st.error(f"❌ 数据评分处理失败: {str(e)}")
        return pd.DataFrame(), False, 999

def process_files(uploaded_files, holiday_mode):
    """处理上传的文件"""
    if not uploaded_files:
        st.warning("⚠️ 请先上传数据文件")
        return None
    
    all_results = []
    total_original_rows = 0
    total_processed_rows = 0
    holiday_files = 0
    
    # 创建进度条
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, uploaded_file in enumerate(uploaded_files):
        # 更新进度
        progress = (i + 1) / len(uploaded_files)
        progress_bar.progress(progress)
        status_text.text(f"正在处理: {uploaded_file.name} ({i+1}/{len(uploaded_files)})")
        
        # 读取文件
        df = read_uploaded_file(uploaded_file)
        if df is None:
            continue
        
        # 验证格式
        if not validate_data_format(df, uploaded_file.name):
            continue
        
        original_rows = len(df)
        total_original_rows += original_rows
        
        # 评分处理
        processed_df, is_holiday_mode, days_to_holiday = score_dataframe(df, holiday_mode)
        
        if len(processed_df) > 0:
            all_results.append(processed_df)
            total_processed_rows += len(processed_df)
            
            if is_holiday_mode:
                holiday_files += 1
                st.success(f"✅ {uploaded_file.name}: {len(processed_df)}/{original_rows} 行有效 (节日模式: 距离下一节日 {days_to_holiday} 天)")
            else:
                st.info(f"ℹ️ {uploaded_file.name}: {len(processed_df)}/{original_rows} 行有效 (标准模式)")
        else:
            st.warning(f"⚠️ {uploaded_file.name}: 处理后无有效数据")
    
    # 清除进度显示
    progress_bar.empty()
    status_text.empty()
    
    if not all_results:
        st.error("❌ 没有有效数据可处理")
        return None
    
    # 合并结果
    combined_df = pd.concat(all_results, ignore_index=True)
    
    # 去重和排序
    before_dedup = len(combined_df)
    combined_df = combined_df.drop_duplicates(subset=['product_url'], keep='first')
    after_dedup = len(combined_df)
    
    # 取TOP50
    top50_df = combined_df.nlargest(50, 'total_score')
    
    # 保持原字段结构
    original_cols = [
        'product_name', 'product_url', 'category_l1', 'commission',
        'sales_7d', 'gmv_7d', 'sales_30d', 'gmv_30d',
        'live_gmv_30d', 'live_gmv_7d', 'card_gmv_30d',
        'sales_1y', 'conv_30d', 'rank_type', 'rank_no', 
        'influencer_7d', 'snapshot_tag', 'file_date', 'data_period'
    ]
    
    output_cols = [col for col in original_cols if col in top50_df.columns] + ['total_score']
    top50_df = top50_df[output_cols]
    
    # 显示处理统计
    st.success(f"""
    📊 **处理完成统计**
    - 处理文件数: {len(uploaded_files)}
    - 节日模式文件: {holiday_files}
    - 原始数据行数: {total_original_rows:,}
    - 有效数据行数: {total_processed_rows:,}
    - 去重前: {before_dedup:,} → 去重后: {after_dedup:,}
    - 最终TOP50商品已生成
    """)
    
    return top50_df

def display_results(top50_df):
    """显示结果"""
    if top50_df is None or len(top50_df) == 0:
        return
    
    st.header("🏆 TOP50 商品排行榜")
    
    # 显示关键统计
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("商品数量", len(top50_df))
    with col2:
        st.metric("最高评分", f"{top50_df['total_score'].max():.4f}")
    with col3:
        st.metric("平均评分", f"{top50_df['total_score'].mean():.4f}")
    with col4:
        st.metric("最低评分", f"{top50_df['total_score'].min():.4f}")
    
    # 显示数据表
    st.dataframe(
        top50_df,
        use_container_width=True,
        height=400,
        column_config={
            "total_score": st.column_config.NumberColumn(
                "总评分",
                help="综合8大维度的加权评分",
                format="%.4f"
            ),
            "commission": st.column_config.NumberColumn(
                "佣金率",
                format="%.3f"
            ),
            "conv_30d": st.column_config.NumberColumn(
                "转化率",
                format="%.3f"
            )
        }
    )
    
    # 下载按钮
    csv_data = top50_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 下载TOP50结果 (CSV)",
        data=csv_data,
        file_name=f"top50_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

def main():
    """主函数"""
    configure_page()
    display_header()
    
    # 创建侧边栏
    uploaded_files, holiday_mode, start_scoring = create_sidebar()
    
    # 主要处理逻辑
    if start_scoring:
        with st.spinner("🔄 正在处理数据，请稍候..."):
            try:
                top50_df = process_files(uploaded_files, holiday_mode)
                if top50_df is not None:
                    st.session_state['results'] = top50_df
            except Exception as e:
                st.error(f"❌ 处理过程中发生错误: {str(e)}")
    
    # 显示结果
    if 'results' in st.session_state:
        display_results(st.session_state['results'])
    else:
        # 显示使用说明
        st.info("""
        ### 📋 使用说明
        
        1. **上传数据**: 在左侧上传一个或多个清洗后的CSV/XLSX文件
        2. **配置选项**: 选择是否启用节日加权模式
        3. **开始评分**: 点击"开始评分"按钮处理数据
        4. **查看结果**: 系统将显示TOP50商品排行榜
        5. **下载结果**: 可下载CSV格式的评分结果
        
        **数据要求**: 文件需包含19个标准字段，包括商品信息、销量数据、GMV数据等
        """)

if __name__ == "__main__":
    main()
