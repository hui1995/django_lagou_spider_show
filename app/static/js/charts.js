/**
 * Created by SoulPainterC on 2018/5/20.
 */

$("#sub").click(function () {
//        $.ajax({
//        type: "post",
//        dataType: 'json',
//        async: false,
//        url: "/statistics",//此处填写你的url
//        success: function (data) {//这个data就是返回来的json数据
//            console.log(data)           //s就是Error
//            update_chart(data)
//        }
//    });
    var serach = document.getElementById("search").value;
    $.post('/statistics', {"search": serach}).done(update_citychart2, update_educationchart2, update_salarychart2);
});


function check() {
    var serach = document.getElementById("search").value;
    if (serach == "") {
        alert("查询内容不能为空");
        return false;
    }
    //document.getElementById("form1").submit();

}

function collect() {
    $.post('/collect', {"skillname": skillname}).done(result);
}

var result = function (data) {
    alert(data);
}

function validate_required(field, alerttxt) {
    with (field) {
        if (value == null || value == "") {
            alert(alerttxt);
            return false
        }
        else {
            return true
        }
    }
}

function validate_form(thisform) {
    with (thisform) {
        if (validate_required(search, "请输入查询内容") == false) {
            search.focus();
            return false
        }
    }
}


var cityChart = echarts.init(document.getElementById('citychart'));
var salaryChart = echarts.init(document.getElementById('salarychart'));
var educationChart = echarts.init(document.getElementById('educationchart'));

var myDate = new Date();
var skillname;
option = {
    title: {
        //text: '岗位总体城市分布饼图',
        subtext: '数据来源于lagou.com\n' + myDate.toLocaleDateString(),     //获取当前日期
        x: 'left'
    },
    tooltip: {
        trigger: 'item',
        formatter: "{a} <br/>{b} : {c} ({d}%)"
    },
    legend: {
        orient: 'vertical',
        left: 'left',
        data: []
    },
    series: [
        {
            name: '岗位数',
            type: 'pie',
            radius: '55%',
            center: ['50%', '60%'],
            data: [],
            itemStyle: {
                emphasis: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            }
        }
    ]
};

cityChart.setOption(option);
salaryChart.setOption(option);
educationChart.setOption(option);

var update_citychart1 = function (data) {
    skillname = data.skillname
    cityChart.hideLoading();
    cityChart.setOption({
        title: {
            text: '岗位总体城市分布饼图'
        },
        series: [{
            data: getseries_by_city(data)
        }
        ]
    });

};
var update_citychart2 = function (data) {
    skillname = data.skillname
    cityChart.hideLoading();
    cityChart.setOption({
        title: {
            text: data.skillname + '岗位城市分布饼图'
        },
        series: [{
            data: getseries_by_city(data)
        }
        ]
    });

};
function getseries_by_city(data) {
    var serie = []
    for (var i = 0; i < data.citynum.length; i++) {
        var item = {
            name: data.city[i],
            value: data.citynum[i],

        }
        serie.push(item)
    }
    console.log(serie)
    return serie
}

var update_salarychart1 = function (data) {
    salaryChart.hideLoading();
    salaryChart.setOption({
        title: {
            text: '岗位总体薪资分布饼图'
        },
        series: [{
            data: getseries_by_salary(data)
        }
        ]
    });

};
var update_salarychart2 = function (data) {
    salaryChart.hideLoading();
    salaryChart.setOption({
        title: {
            text: data.skillname + '岗位薪资分布饼图'
        },
        series: [{
            data: getseries_by_salary(data)
        }
        ]
    });

};
function getseries_by_salary(data) {
    var serie = []
    for (var i = 0; i < data.salarynum.length; i++) {
        var item = {
            name: data.salary[i],
            value: data.salarynum[i],

        }
        serie.push(item)
    }
    console.log(serie)
    return serie
}

var update_educationchart1 = function (data) {
    educationChart.hideLoading();
    educationChart.setOption({
        title: {
            text: '岗位总体学历分布饼图'
        },
        series: [{
            data: getseries_by_education(data)
        }
        ]
    });

};
var update_educationchart2 = function (data) {
    educationChart.hideLoading();
    educationChart.setOption({
        title: {
            text: data.skillname + '岗位学历分布饼图'
        },
        series: [{
            data: getseries_by_education(data)
        }
        ]
    });

};
function getseries_by_education(data) {
    var serie = []
    for (var i = 0; i < data.educationnum.length; i++) {
        var item = {
            name: data.education[i],
            value: data.educationnum[i],

        }
        serie.push(item)
    }
    console.log(serie)
    return serie
}

cityChart.showLoading();
salaryChart.showLoading();
educationChart.showLoading();

console.log("000")
// 异步加载数据 （首次，get，显示6个数据）
//$.get('/statistics').done(update_mychart);
console.log("111")
$.get('/alldata').done(update_citychart1, update_educationchart1, update_salarychart1);
console.log('2222')