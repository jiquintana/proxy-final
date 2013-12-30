//<![CDATA[
	$(window).load(function(){
		var mousedown = false;

		$(document).mousedown(function() {
		    mousedown = true;
		    return false;
		});
		
		$(document).mouseup(function() {
		    mousedown = false;
		});
	
		$('td.cell').mousedown(function() {
		    $(this).toggleClass('active');
		});
	
		$('td.cell').mouseover(function() {
		    if (mousedown) {	
		        $(this).toggleClass('active');
		    }
		});
		
		$('td').bind('onselectstart', function() {
		    e.preventDefault();
		    return false;
		});
	});
	
	

	function hasClass(element, cls) {
    	return (' ' + element.className + ' ').indexOf(' ' + cls + ' ') > -1;
	}
	
	function myFunction0() {
		alert("I am an alert box!");
	}
	
	function element_name_set_value(elementname, valor) {
		theElement = document.getElementsByName(elementname)[0];
		theElement.value = valor.toString()
		
		//alert(theElement.value)
		//document.getAttribute('name')).value = valor
		
	}
	
	/** Convert a decimal number to binary **/
	var toBinary = function(decNum){
    	return parseInt(decNum,10).toString(2);
	}
	
	/** Convert a binary number to decimal **/
	var toDecimal = function(binary) {
	    return parseInt(binary,2).toString(10);
	}
	
	function setCharAt(str,index,chr) {
	    if(index > str.length-1) return str;
	    return str.substr(0,index) + chr + str.substr(index+1);
	}
	
	function myFunction() {
		//var welements = document.getElementsByClassName("cell"); // Removed [0], that gets the **1st** node, not the NodeList.
		//var checkboxCount = welements.length;

		
		//for (var i = 0; i < welements.length; i++) {
		//	myList[0].style.color
		// getAttribute('class');	
		//	welements[i].getAttribute("name") == 
		//}
		//alert(welements[0].getAttribute('class'));
		//var welements = document.getElementByID("cell");
		var welements = document.getElementsByClassName("cell");
		var checkboxCount = welements.length;
		var L_AH ="", M_AH="", X_AH="", J_AH="", V_AH="", S_AH="", D_AH=""
		
		for (var i = 0; i <  welements.length; i++) {
			var elemento = welements[i].getAttribute('name').substring(0,4);
			//var indice   = welements[i].getAttribute('name').substring(5,7);
			var valor    = hasClass(welements[i],("active")) ? 1 : 0 ;

			switch (elemento) {
			    case "L_AH":	L_AH = valor + L_AH;	break;
			    case "M_AH":	M_AH = valor + M_AH;	break;
			    case "X_AH":	X_AH = valor + X_AH;	break;
			    case "J_AH":	J_AH = valor + J_AH;	break;
			    case "V_AH":	V_AH = valor + V_AH;	break;
			    case "S_AH":	S_AH = valor + S_AH;	break;
			    case "D_AH":	D_AH = valor + D_AH;	break;
			}
		}
		document.getElementById("L_AH").value=toDecimal(L_AH);
		document.getElementById("M_AH").value=toDecimal(M_AH);
		document.getElementById("X_AH").value=toDecimal(X_AH);
		document.getElementById("J_AH").value=toDecimal(J_AH);
		document.getElementById("V_AH").value=toDecimal(V_AH);
		document.getElementById("S_AH").value=toDecimal(S_AH);
		document.getElementById("D_AH").value=toDecimal(D_AH);		
	}
//]]>