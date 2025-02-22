from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_job
from task_scheduler.utils.exec_cmds import exec_cmd

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), 'default')


# cron任务
def create_cron_tasks(cmd, task_id, cron_date, project_id):
    try:
        cron = cron_date.split(' ')
        cron_rel = dict(second=cron[0], minute=cron[1], hour=cron[2], day=cron[3], month=cron[4],
                        day_of_week=cron[5])
        scheduler.add_job(func=exec_cmd, id=task_id,
                          kwargs={'cmd': cmd, 'task_id': task_id, 'project_id': project_id}, trigger='cron',
                          **cron_rel, replace_existing=True)

        return "success"
    except:
        return "cron任务参数配置错误"


# date任务
def create_date_tasks(cmd, task_id, run_date, project_id):
    try:
        scheduler.add_job(id=task_id, func=exec_cmd, trigger='date',
                          kwargs={'cmd': cmd, 'task_id': task_id, 'project_id': project_id},
                          run_date=run_date, replace_existing=True)
        return "success"
    except:
        return "date任务参数配置错误"


# interval任务
def create_interval_tasks(cmd, task_id, interval_date, project_id):
    start_date = None
    end_date = None
    try:
        interval_time = interval_date.split(" ")
        scheduler.add_job(func=exec_cmd, id=task_id,
                          kwargs={'cmd': cmd, 'task_id': task_id, 'project_id': project_id},
                          trigger='interval',
                          seconds=int(interval_time[0]), minutes=int(interval_time[1]),
                          hours=int(interval_time[2]),
                          days=int(interval_time[3]),
                          weeks=int(interval_time[4]),
                          start_date=start_date, end_date=end_date, replace_existing=True)

        return "success"
    except:
        return "interval任务参数配置错误"


# 暂停任务
def pause(task_id):
    scheduler.pause_job(task_id)


# 恢复任务
def resume(task_id):
    scheduler.resume_job(task_id)


# 删除任务
def remove_job(task_id):
    scheduler.remove_job(task_id)


register_job(scheduler)
scheduler.start()
