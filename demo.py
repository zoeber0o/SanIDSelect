import json
import lark_oapi as lark
from lark_oapi.api.im.v1 import *

data =  {
    "has_more": False,
    "page_token": "",
    "items": [
        {
            "message_id": "om_x100b41d555b86ce40f31621ab3c53d2",
            "msg_type": "text",
            "create_time": "1760432567562",
            "update_time": "1760432567562",
            "deleted": False,
            "updated": False,
            "chat_id": "oc_359b218475aea83c9e2caec5989e206a",
            "sender": {
                "id": "ou_784cf11b49253ddc4f3fc319bc688ed2",
                "id_type": "open_id",
                "sender_type": "user",
                "tenant_key": "157961274af45758"
            },
            "body": {
                "content": "{\"text\":\"你好\"}"
            }
        },
        {
            "message_id": "om_x100b41d5a29cf8980e370e71017051b",
            "msg_type": "text",
            "create_time": "1760435909235",
            "update_time": "1760435909235",
            "deleted": False,
            "updated": False,
            "chat_id": "oc_359b218475aea83c9e2caec5989e206a",
            "sender": {
                "id": "cli_a864be79129f901c",
                "id_type": "app_id",
                "sender_type": "app",
                "tenant_key": "157961274af45758"
            },
            "body": {
                "content": "{\"text\":\"图像识别失败\"}"
            }
        },
        {
            "message_id": "om_x100b41d5a1b8fc880e3eb312b0ea057",
            "msg_type": "text",
            "create_time": "1760435959507",
            "update_time": "1760435959507",
            "deleted": False,
            "updated": False,
            "chat_id": "oc_359b218475aea83c9e2caec5989e206a",
            "sender": {
                "id": "cli_a864be79129f901c",
                "id_type": "app_id",
                "sender_type": "app",
                "tenant_key": "157961274af45758"
            },
            "body": {
                "content": "{\"text\":\"只要你截图复制到剪贴板\"}"
            }
        },
        {
            "message_id": "om_x100b41d637cd80b00e3f7e003c78a79",
            "msg_type": "text",
            "create_time": "1760438160158",
            "update_time": "1760438160158",
            "deleted": False,
            "updated": False,
            "chat_id": "oc_359b218475aea83c9e2caec5989e206a",
            "sender": {
                "id": "cli_a864be79129f901c",
                "id_type": "app_id",
                "sender_type": "app",
                "tenant_key": "157961274af45758"
            },
            "body": {
                "content": "{\"text\":\"grab_cLipboard_image\"}"
            }
        },
        {
            "message_id": "om_x100b41d6cbe6f4e40e349fae78e3f02",
            "msg_type": "text",
            "create_time": "1760438354851",
            "update_time": "1760438354851",
            "deleted": False,
            "updated": False,
            "chat_id": "oc_359b218475aea83c9e2caec5989e206a",
            "sender": {
                "id": "cli_a864be79129f901c",
                "id_type": "app_id",
                "sender_type": "app",
                "tenant_key": "157961274af45758"
            },
            "body": {
                "content": "{\"text\":\"test content\"}"
            }
        }
    ]
}


def ProcessingMsg(data):
    items = data.get("items", [])
    bot_msgs = [m for m in items if m.get("sender", {}).get("sender_type") == "app"]
    if not bot_msgs:
        return None  # 没有机器人消息
    # create_time 是字符串毫秒时间戳，转 int 比大小
    latest = max(bot_msgs, key=lambda m: int(m.get("create_time", "0")))
    # 文本消息体在 body.content（内层还是 JSON 字符串）
    content = None
    try:
        body = latest.get("body", {})
        raw = body.get("content")
        if raw:
            content = json.loads(raw).get("text")
    except Exception:
        pass
    return {
        "text": content,
    }
if __name__ == '__main__':
    print(ProcessingMsg(data))
