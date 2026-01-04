import tkinter as tk
from .state import AppState
#from pipeline.adapter import PipelineAdapter
from .panels.left_sidebar import LeftSidebar
from .panels.right_sidebar import RightSidebar
from .panels.portfolio import Portfolio

class MoldVisionApp:
    def __init__(self, master):
        self.master = master
        self.master.title("MoldVisionGUI")
        self.master.geometry("1600x900")

        self.state = AppState()
        #self.pipeline = PipelineAdapter((), ())

        self.state.add_listener(self.active_changed)
        self.build_ui()

    def build_ui(self):
        self.left = LeftSidebar(self.master, self.state)
        self.left.pack(side="left", fill="y")    

        self.right = RightSidebar(self.master, self.state)
        self.right.pack(side="right", fill="y")

        self.portfolio = Portfolio(self.master, self.state)
        self.portfolio.pack(side="left", fill="both", expand=True)

    def active_changed(self):
        self.left.refresh()
        self.portfolio.refresh()

if __name__ == "__main__":
    master = tk.Tk()
    MoldVisionApp(master)
    master.mainloop()