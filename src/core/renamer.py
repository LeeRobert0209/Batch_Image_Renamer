
import os
import re
from datetime import datetime
from PIL import Image

class RenamerEngine:
    """
    负责计算文件的新名称，不进行实际的重命名操作。
    支持：序列重命名、正则、大小写转换、元数据提取。
    """
    def __init__(self):
        self.rules = {}

    def set_rules(self, rules):
        """
        设置重命名规则。
        rules: dict, 包含如 'mode', 'prefix', 'suffix', 'start_index', 'regex_pattern' 等。
        """
        self.rules = rules

    def generate_preview(self, file_list):
        """
        生成预览列表。
        file_list: list of full file paths
        returns: list of (original_name, new_name, status)
        """
        preview_data = []
        files = sorted(file_list) # 默认排序
        
        # 序列计数器初始化
        counter = int(self.rules.get('start_index', 1))
        padding = int(self.rules.get('padding', 0))

        for idx, file_path in enumerate(files):
            try:
                original_name = os.path.basename(file_path)
                directory = os.path.dirname(file_path)
                name_part, ext = os.path.splitext(original_name)
                ext = ext.lower() # 默认统一小写扩展名，或者根据规则

                new_name = original_name # 默认不变

                mode = self.rules.get('mode', 'sequence')

                if mode == 'sequence':
                    prefix = self.rules.get('prefix', '')
                    if not prefix: # 如果没有前缀，尝试使用文件夹名
                         prefix = os.path.basename(directory)
                    
                    suffix = self.rules.get('suffix', '')
                    
                    # 格式化数字
                    num_str = str(counter).zfill(padding)
                    new_name = f"{prefix}{suffix}_{num_str}{ext}"
                    counter += 1

                elif mode == 'regex':
                    pattern = self.rules.get('regex_pattern', '')
                    repl = self.rules.get('regex_replacement', '')
                    if pattern:
                        try:
                            # 仅对文件名部分进行正则替换，保留扩展名? 或者整个文件名
                            # 这里假设是对整个文件名进行替换
                            new_name = re.sub(pattern, repl, original_name)
                        except re.error:
                            new_name = "[正则错误]"

                elif mode.startswith('metadata_'):
                    try:
                        prefix = self.rules.get('prefix', '')
                        suffix = self.rules.get('suffix', '')

                        with Image.open(file_path) as img:
                            num_str = str(counter).zfill(padding)
                            
                            meta_part = ""
                            if mode == 'metadata_resolution':
                                width, height = img.size
                                meta_part = f"{width}x{height}"
                            
                            elif mode == 'metadata_date':
                                # 尝试获取拍摄日期 Exif.DateTimeOriginal (36867) 或 DateTime (306)
                                exif = img._getexif() or {}
                                date_str = exif.get(36867) or exif.get(306)
                                if date_str:
                                    dt = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                                    meta_part = dt.strftime('%Y%m%d_%H%M%S')
                                else:
                                    mtime = os.path.getmtime(file_path)
                                    dt = datetime.fromtimestamp(mtime)
                                    meta_part = dt.strftime('%Y%m%d_%H%M%S')

                            elif mode == 'metadata_model':
                                exif = img._getexif() or {}
                                model = exif.get(272, "UnknownCamera")
                                meta_part = re.sub(r'[^\w\-]', '', model.replace(' ', '_'))
                            
                            # 拼接: Prefix + Meta + Suffix + _Sequence.ext
                            # 如果用户不想要中间的下划线，必须自己控制后缀或者前缀
                            # 这里默认连接符处理：
                            # 如果有后缀，sequence 前面的下划线通常是需要的，除非 suffix 结尾已有
                            new_name = f"{prefix}{meta_part}{suffix}_{num_str}{ext}"

                            counter += 1
                    except Exception:
                        new_name = f"[无法读取图片]{ext}"
                
                # 公共后处理：大小写转换
                case_mode = self.rules.get('case', 'none')
                if case_mode == 'lower':
                    new_name = new_name.lower()
                elif case_mode == 'upper':
                    new_name = new_name.upper()

                # 公共后处理：Web 安全 (空格转下划线)
                if self.rules.get('web_safe', False):
                    new_name = new_name.replace(" ", "_")

                status = "OK"
                if new_name == original_name:
                    status = "无变化"
                
                preview_data.append({
                    "original": original_name,
                    "new": new_name,
                    "path": file_path,
                    "status": status
                })

            except Exception as e:
                preview_data.append({
                    "original": os.path.basename(file_path),
                    "new": "Error",
                    "path": file_path,
                    "status": str(e)
                })
        
        return preview_data

