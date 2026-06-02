# DecisionAtlas 使用流程与优化建议

## 🚀 项目完整使用流程

DecisionAtlas 是一个自动从 GitHub 仓库提取和分析技术决策的系统。以下是最新优化后的标准使用流程：

### 1. 启动与准备
1. 确保已安装并配置好所有的环境变量（如 `GITHUB_TOKEN`, `OPENAI_API_KEY`, 数据库连接等）。
2. 启动后端引擎：
   ```bash
   cd services/engine
   poetry run uvicorn app.main:app --reload --port 8000
   ```
3. 启动前端控制台：
   ```bash
   cd apps/web
   npm run dev
   ```
4. 在浏览器中访问 `http://localhost:3000` 进入控制台。

### 2. 导入与分析 GitHub 仓库
1. 在 Dashboard 首页的 **Demo Import** 区域，输入目标仓库名（例如 `Fission-AI/OpenSpec`）。
2. 点击 **导入 (Import)** 开始全量同步与分析流程。系统会自动分为四个阶段进行：
   - **Queued**: 等待进入队列。
   - **Importing Artifacts**: 提取 Issue、Pull Request 等项目记录。
   - **Indexing Artifacts**: 生成内部索引以便后续提取。
   - **Extracting Decisions**: 结合 LLM 进行技术决策的结构化提取。
3. **⏸ 暂停与恢复控制**：
   - 导入过程中，如果您需要临时中止任务，可以点击 **暂停 (Pause)** 按钮。后台 worker 会在当前处理批次完成后挂起。
   - 随时点击 **恢复 (Resume)** 继续中断的导入进度。
4. 进度条与状态面板将实时更新已导入的数量与剩余的预估时间（ETA）。

### 3. 查看知识图谱与决策分析
1. 导入成功后，前往 **Decisions** 页面查看所有提取出的架构与设计决策。
2. 您可以通过前端面板可视化这些决策的时序演进。

---

## 🛠 待优化项 (Future Optimizations)

尽管当前系统已经修复了多线程并发与大文件存储截断的问题，并支持了暂停/恢复机制，未来仍有进一步优化的空间：

### 后端引擎优化
1. **多线程/异步架构的深度改造**：
   - 当前的下载过程使用了 `ThreadPoolExecutor`，但数据库存储仍为单线程提交。未来可采用 `asyncio` + `asyncpg`（或异步 SQLAlchemy）来彻底解耦 I/O 阻塞，提升超大型仓库的吞吐量。
2. **细粒度的暂停机制**：
   - 目前暂停是在处理阶段之间的外层循环检测。可以通过取消 `Event` 或传递 `CancellationToken` 使暂停立即生效，而不需要等待当前的批次/网络请求完成。
3. **断点续传功能**：
   - 若系统意外崩溃，当前可能需要从特定阶段重试。增加针对每一个 Artifact 的状态机标记，可以做到精准的异常断点续传。

### 前端体验优化
1. **WebSocket 实时推送**：
   - 目前前端使用轮询（Polling，间隔约 500ms）来获取进度状态。替换为 Server-Sent Events (SSE) 或 WebSocket 可极大减少网络请求开销，并实现毫无延迟的进度条动画。
2. **全局并发任务管理器**：
   - 引入一个悬浮的全局任务托盘。这样用户在导入超大型仓库（需耗时数十分钟）时可以自由导航至其他页面，并随时弹出托盘查看进度或控制暂停。
3. **错误提示交互**：
   - 当前的失败详情显示在状态文本下方。可为其增加详细的 Log 查看器，提供直接复制错误堆栈的按钮。

### 数据与容错
1. **速率限制 (Rate Limit) 智能规避**：
   - 增加对 GitHub API 次数耗尽的智能等待机制，自动根据 `X-RateLimit-Reset` 响应头挂起任务并在恢复后继续。
2. **LLM 提取容错**：
   - 针对部分非常复杂或文本超长的 PR，当前偶尔会由于 Token 限制导致提取失败。可引入动态切割 (Chunking) 或基于 Tree-of-Thought 的多轮提取逻辑。
