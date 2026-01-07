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
        
        self.state.add_listener(self._update_ui_state)
        
        self.custom_var = tk.BooleanVar(value=False)
        self.custom_var.trace_add("write", self._on_custom_toggle)

        self._build_ui()
        self._update_ui_state()

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

        # Global Customize Toggle
        self.cbtn_custom = tk.Checkbutton(
            self, text="Customize Parameters", variable=self.custom_var,
            bg="#f4f4f4", command=self._update_controls_state
        )
        self.cbtn_custom.pack(anchor="w", padx=16, pady=(0, 8))

        self._preprocess_section()
        self._divider()
        self._detect_section()
        self._divider()
        self._main_actions()
        
        self.lbl_info = tk.Label(
            self, text="", bg="#f4f4f4", fg="#666", font=("Segoe UI", 9)
        )
        self.lbl_info.pack(side="bottom", pady=8)

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
        
        self.actions_container = tk.Frame(frame, bg="#f4f4f4")
        self.actions_container.pack(fill="x")

        # Auto Detect Button
        self.btn_auto = tk.Button(
            self.actions_container,
            text="Auto Detect",
            command=self._auto_detect,
            bg="#673ab7", fg="white",
            relief="flat", font=btn_font,
            cursor="hand2", height=2
        )

        # Preprocess Button
        self.btn_preprocess = tk.Button(
            self.actions_container,
            text="Preprocess",
            command=self._preprocess_active, 
            bg="#2196f3", fg="white",
            relief="flat", font=btn_font,
            cursor="hand2", height=2
        )
        # self.btn_preprocess.pack(fill="x", pady=(0, 8))

        # Detect Button
        self.btn_detect = tk.Button(
            self.actions_container,
            text="Detect Mold",
            command=self._detect_active, 
            bg="#4caf50", fg="white",
            relief="flat", font=btn_font,
            cursor="hand2", height=2
        )
        # self.btn_detect.pack(fill="x")


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
        
        self.cb_gray_method = self._dropdown(
            "Grayscale Method", self.gray_method_var,
            PREPROCESS_METHODS 
        )
        
        # Live Update Triggers
        # self.preprocess_custom_var.trace_add - removed
        self.gray_method_var.trace_add("write", self._on_preprocess_change)

        # _toggle_prep() - removed

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

        # Removed individual checkbutton

        self.method_var = tk.StringVar(value=DEF_DETECT_PARAMS.method)
        self.ksize_var = tk.IntVar(value=DEF_DETECT_PARAMS.ksize)
        self.elemsize_var = tk.IntVar(value=DEF_DETECT_PARAMS.elemsize)
        self.th_var = tk.IntVar(value=DEF_DETECT_PARAMS.th)    
        self.opacity_var = tk.DoubleVar(value=DEF_DETECT_PARAMS.opacity)

        self.cb_detect_method = self._dropdown(
            "Detection Method", self.method_var,
            DETECT_METHODS
        )

        self.sc_ksize = self._slider("Kernel Size", self.ksize_var, 3, 31)
        self.sc_elemsize = self._slider("Structuring Element Size", self.elemsize_var, 10, 100)
        self.sc_th = self._slider("Threshold", self.th_var, 0, 255)
        self.sc_opacity = self._slider("Overlay Opacity", self.opacity_var, 0.0, 1.0, step=0.05)
        
        # Live Update Triggers
        # Live Update Triggers
        # self.detect_custom_var.trace_add("write", self._on_detect_change)
        self.method_var.trace_add("write", self._on_detect_change)
        self.method_var.trace_add("write", self._on_detect_change)
        self.ksize_var.trace_add("write", self._on_detect_change)
        self.elemsize_var.trace_add("write", self._on_detect_change)
        self.th_var.trace_add("write", self._on_detect_change)
        self.opacity_var.trace_add("write", self._on_detect_change)
        
        # Histogram Button
        self.btn_hist = tk.Button(
            self,
            text="Plot Histogram",
            command=self._plot_histogram,
            bg="#e0e0e0", 
            relief="flat",
            cursor="hand2"
        )
        self.btn_hist.pack(anchor="w", padx=16, pady=4, fill="x")
        
        self.btn_hist.pack(anchor="w", padx=16, pady=4, fill="x")
        
        self.cb_detect_method.config(state="disabled")
        for sc in (self.sc_ksize, self.sc_elemsize, self.sc_th, self.sc_opacity):
            sc.config(state="disabled")
        self.btn_hist.config(state="disabled")

        self._row_buttons(
            ("Restore Default", self._restore_detect),
        )

    # ====================== WIDGET HELPERS ====================== 

    def _dropdown(self, label, var, values):
        frame = tk.Frame(self, bg="#f4f4f4")
        frame.pack(fill="x", padx=16, pady=4)

        tk.Label(frame, text=label, bg="#f4f4f4").pack(anchor="w")
        cb = ttk.Combobox(
            frame,
            textvariable=var,
            values=values,
            state="readonly"
        )
        cb.pack(fill="x")
        return cb
    
    def _slider(self, label, var, minv, maxv, step=1):
        frame = tk.Frame(self, bg="#f4f4f4")
        frame.pack(fill="x", padx=16, pady=4)

        tk.Label(frame, text=label, bg="#f4f4f4").pack(anchor="w")
        sc = tk.Scale(
            frame,
            from_=minv,
            to=maxv,
            resolution=step,
            orient="horizontal",
            variable=var,
            bg="#f4f4f4",
            highlightthickness=0
        )
        sc.pack(fill="x")
        return sc

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
    
    def _update_ui_state(self):
        self._update_button_states()
        self._update_info_label()

    def _update_button_states(self):
        # Update button enable/disable logic based on image availability
        has_active = (self.state.images and self.state.active_index != -1)
        
        # Decide which buttons to show
        self.btn_auto.pack_forget()
        self.btn_preprocess.pack_forget()
        self.btn_detect.pack_forget()

        if self.custom_var.get():
            self.btn_preprocess.pack(fill="x", pady=(0, 8))
            self.btn_detect.pack(fill="x")
        else:
            self.btn_auto.pack(fill="x")

        # Set states
        if not has_active:
            self._set_btn_state(self.btn_auto, False, "#673ab7")
            self._set_btn_state(self.btn_preprocess, False, "#2196f3")
            self._set_btn_state(self.btn_detect, False, "#4caf50")
            return

        self._set_btn_state(self.btn_auto, True, "#673ab7")
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

    def _update_controls_state(self):
        is_custom = self.custom_var.get()
        state = "normal" if is_custom else "disabled"
        cb_state = "readonly" if is_custom else "disabled"

        # Preprocess
        self.cb_gray_method.config(state=cb_state)

        # Detect
        self.cb_detect_method.config(state=cb_state)
        for w in (self.sc_ksize, self.sc_elemsize, self.sc_th, self.sc_opacity, self.btn_hist):
            w.config(state=state)
            
        self._update_ui_state()

    def _on_custom_toggle(self, *args):
        # Triggered when global custom var changes
        self._update_controls_state()
        # Also need to update listeners or params
        # But we do lazy update on action usually. 
        # However, if we switch to Custom, we want to ensure params are synced?
        # Actually params are written when action runs.
        pass

    def _update_info_label(self):
        img = self._active()
        if not img:
            self.lbl_info.config(text="")
            return
        
        txt = ""
        # Assuming we can get info from img state if we store it
        # For now, if custom:
        if self.custom_var.get():
             txt = f"Custom | Gray: {self.gray_method_var.get()} | Det: {self.method_var.get()}"
        else:
             # Auto mode
             # Check if we have active info
             if img.preprocessed.img is not None:
                 txt = getattr(img, 'auto_info', f"Auto Mode | Texture: {getattr(img.preprocessed, 'texture', '?')}")
             else:
                 txt = "Auto Detect Mode"
        
        self.lbl_info.config(text=txt)

    def _on_preprocess_change(self, *args):
        img = self._active()
        if img is None: return
        self._write_preprocess_params(img)

    def _write_preprocess_params(self, img: ImageState):
        img.preprocess_params.custom = self.custom_var.get()
        img.preprocess_params.gray_method = self.gray_method_var.get() # Even if disabled, we can read it
    
    def _write_detect_params(self, img: ImageState):
        img.detect_params.custom = self.custom_var.get()
        img.detect_params.method = self.method_var.get()
        img.detect_params.ksize = self.ksize_var.get()
        img.detect_params.elemsize = self.elemsize_var.get()
        img.detect_params.th = self.th_var.get()
        img.detect_params.opacity = self.opacity_var.get()

    def _restore_preprocess(self):
        self.gray_method_var.set(DEF_PREPROCESS_PARAMS.gray_method)
    
    def _restore_detect(self):
        self.method_var.set(DEF_DETECT_PARAMS.method)
        self.ksize_var.set(DEF_DETECT_PARAMS.ksize)
        self.elemsize_var.set(DEF_DETECT_PARAMS.elemsize)
        self.th_var.set(DEF_DETECT_PARAMS.th)   
        self.opacity_var.set(DEF_DETECT_PARAMS.opacity)

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
                res, txt = self.processor.preprocess(img)
                img.preprocessed.img = res
                img.preprocessed.texture = txt
                img.detected = None # Invalidate detection if re-processed
            except Exception as e:
                print(f"Preprocess Error: {e}")

    def _detect_active(self):
        img = self._active()
        if img is None: return
        self._run_detect(img)
        self.state._notify()

    def _detect_all(self):
        for img in self.state.images:
            self._run_detect(img)
        self.state._notify()

    def _auto_detect(self):
        self._preprocess_active()
        # _preprocess_active calls run_preprocess -> notify -> updates UI
        # We need to queue detect or call immediately?
        # Detect needs preprocessed image.
        # run_preprocess is synchronous.
        self._detect_active()


    def _plot_histogram(self):
        img = self._active()
        if img and self.processor:
            self.processor.show_variance_histogram(img)

    def _on_detect_change(self, *args):
        img = self._active()
        if img is None: return
        self._write_detect_params(img)

    def _run_detect(self, img: ImageState):
        if img.preprocessed.img is None: return 
        self._write_detect_params(img)
        if self.processor:
            try:        
                img.detected = self.processor.detect(img)
            except Exception as e:
                print(f"Detect Error: {e}")
