import os
import json
import sys
from pathlib import Path

def load_config(filename):
    """加载配置文件 - 优先读取外部 config，再回退到内部资源"""
    if getattr(sys, 'frozen', False):
        app_dir = Path(sys.executable).parent
    else:
        app_dir = Path(__file__).parent.parent.parent
    
    external_config_path = app_dir / "config" / filename
    if external_config_path.exists():
        try:
            with open(external_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"警告: 无法读取外部配置文件 {external_config_path}: {e}")
    
    try:
        if getattr(sys, 'frozen', False):
            import tempfile
            internal_path = Path(sys._MEIPASS) / "config" / filename
        else:
            internal_path = Path(__file__).parent.parent.parent / "config" / filename
        
        with open(internal_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"错误: 无法加载配置文件 {filename}: {e}")
        return {}