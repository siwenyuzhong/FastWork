COLOR_CHOICES = {
    "浅蓝": "#56b8eb",
    "橙色": "#f28033",
    "黄色": "#ebc656",
    "青色": "#a2d148",
    "紫色": "#7461c2",
    "蓝色": "#167be0"
}


def return_color(color_str):
    return COLOR_CHOICES.get(color_str.strip())


if __name__ == '__main__':
    print(return_color("橙色"))
