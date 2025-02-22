$.getJSON(
    "/web/monitor/ips/",
    function (data) {
        // Build the chart
        Highcharts.chart('containerIPS', {
            chart: {
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                type: 'pie'
            },
            title: {
                text: '访问最频繁的IP TOP20'
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
                name: '访问量',
                colorByPoint: true,
                data: data.data
            }]
        });
    }
)
