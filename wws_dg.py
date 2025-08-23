import asyncio
import threading
import io
from ipaddress import ip_address
from pickle import GLOBAL
import cv2
import numpy as np
import pyautogui
import time
import os
import socket
from datetime import datetime
from ultralytics import YOLO
import qrcode
from pydglab_ws import StrengthData, FeedbackButton, Channel, StrengthOperationType, RetCode, DGLabWSServer

import strength_show

PULSE_DATA = {
    '呼吸': [
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 5, 10, 20)),
        ((10, 10, 10, 10), (20, 25, 30, 40)), ((10, 10, 10, 10), (40, 45, 50, 60)),
        ((10, 10, 10, 10), (60, 65, 70, 80)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((0, 0, 0, 0), (0, 0, 0, 0)), ((0, 0, 0, 0), (0, 0, 0, 0)), ((0, 0, 0, 0), (0, 0, 0, 0))
    ],
    '潮汐': [
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 4, 8, 17)),
        ((10, 10, 10, 10), (17, 21, 25, 33)), ((10, 10, 10, 10), (50, 50, 50, 50)),
        ((10, 10, 10, 10), (50, 54, 58, 67)), ((10, 10, 10, 10), (67, 71, 75, 83)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 98, 96, 92)),
        ((10, 10, 10, 10), (92, 90, 88, 84)), ((10, 10, 10, 10), (84, 82, 80, 76)),
        ((10, 10, 10, 10), (68, 68, 68, 68))
    ],
    '连击': [
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 92, 84, 67)),
        ((10, 10, 10, 10), (67, 58, 50, 33)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (0, 0, 0, 1)), ((10, 10, 10, 10), (2, 2, 2, 2))
    ],
    '快速按捏': [
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((0, 0, 0, 0), (0, 0, 0, 0))
    ],
    '按捏渐强': [
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (29, 29, 29, 29)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (52, 52, 52, 52)),
        ((10, 10, 10, 10), (2, 2, 2, 2)), ((10, 10, 10, 10), (73, 73, 73, 73)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (87, 87, 87, 87)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (0, 0, 0, 0))
    ],
    '心跳节奏': [
        ((110, 110, 110, 110), (100, 100, 100, 100)), ((110, 110, 110, 110), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (75, 75, 75, 75)),
        ((10, 10, 10, 10), (75, 77, 79, 83)), ((10, 10, 10, 10), (83, 85, 88, 92)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 0, 0, 0))
    ],
    '压缩': [
        ((25, 25, 24, 24), (100, 100, 100, 100)), ((24, 23, 23, 23), (100, 100, 100, 100)),
        ((22, 22, 22, 21), (100, 100, 100, 100)), ((21, 21, 20, 20), (100, 100, 100, 100)),
        ((20, 19, 19, 19), (100, 100, 100, 100)), ((18, 18, 18, 17), (100, 100, 100, 100)),
        ((17, 16, 16, 16), (100, 100, 100, 100)), ((15, 15, 15, 14), (100, 100, 100, 100)),
        ((14, 14, 13, 13), (100, 100, 100, 100)), ((13, 12, 12, 12), (100, 100, 100, 100)),
        ((11, 11, 11, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (100, 100, 100, 100))
    ],
    '节奏步伐': [
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 5, 10, 20)),
        ((10, 10, 10, 10), (20, 25, 30, 40)), ((10, 10, 10, 10), (40, 45, 50, 60)),
        ((10, 10, 10, 10), (60, 65, 70, 80)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 6, 12, 25)),
        ((10, 10, 10, 10), (25, 31, 38, 50)), ((10, 10, 10, 10), (50, 56, 62, 75)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (0, 8, 16, 33)), ((10, 10, 10, 10), (33, 42, 50, 67)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (0, 12, 25, 50)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (100, 100, 100, 100))
    ],
    '颗粒摩擦': [
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (0, 0, 0, 0))
    ],
    '渐变弹跳': [
        ((10, 10, 10, 10), (1, 1, 1, 1)), ((10, 10, 10, 10), (1, 9, 18, 34)),
        ((10, 10, 10, 10), (34, 42, 50, 67)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((0, 0, 0, 0), (0, 0, 0, 0)), ((0, 0, 0, 0), (0, 0, 0, 0))
    ],
    '波浪涟漪': [
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 12, 25, 50)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (73, 73, 73, 73))
    ],
    '雨水冲刷': [
        ((10, 10, 10, 10), (34, 34, 34, 34)), ((10, 10, 10, 10), (34, 42, 50, 67)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((0, 0, 0, 0), (0, 0, 0, 0)),
        ((0, 0, 0, 0), (0, 0, 0, 0))
    ],
    '变速敲击': [
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((110, 110, 110, 110), (100, 100, 100, 100)),
        ((110, 110, 110, 110), (100, 100, 100, 100)), ((110, 110, 110, 110), (100, 100, 100, 100)),
        ((110, 110, 110, 110), (100, 100, 100, 100)), ((0, 0, 0, 0), (0, 0, 0, 0))
    ],
    '信号灯': [
        ((197, 197, 197, 197), (100, 100, 100, 100)), ((197, 197, 197, 197), (100, 100, 100, 100)),
        ((197, 197, 197, 197), (100, 100, 100, 100)), ((197, 197, 197, 197), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 8, 16, 33)),
        ((10, 10, 10, 10), (33, 42, 50, 67)), ((10, 10, 10, 10), (100, 100, 100, 100))
    ],
    '挑逗1': [
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 6, 12, 25)),
        ((10, 10, 10, 10), (25, 31, 38, 50)), ((10, 10, 10, 10), (50, 56, 62, 75)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (100, 100, 100, 100))
    ],
    '挑逗2': [
        ((10, 10, 10, 10), (1, 1, 1, 1)), ((10, 10, 10, 10), (1, 4, 6, 12)),
        ((10, 10, 10, 10), (12, 15, 18, 23)), ((10, 10, 10, 10), (23, 26, 28, 34)),
        ((10, 10, 10, 10), (34, 37, 40, 45)), ((10, 10, 10, 10), (45, 48, 50, 56)),
        ((10, 10, 10, 10), (56, 59, 62, 67)), ((10, 10, 10, 10), (67, 70, 72, 78)),
        ((10, 10, 10, 10), (78, 81, 84, 89)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((0, 0, 0, 0), (0, 0, 0, 0))
    ]
}

#buff_number/strength setup
fire_num = 0
leak_num = 0
engine_dam = 0
barbette_dam = 0
trop_dam = 0
fire_strength=30
leak_strength=40
engine_strength=20
barbette_strength=20

A_total_strength=0
B_total_strength=0

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def print_qrcode(data: str):
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1
    )
    qr.add_data(data)
    f = io.StringIO()
    qr.print_ascii(out=f, invert=True)
    f.seek(0)
    print(f.read())
    qr.make(fit=True)
    img = qr.make_image()
    img.save("DG.png")
    print("二维码已生成并保存为 DG.png")

def strength_set():
    global fire_strength, leak_strength, engine_strength, barbette_strength
    print("是否要更改默认强度？，请输入Y/N")
    strength_change = input()
    if strength_change.lower() == 'y':
        print("请输入火灾强度（默认30）:")
        fire_strength = int(input())
        print("请输入漏水强度（默认40）:")
        leak_strength = int(input())
        print("请输入引擎损坏强度（默认20）:")
        engine_strength = int(input())
        print("请输入炮塔损坏强度（默认20）:")
        barbette_strength = int(input())
    else:
        print("使用默认值")


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
        """捕获屏幕指定区域截图"""
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
        
        return screenshot
    
    def predict_and_return_results(self, screenshot):
        """使用YOLO模型进行预测并返回结果"""
        # 进行预测（直接使用图像数据，不保存文件）
        results = self.model(screenshot, verbose=False)
        
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


async def main():
    # 初始化YOLO检测器
    screen_size = pyautogui.size()
    print(f"屏幕尺寸: {screen_size.width} x {screen_size.height}")
    
    # 设置截图区域 (根据实际情况调整)
    region = (1060, 1395, 770, 121)
    print(f"选择的区域: {region}")
    
    capture_app = ScreenCaptureYOLO(region=region)
    ip_address = get_local_ip()
    
    strength_set()

    # 初始化DG-Lab连接
    async with DGLabWSServer(ip_address, 5678, 60) as server:
        client = server.new_local_client()

        url = client.get_qrcode(f"ws://{ip_address}:5678")
        print("请用 DG-Lab App 扫描二维码以连接，且确保本机与扫码设备处于同一局域网下")
        print_qrcode(url)

        # 等待绑定
        await client.bind()
        print(f"已与 App {client.target_id} 成功绑定")

        # 从 App 接收数据更新，并进行远控操作
        last_strength = None
        
        # 创建异步任务来处理YOLO检测
        async def yolo_detection_task():
            global A_total_strength
            global B_total_strength
            #global fire_num
            global leak_num
            while True:
                start_time = time.time()
                
                # 截图
                screenshot = capture_app.capture_screenshot()
                
                # 识别
                results = capture_app.predict_and_return_results(screenshot)
                
                # 打印结果
                if results:
                    print(f"检测到 {len(results)} 个对象:")

                    for result in results:
                        print(f"  对象: {result['class']} (置信度: {result['confidence']:.2f})")
                
                        if "fire" in result["class"]:
                            fire_num = int(result['class'][0])
                            print(f"    检测到 {fire_num} 把火")

                        elif "leak" in result["class"]:
                            leak_num = int(result['class'][0])
                            print(f"    检测到 {leak_num} 个漏水")
                
                        elif "engine" in result["class"]:
                            engine_num = int(result['class'][0])
                            print(f"    检测到 {engine_num} 个引擎损坏")
                
                        elif "barbette" in result["class"]:
                            barbette_num = int(result['class'][0])
                            print(f"    检测到 {barbette_num} 个炮塔损坏")
                    A_total_strength = fire_num * fire_strength + leak_num * leak_strength
                    print(f"  设置A通道总强度为: {A_total_strength}")

                    pulse_data_iterator = iter(PULSE_DATA.values())
                    pulse_data_current = next(pulse_data_iterator, None)    # 当前准备发送的波形
                    if not pulse_data_current:
                        pulse_data_iterator = iter(PULSE_DATA.values())
                    await client.add_pulses(Channel.A, *(pulse_data_current * 5))

                    await client.set_strength(
                        Channel.A,
                        StrengthOperationType.SET_TO,
                        A_total_strength
                    )

                else:
                    print("未检测到任何对象")
                    A_total_strength = 0
                    await client.set_strength(
                                Channel.A,
                                StrengthOperationType.SET_TO,
                                A_total_strength
                    )
                
                # 确保每秒执行一次
                processing_time = time.time() - start_time
                wait_time = max(0, 1.0 - processing_time)
                await asyncio.sleep(wait_time)
        
        # 创建任务
        yolo_task = asyncio.create_task(yolo_detection_task())
        
        try:
            # 同时处理DG-Lab的数据更新
            async for data in client.data_generator():
                # 接收通道强度数据
                if isinstance(data, StrengthData):
                    print(f"从 App 收到通道强度数据更新：{data}")
                    last_strength = data

                    """
                # 接收 App 反馈按钮
                elif isinstance(data, FeedbackButton):
                    print(f"App 触发了反馈按钮：{data.name}")

                    if data == FeedbackButton.A1:
                        # 设置强度到 A 通道上限
                        print("对方按下了 A 通道圆圈按钮，加大力度")
                        if last_strength:
                            await client.set_strength(
                                Channel.A,
                                StrengthOperationType.SET_TO,
                                last_strength.a_limit
                            )
                    """
                # 接收 心跳 / App 断开通知
                elif data == RetCode.CLIENT_DISCONNECTED:
                    print("App 已断开连接，你可以尝试重新扫码进行连接绑定")
                    await client.rebind()
                    print("重新绑定成功")
        
        except asyncio.CancelledError:
            # 取消YOLO任务
            yolo_task.cancel()
            try:
                await yolo_task
            except asyncio.CancelledError:
                pass
            raise
        finally:
            # 确保任务被取消
            if not yolo_task.done():
                yolo_task.cancel()
                try:
                    await yolo_task
                except asyncio.CancelledError:
                    pass


if __name__ == "__main__":
    overlay = strength_show.start_dynamic_overlay(
        lambda: A_total_strength,
        lambda: B_total_strength
    )
    asyncio.run(main())