
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DRAG_DROP_AVAILABLE = True
except ImportError:
    DRAG_DROP_AVAILABLE = False
    
from src.core.renamer import RenamerEngine
from src.core.file_ops import FileProcessor

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("全能批量图片重命名工具 v1.0")
        self.root.geometry("800x600")
        
        # Core Components
        self.renamer = RenamerEngine()
        self.processor = FileProcessor()
        
        # State
        self.current_files = [] # List of full paths
        
        # UI Setup
        self._setup_icon()
        self._setup_style()
        self._create_layout()
        self._bind_events()

    def _setup_icon(self):
        """生成并设置程序图标"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            # Create a 64x64 icon
            isize = 64
            img = Image.new('RGBA', (isize, isize), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Blue rounded rectangle background
            bg_color = (33, 150, 243) # Material Blue
            draw.rounded_rectangle((0, 0, isize, isize), radius=16, fill=bg_color)
            
            # White text "R"
            # Try to load a font, fallback to default
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()
                
            text = "R"
            # Get text bounding box for centering
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (isize - text_width) / 2
            y = (isize - text_height) / 2 - 4 # slightly adjust up
            
            draw.text((x, y), text, font=font, fill="white")
            
            # Set as window icon
            from PIL import ImageTk
            self.icon_img = ImageTk.PhotoImage(img) # Keep reference
            self.root.iconphoto(True, self.icon_img)
            
        except Exception as e:
            print(f"Failed to set icon: {e}")

    def _setup_style(self):
        style = ttk.Style()
        
        # 强制使用 'clam' 主题以支持自定义背景色
        style.theme_use('clam')
        
        # 强制定义亮色系配色，确保不压抑
        # 定义全局字体，优先使用微软雅黑，回退到黑体
        default_font = ("Microsoft YaHei UI", 10)
        bold_font = ("Microsoft YaHei UI", 10, "bold")
        large_bold_font = ("Microsoft YaHei UI", 12, "bold")
        
        # 定义颜色常量
        COLOR_BG_MAIN = "#f5f7fa" # 极浅蓝灰
        COLOR_BG_WHITE = "#ffffff"
        COLOR_PRIMARY = "#2196f3" # Material Blue
        COLOR_SUCCESS = "#4caf50" # Material Green
        COLOR_TEXT = "#37474f"
        COLOR_ACCENT = "#1976d2"
        
        # 配置常规控件颜色 (浅灰背景，深黑文字)
        style.configure(".", background=COLOR_BG_MAIN, foreground=COLOR_TEXT, font=default_font)
        style.configure("TFrame", background=COLOR_BG_MAIN)
        style.configure("TLabel", background=COLOR_BG_MAIN, foreground=COLOR_TEXT, font=default_font)
        
        # 按钮样式 (普通)
        style.configure("TButton", font=default_font, padding=8, borderwidth=1)
        style.map("TButton", background=[('active', '#e0e0e0')])
        
        # 按钮样式 (主要操作 - 蓝色)
        # 在 clam 主题下，background 是有效的
        style.configure("Primary.TButton", font=bold_font, background=COLOR_PRIMARY, foreground="white", borderwidth=0)
        style.map("Primary.TButton", 
            background=[('active', COLOR_ACCENT), ('disabled', '#bdc3c7')],
            foreground=[('disabled', '#ecf0f1')]
        )
        
        # 按钮样式 (执行操作 - 绿色强调)
        style.configure("Action.TButton", font=large_bold_font, background=COLOR_SUCCESS, foreground="white", padding=10, borderwidth=0)
        style.map("Action.TButton", 
            background=[('active', '#43a047')],
            relief=[('pressed', 'sunken')]
        )
        
        # LabelFrame 标题
        style.configure("TLabelframe", background=COLOR_BG_MAIN, borderwidth=2, relief="groove")
        style.configure("TLabelframe.Label", font=bold_font, foreground=COLOR_ACCENT, background=COLOR_BG_MAIN)

        # Toolbar
        style.configure("Toolbar.TFrame", background="#e3f2fd") # 浅蓝顶部条
        style.configure("Toolbar.TLabel", background="#e3f2fd")
        
        # Treeview (列表)
        style.configure("Treeview", 
            background=COLOR_BG_WHITE, 
            fieldbackground=COLOR_BG_WHITE, 
            foreground=COLOR_TEXT,
            font=("Microsoft YaHei UI", 10), 
            rowheight=30
        )
        style.configure("Treeview.Heading", font=bold_font, background="#e1f5fe", foreground="#0277bd") # 浅蓝表头
        style.map("Treeview", background=[("selected", COLOR_PRIMARY)], foreground=[("selected", COLOR_BG_WHITE)])

        # Notebook (选项卡)
        style.configure("TNotebook", background=COLOR_BG_MAIN)
        style.configure("TNotebook.Tab", padding=[12, 6], font=default_font)
        style.map("TNotebook.Tab", background=[("selected", COLOR_PRIMARY)], foreground=[("selected", COLOR_TEXT)])

        # 底部状态栏略深一点以区分
        # 由于我们是用 Label 模拟状态栏，这里不需要专门配置，只需要在创建时指定颜色即可或者保持统一


    def _create_layout(self):
        # Top Toolbar
        toolbar = ttk.Frame(self.root, style="Toolbar.TFrame", padding=10)
        toolbar.pack(fill=tk.X)
        
        ttk.Button(toolbar, text="添加文件夹", command=self.load_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="清空列表", command=self.clear_list).pack(side=tk.LEFT, padx=5)
        self.undo_btn = ttk.Button(toolbar, text="撤回上一步", command=self.undo_action, state=tk.DISABLED)
        self.undo_btn.pack(side=tk.RIGHT, padx=5)

        # Main Split
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left Panel: Settings
        left_frame = ttk.LabelFrame(paned, text="重命名规则", padding=5)
        paned.add(left_frame, weight=1)
        
        self._create_settings_ui(left_frame)
        
        # Right Panel: Preview
        right_frame = ttk.LabelFrame(paned, text="实时预览", padding=5)
        paned.add(right_frame, weight=3)
        
        self._create_preview_ui(right_frame)
        
        # Bottom Status
        self.status_var = tk.StringVar(value="准备就绪")
        ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, background="#e0e0e0").pack(fill=tk.X)

    def _create_settings_ui(self, parent):
        # ... (Notebook part skipped in context, will keep unchanged in diff logic if possible or overwrite carefully)
        # Notebook for Modes
        self.nb = ttk.Notebook(parent)
        self.nb.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # ... (Tabs content are same as previous, omitting strictly sequential logic for brevity in tool call, 
        # but to be safe I will just target the button area if replace_file_content supports context matching well)
        
        # I will replace the Action Button area specifically first, then Toolbar.
        pass # Logic handled by multiple replacements below for safety 


    def _create_settings_ui(self, parent):
        # 1. 基础配置 (Prefix, Suffix, Sequence)
        # 使用 Grid 布局
        ttk.Label(parent, text="起始序号:").grid(row=0, column=0, sticky='w', pady=5)
        self.start_idx_var = tk.StringVar(value="1")
        ttk.Entry(parent, textvariable=self.start_idx_var, width=10).grid(row=0, column=1, sticky='w')
        ttk.Label(parent, text="例如: 1", foreground="gray").grid(row=0, column=2, sticky='w', padx=5)
        
        ttk.Label(parent, text="序号位数 (Padding):").grid(row=1, column=0, sticky='w', pady=5)
        self.padding_var = tk.StringVar(value="3")
        ttk.Spinbox(parent, from_=1, to=10, textvariable=self.padding_var, width=8).grid(row=1, column=1, sticky='w')
        ttk.Label(parent, text="例如: 3 (生成 001)", foreground="gray").grid(row=1, column=2, sticky='w', padx=5)

        ttk.Label(parent, text="前缀 (Prefix):").grid(row=2, column=0, sticky='w', pady=5)
        self.prefix_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.prefix_var).grid(row=2, column=1, sticky='we')
        ttk.Label(parent, text="例如: Vacation_", foreground="gray").grid(row=2, column=2, sticky='w', padx=5)
        
        ttk.Label(parent, text="后缀 (Suffix):").grid(row=3, column=0, sticky='w', pady=5)
        self.suffix_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.suffix_var).grid(row=3, column=1, sticky='we')
        ttk.Label(parent, text="例如: _edit", foreground="gray").grid(row=3, column=2, sticky='w', padx=5)

        # 2. 插入动态元数据 (原元数据模式)
        ttk.Separator(parent, orient='horizontal').grid(row=4, column=0, columnspan=3, sticky='ew', pady=15)
        
        ttk.Label(parent, text="插入动态信息:").grid(row=5, column=0, sticky='nw', pady=5)
        self.meta_mode_var = tk.StringVar(value="none") # Default is none (sequence only)
        
        frame_meta = ttk.Frame(parent)
        frame_meta.grid(row=5, column=1, columnspan=2, sticky='w')
        
        ttk.Radiobutton(frame_meta, text="无 (仅使用前后缀+序号)", variable=self.meta_mode_var, value="none").pack(anchor='w', pady=2)
        ttk.Radiobutton(frame_meta, text="分辨率 (宽x高)", variable=self.meta_mode_var, value="resolution").pack(anchor='w', pady=2)
        ttk.Radiobutton(frame_meta, text="拍摄时间 (EXIF)", variable=self.meta_mode_var, value="date").pack(anchor='w', pady=2)
        ttk.Radiobutton(frame_meta, text="相机型号", variable=self.meta_mode_var, value="model").pack(anchor='w', pady=2)
        
        # 3. 配置网格权重
        parent.columnconfigure(1, weight=1)
        
        opt_frame = ttk.LabelFrame(parent, text="通用选项", padding=10)
        opt_frame.grid(row=6, column=0, columnspan=3, sticky='ew', pady=15)
        
        self.case_var = tk.StringVar(value="全大写")
        ttk.OptionMenu(opt_frame, self.case_var, "全大写", "不改变", "全小写", "全大写").pack(anchor='w')
        
        self.websafe_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt_frame, text="Web安全 (空格转下划线)", variable=self.websafe_var).pack(anchor='w')
        
        self.sidecar_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt_frame, text="同步重命名同名文件 (.txt/.json)", variable=self.sidecar_var).pack(anchor='w')

        # Action Button
        # 刷新按钮已移除，功能改为实时触发
        ttk.Button(parent, text="执行重命名", command=self.run_rename, style="Action.TButton").grid(row=7, column=0, columnspan=3, sticky='ew', pady=(10, 10))

    def _create_preview_ui(self, parent):
        cols = ("原文件名", "新文件名", "状态")
        self.tree = ttk.Treeview(parent, columns=cols, show='headings')
        
        self.tree.heading("原文件名", text="原文件名")
        self.tree.column("原文件名", width=200)
        
        self.tree.heading("新文件名", text="新文件名")
        self.tree.column("新文件名", width=200)
        
        self.tree.heading("状态", text="状态")
        self.tree.column("状态", width=80)
        
        scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _bind_events(self):
        if DRAG_DROP_AVAILABLE:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.on_drop)
        
        # 绑定所有输入变量的变化以实现实时预览
        # 定义需要监听的变量列表
        vars_to_trace = [
            self.prefix_var, self.suffix_var, self.start_idx_var, self.padding_var,
            self.meta_mode_var,
            self.case_var, self.websafe_var
        ]
        
        for var in vars_to_trace:
            # trace_add 'write' 模式会在变量值修改时触发
            # 使用 lambda *args 忽略 trace 回调传来的内部参数
            var.trace_add("write", lambda *args: self.update_preview())

    def load_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            # 如果列表不为空，询问是否清空
            if self.current_files:
                ans = messagebox.askyesnocancel("导入方式", "当前列表已有文件。\n\n选择【是】保留并追加新文件\n选择【否】清空列表并仅加载新文件")
                if ans is None: # Cancel
                    return
                elif ans is False: # No -> Replace
                    self.current_files = []
            
            self.add_files_from_folder(folder)

    def on_drop(self, event):
        path = event.data
        if path.startswith('{') and path.endswith('}'):
            path = path[1:-1]
        
        if os.path.isdir(path):
            self.add_files_from_folder(path)
        elif os.path.isfile(path):
            # 支持单个拖拽？暂时先支持追加到列表
            if path not in self.current_files:
                self.current_files.append(path)
                self.update_preview()

    def add_files_from_folder(self, folder):
        valid_exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif'}
        count = 0
        for f in os.listdir(folder):
            ext = os.path.splitext(f)[1].lower()
            if ext in valid_exts:
                full_path = os.path.normpath(os.path.join(folder, f))
                if full_path not in self.current_files:
                    self.current_files.append(full_path)
                    count += 1
        self.status_var.set(f"已添加 {count} 个文件")
        self.update_preview()

    def clear_list(self):
        self.current_files = []
        self.update_preview()

    def get_current_rules(self):
        # Map localized case option to internal key
        case_map = {
            "不改变": "none",
            "全小写": "lower", 
            "全大写": "upper"
        }
        internal_case = case_map.get(self.case_var.get(), "none")

        # Determine mode based on meta usage
        # 如果 meta_mode 不是 'none'，则使用 metadata_xxx 逻辑
        # 否则使用 序列化逻辑 ('sequence')
        meta_val = self.meta_mode_var.get()
        if meta_val and meta_val != 'none':
            mode = f"metadata_{meta_val}"
        else:
            mode = 'sequence'

        rules = {
            'case': internal_case,
            'web_safe': self.websafe_var.get(),
            'mode': mode,
            'prefix': self.prefix_var.get(),
            'suffix': self.suffix_var.get(),
            'start_index': int(self.start_idx_var.get()) if self.start_idx_var.get().isdigit() else 1,
            'padding': int(self.padding_var.get())
        }
        
        return rules

    def update_preview(self):
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not self.current_files:
            return

        rules = self.get_current_rules()
        self.renamer.set_rules(rules)
        
        self.preview_data = self.renamer.generate_preview(self.current_files)
        
        for item in self.preview_data:
            values = (item['original'], item['new'], item['status'])
            tag = 'error' if 'Error' in item['status'] else 'ok'
            self.tree.insert('', 'end', values=values, tags=(tag,))
        
        self.tree.tag_configure('error', foreground='red')

    def run_rename(self):
        if not hasattr(self, 'preview_data') or not self.preview_data:
            messagebox.showinfo("提示", "请先加载文件并刷新预览")
            return
            
        if messagebox.askyesno("确认", "确定要执行重命名吗？此操作将修改文件名。"):
            count, error = self.processor.execute_rename(self.preview_data, sync_sidecar=self.sidecar_var.get())
            if error:
                messagebox.showerror("部分错误", f"完成 {count} 个文件，但遇到错误: {error}")
            else:
                messagebox.showinfo("成功", f"成功重命名 {count} 个文件！")
                self.undo_btn.config(state=tk.NORMAL)
            
            # Refresh list with new names
            # Logic: We can't easily guess new names if they were complex. 
            # Simplest way: Clear list and ask user to reload, or try to map.
            # Here: Clear list
            self.current_files = [] # Reset
            self.update_preview() 
            self.status_var.set("重命名完成，列表已清空")

    def undo_action(self):
        count, error = self.processor.undo_last_operation()
        if error:
            messagebox.showerror("撤回失败", error)
        else:
            messagebox.showinfo("撤回成功", f"已撤回 {count} 个文件的操作")
            self.undo_btn.config(state=tk.DISABLED) # 简单起见，只支持单步撤回
