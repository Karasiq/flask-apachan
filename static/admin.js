function ban(id) {
    $.getJSON($SCRIPT_ROOT + '/admin/ban', {
        userid: id
    }, function (data) {
        refresh_page();
    });
}
function delall(id) {
    $.getJSON($SCRIPT_ROOT + '/admin/delall', {
        userid: id
    }, function (data) {
        refresh_page();
    });
}
function delall_ip(ip) {
    $.getJSON($SCRIPT_ROOT + '/admin/del_ip', {
        ipaddr: ip
    }, function (data) {
        refresh_page();
    });
}
function transfer(id) {
    $.ajax({
        url: $SCRIPT_ROOT + '/admin/transfer_data',
        data: {
            thread_id: id
        },
        success: function (data) {
            $("#transfer_" + id).replaceWith(data);
            var $selbox = $("#tsb_" + id);
            $selbox.change(function() {
                $.post($SCRIPT_ROOT + '/admin/transfer', { thread_id: id, new_section: $selbox.val() }, function(data) {
                    if(data.result) {
                        refresh_page();
                    }
                });
            })
        }
    });
}

$(function() {
    var $clear_cache = $("#admin-clear-cache");
    $clear_cache.click(function() {
        $.getJSON($SCRIPT_ROOT + '/admin/clear_cache', {}, function(data) {
            var $status_img = $("#admin-clear-cache-status");
            if(!$status_img.length)
            {
                $status_img = $('<img id="admin-clear-cache-status">');
                $clear_cache.after($status_img);
            }
            $status_img.attr('src', data.result ? flask_util.url_for('static', {filename:"success.png"}) : flask_util.url_for('static', {filename:"fail.png"}));

            if(data.result) {
                refresh_page();
            }
        });
    });
});