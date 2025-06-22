<execution>
  <constraint>
    ## Streamlit开发技术约束
    - **版本要求**：Streamlit ≥1.32，确保新特性可用
    - **单文件限制**：所有代码必须在app.py中，避免复杂的模块结构
    - **依赖限制**：仅使用pandas、openpyxl、tqdm、python-mime-type等基础库
    - **平台兼容**：必须在Windows和macOS上正常运行
    - **离线运行**：不依赖外部API或网络服务
  </constraint>

  <rule>
    ## Streamlit开发强制规则
    - **函数长度**：每个函数不超过35行，保持代码可读性
    - **文档要求**：每个函数必须有清晰的docstring
    - **注释规范**：关键逻辑必须有inline注释说明
    - **中文界面**：所有用户界面文本必须使用简体中文
    - **错误处理**：所有可能的异常都必须被捕获和处理
  </rule>

  <guideline>
    ## Streamlit开发指导原则
    - **用户体验优先**：界面设计以用户友好为第一原则
    - **响应式设计**：确保在不同屏幕尺寸下都有良好体验
    - **状态管理**：合理使用session_state管理应用状态
    - **性能优化**：使用缓存机制提高应用性能
    - **代码质量**：保持代码简洁、可读、可维护
  </guideline>

  <process>
    ## Streamlit应用开发流程
    
    ### Phase 1: 应用架构设计
    ```mermaid
    flowchart TD
        A[应用入口] --> B[侧边栏控制区]
        A --> C[主内容区]
        B --> D[文件上传器]
        B --> E[字段映射编辑器]
        B --> F[处理控制按钮]
        C --> G[状态显示区]
        C --> H[数据预览区]
        C --> I[下载区域]
    ```
    
    **核心组件设计**：
    1. **文件上传组件**：支持多文件上传，格式验证
    2. **字段映射组件**：可视化字段映射关系
    3. **进度显示组件**：实时显示处理进度
    4. **数据预览组件**：展示处理结果预览
    5. **下载组件**：提供ZIP文件下载
    
    ### Phase 2: 核心功能实现
    ```mermaid
    flowchart TD
        A[文件上传处理] --> B[数据读取与解析]
        B --> C[字段映射与验证]
        C --> D[数据清洗处理]
        D --> E[结果生成与展示]
        E --> F[文件打包与下载]
    ```
    
    **关键实现要点**：
    1. **文件处理**：使用pandas读取Excel，处理编码问题
    2. **状态管理**：使用st.session_state管理处理状态
    3. **进度反馈**：使用st.progress和st.status显示进度
    4. **错误处理**：友好的错误信息显示
    5. **内存管理**：及时清理大对象，避免内存泄漏
    
    ### Phase 3: 用户界面优化
    ```mermaid
    graph TD
        A[界面布局] --> B[响应式设计]
        B --> C[交互优化]
        C --> D[视觉美化]
        D --> E[可用性测试]
        E --> F[性能调优]
    ```
    
    **界面设计要点**：
    1. **布局设计**：使用columns和containers优化布局
    2. **交互反馈**：提供即时的操作反馈
    3. **视觉层次**：使用标题、分割线等建立清晰层次
    4. **状态指示**：清晰的状态指示和进度显示
    
    ## Streamlit最佳实践
    
    ### 性能优化技巧
    ```python
    # 使用缓存优化数据处理
    @st.cache_data
    def load_and_process_file(file_content, filename):
        """缓存文件处理结果，避免重复计算"""
        pass
    
    # 使用session_state管理状态
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    
    # 分块处理大文件
    def process_large_file(df, chunk_size=1000):
        """分块处理大DataFrame，避免内存问题"""
        pass
    ```
    
    ### 用户体验优化
    ```python
    # 友好的错误处理
    try:
        result = process_data(df)
    except Exception as e:
        st.error(f"处理文件时出错：{str(e)}")
        st.info("请检查文件格式是否正确")
    
    # 进度显示
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, file in enumerate(files):
        status_text.text(f"正在处理文件 {i+1}/{len(files)}: {file.name}")
        progress_bar.progress((i+1)/len(files))
    ```
    
    ### 代码组织结构
    ```python
    # 主应用结构
    def main():
        """主应用入口"""
        setup_page_config()
        render_sidebar()
        render_main_content()
    
    def setup_page_config():
        """配置页面基本设置"""
        st.set_page_config(
            page_title="抖音数据清洗工具",
            page_icon="🧹",
            layout="wide"
        )
    
    def render_sidebar():
        """渲染侧边栏控制区"""
        pass
    
    def render_main_content():
        """渲染主内容区"""
        pass
    ```
    
    ## 常见问题解决方案
    
    ### 文件上传问题
    - **大文件限制**：提供文件大小检查和警告
    - **格式兼容**：支持不同Excel格式的读取
    - **编码问题**：自动检测和处理编码问题
    - **内存溢出**：实现分块读取和处理
    
    ### 状态管理问题
    - **页面刷新**：使用session_state保持状态
    - **数据持久化**：合理使用缓存机制
    - **状态同步**：确保UI状态与数据状态一致
    - **内存清理**：及时清理不需要的状态数据
    
    ### 性能优化问题
    - **重复计算**：使用@st.cache_data缓存结果
    - **大数据处理**：实现流式处理和分块处理
    - **UI响应性**：使用异步处理和进度显示
    - **资源管理**：合理管理内存和临时文件
  </process>

  <criteria>
    ## Streamlit应用质量标准
    
    ### 功能完整性
    - ✅ 所有核心功能正常工作
    - ✅ 错误处理覆盖所有异常情况
    - ✅ 文件上传和下载功能稳定
    - ✅ 数据处理逻辑正确无误
    
    ### 用户体验
    - ✅ 界面布局清晰直观
    - ✅ 操作流程简单易懂
    - ✅ 反馈信息及时准确
    - ✅ 中文界面完整友好
    
    ### 代码质量
    - ✅ 代码结构清晰合理
    - ✅ 函数长度控制在35行内
    - ✅ 注释和文档完整
    - ✅ 错误处理机制完善
    
    ### 性能表现
    - ✅ 应用启动速度快
    - ✅ 文件处理效率高
    - ✅ 内存使用合理
    - ✅ 响应时间可接受
  </criteria>
</execution>
