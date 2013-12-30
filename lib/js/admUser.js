//<![CDATA[
	var userFormData;
	var rowSelected = 0;
	var userFormtype;
	
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
		$("#grid").jqGrid('setGridParam',{
			url:'/db/findUser?username='+document.getElementById("filtrado").value,
			datatype:"json"
			}).trigger("reloadGrid");
		$('#delUser').attr("disabled", "disabled");
	}
	
	function loadData() {
		$(window).focus(function() {
			doreload();
		});
		
		$("#grid").jqGrid({
			url:'/db/findUser?username='+document.getElementById("filtrado").value,
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
			colNames: ['uid','Usuario', 'Rol', 'Password','Descripción',
						'L_AH','M_AH','X_AH','J_AH','V_AH','S_AH','D_AH'],
			colModel: [
				{name:'uid', index:'uid', width:50, align: "right"},
				{name:'username',index:'username', width:80  },
				{name:'rol',index:'rol', width:30, align: "center" },
				{name:'password', index:'password', width:60, hidden: true },
				{name:'description', index:'description', width:180 },
				{name:'L_AH', index:'L_AH', width:40, sorttype:"int", align: "right", hidden: true},
				{name:'M_AH', index:'M_AH', width:40, sorttype:"int", align: "right", hidden: true},
				{name:'X_AH', index:'X_AH', width:40, sorttype:"int", align: "right", hidden: true},
				{name:'J_AH', index:'J_AH', width:40, sorttype:"int", align: "right", hidden: true},
				{name:'V_AH', index:'V_AH', width:40, sorttype:"int", align: "right", hidden: true},
				{name:'S_AH', index:'S_AH', width:40, sorttype:"int", align: "right", hidden: true},
				{name:'D_AH', index:'D_AH', width:40, sorttype:"int", align: "right", hidden: true}
				],
			//rowNum:10,
			//pager: '#pager',
			//sortname: 'uid',
			viewrecords: true,
			//sortorder: "asc",
			caption: "Usuarios",
			gridComplete: function() { disableSelection(document.getElementById("grid")); },

		});
	}
	
	function getRowIdData(rowId) {
		var rowData = jQuery('#grid').jqGrid ('getRowData', rowId);
		var jsondata=JSON.stringify(rowData);
		return jsondata;
	}
	
	$(window).load(function(){ 
		loadData();
		$('#delUser').attr("disabled", "disabled");
		
		$("#grid").jqGrid('setGridParam', {ondblClickRow: function(rowid,iRow,iCol,e){
			userFormData = getRowIdData(rowid);
			userFormType = 'modUser'
			window.open("formUser.html", 'userForm', '');

		}});
		
		$("#grid").jqGrid('setGridParam', {onSelectRow: function(rowid, status, e){
			$('#delUser').removeAttr("disabled");
			rowSelected = rowid;
		}});
		
		$("#filtrado" ).bind('input', function() {
			doreload()
		});
	});
	
	$(document).ready(function(){
			$('#newUser').click(function(){
			$('#delUser').attr("disabled", "disabled");
			userFormType = 'addUser'
			window.open("formUser.html", 'userForm', '');
		});
	});
	
	$(document).ready(function(){
		$('#delUser').click(function(){
			userFormType = 'delUser'
			userFormData = getRowIdData(rowSelected);
			window.open("delUser.html", 'userForm', '');
			$('#delUser').attr("disabled", "disabled");
		});
	});
//]]>  