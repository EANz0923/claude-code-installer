"""Installation tab - system check, dependency install, Claude Code install. Dark Theme."""

import tkinter as tk
from tkinter import messagebox

from gui.styles import (
    COLOR_BG, COLOR_SURFACE, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    COLOR_TEXT, COLOR_TEXT_SECONDARY, COLOR_PRIMARY, COLOR_PRIMARY_HOVER,
    FONT_HEADING, FONT_BODY, FONT_SMALL, btn, lbl, card, dot as make_dot,
)
from gui.widgets.progress_frame import ProgressFrame
from core.installer import get_installer, InstallerThread


class InstallTab(tk.Frame):
    """The Installation tab - dark themed."""

    def __init__(self, parent):
        super().__init__(parent, bg=COLOR_BG)
        self.installer = get_installer()
        self._install_thread = None
        self._dots = {}
        self._build_ui()
        self.after(500, self._initial_check)

    def _build_ui(self):
        # ── System Status ──
        sf = tk.Frame(self, bg=COLOR_SURFACE, highlightthickness=0)
        sf.pack(fill="x", padx=16, pady=(16, 8))

        header = tk.Frame(sf, bg=COLOR_SURFACE)
        header.pack(fill="x", padx=18, pady=(14, 4))
        lbl(header, "系统状态", font=FONT_HEADING, fg=COLOR_TEXT).pack(side="left")

        sep = tk.Frame(sf, bg="#21262d", height=1)
        sep.pack(fill="x", padx=18)

        inner = tk.Frame(sf, bg=COLOR_SURFACE)
        inner.pack(fill="x", padx=18, pady=(10, 14))

        self.node_status_var = tk.StringVar(value="检测中...")
        self._status_row(inner, "Node.js", self.node_status_var)
        self.git_status_var = tk.StringVar(value="检测中...")
        self._status_row(inner, "Git", self.git_status_var)
        self.claude_status_var = tk.StringVar(value="检测中...")
        self._status_row(inner, "Claude Code CLI", self.claude_status_var)

        # ── Actions ──
        af = tk.Frame(self, bg=COLOR_SURFACE)
        af.pack(fill="x", padx=16, pady=8)

        h2 = tk.Frame(af, bg=COLOR_SURFACE)
        h2.pack(fill="x", padx=18, pady=(14, 4))
        lbl(h2, "操作", font=FONT_HEADING).pack(side="left")
        tk.Frame(af, bg="#21262d", height=1).pack(fill="x", padx=18)

        btn_row = tk.Frame(af, bg=COLOR_SURFACE)
        btn_row.pack(fill="x", padx=18, pady=(14, 8))

        self.deps_btn = btn(btn_row, "安装缺失依赖", command=self._install_deps)
        self.deps_btn.pack(side="left", padx=(0, 10))

        self.claude_btn = btn(btn_row, "安装 Claude Code CLI", command=self._install_claude, state="disabled")
        self.claude_btn.pack(side="left")

        # Hint row
        hint_row = tk.Frame(af, bg=COLOR_SURFACE)
        hint_row.pack(fill="x", padx=18, pady=(4, 14))
        lbl(hint_row, "先安装依赖，再安装 Claude Code CLI。或点击右侧一键全部安装。",
            font=FONT_SMALL, fg=COLOR_TEXT_SECONDARY).pack(side="left")
        self.all_btn = btn(hint_row, "一键全部安装", command=self._install_all, style="secondary")
        self.all_btn.pack(side="right")

        # ── Progress ──
        self.progress = ProgressFrame(self)
        self.progress.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    def _status_row(self, parent, name, var):
        row = tk.Frame(parent, bg=COLOR_SURFACE)
        row.pack(fill="x", pady=3)
        canvas, d = make_dot(row, color="#6e7681", size=8)
        canvas.pack(side="left", padx=(0, 10))
        self._dots[name] = (canvas, d)
        lbl(row, name, font=FONT_BODY, fg=COLOR_TEXT).pack(side="left")
        lbl(row, textvariable=var, font=FONT_SMALL, fg=COLOR_TEXT_SECONDARY).pack(side="left", padx=(10, 0))

    def _set_dot(self, name, color):
        if name in self._dots:
            c, d = self._dots[name]
            c.itemconfig(d, fill=color)

    def _initial_check(self):
        self.progress.append_log("正在检测系统环境...", "hl")
        self.installer.refresh_status(
            on_log=lambda msg: self.after(0, self.progress.append_log, msg)
        )
        self.after(0, self._update_status_ui)
        self.after(0, self._update_button_states)

    def _update_status_ui(self):
        s = self.installer.status
        for attr, var in [("node", self.node_status_var), ("git", self.git_status_var), ("claude", self.claude_status_var)]:
            st = getattr(s, attr)
            if st.installed:
                var.set(f"已安装 ({st.version})")
                self._set_dot(attr.capitalize() if attr != "claude" else "Claude Code CLI", COLOR_SUCCESS)
            elif st.error:
                var.set(f"失败: {st.error}")
                self._set_dot(attr.capitalize() if attr != "claude" else "Claude Code CLI", COLOR_DANGER)
            else:
                var.set("未安装")
                self._set_dot(attr.capitalize() if attr != "claude" else "Claude Code CLI", COLOR_DANGER)

    def _update_button_states(self):
        self.claude_btn.configure(state="normal" if self.installer.status.node.installed else "disabled")

    def _disable_buttons(self):
        for b in (self.deps_btn, self.claude_btn, self.all_btn):
            b.configure(state="disabled")

    def _enable_buttons(self):
        self.deps_btn.configure(state="normal")
        self._update_button_states()
        self.all_btn.configure(state="normal")

    def _on_progress(self, pct, msg):
        self.progress.set_progress(pct, msg)

    def _on_log(self, msg):
        tag = "ok" if any(w in msg for w in ("成功", "完成")) else ("err" if any(w in msg for w in ("失败", "错误", "警告")) else "info")
        self.progress.append_log(msg, tag)

    def _on_step(self, name, ok, detail):
        tag = "ok" if ok else "err"
        self.progress.append_log(f"{'OK' if ok else 'FAIL'} {name}: {detail}", tag)

    def _on_deps_done(self, ok):
        self._enable_buttons()
        self._update_status_ui()
        self._update_button_states()
        self.progress.set_status("依赖安装完成!" if ok else "依赖安装未完全成功")
        self.progress.set_progress(100 if ok else 0, "完成" if ok else "失败")

    def _on_claude_done(self, ok):
        self._enable_buttons()
        self._update_status_ui()
        self.progress.set_status("Claude Code CLI 安装完成!" if ok else "安装失败")
        self.progress.set_progress(100 if ok else 0, "完成" if ok else "失败")

    def _on_install_done(self, ok):
        self._enable_buttons()
        self._update_status_ui()
        self.progress.set_status("全部安装完成!" if ok else "安装未完全成功")
        self.progress.set_progress(100 if ok else 0, "完成" if ok else "失败")
        if ok:
            self.progress.append_log("在命令行中运行 'claude' 即可开始使用。", "ok")

    def _install_deps(self):
        self._disable_buttons()
        self.progress.clear_log()
        self.progress.set_status("正在安装依赖...")
        self.progress.set_progress(0, "准备中...")
        self._install_thread = InstallerThread(self.winfo_toplevel(), self.installer, "full",
                                               self._on_progress, self._on_log, self._on_step, self._on_deps_done)

        def run():
            try:
                self.installer.run_dependency_install(
                    on_progress=self._install_thread._safe_progress,
                    on_log=self._install_thread._safe_log,
                    on_step=self._install_thread._safe_step)
                self.winfo_toplevel().after(0, self._install_thread._on_done, True)
            except Exception as e:
                self._install_thread._safe_log(f"错误: {e}")
                self.winfo_toplevel().after(0, self._install_thread._on_done, False)

        self._install_thread.run = run
        self._install_thread.start()

    def _install_claude(self):
        if not self.installer.status.node.installed:
            messagebox.showwarning("缺少依赖", "请先安装 Node.js 再安装 Claude Code CLI。")
            return
        self._disable_buttons()
        self.progress.clear_log()
        self.progress.set_status("正在安装 Claude Code CLI...")
        self.progress.set_progress(-1, "npm install -g @anthropic-ai/claude-code")
        self._install_thread = InstallerThread(self.winfo_toplevel(), self.installer, "claude_only",
                                               self._on_progress, self._on_log, self._on_step, self._on_claude_done)
        self._install_thread.start()

    def _install_all(self):
        self._disable_buttons()
        self.progress.clear_log()
        self.progress.set_status("开始一键安装...")
        self.progress.set_progress(0, "准备中...")
        self._install_thread = InstallerThread(self.winfo_toplevel(), self.installer, "full",
                                               self._on_progress, self._on_log, self._on_step, self._on_install_done)
        self._install_thread.start()
