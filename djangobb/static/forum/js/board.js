var txt = ''

function copyQ(nick) { 
	txt = '' 
	if (document.getSelection) {
		txt = document.getSelection()
	} else 
	if (document.selection) {
		txt = document.selection.createRange().text;
	} 
	txt = '[quote=' + nick + ']' + txt + '[/quote]\n'
}

function insertAtCaret (textObj, textFieldValue) { 
	if (document.all) { 
		if (textObj.createTextRange && textObj.caretPos && !window.opera) { 
			var caretPos = textObj.caretPos; 
			caretPos.text = caretPos.text.charAt(caretPos.text.length - 1) == ' ' ?textFieldValue + ' ' : textFieldValue; 
		} else { 
			textObj.value += textFieldValue; 
		} 
	} else { 
		if (textObj.selectionStart) { 
			var rangeStart = textObj.selectionStart; 
			var rangeEnd = textObj.selectionEnd; 
			var tempStr1 = textObj.value.substring(0, rangeStart); 
			var tempStr2 = textObj.value.substring(rangeEnd, textObj.value.length); 
			textObj.value = tempStr1 + textFieldValue + tempStr2; 
			textObj.selectionStart = textObj.selectionEnd = rangeStart + textFieldValue.length;
		} else { 
			textObj.value += textFieldValue; 
		} 
	} 
}

function pasteQ() {
	if (txt!='' && document.forms['post']['body']) 
	insertAtCaret(document.forms['post']['body'], txt); 
} 

function pasteN(text) { 
	if (text != '' && document.forms['post']['body'])
	insertAtCaret(document.forms['post']['body'], "[b]" + text + "[/b]\n");
}

