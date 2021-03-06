var highlighted = 0;
function highlight(comment) {
    var tbl = $("#tbl" + comment);
    tbl.addClass('post-highlighted');
    if (highlighted && highlighted != comment) {
        tbl = $("#tbl" + highlighted);
        tbl.removeClass('post-highlighted');
    }
    highlighted = comment;
}

function enable_post_actions() {
    $('.post').unbind('contextmenu').on('contextmenu', 'td', function() {
        var t = $.trim(window.getSelection());
        if (t != "") {
            var $msgfield = $("textarea#msg");
            $msgfield.val($msgfield.val() + "[quote]" + t + "[/quote]");
            clear_selection();
            return false;
        }
        return true;
    });
    
    $('.page-jump').unbind('click').click(function() {
        $('#posts').animate({opacity:0.2},400);
        ajax_data.page = $(this).text();
        refresh_page(function() {
            $('#posts').animate({opacity:1},200);
        });
        return false;
    });
    
    $('.add-to-favorites').unbind('click').click(function () {
        var $fav_img = $(this);
        $.getJSON($SCRIPT_ROOT + '/add-to-favorites', {
            thid: $fav_img.attr('post-id')
        }, function (data) {
            $fav_img.prop("src", data.result);
        });
        return false;
    });
    
    $('.hide-thread').unbind('click').click(function () {
        var id = $(this).attr('post-id');
        $.getJSON($SCRIPT_ROOT + '/hide-thread', {
            thid: id
        }, function (data) {
            if (data.result) {
                $("table#tbl" + id).hide();
            }
        });
        return false;
    });
    
    $('.delete-post').unbind('click').click(function () {
        if(confirm("Вы уверены?")) {
            var id = $(this).attr('post-id');
            $.get(flask_util.url_for('postdel', {postid : id, ajax : true}), {}, function (data) {
                if(data.result) {
                    refresh_page();
                }
            });
        }
        return false;
    });
    
    $('.vote-post').unbind('click').click(function () {
        var $vt = $(this).parent('#post-voting');
        var $rt = $(this).parents('td:first').children('#post-rating');
        $vt.html($('<img>').attr('height', 15).attr('width', 15).attr('src', flask_util.url_for('static', {filename: 'wait.gif'})));
        $.getJSON($SCRIPT_ROOT + '/_vote', {
            postid: $vt.attr('post-id'),
            vote: $(this).attr('vote')
        }, function (data) {
            $rt.text(data.post_rating);
            $vt.html($('<img>').attr('src', data.result ? flask_util.url_for('static', {filename: "success.png"}) : flask_util.url_for('static', {filename: "fail.png"})));
        });
        return false;
    });
    var $show_answer_to = $('.show-answer-to');
    $show_answer_to.unbind('click').click(function () {
        highlight($(this).attr('answer-to'));
    });
        
    if(!isMobileDevice()) {
        $show_answer_to.unbind('mouseenter').mouseenter(function () {
            var pos = $(this).position();
            var id = $(this).attr('answer-to');
            var $this = $(this);
            
            var $post = $('#tbl' + id + ':first').clone(true);
            if(!$post.length) {
                $.ajax({
                    url: flask_util.url_for('ajax_getpost', {postid : id}),
                    async: false,
                    success: function (data) {
                        $('body').append(data);
                        $post = $('#tbl' + id + ':first').hide().clone(true);
                        enable_post_actions();
                    }
                });
            }
            $post
                .insertAfter($(this))
                .addClass('post-preview')
                .mouseleave(function () {
                    $(this).remove();
                })
                .show()
                .css('left', $(this).offset().left - $(window).scrollLeft() + $post.width() > $(window).width ? pos.left + 200 : pos.left - 200)
                .css('top', $(this).offset().top - $(window).scrollTop() + $post.height() > $(window).height() ? pos.top - $post.height() - 20 : pos.top + 20);

            console.log($(window).height());
            console.log($this.offset());
            return false;
        })
        .mouseleave(function () {
            setTimeout(function () {
                $('.post-preview').each(function () {
                    if(!$(this).is(':hover')) $(this).remove();
                });
            }, 600);
        });
    }

    $('.post-message').css('max-height', 400).unbind('hover').hover(function () {
        $(this).css('max-height', 'none');
    }, function () {
        $(this).css('max-height', 400);
    });
    
    if(typeof enable_image_magnifier !== 'undefined') enable_image_magnifier();
    if(typeof admin_actions_bind !== 'undefined') admin_actions_bind();
    if(typeof custom_actions_bind !== 'undefined') custom_actions_bind();
}

var auto_refresh_enabled = false;
function refresh_page(done_func) {
    $.ajax({
        type:'GET',
        url: $SCRIPT_ROOT + '/ajax/reload',
        cache: false,
        data: ajax_data,
        success: function (data) {
            $("div#posts").html(data);
            var currentdate = new Date();
            $("#last-refresh").text("Последнее обновление страницы: " + currentdate.toLocaleTimeString());
            enable_post_actions();
            if(typeof done_func !== 'undefined') done_func();
        }
    });
}

function set_theme(new_theme)
{
    $('#theme').prop('href', flask_util.url_for('static', {filename: 'themes/' + new_theme}));
}

function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

function getPlayingVideosCount() {
    var d = 0;
    $("embed.youtube-video").each(function(){
        if(typeof this.getPlayerState !== 'undefined' && this.getPlayerState() == 1) d++;
    });
    return d;
}

function clear_selection() {
    if (window.getSelection) {
        if (window.getSelection().empty) {  // Chrome
            window.getSelection().empty();
        }
        else if (window.getSelection().removeAllRanges) {  // Firefox
            window.getSelection().removeAllRanges();
        }
    }
    else if (document.selection) {  // IE?
        document.selection.empty();
    }
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
    
    $('#commit').prop('disabled', false)
    .click(function() {
        $(this).prop('disabled', true);
        $('#form1').submit();
        return false;
    });
    
    if(isMobileDevice()) {
        $('#menu').click(function () {
            var $nd = $('#nav_div');
            if(!$nd.is(':hover')) $nd.toggle();
        });
    }
    
    auto_refresh_enabled = localStorage.getItem('auto-refresh-enabled');
    $("#auto-reload").attr('title', auto_refresh_enabled === 'true' ? "Отключить автообновление" : "Включить автообновление")
    .attr('src', flask_util.url_for('static', {filename: auto_refresh_enabled === 'true' ? "refresh-dis.png" : "refresh.png"}))
    .click(function() {
        auto_refresh_enabled = auto_refresh_enabled === 'true' ? 'false' : 'true';
        $(this).attr('title', auto_refresh_enabled === 'true' ? "Отключить автообновление" : "Включить автообновление").attr('src', flask_util.url_for('static', {filename: auto_refresh_enabled === 'true' ? "refresh-dis.png" : "refresh.png"}));
        localStorage.setItem('auto-refresh-enabled', auto_refresh_enabled);
    });
    var aspf = typeof localStorage['always-show-postform'] !== 'undefined' ? localStorage.getItem('always-show-postform') : (isMobileDevice() ? 'true' : 'false');
    $("#always-show-postform").prop('checked', aspf === 'true').click(function(){
        localStorage.setItem('always-show-postform', $(this).prop('checked'));
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
        var $td = $(this).parents('td:first');
        $td.children("#img_url").attr('disabled', $(this).val() != '0');
        $td.children("#img").attr('disabled', $(this).val() != '0');
    });
    
    var hash = window.location.hash;
    if(hash.charAt(1) == 't') {
        highlight(hash.substring(2));
    }
    $('.shaded').css('opacity', 0.2)
    .hover(function() {
        $(this).fadeTo('fast', 1);
    }, function() {
        $(this).fadeTo('fast', 0.2);
    });
    
    $('#show-hidden-threads').click(function () {
        var $control = $(this); 
        $.getJSON($SCRIPT_ROOT + '/unhide-threads', {}, function (data) {
            if (data.result) {
                refresh_page();
                $control.hide();
            }
        });
        return false;
    });
    
    enable_post_actions();
    
    $('.require-js').show();
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