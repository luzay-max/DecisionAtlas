# DecisionAtlas 季度路线图

日期：2026-04-22  
当前基线：`v0.2.1`  
状态：执行计划

## 目标

本季度的核心目标不是继续横向扩功能，而是把 DecisionAtlas 从“已经能跑通的强原型”推进到“真实仓库路径可信、可验证、可对外展示的产品基线”。

建议按下面这条主线推进：

```text
稳定当前基线
  -> 做深真实仓库能力
  -> 准备轻量发布 / hosted demo
  -> 为下一阶段平台化收口边界
```

---

## 阶段一：基线收口

时间建议：第 1-3 周

### 目标

把当前 `v0.2.1` 基线整理成一个稳定、清晰、可重复验证的版本。

### 重点工作

- 对齐 `README.md`、quick start、demo script、release notes、release checklist
- 跑完整的 release-style 验证，确认当前主分支能力边界与文档一致
- 统一本地开发与验证命令口径，尤其是 `uv` / `python -m uv`
- 明确 demo lane 与 imported lane 的边界，避免产品叙事继续混淆
- 清理本地-only 记录、辅助文档、临时约定，区分哪些应长期保留，哪些只是阶段性材料

### 交付物

- 一版清晰的 `v0.2.1` 基线说明
- 一套可重复执行的本地与回归验证路径
- 一组对外和对内都说得清楚的产品边界文档

### 成功标准

- 新人可以按文档独立跑起 demo 和 real stack
- 当前能力边界不依赖口头解释
- 主分支更像“可发布基线”，而不是长期堆积的实验线

---

## 阶段二：强化真实仓库主线

时间建议：第 4-8 周

### 目标

继续证明“真实仓库这条路成立”，并把 imported workspace 的首个有用结果做得更稳定。

### 主方向

延续已经完成的 candidate conversion slice，继续围绕真实仓库 outcomes 做聚焦改进，而不是同时展开平台化或新 connector。

建议 change 方向：

```text
strengthen-real-repository-outcomes
```

或更具体地收口为：

```text
improve-imported-why-and-review-readiness
```

### 重点工作

- 提高 imported workspace 更稳定进入 `review_ready` 的概率
- 提高 candidate 到 accepted 的有效转化
- 继续优化 imported why-answer 的可信度、聚焦度和支持质量
- 降低那些本可做得更好的 `limited_support` 或 `conversion_limited`
- 让 drift 在 imported workspace 中更易理解、更易操作，而不是只是一种“已经存在的能力”

### 验证策略

固定一组 curated public repositories 作为真实仓库回归面，建议覆盖：

- doc-heavy repo
- framework / medium complexity repo
- stress repo，例如 `n8n`
- why / drift 表现较好的 regression repo，例如 `browser-use`

### 成功标准

- 至少 1-2 个原本偏弱的 repo 更稳定进入 `review_ready`
- accepted 之后 why-answer 的 `ok` / `limited_support` 分布更健康
- drift 的操作语义更清楚，用户知道下一步该做什么
- real-repo validation 从“偶尔成功”提升到“可重复成功”

---

## 阶段三：轻量发布与 hosted demo 准备

时间建议：第 9-11 周

### 目标

把当前产品线做成一个更稳定的对外展示版本，但不提前进入重平台化。

### 重点工作

- hosted demo 的环境布局和依赖边界
- smoke checks、健康检查、operator notes、reset 流程
- live provider 配置与安全边界说明
- demo 展示流程收口，保证“展示能力”和“真实能力”边界清楚

### 非目标

- 不在这一阶段展开 GitHub App 全流程
- 不做 private repo 产品化
- 不做完整多用户系统
- 不把 hosted demo 和 auth / roles / scope 混在一起

### 成功标准

- 可以更稳定地对外展示
- 出现问题时有明确恢复路径
- hosted demo 是“可管理的演示环境”，不是临时拼接的本地流程

---

## 阶段四：为 v0.3 平台化收边界

时间建议：第 12 周

### 目标

不是在本季度重投入平台化，而是为下一阶段做清晰收口。

### 重点工作

- 梳理 GitHub App、private repo、login、roles、owner scope、workspace scoping 的依赖关系
- 判断哪些能力已经有 spec 和 backend 基础，哪些仍只是方向
- 形成下一季度的平台化优先顺序

### 输出

- 一版明确的平台化执行顺序
- 一组下一季度可直接启动的 OpenSpec changes
- 清晰的“这一季度不做什么”的边界

---

## 本季度不建议优先做的事

为了保证主线清晰，建议先压住这些方向：

- 大范围接入新 connector
- 大改 drift 架构
- 把 hosted demo、auth、private repo 同时推进
- 直接冲完整 SaaS 化
- 为了看起来进展更快而扩一批边缘功能

---

## 季度里程碑

### 里程碑 1

`v0.2.1` 基线收口完成

- 文档、验证、主分支口径一致
- release-style 检查可以稳定重复执行

### 里程碑 2

真实仓库主线增强完成

- curated repos 的 imported lane 表现更稳定
- review / why / drift 的真实仓库闭环更可信

### 里程碑 3

轻量 hosted demo 准备完成

- 产品可以更正式地对外展示
- operator 路径明确

### 里程碑 4

v0.3 平台化边界明确

- 下一阶段的 change backlog 已经收口
- 但本季度不重投入实现

---

## 建议执行顺序

```text
1. release-quality cleanup
2. strengthen real repository outcomes
3. host / package the demo more cleanly
4. prepare v0.3 platform work
```

---

## 总结

本季度最重要的不是“再加多少能力”，而是把当前基线收成一个可信产品，再把真实仓库主线继续做深。

一句话概括：

```text
先稳住 v0.2.1
再做强真实仓库路径
然后准备轻量发布
最后为下一阶段平台化定边界
```
