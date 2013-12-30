//<![CDATA[
	var groupFormData;
	var rowSelected = 0;
	var groupFormtype;
	var gidselected = 0;
	var submiturl = '';
	
	function disableSelection(target){
		if (typeof target.onselectstart!="undefined") //IE route
			target.onselectstart=function(){return false}
		else if (typeof target.style.MozUserSelect!="undefined") //Firefox route
			target.style.MozUserSelect="none"
		else //All other route (ie: Opera)
			target.onmousedown=function(){return false}
		target.style.cursor = "default"
	}

	function doreload() {
		gidselected = 0;
		$("#groupgrid").jqGrid('setGridParam',{
			url:'/db/findGroup?groupname='+document.getElementById("filtrado").value,
			datatype:"json"
			}).trigger("reloadGrid");
		$('#wordsbtn').attr("disabled", "disabled");
		$('#urisbtn').attr("disabled", "disabled");
		$('#filesbtn').attr("disabled", "disabled");
	}
	
	function loadData() {
		$(window).focus(function() {
			//doreload();
		});
		
		$("#groupgrid").jqGrid({
			url:'/db/findGroup?groupname='+document.getElementById("filtrado").value,
			datatype: "json",
			autoencode: true,
			hidegrid: false,
			jsonReader: {
				repeatitems: false,
				root: function (obj) { return obj; },
				page: function (obj) { return 1; },
				total: function (obj) { return 1; },
				records: function (obj) { return obj.length; }
			},
			colNames: ['gid','Nombre', 'Descripción'],
			colModel: [
				{name:'gid', index:'gid', width:50, sorttype:"int", align: "right", hidden: true},
				{name:'groupname',index:'groupname', width:120  },
				{name:'description', index:'description', width:180 }
				],
			viewrecords: true,
			caption: "Grupos",
			height: 120,
			width: 325,
			shrinkToFit: false,
			forceFit: true,
			gridComplete: function() { disableSelection(document.getElementById("groupgrid")); }
		});
	}
	
	function getRowIdData(rowId) {
		var rowData = jQuery('#groupgrid').jqGrid('getRowData', rowId);
		return rowData;
	}
	
	$(window).load(function(){ 
		loadData();
		$('#wordsbtn').attr("disabled", "disabled");
		$('#urisbtn').attr("disabled", "disabled");
		$('#filesbtn').attr("disabled", "disabled");
		
		$("#groupgrid").jqGrid('setGridParam', {onSelectRow: function(rowid, status, e){
			//alert('selected '+rowid)
			$('#wordsbtn').removeAttr("disabled");
			$('#urisbtn').removeAttr("disabled");
			$('#filesbtn').removeAttr("disabled");
			rowSelected = rowid;
			rowData = getRowIdData(rowid);
			gidselected = rowData['gid'];
				}});
		
		$("#filtrado" ).bind('input', function() {
			doreload()
		});
	});
	
	$(document).ready(function(){	
		$('#wordsbtn').click(function() {
			submiturl = 'Words';
			$.ajax({
				cache: false,		
				type: "GET",
				url: '/db/getWords',
				data : 'gid='+gidselected,
				success: function(data){
					var lines = $("#reglas").val();
					for (var row in data) {
						lines = lines.concat(data[row]['words'],'\n');
					}
					console.log(lines);
					$("#reglas").val($.trim(lines));
				}
			});
			$("#rulestitle").text('Reglas de palablas');
			$('#divmain').css("visibility","hidden");
			$('#divrules').css("visibility","visible");
			$('#reglas').focus();
			
        });
		
		$('#urisbtn').click(function() {
			submiturl = 'Uris';
			$.ajax({
				cache: false,		
				type: "GET",
				url: '/db/getUris',
				contentType: "application/json; charset=utf-8",
    			dataType: "json",
				scriptCharset: "utf-8",
				data : 'gid='+gidselected,
				success: function(data){
					var lines = $("#reglas").val();
					for (var row in data) {
						lines = lines.concat(data[row]['uri'],'\n');
					}
					console.log(lines);
					$("#reglas").val($.trim(lines));
				},
				error: function (xhr, textStatus, errorThrown) {
        			$("#reglas").val('error recuperando información: '+xhr.responseText);
    			}
			});
			$("#rulestitle").text('Reglas de direcciones URI');
			$('#divmain').css("visibility","hidden");
			$('#divrules').css("visibility","visible");
        }); 
		
		$('#filesbtn').click(function() {
			submiturl = 'Mimes';
			$.ajax({
				cache: false,
				type: "GET",
				url: '/db/getMimes',
				data : 'gid='+gidselected,
				success: function(data){
					var lines = $("#reglas").val();
					for (var row in data) {
						lines = lines.concat(data[row]['mimes'],'\n');
					}
					console.log(lines);
					$("#reglas").val($.trim(lines));
				}
			});
			$("#rulestitle").text('Reglas de tipo de fichero');
			$('#divmain').css("visibility","hidden");
			$('#divrules').css("visibility","visible");
        }); 
		
        $('#savebtn').click(function() {
			//submiturl = 'Uris';
			$.ajax({
				cache: false,		
				type: "GET",
				url: '/db/save'+submiturl,
				data : 'gid='+gidselected+'&data='+encodeURI($("#reglas").val()),
			});

            // update the block message
			$("#reglas").val('');
			$('#divrules').css("visibility","hidden");
			$('#divmain').css("visibility","visible");
            /*
			$.ajax({ 
                url: 'wait.php', 
                cache: false, 
                complete: function() { 
                    // unblock when remote call returns 
                    $.unblockUI(); 
                } 
            }); 
			*/
        }); 
 
        $('#cancelbtn').click(function() {
			$("#reglas").val('');
			$('#divrules').css("visibility","hidden");
			$('#divmain').css("visibility","visible");
			return false; 
        });
		




	});
//]]>  
