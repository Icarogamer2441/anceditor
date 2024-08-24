import tkinter as tk
import json
import os
import re

# Load syntax configuration
def load_syntax_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

syntax_config = load_syntax_config('syntax_config.json')

root = tk.Tk()
root.configure(bg='black')

current_directory = os.getcwd()
current_file = None

def update_window_title():
    global current_file
    if current_file:
        root.title(f"anceditor - {os.path.basename(current_file)}")
    else:
        root.title("anceditor - sem arquivos abertos")

def update_explorer():
    explorer_frame.delete(0, tk.END)
    for item in os.listdir(current_directory):
        full_path = os.path.join(current_directory, item)
        if os.path.isfile(full_path):
            explorer_frame.insert(tk.END, item)
        elif os.path.isdir(full_path):
            explorer_frame.insert(tk.END, item)
    root.after(500, update_explorer)

def open_item(event):
    global current_directory, current_file
    selected = explorer_frame.curselection()
    if selected:
        item = explorer_frame.get(selected[0])
        full_path = os.path.join(current_directory, item)
        if os.path.isfile(full_path):
            current_file = full_path
            with open(full_path, "r") as f:
                content_text.delete("1.0", tk.END)
                content_text.insert("1.0", f.read())
                apply_syntax_highlighting()
                update_window_title()

def create_file():
    def create():
        file_name = file_name_entry.get()
        if file_name:
            with open(os.path.join(current_directory, file_name), "w") as f:
                pass
            update_explorer()
        popup.destroy()
    popup = tk.Toplevel(root)
    popup.title("Criar Arquivo")
    file_name_label = tk.Label(popup, text="Nome do arquivo:")
    file_name_label.pack()
    file_name_entry = tk.Entry(popup)
    file_name_entry.pack()
    create_button = tk.Button(popup, text="Criar", command=create)
    create_button.pack()

def go_back():
    global current_directory, current_file
    parent_directory = os.path.dirname(current_directory)
    if os.path.exists(parent_directory):
        current_directory = parent_directory
        current_file = None
        update_explorer()
        update_window_title()

def go_to_directory():
    global current_directory, current_file
    selected = explorer_frame.curselection()
    if selected:
        item = explorer_frame.get(selected[0])
        full_path = os.path.join(current_directory, item)
        if os.path.isdir(full_path):
            current_directory = full_path
            current_file = None
            update_explorer()
            update_window_title()

def save_file(event=None):
    if current_file:
        with open(current_file, "w") as f:
            f.write(content_text.get("1.0", tk.END))

def insert_spaces(event):
    content_text.insert(tk.INSERT, ' ' * 4)
    return 'break'

def handle_backspace(event):
    index = content_text.index(tk.INSERT)
    line, col = map(int, index.split('.'))

    if col >= 4:
        previous_chars = content_text.get(f"{line}.{col-4}", f"{line}.{col}")
        if previous_chars == '    ':
            content_text.delete(f"{line}.{col-4}", f"{line}.{col}")
            return 'break'

    return None

def apply_syntax_highlighting():
    content_text.tag_remove('keyword', '1.0', 'end')
    content_text.tag_remove('func_keyword', '1.0', 'end')
    content_text.tag_remove('default_func', '1.0', 'end')
    content_text.tag_remove('comment', '1.0', 'end')
    content_text.tag_remove('string', '1.0', 'end')
    content_text.tag_remove('type', '1.0', 'end')
    content_text.tag_remove('boolean', '1.0', 'end')

    text = content_text.get("1.0", tk.END)

    def add_tags(pattern, tag):
        for match in re.finditer(pattern, text, re.DOTALL):
            start_index = f"1.0+{match.start()}c"
            end_index = f"1.0+{match.end()}c"
            content_text.tag_add(tag, start_index, end_index)

    # Define patterns
    keyword_pattern = r'\b(?:' + '|'.join(re.escape(k) for k in syntax_config["keywords"]) + r')\b'
    func_keyword_pattern = r'\b(?:' + '|'.join(re.escape(k) for k in syntax_config["funcsetkeywords"]) + r')\b'
    default_func_pattern = r'\b(?:' + '|'.join(re.escape(f) for f in syntax_config["default_functions"]) + r')\b'

    comment_pattern = re.escape(syntax_config["comments"]) + r'.*?(?=\n|$)'
    multiline_start = re.escape(syntax_config["multilinecomments"][0])
    multiline_end = re.escape(syntax_config["multilinecomments"][1])
    multiline_comment_pattern = f'{multiline_start}.*?{multiline_end}'

    string_pattern = r'"[^"]*"'
    type_pattern = r'\b(?:' + '|'.join(re.escape(t) for t in syntax_config["types"]) + r')\b'
    boolean_pattern = r'\b(?:' + '|'.join(re.escape(b) for b in syntax_config["booleans"]) + r')\b'

    # Apply tags
    add_tags(keyword_pattern, 'keyword')
    add_tags(func_keyword_pattern, 'func_keyword')
    add_tags(default_func_pattern, 'default_func')
    add_tags(comment_pattern, 'comment')
    add_tags(multiline_comment_pattern, 'comment')
    add_tags(string_pattern, 'string')
    add_tags(type_pattern, 'type')
    add_tags(boolean_pattern, 'boolean')

    # Configure tags
    content_text.tag_configure('keyword', foreground='blue')
    content_text.tag_configure('func_keyword', foreground='red')
    content_text.tag_configure('default_func', foreground='purple')
    content_text.tag_configure('comment', foreground='green')
    content_text.tag_configure('string', foreground='orange')
    content_text.tag_configure('type', foreground='cyan')
    content_text.tag_configure('boolean', foreground='magenta')

def on_text_change(event=None):
    apply_syntax_highlighting()
    update_default_functions()

def update_default_functions():
    global syntax_config
    text = content_text.get("1.0", tk.END)
    func_keywords = syntax_config["funcsetkeywords"]

    for keyword in func_keywords:
        pattern = rf'\b{re.escape(keyword)}\b\s+(\w+)'
        for match in re.finditer(pattern, text):
            func_name = match.group(1)
            if func_name not in syntax_config["default_functions"]:
                syntax_config["default_functions"].append(func_name)

    apply_syntax_highlighting()

menu_bar = tk.Menu(root)

file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Voltar", command=go_back)
file_menu.add_command(label="Abrir", command=go_to_directory)
file_menu.add_separator()
file_menu.add_command(label="Criar Arquivo", command=create_file)
file_menu.add_command(label="Salvar", command=save_file, accelerator="Ctrl+S")
file_menu.add_separator()
file_menu.add_command(label="Sair", command=root.quit)
menu_bar.add_cascade(label="Arquivo", menu=file_menu)

root.config(menu=menu_bar)

explorer_frame = tk.Listbox(root, bg='black', fg='white')
explorer_frame.pack(side="left", fill="both", expand=True)
explorer_frame.bind("<Double-1>", open_item)

content_text = tk.Text(root, bg='black', fg='white', insertbackground='white', wrap='none')
content_text.pack(side="right", fill="both", expand=True)

content_text.bind('<Tab>', insert_spaces)
content_text.bind('<BackSpace>', handle_backspace)
content_text.bind('<KeyRelease>', on_text_change)

root.bind("<Control-n>", lambda event: create_file())
root.bind("<Control-s>", save_file)

update_explorer()
update_window_title()

root.mainloop()
