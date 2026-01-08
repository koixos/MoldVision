from ..state import AppState, ImageState
from ..defs import PreprocessParams, DetectParams, PREPROCESS_METHODS, DETECT_METHODS, TH_MODES
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
        
        self._updating_flag = False
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

        # preprocess/detect all btns
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

        # custom preprocess btn
        self.btn_preprocess = tk.Button(
            self.actions_container,
            text="Preprocess",
            command=self._preprocess_active, 
            bg="#2196f3", fg="white",
            relief="flat", font=btn_font,
            cursor="hand2", height=2
        )

        # custom detect btn
        self.btn_detect = tk.Button(
            self.actions_container,
            text="Detect Mold",
            command=self._detect_active, 
            bg="#4caf50", fg="white",
            relief="flat", font=btn_font,
            cursor="hand2", height=2
        )


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
        self.use_clahe_var = tk.BooleanVar(value=DEF_PREPROCESS_PARAMS.use_clahe)
        self.clahe_clip_var = tk.DoubleVar(value=DEF_PREPROCESS_PARAMS.clahe_clip)
        self.clahe_grid_var = tk.IntVar(value=DEF_PREPROCESS_PARAMS.clahe_grid)
        
        self.cb_gray_method = self._dropdown(
            "Grayscale Method", self.gray_method_var,
            PREPROCESS_METHODS 
        )
        
        # CLAHE
        self.cbtn_clahe = tk.Checkbutton(
            self, text="Use CLAHE (Contrast Limited Adaptive Histogram Equalization)", variable=self.use_clahe_var,
            bg="#f4f4f4", command=self._on_preprocess_change
        )
        self.cbtn_clahe.pack(anchor="w", padx=16, pady=4)

        self.frm_clahe = tk.Frame(self, bg="#f4f4f4")
        self.frm_clahe.pack(fill="x")

        self.sc_clahe_clip = self._slider("Clip Limit", self.clahe_clip_var, 1.0, 10.0, step=0.1, parent=self.frm_clahe)
        self.sc_clahe_grid = self._slider("Grid Size", self.clahe_grid_var, 2, 32, parent=self.frm_clahe)
        
        # Live Update Triggers
        self.gray_method_var.trace_add("write", self._on_preprocess_change)
        self.use_clahe_var.trace_add("write", self._on_preprocess_change)
        self.clahe_clip_var.trace_add("write", self._on_preprocess_change)
        self.clahe_grid_var.trace_add("write", self._on_preprocess_change)

        self._row_buttons(("Restore Default", self._restore_preprocess))


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

        # --- VARS ---
        self.method_var = tk.StringVar(value=DEF_DETECT_PARAMS.method)
        
        # Variance / Generic
        self.th_mode_var = tk.StringVar(value=DEF_DETECT_PARAMS.th_mode)
        self.fixed_th_var = tk.IntVar(value=DEF_DETECT_PARAMS.fixed_th)
        self.zk_var = tk.DoubleVar(value=DEF_DETECT_PARAMS.z_k)
        self.percentile_var = tk.DoubleVar(value=DEF_DETECT_PARAMS.percentile)
        
        # LBP
        self.use_lbp_var = tk.BooleanVar(value=DEF_DETECT_PARAMS.use_lbp)
        self.lbp_rad_var = tk.IntVar(value=DEF_DETECT_PARAMS.lbp_rad)
        self.lbp_points_var = tk.IntVar(value=DEF_DETECT_PARAMS.lbp_points)
        
        # Filters
        self.min_area_var = tk.DoubleVar(value=DEF_DETECT_PARAMS.min_area)
        self.max_area_var = tk.DoubleVar(value=DEF_DETECT_PARAMS.max_area)
        self.elemsize_var = tk.IntVar(value=DEF_DETECT_PARAMS.elemsize)
        self.open_iter_var = tk.IntVar(value=DEF_DETECT_PARAMS.open_iter)
        self.close_iter_var = tk.IntVar(value=DEF_DETECT_PARAMS.close_iter)

        # Adaptive
        self.block_size_var = tk.IntVar(value=DEF_DETECT_PARAMS.block_size)
        self.c_var = tk.IntVar(value=DEF_DETECT_PARAMS.c)

        # Edge
        self.edge_t1_var = tk.IntVar(value=DEF_DETECT_PARAMS.edge_t1)
        self.edge_t2_var = tk.IntVar(value=DEF_DETECT_PARAMS.edge_t2)
        self.edge_kernel_var = tk.IntVar(value=DEF_DETECT_PARAMS.edge_kernel)
        self.edge_density_th_var = tk.IntVar(value=DEF_DETECT_PARAMS.edge_density_th)


        # --- WIDGETS ---
        self.cb_detect_method = self._dropdown(
            "Detection Method", self.method_var,
            DETECT_METHODS
        )

        
        # Container frames for dynamic visibility
        self.frm_variance_opts = tk.Frame(self, bg="#f4f4f4")
        self.frm_adaptive_opts = tk.Frame(self, bg="#f4f4f4")
        self.frm_edge_opts = tk.Frame(self, bg="#f4f4f4")
        
        # -- Variance Vars --
        self.cb_th_mode = self._dropdown("Threshold Mode", self.th_mode_var, TH_MODES, parent=self.frm_variance_opts)
        self.sc_fixed_th = self._slider("Fixed Threshold", self.fixed_th_var, 0, 255, parent=self.frm_variance_opts)
        self.sc_zk = self._slider("Z-Score K", self.zk_var, 0.1, 10.0, step=0.1, parent=self.frm_variance_opts)
        self.sc_percentile = self._slider("Percentile", self.percentile_var, 1.0, 99.9, step=0.5, parent=self.frm_variance_opts)

        self.cbtn_lbp = tk.Checkbutton(
            self.frm_variance_opts, text="Use LBP Filter", variable=self.use_lbp_var,
            bg="#f4f4f4", command=self._on_detect_change
        )
        self.cbtn_lbp.pack(anchor="w", padx=16, pady=4)
        
        self.sc_lbp_rad = self._slider("LBP Radius", self.lbp_rad_var, 1, 10, parent=self.frm_variance_opts)
        self.sc_lbp_points = self._slider("LBP Points", self.lbp_points_var, 4, 32, parent=self.frm_variance_opts)

        # -- Adaptive Vars --
        self.sc_block_size = self._slider("Block Size", self.block_size_var, 3, 99, parent=self.frm_adaptive_opts)
        self.sc_c = self._slider("C Constant", self.c_var, -20, 20, parent=self.frm_adaptive_opts)

        # -- Edge Vars --
        self.sc_edge_t1 = self._slider("Canny T1", self.edge_t1_var, 0, 255, parent=self.frm_edge_opts)
        self.sc_edge_t2 = self._slider("Canny T2", self.edge_t2_var, 0, 255, parent=self.frm_edge_opts)
        self.sc_edge_k = self._slider("Filter Kernel", self.edge_kernel_var, 3, 31, parent=self.frm_edge_opts)
        self.sc_edge_dth = self._slider("Density Th", self.edge_density_th_var, 0, 255, parent=self.frm_edge_opts)

        # -- Common --
        self.frm_common = tk.Frame(self, bg="#f4f4f4")
        self.sc_min_area = self._slider("Min Area Ratio", self.min_area_var, 0.0, 0.1, step=0.0001, parent=self.frm_common)
        self.sc_max_area = self._slider("Max Area Ratio", self.max_area_var, 0.0, 1.0, step=0.01, parent=self.frm_common)
        self.sc_elemsize = self._slider("Morph. Size", self.elemsize_var, 1, 31, parent=self.frm_common)
        self.sc_opener = self._slider("Open Iter", self.open_iter_var, 0, 10, parent=self.frm_common)
        self.sc_closer = self._slider("Close Iter", self.close_iter_var, 0, 10, parent=self.frm_common)

        # Triggers
        self.method_var.trace_add("write", self._on_detect_change)
        self.th_mode_var.trace_add("write", self._on_detect_change)
        
        all_vars = [
            self.fixed_th_var, self.zk_var, self.percentile_var,
            self.use_lbp_var, self.lbp_rad_var, self.lbp_points_var,
            self.min_area_var, self.max_area_var, self.elemsize_var, 
            self.open_iter_var, self.close_iter_var,
            self.block_size_var, self.c_var,
            self.edge_t1_var, self.edge_t2_var, self.edge_kernel_var, self.edge_density_th_var
        ]
        for v in all_vars:
            v.trace_add("write", self._on_detect_change)

        
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

        self._row_buttons(("Restore Default", self._restore_detect))


    # ====================== WIDGET HELPERS ====================== 

    def _dropdown(self, label, var, values, parent=None):
        frame = tk.Frame(parent or self, bg="#f4f4f4")
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
    

    def _slider(self, label, var, minv, maxv, step=1, parent=None):
        frame = tk.Frame(parent or self, bg="#f4f4f4")
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
        
        # Sync Custom Toggle (Safe Update)
        active_img = self._active()
        if active_img:
            self._updating_flag = True
            try:
                self.custom_var.set(active_img.custom)
            finally:
                self._updating_flag = False

        self._update_controls_state()
        self._update_info_label()


    def _update_button_states(self):
        has_active = (self.state.images and self.state.active_index != -1)
        
        self.btn_auto.pack_forget()
        self.btn_preprocess.pack_forget()
        self.btn_detect.pack_forget()

        if self.custom_var.get():
            self.btn_preprocess.pack(fill="x", pady=(0, 8))
            self.btn_detect.pack(fill="x")
        else:
            self.btn_auto.pack(fill="x")

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
        if self._updating_flag: return
        is_custom = self.custom_var.get()
        
        active_img = self._active()
        has_prep = (active_img is not None and active_img.preprocessed.img is not None)

        # Preprocess State
        prep_state = "normal" if is_custom else "disabled"
        self.cb_gray_method.config(state="readonly" if is_custom else "disabled")
        self.cbtn_clahe.config(state=prep_state)
        
        # CLAHE Visibility
        if is_custom and self.use_clahe_var.get():
            self.frm_clahe.pack(fill="x")
            for w in (self.sc_clahe_clip, self.sc_clahe_grid):
                w.config(state="normal")
        else:
            self.frm_clahe.pack_forget()


        # Detect State
        det_enabled = is_custom and has_prep
        det_state = "normal" if det_enabled else "disabled"
        det_cb_state = "readonly" if det_enabled else "disabled"
        
        self.cb_detect_method.config(state=det_cb_state)
        self.btn_hist.config(state=det_state)

        # Visibility Logic
        self.frm_variance_opts.pack_forget()
        self.frm_adaptive_opts.pack_forget()
        self.frm_edge_opts.pack_forget()
        self.frm_common.pack_forget()

        method = self.method_var.get()
        
        if det_enabled:
            # Common params usually valid for all (morphology, area)
            self.frm_common.pack(fill="x")
            
            if method in ("variance", "var_lbp"):
                self.frm_variance_opts.pack(fill="x")
                
                # Sub-visibility for Variance
                th_mode = self.th_mode_var.get()
                if th_mode == "fixed":
                    self.sc_fixed_th.pack(fill="x", padx=16, pady=4)
                    self.sc_zk.pack_forget()
                    self.sc_percentile.pack_forget()
                elif th_mode == "zscore":
                    self.sc_fixed_th.pack_forget()
                    self.sc_zk.pack(fill="x", padx=16, pady=4)
                    self.sc_percentile.pack_forget()
                else:
                    self.sc_fixed_th.pack_forget()
                    self.sc_zk.pack_forget()
                    self.sc_percentile.pack(fill="x", padx=16, pady=4)

            elif method == "adaptive":
                self.frm_adaptive_opts.pack(fill="x")
            
            elif method in ("edge", "saturation"):
                self.frm_edge_opts.pack(fill="x")

            # Enable/Disable all children of visible frames
            for frm in (self.frm_variance_opts, self.frm_adaptive_opts, self.frm_edge_opts, self.frm_common):
                for child in frm.winfo_children():
                    if isinstance(child, (tk.Scale, tk.Checkbutton, tk.Entry, ttk.Combobox)):
                        child.configure(state=det_state)
                    # For sliders which are frames in my helper...
                    if isinstance(child, tk.Frame):
                        for sub in child.winfo_children():
                             if isinstance(sub, (tk.Scale, tk.Label)):
                                 try: sub.configure(state=det_state)
                                 except: pass

        self._update_all_vars_from_model()


    def _on_custom_toggle(self, *args):
        if self._updating_flag: return
        img = self._active()
        if img:
            img.custom = self.custom_var.get()
        self._update_ui_state()


    def _update_info_label(self):
        img = self._active()
        if not img:
            self.lbl_info.config(text="")
            return
        
        txt = ""
        if self.custom_var.get():
            txt = f"Custom | Gray: {self.gray_method_var.get()} | Det: {self.method_var.get()}"
        else:
            if img.preprocessed.img is not None:
                txt = getattr(img, 'auto_info', f"Auto Mode | Texture: {getattr(img.preprocessed, 'texture', '?')}")
            else:
                txt = "Auto Detect Mode"
        
        self.lbl_info.config(text=txt)


    def _on_preprocess_change(self, *args):
        img = self._active()
        if img is None: return
        self._write_preprocess_params(img)

    
    def _on_detect_change(self, *args):
        img = self._active()
        if img is None: return
        self._write_detect_params(img)


    def _update_all_vars_from_model(self):
        # We might want to refresh sliders if model changed externally 
        # But usually UI drives Model. 
        # This is strictly when we switch images or toggle custom.
        img = self._active()
        if not img or self._updating_flag: return

        # IMPORTANT: Set _updating_flag to avoid trigger loops if we set vars here
        self._updating_flag = True
        try:
            p = img.preprocess_params
            self.gray_method_var.set(p.gray_method)
            self.use_clahe_var.set(p.use_clahe)
            self.clahe_clip_var.set(p.clahe_clip)
            self.clahe_grid_var.set(p.clahe_grid)

            d = img.detect_params
            self.method_var.set(d.method)
            self.th_mode_var.set(d.th_mode)
            self.fixed_th_var.set(d.fixed_th)
            self.zk_var.set(d.z_k)
            self.percentile_var.set(d.percentile)
            self.use_lbp_var.set(d.use_lbp)
            self.lbp_rad_var.set(d.lbp_rad)
            self.lbp_points_var.set(d.lbp_points)
            self.min_area_var.set(d.min_area)
            self.max_area_var.set(d.max_area)
            self.elemsize_var.set(d.elemsize)
            self.open_iter_var.set(d.open_iter)
            self.close_iter_var.set(d.close_iter)
            self.block_size_var.set(d.block_size)
            self.c_var.set(d.c)
            self.edge_t1_var.set(d.edge_t1)
            self.edge_t2_var.set(d.edge_t2)
            self.edge_kernel_var.set(d.edge_kernel)
            self.edge_density_th_var.set(d.edge_density_th)
        except Exception as e:
            print(f"Update VARS error: {e}")
        finally:
            self._updating_flag = False


    def _write_preprocess_params(self, img: ImageState):
        if self._updating_flag: return
        img.preprocess_params.gray_method = self.gray_method_var.get()
        img.preprocess_params.use_clahe = self.use_clahe_var.get()
        img.preprocess_params.clahe_clip = self.clahe_clip_var.get()
        img.preprocess_params.clahe_grid = self.clahe_grid_var.get()
    

    def _write_detect_params(self, img: ImageState):
        if self._updating_flag: return
        d = img.detect_params
        d.method = self.method_var.get()
        d.th_mode = self.th_mode_var.get()
        d.fixed_th = self.fixed_th_var.get()
        d.z_k = self.zk_var.get()
        d.percentile = self.percentile_var.get()
        d.use_lbp = self.use_lbp_var.get()
        d.lbp_rad = self.lbp_rad_var.get()
        d.lbp_points = self.lbp_points_var.get()
        d.min_area = self.min_area_var.get()
        d.max_area = self.max_area_var.get()
        d.elemsize = self.elemsize_var.get()
        d.open_iter = self.open_iter_var.get()
        d.close_iter = self.close_iter_var.get()
        d.block_size = self.block_size_var.get()
        d.c = self.c_var.get()
        d.edge_t1 = self.edge_t1_var.get()
        d.edge_t2 = self.edge_t2_var.get()
        d.edge_kernel = self.edge_kernel_var.get()
        d.edge_density_th = self.edge_density_th_var.get()


    def _restore_preprocess(self):
        self._updating_flag = True
        self.gray_method_var.set(DEF_PREPROCESS_PARAMS.gray_method)
        self.use_clahe_var.set(DEF_PREPROCESS_PARAMS.use_clahe)
        self.clahe_clip_var.set(DEF_PREPROCESS_PARAMS.clahe_clip)
        self.clahe_grid_var.set(DEF_PREPROCESS_PARAMS.clahe_grid)
        self._updating_flag = False
        self._on_preprocess_change()
    

    def _restore_detect(self):
        self._updating_flag = True
        self.method_var.set(DEF_DETECT_PARAMS.method)
        self.th_mode_var.set(DEF_DETECT_PARAMS.th_mode)
        self.fixed_th_var.set(DEF_DETECT_PARAMS.fixed_th)
        self.zk_var.set(DEF_DETECT_PARAMS.z_k)
        self.percentile_var.set(DEF_DETECT_PARAMS.percentile)
        self.use_lbp_var.set(DEF_DETECT_PARAMS.use_lbp)
        self.lbp_rad_var.set(DEF_DETECT_PARAMS.lbp_rad)
        self.lbp_points_var.set(DEF_DETECT_PARAMS.lbp_points)
        self.min_area_var.set(DEF_DETECT_PARAMS.min_area)
        self.max_area_var.set(DEF_DETECT_PARAMS.max_area)
        self.elemsize_var.set(DEF_DETECT_PARAMS.elemsize)
        self.open_iter_var.set(DEF_DETECT_PARAMS.open_iter)
        self.close_iter_var.set(DEF_DETECT_PARAMS.close_iter)
        self.block_size_var.set(DEF_DETECT_PARAMS.block_size)
        self.c_var.set(DEF_DETECT_PARAMS.c)
        self.edge_t1_var.set(DEF_DETECT_PARAMS.edge_t1)
        self.edge_t2_var.set(DEF_DETECT_PARAMS.edge_t2)
        self.edge_kernel_var.set(DEF_DETECT_PARAMS.edge_kernel)
        self.edge_density_th_var.set(DEF_DETECT_PARAMS.edge_density_th)
        self._updating_flag = False
        self._on_detect_change()


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
        self._detect_active()


    def _plot_histogram(self):
        img = self._active()
        if img and self.processor:
            self.processor.show_variance_histogram(img)

    
    def _run_detect(self, img: ImageState):
        if img.preprocessed.img is None: return 
        self._write_detect_params(img)
        if self.processor:
            try:        
                img.detected = self.processor.detect(img)
            except Exception as e:
                print(f"Detect Error: {e}")
                # Print stack trace
                import traceback
                traceback.print_exc()
