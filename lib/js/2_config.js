//<![CDATA[
	var userFormData;
	var rowSelected = 0;
	var userFormtype;
	var selected_username = "";
	var selected_uid = 0;
	var group_membergrid_selected_gid = 0;
	var group_notmembergrid_selected_gid = 0;

	function disableSelection(target){
		if (typeof target.onselectstart!="undefined") //IE route
			target.onselectstart=function(){return false}
		else if (typeof target.style.MozUserSelect!="undefined") //Firefox route
			target.style.MozUserSelect="none"
		else //All other route (ie: Opera)
			target.onmousedown=function(){return false}
		target.style.cursor = "default"
	}

	function do_reset_form() {
	}
	

	function loadData() {
	}
	
	$(window).focus(function() {
		$( "#refreshbtn" ).trigger( "click" );

	});
	
	$(window).load(function(){
		$( "#refreshbtn" ).trigger( "click" );
	});
		
	$(document).ready(function(){
		$('#refreshbtn').click(function() {
			$.ajax({
				cache: false,		
				type: "GET",
				url: '/db/getLog',
				contentType: "application/json; charset=utf-8",
				data : 'numLines='+$("#numLines").val(),
				scriptCharset: "utf-8",
				success: function(data){
					var lines='';
					for (var row in data) {
						lines = lines.concat(data[row]['lineid'],' : ',data[row]['timestamp'],' : ',data[row]['line'],'\n');
					}
					$("#logtext").val(lines);
				},
				error: function (xhr, textStatus, errorThrown) {
        			$("#logtext").val('error recuperando información: '+xhr.responseText);
    			}
			});
        });
		/*
		$('#delmember').click(function(){
			var dataString= 'uid='+selected_uid+'&gid='+group_membergrid_selected_gid;
			$.ajax({
				type: "GET",
				url: '/db/delUserFromGroup',
				data: dataString
			});
			do_reset_form();
			return false; 
		});
		$('#addmember').click(function(){
			var dataString= 'uid='+selected_uid+'&gid='+group_notmembergrid_selected_gid;
			$.ajax({
				type: "GET",
				url: '/db/addUserToGroup',
				data: dataString
			});
			do_reset_form();
			return false; 
		});
		$('#refreshbtn').click(function(){
			do_reset_form();
		});
		*/
	});
//]]>  
