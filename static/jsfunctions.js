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
    var tbl = document.getElementById("tbl" + comment);
    tbl.style.background = "#F0E68C";
    if (highlighted && highlighted != comment) {
        tbl = document.getElementById("tbl" + highlighted);
        tbl.style.background = "#E6E6E6";
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
        if (data.result) $("div#posts").html(data.posts);
    });
}
$(document).ready(function () {
    auto_refresh_enabled = localStorage.getItem('auto-refresh-enabled');
    $("#auto-reload").text(auto_refresh_enabled ? "Отключить автообновление" : "Включить автообновление");
    /* $(".post-form-show").show();
    $(".post-form").hide();
    $(".post-form-show").click(function() {
        $(this).hide();
        $(this).parent('div').children(".post-form").show();
        return false;
    }); */
});
setInterval(function () {
    if (auto_refresh_enabled) {
        refresh_page();
    }
    return true;
}, 20000);
function change_auto_refresh() {
    auto_refresh_enabled = !auto_refresh_enabled;
    $("#auto-reload").text(auto_refresh_enabled ? "Отключить автообновление" : "Включить автообновление");
    localStorage.setItem('auto-refresh-enabled', auto_refresh_enabled);
}