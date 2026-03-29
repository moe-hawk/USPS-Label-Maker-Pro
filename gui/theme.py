from __future__ import annotations
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

HAS_CUSTOMTKINTER = False
try:
    import customtkinter as ctk
    HAS_CUSTOMTKINTER = True
except Exception:
    ctk = None

if HAS_CUSTOMTKINTER:
    def setup_theme(mode: str = "system") -> None:
        ctk.set_appearance_mode(mode)
        ctk.set_default_color_theme("blue")
    CTk = ctk.CTk; CTkToplevel = ctk.CTkToplevel; CTkFrame = ctk.CTkFrame
    CTkButton = ctk.CTkButton; CTkLabel = ctk.CTkLabel; CTkEntry = ctk.CTkEntry
    CTkTextbox = ctk.CTkTextbox; CTkCheckBox = ctk.CTkCheckBox; CTkComboBox = ctk.CTkComboBox
    CTkTabview = ctk.CTkTabview; CTkScrollableFrame = ctk.CTkScrollableFrame
    CTkProgressBar = ctk.CTkProgressBar; CTkSwitch = ctk.CTkSwitch; CTkOptionMenu = ctk.CTkOptionMenu
else:
    class _Progress(ttk.Progressbar):
        def __init__(self, master=None, **kwargs):
            super().__init__(master, orient="horizontal", mode="determinate", **kwargs)
        def set(self, value: float) -> None:
            self["value"] = max(0, min(100, value * 100))

    class _Tabview(ttk.Notebook):
        def __init__(self, master=None, **kwargs):
            super().__init__(master)
            self._tabs = {}
        def add(self, name: str):
            frame = ttk.Frame(self)
            super().add(frame, text=name)
            self._tabs[name] = frame
            return frame
        def tab(self, name: str): return self._tabs[name]

    class _Combo(ttk.Combobox):
        def __init__(self, master=None, values=None, variable=None, **kwargs):
            self._var = variable or tk.StringVar()
            super().__init__(master, textvariable=self._var, values=list(values or []), **kwargs)
        def set(self, value): self._var.set(value)
        def get(self): return self._var.get()

    class _Text(tk.Text):
        def __init__(self, master=None, **kwargs):
            super().__init__(master, wrap="word", relief="solid", borderwidth=1, **kwargs)
        def get(self, start="1.0", end="end-1c"): return super().get(start, end)

    class _Entry(ttk.Entry):
        def __init__(self, master=None, textvariable=None, **kwargs):
            self._var = textvariable or tk.StringVar()
            super().__init__(master, textvariable=self._var, **kwargs)
        def get(self): return self._var.get()
        def insert(self, index, string): self._var.set(string)

    class _Check(ttk.Checkbutton):
        def __init__(self, master=None, text="", variable=None, onvalue=True, offvalue=False, **kwargs):
            self._var = variable or tk.BooleanVar(value=False)
            super().__init__(master, text=text, variable=self._var, onvalue=onvalue, offvalue=offvalue, **kwargs)
        def get(self): return self._var.get()
        def select(self): self._var.set(True)
        def deselect(self): self._var.set(False)

    class _ScrollableFrame(ttk.Frame):
        def __init__(self, master=None, **kwargs): super().__init__(master, **kwargs)

    class _Switch(_Check): pass
    class _OptionMenu(_Combo): pass
    class _Top(tk.Toplevel): pass

    def setup_theme(mode: str = "system") -> None: pass

    CTk = tk.Tk; CTkToplevel = _Top; CTkFrame = ttk.Frame; CTkButton = ttk.Button
    CTkLabel = ttk.Label; CTkEntry = _Entry; CTkTextbox = _Text; CTkCheckBox = _Check
    CTkComboBox = _Combo; CTkTabview = _Tabview; CTkScrollableFrame = _ScrollableFrame
    CTkProgressBar = _Progress; CTkSwitch = _Switch; CTkOptionMenu = _OptionMenu

__all__ = ["HAS_CUSTOMTKINTER","setup_theme","CTk","CTkToplevel","CTkFrame","CTkButton",
    "CTkLabel","CTkEntry","CTkTextbox","CTkCheckBox","CTkComboBox","CTkTabview",
    "CTkScrollableFrame","CTkProgressBar","CTkSwitch","CTkOptionMenu",
    "filedialog","messagebox","ttk","tk"]
