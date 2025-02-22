import datetime


# 返回告警模板
def return_alarm_template(data_msg):
    message = "告警名称：{alarm_name}\n告警信息：{alarm_message}\n任务ID：{task_id}\n命令执行码：{cmd_code}\n告警时间：{alarm_time}\n是否告警：{is_alarm}\n".format(
        alarm_name="DingDing_{}_{}_is_alarm".format(data_msg.get("task_id"),
                                                    data_msg.get("cmd_code")),
        alarm_message=data_msg.get("cmd_stdout"),
        task_id=data_msg.get("task_id"),
        cmd_code=data_msg.get("cmd_code"),
        alarm_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        is_alarm="是" if data_msg.get("is_alarm") else "否",
    )
    return message


def return_alarm_template_v2(task_id, cmd_code, cmd_stdout, is_alarm):
    message = "告警名称：{alarm_name}\n告警信息：{alarm_message}\n任务ID：{task_id}\n命令执行码：{cmd_code}\n告警时间：{alarm_time}\n是否告警：{is_alarm}\n".format(
        alarm_name="DingDing_{}_{}_is_alarm".format(task_id, cmd_code),
        alarm_message=cmd_stdout,
        task_id=task_id,
        cmd_code=cmd_code,
        alarm_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        is_alarm=is_alarm,
    )
    return message
