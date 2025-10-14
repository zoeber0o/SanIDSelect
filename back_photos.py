import json
import lark_oapi as lark
from lark_oapi.api.im.v1 import (
    CreateImageRequest, CreateImageRequestBody,
    CreateMessageRequest, CreateMessageRequestBody
)

APP_ID = "你的AppID"
APP_SECRET = "你的AppSecret"

# 1) OpenAPI 客户端（REST 调用）
client = lark.Client.builder() \
    .app_id(APP_ID) \
    .app_secret(APP_SECRET) \
    .log_level(lark.LogLevel.INFO) \
    .build()

def upload_image_get_key(local_path: str) -> str:
    """上传本地图片，返回 image_key"""
    req = CreateImageRequest.builder().request_body(
        CreateImageRequestBody.builder()
        .image_type("message")                                # 固定："message"
        .image(lark.File.from_path(local_path))               # 本地文件
        .build()
    ).build()

    resp = client.im.v1.image.create(req)
    if not resp.success():
        raise RuntimeError(f"上传图片失败: code={resp.code}, msg={resp.msg}")
    return resp.data.image_key

def send_image_to_chat_id(chat_id: str, image_key: str):
    """发送图片到群聊/单聊（已知 chat_id）"""
    content = {"image_key": image_key}
    req = CreateMessageRequest.builder() \
        .receive_id_type("chat_id") \
        .request_body(CreateMessageRequestBody.builder()
            .receive_id(chat_id)
            .msg_type("image")
            .content(json.dumps(content))
            .build()) \
        .build()

    resp = client.im.v1.message.create(req)
    if not resp.success():
        raise RuntimeError(f"发送失败: code={resp.code}, msg={resp.msg}")
    return resp.data.message_id

def send_image_to_open_id(open_id: str, image_key: str):
    """发送图片到指定用户（open_id 私聊）"""
    content = {"image_key": image_key}
    req = CreateMessageRequest.builder() \
        .receive_id_type("open_id") \
        .request_body(CreateMessageRequestBody.builder()
            .receive_id(open_id)
            .msg_type("image")
            .content(json.dumps(content))
            .build()) \
        .build()

    resp = client.im.v1.message.create(req)
    if not resp.success():
        raise RuntimeError(f"发送失败: code={resp.code}, msg={resp.msg}")
    return resp.data.message_id

if __name__ == "__main__":
    # 本地图片路径
    img_path = "demo.png"

    # A) 如果你手上是 chat_id（群/私聊都行）
    chat_id = "oc_xxxxxxxxxxxxxxxxxxxxxxxxx"
    image_key = upload_image_get_key(img_path)
    msg_id = send_image_to_chat_id(chat_id, image_key)
    print("已发送到 chat_id，message_id:", msg_id)

    # B) 如果你只有对方 open_id（私聊）
    # open_id = "ou_xxxxxxxxxxxxxxxxxxxxxxxx"
    # image_key = upload_image_get_key(img_path)
    # msg_id = send_image_to_open_id(open_id, image_key)
    # print("已发送到 open_id，message_id:", msg_id)