import tkinter as tk
from tkinter import ttk
from CodeCell import Cell
import tkinter.colorchooser as cc

import tkinter as tk
import json
import FileHandler
import tkinter.messagebox as mb
import tkinter.simpledialog as sd

# TODO: Fix scrolling

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.after_id = None
        self.x = 0
        self.y = 0

        widget.bind("<Enter>", self.schedule)
        widget.bind("<Leave>", self.hide_tooltip)
        widget.bind("<Motion>", self.update_position)

    def schedule(self, event=None):
        self.unschedule()
        self.after_id = self.widget.after(500, self.show_tooltip)

    def unschedule(self):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None

    def update_position(self, event):
        self.x = event.x_root + 10
        self.y = event.y_root + 10
        if self.tooltip_window:
            self.tooltip_window.wm_geometry(f"+{self.x}+{self.y}")

    def show_tooltip(self):
        if self.tooltip_window or not self.text:
            return
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{self.x}+{self.y}")
        label = tk.Label(tw, text=self.text, background="lightyellow", foreground="black", relief='solid', borderwidth=1)
        label.pack()

    def hide_tooltip(self, event=None):
        self.unschedule()
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class Preferences(tk.Frame):
    def __init__(self, master, options: dict):
        super().__init__(master)
        self.option_add("*Checkbutton*Background", "gray12")
        self.option_add("*Checkbutton*Foreground", "White")
        self.option_add("*Button*Background", "gray12")
        self.option_add("*Button*Foreground", "White")
        self.option_add("*Label*Background", "gray12")
        self.option_add("*Label*Foreground", "White")

        self.options = options
        self.label = tk.Label(master, text="Settings", font=("Ariel", 12))
        self.label.grid(row=0, columnspan=2)
        
        self.b = tk.Checkbutton(master, text="Ask before deleting a cell", command=lambda: self.toggle("Ask before deleting a cell"), font=("Ariel", 12))
        if self.options["Settings"]["Ask before deleting a cell"]: self.b.select()
        self.b.grid(row=1,columnspan=2)
        ToolTip(self.b, "Prevents accidental deletion of cells.")

        self.c = tk.Entry(master, font=("Ariel", 12), width=5)
        self.c.insert(0, self.options["Settings"]["Max lines"])
        self.c.grid(row=2, column=0)

        self.d = tk.Label(master, text="Max lines expand")
        self.d.grid(row=2, column=1)
        ToolTip(self.d, "Set the max number of lines (at least 10) before scrolling.\nValues below 10 will be treated as no maximum.")

        self.apply = tk.Button(master, text="Apply and Save", command=self.apply_and_save)
        self.apply.grid(row=3,columnspan=2)
    
    def toggle(self, item):
        self.options["Settings"][item] = not self.options["Settings"][item]

    def set_max_lines(self):
        try:
            a = int(self.c.get())
            self.options["Settings"]["Max lines"] = a
        except:
            pass

    def apply_and_save(self):
        self.set_max_lines()
        with open(FileHandler.get_path_to_options(), "w") as file:
            json.dump(self.options, file, indent=4)

class Bindings(tk.Frame):
    def __init__(self, master, options: dict):
        super().__init__(master)
        self.option_add("*Checkbutton*Background", "gray12")
        self.option_add("*Checkbutton*Foreground", "White")
        self.option_add("*Button*Background", "gray12")
        self.option_add("*Button*Foreground", "White")
        self.option_add("*Label*Background", "gray12")
        self.option_add("*Label*Foreground", "White")

        self.options = options
        self.label = tk.Label(master, text="Bindings", font=("Ariel", 12))
        self.label.grid(row=0)

        self.listening_to_keys = False
        self.binding_for = None

        tooltips = ["Open a new file","Clear the notebook","Save the notebook","Undo last action","Redo last undo","Increases font size","Decreases font size","Run current cell","Find string in a text"]
        self.labels: dict[str, list[str, tk.Button]] = {}
        for e, k in enumerate(self.options["Settings"]["Bindings"].items()):
            i,j = k
            l = tk.Label(master, text=i)
            l.grid(row=e+1, column=0)
            ToolTip(l, tooltips[e])
            m = tk.Button(master, text=j, command=lambda x=i: self.set_bind(x))
            m.grid(row=e+1, column=1, sticky="ew")
            self.labels[i] = [j,m]
        

        self.bind_all("<KeyPress>", self.on_key_press)
        self.apply = tk.Button(master, text="Apply Bindings", command=self.apply_binds)
        self.apply.grid(columnspan=2)

    def apply_binds(self):
        for i,j in self.labels.items():
            self.options["Settings"]["Bindings"][i] = j[0]
        with open(FileHandler.get_path_to_options(), "w") as file:
            json.dump(self.options, file, indent=4)

    def check_for_duplicate_binding(self):
        a = list(b[0] for b in self.labels.values())
        duplicates = [key for key in self.labels if a.count(self.labels[key][0]) > 1]

        for key in self.labels:
            if key in duplicates:
                self.labels[key][1].configure(foreground="red")
            else:
                self.labels[key][1].configure(foreground="white")
                
    def on_key_press(self, event: tk.Event):
        if self.listening_to_keys:
            if event.keysym.lower() in "abcdefghijklmnopqrstuvwxyz0123456789": # No special symbols
                self.listening_to_keys = False
                self.labels[self.binding_for][0] = f"Control-{event.keysym.lower()}"
                self.labels[self.binding_for][1].configure(background="gray12", text=f"Control-{event.keysym.lower()}")
                self.binding_for = None
                self.check_for_duplicate_binding()
            elif event.keysym in ["Escape", "Return"]:
                self.listening_to_keys = False
                self.labels[self.binding_for][1].configure(background="gray12")
                self.binding_for = None

    def set_bind(self, action: str):
        if self.binding_for:
            # print(self.binding_for, action, self.binding_for == action)
            self.labels[self.binding_for][1].configure(background="gray12")
            if self.binding_for == action:
                self.listening_to_keys = False
                self.binding_for = None
                return
            self.labels[self.binding_for][1].configure(background="gray12")

        self.labels[action][1].configure(background="lime")
        self.listening_to_keys = True
        self.binding_for = action

class ChangeColorDialog(tk.Frame):
    default_text = """version(1.21) 
sprint(8, slow=3) sprintair.wd walk.s walk[water](3) stop stopair
outx(0.03125, label=hey I'm an x axis output) vec
wall(1.8125, repeat(sprintjump.wa(4), 2)) zb(2.2, z output)
var(new_var, 37) print(new_var: {new_var})
print(help\, its been 4 years) # comments are \# cool #
func(hello, param, code=print(hello {param} {new_var} times))
hello(mothballer)
"""
    def __init__(self, premaster, master, options):
        super().__init__(master)
        self.main_frame = master
        self.premaster = premaster
        self.option_add("*Button*Background", "gray12")
        self.option_add("*Button*Foreground", "White")
        self.option_add("*Label*Background", "gray12")
        self.option_add("*Label*Foreground", "White")
        self.configure(bg="gray12")
        self.side_display = Cell(master, 'xz', options)
        self.side_display.configure(width=100)
        self.side_display.grid(row=0, column=0, columnspan=4)
        self.side_display.eval_button.destroy()
        self.side_display.add_cell.destroy()
        self.side_display.add_cell_y.destroy()
        self.side_display.delete_cell.destroy()
        self.side_display.title_frame.destroy()
        self.side_display.add_text.destroy()
        self.side_display.text.insert("1.0", ChangeColorDialog.default_text)
        self.side_display.evaluate()
        self.side_display.text.configure(width=60)
        self.side_display.label2.configure(width=60)
        self.side_display.output.configure(width=60)
        self.side_display.text.insert(tk.END, "# parenthesis # (( { ( {{}} ) } ))\n( 4..5 #ERRORS#")
        self.side_display.colorize_code()
        self.side_display.text.update_idletasks()
        self.side_display.adjust_height()
        self.side_display.adjust_height(self.side_display.output)
        self.side_display.text.configure(state="disabled")
        self.side_display.text.tag_configure("bold", background="gray")
        self.side_display.output.tag_configure("bold", background="gray")
        self.side_display.label2.configure(state="normal")
        self.side_display.label2.delete("1.0", tk.END)
        self.side_display.label2.insert("1.0", "Output is shown below (Executed at <time goes here>)")
        self.side_display.label2.configure(state="disabled")
        self.side_display.colorize_output()

        self.options = options
        self.colors = options["Current-theme"]
        tag_names = ["fast-movers", "slow-movers", "stoppers", "modifiers","setters", "inputs", "returners", "calculators", "numbers", "comment", "keyword", "string", "custom-function", "custom-function-parameter","error", "nest-mod1", "nest-mod2", "nest-mod0"]
        code_label_names = ["Fast movement", "Slow movement", "Stop movement", "Modifiers", "Setters", "inputs", "Returners", "Calculators", "Numbers", "Comments", "Keyword arguments", "Strings", "Defined functions", "Defined Function Parameters", "Errors", "Brackets 1", "Brackets 2", "Brackets 3"]
        self.code_tag_name_to_label = {l:t for t,l in zip(tag_names, code_label_names)}

        tk.Label(master, text="Code Colors").grid(row=1, column=0, columnspan=2)
        self.code_menu = tk.Listbox(master, height=8)
        self.code_menu.grid(row=2, column=0)
        for i in code_label_names:
            self.code_menu.insert(tk.END, i)
        
        self.code_menu.bind("<Motion>", lambda e, s='code': self.motion(e, s))
        self.code_menu.bind("<Leave>", lambda e: self.unhighlight(self.code_tag_name_to_label.get(self.code_last_hover), "code"))
        self.code_last_hover = ""
        
        tk.Label(master, text="Output Colors").grid(row=1, column=2, columnspan=2)

        
        tag_names2 = ["z-label", "x-label", "label", "warning", "text", "positive-number", "negative-number"]
        output_label_names = ["Z outputs", "X outputs", "Vec/Y outputs", "Warnings", "Text", "Positive numbers", "Negative numbers"]
        self.output_tag_name_to_label = {l:t for t,l in zip(tag_names2, output_label_names)}

        self.output_menu = tk.Listbox(master, height=8)
        self.output_menu.grid(row=2, column=2)
        for i in output_label_names:
            self.output_menu.insert(tk.END, i)
        
        self.output_menu.bind("<Motion>", lambda e, s='output': self.motion(e, s))
        self.output_menu.bind("<Leave>", lambda e: self.unhighlight(self.output_tag_name_to_label.get(self.output_last_hover), "output"))
        self.output_last_hover = ""

        self.code_menu.bind("<<ListboxSelect>>", lambda e: self.on_selection(e, "code"))
        self.output_menu.bind("<<ListboxSelect>>", lambda e: self.on_selection(e, "output"))
        
        self.f = tk.Frame(master)
        self.f.grid(row=2, column=1, sticky="nswe")
        self.code_color_square = tk.Canvas(self.f, width=1, height=1, bg="gray12", background="gray12", relief=tk.SUNKEN, highlightthickness=0, borderwidth=0)
        self.code_color_square.pack(fill="both", expand=True)
        self.f.a = tk.Button(self.f, text="Select", wraplength=100)
        self.f.a.pack(fill="both")

        self.g = tk.Frame(master)
        self.g.grid(row=2, column=3, sticky="nswe")
        self.output_color_square = tk.Canvas(self.g, width=1, height=1, bg="gray12", relief=tk.SUNKEN, highlightthickness=0, borderwidth=0)
        self.output_color_square.pack(expand=True, fill="both")
        self.g.b = tk.Button(self.g, text="Select", wraplength=100)
        self.g.b.pack(fill='both')

        self.apply = tk.Button(master, text="Apply and Save", command=self.set_theme)
        self.apply.grid(row=3, column=0)

        self.set_new_theme = tk.Button(master, text="New Theme", command=self.new_theme)
        self.set_new_theme.grid(row=3, column=1)

        self.del_theme = tk.Button(master, text="Delete Theme", command= self.delete_theme)
        self.del_theme.grid(row=3, column=2)

        self.theme_selected = tk.StringVar(master, value=self.options["Current-theme"]["Name"])
        self.theme_selected.trace_add("write", lambda *args: self.update_display())
        self.theme = tk.OptionMenu(master, self.theme_selected, *list(self.options["Themes"].keys()))
        self.theme.grid(row=3, column=3)

    def update_display(self):
        self.options['Current-theme'] = self.options["Themes"][self.theme_selected.get()]
        for i,j in self.options['Current-theme']['Code'].items():
            self.side_display.text.tag_configure(i, foreground=j)
        for l,m in self.options['Current-theme']['Output'].items():
            self.side_display.output.tag_configure(l, foreground=m)
        
        self.side_display.text.configure(state="normal")
        self.side_display.colorize_code()
        self.side_display.text.configure(state="disabled")
        self.side_display.output.configure(state="normal")
        self.side_display.colorize_output()
        self.side_display.output.configure(state="disabled")

        self.colors = self.options['Current-theme']

        self.on_selection(0, "code")
        self.on_selection(0, "output")

    def new_theme(self):
        b = sd.askstring("New Theme", "Name your new theme")
        if b:
            b = b.strip()
            if b.lower() == "default":
                mb.showerror("Naming failed", "Cannot name a theme \"default\".")
                return
            elif b in self.options["Themes"]:
                mb.showerror("Namnig failed", f"Name \"{b}\" already exists.")
                return
            else:
                self.colors["Name"] = b
                self.options["Themes"][b] = self.colors
                with open(FileHandler.get_path_to_options(), "w") as file:
                    json.dump(self.options, file, indent=4)
                self.theme["menu"].add_command(label=b.strip(), command=tk._setit(self.theme_selected, b.strip()))
                self.theme_selected.set(b.strip())

                self.options["Current-theme"] = self.colors
                # self.colors = self.options["Current-theme"]


    def delete_theme(self):
        a=self.theme_selected.get()
        if a == "Default":
            mb.showerror("Error", "Cannot delete default theme")
            return
        del self.options["Themes"][a]
        with open(FileHandler.get_path_to_options(), "w") as file:
            json.dump(self.options, file, indent=4)
    
    def set_theme(self):
        with open(FileHandler.get_path_to_options(), "w") as file:
            json.dump(self.options, file, indent=4)
        self.premaster.change_colors(self.options)
        

    def on_selection(self, event, code_or_output: str):
        if code_or_output == "code":
            selected_index = self.code_menu.curselection()
            if selected_index:
                selected_item = self.code_menu.get(selected_index[0])
                self.f.a.configure(text=selected_item, command=lambda: self.ask_for_color("code"))
                tag_name = self.code_tag_name_to_label[selected_item]
                color = self.colors['Code'][tag_name]
                self.code_color_square.configure(bg=color)
                
        elif code_or_output == "output":
            selected_index = self.output_menu.curselection()
            if selected_index:
                selected_item = self.output_menu.get(selected_index[0])
                self.g.b.configure(text=selected_item, command=lambda: self.ask_for_color("output"))
                tag_name = self.output_tag_name_to_label[selected_item]
                color = self.colors['Output'][tag_name]
                self.output_color_square.configure(bg=color)

    def on_hover(self, index, code_or_output):
        if code_or_output == "code": 
            item = self.code_menu.get(index)
            if self.code_last_hover != item:
                if self.code_last_hover:
                    self.unhighlight(self.code_tag_name_to_label.get(self.code_last_hover), "code")
                self.code_last_hover = item
                self.highlight(self.code_tag_name_to_label.get(item), "code")
        elif code_or_output == "output":
            item = self.output_menu.get(index)
            if self.output_last_hover != item:
                if self.output_last_hover:
                    self.unhighlight(self.output_tag_name_to_label.get(self.output_last_hover), "output")
                self.output_last_hover = item
                self.highlight(self.output_tag_name_to_label.get(item), "output")

    def motion(self, event, code_or_output: str):
        if code_or_output == "code":
            index = self.code_menu.nearest(event.y)
        elif code_or_output == "output":
            index = self.output_menu.nearest(event.y)
        self.on_hover(index, code_or_output)

    def highlight(self, tag, code_or_output: str):
        if code_or_output == "code":
            index_pairs = self.side_display.text_color_to_indexes[tag]
            indexes = []
            for pair in index_pairs:
                indexes.append(pair[0])
                indexes.append(pair[1])
            self.side_display.text.configure(state="normal")
            self.side_display.text.tag_add("bold", *indexes)
            self.side_display.text.configure(state="disabled")
        elif code_or_output == "output":
            index_pairs = self.side_display.output_color_to_indexes[tag]
            indexes = []
            for pair in index_pairs:
                indexes.append(pair[0])
                indexes.append(pair[1])
            self.side_display.output.configure(state="normal")
            self.side_display.output.tag_add("bold", *indexes)
            self.side_display.output.configure(state="disabled")

    
    def unhighlight(self,tag, code_or_output: str):
        if code_or_output == "code":
            index_pairs = self.side_display.text_color_to_indexes.get(tag)
            if index_pairs:
                self.side_display.text.configure(state="normal")
                for pair in index_pairs:
                    self.side_display.text.tag_remove("bold", pair[0], pair[1])
                self.side_display.text.configure(state="disabled")
                self.code_last_hover = ""
        elif code_or_output == "output":
            index_pairs = self.side_display.output_color_to_indexes.get(tag)
            if index_pairs:
                self.side_display.output.configure(state="normal")
                for pair in index_pairs:
                    self.side_display.output.tag_remove("bold", pair[0], pair[1])
                self.side_display.output.configure(state="disabled")
                self.output_last_hover = ""
    
    def ask_for_color(self, code_or_output):
        if self.theme_selected.get() == "Default":
            mb.showerror("Error", "Cannot edit default theme.")
            return
        m = cc.askcolor()
        if m[1]:
            if code_or_output == "code":
                a = self.f.a.cget("text")
                tag_name = self.code_tag_name_to_label[a]
                self.colors["Code"][tag_name] = m[1]
                self.code_color_square.configure(bg=m[1])

                self.side_display.text.configure(state="normal")
                self.side_display.text.tag_configure(tag_name, foreground=m[1])
                self.side_display.text.configure(state="disabled")

            elif code_or_output == "output":
                b = self.g.b.cget("text")
                tag_name = self.output_tag_name_to_label[b]
                self.colors["Output"][tag_name] = m[1]
                self.output_color_square.configure(bg=m[1])

                self.side_display.output.configure(state="normal")
                self.side_display.output.tag_configure(tag_name, foreground=m[1])
                self.side_display.output.configure(state="disabled")



class Settings:
    def __init__(self, master, options: dict):
        self.options = options
        self.master = master
        self.top = tk.Toplevel()
        self.top.grab_set()
        
        self.notebook = ttk.Notebook(self.top)
        self.notebook.pack(expand=True, fill='both')


        frame2 = tk.Frame(self.notebook, background="gray12")
        c = ChangeColorDialog(master, frame2, options)
        self.notebook.add(frame2, text="Colors")

        frame1 = tk.Frame(self.notebook, background="gray12")
        b = Bindings(frame1, options)
        self.notebook.add(frame1, text="Bindings")

        frame = tk.Frame(self.notebook, background="gray12")
        a = Preferences(frame, options)
        self.notebook.add(frame, text="Preferences")
    


if __name__ == "__main__":
    import FileHandler
    options = FileHandler.get_options()
    r = tk.Tk()
    a = Settings(r, options)
    r.mainloop()
