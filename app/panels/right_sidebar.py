from ..state import AppState, ImageState
from ..defs import PreprocessParams, DetectParams, PREPROCESS_METHODS, DETECT_METHODS
from ..pipeline.processor import Processor

import tkinter as tk
from tkinter import ttk

DEF_PREPROCESS_PARAMS = PreprocessParams()
DEF_DETECT_PARAMS = DetectParams()

class RightSidebar(tk.Frame):
    def __init__(self, parent, state: AppState, processor: Processor, width=340):
        super().__init__(parent, width=width, bg="#f4f4f4")
        self.pack_propagate(False)

        self.state = state
        self.processor = processor
        
        self.state.add_listener(self._update_button_states)
        self._build_ui()
        self._update_button_states()

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

        # Menu Button
        top_bar = tk.Frame(frame, bg="#f4f4f4")
        top_bar.pack(fill="x", pady=(0, 4))
        
        btn_menu = tk.Button(
            top_bar, text="...", 
            relief="flat", bg="#e0e0e0", fg="#555",
            cursor="hand2", width=3
        )
        btn_menu.pack(side="right")
        
        self.menu_actions = tk.Menu(self, tearoff=0)
        self.menu_actions.add_command(label="Preprocess All", command=self._preprocess_all)
        self.menu_actions.add_command(label="Detect All", command=self._detect_all)
        
        def show_menu(e):
            self.menu_actions.post(e.x_root, e.y_root)
        btn_menu.bind("<Button-1>", show_menu)

        btn_font = ("Segoe UI", 12, "bold")
        
        # Preprocess Button
        self.btn_preprocess = tk.Button(
            frame,
            text="Preprocess",
            command=self._preprocess_active, 
            bg="#2196f3", fg="white",
            relief="flat", font=btn_font,
            cursor="hand2", height=2
        )
        self.btn_preprocess.pack(fill="x", pady=(0, 8))

        # Detect Button
        self.btn_detect = tk.Button(
            frame,
            text="Detect Mold",
            command=self._detect_active, 
            bg="#4caf50", fg="white",
            relief="flat", font=btn_font,
            cursor="hand2", height=2
        )
        self.btn_detect.pack(fill="x")


    def _divider(self):
        tk.Frame(self, height=1, bg="#cccccc").pack(fill="x", padx=16, pady=12)

    # ====================== PREPROCESS ====================== 

    def _preprocess_section(self):
        lbl = tk.Label(
            self,
            text="Preprocess Parameters Customization",
            bg="#f4f4f4",
            fg="#444",
            font=("Segoe UI", 11, "bold")
        )
        lbl.pack(anchor="w", padx=16, pady=(8, 4))

        self.gray_method_var = tk.StringVar(value=DEF_PREPROCESS_PARAMS.gray_method)
        
        self._dropdown(
            "Grayscale Method", self.gray_method_var,
            PREPROCESS_METHODS 
        )

        self._row_buttons(
            ("Restore Default", self._restore_preprocess),
        )

    # ====================== DETECT ====================== 

    def _detect_section(self):
        lbl = tk.Label(
            self,
            text="Mold Detection Parameters Customization",
            bg="#f4f4f4",
            fg="#444",
            font=("Segoe UI", 11, "bold")
        )
        lbl.pack(anchor="w", padx=16, pady=(8, 4))

        self.method_var = tk.StringVar(value=DEF_DETECT_PARAMS.method)
        self.ksize_var = tk.IntVar(value=DEF_DETECT_PARAMS.ksize)
        self.elemsize_var = tk.IntVar(value=DEF_DETECT_PARAMS.elemsize)
        self.th_var = tk.IntVar(value=DEF_DETECT_PARAMS.th)    
        self.opacity_var = tk.DoubleVar(value=DEF_DETECT_PARAMS.opacity)

        self._dropdown(
            "Detection Method", self.method_var,
            DETECT_METHODS
        )

        self._slider("Kernel Size", self.ksize_var, 3, 31)
        self._slider("Structuring Element Size", self.elemsize_var, 10, 100)
        self._slider("Threshold", self.th_var, 0, 255)
        self._slider("Overlay Opacity", self.opacity_var, 0.0, 1.0, step=0.05)

        self._row_buttons(
            ("Restore Default", self._restore_detect),
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
    
    def _update_button_states(self):
        if not self.state.images or self.state.active_index == -1:
            self._set_btn_state(self.btn_preprocess, False, "#2196f3")
            self._set_btn_state(self.btn_detect, False, "#4caf50")
            return

        self._set_btn_state(self.btn_preprocess, True, "#2196f3")
        
        active_img = self._active()
        if active_img and active_img.preprocessed.img is not None:
             self._set_btn_state(self.btn_detect, True, "#4caf50")
        else:
             self._set_btn_state(self.btn_detect, False, "#4caf50")

    def _set_btn_state(self, btn, enabled, color):
        if enabled:
            btn.config(state="normal", bg=color, cursor="hand2")
        else:
            btn.config(state="disabled", bg="#cccccc", cursor="arrow")

    # ---- preprocess ----

    def _write_preprocess_params(self, img: ImageState):
        img.preprocess_params.gray_method = self.gray_method_var.get()
    
    def _restore_preprocess(self):
        self.gray_method_var.set(DEF_PREPROCESS_PARAMS.gray_method)
        
        img = self._active()
        img.preprocess_params.custom = False
    
    def _preprocess_active(self):
        img = self._active()
        if img is None: return
        self._run_preprocess(img)
        self.state._notify() # Refresh UI

    def _preprocess_all(self):
        for img in self.state.images:
            self._run_preprocess(img)
        self.state._notify()

    def _run_preprocess(self, img: ImageState):
        self._write_preprocess_params(img)
        if self.processor:
            try:
                res, brightness = self.processor.preprocess(img.original, img.preprocess_params)
                img.preprocessed.img = res
                img.preprocessed.brightness = brightness
                img.detected = None # Invalidate detection if re-processed
            except Exception as e:
                print(f"Preprocess Error: {e}")

    # ---- detect ----

    def _write_detect_params(self, img: ImageState):
        img.detect_params.method = self.method_var.get()
        img.detect_params.ksize = self.ksize_var.get()
        img.detect_params.elemsize = self.elemsize_var.get()
        img.detect_params.th = self.th_var.get()
        img.detect_params.opacity = self.opacity_var.get()

    def _restore_detect(self):
        self.method_var.set(DEF_DETECT_PARAMS.method)
        self.ksize_var.set(DEF_DETECT_PARAMS.ksize)
        self.elemsize_var.set(DEF_DETECT_PARAMS.elemsize)
        self.th_var.set(DEF_DETECT_PARAMS.th)   
        self.opacity_var.set(DEF_DETECT_PARAMS.opacity)

        img = self._active()
        img.detect_params.custom = False

    def _detect_active(self):
        img = self._active()
        if img is None: return
        self._run_detect(img)
        self.state._notify()

    def _detect_all(self):
        for img in self.state.images:
            self._run_detect(img)
        self.state._notify()

    def _run_detect(self, img: ImageState):
        if img.preprocessed.img is None: return 
        self._write_detect_params(img)
        if self.processor:
            try:        
                self.processor.detect(img.preprocessed, img.detect_params)
                #img.detected = res
            except Exception as e:
                print(f"Detect Error: {e}")
