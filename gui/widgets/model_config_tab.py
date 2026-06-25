"""Model configuration tab - company/model selection, API key input. Dark Theme."""

import tkinter as tk
from tkinter import ttk, messagebox
import threading

from gui.styles import (
    COLOR_BG, COLOR_SURFACE, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    COLOR_TEXT, COLOR_TEXT_SECONDARY, COLOR_PRIMARY, COLOR_INPUT_BG,
    COLOR_INPUT_BORDER, FONT_HEADING, FONT_BODY, FONT_SMALL,
    btn, lbl, entry as make_entry, card,
)
from data.models import COMPANIES, CompanyInfo
from core.config_manager import ConfigManager


class ModelConfigTab(tk.Frame):
    """The Model Configuration tab - dark themed."""

    def __init__(self, parent):
        super().__init__(parent, bg=COLOR_BG)
        self.config_manager = ConfigManager()
        self._build_ui()
        self._load_current_config()

    def _build_ui(self):
        # ── Provider Selection ──
        cf = tk.Frame(self, bg=COLOR_SURFACE)
        cf.pack(fill="x", padx=16, pady=(16, 8))

        h = tk.Frame(cf, bg=COLOR_SURFACE)
        h.pack(fill="x", padx=18, pady=(14, 4))
        lbl(h, "模型配置", font=FONT_HEADING).pack(side="left")
        tk.Frame(cf, bg="#21262d", height=1).pack(fill="x", padx=18)

        inner = tk.Frame(cf, bg=COLOR_SURFACE)
        inner.pack(fill="x", padx=18, pady=(14, 14))

        # Company
        r1 = tk.Frame(inner, bg=COLOR_SURFACE)
        r1.pack(fill="x", pady=4)
        lbl(r1, "AI 公司  ", font=FONT_BODY, fg=COLOR_TEXT_SECONDARY).pack(side="left")

        company_names = [c.name for c in COMPANIES]
        self.company_var = tk.StringVar(value=company_names[0])
        self.company_dropdown = ttk.Combobox(
            r1, textvariable=self.company_var, values=company_names,
            state="readonly", font=FONT_BODY, width=28)
        self.company_dropdown.pack(side="left", padx=(8, 0))
        self.company_dropdown.bind("<<ComboboxSelected>>", self._on_company_changed)

        # Model
        r2 = tk.Frame(inner, bg=COLOR_SURFACE)
        r2.pack(fill="x", pady=4)
        lbl(r2, "模型    ", font=FONT_BODY, fg=COLOR_TEXT_SECONDARY).pack(side="left")

        self.model_var = tk.StringVar()
        self.model_dropdown = ttk.Combobox(
            r2, textvariable=self.model_var, values=[], state="readonly",
            font=FONT_BODY, width=28)
        self.model_dropdown.pack(side="left", padx=(8, 0))

        # API Key
        r3 = tk.Frame(inner, bg=COLOR_SURFACE)
        r3.pack(fill="x", pady=4)
        lbl(r3, "API Key ", font=FONT_BODY, fg=COLOR_TEXT_SECONDARY).pack(side="left")

        self.api_key_var = tk.StringVar()
        self.api_key_entry = make_entry(r3, textvariable=self.api_key_var, show="*", width=28)
        self.api_key_entry.pack(side="left", padx=(8, 0))

        self.show_key_btn = btn(r3, "显示", command=self._toggle_key_visibility,
                                style="secondary", font=FONT_SMALL, padx=10, pady=4)
        self.show_key_btn.pack(side="left", padx=(8, 0))

        # Help text
        self.help_var = tk.StringVar()
        self.help_label = lbl(inner, textvariable=self.help_var, font=FONT_SMALL,
                              fg=COLOR_TEXT_SECONDARY, bg=COLOR_SURFACE)
        self.help_label.pack(fill="x", pady=(10, 0), anchor="w")

        # Validation
        self.validation_var = tk.StringVar()
        self.validation_label = lbl(inner, textvariable=self.validation_var,
                                    font=FONT_SMALL, fg=COLOR_DANGER, bg=COLOR_SURFACE)
        self.validation_label.pack(fill="x", pady=(4, 0), anchor="w")

        # ── Actions ──
        af = tk.Frame(self, bg=COLOR_BG)
        af.pack(fill="x", padx=16, pady=8)

        self.test_btn = btn(af, "测试连接", command=self._test_connection, style="secondary")
        self.test_btn.pack(side="left", padx=(0, 10))

        self.save_btn = btn(af, "保存配置", command=self._save_config)
        self.save_btn.pack(side="left")

        # ── Current Config ──
        ccf = tk.Frame(self, bg=COLOR_SURFACE)
        ccf.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        h2 = tk.Frame(ccf, bg=COLOR_SURFACE)
        h2.pack(fill="x", padx=18, pady=(14, 4))
        lbl(h2, "当前配置", font=FONT_HEADING).pack(side="left")
        tk.Frame(ccf, bg="#21262d", height=1).pack(fill="x", padx=18)

        self.current_text = tk.Text(
            ccf, wrap="word", bg=COLOR_SURFACE, fg=COLOR_TEXT_SECONDARY,
            font=FONT_SMALL, relief="flat", borderwidth=0, height=6,
            padx=18, pady=10, state="disabled")
        self.current_text.pack(fill="both", expand=True, pady=(4, 14))

        self._on_company_changed()

    # ── event handlers ──────────────────────────────────

    def _on_company_changed(self, event=None):
        name = self.company_var.get()
        company = self._find(name)
        if company:
            models = [m.name for m in company.models]
            self.model_dropdown["values"] = models
            if models:
                self.model_var.set(models[0])
            prefix_hint = f"\nAPI Key 以 '{company.api_key_prefix}' 开头" if company.api_key_prefix else ""
            self.help_var.set(f"{company.api_key_help}{prefix_hint}")
            self.validation_var.set("")

    def _toggle_key_visibility(self):
        show = self.api_key_entry.cget("show") == "*"
        self.api_key_entry.configure(show="" if show else "*")
        self.show_key_btn.configure(text="隐藏" if show else "显示")

    def _get_company(self):
        return self._find(self.company_var.get())

    def _get_model_id(self):
        c = self._get_company()
        if not c: return ""
        name = self.model_var.get()
        for m in c.models:
            if m.name == name:
                return m.id
        return ""

    @staticmethod
    def _find(name):
        for c in COMPANIES:
            if c.name == name:
                return c
        return None

    def _validate(self):
        api_key = self.api_key_var.get().strip()
        if not api_key:
            self.validation_var.set("请输入 API Key"); return False
        if not self.model_var.get():
            self.validation_var.set("请选择模型"); return False
        c = self._get_company()
        if c and c.api_key_prefix and not api_key.startswith(c.api_key_prefix):
            self.validation_var.set(f"API Key 格式不正确，应以 '{c.api_key_prefix}' 开头"); return False
        self.validation_var.set("")
        return True

    def _test_connection(self):
        if not self._validate(): return
        c = self._get_company()
        key = self.api_key_var.get().strip()
        self.test_btn.configure(state="disabled", text="测试中...")
        self.validation_var.set("正在测试连接...")
        self.validation_label.configure(fg=COLOR_WARNING)

        def run():
            try:
                ok, msg = self.config_manager.test_connection(c, key)
                self.after(0, lambda: self._test_done(ok, msg))
            except Exception as e:
                self.after(0, lambda: self._test_done(False, str(e)))

        threading.Thread(target=run, daemon=True).start()

    def _test_done(self, ok, msg):
        self.test_btn.configure(state="normal", text="测试连接")
        self.validation_var.set(msg)
        self.validation_label.configure(fg=COLOR_SUCCESS if ok else COLOR_DANGER)

    def _save_config(self):
        if not self._validate(): return
        c = self._get_company()
        mid = self._get_model_id()
        key = self.api_key_var.get().strip()
        try:
            ok = self.config_manager.save_provider_config(c, mid, key)
            if ok:
                messagebox.showinfo("保存成功", f"配置已保存到 ~/.claude.json\n公司: {c.name}\n模型: {mid}")
                self._load_current_config()
            else:
                messagebox.showerror("保存失败", "无法写入配置文件，请检查权限。")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

    def _load_current_config(self):
        self.current_text.configure(state="normal")
        self.current_text.delete("1.0", "end")
        cur = self.config_manager.get_current_provider()
        if cur and cur.get("has_key"):
            self.current_text.insert("end", "当前已配置:\n\n")
            self.current_text.insert("end", f"  公司:     {cur['company_id']}\n")
            self.current_text.insert("end", f"  模型:     {cur['model_id']}\n")
            self.current_text.insert("end", f"  API Key:  {cur['api_key_masked']}\n")
        else:
            self.current_text.insert("end", "尚未配置模型。\n请选择公司、模型并输入 API Key，然后点击「保存配置」。")
        self.current_text.configure(state="disabled")
