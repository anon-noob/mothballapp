import tkinter as tk
from CodeCell import Page

class Credits:
    TEXT = """# Credits
To CyrenArkade for the original Mothball concept (in the form of a discord bot): [https://github.com/CyrenArkade/mothball](https://github.com/CyrenArkade/mothball)
To anonnoob (myself) for updating Mothball and creating the GUI version
To hammsamichz for helping with the help pages
To everyone else who has contributed to Mothball, whether it be through code, suggestions, or bug reports
And to you for using Mothball, thank you!

# News
Please stop watching the minecraft movie...

Thank Erasmian (youtube: [https://www.youtube.com/@3rasmian](https://www.youtube.com/@3rasmian)) for helping us revert back to good movement mechanics. 
"""
    def __init__(self, master, options):
        self.top = tk.Toplevel(master)
        self.text = Page(self.top, options, scrollable=True)
        self.text.mainframe.pack_propagate(True)
        self.text.mainframe.pack(fill="both", expand=True)
        self.text.parse_text(Credits.TEXT)
        self.text.finalize()

if __name__ == "__main__":
    root = tk.Tk()
    Credits(root, {})
    root.mainloop()
