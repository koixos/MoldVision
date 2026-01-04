import tkinter as tk
from tkinter import filedialog, messagebox
from ..utils.image_loader import EXTS, load_image
from ..state import ImageState, AppState
import os

class LeftSidebar(tk.Frame):
    def __init__(self, parent, state: AppState, width=300):
        super().__init__(parent, width=width, bg="#f2f2f2")
        self.pack_propagate(False)

        self.state = state

        self._build_ui()
    
    # ====================== UI ====================== 

    def _build_ui(self):
        title = tk.Label(
            self,
            text="Images",
            bg="#f2f2f2",
            fg="#333",
            font=("Segoe UI", 14, "bold")
        )
        title.pack(anchor="w", padx=16, pady=(16, 8))

        load_btn = tk.Button(
            self,
            text=" + Load Images",
            command=self._load_images,
            relief="flat",
            bg="#e6e6e6",
            fg="#222",
            cursor="hand2"
        )
        load_btn.pack(fill="x", padx=16, pady=(0, 12))

        # original imgs
        self._section_label("Original Images")
        self.original_container = self._scrollable_container()

        # processed imgs
        self._section_label("Processed Images")
        self.processed_container = self._scrollable_container()

    def _section_label(self, text):
        lbl = tk.Label(
            self,
            text=text,
            bg="#f2f2f2",
            fg="#666",
            font=("Segoe UI", 10, "bold")
        )
        lbl.pack(anchor="w", padx=16, pady=(12, 4))

    def _scrollable_container(self):
        outer = tk.Frame(self, bg="#f2f2f2")
        outer.pack(fill="both", expand=False, padx=12)

        canvas = tk.Canvas(
            outer,
            bg="#f2f2f2",
            highlightthickness=0,
            height=180
        )
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)

        inner = tk.Frame(canvas, bg="#f2f2f2")

        inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")        

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
                if self.state.images:
                    self.state.set_active(len(self.state.images) - 1)
            except Exception as e:
                messagebox.showerror("Load error", str(e))
        
        self.refresh()

    def refresh(self):
        self._clear(self.original_container)
        self._clear(self.processed_container)

        for idx, img_st in enumerate(self.state.images):
            self._add_item(
                self.original_container,
                idx,
                img_st.filename,
                processed=False
            )

            if img_st.detected is not None:
                self._add_item(
                    self.processed_container,
                    idx,
                    f"processed_{img_st.filename}",
                    processed=True
                )
    
    def _add_item(self, parent, index, text, processed):
        is_active = (index == self.state.active_index)
        bg = "#dfefff" if is_active else "#f7f7f7"

        row = tk.Frame(parent, bg=bg)
        row.pack(fill="x", pady=1)

        label = tk.Label(
            row,
            text=text,
            bg=bg,
            fg="#222",
            anchor="w",
            padx=6,
            cursor="hand2"
        )
        label.pack(side="left", fill="x", expand=True)

        delete_btn = tk.Label(
            row,
            text="\U0001f5d1",
            bg=bg,
            fg="#aa0000",
            cursor="hand2"
        )
        delete_btn.pack(side="right", padx=6)

        # interactions
        label.bind("<Button-1>", lambda e, i=index: self._set_active(i))

        def on_delete(e, i=index):
            e.widget.master.focus_set()
            self._delete(i)
            return "break"
        
        delete_btn.bind("<Button-1>", on_delete)

        row.bind("<Enter>", lambda e: row.config(bg="#eaeaea"))
        label.bind("<Enter>", lambda e: row.config(bg=bg))

    def _set_active(self, index):
        self.state.set_active(index)
        self.refresh()

    def _delete(self, index):
        self.state.remove_image(index)
        self.refresh()

    def _clear(self, frame: tk.Frame):
        for w in frame.winfo_children():
            w.destroy()
        