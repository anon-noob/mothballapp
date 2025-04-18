import tkinter as tk
from CodeCell import Page
import requests

class Version:
        
    def __init__(self, version, master=None):
        self.top = tk.Toplevel(master)
        self.text = Page(self.top, scrollable=True)
        self.text.mainframe.pack()
        a,b = self.check_updates()
        self.text.parse_text(f"""You are on Mothball version {version}\nLatest version {a} changelog:\n{b}""")
        self.text.finalize()

    def check_updates(self):
        try:
            response = requests.get("https://api.github.com/repos/anon-noob/mothballapp/releases")
            if response.status_code == 200:
                releases = response.json()
                releases = sorted(releases, key=lambda r: r["tag_name"], reverse=True)
                latest_version = releases[0]

                text = latest_version.get('body')
                
            return (latest_version['tag_name'], text)
        except Exception as e:
            return ("Unable to get latest version", "")
        
if __name__ == "__main__":
    root = tk.Tk()
    Version("BETA", root)
    root.mainloop()
