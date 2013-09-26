function ban(id)
{
	$.getJSON($SCRIPT_ROOT + '/admin/ban', {
			userid: id
		}, function(data) {
        location.reload();
      });
}
function delall(id)
{
	$.getJSON($SCRIPT_ROOT + '/admin/delall', {
			userid: id
		}, function(data) {
        location.reload();
      });
}
function delall_ip(ip)
{
	$.getJSON($SCRIPT_ROOT + '/admin/del_ip', {
			ipaddr: ip
		}, function(data) {
        location.reload();
      });
}
function to_trash(id)
{
	$.getJSON($SCRIPT_ROOT + '/admin/totrash', {
			thread_id: id
		}, function(data) {
        location.reload();
      });
}