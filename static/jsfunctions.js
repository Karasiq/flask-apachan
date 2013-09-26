function submit_vote(id,v)
{
	$.getJSON($SCRIPT_ROOT + '/_vote', {
			postid: id,
			vote: v
		}, function(data) {
        $("span#rt" + id).text(data);
		$("a#vt1_" + id).text('');
		$("a#vt2_" + id).text('');
      });
}
function copy_selection()
{
    var t = window.getSelection();
    if(t!="")
    {
        var $msgfield = $("textarea#msg");
        $msgfield.text($msgfield.text() + "[quote]"+t+"[/quote]");
        return false;
    }
    else return true;
}
function set_fp()
{
	var fingerprint = new Fingerprint({canvas: true}).get();
	// var fingerprint = new Fingerprint().get();
	$.getJSON($SCRIPT_ROOT + '/set-fp', {
		fp: fingerprint
	});
}
function get_ec()
{
	if(!ec) var ec = new evercookie();
	ec.get("uid", function(value) {
		$.getJSON($SCRIPT_ROOT + '/set_id', {
			uid: value
		});
	});
}
function set_ec(newid)
{
	if(!ec) var ec = new evercookie();
    ec.set("uid", newid);
}
function add_to_favorites(id)
{
	$.getJSON($SCRIPT_ROOT + '/add-to-favorites', {
			thid: id
		}, function(data) {
        $("img#fav" + id).attr("src", data.result);
      });
}
function hide_post(id)
{
	$.getJSON($SCRIPT_ROOT + '/hide-thread', {
			thid: id
		}, function(data) {
        if(data.result) {
			$("table#tbl" + id).hide();
		}
      });
}
function highlight(comment)
{
  var tbl = document.getElementById("tbl"+comment);
  tbl.style.background = "#F0E68C";
  if(highlighted && highlighted != comment) 
  {
    tbl = document.getElementById("tbl"+highlighted);
    tbl.style.background = "#E6E6E6";
  }
  highlighted = comment;
}
function open_comment(id)
{
  var ndiv = document.getElementById(id);
  ndiv.style.display='block';
}
function menu_over()
{
  var ndiv = document.getElementById("nav_div");
  ndiv.style.display='block';
}
function menu_out()
{
  var ndiv = document.getElementById("nav_div");
  ndiv.style.display='none';
}
function menu_over1()
{
  var ndiv = document.getElementById("nav_div1");
  ndiv.style.display='block';
}
function menu_out1()
{
  var ndiv = document.getElementById("nav_div1");
  ndiv.style.display='none';
}