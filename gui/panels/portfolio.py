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

        self.after(200, self._auto_refresh)

    # ====================== UI ====================== 

    def _build_ui(self):
        self._build_section(
            title="Original Image",
            getter=lambda img: img.original,
            save_name=lambda img: img.filename
        )

        self._build_section(
            title="Preprocessed Image",
            getter=lambda img: img.preprocessed,
            save_name=lambda img: f"preprocessed_{img.filename}"
        )

        tk.Frame(self, height=2, bg="#cccccc").pack(fill="x", pady=6)
        
        self._build_section(
            title="Detection Output",
            getter=lambda img: img.detected,
            save_name=lambda img: f"output_{img.filename}"
        )

    def _build_section(self, title, getter, save_name):
        frame = tk.Frame(self, bg="#ffffff")
        frame.pack(fill="both", expand=True, padx=12, pady=6)

        header = tk.Frame(frame, bg="#ffffff")
        header.pack(fill="x", padx=8, pady=6)

        lbl = tk.Label(
            header,
            text=title,
            bg="#ffffff",
            fg="#222",
            font=("Segoe UI", 11, "bold")
        )
        lbl.pack(side="left")

        save_btn = tk.Label(
            header,
            text="\U0001f4be",
            bg="#ffffff",
            fg="#444",
            cursor="hand2"
        )
        save_btn.pack(side="right")
        save_btn.bind(
            "<Button-1>",
            lambda e, g=getter, s=save_name: self._save_single(g, s)
        )

        canvas = tk.Canvas(
            frame,
            bg="#f5f5f5",
            highlightthickness=0
        )
        canvas.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        frame.canvas = canvas
        frame.getter = getter
        frame.save_name = save_name

        if not hasattr(self, "sections"):
            self.sections = []
        self.sections.append(frame)

    # ====================== LOGIC ====================== 

    def _auto_refresh(self):
        self.refresh()
        self.after(200, self._auto_refresh)

    def refresh(self):
        img_st = self.state.active()
        for sec in getattr(self, "sections", []):
            sec.canvas.delete("all")
            if img_st is None:
                continue

            img = sec.getter(img_st)
            if img is None:
                continue

            self._draw_image(sec.canvas, img)

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

        path = filedialog.asksaveasfilename(
            initialfile=default,
            defaultextension=".png",
            filetypes=[("PNG", "*.png")]
        )
        if path:
            cv2.imread(path, img)