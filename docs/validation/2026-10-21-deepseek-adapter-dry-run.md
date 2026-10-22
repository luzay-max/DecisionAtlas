# DecisionAtlas × DeepSeek：离线接入验收与未来小样本试点

> 状态：**DRY RUN ONLY · NO PAID API CALLS AUTHORIZED**  
> 分支：`fix/security-bootstrap-webhook-import-20261021`，PR [#7](https://github.com/luzay-max/DecisionAtlas/pull/7)。  
> 这是**候选接入方案**，不是完整产品/真实模型价值评估已完成的证据。

## 1. 官方接口与最低侵入配置

截至 2026-10-21，DeepSeek 的 OpenAI 兼容 API 使用：

- `LLM_BASE_URL=https://api.deepseek.com`
- `LLM_MODEL=deepseek-flash`（不沿用过时文档中的 `deepseek-chat`）
- `LLM_PROVIDER_MODE=openai_compatible`
- `LLM_API_KEY` 为 DeepSeek 专用 API Key，**不得提交到 Git、日志或聊天**
- `EMBEDDING_PROVIDER_MODE=fake`：仅在本次受控初期试验使用；DeepSeek chat endpoint **不是** `/embeddings` 的替代，不要假设完整向量索引可直接切换 DeepSeek。

DeepSeek 官方来源（每次付费前再次核对模型和计费）：

- https://api-docs.deepseek.com/zh-cn/ （兼容 API、当前模型别名）
- https://api-docs.deepseek.com/api/create-chat-completion/ （non-thinking `thinking.type=disabled`、`max_tokens`）
- https://api-docs.deepseek.com/quick_start/pricing/ （随时可能调整的 Token 价格）

项目原有 `OpenAICompatibleProvider` 通过 `/chat/completions` 调用；本次仅新增**可选**的 `max_output_tokens` 和 `disable_thinking` 参数，旧运行方式默认不变。专用受控试验固定 `deepseek-flash`、`max_tokens=768`，显式关闭思考以减少不受控生成。

## 2. 免费 Dry Run（已经接入 CI）

工作流 [DeepSeek DecisionAtlas adapter pilot](https://github.com/luzay-max/DecisionAtlas/actions/workflows/deepseek-adapter-pilot.yml) 在 PR #7 分支的相关文件推送时自动运行。

- `push` **只运行 dry-run**：Python `httpx.MockTransport` 本地生成响应，完全不调用 DeepSeek 或 GitHub API。
- 仅检测模型参数、消息体、限流、防泄密、结果 JSON 解析和审核报告结构。
- 输出 `.tmp/deepseek-pilot/deepseek-pilot-summary.json/.md`，GitHub Actions Artifacts 自动上传（非密钥、非完整数据库）。
- 模拟素材对应 `pallets/click` 的 PR #3877 和 #3884，但为手工合成摘要；`mode=dry_run_mock`、`source=synthetic_dry_run`，**绝不能用于主张真实模型决策质量**。
- 附带 pytest 负向测试：未批准付费、缺少密钥、错误模型、错误思考模式、超大请求、第三次调用均需拒绝。

## 3. 未来人工批准的收费样本（本次不执行）

此工作流另有一个 `future-live-opt-in` job，**仅能通过工作流手动触发**、选择 `live_two_requests` 并填写 `I_APPROVE_DEEPSEEK_API_CHARGES` 才进入；平时 `push` 不会触发，也没有付费密钥暴露给 dry-run。

要运行，需要未来维护者另行完成：

1. 对本轮代码和用途作确认，接受 DeepSeek API 可能产生费用；在 DeepSeek 账号侧设置独立 Key、余额/配额限制。
2. 自行将 Key 写到仓库 Settings → Secrets and variables → Actions → New repository secret，名称 **`DEEPSEEK_PILOT_API_KEY`**；不要发到聊天。
3. GitHub 的 `workflow_dispatch` 需要该文件存在于默认分支才能正常出现“Run workflow”。**目前 PR #7 是 Draft，未合并，故不能承诺现在就能运行收费模式**。后续需要另行批准部署/合并策略，绝不为此擅自合并。
4. 在被明确批准的执行中，脚本还会再次检查 `--live`、`DEEPSEEK_PILOT_APPROVED=YES_I_APPROVE_DEEPSEEK_API_CHARGES`、密钥存在，且仅访问 `https://api.deepseek.com/chat/completions`。
5. 仅采样两个公开的 `pallets/click` PR #3877、#3884，各发送一次，最多 **2 个模型请求**，单次输出 `max_tokens=768`，请求体不超过 **5000 字节**，无应用侧自动重试。
6. 根据 2026-10-21 官方**高峰价格**和保守字节→Token 估值，代码预留本地**0.10 美元估算额度**，超过就拒发后续请求；**这不是 DeepSeek 平台认可或强制执行的美元费用上限**。汇率、提供商价格调整和非公开额外费用都可能影响实际扣费，因此更强约束应在 DeepSeek 账号侧设置低余额或硬限额。
7. 报告只记录公开 GitHub 来源、简短候选结果、严格引用字符串匹配、实际 API `usage` 数字（若存在）。人工评价仍是 `not_reviewed`，Why Search 和 Drift 仍是 `not_run`。

## 4. 下一轮真正的质量门禁

上面的未来“2 PR DeepSeek API 小样本”只验证**兼容接口能输出候选结论且引用可定位**，并不能测出整个 DecisionAtlas 导入→筛选→提取→索引→Why Search→Drift 链路的准确率。

完成小样本试验并核实证据后，才在受控预算下规划完整的真实模型评测：20 条候选（不足全部）、10 个预先登记的问题、5 条 Drift 真实变更，并由独立人工标注。测试必须使用可追溯的仓库固定 SHA，分别记录幻觉、错误归因、证据不足与诚实拒答。**此计划不增加新产品功能。**

## 5. 当前保留的安全边界

- 模拟模式零付费，零外部 AI 网络访问。
- 真实模式仅在未来双重显式授权、独立 secret 和人工触发后才可能运行。
- 不在仓库保存 `DEEPSEEK_API_KEY` 的实际值。
- PR #7 保持 Draft、未合并。
