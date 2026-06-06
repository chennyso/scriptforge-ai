# ScriptForge AI

ScriptForge AI 是一款面向小说作者的 AI 剧本改编工具，通过“故事蓝图分析 + Schema 驱动生成 + 自动校验修复”的流程，将 3 章以上小说自动转换为可编辑、可追溯、可导出的 YAML 剧本初稿。

## 核心功能

- 小说粘贴或 `.txt/.md` 上传，自动识别章节。
- 支持影视剧、短剧、舞台剧、广播剧等改编类型。
- 可选择忠实原文、强化冲突、压缩节奏、增强对白等改编策略。
- 生成结构化 YAML 剧本，并展示可读的剧本预览。
- 使用 JSON Schema 校验 YAML，检查字段缺失、角色引用等问题。
- 支持按场景局部重写：强化冲突、增加对白、压缩节奏、影视化。
- 支持导出 YAML。
- 未配置 API Key 时使用规则引擎兜底，保证 Demo 可完整运行。

## 技术栈

- Frontend：React 19、TypeScript、Vite、lucide-react
- Backend：FastAPI、Pydantic、PyYAML、jsonschema、httpx
- AI：MiMo OpenAI-compatible Chat Completions API

MiMo OpenAI 兼容 Base URL：`https://token-plan-cn.xiaomimimo.com/v1`，模型默认 `mimo-v2.5-pro`。

## 本地运行

后端：

```powershell
cd E:\python\scriptforge-ai\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy ..\.env.example ..\.env
uvicorn app.main:app --reload --http h11 --host 127.0.0.1 --port 8000
```

前端：

```powershell
cd E:\python\scriptforge-ai\frontend
npm install
npm run dev
```

访问：

```text
http://127.0.0.1:5173
```

## API Key

在仓库根目录创建 `.env`：

```env
MIMO_API_KEY=你的密钥
MIMO_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1
MIMO_MODEL=mimo-v2.5-pro
USE_MOCK_AI=false
```

`.env` 已加入 `.gitignore`，不要提交真实密钥。

注意：如果你的 Key 页面标注“仅限 AI 编程和智能体工具中交互式使用，不可用于自动化脚本或应用后端”，不要把它作为线上作品后端密钥长期调用。比赛 Demo 可以先使用本地规则引擎兜底，正式接入时应更换允许后端应用调用的服务端 API Key。

可用下面的接口确认后端是否读取到配置，返回结果不会暴露密钥：

```text
http://127.0.0.1:8000/api/config
```

如果当前网络无法访问 MiMo Base URL，生成接口会自动回退到本地规则引擎，并在前端显示 provider 说明，保证 Demo 和基础改编流程仍可运行。

## 示例数据

- `examples/public-domain-novel.md`：基于公共领域作品《A Christmas Carol》的中文改写测试文本。
- `examples/alice-wonderland-gutenberg.txt`：Project Gutenberg ebook #11，公共领域长篇英文小说样例，用于测试长文本章节解析和真实输入规模。
- `examples/journey-to-the-west-gutenberg.txt`：Project Gutenberg ebook #23962，《西游记》中文公版长篇样例，用于测试中文长文本章节解析。
- `examples/guofeng-webnovel-sample.md`：来自 `longyuewangdcu/GuoFeng-Webnovel` 仓库的 WMT2024 公开中文网文测试集片段，用于测试现代网文章节风格。
- `examples/sample-output.yaml`：Schema 输出样例。

## Schema 文档

见 `docs/yaml-schema.md`。机器可读 Schema 位于 `backend/app/schemas/script_schema.json`。

## 测试

```powershell
cd E:\python\scriptforge-ai\backend
pytest
```

## PR 拆分建议

1. 初始化项目结构与开发环境。
2. 实现小说章节识别。
3. 定义 YAML Schema 与示例。
4. 实现 AI/规则生成接口。
5. 实现 Schema 校验和局部重写。
6. 实现前端工作台。
7. 完善 README、示例和 Demo 文档。

## 原创与依赖说明

本项目原创部分包括章节解析、故事蓝图生成、剧本 YAML Schema、Schema 校验、局部重写流程、前端工作台交互和 MiMo API 适配层。第三方依赖已在 `backend/requirements.txt` 与 `frontend/package.json` 中列明。
