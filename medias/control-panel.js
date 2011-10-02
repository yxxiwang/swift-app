var origin_size = new Map();

function Map(){
    //map数据结构
    var struct = function(key, value){
        this.key = key;
        this.value = value;
    };

    var put = function(key, value){
        for (var i=0;i<this.attr.length;i++){
            if(this.attr[i].key==key){
                this.attr[i].value = value;
                return ;
            };
        };
        this.attr[this.attr.length] = new struct(key, value);
    };

    var get = function(key){
        for (var i=0;i<this.attr.length;i++){
            if (this.attr[i].key==key) return this.attr[i].value;
        };
        return null;
    };

    var size = function(){return this.attr.length;};

    this.attr = new Array();
    this.put = put;
    this.get = get;
}

function valid_container(c){
    //验证container名字是否合法
    if (escape(c).length>255 ||c.charAt(0)=="/"){
        return false;
    }
}

function change_unit(){
    var unit = $('#select2 option:selected').val();
    var table = $('#table1').get(0);
    var unit_title = table.rows[0].cells[1].innerHTML;
    unit_title = unit_title.replace(/(byte|kb|M|G)/,unit);
    table.rows[0].cells[1].innerHTML = unit_title;
    for (var i=1;i<table.rows.length;i++){
        var obj_name = table.rows[i].cells[0].innerHTML;
        var size  = table.rows[i].cells[1].innerHTML;
        if (unit=='byte'){
            table.rows[i].cells[1].innerHTML = origin_size.get(obj_name);
        }
        else if(unit=='kb'){
            table.rows[i].cells[1].innerHTML = parseInt(origin_size.get(obj_name))/1024;
        }
        else if(unit=='M'){
            table.rows[i].cells[1].innerHTML = parseInt(origin_size.get(obj_name))/(1024*1025);
        }
        else if(unit=='G'){
            table.rows[i].cells[1].innerHTML = parseInt(origin_size.get(obj_name))/(1024*1024*1024);
        }
    }

}

function show_obj_list(){
    //使选中container的object显示在table中
    $('#objects').show();
    $('#table1').hide();
    var value = $("#select1 option:selected").val();
    $('#container_name').val(value);
    $.get('/operation?q=lo&name='+value,function (res){
        rowlength = $('#table1').get(0).rows.length;
        for(var i=1;i<rowlength;i++){
            $('#table1').get(0).deleteRow(i);
            rowlength--;
            i--;
        }
        var items = res.split('\n');
        name_list = items[0].split('^');
        time_origin_list = items[1].split('^');
        size_list = items[2].split('^');
        var time_list = new Array();
        for(var i=0;i<time_origin_list.length;i++){
            time_list[i]=time_origin_list[i].replace(/T/,'  ');
            time = time_list[i].split(' ');
            y_m_d = time[0].split('-');
            h_m_s = time[2].split('.')[0].split(':');
            new_date = new Date();
            new_date.setFullYear(y_m_d[0],y_m_d[1],y_m_d[2]);
            new_date.setHours(parseInt(h_m_s[0]));
            new_date.setMinutes(h_m_s[1]);
            new_date.setSeconds(h_m_s[2]);
            year = new_date.getFullYear().toString();
            month = new_date.getMonth().toString();
            if (month.length==1) month='0'+month;
            date = new_date.getDate().toString();
            if (date.length==1) date='0'+date;
            hour = new_date.getHours().toString();
            if (hour.length==1) hour='0'+hour;
            minute = new_date.getMinutes().toString();
            if (minute.length==1) minute='0'+minute;
            second = new_date.getSeconds().toString();
            if (second.length==1) second='0'+second;
            time_list[i] = year+'年'+month+'月'+date+'日'+hour+'时'+
                minute+'分'+second+'秒';
        }
        for(name in name_list){
            if(name_list[name]=='') break;
            $('#tbody').append(
                    "<tr><td style='overflow:auto' value="+name_list[name]+">"+name_list[name]+
                    "</td>"+
                    "<td>"+size_list[name]+"</td>"+
                    "<td>"+time_list[name]+"</td>"+
                    "<td align=right><input type='checkbox'/></td>"+
                    "</tr>"
                    );
            origin_size.put(name_list[name],size_list[name]);
        }
        $('#table1').fadeIn();
        $('#table1').tablesorter();
        change_unit();
    });
}

$(document).ready(function (){
    var length = $('#select1>option').length;
    var select1 = $('#select1').get(0);
    if (length>=19) select1.size =19;
    else select1.size = length;
    $('#objects').hide();
    $('#uploadForm').hide();
    $('#container_name').hide();
    if ($('#select1').get(0).selectedIndex!=-1){
        var container_name = $('#select1 option:selected').get(0).value;
        show_obj_list();
    }

    $("#delObject").click(function (){
        //删除object
        var table1 = $('#table1').get(0);
        var obj_array = new Array();
        var objs = '';
        var del_objs = new Array();
        var j = 0;
        for(var i=1;i<table1.rows.length;i++){
            if ($('#table1').get(0).rows[i].style.display=='none') continue;
            if ($(':checkbox').get(i-1).checked){
                objs+=table1.rows[i].cells[0].innerHTML;
                objs+='^';
                del_objs[j]=i;
                j++;
            }
        }
        if (del_objs.length>0) {
            var flag = confirm('是否要删除选中');
            if (flag==false) return ;
        }
        objs+=$('#select1 option:selected').val();
        //do=delete_object
        $.get('/operation?q=do&name='+objs, function(res){
            if(res=='failure'){
                alert("删除失败");
            }
            else if(res=='success'){
                for (var i=0;i<del_objs.length;i++){
                    $('#table1').get(0).rows[del_objs[i]].style.display='none';
                }
                var text = $('#select1 option:selected').html();
                var num  = parseInt(text.substring(text.lastIndexOf('(')+1,
                        text.lastIndexOf(')')));
                num-=del_objs.length;
                text = text.replace(/(\(\d+\))/,'('+num+')');
                $('#select1 option:selected').html(text);
            }
        });
    });

    $("#delContainer").click(function (){
        //删除列表中选定的container
        var opt = $('#select1').get(0).options;
        if (opt.selectedIndex==-1){
            alert("请先选中一个container");
            return;
        }
        if ($('#table1').get(0).rows.length>1){
            alert("无法删除非空的container");
            return;
        }
        var flag = window.confirm("确定要删除选中container？（不可撤销操作）")
        if (!flag){
            return;
        }
    //dc=delete_container
    $.get('/operation?q=dc&name='+opt[opt.selectedIndex].value ,
        function (res){
            if(res=='failure') {
                alert('删除失败');
                return;
            }
            $("#select1 option:selected").remove();
            $('#select1').get(0).size=$('#select1').get(0).options.length;
            if ($('#select1').get(0).options.selectedIndex==-1){
                $('#objects').hide();
            }
        });
    });

    $("#addContainer").click(function (){
        //添加一个container
        var text = window.prompt("输入container名字");
        if(text==null || text.match(/^\s*$/)){
            return ;
        }
        else if(valid_container(text)==false){
            alert("container编码后长度要小于256且不能以/开头");
            return;
        }
    var opts = $('#select1').get(0).options;
    for(i=0;i<opts.length;i++){
        if(opts[i].value==text){
            alert("该container已存在");
            return ;
        }
    }
    opt = new Option(text+'('+0+')');
    opt.value= text;
    $.get('/operation?q=cc&name='+text,function (res){
        if (res=='failure'){
            alert('创建container失败');
            return ;
        }
        opts.add(opt);
        if (opts.length>=19){
            $('#select1').get(0).size=19;
        }else{
            $('#select1').get(0).size=opts.length;
        }
        show_obj_list()
    }); //cc=create_container
    })

    $("#select1").change(function (){
        //选中的container变化时显示里面的object列表
        show_obj_list();
    })
    $('#addObject').click(function (){
        //上传object
        $.blockUI({fadeIn:1000,
            message:$('#uploadForm'),
        css: {
            border: 'none',
        padding: '15px',
        backgroundColor: '#000',
        '-webkit-border-radius': '10px',
        '-moz-border-radius': '10px',
        opacity: .5,
        color: '#8c7a77'
        }});
        $('.blockOverlay').attr('title','Click to unblock').click($.unblockUI);
    })
    $('#uploadForm').submit(function (){
        //提交按钮被点击时检查上传文件名
        var file_name = $('#file_field').val();
        var rows = $('#table1').get(0).rows;
        for(var i=1;i<rows.length;i++){
            if (rows[i].cells[0].innerHTML==file_name){
                var flag = confirm('存在同名object，是否要覆盖？');
                if (flag==true) return true;
                else return false;
            }
        }
        return true;
    })
    $('#download').click(function (){
        //点击下载选中object
        var table1 = $('#table1').get(0);
        var count = 0;
        $(':checkbox:visible').each(function (){
            if($(this).is(':checked')){
                count++;
            }
        });
        if (count==0) return;
        var flag = true;
        if(count>1) flag=confirm('您选择了多于一个object，他们将被打包成zip文件下载');
        if(flag==false) return;
        var objs = '';
        for(var i=1;i<table1.rows.length;i++){
            if(table1.rows[i].style.display=='none') continue;
            if($(':checkbox').get(i-1).checked){
                objs+=table1.rows[i].cells[0].innerHTML;
                objs+='^';
            }
        }
        objs+=$('#select1 option:selected').val();
        //dl=download
        self.location = '/download?name='+objs
    })
    $('#select2').change(function (){
        change_unit();
    })
    $('#all_select').click(function (){
        var table = $('#table1').get(0);
        var count = 0;
        for(var i=1;i<table.rows.length;i++){
            if($(':checkbox').get(i-1).checked){
                count++;
            }
        }
        if (count==(table.rows.length-1)){
            //如果已经全部选中就取消全选
            for(var i=1;i<table.rows.length;i++){
                $(':checkbox').get(i-1).checked = false;
            }
        }
        else{
            for(var i =1;i<table.rows.length;i++){
                $(':checkbox').get(i-1).checked = true;
            }
        }
    });
})
