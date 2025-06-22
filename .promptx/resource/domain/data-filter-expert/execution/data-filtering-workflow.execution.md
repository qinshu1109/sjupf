<execution>
  <constraint>
    ## 技术约束条件
    - **依赖限制**：仅允许使用pandas + numpy，不得引入其他第三方库
    - **文件结构**：必须是单文件脚本score_select.py，不得拆分多个文件
    - **函数规模**：每个函数代码行数≤40行，保持简洁性
    - **命令行接口**：必须支持--in和--out参数，标准化命令行调用
    - **内存限制**：需要考虑大文件处理的内存效率
    - **编码兼容**：支持中文字符，确保跨平台兼容性
  </constraint>
  
  <rule>
    ## 强制执行规则
    - **数据完整性**：输出必须保持原17字段+total_score，不得丢失数据
    - **去重策略**：严格按product_url去重，确保结果唯一性
    - **排序规则**：必须按total_score降序排列，取TOP50
    - **节日检测**：必须自动检测节日模式，无需人工干预
    - **权重平衡**：权重调整后总和必须=1，保持评分体系平衡
    - **异常处理**：conv_30d<0.02的行必须完全淘汰
    - **文件命名**：输出文件必须按top50_{stem}.csv格式命名
    - **中文注释**：所有函数必须包含中文docstring说明
  </rule>
  
  <guideline>
    ## 实施指导原则
    - **模块化设计**：将复杂逻辑拆分为独立的评分函数
    - **向量化优先**：优先使用pandas向量化操作提升性能
    - **防御性编程**：添加必要的数据验证和异常处理
    - **可读性优先**：代码结构清晰，变量命名语义化
    - **性能平衡**：在功能完整性和执行效率间找到平衡
    - **测试友好**：设计便于测试和调试的代码结构
  </guideline>
  
  <process>
    ## 数据过滤完整工作流程
    
    ### Step 1: 环境准备与参数解析
    ```python
    # 命令行参数配置
    parser = argparse.ArgumentParser(description='电商数据智能过滤评分系统')
    parser.add_argument('--in', dest='input_dir', required=True, help='输入清洗数据目录')
    parser.add_argument('--out', dest='output_dir', required=True, help='输出TOP50结果目录')
    ```
    
    ### Step 2: 数据读取与预处理
    ```mermaid
    flowchart TD
        A[扫描输入目录] --> B[识别CSV/XLSX文件]
        B --> C[逐文件读取]
        C --> D[数据类型转换]
        D --> E[缺失值处理]
        E --> F[异常值检测]
        F --> G[数据验证]
    ```
    
    ### Step 3: 多维度评分计算
    ```mermaid
    graph LR
        A[原始数据] --> B[销量/GMV截断]
        A --> C[Commission分段]
        A --> D[达人余弦衰减]
        A --> E[排名指数衰减]
        A --> F[增长潜力计算]
        A --> G[渠道分布评分]
        A --> H[转化率过滤]
        
        B --> I[标准化得分]
        C --> I
        D --> I
        E --> I
        F --> I
        G --> I
        H --> I
    ```
    
    ### Step 4: 节日模式感知
    ```python
    def detect_holiday_mode(file_date):
        """检测是否启用节日模式"""
        holidays = [
            (1, 1),   # 元旦
            (2, 14),  # 情人节  
            (3, 8),   # 妇女节
            (6, 1),   # 儿童节
            (9, 15),  # 中秋
            (10, 1),  # 国庆
            (12, 25)  # 圣诞
        ]
        # 计算距离下一节日天数
        # 如果 <= 45天，返回True
    ```
    
    ### Step 5: 权重动态调整
    ```mermaid
    graph TD
        A[检测节日模式] --> B{距离节日≤45天?}
        B -->|是| C[启用节日模式]
        B -->|否| D[使用标准权重]
        
        C --> E[sales_7d权重+0.02]
        C --> F[销量榜基础分+0.02]
        C --> G[其他权重按比例缩放]
        
        D --> H[标准权重配置]
        
        E --> I[权重归一化]
        F --> I
        G --> I
        H --> I
    ```
    
    ### Step 6: 总分计算与排序
    ```python
    def calculate_total_score(df, weights, holiday_mode=False):
        """计算加权总分"""
        # 应用权重调整
        if holiday_mode:
            weights = adjust_holiday_weights(weights)
        
        # 加权求和
        total_score = sum(df[col] * weight for col, weight in weights.items())
        return total_score
    ```
    
    ### Step 7: 结果输出与验证
    ```mermaid
    flowchart LR
        A[总分排序] --> B[TOP50筛选]
        B --> C[按product_url去重]
        C --> D[保持17字段+total_score]
        D --> E[输出CSV文件]
        E --> F[打印处理统计]
    ```
    
    ## 核心函数设计模板
    
    ### 评分函数标准模板
    ```python
    def score_dimension_name(df):
        """
        维度评分函数
        
        Args:
            df: 输入数据DataFrame
            
        Returns:
            Series: 该维度的标准化得分[0,1]
        """
        # 数据预处理
        # 评分算法实现  
        # 标准化处理
        # 返回得分
        pass
    ```
    
    ### 权重管理函数
    ```python
    def get_base_weights():
        """获取基础权重配置"""
        return {
            'sales_7d': 0.15,
            'sales_30d': 0.12, 
            'gmv_7d': 0.10,
            'gmv_30d': 0.08,
            'commission': 0.15,
            'influencer_7d': 0.10,
            'rank_score': 0.12,
            'growth_score': 0.08,
            'channel_score': 0.05,
            'conv_score': 0.05
        }
    ```
    
    ### 节日模式权重调整
    ```python
    def adjust_holiday_weights(base_weights):
        """节日模式权重调整"""
        adjusted = base_weights.copy()
        adjusted['sales_7d'] += 0.02
        # 其他权重按比例缩放
        total_others = sum(v for k, v in adjusted.items() if k != 'sales_7d')
        scale_factor = (1 - adjusted['sales_7d']) / total_others
        for k in adjusted:
            if k != 'sales_7d':
                adjusted[k] *= scale_factor
        return adjusted
    ```
  </process>
  
  <criteria>
    ## 质量评价标准
    
    ### 功能完整性
    - ✅ 支持CSV/XLSX多格式读取
    - ✅ 实现8大评分规则算法
    - ✅ 自动节日模式检测和权重调整
    - ✅ TOP50筛选和去重处理
    - ✅ 标准化命令行接口
    
    ### 代码质量
    - ✅ 单文件架构，函数≤40行
    - ✅ 仅使用pandas+numpy依赖
    - ✅ 中文docstring完整
    - ✅ 变量命名清晰语义化
    - ✅ 异常处理完善
    
    ### 性能效率
    - ✅ 向量化计算优化
    - ✅ 内存使用合理
    - ✅ 大文件处理稳定
    - ✅ 执行时间可接受
    
    ### 业务准确性
    - ✅ 评分算法数学正确
    - ✅ 权重调整逻辑准确
    - ✅ 节日检测算法可靠
    - ✅ 输出格式符合要求
    - ✅ 去重和排序正确
    
    ### 可维护性
    - ✅ 代码结构清晰
    - ✅ 模块化程度高
    - ✅ 参数配置集中
    - ✅ 便于调试和测试
    - ✅ 扩展性良好
  </criteria>
</execution>
