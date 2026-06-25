# Claude Code CLI Installer

适配中国网络环境的 **Claude Code 命令行工具** 一键安装器，带图形界面。

## 功能

| 功能 | 说明 |
|------|------|
| 🚀 一键安装 | 自动检测并安装 Node.js + Git + Claude Code CLI |
| 🪞 国内镜像 | 阿里云 npmmirror + 华为云镜像加速，自动切换 |
| 🤖 模型配置 | 支持 6 家 AI 公司，15+ 模型，API Key 配置写入 `~/.claude.json` |
| 📦 独立打包 | 可打包为单个 .exe 文件，无需安装 Python |

## 如何使用

### 方式一：直接运行（推荐）

双击 **`启动.bat`**，程序自动检测 Python 环境并启动。

### 方式二：命令行运行

```bash
python main.py
```

### 方式三：打包为 EXE

```bash
build.bat
```

打包完成后，EXE 文件在 `dist\ClaudeCodeInstaller.exe`，可直接复制给其他人使用。

## 环境要求

- Windows 10 / 11
- Python 3.10+（仅源码运行需要，打包后的 EXE 不需要）

## 支持的 AI 公司

| 公司 | 模型 |
|------|------|
| Anthropic | Claude Opus 4.8 / Sonnet 4.6 / Haiku 4.5 |
| OpenAI | GPT-4o / GPT-4o Mini / o4-mini |
| Google | Gemini 2.5 Pro / Gemini 2.5 Flash |
| DeepSeek | DeepSeek Chat (V3) / Reasoner (R1) |
| Moonshot (Kimi) | Moonshot v1 (8K / 32K / 128K) |
| 智谱 AI | GLM-4 Plus / GLM-4 Flash |

## 项目结构

```
├── 启动.bat              # 👈 双击这个运行
├── main.py               # 程序入口
├── gui/                  # 图形界面
│   ├── app.py            # 主窗口
│   ├── styles.py         # 配色/字体
│   └── widgets/          # 界面组件
├── core/                 # 核心逻辑
│   ├── installer.py      # 安装编排
│   ├── downloader.py     # 下载引擎
│   ├── config_manager.py # 配置管理
│   └── ...               # 各工具安装器
├── data/                 # 数据
│   ├── models.py         # 公司/模型目录
│   └── mirrors.py        # 镜像地址
├── build.bat             # 打包脚本
└── requirements.txt
```
