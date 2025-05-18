import tkinter as tk
import random
import datetime
import json
import FileHandler
import os, sys

if getattr(sys, "frozen", False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

words_file_path = os.path.join(base_path, "Minigame_Files", "Five Letter Words.txt")
with open(words_file_path) as f:
    FIVE_LETTER_WORDS = list(filter(lambda x: len(x) == 5, f.read().split("\n")))

l = ['58541283804c', '5a24cd629f6b', '5dc81f9b3e54', '960b15c1feb', 'a781dac7e73', '68b076d38b8c', '585235332a05', 'a46503c0c7b', '68b19fe53e2c', 'a8f4da2aa2b', '593cabbbb42c', 'e8c375f0a0', '9498ca8666d', '94963bd16c3', '8ec41ea9e83', 'ae94bd7f1fa', '917a2047dbb', '5f98dae5217c', '593b45ed316c', '68afc34bfb24', '68b341b98d74', 'a78469df454', 'e8c8abd149', '90377a8d4d6', '10c024c6be3', '5a2278be24ec', '90377a8e478', '6b6a7d223c7b', '68b128ecde25', '5a241a923d74', 'a0076d76418', '65f581dc72f4', 'a78469de0da', 'a323d8a4bc5', '1105d6693c5', '8ec58eb3ed3', '91aa91aabe1', 'a3226914ca0', '6998d34efb03', '699aecb4063a', '585236180014', '98c0c84c893', 'a320eaf4b71', '68b0b1b73e6d', '593a92c13a33', '65f493253661', '977d019a653', 'e6c359a91d', '9493a0b90dd', 'a7841839a9c', '60835097dd33', '616d13f45c80', '9ec52626d7f', '6423d89252fb', '6422e9f98f33', '94975ac755d', '5eb041bc1881', '8ec1d505d63', 'a74e129f3eb', '68af1123b078', '1001122b17f', '67c63c6f1fbc']
def e():
    globals()['\x63\x68\x72'] = chr
    globals()['\x69\x6e\x74'] = int
    f = lambda n: (
        str(globals()['\x69\x6e\x74'](n, 16))
    )
    g = lambda s: (
        (lambda i=0, r="": 
            r if i >= len(s) else
            (lambda c: g._setitem(i + len(c), r + globals()['\x63\x68\x72'](int(s[i:i+len(c)]))) or g(s))
            (next(c for c in ('3', '2') if 97 <= int(s[i:i+globals()['\x69\x6e\x74'](c)]) <= 122))
        )()
    )
    globals()['\x65\x6e\x71'] = len
    g._setitem = lambda i, r: setattr(g, "_i", i) or setattr(g, "_r", r) or True
    g._i = 12-3+4-9-5+1
    g._r = ""
    def g(s):
        i = 0
        r = ""
        while i < globals()['\x65\x6e\x71'](s):
            for p in (6/2, 6/3):
                p = list(map(globals()['\x69\x6e\x74'], [p]))[0]
                if i + p <= len(s):
                    y = globals()['\x69\x6e\x74'](s[i:i+p])
                    if 3*(4**2-5)*3-2 <= y <= (10+1)**2+1:
                        r += globals()['\x63\x68\x72'](y)
                        i += p
                        break
            else:
                break
        return r

    return list(map(lambda x: g(f(x)), l))
PARKOUR_FIVE_LETTER_WORDS = e()

class Wordle:

    class MiniKeyboard(tk.Frame):
        def __init__(self, master):
            super().__init__(master, background="gray12")
            self.alphakeys = [
                "QWERTYUIOP",
                "ASDFGHJKL",
                "ZXCVBNM"
            ]
            self.buttons = {}
            self.master = master

            for row_index, row in enumerate(self.alphakeys):
                row_frame = tk.Frame(self)
                row_frame.pack()
                if row_index == 2:
                    self.enter_button = tk.Button(row_frame, text="Enter", width=5, height=1, font=("Ariel", 15, 'bold'), command=lambda k="Return": self.sendkey(k))
                    self.enter_button.pack(side=tk.LEFT)
                
                for key in row:
                    button = tk.Button(row_frame, text=key, width=3, height=1, font=("Ariel", 15, 'bold'), command=lambda k=key: self.sendkey(k))
                    button.pack(side=tk.LEFT)
                    self.buttons[key] = button
                if row_index == 2:
                    self.back_button = tk.Button(row_frame, text="Back", width=5, height=1, font=("Ariel", 15, 'bold'), command=lambda k="BackSpace": self.sendkey(k))
                    self.back_button.pack(side=tk.RIGHT)
        
        def sendkey(self, key):
            a = tk.Event()
            a.keysym = key
            self.master.time(a)
    
    class SideFrame(tk.Frame):
        def __init__(self, master, stats):
            super().__init__(master, background="gray12")
            help_button = tk.Button(self,text="Help", background="gray12", foreground="white", font=("Comic Sans", 24), command=self.openhelp)
            help_button.pack()

            self.wordle_stats = stats
            wins = stats["Wins"]
            lose = stats["Lose"]

            self.win_label = tk.Label(self,text=f"Wins: {wins}",  background="gray12", foreground="white", font=("Comic Sans", 24))
            self.win_label.pack()
            self.lose_label = tk.Label(self,text=f"Lose: {lose}",  background="gray12", foreground="white", font=("Comic Sans", 24))
            self.lose_label.pack()

            self.help_page = False
            self.history_page = False

            self.share = tk.Button(self, text=f"Share", background="gray12", foreground="white", font=("Comic Sans", 24), command=self.to_clipboard)
            self.share.pack()

            self.history = tk.Button(self, text="More", command=self.openhistory, background="gray12", foreground="white", font=("Comic Sans", 24))
            self.history.pack()

            self.clipboard_message = ""
        

        def openhelp(self):
            if not self.help_page:
                self.help_page = HelpPage(self)
                self.help_page.top.bind("<Destroy>", func = self.setfalse)
            else:
                self.help_page.top.focus()
        
        def openhistory(self):
            if not self.history_page:
                self.history_page = HistoryAndMore(self, self.wordle_stats)
                self.history_page.top.bind("<Destroy>", func = self.setfalse2)
            else:
                self.history_page.top.focus()

        def setfalse(self, event):
            self.help_page = False

        def setfalse2(self, event):
            self.history_page = False
        
        def update_count(self, new_stats):
            wins = new_stats["Wins"]
            lose = new_stats["Lose"]
            self.win_label.configure(text=f"Wins: {wins}")
            self.lose_label.configure(text=f"Lose: {lose}")
            self.wordle_stats = new_stats
        
        def to_clipboard(self):
            self.clipboard_clear()
            self.clipboard_append(self.clipboard_message)
            self.update()

    def __init__(self, master):
        FileHandler.create_minigame_directories()
        with open(FileHandler.get_path_to_minigame_stats()) as file:
            self.minigame_stats = json.load(file)
            self.wordle_stats = self.minigame_stats["Parkour Wordle"]

        self.top = tk.Toplevel(master)
        self.top.configure(background="gray12")
        self.top.title("Parkour Wordle")
        self.msg = tk.Label(self.top, text="Parkour Wordle!", background="gray12", foreground="white", font=("Comic Sans", 24))
        self.msg.grid(row=0, columnspan=5, sticky="nsew")

        self.blanks = {j:{i: tk.Button(self.top, text=" ", width=3, height=1,background="gray20", font=("Ariel", 30, 'bold')) for i in range(5)} for j in range(6)}
        for i in self.blanks:
            for j in self.blanks[i]:
                self.blanks[i][j].grid(row=i+1, column=j, sticky="ew")
        
        self.guesses = {i+1:"" for i in range(6)}
        self.next_available: list[int] = [0,0]
        self.guess_count = 0
        self.game_result = None
        self.add_to_stats = True
        self.clipboard_message = ""
        self.top.bind_all("<KeyPress>", self.time)

        self.today = datetime.datetime.now(datetime.timezone.utc).toordinal()
        random.seed(self.today)

        self.secret_word = random.choice(PARKOUR_FIVE_LETTER_WORDS)
        self.typed_word = ""

        self.positions = {}
        self.counts = {}

        for i,p in enumerate(self.secret_word):
            try:
                self.positions[i] = p
                self.counts[p] += 1
            except:
                self.counts[p] = 1
        
        self.keyboard = Wordle.MiniKeyboard(self.top)
        self.keyboard.grid(columnspan=5)

        self.green = set()
        self.yellow = set()
        self.gray = set()

        self.side = Wordle.SideFrame(self.top, self.wordle_stats)
        self.side.grid(column=5, row=0, rowspan=7)

        if self.wordle_stats["Last Game"]["Game ID"] == self.today: # Load current state
            if isinstance(self.wordle_stats["Last Game"]["Result"], int):
                self.add_to_stats = False

            b = self.wordle_stats["Resume Game State"]
            for guess,word in b.items():
                if not word:
                    break
                for i in word:
                    a = tk.Event()
                    a.keysym = i
                    self.time(a)

                a = tk.Event()
                a.keysym = "Return"
                self.time(a)

        else: # New Game
            self.wordle_stats["Last Game"] = {"Game ID": self.today, "Result": None}
            self.wordle_stats["Resume Game State"] = self.guesses

        self.top.protocol("WM_DELETE_WINDOW", self.on_destroy)

    def on_destroy(self):
        if self.side.history_page:
            self.side.history_page.on_destroy()
        
        self.wordle_stats["Resume Game State"] = self.guesses
        self.wordle_stats["Last Game"] = {"Game ID": self.today, "Result": self.game_result}
        self.minigame_stats["Parkour Wordle"] = self.wordle_stats
        with open(FileHandler.get_path_to_minigame_stats(), "w") as file:
            json.dump(self.minigame_stats, file, indent=4)
        
        self.top.destroy()

    def time(self, event):
        if event.keysym.isalpha() and len(event.keysym)==1:
            a,b = self.next_available
            if b <= 4:
                self.blanks[a][b].configure(text=event.keysym.upper())
                self.next_available[1] = b + 1
                self.typed_word += event.keysym.lower()
        elif event.keysym == "BackSpace":
            a,b = self.next_available
            if b > 0:
                self.next_available[1] = b - 1
                self.blanks[a][b-1].configure(text=" ")
                self.typed_word = self.typed_word[0:len(self.typed_word) - 1].lower()
        elif event.keysym == "Return" and self.next_available[1] == 5:
            if self.typed_word in FIVE_LETTER_WORDS + PARKOUR_FIVE_LETTER_WORDS:
                self.guess_count += 1
                self.msg.configure(text=f"Guessed {self.guess_count}/6")
                self.check(self.typed_word)
                self.next_available[0] += 1
                self.next_available[1] = 0
                self.typed_word = ""
            else:
                self.msg.configure(text=f"{self.typed_word} is not a word")
                for i in range(5):
                    self.animate(self.blanks[self.next_available[0]][i], 200, "red")
                for i in range(5):
                    self.blanks[self.next_available[0]][i].after(500, lambda j=i: self.animate(self.blanks[self.next_available[0]][j], 200, "gray20"))
                    
    
    def check(self, word):
        row = self.next_available[0]
        self.guesses[row+1] = word

        colored_boxes = {i:"" for i in range(5)}
        # Check for green
        a = {} | self.counts
        need_check = [0,1,2,3,4]
        for i in range(5):
            if word[i] == self.positions[i]:
                a[word[i]] -= 1
                need_check.remove(i)
                self.animate(self.blanks[row][i], 200, "green")
                self.animate(self.keyboard.buttons[word[i].upper()], 200, "green")
                self.green.add(word[i])
                try:
                    self.yellow.remove(word[i])
                except:
                    pass
                colored_boxes[i] = "🟩"
        
        if not need_check: # WIN
            self.msg.configure(text="Victory!", foreground="green")
            self.game_result = 1
            s = "".join(colored_boxes.values())
            self.clipboard_message += s + "\n"
            self.end_game(1)
            return

        for j in need_check:
            if word[j] in a: # Letter in word
                if a[word[j]] != 0: # Yellow
                    a[word[j]] -= 1
                    if word[j] not in self.green:
                        self.animate(self.keyboard.buttons[word[j].upper()], 200, 'yellow')
                    self.animate(self.blanks[row][j], 200, 'yellow')
                    self.yellow.add(word[j])
                    colored_boxes[j] = "🟨"
                else: # Gray (extra letter)
                    self.animate(self.blanks[row][j], 200, 'gray12')
                    if word[j] not in self.yellow:
                        self.animate(self.keyboard.buttons[word[j].upper()], 200, 'gray12')
                    self.gray.add(word[j])
                    colored_boxes[j] = "⬛"

            elif word[j] not in a: # Gray (not in word)
                self.animate(self.blanks[row][j], 200, 'gray12')
                self.animate(self.keyboard.buttons[word[j].upper()], 200, 'gray12')
                colored_boxes[j] = "⬛"
        
        s = "".join(colored_boxes.values())
        self.clipboard_message += s + "\n"

        if self.next_available[0] == 5: # LOSS
            self.msg.configure(text=f"Defeat! Word was {self.secret_word.upper()}", foreground="red")
            self.game_result = 0
            self.end_game(0)
        
    
    def end_game(self, result):
        # Unbind everything
        self.top.unbind_all("<KeyPress>")
        self.keyboard.enter_button.configure(command=0)
        self.keyboard.back_button.configure(command=0)
        for i in self.keyboard.buttons.values():
            i.configure(command=0)

        # Save Data
        if result == 1 and self.add_to_stats:
            self.wordle_stats["Wins"] += 1
            self.wordle_stats["Guess Distribution"][str(self.guess_count)] += 1
        elif result == 0 and self.add_to_stats:
            self.wordle_stats["Lose"] += 1
            self.wordle_stats["Guess Distribution"]["0"] += 1
        
        self.wordle_stats["Last Game"]["Results"] = self.game_result
        self.side.update_count(self.wordle_stats)

        self.clipboard_message = f"Parkour Wordle {self.guess_count}/6\n"+self.clipboard_message
        self.clipboard_message += f"I played in the Mothball App"
        self.side.clipboard_message = self.clipboard_message
        

    def animate(self, widget, duration=200, target_color=None):
        color_map = {
            "gray12": "#1f1f1f",
            "gray20": "#333333",
            "yellow": "#ffff00",
            "green": "#00ff00",
            "red": "#ff0000"
        }
        if target_color not in color_map:
            return

        start_color = widget.winfo_rgb(widget.cget('background'))
        end_color = widget.winfo_rgb(color_map[target_color])

        steps = 10
        delay = duration // steps

        def rgb_to_hex(rgb):
            return "#%02x%02x%02x" % rgb

        def interpolate(start, end, step, max_steps):
            return tuple(
                int(start[i] + (end[i] - start[i]) * step / max_steps) // 256
                for i in range(3)
            )

        def step_func(step=0):
            if step > steps:
                widget.configure(background=color_map[target_color])
                return
            new_color = interpolate(start_color, end_color, step, steps)
            widget.configure(background=rgb_to_hex(new_color))
            widget.after(delay, step_func, step + 1)

        step_func()
    
    

class HelpPage:
    def __init__(self, master):
        self.top = tk.Toplevel(master, background="gray12")
        self.top.title("Help on Parkour Wordle")
        self.label1 = tk.Label(self.top, text="How to Play",  background="gray12", foreground="white", font=("Comic Sans", 24))
        self.label1.grid(row=0, column=0, columnspan=5)
        
        self.label2 = tk.Text(self.top, background="gray12", foreground="white", font=("Comic Sans", 14), wrap=tk.WORD, width=37)
        self.label2.grid(row=1, column=0, columnspan=5)
        self.label2.update_idletasks()
        self.label2.insert(tk.END, "Guess the secret 5-letter word in 6 tries.\n\nEach guess must be a valid 5-letter word. After each guess, the color of the tiles will change to reveal hints.\n- Green: The letter is in the correct spot.\n- Yellow: The letter is in the word but in the wrong spot.\n- Gray: The letter is not in the word at all.")

        self.label2.tag_configure("green", foreground="green")
        self.label2.tag_configure("yellow", foreground="yellow")
        self.label2.tag_configure("grays", foreground="gray")
        self.label2.tag_add("green", "4.2", "4.7")
        self.label2.tag_add("yellow", "5.2", "5.8")
        self.label2.tag_add("grays", "6.2", "6.6")
        self.label2.configure(height = self.label2.count("1.0", tk.END, "displaylines"), state="disabled")


        self.example = {i: tk.Button(self.top, text=k, width=3, height=1,background=j, font=("Ariel", 30, 'bold')) for i,j,k in zip(range(5), ["gray12", "gray12", "green", "yellow", "gray12"], "ACUTE")}
        for b,a in self.example.items():
            a.grid(row=2, column=b)
        
        self.label3 = tk.Text(self.top, background="gray12", foreground="white", font=("Comic Sans", 14), wrap=tk.WORD, width=37)
        self.label3.grid(row=3, column=0, columnspan=5)
        self.label3.update_idletasks()
        self.label3.insert(tk.END, "In the above example, the letter U is in the right place.\nThe letter T is in word but is not the 4th letter.\nThe letters A, C, and E are not in the word.\n\nSince you're playing this inside a Mothball app, the answer is always parkour related. The answer could be in plural tense. The answer is never a player's name, unless that player's name is the name of a jump or strategy.")
        self.label3.tag_configure("green", foreground="green")
        self.label3.tag_configure("yellow", foreground="yellow")
        self.label3.tag_configure("grays", foreground="gray")
        self.label3.tag_add("green", "1.33", "1.34")
        self.label3.tag_add("yellow", "2.11", "2.12")
        self.label3.tag_add("grays", "3.12", "3.13", "3.15", "3.16", "3.22", "3.23")
        self.label3.configure(height = self.label3.count("1.0", tk.END, "displaylines"), state="disabled")
        
class HistoryAndMore:
    def __init__(self, master, stats):
        self.top = tk.Toplevel(master, background="gray12")
        self.top.title("Your Game History")
        
        label = tk.Label(self.top, text="hihi", background="gray12", foreground="white", font=("Comic Sans", 24))
        label.pack()
        self.id = ""

        def update_countdown():
            now = datetime.datetime.now(datetime.timezone.utc)
            tomorrow = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            remaining = tomorrow - now
            hours, remainder = divmod(remaining.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            label.config(text=f"Next word in {hours:02}:{minutes:02}:{seconds:02}")
            self.id = self.top.after(1000, update_countdown)
        update_countdown()
        
        x = [1,2,3,4,5,6,"Fail"]
        y = [j for j in stats["Guess Distribution"].values()]
        
        canvas_width = 500
        graph_height = 320
        canvas_height = 400
        canvas = tk.Canvas(self.top, width=canvas_width, height=canvas_height, bg="gray12")
        canvas.pack()

        bar_width = canvas_width // len(x)
        max_y = max(y)
        scale = (graph_height + 20 - canvas_height + graph_height) / max_y
        # scale = (2 * graph_height - 20 - canvas_height) / max_y
        # print(scale)

        canvas.create_text(canvas_width//2, 20, text="Wins & Losses by Guess Count", font=("Comic Sans", 20), fill="white")

        for i, value in enumerate(y):
            x0 = i * bar_width + 10
            y0 = graph_height - value * scale + 20
            x1 = (i + 1) * bar_width - 10
            y1 = graph_height + 20
            canvas.create_rectangle(x0, y0, x1, y1, fill="skyblue", outline="skyblue")
            
            canvas.create_text((x0 + x1) // 2, graph_height+40, text=str(x[i]), font=("Comic Sans", 18), fill="white")
            canvas.create_text((x0 + x1) // 2, y0-20, text=value, font=("Comic Sans", 14), fill="white")

        # Draw x-axis
        # canvas.create_line(0, canvas_height - graph_height, canvas_width, canvas_height - graph_height, width=2, fill='black')
        canvas.create_line(0, graph_height+20, canvas_width, graph_height+20, width=2, fill="white")
        canvas.create_text((canvas_width // 2), canvas_height - 15, text="Guess Distribution", font=("Comic Sans", 18), fill="white")

        self.top.protocol("WM_DELETE_WINDOW", self.on_destroy)

    def on_destroy(self):
        self.top.after_cancel(self.id)
        self.top.destroy()


if __name__ == "__main__":
    r = tk.Tk()
    a = Wordle(r)
    r.mainloop()
