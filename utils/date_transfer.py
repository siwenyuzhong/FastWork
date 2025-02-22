from datetime import *
import time


def dateTransfer():
    months = {
        "01": "Jan",
        "02": "Feb",
        "03": "Mar",
        "04": "Apr",
        "05": "May",
        "06": "Jun",
        "07": "Jul",
        "08": "Aug",
        "09": "Sept",
        "10": "Oct",
        "11": "Nov",
        "12": "Dec"
    }

    date_name = str(date.fromtimestamp(time.time()))
    date_split = date_name.split("-")
    after_transfer_date = "{day}/{month}/{year}".format(day=date_split[2], month=months.get(date_split[1]),
                                                        year=date_split[0])
    return after_transfer_date


if __name__ == '__main__':
    print(dateTransfer())
