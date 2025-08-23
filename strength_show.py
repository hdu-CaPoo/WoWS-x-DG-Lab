import tkinter as tk
import time
import threading

class DynamicIntOverlay:
    def __init__(self, variable_getter_a, variable_getter_b):
        self.root = tk.Tk()
        self.root.title("Monitor")
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        self.root.configure(bg='white')
        
        # 存储获取变量的函数
        self.get_variable_a = variable_getter_a
        self.get_variable_b = variable_getter_b
        # 创建标签AB显示变量值
        self.label_a = tk.Label(self.root, text="A: 0", 
                               font=("Arial", 12), fg="black", bg="white")
        self.label_a.pack(padx=10, pady=2)
        
        self.label_b = tk.Label(self.root, text="B: 0", 
                               font=("Arial", 12), fg="black", bg="white")
        self.label_b.pack(padx=10, pady=2)

        screen_width = self.root.winfo_screenwidth()
        self.root.geometry(f"+{screen_width-150}+10")
        
        self.running = True
        
        self.update_display()
    
    def update_display(self):
        if self.running:
            current_value_a = self.get_variable_a()  # 调用函数获取最新值
            current_value_b = self.get_variable_b()
            self.label_a.config(text=f"A: {current_value_a}")
            self.label_b.config(text=f"B: {current_value_b}")
            self.root.after(1000, self.update_display)
    
    def close_window(self):
        self.running = False
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        try:
            self.root.mainloop()
        except:
            self.running = False

def start_dynamic_overlay(variable_getter_a, variable_getter_b):
    def run_dynamic_overlay():
        overlay = DynamicIntOverlay(variable_getter_a, variable_getter_b)
        overlay.run()
    
    thread = threading.Thread(target=run_dynamic_overlay, daemon=True)
    thread.start()
    time.sleep(0.5)
    return thread