import mothball_simulation_xz as xz
import tkinter as tk
from tkinter import ttk
import mothball_simulation_y as y
from utils import *
from TkinterPosition import TkinterPosition
import re
import datetime
from TkinterPosition import TkinterPosition
from tkinter.scrolledtext import ScrolledText
import webbrowser
import inspect
import re
import os
import sys
import platform
from PIL import Image, ImageTk
import FileHandler
options = FileHandler.get_options()

class Cell(tk.Frame):
    def __init__(self, parent, mode: str, options: dict, grandparent = None, fontsize = 12, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # self.width = 500
        self.mode = mode # Either "xz" or "/y"
        self.FUNCTIONS_TO_TYPE = {} # Combines all of the mappings of FUNCTIONS_BY_TYPE so it maps a function ailas to the appropiate type
        self.parent = parent
        self.execution_time = None
        self.has_changed = False
        self.grandparent = grandparent
        self.type = "code"
        self.last_applied_tag = ""
        self.options = options
        self.binds = self.options["Settings"]["Bindings"]
        self.padx = 0

        if self.mode == "xz":
            self.inputs = ["w","a","s","d", "wa", "wd", "sa", "sd"]
    
            for func_type, func_aliases in xz.Player.FUNCTIONS_BY_TYPE.items():
                for func_alias in func_aliases:
                    self.FUNCTIONS_TO_TYPE[func_alias] = func_type
            
            self.modifiers = xz.Player.ALIAS_TO_MODIFIER
        else:
            self.inputs = []
            self.modifiers = []
            for func_type, func_aliases in y.Player.FUNCTIONS_BY_TYPE.items():
                for func_alias in func_aliases:
                    self.FUNCTIONS_TO_TYPE[func_alias] = func_type
        
        self.fontsize = fontsize

        self._pos = TkinterPosition(1,0)

        # TEMPORARY FIX
        operating_system = platform.system()
        if operating_system == "Windows":
            color = "white"
        else:
            color = 'black'

        self.configure(background="gray12", border=5)
        self.title_frame = tk.Frame(self, background="gray12")
        self.title_frame.pack(padx=self.padx)
        self.label = ttk.Label(self.title_frame, text=f"Code Cell {mode.upper()}", background="gray12", foreground="white", font=("Ariel",self.fontsize))
        self.label.pack()
        
        self.text = tk.Text(self, state='normal', bg="gray12", fg="white", font=("Courier", self.fontsize), wrap=tk.WORD, undo=True, maxundo=-1)
        self.text.pack(padx=self.padx)
        self.text.bind('<KeyPress>', lambda event: self.timed(event))

        self.label2 = tk.Text(self, background="gray12", foreground="white", height = 1, font=("Courier", self.fontsize), wrap=tk.WORD)
        self.label2.insert("1.0", "Output is shown below ")
        self.label2.configure(state="disabled")
        self.label2.tag_configure("grayed", foreground="gray")
        self.label2.pack(padx=self.padx)
        
        self.output = tk.Text(self, bg="gray12", fg="white", font=("Courier", self.fontsize), wrap=tk.WORD)
        self.output.pack(padx=self.padx)
        self.output_scrollable = False

        self.raw_output = []


        button_frame = tk.Frame(self, background="gray12")
        button_frame.pack(side="bottom", fill="x", padx=self.padx)

        self.eval_button = tk.Button(button_frame, text="Run", command=self.evaluate, background="gray12", foreground=color, font=("Ariel", 10, "bold"))
        self.add_cell = tk.Button(button_frame, text="Add Cell XZ", background="gray12", foreground=color, font=("Ariel", 10, "bold"))
        self.add_cell_y = tk.Button(button_frame, text="Add Cell Y", background="gray12", foreground=color, font=("Ariel", 10, "bold"))
        self.add_text = tk.Button(button_frame, text="Add Text", background="gray12", foreground=color, font=("Ariel", 10, "bold"))
        self.delete_cell = tk.Button(button_frame, text="Delete", background="gray12", foreground=color, font=("Ariel", 10, "bold"))
        self.bind_hover(self.eval_button)
        self.bind_hover(self.add_cell)
        self.bind_hover(self.add_cell_y)
        self.bind_hover(self.add_text)
        self.bind_hover(self.delete_cell)
        self.eval_button.pack(side="left", expand=True, fill="x")
        self.add_cell.pack(side="left", expand=True, fill="x")
        self.delete_cell.pack(side="right", expand=True, fill="x")
        self.add_text.pack(side="right", expand=True, fill="x")
        self.add_cell_y.pack(side="right", expand=True, fill="x")

        self.adjust_height()
        self.adjust_height(widget=self.output)
        self.output.insert("1.0", "Run some functions and the output will show here!")
        self.output.configure(state="disabled")

        # self.bind("<Control-r>", lambda x: self.evaluate())

        # Linter
        for tag_name, foreground_color in self.options["Current-theme"]["Code"].items():
            self.text.tag_configure(tag_name, foreground=foreground_color)

        for tag_name, foreground_color in self.options["Current-theme"]["Output"].items():
            self.output.tag_configure(tag_name, foreground=foreground_color)
        
        # TO BE DETERMINED
        # self.text.tag_configure("modifiers", foreground="lime")

        self.output.tag_add("placeholder", "1.0", tk.END)

        self.text.bind("<Key>", self.timed)
        self.timer = 0
        self.timer_id = None

        self.text_color_to_indexes: dict[str, list] = {
            'fast-movers': [],
            'slow-movers': [],
            'stoppers': [],
            "setters": [],
            "returners": [],
            "inputs": [],
            "modifiers": [],
            "calculators": [],
            "numbers": [],
            "comment": [],
            "nest-mod1": [],
            "nest-mod2": [],
            "nest-mod0": [],
            "keyword": [],
            "variable": [],
            "string": [],
            "backslash": [],
            "comment-backslash": [],
            "custom-function-parameter": [],
            "custom-function": [],
            "error": []
        }

        self.output_color_to_indexes: dict[str, list] = {
            "z-label": [],
            "x-label": [],
            "label": [],
            "warning": [],
            "text": [],
            "positive-number": [],
            "negative-number": [],
            "placeholder": []
        }

        self.text.bind(f"<{self.binds['Open']}>", lambda e: self.grandparent.load())
        self.label.bind("<Double-1>", self.edit_cell_name)
    
    def edit_cell_name(self, e):
        self.label.pack_forget()
        self.entry = tk.Entry(self.title_frame, background="gray12", foreground="white", font=("Ariel",12))
        old = self.label.cget("text")
        self.entry.insert(0, old)
        self.entry.pack(side="left")
        self.entry.bind("<Return>", lambda e: self.set_cell_name(old, self.entry.get()))
        self.accept = tk.Button(self.title_frame, background="gray12", foreground="green", font=("Ariel",8), text="Save", command=lambda: self.set_cell_name(old, self.entry.get()))
        self.cancel = tk.Button(self.title_frame, background="gray12", foreground="red", font=("Ariel",8), text="Cancel", command= lambda: self.set_cell_name(old, None))
        self.cancel.pack(side="right")
        self.accept.pack(side="right")
    
    def set_cell_name(self, old_name, new_name):
        self.entry.pack_forget()
        self.accept.pack_forget()
        self.cancel.pack_forget()
        if not new_name or new_name.isspace():
            new_name = old_name
        self.label = ttk.Label(self.title_frame, text=new_name, background="gray12", foreground="white", font=("Ariel",self.fontsize))
        self.label.pack(side="top")
        self.label.bind("<Double-1>", lambda e: self.edit_cell_name(e))
        if self.grandparent: self.grandparent.has_unsaved_changes = True

    def adjust_width(self, width: int):
        self.text.configure(width=width)
        self.output.configure(width=width)
        self.label2.configure(width=width)

    def adjust_height(self, event=0, widget = None):
        if not widget:
            widget = self.text

        height = widget.count('1.0', 'end', 'displaylines')[0]
        if widget == self.output and self.options["Settings"]["Max lines"] >= 10: # TO CHANGE
            height = min(self.options["Settings"]["Max lines"], height)

        widget.configure(height=height)

    
    def timed(self, event: tk.Event = 0):
        if self.timer_id is not None and event and event.keysym not in ["Control_L", "Control_R", "Shift_L", "Shift_R", "Caps_Lock", "Escape", "Down", "Up", "Left", "Right", "Alt_R", "Alt_L"]:
            self.after_cancel(self.timer_id)
        
        if event and event.keysym not in ["Control_L", "Control_R", "Shift_L", "Shift_R", "Caps_Lock", "Escape", "Down", "Up", "Left", "Right", "Alt_R", "Alt_L"]:
            # self.after("idle",self.adjust_height)
            self.after_idle(self.adjust_height)
            self.timer_id = self.after(250, self.colorize_code)
            if not self.has_changed:
                self.has_changed = True
                if self.grandparent: self.grandparent.has_unsaved_changes = True
                self.label2.configure(state="normal")
                self.label2.tag_add("grayed", "1.22", tk.END)
                self.label2.configure(state="disabled")
        

    def parse(self, text: str) -> list[str]:
        """
        Parses the text, separating whenever the following symbols is encountered: `(){}\\#.| \\n\\t,=+*-/:`
        
        Returning a list containing all elements
        """
        tokens = []
        follows_backslash = False
        word = ""
        for char in text:
            if follows_backslash:
                word += char
                tokens.append(word)
                word = ""
                follows_backslash = False

            elif char in "(){}[]\\#.| \n\t,=+*-/:":
                tokens.append(word) if word else None
                tokens.append(char)
                word = ""
                
                if char == "\\":
                    follows_backslash = True

            else:
                word += char
        
        return tokens
    
    def colorize_code(self, event=0, start_position = (1,0)):
        "Color the text, does the syntax highlighting logic"
        tokens = self.parse(self.text.get("1.0", tk.END))
        self._pos = TkinterPosition(start_position[0],start_position[1])
        self.text_color_to_indexes: dict[str, list] = {
            'fast-movers': [],
            'slow-movers': [],
            'stoppers': [],
            "setters": [],
            "returners": [],
            "inputs": [],
            "modifiers": [],
            "calculators": [],
            "numbers": [],
            "comment": [],
            "nest-mod1": [],
            "nest-mod2": [],
            "nest-mod0": [],
            "keyword": [],
            "variable": [],
            "string": [],
            "backslash": [],
            "comment-backslash": [],
            "custom-function-parameter": [],
            "custom-function": [],
            "error": []
        }

        for tag in self.text_color_to_indexes:
            self.text.tag_remove(tag, "1.0", tk.END)

        parenthesis_stack = ParenthesisStack()
        nest_depth = 0
        function_stack = FunctionStack()
        last_token = ""
        last_nonspace_token = ""
        last_nonspace_token_position = ("","")
        last_function = ""

        in_comment = False
        in_bracket = False
        follows_dot = False
        follows_backslash = False
        in_modifiers = False
        self.last_applied_tag = ""

        current_parameter_type = None

        if self.mode == "xz":
            defined_variables = set(xz.Player().local_vars)
        elif self.mode == 'y':
            defined_variables = set(y.Player().local_vars)

        defined_functions = set()
        local_variables_stack = []
        inside_main_function = False
        inner_function_stack = []



        for token in tokens:
            # print(token)

            if token == "\\":
                follows_backslash = True
                if in_comment:
                    self.apply_tag(token, "comment-backslash")
                elif not in_comment:
                    self.apply_tag(token, "backslash")

            elif in_comment or (not in_comment and token == "#"):
                if (follows_backslash and token in "()[]{},\\#"):
                    self.apply_tag(token, "comment-backslash")
                else:
                    if token == "\n":
                        self._pos = self._pos.add_row(1).reset_column()
                    elif token == "#":
                        in_comment = not in_comment
                    self.apply_tag(token, "comment")

            elif follows_backslash and token in "\#(),[]{}=:":
                self.apply_tag(token, "backslash")
            
            elif current_parameter_type == str and (not isinstance(function_stack.peek().current_parameter, str) and function_stack.peek().current_parameter.name == "variable_name") and token != ",":
            # elif current_parameter_type == str and nest_depth and function_stack.peek().current_parameter.name == "variable_name") and token != ",":
                self.apply_tag(token, "variable")
                defined_variables.add(token)
            
            elif current_parameter_type == str and function_stack.peek_function_name() == "function" and function_stack.peek().current_parameter.name == "name" and token not in "(),\\{}=[]":
                self.apply_tag(token, "custom-function")
                if local_variables_stack:
                    local_variables_stack.append(local_variables_stack[-1].union(set()))
                else:
                    local_variables_stack.append(set())
                
                if not inside_main_function:
                    inside_main_function = True
                    defined_functions.add(token)
                elif inside_main_function:
                    inner_function_stack.append(token)
                
            elif current_parameter_type == str and not token.isspace() and function_stack.peek_function_name() == "function" and function_stack.peek().current_parameter.name == 'args' and token not in "(),\\{}=[]":
                self.apply_tag(token, "custom-function-parameter")
                local_variables_stack[-1].add(token)

            elif current_parameter_type == str and token not in "(),\\{}=[]" and not in_bracket and function_stack.peek().current_parameter.name not in ['sequence', 'value','code', 'func', 'seq_or_num']:
                self.apply_tag(token, "string")
                if token == "\n":
                    self._pos = self._pos.add_row(1).reset_column()
            
            elif in_modifiers and token in self.modifiers:
                self.apply_tag(token, "modifiers")

            elif local_variables_stack and token in local_variables_stack[-1]:
                self.apply_tag(token, "custom-function-parameter")

            elif token in defined_variables and nest_depth and (function_stack.is_empty() or (function_stack.peek().current_parameter and function_stack.peek().current_parameter.name not in ["sequence", 'seq_or_num'])): # PLEASE CHECK LOGIC !
                self.apply_tag(token, "variable")

            else:
                func_tag = self.get_tag_from_string(token, defined_functions.union(set(inner_function_stack)))
                if follows_dot and token in self.inputs:
                    self.apply_tag(token, "inputs")

                elif func_tag is not None:
                    self.apply_tag(token, func_tag)
                    last_function = token
                
                elif token in "({[":
                    parenthesis_stack.push(self._pos.string, token)
                    self.apply_tag(token, "error")
                    nest_depth += 1

                    if token == "(" and not last_token.isspace() and last_function:
                        try: 
                            if self.mode == "xz":
                                function_stack.push(xz.Player.FUNCTIONS[last_function])
                            elif self.mode == "y":
                                function_stack.push(y.Player.FUNCTIONS[last_function])
                            current_parameter_type = function_stack.peek_current_parameter_annotation()
                        except KeyError:
                            function_stack.push(last_function)
                            current_parameter_type = function_stack.peek_current_parameter_annotation()

                    elif token == "{":
                        in_bracket = not in_bracket
                    
                    elif token == "[" and not last_token.isspace() and last_function:
                        in_modifiers = True

                elif token in ")}]":
                    if parenthesis_stack.matches_parenthesis_stack(token):
                        self.apply_tag(token, f"nest-mod{nest_depth % 3}")
                        position = parenthesis_stack.pop()[0]
                        self.text.tag_remove("error", position[0], position[1])
                        self.text_color_to_indexes["error"].remove((position[0],position[1]))
                        self.text_color_to_indexes[f"nest-mod{nest_depth % 3}"].append((position[0],position[1]))
                        self.text.tag_add(f"nest-mod{nest_depth % 3}", position[0], position[1])
                        nest_depth -= 1

                        if token == ")":
                            a = function_stack.pop()
                            if not function_stack.is_empty():
                                current_parameter_type = function_stack.peek_current_parameter_annotation()
                            else:
                                current_parameter_type = None
                            if a is not None and a.name == "function" and local_variables_stack:
                                local_variables_stack.pop()
                        elif token == "}":
                            in_bracket = not in_bracket
                        elif token == "]":
                            in_modifiers = not in_modifiers
                            
                    else:
                        self.apply_tag(token, "error")

                elif token == ",":
                    if not in_modifiers and not function_stack.is_empty() and not function_stack.peek_after_keyword(): # positional
                        function_stack.peek_next_positional_parameter()
                        current_parameter_type = function_stack.peek_current_parameter_annotation()
                    
                    self.apply_tag(token, "none")
                
                elif token == "=":
                    if not function_stack.is_empty() and last_nonspace_token in function_stack.peek_remaining_keywords():
                        self.text.tag_remove("string", last_nonspace_token_position[0].string, last_nonspace_token_position[1].string)
                        self.text.tag_remove("setters", last_nonspace_token_position[0].string, last_nonspace_token_position[1].string)
                        self.text.tag_remove("custom-function-parameter", last_nonspace_token_position[0].string, last_nonspace_token_position[1].string)

                        try:
                            self.text_color_to_indexes['string'].remove((last_nonspace_token_position[0].string, last_nonspace_token_position[1].string))
                        except ValueError:
                            try:
                                self.text_color_to_indexes['setters'].remove((last_nonspace_token_position[0].string, last_nonspace_token_position[1].string))
                            except ValueError:
                                try:
                                    self.text_color_to_indexes['custom-function-parameter'].remove((last_nonspace_token_position[0].string, last_nonspace_token_position[1].string))
                                except ValueError:
                                    pass
                        
                        self.text_color_to_indexes['keyword'].append((last_nonspace_token_position[0].string, last_nonspace_token_position[1].string))

                        self.text.tag_add("keyword", last_nonspace_token_position[0].string, last_nonspace_token_position[1].string)
                        current_parameter_type = function_stack.peek_get_keyword_type(last_nonspace_token)
                        function_stack.peek_remove_keyword(last_nonspace_token)
                    
                        if function_stack.peek_function_name() == "function":
                            local_variables_stack[-1].remove(last_nonspace_token)
                    
                    self.apply_tag(token, "none")
                
                elif token == ".":
                    if follows_dot:
                        self.apply_tag(token, "error")
                    elif last_nonspace_token.isnumeric():
                        self.apply_tag(token, "numbers")
                    else:
                        self.apply_tag(token, "none")
                    follows_dot = True

                elif token.isnumeric():
                    self.apply_tag(token, "numbers")
                    if follows_dot:
                        self.text.tag_add("numbers", last_nonspace_token_position[0].string, last_nonspace_token_position[1].string)
                else:
                    if not in_modifiers:
                        last_function = ""
                    if token == "\n":
                        self._pos = self._pos.add_row(1).reset_column()
                    else:
                        self._pos = self._pos + len(token)
            
            last_token = token
            if not token.isspace():
                last_nonspace_token = token
                last_nonspace_token_position = (self._pos - len(last_nonspace_token),self._pos)
            if token != ".":
                follows_dot = False
            if token != "\\":
                follows_backslash = False
        
        
    def apply_tag(self, item: str, tag: str):
        new_pos = self._pos + len(item)
        self.text.tag_add(tag, self._pos.string, new_pos.string)
        try:
            self.text_color_to_indexes[tag].append((self._pos.string, new_pos.string))
        except KeyError:
            pass
        self._pos = self._pos + len(item)

        self.last_applied_tag = tag
    
    def get_tag_from_string(self, string: str, local_functions):
        a = self.FUNCTIONS_TO_TYPE.get(string)
        if a is not None:
            return a
        else:
            if string in local_functions:
                return "custom-function"
    
    def evaluate(self, start_row = 1):
        "Runs the simulation"
        self.output_color_to_indexes: dict[str, list] = {
            "z-label": [],
            "x-label": [],
            "label": [],
            "warning": [],
            "text": [],
            "positive-number": [],
            "negative-number": [],
            "placeholder": []
        }

        string = self.text.get("1.0", tk.END)
        if self.mode == "xz":
            player = xz.Player()
        elif self.mode == "y":
            player = y.Player()
        
        try:
            player.simulate(string)
            self.raw_output = player.output
            self.colorize_output(start_row=start_row)
        except BaseException as e:
            self.output.configure(state="normal")
            self.output.delete("1.0", tk.END)
            self.output.insert("1.0", f"Error: {e}")
            self.adjust_height(widget=self.output)
            self.output.configure(state="disabled")
            self.raw_output = [(f"Error: {e}","None")]
        
        if self.grandparent: self.grandparent.has_unsaved_changes = True
        self.execution_time = datetime.datetime.now().replace(microsecond=0)
        self.has_changed = False
        self.label2.configure(state="normal")
        self.label2.delete("1.0", tk.END)
        self.label2.tag_remove("grayed", "1.0", tk.END)
        self.label2.insert(tk.END, f"Output is shown below (Executed at {str(self.execution_time)})")
        self.label2.configure(state="disabled")

        
    
    def colorize_output(self, start_row = 1):
        self.output.configure(state="normal")
        self.output.delete("1.0", tk.END)

        row_index = start_row
        column_index = 0

        for line in self.raw_output:
            column_index = 0
            
            # for string, tag_name in line:
            string, expr_type = line
            if expr_type == "normal":
                string = re.split(r"(\n)", string)
                string = [(s, "text") for s in string]
            else:
                string = self.separate(string, expr_type)


            for string_to_insert, tag_name in string:
                
                self.output.insert(f"{row_index}.{column_index}", string_to_insert)
                if string_to_insert == "\n":
                    row_index += 1
                    column_index = 0
                else:
                    self.output.tag_add(tag_name, f"{row_index}.{column_index}", f"{row_index}.{column_index+len(string_to_insert)}")
                    if tag_name and tag_name != "none":
                        # print(f"tagname {tag_name}")
                        self.output_color_to_indexes[tag_name].append((f"{row_index}.{column_index}", f"{row_index}.{column_index+len(string_to_insert)}"))
                    column_index += len(string_to_insert)

            self.output.insert(f"{row_index}.{column_index}", "\n")
            row_index += 1

        self.output.delete(f"{row_index}.{column_index}", tk.END) # Delete last whitespace
        self.output.configure(state="disabled") 
        self.adjust_height(widget=self.output)

    def separate(self, string: str, expr_type: str):
        """
        Internal function.
        
        Separates strings in the form `label: a` or `label: a + b` into a list `[label, :, a, +, b]` 
        """
        result: list[tuple[str, str]] = []

        expr_type_to_tag_name = {
            "expr": "label",
            "x-expr": "x-label",
            "z-expr": "z-label",
            "warning": "warning"
        }

        a, b = string.split(": ")
        tag_name = expr_type_to_tag_name.get(expr_type)
        if tag_name is None:
            return [(string, "none")]
        result.append((a, tag_name))
        result.append((": ", ""))

        if expr_type == "warning":
            result.append((b, "text"))
            return result
        
        b = b.split(" ")
         
        # Either 1 or 3 items
        b_float = float(b[0])
        if b_float >= 0: # positive number
            result.append((b[0], "positive-number"))
        else: # Negative number
            result.append(('-', ""))
            result.append((b[0][1:], "negative-number"))

        if len(b) == 3:
            sign = b[1]
            number = b[2]
            result.append((f" {sign} ", ""))
            result.append((number, f"{'positive' if sign == '+' else 'negative'}-number"))
        
        return result
    
    def change_font_size(self, change: int):
        for text_widget in (self.label, self.text, self.label2, self.output):
            current_font = str(text_widget.cget("font"))
            font_family, font_size = current_font.rsplit(" ", 1)
            font_family = font_family.strip("{}")
            new_font_size = min(max(4, int(font_size) + change), 40)
            text_widget.configure(font=(font_family, new_font_size))
        self.adjust_height()
        self.adjust_height(widget=self.output)
    
    def bind_hover(self, button: tk.Button):
        button.bind("<Enter>", func=lambda e: self.on_hover(button))
        button.bind("<Leave>", func=lambda e: self.off_hover(button))

    def on_hover(self, button: tk.Button):
        button.configure(background="DeepSkyBlue4")

    def off_hover(self, button: tk.Button):
        button.configure(background="gray12")


class Page:
    def __init__(self, parent, options, scrollable: bool = False, fontname = "Courier", fontsize: int = 12):
        if scrollable:
            self.mainframe = ScrolledText(parent)
        else:
            self.mainframe = tk.Text(parent)
        self.parent = parent
        self.options = options
        self.binds = self.options["Settings"]["Bindings"]

        self.mainframe.configure(background="gray15", foreground="white", font=(fontname, fontsize), wrap=tk.WORD)
        # self.mainframe.configure(background="gray15", foreground="white", font=("Times new roman", fontsize), wrap=tk.WORD, spacing1=1, spacing3=1)

        self.pos = TkinterPosition(1,0)
        self.matches = []
        self.mainframe.bind("<Configure>", self.resize_image_on_resize)
        self.mainframe.bind(f"<{self.binds['Zoom in']}>", lambda e, x=2: self.change_font_size(e, x))
        self.mainframe.bind(f"<{self.binds['Zoom out']}>", lambda e, x=-2: self.change_font_size(e, x))
        self.tags = []
        self.fontsize = fontsize
        
        self.images: dict[str, tuple[str, ImageTk.PhotoImage]] = {} # string is a path to source

        for tag_name, foreground_color in options["Current-theme"]["Code"].items():
            self.mainframe.tag_configure(tag_name, foreground=foreground_color)
            self.tags.append(tag_name)

        for tag_name, foreground_color in options["Current-theme"]["Output"].items():
            self.mainframe.tag_configure(tag_name, foreground=foreground_color)
            self.tags.append(tag_name)
        
        self.mainframe.tag_configure("code", background="gray12", font=("Courier", self.fontsize), borderwidth=1, relief="solid", border=1, lmargin1=5, lmargin2=5, rmargin=5)
        self.mainframe.tag_configure("inline code", font=("Courier", self.fontsize))
        self.mainframe.tag_configure("header", font=('Ariel', self.fontsize+8), foreground="light blue")
        self.mainframe.tag_configure("header2", font=('Ariel', self.fontsize+5), foreground="light blue")
        self.mainframe.tag_configure("header3", font=('Ariel', self.fontsize+3), foreground="light blue")
        self.mainframe.tag_configure('highlight', background='yellow', foreground="black")
        self.mainframe.tag_configure('current_highlight', background='orange', foreground="black")
        
        self.tags += ["code", "inline code", "header", "header2", "header3", "highlight", "current_highlight"]
        self.CodeCell = Cell(None, "xz", options)

        self.headings = {} # Name: (index, depth)
        self.mainframe.bind(f"<{self.binds['Find']}>", self.open_search_widget)
        self.mainframe.pack_propagate(False)

    def reset_code_processor(self):
        self.CodeCell.text.delete("1.0", tk.END)
    
    def insert_text(self, content: str):
        self.mainframe.insert(tk.END, content)            
        if "\n" in content:
            self.pos = self.pos.add_row(content.count("\n")).reset_column() + (len(content) - content.rindex("\n") - 1)
        else:
            self.pos += len(content)
    
    def heading(self, title: str):
        self.mainframe.insert(tk.END, title)
        self.mainframe.tag_add("header", self.pos.string, (self.pos + len(title)).string)
        self.pos = self.pos.add_row(1).reset_column()
    
    def heading2(self, title: str):
        self.mainframe.insert(tk.END, title)
        self.mainframe.tag_add("header2", self.pos.string, (self.pos + len(title)).string)
        self.pos = self.pos.add_row(1).reset_column()

    def heading3(self, title: str):
        self.mainframe.insert(tk.END, title)
        self.mainframe.tag_add("header3", self.pos.string, (self.pos + len(title)).string)
        self.pos = self.pos.add_row(1).reset_column()
    
    def open_search_widget(self, event=None):
        if hasattr(self, 'search_frame'):
            self.search_frame.lift()
            self.search_text(self.search_entry.get())
            self.search_entry.focus_set()
            return

        self.search_frame = tk.Frame(self.parent, background="gray15", borderwidth=1, border=2, relief="solid")
        self.search_frame.place(relx=0.97, rely=0.01, anchor='ne')
        self.search_label = tk.Label(self.search_frame, text="Search:", background="gray15", foreground="white")
        self.search_label.grid(row=0, column=0)
        self.search_entry = tk.Entry(self.search_frame, background="gray15", foreground="white", border=0)
        self.search_entry.grid(row=0, column=1, columnspan=3)
        self.found_label = tk.Label(self.search_frame, text="Found",background="gray15", foreground="white")
        self.found_label.grid(row=1, column=0)
        self.results = tk.Label(self.search_frame, text="Found", background="gray15", foreground="white")
        self.results.grid(row=1, column=1, columnspan=3)
        self.nocase_search = tk.Button(self.search_frame, text="Aa", command=self.toggle_case, background="gray15", foreground="white")
        self.nocase_search.grid(row=2, column=0)
        self.search_frame.nocase = False
        
        self.up = tk.Button(self.search_frame, text="↑", background="gray15", foreground="white", command=lambda: self.next_match(-1))
        self.up.grid(row=2, column=1)

        self.down = tk.Button(self.search_frame, text="↓", background="gray15", foreground="white", command=lambda: self.next_match(1))
        self.down.grid(row=2, column=2)

        self.leave = tk.Button(self.search_frame, text="✖", background="gray15", foreground="white", command=lambda: self.hide_search_widget())
        self.leave.grid(row=2, column=3)

        self.search_entry.bind('<Key>', self.timer)
        self.mainframe.bind('<Key>', self.hide_search_widget)
        self.search_entry.focus_set()
    
    def toggle_case(self):
        self.search_frame.nocase = not self.search_frame.nocase
        if self.search_frame.nocase:
            self.nocase_search.configure(background="green")
        else:
            self.nocase_search.configure(background="gray15")
        search_term = self.search_entry.get()
        self.search_text(search_term)

    def hide_search_widget(self, event: tk.Event = None):
        if not event or event.keysym == "Escape":
            self.search_text("")
            self.search_frame.lower()
            self.mainframe.lift()
            self.mainframe.focus_set()

    def timer(self, event):
        self.mainframe.after(1, lambda: self.on_key_press(event))

    def on_key_press(self, event: tk.Event=None):
        if event.keysym == "Escape":
            self.hide_search_widget(event)
        elif event.keysym == "Return" or event.keysym == "Down":
            self.next_match()
        elif event.keysym == "Up":
            self.next_match(-1)
        else:
            search_term = self.search_entry.get()
            self.search_text(search_term)

    def search_text(self, search_term):
        self.mainframe.tag_remove("current_highlight", "1.0", tk.END)
        self.mainframe.tag_remove('highlight', '1.0', tk.END)
        self.search_frame.i = 0

        if search_term:
            self.matches = []
            start_pos = '1.0'
            while True:
                start_pos = self.mainframe.search(search_term, start_pos, stopindex=tk.END, nocase=self.search_frame.nocase)
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(search_term)}c"
                self.mainframe.tag_add('highlight', start_pos, end_pos)
                self.matches.append((start_pos, end_pos))
                start_pos = end_pos
            
            if self.matches:
                self.mainframe.tag_remove('highlight', self.matches[self.search_frame.i][0], self.matches[self.search_frame.i][1])
                self.mainframe.tag_add('current_highlight', self.matches[self.search_frame.i][0], self.matches[self.search_frame.i][1])
                self.mainframe.see(self.matches[self.search_frame.i][0])
                self.results.configure(text=f"{self.search_frame.i + 1} of {len(self.matches)}")

            else:
                self.results.configure(text=f"0 of 0")
        else:
            self.results.configure(text=f"0 of 0")

    
    def next_match(self, index_shift=1):
        if self.matches:
            self.mainframe.tag_add('highlight', self.matches[self.search_frame.i][0], self.matches[self.search_frame.i][1])
            self.mainframe.tag_remove('current_highlight', self.matches[self.search_frame.i][0], self.matches[self.search_frame.i][1])
            self.search_frame.i = (self.search_frame.i + index_shift) % len(self.matches)
            self.mainframe.tag_remove('highlight', self.matches[self.search_frame.i][0], self.matches[self.search_frame.i][1])
            self.mainframe.tag_add('current_highlight', self.matches[self.search_frame.i][0], self.matches[self.search_frame.i][1])
            self.mainframe.see(self.matches[self.search_frame.i][0])
            self.results.configure(text=f"{self.search_frame.i + 1} of {len(self.matches)}")
    
    def link(self, link: str, display: str):
        if link.endswith(".png") or link.endswith(".jpg"):
            try:
                # Determine the correct path for the image
                if getattr(sys, "frozen", False):
                    base_path = sys._MEIPASS  # Path for PyInstaller executable
                else:
                    base_path = os.getcwd()  # Path for script execution

                image_path = os.path.join(base_path, "images", link)
                image = Image.open(image_path)

                text_width = self.mainframe.winfo_width()
                img_width, img_height = image.size
                new_width = text_width
                new_height = int(img_height * (new_width / img_width))
                photo = ImageTk.PhotoImage(image)

                self.images[self.pos] = (image_path, photo)
                self.mainframe.image_create(tk.END, image=photo)

            except Exception as e:
                self.insert_text(display)
            
        else:
            self.mainframe.insert(tk.END, display)
            self.mainframe.tag_configure(f"link {link}", foreground="light blue", underline=True)
            self.mainframe.tag_add(f"link {link}", self.pos.string, (self.pos + len(display)).string)
            self.mainframe.tag_bind(f"link {link}", "<Button-1>", func=lambda e: webbrowser.open_new(link))
            self.pos += len(display)
    
    def inline_code(self, code: str):
        self.reset_code_processor()
        self.mainframe.insert(tk.END, code)

        self.CodeCell.text.insert("1.0", code)
        self.CodeCell.colorize_code()

        for tag, pairs in self.CodeCell.text_color_to_indexes.items():
            l = []
            for pair in pairs:
                begin, end = pair
                begin = self.string_to_position(begin).add_row(self.pos.row-1) + self.pos.column
                end = self.string_to_position(end).add_row(self.pos.row-1) + self.pos.column
                l.append(begin.string)
                l.append(end.string)
            if l:
                self.mainframe.tag_add(tag, *l)

        new_pos = self.pos + len(code)
        
        self.mainframe.tag_add("inline code", self.pos.string, new_pos.string)
        self.pos = new_pos

        
    def code_snippet(self, code: str):
        self.reset_code_processor()
        code = code + "\n"
        self.mainframe.insert(tk.END, code)

        self.CodeCell.text.insert("1.0", code)
        self.CodeCell.colorize_code()

        for tag, pairs in self.CodeCell.text_color_to_indexes.items():
            l = []
            for pair in pairs:
                begin, end = pair
                begin = self.string_to_position(begin).add_row(self.pos.row-1) + self.pos.column
                end = self.string_to_position(end).add_row(self.pos.row-1) + self.pos.column
                l.append(begin.string)
                l.append(end.string)
            if l:
                self.mainframe.tag_add(tag, *l)

        if "\n" in code:
            index = code.rindex("\n")

            new_pos = self.pos.add_row(code.count("\n")).reset_column() + (len(code) - index - 1)
        else:
            new_pos = self.pos + len(code)
        
        self.mainframe.tag_add("code", self.pos.string, new_pos.string)
        self.pos = new_pos

    def code_snippet_with_output(self, code: str):
        self.reset_code_processor()
        code = code + "\n"
        self.mainframe.insert(tk.END, code + "-----------------------------\n")
        self.CodeCell.text.insert("1.0", code)
        self.CodeCell.colorize_code()

        for tag, pairs in self.CodeCell.text_color_to_indexes.items():
            l = []
            for pair in pairs:
                begin, end = pair
                begin = self.string_to_position(begin).add_row(self.pos.row-1) + self.pos.column
                end = self.string_to_position(end).add_row(self.pos.row-1) + self.pos.column
                l.append(begin.string)
                l.append(end.string)
            if l:
                self.mainframe.tag_add(tag, *l)

        code += "-----------------------------\n"
        new_pos = self.pos.add_row(code.count("\n")).reset_column()

        self.mainframe.tag_add("code", self.pos.string, new_pos.string)
        self.pos = new_pos

        self.CodeCell.evaluate()
        output = self.CodeCell.output.get("1.0", tk.END)
        self.mainframe.insert(tk.END, output)

        for tag, pairs in self.CodeCell.output_color_to_indexes.items():
            l = []
            for pair in pairs:
                begin, end = pair
                begin = self.string_to_position(begin).add_row(self.pos.row-1) + self.pos.column
                end = self.string_to_position(end).add_row(self.pos.row-1) + self.pos.column
                l.append(begin.string)
                l.append(end.string)
            if l:
                self.mainframe.tag_add(tag, *l)

        new_pos = self.pos.add_row(output.count("\n")).reset_column()
        self.mainframe.tag_add("code", self.pos.string, new_pos.string)
        self.pos = new_pos

    def string_to_position(self, string: str):
        a,b = string.split('.')
        a = int(a)
        b = int(b)
        return TkinterPosition(a,b)

    def show_function_signature(self, func: str, module = "xz"):
        if module == "xz":
            f = xz.Player.FUNCTIONS[func]
            params = inspect.signature(f).__repr__()
        elif module == "y":
            f = y.Player.FUNCTIONS[func]
            params = inspect.signature(f).__repr__()
        params = params.removeprefix("<Signature (").removesuffix(")>").split(", ")
        if 'self' in params:
            params.remove('self')

        l = []

        regex = r"(\*?\w+)(?:: ([\w\.]+))?(?: = (\w+))?"
        for p in params:
            x = re.findall(regex,p)
            if x:
                l.append(x[0])
            elif p in "/*":
                l.append(p)
        
        self.colorize(f.__name__, l, module)
    
    def colorize(self, func: str, args, module):

        tag = self.CodeCell.get_tag_from_string(func, [])
        old_pos = self.pos
        if module == "xz":
            all_aliases = [x for x,y in xz.Player.FUNCTIONS.items() if y.__name__ == func and x != func]
        elif module == "y":
            all_aliases = [x for x,y in y.Player.FUNCTIONS.items() if y.__name__ == func and x != func]
        
        if all_aliases:
            self.insert_and_apply_tag("Aliases: ", "backslash")
            self.insert_and_apply_tag(" ".join(all_aliases), tag)
            self.mainframe.insert(tk.END, "\n")
            self.pos = self.pos.add_row(1).reset_column()


        self.insert_and_apply_tag(func, tag)
        self.insert_and_apply_tag("(", "nest-mod1")

        for arg in args:
            if isinstance(arg, tuple):
                arg_name, datatype, default = arg
                if datatype == "numpy.float32":
                    datatype = "float"

                self.insert_and_apply_tag(arg_name, "custom-function-parameter")
                
                if datatype:
                    self.insert_and_apply_tag(": ", "none")

                    self.insert_and_apply_tag(datatype, "inputs")
                
                if default:
                    self.insert_and_apply_tag(" = ", "none")

                    if default == "None":
                        self.insert_and_apply_tag(default, "comment")
                    elif default.isnumeric():
                        self.insert_and_apply_tag(default, "numbers")
                    else:
                        self.insert_and_apply_tag(default, "string")

            else:
                self.insert_and_apply_tag(arg, "setters")
        
            self.insert_and_apply_tag(", ", "none")

        self.pos -= 2
        self.mainframe.delete(self.pos.string, tk.END)
        self.insert_and_apply_tag(")", "nest-mod1")

        self.mainframe.insert(tk.END, "\n")
        self.pos = self.pos.add_row(1).reset_column()

        self.mainframe.tag_add("code", old_pos.string, self.pos.string)

    def insert_and_apply_tag(self, text, tag):
        self.mainframe.insert(tk.END, text)
        self.mainframe.tag_add(tag, self.pos.string, (self.pos+len(text)).string)
        self.pos += len(text)
    
    def finalize(self):
        self.mainframe.configure(state="disabled")

    def parse_text(self, text):
        # Regex to match different components in the markdown
        pattern = r'([#]+ .+?\n)|(```.*?```\n)|(`.*?`)|(\[.+?\]\(.+?\))|([^#`\[]+)'

        # TEMPORARY FIX: ([^#\[\]`]+) ignores brackets
        
        components = re.findall(pattern, text, re.DOTALL)

        result = [match[0] or match[1] or match[2] or match[3] or match[4] for match in components]
        
        for text in result:
            self.process_text(text)
        self.mainframe.event_generate("<Configure>")
            
    def process_text(self, text: str):
        if text.startswith("# "):
            self.heading(text[2:])
        elif text.startswith("## "):
            self.heading2(text[3:])
        elif text.startswith("### "):
            self.heading3(text[4:])
        
        elif text.startswith("`") and text.endswith("`"):
            self.inline_code(text.strip("`"))
        elif text.startswith("```") and text.endswith("```\n"):
            args = ""
            for i in text[3:]:
                if i == "\n":
                    break
                args += i

            t = text[4+len(args):len(text)-5]
            args = args.split("/")

            # should be args[0] = mothball
            if "output" in args:
                self.code_snippet_with_output(t)
            elif "signature" in args:
                if "y" in args:
                    self.show_function_signature(t, "y")
                else:
                    self.show_function_signature(t, "xz")
            else:
                self.code_snippet(t)

        elif text.startswith("[") and text.endswith(")") and "](" in text:
            display = text[1:text.index("]")]
            link = text[text.index("(")+1:len(text)-1]
            self.link(link, display)
        else:
            self.insert_text(text)
    
    @staticmethod
    def get_headings(text: str):
        lines = text.split("\n")
        headings = {}
        in_code = False
        pos = TkinterPosition(1,0)
        for line in lines:
            if line.startswith("```"):
                in_code = not in_code
            elif not in_code:
                if line.startswith("# "):
                    headings[line[2:]] = (pos.string, 1)
                elif line.startswith("## "):
                    headings[line[3:]] = (pos.string, 2)
                elif line.startswith("### "):
                    headings[line[4:]] = (pos.string, 3)
            pos = pos.add_row(1)
        
        return headings

    def resize_image_on_resize(self, event):
        for index, (src, img) in self.images.items():
            image = Image.open(src)

            img_width, img_height = image.size
            new_width = self.mainframe.winfo_width()
            new_height = int(img_height * (new_width / img_width))

            image = image.resize((new_width, new_height), Image.LANCZOS)
            image = ImageTk.PhotoImage(image)
            old_image = self.images[index][1]
            self.images[index] = (src, image)
            del old_image
            self.mainframe.image_configure(index, image=image)

    def change_font_size(self, e, change:int):
        current_font = self.mainframe.cget("font")
        font_family, font_size = current_font.rsplit(" ", 1)
        font_family = font_family.strip("{}")
        new_font_size = int(font_size) + change
        self.mainframe.configure(font=(font_family, new_font_size))
        self.fontsize = new_font_size

        self.mainframe.tag_configure("code", background="gray12", font=("Courier", self.fontsize), borderwidth=1, relief="solid", border=1, lmargin1=5, lmargin2=5, rmargin=5)
        self.mainframe.tag_configure("inline code", font=("Courier", self.fontsize))
        self.mainframe.tag_configure("header", font=('Ariel', self.fontsize+8), foreground="light blue")
        self.mainframe.tag_configure("header2", font=('Ariel', self.fontsize+5), foreground="light blue")
        self.mainframe.tag_configure("header3", font=('Ariel', self.fontsize+3), foreground="light blue")

        return "break"

class TextBox(tk.Frame):
    def __init__(self, parent, options: dict, grandparent = None, fontsize = 12, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.execution_time = None
        self.has_changed = False
        self.grandparent = grandparent
        self.fontsize = fontsize
        self._pos = TkinterPosition(1,0)
        self.headings = {}
        self.mode = 'edit'
        self.type = "text"
        self.rows = 0

        self.configure(background="gray12", border=5)

        self.timer = 0
        self.timer_id = None

        self.textbox = Page(self, options, False, fontsize=fontsize)
        self.textbox.mainframe.bind("<Key>", self.timed)
        self.textbox.mainframe.pack(expand=True, fill="y")
        # self.textbox.mainframe.pack_propagate(True)
        # self.pack_propagate(True)

        button_frame = tk.Frame(self, background="gray12")
        button_frame.pack(side="bottom", fill="x")

        # TEMPORARY FIX
        operating_system = platform.system()
        if operating_system == "Windows":
            color = "white"
        else:
            color = 'black'

        self.eval_button = tk.Button(button_frame, text="Render", command=self.render,  foreground=color, background="gray12", font=("Ariel", 10, "bold"))
        self.add_cell = tk.Button(button_frame, text="Add Cell XZ", background="gray12", foreground=color,  font=("Ariel", 10, "bold"))
        self.add_cell_y = tk.Button(button_frame, text="Add Cell Y", background="gray12", foreground=color,  font=("Ariel", 10, "bold"))
        self.add_text = tk.Button(button_frame, text="Add Text", background="gray12", foreground=color,  font=("Ariel", 10, "bold"))
        self.delete_cell = tk.Button(button_frame, text="Delete", background="gray12", foreground=color,  font=("Ariel", 10, "bold"))
        self.bind_hover(self.eval_button)
        self.bind_hover(self.add_cell)
        self.bind_hover(self.add_cell_y)
        self.bind_hover(self.add_text)
        self.bind_hover(self.delete_cell)
        self.eval_button.pack(side="left", expand=True, fill="x")
        self.add_cell.pack(side="left", expand=True, fill="x")
        self.delete_cell.pack(side="right", expand=True, fill="x")
        self.add_text.pack(side="right", expand=True, fill="x")
        self.add_cell_y.pack(side="right", expand=True, fill="x")

        self.adjust_height(mode='edit')

        self.options = options
        self.binds = self.options["Settings"]["Bindings"]

        self.textbox.mainframe.bind("<Key>", self.timed)
        self.timer = 0
        self.timer_id = None


        self.textbox.mainframe.bind(f"<{self.binds['Open']}>", lambda e: self.grandparent.load())
        self.textbox.mainframe.unbind(f"<{self.binds['Zoom in']}>")
        self.textbox.mainframe.unbind(f"<{self.binds['Zoom out']}>")
    
    def render(self, adjust: bool = True):
        self.eval_button.configure(command= self.edit, text="Edit")
        a = self.textbox.mainframe.get("1.0", tk.END)
        self.raw_text = a.strip()
        self.textbox.mainframe.delete("1.0", tk.END)
        self.textbox.parse_text(a)
        self.headings = Page.get_headings(a)
        if adjust: self.adjust_height(mode='render')
        self.textbox.mainframe.configure(state="disabled")
        self.mode = 'render'
        self.textbox.mainframe.unbind("<Key>")
    
    def edit(self):
        self.textbox.mainframe.configure(state="normal")
        for i in self.textbox.tags:
            self.textbox.mainframe.tag_remove(i, "1.0", tk.END)
        self.textbox.pos = TkinterPosition(1,0)
        self.eval_button.configure(command= self.render, text="Render")
        self.textbox.mainframe.delete("1.0", tk.END)
        self.textbox.mainframe.insert("1.0", self.raw_text)
        self.adjust_height(mode='edit')
        self.textbox.mainframe.configure(state="normal")
        self.mode = 'edit'
        self.textbox.mainframe.bind("<Key>", self.timed)

    def bind_hover(self, button: tk.Button):
        button.bind("<Enter>", func=lambda e: self.on_hover(button))
        button.bind("<Leave>", func=lambda e: self.off_hover(button))

    def on_hover(self, button: tk.Button):
        button.configure(background="DeepSkyBlue4")

    def off_hover(self, button: tk.Button):
        button.configure(background="gray12")
    
    def adjust_height(self, event=0, mode=None):
        if mode == None:
            mode = self.mode

        num_lines = self.textbox.mainframe.count("1.0", tk.END, "displaylines")[0]

        if mode == "render": # THIS ALGORITHM SHOULD BE CHANGED PART 2 (?)
            # print(f"START {num_lines} / {b}-{a}")
            # print(f"START {num_lines}")
            # num_lines = int(num_lines / (b-a))
            self.textbox.mainframe.configure(height=num_lines)
            self.textbox.mainframe.update_idletasks()
            a,b = self.textbox.mainframe.yview()
            # print(num_lines/(b-a))
            # print("BOUNDS", a,b)
            self.textbox.mainframe.configure(height=int(num_lines/(b-a)) + 1)
            self.textbox.mainframe.update_idletasks()
            # a,b = self.textbox.mainframe.yview()
            # print("NEW BOUNDS", a,b)
            

        elif mode == "edit":
            if num_lines != self.rows:
                self.textbox.mainframe.configure(height=num_lines)
                self.textbox.mainframe.update_idletasks()
            # print(num_lines)
        
        self.rows = num_lines
    
    def adjust_width(self, width: int):
        self.textbox.mainframe.configure(width=width)

    
    def timed(self, event: tk.Event = 0):
        if self.timer_id is not None and event and event.keysym not in ["Control_L", "Control_R", "Shift_L", "Shift_R", "Caps_Lock", "Escape", "Down", "Up", "Left", "Right", "Alt_R", "Alt_L"]:
            self.after_cancel(self.timer_id)
        
        if event and event.keysym not in ["Control_L", "Control_R", "Shift_L", "Shift_R", "Caps_Lock", "Escape", "Down", "Up", "Left", "Right", "Alt_R", "Alt_L"]:
            if not self.has_changed:
                self.has_changed = True
                if self.grandparent: self.grandparent.has_unsaved_changes = True
            self.after_idle(self.adjust_height)



if __name__ == "__main__":
    r = tk.Tk()
    a = Cell(r, "xz", options) # Test
    a.grid(row=0, column=0, sticky="nswe")
    r.grid_rowconfigure(0, weight=1)
    r.grid_columnconfigure(0, weight=1)
    
    
    # r = tk.Tk()
    # a = TextBox(r, options)
    # a.grid(row=0, column=0, sticky="nswe")
    # r.grid_rowconfigure(0, weight=1)
    # r.grid_columnconfigure(0, weight=1)
    r.mainloop()
