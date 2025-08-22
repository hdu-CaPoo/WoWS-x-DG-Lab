import os
import re

def clean_filename(filename):
    # 匹配中文字符的正则表达式
    chinese_pattern = re.compile('[\u4e00-\u9fa5]')
    
    # 分离文件名和扩展名
    name, ext = os.path.splitext(filename)
    
    # 去除所有中文字符
    cleaned_name = chinese_pattern.sub('', name)
    
    # 去除所有连字符 (-)
    cleaned_name = cleaned_name.replace('-', '')
    
    # 去除所有空格
    cleaned_name = cleaned_name.replace(' ', '')
    
    # 如果清理后名称为空，则使用原始名称（不含中文）
    if not cleaned_name:
        cleaned_name = re.sub(r'[^\w\s-]', '', name)  # 保留字母数字和基本符号
    
    return cleaned_name + ext

def batch_rename_files(directory):
    # 遍历目录中的所有文件
    for filename in os.listdir(directory):
        # 获取文件完整路径
        old_path = os.path.join(directory, filename)
        
        # 如果是文件而不是目录
        if os.path.isfile(old_path):
            # 清理文件名
            new_name = clean_filename(filename)
            
            # 新文件完整路径
            new_path = os.path.join(directory, new_name)
            
            # 如果文件名有变化，则重命名
            if new_name != filename:
                # 处理文件名冲突
                counter = 1
                while os.path.exists(new_path):
                    name, ext = os.path.splitext(new_name)
                    new_name = f"{name}_{counter}{ext}"
                    new_path = os.path.join(directory, new_name)
                    counter += 1
                
                try:
                    os.rename(old_path, new_path)
                    print(f'重命名: "{filename}" -> "{new_name}"')
                except Exception as e:
                    print(f'重命名错误 "{filename}": {e}')

if __name__ == "__main__":
    # 输入要处理的目录路径
    directory = input("请输入包含照片的目录路径: ").strip()
    
    # 检查目录是否存在
    if os.path.isdir(directory):
        print("开始处理文件...")
        batch_rename_files(directory)
        print("批量重命名完成！")
    else:
        print("错误: 指定的目录不存在。")
