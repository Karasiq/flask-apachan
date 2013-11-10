var highlighted = 0;
function submit_vote(id, v) {
    var $vt = $("#voting_" + id);
    $vt.html('<img width="15" height="15" src="' + flask_util.url_for('static', {filename: 'wait.gif'}) + '">');
    $.getJSON($SCRIPT_ROOT + '/_vote', {
        postid: id,
        vote: v
    }, function (data) {
        $("span#rt" + id).text(data.post_rating);
        var $status_img = $('<img>');
        $vt.html($status_img);
        $status_img.attr('src', data.result ? flask_util.url_for('static', {filename: "success.png"}) : flask_util.url_for('static', {filename: "fail.png"}));
    });
}
function unhide_threads() {
    $.getJSON($SCRIPT_ROOT + '/unhide-threads', {}, function (data) {
        if (data.result) {
            refresh_page();
        }
    });
}
function copy_selection() {
    var t = window.getSelection();
    if (t != "") {
        var $msgfield = $("textarea#msg");
        $msgfield.val($msgfield.val() + "[quote]" + t + "[/quote]");
    }
    return true;
}
function set_fp() {
    var fingerprint = new Fingerprint({canvas: true}).get();
    // var fingerprint = new Fingerprint().get();
    $.getJSON($SCRIPT_ROOT + '/set-fp', {
        fp: fingerprint
    });
}
function get_ec() {
    ec.get("uid", function (value) {
        $.getJSON($SCRIPT_ROOT + '/set_id', {
            uid: value
        });
    });
}
function set_ec(newid) {
    ec.set("uid", newid);
}
function add_to_favorites(id) {
    $.getJSON($SCRIPT_ROOT + '/add-to-favorites', {
        thid: id
    }, function (data) {
        $("img#fav" + id).attr("src", data.result);
    });
}
function hide_post(id) {
    $.getJSON($SCRIPT_ROOT + '/hide-thread', {
        thid: id
    }, function (data) {
        if (data.result) {
            $("table#tbl" + id).hide();
        }
    });
}
function highlight(comment) {
    var tbl = $("#tbl" + comment);
    tbl.addClass('post-highlighted');
    if (highlighted && highlighted != comment) {
        tbl = $("#tbl" + highlighted);
        tbl.removeClass('post-highlighted');
    }
    highlighted = comment;
}
function open_comment(id) {
    var ndiv = document.getElementById(id);
    ndiv.style.display = 'block';
}
function menu_over() {
    var ndiv = document.getElementById("nav_div");
    ndiv.style.display = 'block';
}
function menu_out() {
    var ndiv = document.getElementById("nav_div");
    ndiv.style.display = 'none';
}
function menu_over1() {
    var ndiv = document.getElementById("nav_div1");
    ndiv.style.display = 'block';
}
function menu_out1() {
    var ndiv = document.getElementById("nav_div1");
    ndiv.style.display = 'none';
}

var auto_refresh_enabled = false;
function refresh_page() {
    $.getJSON($SCRIPT_ROOT + '/ajax/reload', ajax_data, function (data) {
        if (data.result) {
            $("div#posts").html(data.posts);
            var currentdate = new Date();
            $("#last-refresh").text("Последнее обновление страницы: " + currentdate.toLocaleTimeString());
        }
    });
}

function set_theme(new_theme)
{
    $('#theme').html('');
    $('<link>')
        .appendTo($('#theme'))
        .attr({type : 'text/css', rel : 'stylesheet'})
        .attr('href', flask_util.url_for('static', {filename: 'themes/' + new_theme}));
}

function getPlayingVideosCount() {
    var d = 0;
    $("embed.youtube-video").each(function(){
        if(this.getPlayerState() == 1) d++;
    });
    return d;
}

$(document).ready(function () {
    set_theme('default.css');
    var theme_select = $("#theme-select");
    theme_select.change(function() {
        localStorage.setItem('theme', $(this).val());
        set_theme($(this).val());
    });
    var theme = localStorage.getItem('theme') || 'default.css';
    if(theme)
    {
        theme_select.val(theme);
        set_theme(theme);
    }
    theme_select.show();
    
    var $post_button = $('#commit');
    $post_button.prop('disabled', false);
    $post_button.click(function() {
        $(this).prop('disabled', true);
        $('#form1').submit();
        return false;
    });

    auto_refresh_enabled = localStorage.getItem('auto-refresh-enabled');
    var $auto_reload = $("#auto-reload");
    $auto_reload.attr('title', auto_refresh_enabled === 'true' ? "Отключить автообновление" : "Включить автообновление");
    $auto_reload.attr('src', flask_util.url_for('static', {filename: auto_refresh_enabled === 'true' ? "refresh-dis.png" : "refresh.png"}));
    $auto_reload.show();
    $auto_reload.click(function() {
        auto_refresh_enabled = auto_refresh_enabled === 'true' ? 'false' : 'true';
        $auto_reload.attr('title', auto_refresh_enabled === 'true' ? "Отключить автообновление" : "Включить автообновление");
        $auto_reload.attr('src', flask_util.url_for('static', {filename: auto_refresh_enabled === 'true' ? "refresh-dis.png" : "refresh.png"}));
        localStorage.setItem('auto-refresh-enabled', auto_refresh_enabled);
    });
    var aspf = localStorage.getItem('always-show-postform') || 'false';
    $("#always-show-postform").val(aspf);
    $("#always-show-postform").click(function(){
        localStorage.setItem('always-show-postform', $(this).is(':checked'));
        location.reload();
    });
    if(aspf == 'false')
    {
        $(".post-form-show").show();
        $(".post-form").hide();
        $(".post-form-show").click(function() {
            $(this).hide();
            $(this).parent().parent().children(".post-form").show();
            return false;
        });
    }

    $('.ins_random').change(function() {
        $(this).parents('td:first').children("#img_url").attr('disabled', $(this).val() != '0');
        $(this).parents('td:first').children("#img").attr('disabled', $(this).val() != '0');
    });
    
    var hash = window.location.hash;
    if(hash.charAt(1) == 't') {
        highlight(hash.substring(2));
    }
});
setInterval(function () {
	auto_refresh_enabled = localStorage.getItem('auto-refresh-enabled');
    var $auto_reload = $("#auto-reload");
    $auto_reload.attr('title', auto_refresh_enabled === 'true' ? "Отключить автообновление" : "Включить автообновление");
    $auto_reload.attr('src', flask_util.url_for('static', {filename: auto_refresh_enabled === 'true' ? "refresh-dis.png" : "refresh.png"}));
	
    if (auto_refresh_enabled === 'true' && !getPlayingVideosCount()) {
        refresh_page();
    }
    return true;
}, 30000);