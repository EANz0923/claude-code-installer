"""Installation tab - system check, dependency install, Claude Code install."""

import tkinter as tk
from tkinter import ttk, messagebox
import threading

from gui.styles import (
    COLOR_BG,
    COLOR_SURFACE,
    COLOR_SUCCESS,
    COLOR_DANGER,
    COLOR_WARNING,
    FONT_HEADING,
    FONT_BODY,
    FONT_SMALL,
)
from gui.widgets.progress_frame import ProgressFrame
from core.installer import get_installer, InstallerThread


class InstallTab(ttk.Frame):
    """The Installation tab containing system checks and install buttons."""

    def __init__(self, parent):
        super().__init__(parent, style="Main.TFrame")
        self.installer = get_installer()
        self._install_thread: InstallerThread | None = None
        self._build_ui()

        # Initial status check (deferred so UI renders first)
        self.after(500, self._initial_check)

    def _build_ui(self):
        """Build the installation tab UI."""
        # --- System Status Section ---
        status_frame = ttk.LabelFrame(
            self, text="  系统状态  ", style="Card.TLabelframe", padding=16
        )
        status_frame.pack(fill="x", padx=16, pady=(16, 8))

        # Node.js status
        self.node_status_var = tk.StringVar(value="检测中...")
        self._create_status_row(status_frame, "Node.js", self.node_status_var, 0)

        # Git status
        self.git_status_var = tk.StringVar(value="检测中...")
        self._create_status_row(status_frame, "Git", self.git_status_var, 1)

        # Claude Code status
        self.claude_status_var = tk.StringVar(value="检测中...")
        self._create_status_row(status_frame, "Claude Code CLI", self.claude_status_var, 2)

        # --- Actions Section ---
        actions_frame = ttk.LabelFrame(
            self, text="  操作  ", style="Card.TLabelframe", padding=16
        )
        actions_frame.pack(fill="x", padx=16, pady=8)

        btn_row = ttk.Frame(actions_frame, style="Surface.TFrame")
        btn_row.pack(fill="x")

        self.deps_btn = ttk.Button(
            btn_row,
            text="安装缺失依赖 (Node.js + Git)",
            style="Primary.TButton",
            command=self._install_deps,
        )
        self.deps_btn.pack(side="left", padx=(0, 12))

        self.claude_btn = ttk.Button(
            btn_row,
            text="安装 Claude Code CLI",
            style="Primary.TButton",
            command=self._install_claude,
            state="disabled",
        )
        self.claude_btn.pack(side="left")

        # Separator text (tk.Label for reliable color support)
        sep_frame = tk.Frame(actions_frame, bg=COLOR_SURFACE)
        sep_frame.pack(fill="x", pady=(12, 0))
        tk.Label(
            sep_frame,
            text="先安装依赖，再安装 Claude Code CLI。或点击下方一键完成全部安装。",
            font=FONT_SMALL,
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_SURFACE,
        ).pack(side="left")

        # One-click all button
        self.all_btn = ttk.Button(
            sep_frame,
            text="一键全部安装",
            style="Secondary.TButton",
            command=self._install_all,
        )
        self.all_btn.pack(side="right")

        # --- Progress Section ---
        self.progress = ProgressFrame(self)
        self.progress.pack(fill="both", expand=True, padx=16, pady=8)

    def _create_status_row(self, parent, name: str, var: tk.StringVar, row: int):
        """Create a status indicator row."""
        frame = ttk.Frame(parent, style="Surface.TFrame")
        frame.pack(fill="x", pady=4)

        # Status dot (canvas)
        canvas = tk.Canvas(frame, width=12, height=12, bg=COLOR_SURFACE, highlightthickness=0)
        canvas.pack(side="left", padx=(0, 8))
        dot = canvas.create_oval(2, 2, 12, 12, fill="#94a3b8", outline="")

        ttk.Label(frame, text=name, font=FONT_BODY, background=COLOR_SURFACE).pack(side="left")
        ttk.Label(
            frame,
            textvariable=var,
            font=FONT_SMALL,
            foreground="#64748b",
            background=COLOR_SURFACE,
        ).pack(side="left", padx=(8, 0))

        # Store canvas/dot reference for later updates
        if not hasattr(self, "_dots"):
            self._dots = {}
        self._dots[name] = (canvas, dot)

    def _initial_check(self):
        """Run initial system check."""
        self.progress.append_log("正在检测系统环境...")
        self.installer.refresh_status(
            on_log=lambda msg: self.after(0, self.progress.append_log, msg)
        )
        self.after(0, self._update_status_ui)
        self.after(0, self._update_button_states)

    def _update_status_ui(self):
        """Update status labels and dots."""
        # Node.js
        if self.installer.status.node.installed:
            self.node_status_var.set(f"已安装 (v{self.installer.status.node.version})")
            self._set_dot("Node.js", COLOR_SUCCESS)
        elif self.installer.status.node.error:
            self.node_status_var.set(f"失败: {self.installer.status.node.error}")
            self._set_dot("Node.js", COLOR_DANGER)
        else:
            self.node_status_var.set("未安装")
            self._set_dot("Node.js", COLOR_DANGER)

        # Git
        if self.installer.status.git.installed:
            self.git_status_var.set(f"已安装 ({self.installer.status.git.version})")
            self._set_dot("Git", COLOR_SUCCESS)
        elif self.installer.status.git.error:
            self.git_status_var.set(f"失败: {self.installer.status.git.error}")
            self._set_dot("Git", COLOR_DANGER)
        else:
            self.git_status_var.set("未安装")
            self._set_dot("Git", COLOR_DANGER)

        # Claude Code
        if self.installer.status.claude.installed:
            self.claude_status_var.set(f"已安装 ({self.installer.status.claude.version})")
            self._set_dot("Claude Code CLI", COLOR_SUCCESS)
        elif self.installer.status.claude.error:
            self.claude_status_var.set(f"失败: {self.installer.status.claude.error}")
            self._set_dot("Claude Code CLI", COLOR_DANGER)
        else:
            self.claude_status_var.set("未安装")
            self._set_dot("Claude Code CLI", COLOR_DANGER)

    def _set_dot(self, name: str, color: str):
        """Update a status dot color."""
        if hasattr(self, "_dots") and name in self._dots:
            canvas, dot = self._dots[name]
            canvas.itemconfig(dot, fill=color)

    def _update_button_states(self):
        """Enable/disable buttons based on current status."""
        # Enable Claude Code install button if Node.js is installed
        if self.installer.status.node.installed:
            self.claude_btn.configure(state="normal")
        else:
            self.claude_btn.configure(state="disabled")

    def _disable_buttons(self):
        """Disable all action buttons during installation."""
        self.deps_btn.configure(state="disabled")
        self.claude_btn.configure(state="disabled")
        self.all_btn.configure(state="disabled")

    def _enable_buttons(self):
        """Re-enable buttons after installation."""
        self.deps_btn.configure(state="normal")
        self._update_button_states()
        self.all_btn.configure(state="normal")

    def _install_deps(self):
        """Install missing dependencies."""
        self._disable_buttons()
        self.progress.clear_log()
        self.progress.set_status("正在安装依赖...")
        self.progress.set_progress(0, "准备中...")

        self._install_thread = InstallerThread(
            root=self.winfo_toplevel(),
            installer=self.installer,
            mode="full",  # We only want deps, but full also works; let's use a targeted approach
            on_progress=self._on_progress,
            on_log=self._on_log,
            on_step=self._on_step,
            on_done=self._on_deps_done,
        )

        # Override mode: we run dep install only
        def run_deps_only():
            try:
                self.installer.run_dependency_install(
                    on_progress=self._install_thread._safe_progress,
                    on_log=self._install_thread._safe_log,
                    on_step=self._install_thread._safe_step,
                )
                if self._install_thread._on_done:
                    self.winfo_toplevel().after(0, self._install_thread._on_done, True)
            except Exception as e:
                self._install_thread._safe_log(f"错误: {e}")
                if self._install_thread._on_done:
                    self.winfo_toplevel().after(0, self._install_thread._on_done, False)

        self._install_thread.run = run_deps_only
        self._install_thread.start()

    def _install_claude(self):
        """Install Claude Code CLI only."""
        if not self.installer.status.node.installed:
            messagebox.showwarning("缺少依赖", "请先安装 Node.js 再安装 Claude Code CLI。")
            return

        self._disable_buttons()
        self.progress.clear_log()
        self.progress.set_status("正在安装 Claude Code CLI...")
        self.progress.set_progress(-1, "npm install -g @anthropic-ai/claude-code")

        self._install_thread = InstallerThread(
            root=self.winfo_toplevel(),
            installer=self.installer,
            mode="claude_only",
            on_progress=self._on_progress,
            on_log=self._on_log,
            on_step=self._on_step,
            on_done=self._on_claude_done,
        )
        self._install_thread.start()

    def _install_all(self):
        """Run full installation."""
        self._disable_buttons()
        self.progress.clear_log()
        self.progress.set_status("开始一键安装...")
        self.progress.set_progress(0, "准备中...")

        self._install_thread = InstallerThread(
            root=self.winfo_toplevel(),
            installer=self.installer,
            mode="full",
            on_progress=self._on_progress,
            on_log=self._on_log,
            on_step=self._on_step,
            on_done=self._on_install_done,
        )
        self._install_thread.start()

    def _on_progress(self, percent: float, message: str):
        """Handle progress update."""
        self.progress.set_progress(percent, message)

    def _on_log(self, message: str):
        """Handle log message."""
        # Determine tag based on content
        tag = "info"
        if "成功" in message or "完成" in message or "✓" in message:
            tag = "success"
        elif "失败" in message or "错误" in message or "✗" in message or "警告" in message:
            tag = "error"
        self.progress.append_log(message, tag)

    def _on_step(self, step_name: str, success: bool, detail: str):
        """Handle step completion."""
        status = "✓" if success else "✗"
        tag = "success" if success else "error"
        self.progress.append_log(f"{status} {step_name}: {detail}", tag)

    def _on_deps_done(self, result: bool):
        """Called when dependency installation completes."""
        self._enable_buttons()
        self._update_status_ui()
        self._update_button_states()

        if result:
            self.progress.set_status("依赖安装完成!")
            self.progress.set_progress(100, "完成")
            self.progress.append_log("依赖安装完成，可以安装 Claude Code CLI 了。", "success")
        else:
            self.progress.set_status("依赖安装未完全成功")
            self.progress.append_log("请检查错误信息并重试。", "error")

    def _on_claude_done(self, result: bool):
        """Called when Claude Code installation completes."""
        self._enable_buttons()
        self._update_status_ui()

        if result:
            self.progress.set_status("Claude Code CLI 安装完成!")
            self.progress.set_progress(100, "完成")
            self.progress.append_log("在命令行中运行 'claude' 即可开始使用。", "success")
        else:
            self.progress.set_status("安装失败")
            self.progress.append_log("请检查错误信息并重试。", "error")

    def _on_install_done(self, result: bool):
        """Called when full installation completes."""
        self._enable_buttons()
        self._update_status_ui()

        if result:
            self.progress.set_status("全部安装完成!")
            self.progress.set_progress(100, "完成")
            self.progress.append_log("=== 安装完成! ===", "success")
            self.progress.append_log("在命令行中运行 'claude' 即可开始使用。", "success")
        else:
            self.progress.set_status("安装未完全成功")
            self.progress.append_log("请检查错误信息并重试。", "error")
