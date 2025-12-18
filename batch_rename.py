import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DRAG_DROP_AVAILABLE = True
except ImportError:
    DRAG_DROP_AVAILABLE = False

def rename_images_in_folder(folder_path, allowed_extensions, update_status_callback):
    """
    Renames images in the folder.
    allowed_extensions: set of strings, e.g., {'.jpg', '.png'}
    """
    if not folder_path:
        return

    folder_name = os.path.basename(folder_path)
    if not folder_name:
        folder_name = os.path.basename(os.path.dirname(folder_path))

    try:
        # Filter files based on allowed extensions
        files = [f for f in os.listdir(folder_path) 
                 if os.path.splitext(f)[1].lower() in allowed_extensions]
        files.sort()

        if not files:
            messagebox.showinfo("提示", "在选定的文件夹中没有找到符合条件的图片文件。")
            return

        count = 0
        total = len(files)
        
        temp_map = []
        # First pass
        for index, filename in enumerate(files, start=1):
            ext = os.path.splitext(filename)[1].lower()
            new_name = f"{folder_name}_{index}{ext}"
            old_path = os.path.join(folder_path, filename)
            
            temp_name = f"__temp_{folder_name}_{index}{ext}"
            temp_path = os.path.join(folder_path, temp_name)
            
            os.rename(old_path, temp_path)
            temp_map.append((temp_path, os.path.join(folder_path, new_name)))
            
            update_status_callback(f"处理中... {int((index/total)*50)}%")

        # Second pass
        for index, (temp_path, final_path) in enumerate(temp_map, start=1):
            os.rename(temp_path, final_path)
            update_status_callback(f"处理中... {50 + int((index/total)*50)}%")

        update_status_callback("准备就绪")
        messagebox.showinfo("成功", f"成功重命名了 '{folder_name}' 中的 {len(files)} 张图片！")

    except Exception as e:
        messagebox.showerror("错误", f"发生错误: {str(e)}")
        update_status_callback("错误")

class RenameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("批量图片重命名工具")
        self.root.geometry("600x450")
        self.root.resizable(False, False)

        # Enable Drag and Drop
        if DRAG_DROP_AVAILABLE:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.drop)

        # Style
        style = ttk.Style()
        style.configure("TButton", font=("Microsoft YaHei", 12), padding=10)
        style.configure("TLabel", font=("Microsoft YaHei", 11))
        style.configure("TRadiobutton", font=("Microsoft YaHei", 10))

        # Main Container (for centering)
        container = ttk.Frame(root)
        container.pack(expand=True, fill=tk.BOTH, padx=40, pady=40)

        # Title Label
        title_label = ttk.Label(container, text="批量图片重命名工具", font=("Microsoft YaHei", 18, "bold"))
        title_label.pack(pady=(0, 30))

        # Info Label
        drop_text = "将文件夹拖入此处，或点击按钮选择" if DRAG_DROP_AVAILABLE else "点击按钮选择文件夹"
        info_text = f"{drop_text}\n指定类型的图片将被重命名为：\n'文件夹名_1.类型', '文件夹名_2.类型' 等。"
        
        info_label = ttk.Label(container, text=info_text, justify=tk.CENTER)
        info_label.pack(pady=(0, 20))

        # File Type Selection Frame
        type_frame = ttk.LabelFrame(container, text="请选择一种文件类型", padding=20)
        type_frame.pack(fill=tk.X, pady=10)

        self.selected_type = tk.StringVar(value="JPG")
        
        # Mapping display names to actual extensions
        self.ext_map = {
            'JPG': ['.jpg', '.jpeg'],
            'PNG': ['.png'],
            'WEBP': ['.webp']
        }

        # Radio Buttons
        radios_frame = ttk.Frame(type_frame)
        radios_frame.pack(expand=True)
        
        types = ['JPG', 'PNG', 'WEBP']
        for t in types:
            rb = ttk.Radiobutton(radios_frame, text=t, variable=self.selected_type, value=t)
            rb.pack(side=tk.LEFT, padx=20)

        # Select Button
        self.select_btn = ttk.Button(container, text="选 择 文 件 夹", command=self.select_folder)
        self.select_btn.pack(pady=30, ipadx=30)

        # Status Label
        self.status_var = tk.StringVar()
        self.status_var.set("准备就绪" if DRAG_DROP_AVAILABLE else "准备就绪 (未检测到拖拽库)")
        self.status_label = ttk.Label(container, textvariable=self.status_var, foreground="gray")
        self.status_label.pack(side=tk.BOTTOM)

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.process_folder(folder_selected)

    def drop(self, event):
        path = event.data
        # Handle curly braces for paths with spaces usually sent by DnD
        if path.startswith('{') and path.endswith('}'):
            path = path[1:-1]
            
        if os.path.isdir(path):
            self.process_folder(path)
        else:
            messagebox.showwarning("提示", "请拖入一个文件夹！")

    def process_folder(self, folder_path):
        # Build allowed extensions set based on single selection
        type_key = self.selected_type.get()
        allowed = set(self.ext_map[type_key])
        
        self.status_var.set("处理中...")
        self.root.update_idletasks()
        rename_images_in_folder(folder_path, allowed, self.update_status)

    def update_status(self, text):
        self.status_var.set(text)
        self.root.update_idletasks()

if __name__ == "__main__":
    if DRAG_DROP_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    app = RenameApp(root)
    root.mainloop()
