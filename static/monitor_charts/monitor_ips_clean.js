$("#btnIpsClear").click(function () {
        if (window.confirm('确定要清空IP数据吗？')) {
            var pwd;
            pwd = prompt("请输入管理员密码");
            if (parseInt(pwd) === 19940620) {
                $.ajax({
                    url: "/web/monitor/ips/clean/",
                    type: "POST",
                    async: true,
                    data: $("#cleanIPForm").serialize(),
                })
                alert("清空IP数据完成！")
                window.location.href = "/web/monitor/index/"
            } else {
                alert("管理员密码校验错误，本次操作终止！")
                return false;
            }
        }
    }
)
