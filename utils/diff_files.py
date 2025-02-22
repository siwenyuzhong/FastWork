import difflib
import sys


def readfile(filename):
    try:
        fileHandle = open(filename, 'r')
        text = fileHandle.read().splitlines()
        fileHandle.close()
        return text

    except IOError as ie:
        print("Read file Error: " + str(ie))
        sys.exit()


def diff_files(html_file, file_left, file_right):
    text1_lines = readfile(file_left)
    text2_lines = readfile(file_right)

    d = difflib.HtmlDiff()
    results = d.make_file(text1_lines, text2_lines)
    with open(html_file, "w+") as file:
        file.write("<title>FastWork - 文件差异性报告</title>\n{}".format(results))


if __name__ == '__main__':
    diff_files("", "./1.json", "./2.json")
