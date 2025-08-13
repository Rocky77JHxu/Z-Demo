# 🏋️‍♂️ AI 饮食与健身计划助手

一个基于 Streamlit 的轻量应用，帮助你快速生成个性化的饮食与健身计划，并提供上下文问答能力。

- 代码主入口：`health_agent/health_agent.py`
- UI 框架：`streamlit`
- 智能体框架：`agno`（`Agent` 抽象）
- 模型适配：`agno.models.openrouter.OpenRouter`
- 默认模型：GLM-4.5（`id="glm-4.5"`，`base_url=https://open.bigmodel.cn/api/paas/v4/`）

> （推下公众号文章）一文教你如何基于 Streamlit 快速构建智能体应用：[模型交互门面：Gradio vs. Streamlit](https://mp.weixin.qq.com/s/1Y7TUfuaDT-rVN7oB94v-g)
---

## ✨ 功能特性

- __个性化饮食计划__：结合年龄、性别、身高体重、活动水平与饮食偏好生成详细方案。
- __个性化健身计划__：包含热身、主训练与放松环节，并附解释说明与训练建议。
- __上下文问答__：基于刚生成的饮食/健身计划进行追问，获得连贯的解释与优化建议。
- __健壮的 Key 读取__：优先读取 `st.secrets["glm_api_key"]`，读取不到或异常时自动回退到侧边栏输入，避免报错。

---

## 🧱 技术栈与架构

- __前端/应用层__：`Streamlit`
  - 侧边栏输入 GLM API Key、参数表单、计划展示、问答模块。
- __智能体层__：`agno.Agent`
  - 定义两个角色：`饮食专家` 与 `健身专家`。
  - 通过 `Agent.run()` 生成内容。
- __模型与推理__：`OpenRouter` 适配器
  - `OpenRouter(id="glm-4.5", base_url=..., api_key=..., max_tokens=16384, timeout=120)`
  - 实际调用 ZhipuAI GLM API（bigmodel.cn）。

代码位置：
- UI 与主逻辑：`health_agent/health_agent.py` 的 `main()`
- 展示函数：`display_dietary_plan()`、`display_fitness_plan()`

---

## 📁 目录结构

```
Z-Demo/
└── health_agent/
    ├── health_agent.py     # 主应用
    └── README.md           # 本文档
```

如使用 `st.secrets`，建议在项目根或运行目录下加入：
```
.streamlit/
└── secrets.toml
```

---

## 🚀 快速开始

1) 安装依赖

```bash
pip install -r requirements.txt
```

> 若无 `requirements.txt`，应用在首次运行时会尝试自动安装 `agno` 与 `openai`（见 `health_agent.py` 顶部的兜底逻辑）。建议仍使用 `requirements.txt` 固化版本。

2) 运行应用（在仓库根目录）

```bash
streamlit run health_agent/health_agent.py
```

或在 `health_agent/` 目录内：

```bash
streamlit run health_agent.py
```

---

## 🔑 配置 GLM API Key（两种任选其一）

- __方式 A：侧边栏输入__（推荐入门）
  - 运行后在左侧输入框粘贴你的 GLM API Key。

- __方式 B：Streamlit Secrets__（适合部署）
  - 创建文件 `.streamlit/secrets.toml`
  - 写入：

```toml
# .streamlit/secrets.toml
glm_api_key = "你的GLM_API_KEY"
```

> 程序会优先读取 `st.secrets["glm_api_key"]`，如果 secrets 不存在或读取失败，会自动回退到侧边栏输入的 Key。

获取 Key：https://bigmodel.cn/

---

## 🧑‍💻 使用指南

1) 在侧边栏输入 GLM API Key（或配置 `secrets.toml`）。
2) 在表单中填写年龄、性别、身高、体重、活动水平与饮食偏好、健身目标。
3) 点击“生成我的计划”，等待结果：
   - 展示“个性化饮食计划”与“个性化健身计划”。
4) 如需深入了解，使用页面下方“计划答疑”：
   - 输入问题，系统会结合刚刚生成的计划进行上下文回答。

---

## ⚙️ 工作原理（Pipeline）

1) __Key 初始化__：
   - 尝试 `st.secrets.get("glm_api_key")`；异常或缺失时回退到侧边栏输入。
   - 构造 `OpenRouter(id="glm-4.5", base_url=..., api_key=..., max_tokens=16384, timeout=120)`。

2) __构建用户画像__：
   - 在 `main()` 中将表单字段整合为 `user_profile` 字符串。

3) __智能体推理__：
   - `饮食专家 Agent` 生成饮食方案。
   - `健身专家 Agent` 生成训练方案。

4) __展示与问答__：
   - 通过 `display_dietary_plan()`、`display_fitness_plan()` 展示结果。
   - 问答时将“饮食/健身计划 + 用户问题”拼接为上下文，使用同一 `glm_model` 生成回答。

对应代码片段参考：`health_agent/health_agent.py` 中 `main()`、`Agent(...).run()` 调用。

---

## ❓ 常见问题（FAQ）

- __没有 API Key 能运行吗？__
  - 不行。侧边栏会提示输入 Key；也可通过 `secrets.toml` 提前配置。

- __为什么我在本地没有配置 `secrets.toml` 也能运行？__
  - 因为代码做了兜底：读取不到 `st.secrets` 会使用侧边栏输入的 Key。

- __如何更换模型或参数？__
  - 修改 `health_agent/health_agent.py` 中初始化 `OpenRouter(...)` 的参数，如 `id`、`max_tokens`、`timeout`。

- __报错“初始化 GLM 模型出错”__
  - 检查 Key 是否正确、有无网络代理、`base_url` 是否可达、是否超时；必要时减小 `max_tokens`。

---

## 🔧 二次开发/定制建议

- __调整提示词__：修改 `Agent(instructions=[...])` 的中文指令以改变风格与细节。
- __扩展输入字段__：在 `main()` 的表单区域新增字段（如伤病史、器械条件）。
- __丰富展现__：在 `display_*` 中加入更细的分区、卡片、图标或下载功能。
- __新增工具/推理链__：基于 `agno.Agent` 组合更多工具（比如卡路里数据库查询、训练视频链接生成等）。