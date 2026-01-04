import tkinter as tk
from tkinter import filedialog, messagebox
from ..utils.image_loader import EXTS, load_image
from ..state import ImageState, AppState
import os

class LeftSidebar(tk.Frame):
    def __init__(self, parent, state: AppState, width=380): # Adjusted width
        super().__init__(parent, width=width, bg="#f2f2f2")
        self.pack_propagate(False)

        self.state = state
        self._img_refs = [] 

        self._build_ui()
    
    # ====================== UI ====================== 

    def _build_ui(self):
        # Top Header
        header = tk.Frame(self, bg="#f2f2f2")
        header.pack(fill="x", padx=8, pady=16)
        
        title = tk.Label(header, text="Images", bg="#f2f2f2", fg="#333", font=("Segoe UI", 14, "bold"))
        title.pack(side="left")

        load_btn = tk.Button(header, text=" + ", command=self._load_images, 
                             relief="flat", bg="#e6e6e6", fg="#222", cursor="hand2", width=4)
        load_btn.pack(side="right")

        # Table Header
        tbl_head = tk.Frame(self, bg="#e0e0e0")
        tbl_head.pack(fill="x", padx=8)
        
        def h_col(text, weight=1):
            f = tk.Frame(tbl_head, bg="#e0e0e0")
            f.pack(side="left", fill="x", expand=(weight>0))
            tk.Label(f, text=text, bg="#e0e0e0", font=("Segoe UI", 9, "bold")).pack(anchor="center")
            
        h_col("Original", 1) # Fuller width for name
        h_col("Prep", 0)     # Fixed width mostly
        h_col("Result", 0)   # Fixed width mostly

        # Scrollable Area
        self.list_container = self._scrollable_container()


    def _scrollable_container(self):
        outer = tk.Frame(self, bg="#ffffff")
        outer.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.canvas = tk.Canvas(outer, bg="#ffffff", highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        
        self.inner = tk.Frame(self.canvas, bg="#ffffff")
        
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Width sync
        def _configure_width(event):
            self.canvas.itemconfig(self.canvas.create_window((0,0), window=self.inner, anchor='nw'), width=event.width)
        self.canvas.bind("<Configure>", _configure_width)

        # Mousewheel - Bind on hover
        self.bind("<Enter>", self._bind_wheel)
        self.bind("<Leave>", self._unbind_wheel)
        
        return self.inner

    def _bind_wheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _unbind_wheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    # ====================== LOGIC ====================== 

    def _load_images(self):
        paths = filedialog.askopenfilenames(title="Select Images", filetypes=[("Images", "*" + " *".join(EXTS))])
        for path in paths:
            try:
                img = load_image(path)
                state = ImageState(path=path, filename=os.path.basename(path), original=img)
                self.state.add_image(state)
            except Exception as e:
                messagebox.showerror("Load error", str(e))
        
        if paths and self.state.images:
             self.state.set_active(len(self.state.images) - 1)

    def refresh(self):
        for w in self.inner.winfo_children(): w.destroy()
        self._img_refs = []

        for idx, img_st in enumerate(self.state.images):
            self._add_row(idx, img_st)

    def _add_row(self, index, img_st):
        is_active = (index == self.state.active_index)
        bg = "#dfefff" if is_active else "#ffffff"
        
        row = tk.Frame(self.inner, bg=bg, pady=4, bd=1, relief="flat")
        row.pack(fill="x", pady=1)

        # Column structure using grid inside row for alignment, or pack logic
        # Pack logic with fixed widths for icons might be easier for alignment
        
        # Col 3: Result (Right)
        # Col 2: Prep (Right)
        # Col 1: Original (Fill rest)
        
        # Helper for Icon Cell
        def icon_cell(parent, img, side="right"):
            f = tk.Frame(parent, bg=bg, width=40, height=40)
            f.pack_propagate(False)
            f.pack(side=side, padx=4)
            
            if img is not None:
                import cv2
                from PIL import Image, ImageTk
                try:
                    thumb_bgr = cv2.resize(img, (32, 32))
                    thumb_rgb = cv2.cvtColor(thumb_bgr, cv2.COLOR_BGR2RGB)
                    thumb_pil = Image.fromarray(thumb_rgb)
                    thumb_tk = ImageTk.PhotoImage(thumb_pil)
                    self._img_refs.append(thumb_tk)
                    
                    lbl = tk.Label(f, image=thumb_tk, bg=bg)
                    lbl.pack(expand=True)
                    lbl.bind("<Button-1>", lambda e, i=index: self._set_active(i))
                except: pass
            return f

        # Delete Btn
        btn_del = tk.Label(row, text="x", bg=bg, fg="#999", cursor="hand2")
        btn_del.pack(side="right", padx=6)
        btn_del.bind("<Button-1>", lambda e, i=index: self._delete(i))

        # Result Icon
        icon_cell(row, img_st.detected, side="right")
        
        # Prep Icon
        icon_cell(row, img_st.preprocessed, side="right")

        # Original Icon + Text (Left)
        f_orig = tk.Frame(row, bg=bg)
        f_orig.pack(side="left", fill="x", expand=True, padx=4)
        
        # Orig Icon
        icon_cell(f_orig, img_st.original, side="left")
        
        # Filename
        lbl_name = tk.Label(f_orig, text=img_st.filename, bg=bg, fg="#222", anchor="w", font=("Segoe UI", 9))
        lbl_name.pack(side="left", fill="x", expand=True)
        
        # Bindings
        for w in [row, f_orig, lbl_name]:
            w.bind("<Button-1>", lambda e, i=index: self._set_active(i))
        
        row.bind("<Enter>", lambda e: row.config(bg="#e8e8e8"))
        row.bind("<Leave>", lambda e: row.config(bg=bg))


    def _set_active(self, index):
        self.state.set_active(index)

    def _delete(self, index):
        self.state.remove_image(index)
        