import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
from main import run_pipeline
from PIL import Image, ImageTk
import time
#LOGO
def show_splash():
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.geometry('400x300+500+200')
    try:
        img = Image.open('logo.png')
        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = Image.ANTIALIAS
        img = img.resize((400, 300), resample)
        logo = ImageTk.PhotoImage(img)
        label = tk.Label(splash, image=logo)
        label.image = logo
        label.pack()
    except Exception as e:
        print(f"加载logo.png失败: {e}")
        label = tk.Label(splash, text='LOGO', font=('Arial', 40))
        label.pack(expand=True)
    splash.update()
    splash.after(3000, splash.destroy)
    splash.mainloop()

show_splash()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("视频字幕翻译工具")
        self.geometry("600x400")
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        # 输入视频
        tk.Label(self, text="输入视频:").place(x=30, y=30)
        self.input_entry = tk.Entry(self, width=50)
        self.input_entry.place(x=100, y=30)
        tk.Button(self, text="选择", command=self.select_input).place(x=500, y=27)

        # 输出视频
        tk.Label(self, text="输出视频:").place(x=30, y=70)
        self.output_entry = tk.Entry(self, width=50)
        self.output_entry.place(x=100, y=70)
        tk.Button(self, text="选择", command=self.select_output).place(x=500, y=67)

        # OCR方式
        tk.Label(self, text="OCR方式:").place(x=30, y=110)
        self.ocr_var = tk.StringVar(value="paddleocr")
        tk.Radiobutton(self, text="PaddleOCR", variable=self.ocr_var, value="paddleocr").place(x=100, y=110)
        tk.Radiobutton(self, text="大模型OCR", variable=self.ocr_var, value="bigmodel").place(x=200, y=110)

        # 大模型平台选择与API输入
        tk.Label(self, text="大模型平台:").place(x=30, y=150)
        self.platform_var = tk.StringVar(value="deepseek")
        self.platform_menu = tk.OptionMenu(self, self.platform_var, '豆包', 'deepseek', 'kimi', 'chat GPT')
        self.platform_menu.place(x=120, y=145, width=100)
        tk.Label(self, text="请输入api:").place(x=240, y=150)
        # 读取config.yaml中的默认api
        import yaml
        try:
            with open('config/config.yaml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            default_api = config.get('openai', {}).get('api_key', '')
        except Exception:
            default_api = ''
        self.api_entry = tk.Entry(self, width=30)
        self.api_entry.place(x=320, y=150)
        self.api_entry.insert(0, default_api)
        tk.Button(self, text="保存", command=self.save_api_config).place(x=500, y=145, width=60)

        # 运行按钮
        self.run_btn = tk.Button(self, text="开始处理", command=self.run)
        self.run_btn.place(x=260, y=190, width=100, height=35)

        # 停止处理按钮
        self.stop_flag = False
        self.stop_btn = tk.Button(self, text="停止处理", command=self.stop_processing)
        self.stop_btn.place(x=140, y=190, width=100, height=35)

        # 清除缓存按钮
        self.clear_btn = tk.Button(self, text="清除缓存", command=self.clear_cache)
        self.clear_btn.place(x=380, y=190, width=100, height=35)

        # 日志输出
        self.log_text = scrolledtext.ScrolledText(self, width=70, height=12, state='disabled', font=("Consolas", 10))
        self.log_text.place(x=30, y=240)

    def select_input(self):
        path = filedialog.askopenfilename(filetypes=[("请选择要翻译的MP4文件", "*.mp4"), ("所有文件", "*.*")])
        if path:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, path)

    def select_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("请选择输出目录", "*.mp4"), ("所有文件", "*.*")])
        if path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, path)

    def log(self, msg):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, str(msg) + '\n')
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.update()

    def save_api_config(self):
        import yaml
        platform = self.platform_var.get()
        api_key = self.api_entry.get().strip()
        # 平台对应base_url和model
        base_url_map = {
            '豆包': 'https://ark.cn-beijing.volces.com/api/v3',
            'deepseek': 'https://api.deepseek.com/v1',
            'kimi': 'https://api.moonshot.cn/v1',
            'chat GPT': 'https://api.openai.com/v1',
        }
        model_map = {
            '豆包': 'glm-4',
            'deepseek': 'deepseek-chat',
            'kimi': 'moonshot-v1-8k',
            'chat GPT': 'gpt-3.5-turbo',
        }
        base_url = base_url_map.get(platform, '')
        model = model_map.get(platform, '')
        config_path = 'config/config.yaml'
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            if 'openai' not in config:
                config['openai'] = {}
            config['openai']['api_key'] = api_key
            config['openai']['base_url'] = base_url
            config['openai']['model'] = model
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(config, f, allow_unicode=True)
            self.log(f"已保存API配置: 平台={platform}, base_url={base_url}, model={model}")
        except Exception as e:
            self.log(f"保存API配置失败: {e}")

    def run(self):
        self.stop_flag = False
        input_video = self.input_entry.get().strip()
        output_video = self.output_entry.get().strip()
        ocr_method = self.ocr_var.get()
        if not input_video or not output_video:
            messagebox.showwarning("提示", "请先选择输入和输出视频路径！")
            return
        self.run_btn.config(state='disabled')
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        self.worker_thread = threading.Thread(target=self._run_pipeline, args=(input_video, output_video, ocr_method), daemon=True)
        self.worker_thread.start()

    def stop_processing(self):
        self.stop_flag = True
        self.log("已请求停止处理，稍等当前步骤结束...")

    def _run_pipeline(self, input_video, output_video, ocr_method):
        if not output_video.lower().endswith('.mp4'):
            output_video += '.mp4'
        try:
            import time
            for i in range(1):  # 这里保留原有结构，实际处理流程在run_pipeline
                if self.stop_flag:
                    self.log("处理已被用户中断。")
                    self.run_btn.config(state='normal')
                    return
                run_pipeline(input_video, output_video, ocr_method, log_callback=self.log, stop_flag_getter=lambda: self.stop_flag)
            self.log("\n处理完成！")
        except NotImplementedError as e:
            self.log(f"错误: {e}")
            messagebox.showerror("错误", str(e))
        except Exception as e:
            self.log(f"发生异常: {e}")
            messagebox.showerror("异常", str(e))
        finally:
            self.run_btn.config(state='normal')

    def clear_cache(self):
        try:
            from main import clean_dir
            clean_dir('data/output')
            clean_dir('data/cache/frames')
            clean_dir('data/cache/frames_processed')
            self.log('缓存已清理。')
        except Exception as e:
            self.log(f'清理缓存失败: {e}')

if __name__ == "__main__":
    app = App()
    app.mainloop() 