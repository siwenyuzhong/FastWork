$.getJSON(
    "/web/monitor/pv/",
    function (data) {
        Highcharts.chart('containerPV', {
            chart: {
                type: 'line'
            },
            title: {
                text: ' PV访问量统计'
            },
            subtitle: {
                text: '数据来源: fastwork.cc'
            },
            xAxis: {
                categories: data.name
            },
            yAxis: {
                title: {
                    text: '访问量（次）'
                }
            },
            plotOptions: {
                line: {
                    dataLabels: {
                        // 开启数据标签
                        enabled: true
                    },
                    // 关闭鼠标跟踪，对应的提示框、点击事件会失效
                    enableMouseTracking: false
                }
            },
            series: [{
                name: 'PV访问量',
                data: data.accNum
            }]
        });
    }
)
