import requests
from configFiles import config_files

access_token = config_files.get_key_value("DINGDING", "access_token")
atMobiles = config_files.get_key_value("DINGDING", "atMobiles")


def post_dingding_message(message):
    webhook_url = "https://oapi.dingtalk.com/robot/send?access_token" \
                  "={}".format(access_token)
    data = {
        "msgtype": "text",
        "text": {
            "content": message
        },
        "at": {
            # 被@人的手机号
            "atMobiles": [].append(atMobiles),
            # 控制@所有人
            # "isAtAll": True
        }
    }
    r = requests.post(url=webhook_url, json=data)
    print(r.json())


if __name__ == '__main__':
    post_dingding_message("hello test")
