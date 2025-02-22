import os, zipfile, tarfile


# 打包目录为zip文件（未压缩）
def make_zip(source_dir, output_filename):
    zipf = zipfile.ZipFile(output_filename, 'w')
    pre_len = len(os.path.dirname(source_dir))
    for parent, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)  # 相对路径
            zipf.write(pathfile, arcname)
    zipf.close()


# 一次性打包整个根目录。空子目录会被打包。
# 如果只打包不压缩，将"w:gz"参数改为"w:"或"w"即可。
def make_targz(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


# 逐个添加文件打包，未打包空子目录。可过滤文件。
# 如果只打包不压缩，将"w:gz"参数改为"w:"或"w"即可。
def make_targz_one_by_one(output_filename, source_dir):
    tar = tarfile.open(output_filename, "w:gz")
    for root, dir, files in os.walk(source_dir):
        for file in files:
            pathfile = os.path.join(root, file)
            tar.add(pathfile)
    tar.close()


if __name__ == '__main__':
    # make_zip("/Users/apple/Downloads/脚本仓库/DocumentsWikis/download/23werexssdd1qwe13qsdc",
    #          "/Users/apple/Downloads/脚本仓库/DocumentsWikis/download/output/1.zip")
    # make_targz("/Users/apple/Downloads/脚本仓库/DocumentsWikis/download/output/1.tar.gz",
    #            "/Users/apple/Downloads/脚本仓库/DocumentsWikis/download/23werexssdd1qwe13qsdc")
    print(",,193".split(","))
