import cv2
import numpy as np
import pyautogui
import time
import os
from datetime import datetime
from ultralytics import YOLO

class ScreenCaptureYOLO:
    def __init__(self, model_path="best.pt", region=None):
        """
        初始化截图和YOLO模型
        
        Args:
            model_path: YOLO模型路径
            region: 截图区域 (x, y, width, height)，如果为None则截取全屏
        """
        self.model = YOLO(model_path)
        self.counter = 1
        self.screenshot_dir = os.path.dirname(os.path.abspath(__file__))
        self.region = region  # 截图区域 (x, y, width, height)
        
        # 确保截图目录存在
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
    
    def capture_screenshot(self):
        """捕获屏幕指定区域截图并保存为png文件"""
        # 生成文件名
        filename = f"img{self.counter:05d}.png"
        filepath = os.path.join(self.screenshot_dir, filename)
        
        # 捕获截图
        if self.region:
            # 截取指定区域
            x, y, width, height = self.region
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
        else:
            # 截取全屏
            screenshot = pyautogui.screenshot()
        
        # 转换为OpenCV格式
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # 保存截图
        cv2.imwrite(filepath, screenshot)
        print(f"截图已保存: {filename}")
        
        self.counter += 1
        return filepath, screenshot
    
    def predict_and_return_results(self, image_path):
        """使用YOLO模型进行预测并返回结果"""
        # 进行预测
        results = self.model.predict(source=image_path, save=True, show=True)
        
        # 提取并返回检测结果
        detection_results = []
        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    bbox = box.xyxy[0].tolist()
                    
                    detection_results.append({
                        "class": self.model.names[class_id],
                        "confidence": confidence,
                        "bbox": bbox
                    })
        
        return detection_results
    
    def run(self, interval=1.0):
        """主循环，每隔指定时间截图并识别"""
        try:
            print("开始屏幕截图和对象识别 (按Ctrl+C停止)...")
            if self.region:
                x, y, w, h = self.region
                print(f"截图区域: 左上角({x}, {y}), 宽度:{w}, 高度:{h}")
            else:
                print("截图区域: 全屏")
                
            while True:
                start_time = time.time()
                
                # 截图
                image_path, screenshot = self.capture_screenshot()
                
                # 识别
                results = self.predict_and_return_results(image_path)
                
                # 打印结果
                if results:
                    print(f"检测到 {len(results)} 个对象:")
                    for i, result in enumerate(results, 1):
                        print(f"  对象 {i}: {result['class']} (置信度: {result['confidence']:.2f})")
                else:
                    print("未检测到任何对象")
                
                # 计算并等待剩余时间
                processing_time = time.time() - start_time
                wait_time = max(0, interval - processing_time)
                time.sleep(wait_time)
                
        except KeyboardInterrupt:
            print("\n程序已停止")

# 辅助函数：获取屏幕尺寸和选择区域
def get_screen_info():
    """获取屏幕尺寸信息"""
    screen_size = pyautogui.size()
    print(f"屏幕尺寸: {screen_size.width} x {screen_size.height}")
    return screen_size

if __name__ == "__main__":
    # 获取屏幕信息
    screen = get_screen_info()
    region=(1060, 1395, 770, 121)
    print(f"选择的区域: {region}")
    # 创建实例并运行
    capture_app = ScreenCaptureYOLO(region=region)
    capture_app.run(interval=1.0)  # 每秒执行一次
