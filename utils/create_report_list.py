import time
import hashlib

SECRET_KEY = '2$hkf6(z#yjk&j%an1h5t04w1fy9%isj@m^6hyet-2pq(@^7cy'


def md5(string):
    """ MD5加密 """
    hash_object = hashlib.md5(SECRET_KEY.encode('utf-8'))
    hash_object.update(string.encode('utf-8'))
    return hash_object.hexdigest()


def create_report(create_directory, project_obj, wiki_count, tools_count, files_count, back_up_user):
    # 打包时间
    back_up_time = time.strftime("%Y-%m-%d %H:%M:%S")

    html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>""" + project_obj.name + """ 打包清单</title>
            <link href="./css/bootstrap.min.css" rel="stylesheet">
            <style>
                .tableW {
                    width: 200px;
                }
            </style>
        </head>
        <body>


        <div class="container clearfix content" style="margin-top: 20px;">
            <div class="col-sm-12">
                <div class="panel panel-default">
                    <div class="panel-heading" style="text-align: center">
                        <strong>""" + project_obj.name + """ - 项目打包清单</strong>
                    </div>
                    <div class="panel-body">

                        <div class="panel panel-default">
                            <div class="panel-heading">
                                <strong>打包情况：</strong>
                            </div>
                            <div class="panel-body">
                                <table class="table table-hover table-bordered">
                                    <tbody>
                                    <tr>
                                        <td>打&nbsp;&nbsp;包&nbsp;&nbsp;人：</td>
                                        <td>""" + back_up_user + """</td>
                                    </tr>
                                    <tr>
                                        <td class="tableW">打包时间：</td>
                                        <td>""" + back_up_time + """</td>
                                    </tr>
                                    </tbody>
                                </table>
                            </div>
                            <div class="panel-heading">
                                <strong>项目情况：</strong>
                            </div>
                            <div class="panel-body">
                                <table class="table table-hover table-bordered">
                                    <tbody>
                                    <tr>
                                        <td class="tableW">项目名称：</td>
                                        <td>""" + project_obj.name + """</td>
                                    </tr>
                                    <tr>
                                        <td>项目描述：</td>
                                        <td>""" + project_obj.desc + """</td>
                                    </tr>
                                    <tr>
                                        <td>创建时间：</td>
                                        <td>""" + str(project_obj.create_datetime).split(".")[0] + """</td>
                                    </tr>
                                    <tr>
                                        <td>创&nbsp;&nbsp;建&nbsp;&nbsp;人：</td>
                                        <td>""" + str(project_obj.creator.username) + """</td>
                                    </tr>
                                    </tbody>
                                </table>
                            </div>
                            <div class="panel-heading">
                                <strong>知识文档统计：</strong>
                            </div>
                            <div class="panel-body">
                                <table class="table table-hover table-bordered">
                                    <tbody>
                                    <tr>
                                        <td class="tableW">知识库数量：</td>
                                        <td>""" + wiki_count + """</td>
                                    </tr>
                                    </tbody>
                                </table>
                            </div>
                            <div class="panel-heading">
                                <strong>工具库统计：</strong>
                            </div>
                            <div class="panel-body">
                                <table class="table table-hover table-bordered">
                                    <tbody>
                                    <tr>
                                        <td class="tableW">工具库数量：</td>
                                        <td>""" + tools_count + """</td>
                                    </tr>
                                    </tbody>
                                </table>
                            </div>
                            <div class="panel-heading">
                                <strong>文件仓库统计：</strong>
                            </div>
                            <div class="panel-body">
                                <table class="table table-hover table-bordered">
                                    <tbody>
                                    <tr>
                                        <td class="tableW">文件仓库数量：</td>
                                        <td>""" + files_count + """</td>
                                    </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        </body>
        </html>
        """
    with open("{}/{}.html".format(create_directory, md5(project_obj.name)), "wb") as file:
        file.write(html.strip().encode())
