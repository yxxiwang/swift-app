$(document).ready(function (){
    $('#register_form').submit(function(){
        var username = $('#id_username').val();
        var password = $('#id_password').val();
        var password_2 = $('#id_password_again').val();
        var email = $('#id_email').val();
        if(username.match(/^\s*$/)||password.match(/^\s*$/)
            ||email.match(/^\s*$/)){
            alert("用户名密码和邮箱不能为空");
            return false;
        }
        if (password!=password_2){
            alert('两次输入的密码不一致');
            return false;
        }
        if (!email.match(/^([a-zA-Z0-9_\.-])+@([a-zA-Z0-9_-])+((\.[a-zA-Z0-9_-]{2,3}){1,2})$/)){
            alert('邮箱不符合格式');
            return false;
        }
        if(username.length>20||password.length>16){
            alert('用户名不能超过20字节，密码不能超过16字节');
            return false;
        ;}
    });
});
