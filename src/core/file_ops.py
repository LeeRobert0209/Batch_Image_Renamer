
import os
import shutil

class FileProcessor:
    """
    负责执行实际的文件操作，包括重命名、移动、格式转换等。
    维护操作历史以支持撤回。
    """
    def __init__(self):
        # 历史栈，每个元素是一个列表: [{'from': path, 'to': path}, ...]
        self.history_stack = []

    def execute_rename(self, preview_data, sync_sidecar=False):
        """
        执行重命名操作。
        preview_data: RenamerEngine.generate_preview 返回的数据结构
        sync_sidecar: 是否同步重命名同名文件 (如 .txt, .json)
        returns: (success_count, error_msg)
        """
        operation_log = [] # 记录本次操作，用于撤回
        success_count = 0 

        # 为了避免命名冲突（例如 1->2, 2->3），我们采用两步法：
        # 1. 全部重命名为临时名称
        # 2. 临时名称 -> 最终名称
        # 但这比较耗时。如果直接重命名，需要反向排序或者拓扑排序？
        # 系统原有的简单逻辑是两步法，这里保留两步法以确保安全。
        
        # 筛选出需要重命名的项
        to_process = [item for item in preview_data if item['status'] not in ("无变化", "Error")]
        
        if not to_process:
            return 0, "没有需要执行的任务"

        try:
            temp_map = []
            
            # 第一步：原名 -> 临时名
            for item in to_process:
                old_path = item['path']
                dir_name = os.path.dirname(old_path)
                new_filename = item['new']
                
                # 生成临时文件名
                temp_filename = f"__tmp_{os.path.basename(old_path)}"
                temp_path = os.path.join(dir_name, temp_filename)
                
                os.rename(old_path, temp_path)
                temp_map.append({
                    "temp": temp_path,
                    "final": os.path.join(dir_name, new_filename),
                    "original": old_path # 记录原始路径用于撤回
                })
                
                # Sidecar 处理 (仅支持简单的一对一同名文件)
                if sync_sidecar:
                    base_old = os.path.splitext(old_path)[0]
                    # 查找该目录下以 base_old 开头的文件（除去自身）
                    # 简化处理：假设只处理 .txt, .json, .xml
                    for ext in ['.txt', '.json', '.xml']:
                        side_old = base_old + ext
                        if os.path.exists(side_old):
                            side_new_base = os.path.splitext(os.path.join(dir_name, new_filename))[0]
                            side_tmp = os.path.join(dir_name, f"__tmp_{os.path.basename(side_old)}")
                            
                            os.rename(side_old, side_tmp)
                            temp_map.append({
                                "temp": side_tmp,
                                "final": side_new_base + ext,
                                "original": side_old
                            })

            # 第二步：临时名 -> 最终名
            for item in temp_map:
                os.rename(item['temp'], item['final'])
                operation_log.append({
                    "from": item['original'],
                    "to": item['final']
                })
                success_count += 1
            
            # 记录到历史栈
            self.history_stack.append(operation_log)
            return success_count, None

        except Exception as e:
            # 尝试回滚已经在本次操作中完成的部分（可选，这里暂不做自动回滚，依靠手动撤回）
            return success_count, str(e)

    def undo_last_operation(self):
        """
        撤回上一次操作。
        returns: (success_count, error_msg)
        """
        if not self.history_stack:
            return 0, "没有可撤回的操作"
        
        last_ops = self.history_stack.pop()
        success_count = 0
        
        try:
            # 反向执行：将 'to' 重命名回 'from'
            # 同样可能通过中转文件更安全，但作为撤回，暂时直接重命名
            # 注意：如果文件被移动或覆盖，可能会失败
            for op in last_ops:
                if os.path.exists(op['to']):
                    os.rename(op['to'], op['from'])
                    success_count += 1
            
            return success_count, None
        except Exception as e:
            return success_count, str(e)
