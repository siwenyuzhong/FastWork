$.getJSON(
    "/web/monitor/logs/",
    function (data) {
        // Build the chart
        Highcharts.chart('containerAPIS', {
            chart: {
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                type: 'pie'
            },
            title: {
                text: '访问最频繁的接口 TOP20'
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: false
                    },
                    showInLegend: true
                }
            },
            series: [{
                name: '接口访问量',
                colorByPoint: true,
                data: data.data
            }]
        });
    }
)
