import os
import json
import platform

options = {"Current-theme": 
{"Code":{
    "fast-movers": "#00ffff",
    "slow-movers": "#1e90ff",
    "stoppers": "#7fffd4",
    "setters": "#ff8c00",
    "returners": "#ff6347",
    "inputs": "#00ff00",
    "modifiers": "#00ff88",
    "calculators": "#ffc0cb",
    "numbers": "#ffff00",
    "comment": "#808080",
    "nest-mod1": "#ee82ee",
    "nest-mod2": "#4169e1",
    "nest-mod0": "#ffd700",
    "keyword": "#ff00ff",
    "variable": "#7cfc00",
    "string": "#ff3030",
    "backslash": "#fa8072",
    "comment-backslash": "#424242",
    "custom-function-parameter": "#e066ff",
    "custom-function": "#c6e2ff",
    "error": "#ff0000"},
"Output":{
    "z-label": "#00ffff",
    "x-label": "#ee82ee",
    "label": "#ff8c00",
    "warning": "#ff6347",
    "text": "#ffd700",
    "positive-number": "#00ff00",
    "negative-number": "#ff6347",
    "placeholder": "#808080"
},
"Name": "Default"
},
"Themes": {
    "Default": {"Code":{
        "fast-movers": "cyan",
        "slow-movers": "dodger blue",
        "stoppers": "aquamarine",
        "setters": "dark orange",
        "returners": "tomato",
        "inputs": "lime",
        "modifiers": "#00ff88",
        "calculators": "pink",
        "numbers": "yellow",
        "comment": "gray",
        "nest-mod1": "violet",
        "nest-mod2": "royal blue",
        "nest-mod0": "gold",
        "keyword": "magenta",
        "variable": "lawn green",
        "string": "firebrick1",
        "backslash": "salmon",
        "comment-backslash": "gray26",
        "custom-function-parameter": "MediumOrchid1",
        "custom-function": "SlateGray1",
        "error": "red"},
    "Output":{
        "z-label": "cyan",
        "x-label": "violet",
        "label": "dark orange",
        "warning": "tomato",
        "text": "gold",
        "positive-number": "lime",
        "negative-number": "tomato",
        "placeholder": "gray"
    }
    }
}, 
"Settings": {
    "Ask before deleting a cell": False,
    "Max lines": 12,
    "Bindings": {
        "Open": "Control-o",
        "New": "Control-n",
        "Save": "Control-s",
        "Undo": "Control-z",
        "Redo": "Control-y",
        "Zoom in": "Control-equal",
        "Zoom out": "Control-minus",
        "Execute": "Control-r",
        "Find": "Control-f"
    }},
"Show-tutorial": True,
"Default-Font-Size": 12,
"Version": "v1.0.2"
}

def get_path_to_options():
    operating_system = platform.system()
    if operating_system == "Windows":
        return os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Mothball", "Mothball Settings", "Options.json")
    elif operating_system == "Darwin":
        return os.path.join(os.path.expanduser("~"), "Library", "Application Support", "Mothball", "Mothball Settings", "Options.json")
    elif operating_system == "Linux":
        return os.path.join(os.path.expanduser("~"), ".config", "Mothball", "Mothball Settings", "Options.json")
        

def create_directories(force_update = False):
    operating_system = platform.system()
    if operating_system == "Windows":
        create_windows_directories(force_update)
    elif operating_system == "Darwin":
        create_mac_directories(force_update)
    elif operating_system == "Linux":
        create_linux_directories(force_update)

def create_windows_directories(force_update = False):
    user_directory = os.path.expanduser("~")
    os.makedirs(os.path.join(user_directory, "AppData", "Roaming", "Mothball", "Mothball Settings"), exist_ok=True)
    os.makedirs(os.path.join(user_directory, "Documents", "Mothball", "Notebooks"), exist_ok=True)

    if not os.path.exists(os.path.join(user_directory, "AppData" ,"Roaming", "Mothball", "Mothball Settings", "Options.json")) or force_update:
        with open(os.path.join(user_directory, "AppData", "Roaming", "Mothball", "Mothball Settings", "Options.json"), "w") as file:
            json.dump(options, file)   

def create_mac_directories(force_update = False):
    user_directory = os.path.expanduser("~")
    os.makedirs(os.path.join(user_directory, "Library", "Application Support", "Mothball", "Mothball Settings"), exist_ok=True)
    os.makedirs(os.path.join(user_directory, "Documents", "Mothball", "Notebooks"), exist_ok=True)

    if not os.path.exists(os.path.join(user_directory, "Library" ,"Application Support", "Mothball", "Mothball Settings", "Options.json")) or force_update:
        with open(os.path.join(user_directory, "Library" ,"Application Support", "Mothball", "Mothball Settings" ,"Options.json"), "w") as file:
            json.dump(options, file)

def create_linux_directories(force_update = False):
    user_directory = os.path.expanduser("~")
    os.makedirs(os.path.join(user_directory, ".config", "Mothball" ,"Mothball Settings"), exist_ok=True)
    os.makedirs(os.path.join(user_directory, "Documents", "Mothball", "Notebooks"), exist_ok=True)

    if not os.path.exists(os.path.join(user_directory, ".config", "Mothball", "Mothball Settings", "Options.json")) or force_update:
        with open(os.path.join(user_directory, ".config", "Mothball", "Mothball Settings", "Options.json"), "w") as file:
            json.dump(options, file)

def create_minigame_directories():
    operating_system = platform.system()
    user_directory = os.path.expanduser("~")
    if operating_system == "Windows":
        directory = os.path.join(user_directory, "AppData", "Roaming", "Mothball", "Minigames")
    elif operating_system == "Darwin":
        directory = os.path.join(user_directory, "Library", "Application Support", "Mothball", "Minigames")
    elif operating_system == "Linux":
        directory = os.path.join(user_directory, ".config", "Mothball", "Minigames")
    
    os.makedirs(directory, exist_ok=True)
    if not os.path.exists(os.path.join(directory, "Stats.json")):
        
        a = {"Parkour Wordle": {
            "Wins": 0, "Lose": 0, "Last Game": {"Game ID": 0, "Result": None}, "Resume Game State": {1:"", 2:"", 3:"", 4:"", 5:"", 6:""}, "Guess Distribution": {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 0:0}
        }}
        
        with open(os.path.join(directory, "Stats.json"), "w") as file:
            json.dump(a, file, indent=4)

def get_path_to_minigame_stats():
    operating_system = platform.system()
    user_directory = os.path.expanduser("~")
    if operating_system == "Windows":
        directory = os.path.join(user_directory, "AppData", "Roaming", "Mothball", "Minigames", "Stats.json")
    elif operating_system == "Darwin":
        directory = os.path.join(user_directory, "Library", "Application Support", "Mothball", "Minigames", "Stats.json")
    elif operating_system == "Linux":
        directory = os.path.join(user_directory, ".config", "Mothball", "Minigames", "Stats.json")
    return directory
    

def get_options():
    operating_system = platform.system()
    if operating_system == "Windows":
        return get_windows_options()
    elif operating_system == "Darwin":
        return get_mac_options()
    elif operating_system == "Linux":
        return get_linux_options()

def get_windows_options():
    with open(os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Mothball", "Mothball Settings" ,"Options.json")) as file:
        return json.load(file)

def get_mac_options():
    with open(os.path.join(os.path.expanduser("~"), "Library", "Application Support", "Mothball", "Mothball Settings", "Options.json")) as file:
        return json.load(file)
    
def get_linux_options():
    with open(os.path.join(os.path.expanduser("~"), ".config", "Mothball", "Mothball Settings", "Options.json")) as file:
        return json.load(file)

def update_documents(version_str: str):
    "Updates the document files and the settings file"
    create_minigame_directories()
    user_directory = os.path.expanduser("~")
    documents_path = os.path.join(user_directory, "Documents", "Mothball", "Notebooks")
    json_files = [f for f in os.listdir(documents_path) if f.endswith('.json')]

    for json_file in json_files:
        file_path = os.path.join(documents_path, json_file)
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        data['version'] = version_str
        
        # For this update... (i should probably change this)
        i = 1
        while True:
            if str(i) not in data:
                break
            if data[str(i)].get('type') is None:
                data[str(i)]['type'] = 'code'
            i += 1

        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    
    ops = get_options()
    def update_dict(target, source):
        for key, value in source.items():
            if key not in target:
                target[key] = value
            elif isinstance(value, dict) and isinstance(target[key], dict):
                update_dict(target[key], value)
                

    update_dict(ops, options)

    options_path = get_path_to_options()
    with open(options_path, 'w') as file:
        json.dump(ops, file, indent=4)
