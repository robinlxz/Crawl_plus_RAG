# RAG Evaluation Set

本文档用于记录和评估 RAG 系统的回答质量。

## 1. 故障排查与数据安全 (Troubleshooting & Data Safety)

### Q1: 无法连接实例时的数据保护
**User Query**: "I cannot connect to my ECS server now. Is there any other ways I can prevent loosing my data?"
**Expected Intent**: 用户担心无法远程登录导致无法备份数据，询问替代方案。
**Expected Key Concepts**: Snapshot (快照), Custom Image (自定义镜像), Disk Detach (卸载云盘挂载到其他实例).
**Current Performance**:
- **Retrieval**: [待填 - Top 3 Chunks]
- **Generation**: [待填 - 评分 1-5]
- **Issue**: 回答主要集中在连接排查，未提及快照备份方案。

### Q2: 误删除文件恢复
**User Query**: "I accidentally deleted a file on my Linux instance. Can I recover it?"
**Expected Intent**: 数据恢复。
**Expected Key Concepts**: Snapshot Rollback (快照回滚), Cloud Assistant (云助手 - 如果有相关命令).

## 2. 实例管理 (Instance Management)

### Q3: 实例规格变更
**User Query**: "How can I change the CPU and memory of my instance?"
**Expected Intent**: 变配/升级。
**Expected Key Concepts**: ModifyInstanceSpec, Upgrade, Downgrade.

## 3. 计费相关 (Billing)

### Q4: 按量转包年包月
**User Query**: "Can I switch my pay-as-you-go instance to subscription?"
**Expected Intent**: 计费方式转换。
**Expected Key Concepts**: Billing method conversion.

## 4. 概念理解 (Conceptual)

### Q5: ESSD vs Local SSD
**User Query**: "What is the difference between ESSD and local SSD?"
**Expected Intent**: 存储类型对比。
**Expected Key Concepts**: IOPS, Latency, Persistence (ESSD 持久化 vs Local SSD 易失性).

## 5. 边界测试与常识回退 (Out-of-Domain & Fallback)

### Q6: WordPress 性能慢
**User Query**: "My backend service (worldpress) seems to be very slow on your ECS, is there anything wrong with the server?"
**Expected Intent**: 寻求故障排查帮助，即使文档未覆盖 WordPress。
**Expected Key Concepts**: CPU/Memory/Disk Monitoring, Network Latency, General Troubleshooting.
**Current Performance**:
- **Retrieval**: 召回了时间同步、维护等无关文档。
- **Generation**: 5/5 (优秀). 明确指出文档未覆盖，但给出了通用排查建议。
- **Note**: 此案例验证了 "Helpfulness" 优于 "Strict Factuality" 的场景。
