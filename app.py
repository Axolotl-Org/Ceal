import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from traceback import print_exc as tb
import customtkinter as ctk
from pprint import pprint

import json
import os
import webcfg

LOCAL_CFG = "./custom_cfg.json"
WEB_CFG = webcfg.CLOUD_CONFIG_PATH
CONFIG_PATH = "./config.json"

use_cloud = True

# 新增配置窗口类
class ConfigWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("映射配置")
        self.geometry("800x600")
        self.after(100, self.lift)
        self.grab_set()
        
        self.custom_config_path = LOCAL_CFG
        self._create_widgets()
        self._load_config()

    def _create_widgets(self):
        # 创建TabView
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 添加两个标签页
        self.mapper_tab = self.tabview.add("Mapper")
        self.resolver_tab = self.tabview.add("Resolver")
        
        # Mapper表格
        self._create_table(self.mapper_tab, "Mapper")
        # Resolver表格
        self._create_table(self.resolver_tab, "Resolver")
        
        # 底部按钮区域
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        # 添加按钮
        ctk.CTkButton(btn_frame, text="添加行", command=self._add_row).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="删除行", command=self._delete_row).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="从网络加载", command=self._load_from_web).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="保存配置", command=self._save_config).pack(side="right", padx=5)

    def _create_table(self, parent, table_type):
        # 创建表格框架
        frame = ctk.CTkScrollableFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 表头
        header = ctk.CTkFrame(frame)
        header.pack(fill="x")
        
        if table_type == "Mapper":
            ctk.CTkLabel(header, text="源地址", width=200).pack(side="left", padx=1)
            ctk.CTkLabel(header, text="目标地址", width=200).pack(side="left", padx=1)
            setattr(self, "mapper_entries", [])
            # 创建内容容器
            self.mapper_content = ctk.CTkFrame(frame)
            self.mapper_content.pack(fill="both", expand=True)
        else:
            ctk.CTkLabel(header, text="域名", width=200).pack(side="left", padx=1)
            ctk.CTkLabel(header, text="IP地址", width=200).pack(side="left", padx=1)
            setattr(self, "resolver_entries", [])
            # 创建内容容器
            self.resolver_content = ctk.CTkFrame(frame)
            self.resolver_content.pack(fill="both", expand=True)

    def _add_row(self, current_tab = None):
        
        # 获取当前激活的标签页
        if current_tab is None:
            current_tab = self.tabview.get()
        
        if current_tab == "Mapper":
            frame = ctk.CTkFrame(self.mapper_content)  # 修改为使用mapper_content
            frame.pack(fill="x", padx=10, pady=5)
            
            src_entry = ctk.CTkEntry(frame, width=200)
            src_entry.pack(side="left", padx=1)
            dest_entry = ctk.CTkEntry(frame, width=200)
            dest_entry.pack(side="left", padx=1)
            
            self.mapper_entries.append((src_entry, dest_entry))
        else:
            frame = ctk.CTkFrame(self.resolver_content)  # 修改为使用resolver_content
            frame.pack(fill="x", padx=10, pady=5)
            
            domain_entry = ctk.CTkEntry(frame, width=200)
            domain_entry.pack(side="left", padx=1)
            ip_entry = ctk.CTkEntry(frame, width=200)
            ip_entry.pack(side="left", padx=1)
            
            self.resolver_entries.append((domain_entry, ip_entry))

    def _delete_row(self):
        current_tab = self.tabview.get()
        last_row = None
        if current_tab == "Mapper" and self.mapper_entries:
            last_row = self.mapper_entries.pop()
        elif self.resolver_entries:
            last_row = self.resolver_entries.pop()
        else: return

        parent_frame = last_row[0].master
        
        # 从列表中移除并销毁行的Widget
        for widget in last_row:
            widget.destroy()

        parent_frame.destroy()
        

    def _load_from_web(self):
        try:
            mapper, resolver = webcfg.get_config_from_web()
            if mapper and resolver:
                self._clear_tables()
                
                # 加载Mapper数据
                for src, dests in mapper.items():
                    for dest in dests:
                        # dest -> src
                        self._add_row(current_tab="Mapper")
                        self.mapper_entries[-1][1].insert(0, src)
                        self.mapper_entries[-1][0].insert(0, dest)
                
                # 加载Resolver数据
                for ip, domains in resolver.items():
                    for domain in domains:
                        self._add_row(current_tab="Resolver")
                        self.resolver_entries[-1][0].insert(0, domain)
                        self.resolver_entries[-1][1].insert(0, ip)
        except Exception as e:
            messagebox.showerror("加载错误", f"从网络加载配置失败: {str(e)}")

    def _clear_tables(self):
        for entries in [self.mapper_entries, self.resolver_entries]:
            while entries:
                row = entries.pop()
                for widget in row:
                    widget.destroy()

    def _save_config(self):
        try:
            mapper = {}
            resolver = {}
            
            # 收集Mapper数据
            for src_entry, dest_entry in self.mapper_entries:
                src = src_entry.get()
                dest = dest_entry.get()
                if src and dest:
                    if dest in mapper:
                        mapper[dest].append(src)
                    else:
                        mapper[dest] = [src]
            
            # 收集Resolver数据
            for domain_entry, ip_entry in self.resolver_entries:
                domain = domain_entry.get()
                ip = ip_entry.get()
                if domain and ip:
                    if ip in resolver:
                        resolver[ip].append(domain)
                    else:
                        resolver[ip] = [domain]
            
            # 保存到文件
            config = {
                "mapper": mapper,
                "resolver": resolver
            }
            
            with open(self.custom_config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
            messagebox.showinfo("成功", "配置已保存到custom_cfg.json")
            
        except Exception as e:
            messagebox.showerror("保存错误", f"保存配置失败: {str(e)}")

    def _load_config(self):
        try:
            if os.path.isfile(self.custom_config_path):
                with open(self.custom_config_path, 'r') as f:
                    config = json.load(f)
                    
                self._clear_tables()
                
                # 加载Mapper数据
                for dest, srcs in config.get("mapper", {}).items():
                    for src in srcs:
                        self._add_row("Mapper")
                        self.mapper_entries[-1][0].insert(0, src)
                        self.mapper_entries[-1][1].insert(0, dest)
                
                # 加载Resolver数据
                for ip, domains in config.get("resolver", {}).items():
                    for domain in domains:
                        self._add_row("Resolver")
                        self.resolver_entries[-1][0].insert(0, domain)
                        self.resolver_entries[-1][1].insert(0, ip)
                        
        except Exception as e:
            messagebox.showerror("加载错误", f"加载本地配置失败: {str(e)}")
            tb(e)


class ChromeLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Chrome Launcher")
        self.geometry("600x400")  # 增加窗口高度
        self._create_widgets()
        self._load_config()

    def _create_widgets(self):
        # Chrome Binary Path Section
        ctk.CTkLabel(self, text="Chrome Binary Path:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.path_entry = ctk.CTkEntry(self, width=400)
        self.path_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        self.browse_btn = ctk.CTkButton(self, text="Browse", width=80, command=self._browse_chrome)
        self.browse_btn.grid(row=0, column=2, padx=10, pady=10)

        # 替换原有命令行参数输入框为配置按钮 (row 1)
        self.config_btn = ctk.CTkButton(self, text="配置映射", command=self._open_config)
        self.config_btn.grid(row=1, column=1, padx=10, pady=10)

        # 新增配置URL输入框 (row 2)
        ctk.CTkLabel(self, text="配置URL:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.url_entry = ctk.CTkEntry(self, width=400)
        
        self.url_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        # 是否使用云配置
        self.cloud_switch = ctk.CTkSwitch(self, text="使用云配置", command=self._toggle_cloud)
        self.cloud_switch.grid(row=2, column=2, padx=10, pady=10, sticky="w")
        self.cloud_switch.select() if use_cloud else self.cloud_switch.deselect()

        # Launch Button
        self.launch_btn = ctk.CTkButton(self, text="Launch Chrome", command=self._launch_chrome)
        self.launch_btn.grid(row=3, column=1, padx=10, pady=20, sticky="ew")

        # Configure grid column weights
        self.grid_columnconfigure(1, weight=1)

    def _browse_chrome(self):
        path = filedialog.askopenfilename(
            title="Select Chrome Executable",
            filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
        )
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    def _launch_chrome(self):
        chrome_path = self.path_entry.get()

        if not chrome_path:
            messagebox.showerror("Error", "Please select Chrome executable path")
            return

        try:
            cmd = [chrome_path]
            args = mapper_str()
            cmd.extend(args)
            pprint(args) # debug
            # 启动Chrome
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to launch Chrome: {str(e)}")
            tb(e)
        else:
            self._save_config()  # 新增配置保存

    @staticmethod
    def _toggle_cloud():
        global use_cloud
        use_cloud = not use_cloud

    # 新增配置保存方法
    def _save_config(self):
        config = {
            "chrome_path": self.path_entry.get(),
            "config_url": self.url_entry.get()
        }
        
        try:
            with open(CONFIG_PATH, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            messagebox.showerror("Config Error", f"保存配置失败: {str(e)}")

    # 新增配置加载方法
    def _load_config(self):
        try:
            if os.path.isfile(CONFIG_PATH):
                with open(CONFIG_PATH, 'r') as f:
                    config = json.load(f)
                    uri = config.get("config_url", webcfg.URL)
                    webcfg.URL = uri
                    self.path_entry.insert(0, config.get("chrome_path", ""))
                    self.url_entry.insert(0, uri)

            else:
                self.url_entry.insert(0, webcfg.URL)
        except Exception as e:
            messagebox.showerror("Config Error", f"读取配置失败: {str(e)}")
    def _open_config(self):
        """打开映射配置窗口"""
        if not hasattr(self, '_config_window') or not self._config_window.winfo_exists():
            self._config_window = ConfigWindow(self)
    
def mapper_str():
    """获取映射配置"""
    # 这里可以根据需要返回映射配置
    cfg = {}
    cfg["mapper"], cfg["resolver"] = {}, {}
    if use_cloud:
        mapper, resolver = webcfg.get_config_from_web()
        cfg["mapper"].update(mapper)
        cfg["resolver"].update(resolver)
    
    mapper, resolver = webcfg.get_config(LOCAL_CFG)
    # print(mapper, resolver)
    cfg["mapper"].update(mapper)
    cfg["resolver"].update(resolver)

    arr1 = []
    for src, dests in cfg["mapper"].items():
        for dest in dests:
            arr1.append(f"MAP {dest} {src}")

    arr2 = []
    for ip, domains in cfg["resolver"].items():
        for domain in domains:
            arr2.append(f"MAP {domain} {ip}")
    
    s1 = ", ".join(arr1)
    s2 = ", ".join(arr2)

    return f'--host-rules={s1}', f'--host-resolver-rules={s2}'
        
        
        

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    app = ChromeLauncher()
    app.mainloop()