# Claude Code CLI Installer / Claude Code CLI 安装器

[English](#english) | [中文](#中文)

---

## English

A one-click GUI installer for **Claude Code CLI** on Windows, optimized for users in China.

### Features

| Feature | Description |
|---------|-------------|
| 🚀 One-click Install | Auto-detects and installs Node.js + Git + Claude Code CLI |
| 🪞 China Mirrors | Alibaba Cloud npmmirror + Huawei Cloud mirror with auto-fallback |
| 🤖 Model Config | 6 AI providers, 15+ models, writes API key to `~/.claude.json` |
| 📦 Standalone EXE | Package as a single .exe, no Python required |

### How to Use

#### Option 1: Double-click (Recommended)

Double-click **`main.pyw`** — starts the GUI directly, no console window.

#### Option 2: Command Line

```bash
python main.pyw
```

#### Option 3: Build EXE

```bash
build.bat
```

The EXE will be at `dist\ClaudeCodeInstaller.exe`.

### Requirements

- Windows 10 / 11
- Python 3.10+ (source only; packaged EXE needs nothing)

### Supported Providers

| Provider | Models |
|----------|--------|
| Anthropic | Claude Opus 4.8 / Sonnet 4.6 / Haiku 4.5 / Fable 5 |
| OpenAI | GPT-4o / GPT-4o Mini / o4-mini |
| Google | Gemini 2.5 Pro / Flash / Flash Lite |
| DeepSeek | V4 Flash / V4 Pro |
| Moonshot (Kimi) | Kimi Latest / Kimi Thinking |
| Zhipu AI | GLM-4.5 / GLM-4.5 Flash |

---

## 中文

适配中国网络环境的 **Claude Code 命令行工具** 一键安装器，带图形界面。

### 功能

| 功能 | 说明 |
|------|------|
| 🚀 一键安装 | 自动检测并安装 Node.js + Git + Claude Code CLI |
| 🪞 国内镜像 | 阿里云 npmmirror + 华为云镜像加速，自动切换 |
| 🤖 模型配置 | 支持 6 家 AI 公司，15+ 模型，API Key 配置写入 `~/.claude.json` |
| 📦 独立打包 | 可打包为单个 .exe 文件，无需安装 Python |

### 如何使用

#### 方式一：双击运行（推荐）

双击 **`main.pyw`**，直接启动 GUI，无命令行黑框。

#### 方式二：命令行运行

```bash
python main.pyw
```

#### 方式三：打包为 EXE

```bash
build.bat
```

打包完成后，EXE 文件在 `dist\ClaudeCodeInstaller.exe`，可直接复制给其他人使用。

### 环境要求

- Windows 10 / 11
- Python 3.10+（仅源码运行需要，打包后的 EXE 不需要）

### 支持的 AI 公司

| 公司 | 模型 |
|------|------|
| Anthropic | Claude Opus 4.8 / Sonnet 4.6 / Haiku 4.5 / Fable 5 |
| OpenAI | GPT-4o / GPT-4o Mini / o4-mini |
| Google | Gemini 2.5 Pro / Flash / Flash Lite |
| DeepSeek | V4 Flash / V4 Pro |
| Moonshot (Kimi) | Kimi Latest / Kimi Thinking |
| 智谱 AI | GLM-4.5 / GLM-4.5 Flash |

### 项目结构

```
├── main.pyw               # 👈 双击这个运行
├── gui/                   # 图形界面
│   ├── app.py             # 主窗口
│   ├── styles.py          # 暗色主题配色
│   └── widgets/           # 界面组件
├── core/                  # 核心逻辑
│   ├── installer.py       # 安装编排
│   ├── downloader.py      # 下载引擎（镜像回退+重试）
│   ├── config_manager.py  # 配置管理
│   └── ...
├── data/                  # 数据
│   ├── models.py          # 公司/模型目录
│   └── mirrors.py         # 国内镜像地址
├── build.bat              # PyInstaller 打包脚本
└── requirements.txt
```
