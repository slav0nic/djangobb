// helper function for console logging
function log() {
    if (window.console && window.console.log) {
        try {
            window.console.log(Array.prototype.join.call(arguments,''));
        } catch (e) {
            log("Error:" + e);
        }
    }
}
//log("board.js loaded");

function copy_paste(id) {   
    var post = $('#' + id);
    var username = post.find(".username").text();
    $.ajax('/forums/post/' + id.substr(1) + '/source/').done(function (data) {
        paste('[quote=' + username + ']' + data + '[/quote]\n');
    });
}

function paste(txt) {
    //textarea = $("#id_body");
    textarea = document.forms['post']['body'];
    insertAtCaret(textarea, txt);
    $("#id_body").focus();
}

function insertAtCaret (textObj, textFieldValue) {
    // log("insertAtCaret(" + textObj + "," + textFieldValue + ")");
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

$(document).ready(function() {
    $(".username").click(function() {
        var nick = $(this).text();
        paste("[b]"+nick+"[/b]\n");
    });
    $(".username").attr('title', 'Click to paste nick name in reply form.');
    
    window.onbeforeunload = function() {
        var obj = $("textarea#id_body");
        if (obj.length != 1) {
            // object not found in page -> do nothing
            return
        }
        var text = obj.val().trim();
        //log("onbeforeunload text:" + text);
        if (text.length > 3) {
            // Firefox will not use the string. IE use it
            // TODO: Translate string
            return "Leave page with unsaved content?";
        }
        // if nothing returned, browser leave the page without any message
    };
    $("form input[type=submit]").click(function() {
        //log("unbind onbeforeunload");
        window.onbeforeunload = null;
    });
    
    !function () {
        var submitted = false;
        $('#post').submit(function (e) {
            if (submitted) {
                e.preventDefault();
            }
            submitted = true;
        });
    }();
});
