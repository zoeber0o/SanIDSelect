import lark_oapi as lark
import json
from lark_oapi.api.im.v1 import *

app_id = "cli_a864be79129f901c"
app_secret = "Nq1PjRJsWcQKQNFmTyVpfbSOL8aEXBfO"
chatID = 'oc_359b218475aea83c9e2caec5989e206a'


def do_p2_im_message_receive_v1(data: lark.im.v1.P2ImMessageReceiveV1) -> None:
    print(f'[ do_p2_im_message_receive_v1 access ], data: {lark.JSON.marshal(data, indent=4)}')



def do_message_event(data: lark.CustomizedEvent) -> None:
    # 创建client
    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(app_secret) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    request: ListMessageRequest = ListMessageRequest.builder() \
        .container_id_type("chat") \
        .container_id(chatID) \
        .sort_type("ByCreateTimeAsc") \
        .page_size(20) \
        .build()

    # 发起请求
    response: ListMessageResponse = client.im.v1.message.list(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.im.v1.message.list failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return
    # 处理业务结果
    bot_msgs = [m for m in response.data.items if m.sender.sender_type == "app"]
    if bot_msgs:
        latest = max(bot_msgs, key=lambda m: int(m.create_time))
        text = json.loads(latest.body.content).get("text")
        print("机器人最新消息:", text)
        return text



event_handler = lark.EventDispatcherHandler.builder("", "") \
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
    .register_p1_customized_event("im.message.message_read_v1", do_message_event) \
    .build()
def main():
    cli = lark.ws.Client("cli_a864be79129f901c", "Nq1PjRJsWcQKQNFmTyVpfbSOL8aEXBfO",
                         event_handler=event_handler,
                         log_level=lark.LogLevel.DEBUG)
    cli.start()


if __name__ == "__main__":
    do_message_event()