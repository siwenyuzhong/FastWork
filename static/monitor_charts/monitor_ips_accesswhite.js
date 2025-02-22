function getWhiteLists() {
    $.ajax({
        url: "/web/monitor/ips/accesswhite/",
        type: "GET",
        dataType: 'json',
        success: function (data) {
            if (data.status === 200) {
                document.getElementById("log_content").innerText = data.data
            } else {
                $("#edit_err").show().html(data.msg)
            }
        }
    })
}
