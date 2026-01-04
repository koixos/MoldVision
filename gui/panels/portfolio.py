import tkinter as tk
from tkinter import filedialog
from ..state import AppState
from PIL import Image, ImageTk
import cv2

class Portfolio(tk.Frame):
    def __init__(self, parent, state: AppState):
        super().__init__(parent, bg="#ededed")
        self.state = state

        self._img_refs = {}
        self._build_ui()
        # No auto-refresh needed, handled by state listener in app.py calling refresh()

    # ====================== UI ====================== 

    def _build_ui(self):
        # 1. Image Content Area (Horizontal)
        content = tk.Frame(self, bg="#ededed")
        content.pack(side="top", fill="both", expand=True, padx=12, pady=12)

        # We want 3 columns: Original, Preprocessed, Output
        self.sections = []
        
        # Helper to create a section column
        def create_column(parent, title, getter, save_name):
            col = tk.Frame(parent, bg="#ffffff")
            col.pack(side="left", fill="both", expand=True, padx=4)
            
            # Header
            header = tk.Frame(col, bg="#ffffff")
            header.pack(fill="x", padx=8, pady=6)
            
            lbl = tk.Label(header, text=title, bg="#ffffff", fg="#222", font=("Segoe UI", 11, "bold"))
            lbl.pack(side="left")
            
            save_btn = tk.Label(header, text="\U0001f4be", bg="#ffffff", fg="#444", cursor="hand2")
            save_btn.pack(side="right")
            save_btn.bind("<Button-1>", lambda e: self._save_single(getter, save_name))
            
            # Canvas
            canvas = tk.Canvas(col, bg="#f5f5f5", highlightthickness=0)
            canvas.pack(fill="both", expand=True, padx=8, pady=(0, 8))
            
            # Store metadata on wrapper or creating verify object
            return {
                "canvas": canvas,
                "getter": getter
            }

        # Create the 3 columns
        self.sections.append(create_column(content, "Original Image", lambda s: s.original, lambda s: s.filename))
        self.sections.append(create_column(content, "Preprocessed", lambda s: s.preprocessed, lambda s: f"preprocessed_{s.filename}"))
        self.sections.append(create_column(content, "Result", lambda s: s.detected, lambda s: f"output_{s.filename}"))


        # 2. Bottom Navigation Bar
        nav_bar = tk.Frame(self, bg="#d9d9d9", height=50)
        nav_bar.pack(side="bottom", fill="x")
        nav_bar.pack_propagate(False)

        # Center container for buttons
        center_frame = tk.Frame(nav_bar, bg="#d9d9d9")
        center_frame.pack(expand=True)

        btn_font = ("Segoe UI", 14, "bold")

        self.btn_prev = tk.Button(center_frame, text=" < ", font=btn_font, command=self._prev_image, 
                                  relief="flat", bg="#cccccc", width=6)
        self.btn_prev.pack(side="left", padx=20)

        self.btn_next = tk.Button(center_frame, text=" > ", font=btn_font, command=self._next_image, 
                                  relief="flat", bg="#cccccc", width=6)
        self.btn_next.pack(side="left", padx=20)

    # ====================== LOGIC ====================== 

    def _prev_image(self):
        if not self.state.images:
            return
        new_idx = max(0, self.state.active_index - 1)
        self.state.set_active(new_idx)

    def _next_image(self):
        if not self.state.images:
            return
        new_idx = min(len(self.state.images) - 1, self.state.active_index + 1)
        self.state.set_active(new_idx)

    def refresh(self):
        img_st = self.state.active()
        
        # Update buttons state if needed (optional visual polish)
        if not self.state.images:
             self.btn_prev.config(state="disabled")
             self.btn_next.config(state="disabled")
        else:
             self.btn_prev.config(state="normal" if self.state.active_index > 0 else "disabled")
             self.btn_next.config(state="normal" if self.state.active_index < len(self.state.images) - 1 else "disabled")

        for sec in self.sections:
            canvas = sec["canvas"]
            canvas.delete("all")
            
            if img_st is None:
                continue

            img = sec["getter"](img_st)
            if img is None:
                continue

            self._draw_image(canvas, img)

    def _draw_image(self, canvas: tk.Canvas, img_bgr):
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        h, w = img_rgb.shape[:2]

        cw = max(canvas.winfo_width(), 1)
        ch = max(canvas.winfo_height(), 1)

        scale = min(cw / w, ch / h, 1.0)
        nw, nh = int(w * scale), int(h * scale)

        img_resized = cv2.resize(
            img_rgb,
            (nw, nh),
            interpolation=cv2.INTER_AREA
        )

        img_pil = Image.fromarray(img_resized)
        img_tk = ImageTk.PhotoImage(img_pil)

        canvas.create_image(
            cw // 2,
            ch // 2,
            image=img_tk,
            anchor="center"
        )

        self._img_refs[canvas] = img_tk


    # ====================== SAVE ====================== 

    def _save_single(self, getter, name_fn):
        img_st = self.state.active()
        if img_st is None:
            return
        
        img = getter(img_st)
        if img is None:
            return
        
        default = name_fn(img_st)
        if callable(default): # Handle lambda that returns string
             default = default(img_st)

        path = filedialog.asksaveasfilename(
            initialfile=default,
            defaultextension=".png",
            filetypes=[("PNG", "*.png")]
        )
        if path:
            cv2.imwrite(path, img) # Fixed: verify it was cv2.imread which is wrong for saving