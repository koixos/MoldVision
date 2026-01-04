import tkinter as tk
from gui.app import MoldVisionApp
#from Processor import execute

if __name__ == '__main__':
    root = tk.Tk()
    root.tk.call('tk', 'scaling', 1.0)

    app = MoldVisionApp(root)
    root.mainloop()
    
    '''for i in range (1,4):
        img_path = "./data/" + str(i) + ".jpg"
        execute(img_path)'''
