# -*- coding: utf-8 -*-
import os
import sys
import random
import tkinter as tk
from tkinter import ttk
import threading
import time
import queue
import webbrowser  # 用于调用外部浏览器

class RandomRollCallApp:
    def __init__(self, root):
        self.root = root
        self.root.title("随机点名系统")
        self.root.geometry("600x580")
        self.root.minsize(600, 580)
        self.root.configure(bg='#1a1a2e')
        
        # 语音功能初始化
        self.voice_enabled = tk.BooleanVar(value=True)
        self.voice_queue = queue.Queue()
        self.voice_available = False
        self.check_voice_available()
        
        # 设置窗口居中
        self.center_window()
        
        # 初始化变量
        self.is_rolling = False
        self.names_list = []
        self.animation_thread = None
        
        # 获取软件所在目录
        if getattr(sys, 'frozen', False):
            self.app_dir = os.path.dirname(sys.executable)
        else:
            self.app_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.app_dir = os.path.abspath(self.app_dir)
        self.list_folder = os.path.join(self.app_dir, "list")
        
        print(f"软件目录: {self.app_dir}")
        print(f"名单文件夹: {self.list_folder}")
        
        # 检查并创建list文件夹
        self.check_and_create_list_folder()
        
        # 创建UI
        self.create_ui()
        
        # 加载名单文件
        self.refresh_list_files()
        
        # 启动语音线程
        if self.voice_available:
            self.start_voice_thread()
    
    def check_voice_available(self):
        """检查语音是否可用"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.stop()
            del engine
            self.voice_available = True
            print("✅ 语音引擎可用")
        except Exception as e:
            print(f"⚠️ 语音引擎不可用: {e}")
            self.voice_available = False
    
    def start_voice_thread(self):
        """启动语音处理线程"""
        self.voice_thread = threading.Thread(target=self.voice_worker, daemon=True)
        self.voice_thread.start()
    
    def voice_worker(self):
        """语音工作线程 - 每次播报都重新初始化引擎"""
        import pyttsx3
        
        while True:
            try:
                text = self.voice_queue.get(timeout=0.5)
                if text is None:
                    break
                if not self.voice_enabled.get():
                    continue
                
                try:
                    engine = pyttsx3.init()
                    engine.setProperty('rate', 180)
                    engine.setProperty('volume', 0.9)
                    
                    try:
                        voices = engine.getProperty('voices')
                        for voice in voices:
                            if 'chinese' in voice.name.lower() or 'zh' in voice.id.lower():
                                engine.setProperty('voice', voice.id)
                                break
                    except:
                        pass
                    
                    engine.say(text)
                    engine.runAndWait()
                    engine.stop()
                    del engine
                    
                except Exception as e:
                    print(f"语音播报错误: {e}")
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"语音线程错误: {e}")
    
    def speak(self, text):
        """添加文本到语音队列"""
        if self.voice_available and self.voice_enabled.get():
            try:
                self.voice_queue.put(text)
            except:
                pass
    
    def open_website(self, event=None):
        """
        点击kuxin时在系统默认浏览器中打开网站
        webbrowser.open() 会自动调用外部浏览器（Chrome/Edge/Firefox等）
        """
        try:
            # new=2 表示在新标签页打开（如果浏览器已运行）
            # autoraise=True 表示将浏览器窗口置顶
            webbrowser.open("https://081252.xyz/", new=2, autoraise=True)
            print("正在打开网站: https://081252.xyz/")
        except Exception as e:
            print(f"无法打开网站: {e}")
    
    def center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()
        width = 600
        height = 580
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def check_and_create_list_folder(self):
        """检查并创建list文件夹"""
        if not os.path.exists(self.list_folder):
            os.makedirs(self.list_folder)
            print(f"已创建文件夹: {self.list_folder}")
            sample_file = os.path.join(self.list_folder, "示例名单.txt")
            with open(sample_file, 'w', encoding='utf-8') as f:
                f.write("张三\n李四\n王五\n赵六\n钱七\n孙八\n周九\n吴十")
            print(f"已创建示例文件: {sample_file}")
            
            try:
                if sys.platform == 'win32':
                    os.startfile(self.list_folder)
                elif sys.platform == 'darwin':
                    os.system(f'open "{self.list_folder}"')
                else:
                    os.system(f'xdg-open "{self.list_folder}"')
                print(f"已自动打开文件夹: {self.list_folder}")
            except Exception as e:
                print(f"无法自动打开文件夹: {e}")
    
    def create_ui(self):
        """创建用户界面"""
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(expand=True, fill='both', padx=30, pady=(30, 10))
        
        # 标题
        title_label = tk.Label(
            main_frame, 
            text="随机点名系统", 
            font=('Microsoft YaHei', 24, 'bold'),
            bg='#1a1a2e',
            fg='#eee'
        )
        title_label.pack(pady=(0, 15))
        
        # 名字显示区域
        self.name_frame = tk.Frame(
            main_frame,
            bg='#16213e',
            highlightbackground='#0f3460',
            highlightthickness=2,
            bd=0
        )
        self.name_frame.pack(fill='x', pady=15, ipady=35)
        
        self.name_label = tk.Label(
            self.name_frame,
            text="准备开始",
            font=('Microsoft YaHei', 44, 'bold'),
            bg='#16213e',
            fg='#e94560'
        )
        self.name_label.pack(expand=True)
        
        # 按钮区域
        button_frame = tk.Frame(main_frame, bg='#1a1a2e')
        button_frame.pack(pady=15)
        
        # 开始点名按钮
        self.roll_button = tk.Button(
            button_frame,
            text="开始点名",
            font=('Microsoft YaHei', 16, 'bold'),
            bg='#e94560',
            fg='white',
            activebackground='#ff6b6b',
            activeforeground='white',
            bd=0,
            padx=40,
            pady=12,
            cursor='hand2',
            command=self.toggle_roll
        )
        self.roll_button.pack()
        
        # 语音控制区域
        voice_frame = tk.Frame(main_frame, bg='#1a1a2e')
        voice_frame.pack(pady=10, fill='x')
        
        # 语音开关复选框
        self.voice_checkbox = tk.Checkbutton(
            voice_frame,
            text="🔊 语音播报",
            variable=self.voice_enabled,
            font=('Microsoft YaHei', 11),
            bg='#1a1a2e',
            fg='#aaa',
            selectcolor='#16213e',
            activebackground='#1a1a2e',
            activeforeground='#fff',
            cursor='hand2'
        )
        self.voice_checkbox.pack(side='left', padx=(0, 20))
        
        # 语音状态提示
        voice_status_text = "语音就绪" if self.voice_available else "语音不可用"
        voice_status_color = '#2ecc71' if self.voice_available else '#e74c3c'
        self.voice_status = tk.Label(
            voice_frame,
            text=voice_status_text,
            font=('Microsoft YaHei', 10),
            bg='#1a1a2e',
            fg=voice_status_color
        )
        self.voice_status.pack(side='left')
        
        # 测试语音按钮
        if self.voice_available:
            test_voice_btn = tk.Button(
                voice_frame,
                text="测试",
                font=('Microsoft YaHei', 9),
                bg='#16213e',
                fg='white',
                bd=0,
                padx=15,
                pady=3,
                cursor='hand2',
                command=self.test_voice
            )
            test_voice_btn.pack(side='right')
        
        # 名单选择区域
        select_frame = tk.Frame(main_frame, bg='#1a1a2e')
        select_frame.pack(pady=15, fill='x')
        
        select_label = tk.Label(
            select_frame,
            text="选择名单：",
            font=('Microsoft YaHei', 12),
            bg='#1a1a2e',
            fg='#aaa'
        )
        select_label.pack(side='left', padx=(0, 10))
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            'TCombobox',
            fieldbackground='#16213e',
            background='#16213e',
            foreground='white',
            arrowcolor='#e94560'
        )
        style.map('TCombobox', fieldbackground=[('readonly', '#16213e')])
        
        self.list_var = tk.StringVar()
        self.list_combobox = ttk.Combobox(
            select_frame,
            textvariable=self.list_var,
            state='readonly',
            font=('Microsoft YaHei', 11),
            width=25
        )
        self.list_combobox.pack(side='left', fill='x', expand=True)
        self.list_combobox.bind('<<ComboboxSelected>>', self.on_list_selected)
        
        refresh_btn = tk.Button(
            select_frame,
            text="刷新",
            font=('Microsoft YaHei', 10),
            bg='#16213e',
            fg='white',
            bd=0,
            padx=10,
            cursor='hand2',
            command=self.refresh_list_files
        )
        refresh_btn.pack(side='left', padx=(10, 0))
        
        # 底部信息栏
        bottom_frame = tk.Frame(main_frame, bg='#1a1a2e', height=30)
        bottom_frame.pack(side='bottom', fill='x', pady=(10, 0))
        bottom_frame.pack_propagate(False)
        
        # 左侧：Made by（普通文字）
        made_by_label = tk.Label(
            bottom_frame,
            text="Made by ",
            font=('Microsoft YaHei', 9, 'italic'),
            bg='#1a1a2e',
            fg='#888'
        )
        made_by_label.pack(side='left')
        
        # 可点击的 kuxin 链接
        self.kuxin_label = tk.Label(
            bottom_frame,
            text="kuxin",
            font=('Microsoft YaHei', 9, 'italic', 'underline'),
            bg='#1a1a2e',
            fg='#4da6ff',
            cursor='hand2'
        )
        self.kuxin_label.pack(side='left')
        # 绑定点击事件 - 点击后调用 open_website 打开外部浏览器
        self.kuxin_label.bind("<Button-1>", self.open_website)
        # 悬停效果
        self.kuxin_label.bind("<Enter>", lambda e: self.kuxin_label.config(fg='#66b3ff'))
        self.kuxin_label.bind("<Leave>", lambda e: self.kuxin_label.config(fg='#4da6ff'))
        
        # 右侧：状态栏
        self.status_label = tk.Label(
            bottom_frame,
            text="准备就绪",
            font=('Microsoft YaHei', 9),
            bg='#1a1a2e',
            fg='#666'
        )
        self.status_label.pack(side='right', padx=(10, 0))
    
    def test_voice(self):
        """测试语音功能"""
        self.speak("语音测试")
        self.root.after(1000, lambda: self.speak("测试二"))
        self.root.after(2000, lambda: self.speak("测试三"))
    
    def refresh_list_files(self):
        """刷新名单文件列表"""
        txt_files = []
        if os.path.exists(self.list_folder):
            for file in os.listdir(self.list_folder):
                if file.endswith('.txt'):
                    txt_files.append(file)
        
        self.list_combobox['values'] = txt_files
        
        if txt_files:
            if not self.list_var.get() or self.list_var.get() not in txt_files:
                self.list_combobox.set(txt_files[0])
                self.load_names(txt_files[0])
        else:
            self.list_combobox.set('')
            self.names_list = []
            self.name_label.config(text="无名单文件")
    
    def on_list_selected(self, event=None):
        """当选择名单时触发"""
        selected = self.list_var.get()
        if selected:
            self.load_names(selected)
    
    def load_names(self, filename):
        """加载名单文件"""
        filepath = os.path.join(self.list_folder, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.names_list = [line.strip() for line in f if line.strip()]
            self.name_label.config(text="准备开始", fg='#e94560')
            folder_name = os.path.basename(self.app_dir)
            self.status_label.config(text=f"已加载: {filename} ({len(self.names_list)}人) | ./{folder_name}/list/")
        except Exception as e:
            self.name_label.config(text="加载失败", fg='#ff4757')
            self.status_label.config(text=f"错误: {str(e)}")
    
    def toggle_roll(self):
        """切换点名状态"""
        if not self.names_list:
            self.name_label.config(text="请先选择名单", fg='#ff4757')
            return
        
        if self.is_rolling:
            return
        
        self.start_roll()
    
    def start_roll(self):
        """开始随机点名动画"""
        self.is_rolling = True
        self.roll_button.config(
            text="点名中...",
            bg='#666',
            state='disabled'
        )
        self.name_label.config(fg='#f39c12')
        
        self.animation_thread = threading.Thread(target=self.animation_loop)
        self.animation_thread.daemon = True
        self.animation_thread.start()
    
    def animation_loop(self):
        """动画循环"""
        start_time = time.time()
        duration = 3
        
        while time.time() - start_time < duration:
            name = random.choice(self.names_list)
            self.root.after(0, lambda n=name: self.name_label.config(text=n))
            elapsed = time.time() - start_time
            if elapsed < 1:
                time.sleep(0.15)
            elif elapsed < 2:
                time.sleep(0.08)
            else:
                time.sleep(0.03)
        
        final_name = random.choice(self.names_list)
        self.root.after(0, lambda: self.finish_roll(final_name))
    
    def finish_roll(self, final_name):
        """完成点名并播报"""
        self.is_rolling = False
        self.name_label.config(text=final_name, fg='#2ecc71')
        self.roll_button.config(
            text="开始点名",
            bg='#e94560',
            state='normal'
        )
        
        # 播报选中的名字
        self.speak(final_name)
        
        self.name_frame.config(highlightbackground='#2ecc71')
        self.root.after(500, lambda: self.name_frame.config(highlightbackground='#0f3460'))

def main():
    root = tk.Tk()
    app = RandomRollCallApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
