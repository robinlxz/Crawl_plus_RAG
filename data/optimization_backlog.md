# RAG Optimization Backlog

记录 RAG 系统的潜在优化点，待评估优先级。

## P2: Query Expansion (查询扩展)
- **Problem**: 用户 Query 模糊或使用非专业术语（如 "prevent loosing data"），无法命中专业文档（如 "Snapshot"）。
- **Solution**: 增加 LLM 预处理步骤，将 User Query 改写为包含专业术语的 Expanded Query。
- **Status**: 待定。

## P2: Adaptive RAG (自适应回退)
- **Problem**: 当文档相关性低时（如 "WordPress slow"），Strict RAG 策略导致回答 "I don't know"，用户体验差。
- **Solution**: 
    1. 检测 Top-K 相似度分数。
    2. 若分数低于阈值（e.g., 0.5），切换 System Prompt，允许 LLM 使用通用知识回答，但需声明 "General Advice"。
- **Status**: 待定。

## P3: Intent Classification (意图识别)
- **Problem**: 混合了 Troubleshooting, How-to, Concept 等多种问题，单一检索策略可能不适用。
- **Solution**: 增加意图分类模块，针对不同意图优化检索策略（如 How-to 优先搜步骤文档）。
- **Status**: 低优先级。

## P3: Cross-lingual Retrieval Optimization (跨语言优化)
- **Problem**: 中文 Query 搜英文文档效果不稳定。
- **Solution**: 增加 Query Translation 步骤（中文 -> 英文）。
- **Status**: 待定，需先测试中文 Query 表现。
