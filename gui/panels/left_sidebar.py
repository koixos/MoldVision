import tkinter as tk
from tkinter import filedialog, messagebox
from ..utils.image_loader import EXTS, load_image
from ..state import ImageState, AppState
import os

class LeftSidebar(tk.Frame):
    def __init__(self, parent, state: AppState, width=380):
        super().__init__(parent, width=width, bg="#f2f2f2")
        self.pack_propagate(False)

        self.state = state
        self.is_collapsed = False
        self.expanded_width = width
        self.collapsed_width = 70
        self._img_refs = [] 

        self._build_ui()
    
    # ====================== UI ====================== 

    def _build_ui(self):
        # Top Header Area
        self.top_frame = tk.Frame(self, bg="#f2f2f2")
        self.top_frame.pack(fill="x", padx=4, pady=8)
        
        # Toggle Button (Left aligned)
        self.btn_toggle = tk.Button(self.top_frame, text="<<", command=self._toggle_sidebar,
                                    relief="flat", bg="#e0e0e0", fg="#555", cursor="hand2", width=3)
        self.btn_toggle.pack(side="left")

        # Title (Hidden if collapsed)
        self.lbl_title = tk.Label(self.top_frame, text="Images", bg="#f2f2f2", fg="#333", font=("Segoe UI", 12, "bold"))
        self.lbl_title.pack(side="left", padx=8)

        # Load Button (Right aligned)
        self.btn_load = tk.Button(self.top_frame, text="+", command=self._load_images, 
                             relief="flat", bg="#e6e6e6", fg="#222", cursor="hand2", width=3)
        self.btn_load.pack(side="right")

        # Table Header Frame
        self.tbl_head = tk.Frame(self, bg="#e0e0e0")
        self.tbl_head.pack(fill="x", padx=4, pady=(8, 0))

        # Scrollable Area
        self.list_container = self._scrollable_container()

    def _update_header(self):
        # Clear existing header
        for w in self.tbl_head.winfo_children(): w.destroy()
        
        # Configure Top UI based on collapse
        if self.is_collapsed:
            self.lbl_title.pack_forget()
            self.btn_load.pack_forget() # Hide load in collapsed? Or keep small? 
            # User said "only orig img icons visible".
            # Let's keep toggle visible.
            self.btn_toggle.config(text=">>")
            
            # Allow load? simplified: hide load for clean look or put below.
            # Let's hide load to save space/complexity, user can expand to load.
        else:
            self.lbl_title.pack(side="left", padx=8)
            self.btn_load.pack(side="right")
            self.btn_toggle.config(text="<<")

        # Configure Table Header
        # Configure Table Header
        if self.is_collapsed:
            self.tbl_head.grid_columnconfigure(0, weight=1) 
            for c in [1, 2, 3, 4]: self.tbl_head.grid_columnconfigure(c, weight=0, minsize=0)
            
            f = tk.Frame(self.tbl_head, bg="#e0e0e0", bd=1, relief="solid")
            f.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
            tk.Label(f, bg="#e0e0e0", font=("Segoe UI", 9, "bold")).pack(expand=True)
            
        else:
            # 3 Columns Equal Width + Delete + Scrollbar Spacer
            self.tbl_head.grid_columnconfigure(0, weight=1, uniform="h_cols") 
            self.tbl_head.grid_columnconfigure(1, weight=1, uniform="h_cols") 
            self.tbl_head.grid_columnconfigure(2, weight=1, uniform="h_cols")
            self.tbl_head.grid_columnconfigure(3, weight=0, minsize=30) # Delete
            self.tbl_head.grid_columnconfigure(4, weight=0, minsize=17) # Scrollbar Spacer
            
            def h_lbl(text, col):
                f = tk.Frame(self.tbl_head, bg="#e0e0e0", height=24, bd=1, relief="solid")
                f.pack_propagate(False)
                f.grid(row=0, column=col, sticky="nsew", padx=0, pady=0)
                tk.Label(f, text=text, bg="#e0e0e0", font=("Segoe UI", 9, "bold")).pack(expand=True)

            h_lbl("Original", 0)
            h_lbl("Pre", 1)
            h_lbl("Res", 2)
            
            # Spacer for Delete column (empty border)
            f = tk.Frame(self.tbl_head, bg="#e0e0e0", bd=1, relief="solid") 
            f.grid(row=0, column=3, sticky="nsew")
             
            # Spacer for Scrollbar (invisible)
            tk.Frame(self.tbl_head, bg="#f2f2f2", width=17).grid(row=0, column=4)

    def _scrollable_container(self):
        outer = tk.Frame(self, bg="#ffffff")
        outer.pack(fill="both", expand=True, padx=4, pady=4)

        self.canvas = tk.Canvas(outer, bg="#ffffff", highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        
        self.inner = tk.Frame(self.canvas, bg="#ffffff")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _configure_width(event):
            self.canvas.itemconfig(self.canvas.create_window((0,0), window=self.inner, anchor='nw'), width=event.width)
        self.canvas.bind("<Configure>", _configure_width)

        # Fix: Bind to top level to ensure capture
        self.bind("<Enter>", self._bind_wheel)
        self.bind("<Leave>", self._unbind_wheel)
        
        return self.inner

    def _bind_wheel(self, event):
        # Bind to the entire application/root to catch all mousewheel events when hovering sidebar
        top = self.winfo_toplevel()
        top.bind("<MouseWheel>", self._on_mousewheel)
    
    def _unbind_wheel(self, event):
        top = self.winfo_toplevel()
        top.unbind("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    # ====================== LOGIC ====================== 

    def _toggle_sidebar(self):
        self.is_collapsed = not self.is_collapsed
        target_w = self.collapsed_width if self.is_collapsed else self.expanded_width
        self.configure(width=target_w)
        self.refresh()

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
        # Update UI Structure
        self._update_header()
        
        # Clear List
        for w in self.inner.winfo_children(): w.destroy()
        self._img_refs = []

        for idx, img_st in enumerate(self.state.images):
            self._add_row(idx, img_st)

    def _add_row(self, index, img_st):
        is_active = (index == self.state.active_index)
        bg = "#dfefff" if is_active else "#ffffff"
        
        row = tk.Frame(self.inner, bg=bg, pady=2, bd=0)
        row.pack(fill="x", pady=1)
        
        # Helper for Cell with Border
        def make_cell(col, width=None):
            f = tk.Frame(row, bg=bg, bd=1, relief="solid")
            if width:
                f.configure(width=width)
                f.pack_propagate(False)
            f.grid(row=0, column=col, sticky="nsew", padx=0, pady=0)
            f.bind("<Button-1>", lambda e, i=index: self._set_active(i))
            return f

        def add_icon(parent, img):
             if img is not None:
                 import cv2
                 from PIL import Image, ImageTk
                 try:
                    thumb_bgr = cv2.resize(img, (32, 32))
                    thumb_rgb = cv2.cvtColor(thumb_bgr, cv2.COLOR_BGR2RGB)
                    thumb_pil = Image.fromarray(thumb_rgb)
                    thumb_tk = ImageTk.PhotoImage(thumb_pil)
                    self._img_refs.append(thumb_tk)
                    lbl = tk.Label(parent, image=thumb_tk, bg=bg)
                    lbl.pack(expand=True)
                    lbl.bind("<Button-1>", lambda e, i=index: self._set_active(i))
                 except: pass

        if self.is_collapsed:
            # Collapsed Mode: Only Icon, Centered
            row.grid_columnconfigure(0, weight=1)
            c0 = make_cell(0)
            add_icon(c0, img_st.original)
            
        else:
            # Expanded Mode: 3 Cols Equal Width + Delete
            row.grid_columnconfigure(0, weight=1, uniform="cols") 
            row.grid_columnconfigure(1, weight=1, uniform="cols") 
            row.grid_columnconfigure(2, weight=1, uniform="cols")
            row.grid_columnconfigure(3, weight=0, minsize=30) # Delete

            # C0: Original (Icon + Name) - Wait, per user request "equal widths"
            # If equal widths, C0 might be too cramped for text + icon if width is divided by 3 (~120px).
            # Should be OK.
            c0 = make_cell(0)
            f_icon = tk.Frame(c0, bg=bg)
            f_icon.pack(side="left", padx=2)
            add_icon(f_icon, img_st.original)
            
            lbl_name = tk.Label(c0, text=img_st.filename, bg=bg, fg="#222", anchor="w", font=("Segoe UI", 8))
            lbl_name.pack(side="left", fill="x", expand=True)
            lbl_name.bind("<Button-1>", lambda e, i=index: self._set_active(i))

            # C1: Prep
            c1 = make_cell(1)
            add_icon(c1, img_st.preprocessed)

            # C2: Res
            c2 = make_cell(2)
            add_icon(c2, img_st.detected)

            # C3: Delete
            c3 = make_cell(3)
            btn_del = tk.Label(c3, text="x", bg=bg, fg="#999", cursor="hand2")
            btn_del.pack(expand=True)
            btn_del.bind("<Button-1>", lambda e, i=index: self._delete(i))

        row.bind("<Enter>", lambda e: row.config(bg="#e8e8e8"))
        row.bind("<Leave>", lambda e: row.config(bg=bg))

    def _set_active(self, index):
        self.state.set_active(index)

    def _delete(self, index):
        self.state.remove_image(index)
        