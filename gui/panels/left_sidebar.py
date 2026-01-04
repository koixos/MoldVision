import tkinter as tk
from tkinter import filedialog, messagebox
from ..utils.image_loader import EXTS, load_image
from ..state import ImageState, AppState
import os

class LeftSidebar(tk.Frame):
    def __init__(self, parent, state: AppState, width=900): # Increased width
        super().__init__(parent, width=width, bg="#f2f2f2")
        self.pack_propagate(False) # Maybe set to True if we want auto-resize? 
                                   # But user asked for specific layout. 
                                   # Let's keep False but make it wide enough.

        self.state = state
        self._img_refs = [] # For saving references to icons

        self._build_ui()
    
    # ====================== UI ====================== 

    def _build_ui(self):
        # Top Header
        header = tk.Frame(self, bg="#f2f2f2")
        header.pack(fill="x", padx=16, pady=16)
        
        title = tk.Label(header, text="Project Images", bg="#f2f2f2", fg="#333", font=("Segoe UI", 14, "bold"))
        title.pack(side="left")

        load_btn = tk.Button(header, text=" + Load ", command=self._load_images, 
                             relief="flat", bg="#e6e6e6", fg="#222", cursor="hand2")
        load_btn.pack(side="right")

        # Main Content: 3 Columns
        content_frame = tk.Frame(self, bg="#f2f2f2")
        content_frame.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        # Helper to build column
        def build_column(parent, title):
            frame = tk.Frame(parent, bg="#f2f2f2", bd=1, relief="solid") # slightly visible border
            frame.pack(side="left", fill="both", expand=True, padx=4)
            
            # Column Header
            lbl = tk.Label(frame, text=title, bg="#e0e0e0", fg="#333", font=("Segoe UI", 10, "bold"), pady=6)
            lbl.pack(fill="x")
            
            # Scrollable List
            list_container = self._scrollable_container(frame)
            return list_container

        self.col_orig = build_column(content_frame, "Original")
        self.col_proc = build_column(content_frame, "Preprocessed")
        self.col_res = build_column(content_frame, "Result")

    def _scrollable_container(self, parent):
        outer = tk.Frame(parent, bg="#ffffff")
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg="#ffffff", highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        
        inner = tk.Frame(canvas, bg="#ffffff")
        
        # Proper scroll region update
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mousewheel binding
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Pack
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Force inner frame width to match canvas to avoid layout weirdness
        def _configure_width(event):
            canvas.itemconfig(canvas.create_window((0,0), window=inner, anchor='nw'), width=event.width)
        canvas.bind("<Configure>", _configure_width)

        return inner
    
    # ====================== LOGIC ====================== 

    def _load_images(self):
        paths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Images", "*" + " *".join(EXTS))]
        )

        for path in paths:
            try:
                img = load_image(path)
                state = ImageState(
                    path=path,
                    filename=os.path.basename(path),
                    original=img
                )
                self.state.add_image(state)
            except Exception as e:
                messagebox.showerror("Load error", str(e))
        
        if paths and self.state.images:
             self.state.set_active(len(self.state.images) - 1)
        # Refresh handled by listener in app.py or manual? 
        # app.py listens to state changes. add_image triggers notify. 
        # So we don't need manual refresh if set_active also notifies.
        # But let's check state.py logic. add_image notifies. set_active notifies.
        # Double notify is fine.

    def refresh(self):
        # Clear all
        for c in [self.col_orig, self.col_proc, self.col_res]:
            for w in c.winfo_children(): w.destroy()
        
        self._img_refs = []

        for idx, img_st in enumerate(self.state.images):
            # 1. Original
            self._add_item(self.col_orig, idx, img_st, img_st.filename, icon_img=img_st.original)
            
            # 2. Preprocessed
            if img_st.preprocessed is not None:
                self._add_item(self.col_proc, idx, img_st, f"prep_{img_st.filename}", icon_img=img_st.preprocessed)
            
            # 3. Result
            if img_st.detected is not None:
                self._add_item(self.col_res, idx, img_st, f"res_{img_st.filename}", icon_img=img_st.detected)
    
    def _add_item(self, parent, index, img_st, text, icon_img=None):
        is_active = (index == self.state.active_index)
        bg = "#dfefff" if is_active else "#f7f7f7"

        row = tk.Frame(parent, bg=bg, pady=2)
        row.pack(fill="x", pady=1, padx=2)

        # Thumbnail
        if icon_img is not None:
             import cv2
             from PIL import Image, ImageTk
             try:
                thumb_bgr = cv2.resize(icon_img, (32, 32))
                thumb_rgb = cv2.cvtColor(thumb_bgr, cv2.COLOR_BGR2RGB)
                thumb_pil = Image.fromarray(thumb_rgb)
                thumb_tk = ImageTk.PhotoImage(thumb_pil)
                
                self._img_refs.append(thumb_tk)
                
                lbl = tk.Label(row, image=thumb_tk, bg=bg)
                lbl.pack(side="left", padx=2)
                lbl.bind("<Button-1>", lambda e, i=index: self._set_active(i))
             except Exception:
                 pass

        # Text
        lbl_text = tk.Label(row, text=text, bg=bg, fg="#222", anchor="w", font=("Segoe UI", 9))
        lbl_text.pack(side="left", fill="x", expand=True, padx=4)
        lbl_text.bind("<Button-1>", lambda e, i=index: self._set_active(i))
        
        # Delete (Only on original col? Or all? Usually manage "images" not views. 
        # But if we delete in one view, we delete the image state effectively.
        # Let's add delete button only to Original column to keep UI clean, or all.
        # User didn't specify, but safer to have it everywhere or just main.
        # I'll add to all for consistency since they are parallel lists.)
        btn_del = tk.Label(row, text="x", bg=bg, fg="#999", cursor="hand2", font=("Segoe UI", 9))
        btn_del.pack(side="right", padx=4)
        btn_del.bind("<Button-1>", lambda e, i=index: self._delete(i))

        row.bind("<Enter>", lambda e: row.config(bg="#e0e0e0"))
        row.bind("<Leave>", lambda e: row.config(bg=bg))

    def _set_active(self, index):
        self.state.set_active(index)

    def _delete(self, index):
        self.state.remove_image(index)
        