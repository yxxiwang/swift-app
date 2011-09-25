$(document).ready(function() {
    $('#login_form').submit(function (){
        var username = $('#id_username').val();
        var password = $('#id_password').val();
        if (username.match(/^\s*$/)||password.match(/^\s*$/)){
            alert('用户名和密码不能为空');
            return false;
        }
    });
});
