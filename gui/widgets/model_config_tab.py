"""Model configuration tab - company selection, model selection, API key input."""

import tkinter as tk
from tkinter import ttk, messagebox
import threading

from gui.styles import (
    COLOR_BG,
    COLOR_SURFACE,
    COLOR_SUCCESS,
    COLOR_DANGER,
    COLOR_WARNING,
    COLOR_TEXT,
    COLOR_TEXT_SECONDARY,
    FONT_HEADING,
    FONT_BODY,
    FONT_SMALL,
)
from data.models import COMPANIES, CompanyInfo, find_company
from core.config_manager import ConfigManager


class ModelConfigTab(ttk.Frame):
    """The Model Configuration tab for setting up AI providers."""

    def __init__(self, parent):
        super().__init__(parent, style="Main.TFrame")
        self.config_manager = ConfigManager()
        self._build_ui()
        self._load_current_config()

    def _build_ui(self):
        """Build the model configuration tab UI."""
        # --- Provider Selection ---
        config_frame = ttk.LabelFrame(
            self, text="  模型配置  ", style="Card.TLabelframe", padding=16
        )
        config_frame.pack(fill="x", padx=16, pady=(16, 8))

        # Company dropdown
        row1 = ttk.Frame(config_frame, style="Surface.TFrame")
        row1.pack(fill="x", pady=4)
        ttk.Label(
            row1, text="AI 公司:", font=FONT_BODY, background=COLOR_SURFACE, width=10
        ).pack(side="left")

        company_names = [c.name for c in COMPANIES]
        self.company_var = tk.StringVar(value=company_names[0] if company_names else "")
        self.company_dropdown = ttk.Combobox(
            row1,
            textvariable=self.company_var,
            values=company_names,
            state="readonly",
            font=FONT_BODY,
            width=30,
        )
        self.company_dropdown.pack(side="left", padx=(8, 0))
        self.company_dropdown.bind("<<ComboboxSelected>>", self._on_company_changed)

        # Model dropdown
        row2 = ttk.Frame(config_frame, style="Surface.TFrame")
        row2.pack(fill="x", pady=4)
        ttk.Label(
            row2, text="模型:", font=FONT_BODY, background=COLOR_SURFACE, width=10
        ).pack(side="left")

        self.model_var = tk.StringVar()
        self.model_dropdown = ttk.Combobox(
            row2,
            textvariable=self.model_var,
            values=[],
            state="readonly",
            font=FONT_BODY,
            width=30,
        )
        self.model_dropdown.pack(side="left", padx=(8, 0))

        # API Key input
        row3 = ttk.Frame(config_frame, style="Surface.TFrame")
        row3.pack(fill="x", pady=4)
        ttk.Label(
            row3, text="API Key:", font=FONT_BODY, background=COLOR_SURFACE, width=10
        ).pack(side="left")

        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(
            row3,
            textvariable=self.api_key_var,
            show="*",
            font=FONT_BODY,
            width=32,
        )
        self.api_key_entry.pack(side="left", padx=(8, 0))

        self.show_key_var = tk.BooleanVar(value=False)
        self.show_key_btn = ttk.Button(
            row3,
            text="显示",
            style="Small.TButton",
            command=self._toggle_key_visibility,
            width=6,
        )
        self.show_key_btn.pack(side="left", padx=(8, 0))

        # Help text
        self.help_var = tk.StringVar()
        help_label = ttk.Label(
            config_frame,
            textvariable=self.help_var,
            font=FONT_SMALL,
            foreground=COLOR_TEXT_SECONDARY,
            background=COLOR_SURFACE,
        )
        help_label.pack(fill="x", pady=(8, 0))

        # Validation message
        self.validation_var = tk.StringVar()
        self.validation_label = ttk.Label(
            config_frame,
            textvariable=self.validation_var,
            font=FONT_SMALL,
            foreground=COLOR_DANGER,
            background=COLOR_SURFACE,
        )
        self.validation_label.pack(fill="x", pady=(4, 0))

        # --- Actions ---
        actions_frame = ttk.Frame(self, style="Main.TFrame")
        actions_frame.pack(fill="x", padx=16, pady=8)

        self.test_btn = ttk.Button(
            actions_frame,
            text="测试连接",
            style="Secondary.TButton",
            command=self._test_connection,
        )
        self.test_btn.pack(side="left", padx=(0, 12))

        self.save_btn = ttk.Button(
            actions_frame,
            text="保存配置",
            style="Primary.TButton",
            command=self._save_config,
        )
        self.save_btn.pack(side="left")

        # --- Current Configuration ---
        self.current_frame = ttk.LabelFrame(
            self, text="  当前配置  ", style="Card.TLabelframe", padding=16
        )
        self.current_frame.pack(fill="both", expand=True, padx=16, pady=8)

        self.current_text = tk.Text(
            self.current_frame,
            wrap="word",
            bg=COLOR_SURFACE,
            fg=COLOR_TEXT,
            font=FONT_SMALL,
            relief="flat",
            borderwidth=0,
            height=8,
            state="disabled",
        )
        self.current_text.pack(fill="both", expand=True)

        # Initialize with first company
        self._on_company_changed()

    def _on_company_changed(self, event=None):
        """Handle company selection change."""
        company_name = self.company_var.get()
        company = self._find_company_by_name(company_name)

        if company:
            # Populate model dropdown
            model_names = [m.name for m in company.models]
            self.model_dropdown["values"] = model_names
            if model_names:
                self.model_var.set(model_names[0])

            # Update help text
            self.help_var.set(company.api_key_help)

            # Update API key prefix hint
            if company.api_key_prefix:
                self.help_var.set(
                    f"{company.api_key_help}\nAPI Key 格式: 以 '{company.api_key_prefix}' 开头"
                )
            else:
                self.help_var.set(company.api_key_help)

            # Clear validation
            self.validation_var.set("")

    def _toggle_key_visibility(self):
        """Toggle API key visibility."""
        self.show_key_var.set(not self.show_key_var.get())
        if self.show_key_var.get():
            self.api_key_entry.configure(show="")
            self.show_key_btn.configure(text="隐藏")
        else:
            self.api_key_entry.configure(show="*")
            self.show_key_btn.configure(text="显示")

    def _get_selected_company(self) -> CompanyInfo | None:
        """Get the currently selected company info."""
        return self._find_company_by_name(self.company_var.get())

    def _get_selected_model_id(self) -> str:
        """Get the model ID for the selected model name."""
        company = self._get_selected_company()
        if not company:
            return ""

        model_name = self.model_var.get()
        for model in company.models:
            if model.name == model_name:
                return model.id
        return ""

    @staticmethod
    def _find_company_by_name(name: str) -> CompanyInfo | None:
        """Find a company by its display name."""
        for company in COMPANIES:
            if company.name == name:
                return company
        return None

    def _validate_inputs(self) -> bool:
        """Validate the API key and model selection. Returns True if valid."""
        company = self._get_selected_company()
        api_key = self.api_key_var.get().strip()

        if not api_key:
            self.validation_var.set("请输入 API Key")
            return False

        if not self.model_var.get():
            self.validation_var.set("请选择模型")
            return False

        # Basic prefix validation
        if company and company.api_key_prefix:
            if not api_key.startswith(company.api_key_prefix):
                self.validation_var.set(
                    f"API Key 格式不正确，应以 '{company.api_key_prefix}' 开头"
                )
                return False

        self.validation_var.set("")
        return True

    def _test_connection(self):
        """Test the API connection in a background thread."""
        if not self._validate_inputs():
            return

        company = self._get_selected_company()
        api_key = self.api_key_var.get().strip()

        self.test_btn.configure(state="disabled", text="测试中...")
        self.validation_var.set("正在测试连接...")
        self.validation_label.configure(foreground=COLOR_WARNING)

        def run_test():
            try:
                ok, message = self.config_manager.test_connection(company, api_key)
                self.after(0, lambda: self._on_test_done(ok, message))
            except Exception as e:
                self.after(0, lambda: self._on_test_done(False, str(e)))

        t = threading.Thread(target=run_test, daemon=True)
        t.start()

    def _on_test_done(self, ok: bool, message: str):
        """Handle test connection result."""
        self.test_btn.configure(state="normal", text="测试连接")
        self.validation_var.set(message)

        if ok:
            self.validation_label.configure(foreground=COLOR_SUCCESS)
        else:
            self.validation_label.configure(foreground=COLOR_DANGER)

    def _save_config(self):
        """Save the provider configuration."""
        if not self._validate_inputs():
            return

        company = self._get_selected_company()
        model_id = self._get_selected_model_id()
        api_key = self.api_key_var.get().strip()

        try:
            ok = self.config_manager.save_provider_config(company, model_id, api_key)
            if ok:
                messagebox.showinfo("保存成功", f"配置已保存到 ~/.claude.json\n公司: {company.name}\n模型: {model_id}")
                self._load_current_config()
            else:
                messagebox.showerror("保存失败", "无法写入配置文件，请检查权限。")
        except Exception as e:
            messagebox.showerror("保存失败", f"发生错误: {e}")

    def _load_current_config(self):
        """Load and display the current configuration."""
        self.current_text.configure(state="normal")
        self.current_text.delete("1.0", "end")

        current = self.config_manager.get_current_provider()
        if current and current.get("has_key"):
            self.current_text.insert("end", "当前已配置:\n\n")
            self.current_text.insert("end", f"  公司:     {current['company_id']}\n")
            self.current_text.insert("end", f"  模型:     {current['model_id']}\n")
            self.current_text.insert("end", f"  API Key:  {current['api_key_masked']}\n")
        else:
            self.current_text.insert("end", "尚未配置模型。\n")
            self.current_text.insert("end", "请选择公司、模型并输入 API Key，然后点击「保存配置」。")

        self.current_text.configure(state="disabled")
