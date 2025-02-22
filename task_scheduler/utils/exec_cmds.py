from task_scheduler import models
from .exec_shell import exec_shell
import time
import json
from .post_dingding import post_dingding_message
from .alarm_template import return_alarm_template_v2
import logging

logger = logging.getLogger("django")


# 处理结果
def handle_results(code, result):
    data_msg = {}
    results = []
    for line in result.split("\n"):
        try:
            if json.loads(line):
                if json.loads(line).get("alarm_condition") is not None:
                    data_msg['alarm_condition'] = json.loads(line).get("alarm_condition")
        except:
            if line:
                results.append(line)
    data_msg['stdout'] = "\n".join(results)
    data_msg['code'] = code
    return data_msg


# 执行CMD命令
def exec_cmd(cmd, task_id, project_id):
    message = ""
    recode, stdout = exec_shell(cmd)
    if recode == 127:
        message = stdout
    else:
        data_msg = handle_results(recode, stdout)
        message = data_msg.get("stdout")

    try:
        new_log = models.TaskLog.objects.create(
            task_id=task_id,
            status=recode,
            exe_time=time.strftime("%Y-%m-%d %H:%M:%S"),
            cmd=cmd,
            stdout=message,
            project_id=project_id,
        )

        if new_log:
            logger.info("{}：models.TaskLog写入成功".format(task_id))
        else:
            logger.error("{}：models.TaskLog写入失败".format(task_id))

        # 执行告警的逻辑位置
        alarm_obj = models.AlarmConditions.objects.filter(
            task_id=task_id,
            project_id=project_id
        ).first()

        if all([alarm_obj.alarm_threshold, alarm_obj.alarm_way,
                alarm_obj.operate_condition]) and alarm_obj.alarm_way != "无告警方式" and alarm_obj.operate_condition != "判断条件":
            if alarm_obj.alarm_way == "钉钉群告警":
                # 走钉钉群告警逻辑
                if alarm_obj.operate_condition == "等于":
                    # 判断阈值是数字的情况
                    if alarm_obj.alarm_threshold.isdigit():
                        nums = int(alarm_obj.alarm_threshold)
                        # 工具执行之后返回的判断结果
                        state = data_msg.get("alarm_condition") == nums
                        if state:
                            message = return_alarm_template_v2(
                                task_id=task_id,
                                cmd_code=recode,
                                cmd_stdout=data_msg.get("stdout"),
                                is_alarm="是"
                            )
                            # 发送钉钉告警
                            post_dingding_message(message=message)

                    # 判断阈值是布尔类型的情况
                    elif alarm_obj.alarm_threshold in ["True", "true", "False", "false"]:
                        transfer = alarm_obj.alarm_threshold.capitalize()
                        transfer_bool = bool(transfer)
                        # 工具执行之后返回的判断结果
                        state = data_msg.get("alarm_condition") == transfer_bool
                        if state:
                            message = return_alarm_template_v2(
                                task_id=task_id,
                                cmd_code=recode,
                                cmd_stdout=data_msg.get("stdout"),
                                is_alarm="是"
                            )
                            # 发送钉钉告警
                            post_dingding_message(message=message)

                    # 判断阈值是字符串的情况
                    else:
                        # 工具执行之后返回的判断结果
                        state = data_msg.get("alarm_condition") == alarm_obj.alarm_threshold
                        if state:
                            message = return_alarm_template_v2(
                                task_id=task_id,
                                cmd_code=recode,
                                cmd_stdout=data_msg.get("stdout"),
                                is_alarm="是"
                            )
                            # 发送钉钉告警
                            post_dingding_message(message=message)

                elif alarm_obj.operate_condition == "大于或等于":
                    # 判断阈值是数字的情况
                    if alarm_obj.alarm_threshold.isdigit():
                        nums = int(alarm_obj.alarm_threshold)
                        # 工具执行之后返回的判断结果
                        state = data_msg.get("alarm_condition") >= nums
                        if state:
                            message = return_alarm_template_v2(
                                task_id=task_id,
                                cmd_code=recode,
                                cmd_stdout=data_msg.get("stdout"),
                                is_alarm="是"
                            )
                            # 发送钉钉告警
                            post_dingding_message(message=message)

                elif alarm_obj.operate_condition == "小于或等于":
                    # 判断阈值是数字的情况
                    if alarm_obj.alarm_threshold.isdigit():
                        nums = int(alarm_obj.alarm_threshold)
                        # 工具执行之后返回的判断结果
                        state = data_msg.get("alarm_condition") <= nums
                        if state:
                            message = return_alarm_template_v2(
                                task_id=task_id,
                                cmd_code=recode,
                                cmd_stdout=data_msg.get("stdout"),
                                is_alarm="是"
                            )
                            # 发送钉钉告警
                            post_dingding_message(message=message)

                elif alarm_obj.operate_condition == "不等于":
                    # 判断阈值是数字的情况
                    if alarm_obj.alarm_threshold.isdigit():
                        nums = int(alarm_obj.alarm_threshold)
                        # 工具执行之后返回的判断结果
                        state = data_msg.get("alarm_condition") != nums
                        if state:
                            message = return_alarm_template_v2(
                                task_id=task_id,
                                cmd_code=recode,
                                cmd_stdout=data_msg.get("stdout"),
                                is_alarm="是"
                            )
                            # 发送钉钉告警
                            post_dingding_message(message=message)

                    # 判断阈值是布尔类型的情况
                    elif alarm_obj.alarm_threshold in ["True", "true", "False", "false"]:
                        transfer = alarm_obj.alarm_threshold.capitalize()
                        transfer_bool = bool(transfer)
                        # 工具执行之后返回的判断结果
                        state = data_msg.get("alarm_condition") != transfer_bool
                        if state:
                            message = return_alarm_template_v2(
                                task_id=task_id,
                                cmd_code=recode,
                                cmd_stdout=data_msg.get("stdout"),
                                is_alarm="是"
                            )
                            # 发送钉钉告警
                            post_dingding_message(message=message)

                    # 判断阈值是字符串的情况
                    else:
                        # 工具执行之后返回的判断结果
                        state = data_msg.get("alarm_condition") != alarm_obj.alarm_threshold
                        if state:
                            message = return_alarm_template_v2(
                                task_id=task_id,
                                cmd_code=recode,
                                cmd_stdout=data_msg.get("stdout"),
                                is_alarm="是"
                            )
                            # 发送钉钉告警
                            post_dingding_message(message=message)

    except Exception as e:
        logger.error("models.TaskLog写入异常失败 - %s" % e)

    if recode != 0:
        # print('[Error] (%s---[%s]) failed' % (cmd, task_id))
        logger.error('[Error] (%s---[%s]) failed' % (cmd, task_id))
        exit(407)
    logger.info('[Success] (%s---[%s]) success' % (cmd, task_id))
    return stdout
