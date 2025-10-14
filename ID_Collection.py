import base64
from PIL import ImageGrab,ImageFile,Image
from pathlib import Path
from rapidocr_onnxruntime import RapidOCR
import os,time
import json
import io
import ctypes
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.ocr.v20181119 import ocr_client, models
import subprocess
import requests

# 保存目录
webhub = 'https://open.feishu.cn/open-apis/bot/v2/hook/be80b81c-a5ac-47f4-9b3a-4a4ddf1a99c5'

#生成图片转码base64
def image_to_base64(img) -> str:
    """
    将 PIL.Image 对象转为 Base64 字符串
    :param img: PIL.Image 实例（如 ImageGrab.grabclipboard() 返回值）
    :return: base64 字符串（不带 data:image/png;base64, 前缀）
    """
    buf = io.BytesIO()
    img.save(buf, format="PNG")  # 统一保存为 PNG 格式
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return b64


#获取粘贴板图像
def grab_clipboard_image():
    """
    从系统剪贴板读取图片：
    - 若剪贴板包含图片，返回 PIL.Image 对象；
    - 否则返回 None。
    """
    img = ImageGrab.grabclipboard()
    if img is None:
        return None
    if isinstance(img, (Image.Image, ImageFile.ImageFile)):
        print("检测到文件路径，尝试读取第一张图片...")
        try:
            b64_str = image_to_base64(img)
            try:
           # win清理粘贴板
                ctypes.windll.user32.OpenClipboard(0)
                ctypes.windll.user32.EmptyClipboard()
                ctypes.windll.user32.CloseClipboard()
            except Exception as e:
                # mac清理粘贴板
                subprocess.run("pbcopy < /dev/null", shell=True)
            return b64_str
        except Exception as e:
            print(f"无法打开文件：{e}")
            return None


#图像转文本
def image_to_text() -> str:
    """
    识别图片中的文字并返回纯文本
    :param image_path: 图片文件路径（支持 jpg/png 等）
    :return: 识别出的文本
    """
    ocr = RapidOCR()  # 初始化一次即可复用
    TENCENTCLOUD_SECRET_ID = 'AKIDfCWbQ2PZT8XhdJm11mOs9D3f4E8oFRP8'
    TENCENTCLOUD_SECRET_KEY = 'bz82g5FBuPeeOt9ByYv4yd4HH2atwkKh'
    try:
        cred = credential.Credential(TENCENTCLOUD_SECRET_ID,TENCENTCLOUD_SECRET_KEY)
        # cred = credential.Credential("SecretId", "SecretKey", "Token")
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        httpProfile = HttpProfile()
        httpProfile.endpoint = "ocr.tencentcloudapi.com"

        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        # 实例化要请求产品的client对象,clientProfile是可选的
        client = ocr_client.OcrClient(cred, "ap-beijing", clientProfile)

        # 实例化一个请求对象,每个接口都会对应一个request对象
        req = models.GeneralBasicOCRRequest()
        img64 = grab_clipboard_image()

        params = {"ImageBase64": img64
        }
        req.from_json_string(json.dumps(params))
        # 返回的resp是一个GeneralBasicOCRResponse的实例，与请求对象对应
        resp = client.GeneralBasicOCR(req)
        # 输出json格式的字符串回包
        return json.loads(resp.to_json_string())
    except Exception as e:
        print(f'图像识别失败！{resp.to_json_string()}')


#获取自建应用token
def get_tenant_token():
    url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
    headers = {
        'Content-Type': 'application/json; charset=utf-8'
    }
    body = {

            "app_id": "cli_a864be79129f901c",
            "app_secret": "Nq1PjRJsWcQKQNFmTyVpfbSOL8aEXBfO"
    }
    resp = requests.post(url, headers= headers, json= body)
    print(resp.text)
    tenant_access_token = resp.json()['tenant_access_token']
    return tenant_access_token



#机器人发送消息
def BOT_send_msg(ID_text):
    url = 'https://open.feishu.cn/open-apis/im/v1/messages'
    tenant_access_token = get_tenant_token()
    params = {"receive_id_type": "open_id"}
    msg = ID_text
    msgContent = {
        "text": msg,
    }
    req = {
        "receive_id": "ou_784cf11b49253ddc4f3fc319bc688ed2",  # chat id
        "msg_type": "text",
        "content": json.dumps(msgContent)
    }
    payload = json.dumps(req)
    headers = {
        'Authorization': f'Bearer {tenant_access_token}',  # your access token
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, params=params, headers=headers, data=payload)
    print(f'用户ID已成功发送------{ID_text}')

#启动核心代码
def main():
    print("✅ A 设备监听已启动：只要你截图复制到剪贴板，就会自动识别。按 Ctrl+C 退出。")
    last_digest = None

    while True:
        try:
            img_text = image_to_text()
            texts = [item["DetectedText"] for item in img_text["TextDetections"]]
            full_text = "".join(texts)
            BOT_send_msg(full_text)
        except KeyboardInterrupt:
            print("\n👋 已退出监听。")
            break
        except Exception as e:
            # 不让异常中断后台监听
            time.sleep(1.0)

if __name__ == "__main__":
    main()