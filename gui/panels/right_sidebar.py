import tkinter as tk
from tkinter import ttk
from ..state import AppState, ImageState
from ..pipeline.adapter import PipelineAdapter 

DEF_PREPROCESS = {
    "grayscale": "luminosity",
    "kernel": 11,
    "threshold": 75,
}

DEF_DETECT = {
    "method": "variance",
    "opacity": 0.3,
}

class RightSidebar(tk.Frame):
    def __init__(self, parent, state: AppState, pipeline=PipelineAdapter, width=340):
        super().__init__(parent, width=width, bg="#f4f4f4")
        self.pack_propagate(False)

        self.state = state
        self.pipeline = pipeline

        self._build_ui()

    # ====================== UI ====================== 

    def _build_ui(self):
        title = tk.Label(
            self,
            text="Settings",
            bg="#f4f4f4",
            fg="#222",
            font=("Segoe UI", 14, "bold")
        )
        title.pack(anchor="w", padx=16, pady=(16, 8))

        self._preprocess_section()
        self._divider()
        self._detect_section()
        self._divider()
        self._main_actions()

    def _main_actions(self):
        frame = tk.Frame(self, bg="#f4f4f4")
        frame.pack(side="bottom", fill="x", padx=16, pady=16)

        btn_font = ("Segoe UI", 12, "bold")
        
        # Preprocess Button
        tk.Button(
            frame,
            text="Preprocess",
            command=self._preprocess_active, # Reuse existing logic
            bg="#2196f3", fg="white",
            relief="flat", font=btn_font,
            cursor="hand2", height=2
        ).pack(fill="x", pady=(0, 8))

        # Detect Button
        tk.Button(
            frame,
            text="Detect Mold",
            command=self._detect_active, # Reuse existing logic
            bg="#4caf50", fg="white",
            relief="flat", font=btn_font,
            cursor="hand2", height=2
        ).pack(fill="x")


    def _divider(self):
        tk.Frame(self, height=1, bg="#cccccc").pack(fill="x", padx=16, pady=12)

    # ====================== PREPROCESS ====================== 

    def _preprocess_section(self):
        lbl = tk.Label(
            self,
            text="Preprocessing",
            bg="#f4f4f4",
            fg="#444",
            font=("Segoe UI", 11, "bold")
        )
        lbl.pack(anchor="w", padx=16, pady=(8, 4))

        self.gray_var = tk.StringVar(value=DEF_PREPROCESS["grayscale"])
        self.kernel_var = tk.IntVar(value=DEF_PREPROCESS["kernel"])
        self.th_var = tk.IntVar(value=DEF_PREPROCESS["threshold"])    
    
        self._dropdown(
            "Grayscale", self.gray_var,
            ["average", "weighted", "luminosity"]    
        )
        self._slider("Kernel Size", self.kernel_var, 3, 31)
        self._slider("Threshold", self.th_var, 0, 255)

        self._row_buttons(
            ("Restore Default", self._restore_preprocess),
            ("Preprocess", self._preprocess_active),
        )

        self._row_buttons(
            ("Preprocess All", self._preprocess_all),
            ("Auto", self._auto_preprocess),
        )

    # ====================== DETECT ====================== 

    def _detect_section(self):
        lbl = tk.Label(
            self,
            text="Mold Detection",
            bg="#f4f4f4",
            fg="#444",
            font=("Segoe UI", 11, "bold")
        )
        lbl.pack(anchor="w", padx=16, pady=(8, 4))

        self.method_var = tk.StringVar(value=DEF_DETECT["method"])
        self.opacity_var = tk.DoubleVar(value=DEF_DETECT["opacity"])
    
        self._dropdown(
            "Method", self.method_var,
            ["variance", "threshold", "custom"]    
        )
        self._slider("Overlay Opacity", self.opacity_var, 0.0, 1.0, step=0.05)

        self._row_buttons(
            ("Restore Default", self._restore_detect),
            ("Detect", self._detect_active),
        )

        self._row_buttons(
            ("Detect All", self._detect_all),
            ("Auto", self._auto_detect),
        )

    # ====================== WIDGET HELPERS ====================== 

    def _dropdown(self, label, var, values):
        frame = tk.Frame(self, bg="#f4f4f4")
        frame.pack(fill="x", padx=16, pady=4)

        tk.Label(frame, text=label, bg="#f4f4f4").pack(anchor="w")
        ttk.Combobox(
            frame,
            textvariable=var,
            values=values,
            state="readonly"
        ).pack(fill="x")
    
    def _slider(self, label, var, minv, maxv, step=1):
        frame = tk.Frame(self, bg="#f4f4f4")
        frame.pack(fill="x", padx=16, pady=4)

        tk.Label(frame, text=label, bg="#f4f4f4").pack(anchor="w")
        tk.Scale(
            frame,
            from_=minv,
            to=maxv,
            resolution=step,
            orient="horizontal",
            variable=var,
            bg="#f4f4f4",
            highlightthickness=0
        ).pack(fill="x")

    def _row_buttons(self, *buttons):
        frame = tk.Frame(self, bg="#f4f4f4")
        frame.pack(fill="x", padx=16, pady=6)

        for text, cmd in buttons:
            tk.Button(
                frame,
                text=text,
                command=cmd,
                relief="flat",
                bg="#e6e6e6",
                cursor="hand2"
            ).pack(side="left", expand=True, fill="x", padx=2)

    # ====================== LOGIC ====================== 

    def _active(self):
        return self.state.active()
    
    # ---- preprocess ----

    def _write_preprocess_params(self, img: ImageState):
        img.preprocess_params = {
            "grayscale": self.gray_var.get(),
            "kernel": self.kernel_var.get(),
            "threshold": self.th_var.get(),
        }
    
    def _restore_preprocess(self):
        self.gray_var.set(DEF_PREPROCESS["grayscale"])
        self.kernel_var.set(DEF_PREPROCESS["kernel"])
        self.th_var.set(DEF_PREPROCESS["threshold"])   

    def _preprocess_active(self):
        img = self._active()
        if img is None:
            return
        
        self._write_preprocess_params(img)

        if self.pipeline:
            self.pipeline.preprocess(img)

    def _preprocess_all(self):
        for img in self.state.images:
            self._write_preprocess_params(img)
            if self.pipeline:
                self.pipeline.preprocess(img)

    def _auto_preprocess(self):
        self._restore_preprocess()
        self._preprocess_active()

    # ---- detect ----

    def _write_detect_params(self, img: ImageState):
        img.detect_params = {
            "method": self.method_var.get(),
            "opacity": self.opacity_var.get()
        }

    def _restore_detect(self):
        self.method_var.set(DEF_DETECT["method"])
        self.opacity_var.set(DEF_DETECT["opacity"])

    def _detect_active(self):
        img = self._active()
        if img is None:
            return
        
        self._write_detect_params(img)

        if self.pipeline:
            self.pipeline.detect(img)

    def _detect_all(self):
        for img in self.state.images:
            self._write_detect_params(img)
            if self.pipeline:
                self.pipeline.detect(img)

    def _auto_detect(self):
        self._restore_detect()
        self._detect_active()
