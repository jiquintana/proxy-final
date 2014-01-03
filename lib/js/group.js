function test_onload() {
	var mousedown = false;

	$('table').mousedown(function() {
	    mousedown = true;
	    return false;
	});
	
	$('table').mouseup(function() {
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
}


function hasClass(element, cls) {
	return (' ' + element.className + ' ').indexOf(' ' + cls + ' ') > -1;
}

function myFunction0() {
	alert("I am an alert box!");
}

function element_name_set_value(elementname, valor) {
	theElement = document.getElementsByName(elementname)[0];
	theElement.value = valor.toString()
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

