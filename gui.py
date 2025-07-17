import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
from main import run_pipeline

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("视频字幕处理工具")
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

        # 运行按钮
        self.run_btn = tk.Button(self, text="开始处理", command=self.run)
        self.run_btn.place(x=260, y=150, width=100, height=35)

        # 日志输出
        self.log_text = scrolledtext.ScrolledText(self, width=70, height=12, state='disabled', font=("Consolas", 10))
        self.log_text.place(x=30, y=200)

    def select_input(self):
        path = filedialog.askopenfilename(filetypes=[("MP4文件", "*.mp4"), ("所有文件", "*.*")])
        if path:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, path)

    def select_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4文件", "*.mp4"), ("所有文件", "*.*")])
        if path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, path)

    def log(self, msg):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, str(msg) + '\n')
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.update()

    def run(self):
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
        threading.Thread(target=self._run_pipeline, args=(input_video, output_video, ocr_method), daemon=True).start()

    def _run_pipeline(self, input_video, output_video, ocr_method):
        # 自动补全输出文件名后缀
        if not output_video.lower().endswith('.mp4'):
            output_video += '.mp4'
        try:
            run_pipeline(input_video, output_video, ocr_method, log_callback=self.log)
            self.log("\n处理完成！")
        except NotImplementedError as e:
            self.log(f"错误: {e}")
            messagebox.showerror("错误", str(e))
        except Exception as e:
            self.log(f"发生异常: {e}")
            messagebox.showerror("异常", str(e))
        finally:
            self.run_btn.config(state='normal')

if __name__ == "__main__":
    app = App()
    app.mainloop() 