// ----------------------------------------------------------------------------
// markItUp!
// ----------------------------------------------------------------------------
// Copyright (C) 2008 Jay Salvat
// http://markitup.jaysalvat.com/
// ----------------------------------------------------------------------------
// BBCode tags example
// http://en.wikipedia.org/wiki/Bbcode
// ----------------------------------------------------------------------------
// Feel free to add more tags
// ----------------------------------------------------------------------------
var _simple_http_agent = $('#simple-user-agent').text()
if (swfobject.hasFlashPlayerVersion('1')) {
    var version = swfobject.getFlashPlayerVersion();
    _simple_http_agent += ', Flash '+ version.major +'.'+ version.minor +' (release '+ version.release +')';
} else {
    _simple_http_agent += ', No Flash version detected'
}
mySettings = {
	previewParserPath:	POST_PREVIEW_URL, // path to your BBCode parser
	markupSet: [
		{name:'Bold', key:'B', openWith:'[b]', closeWith:'[/b]'},
		{name:'Italic', key:'I', openWith:'[i]', closeWith:'[/i]'},
		{name:'Underline', key:'U', openWith:'[u]', closeWith:'[/u]'},
		{name:'Stroke', key:'S', openWith:'[s]', closeWith:'[/s]' },
		{separator:'---------------' },
		{name:'Picture', key:'P', replaceWith:'[img][![Url]!][/img]'},
		{name:'Link', key:'L', openWith:'[url=[![Url]!]]', closeWith:'[/url]', placeHolder:'Your text to link here...'},
		{separator:'---------------' },
		{name:'Size', key:'S', openWith:'', closeWith:'',
		dropMenu :[
			{name:'Big', openWith:'[big]', closeWith:'[/big]' },
			{name:'Small', openWith:'[small]', closeWith:'[/small]' }
		]},
		{separator:'---------------' },
		{name:'Bulleted list', openWith:'[list]\n', closeWith:'\n[/list]'},
		{name:'Numeric list', openWith:'[list=[![Starting number]!]]\n', closeWith:'\n[/list]'}, 
		{name:'List item', openWith:'[*] '},
		{separator:'---------------' },
		{name:'Quotes', openWith:'[quote]', closeWith:'[/quote]'},
        {name:'Smiles', openWith:'', closeWith:'', dropMenu:[
            {name:'Smile', openWith:':)'}, 
            {name:'Neutral', openWith:':|'}, 
            {name:'Sad', openWith:':('}, 
            {name:'Big smile', openWith:':D'}, 
            {name:'Yikes', openWith:':o'}, 
            {name:'Wink', openWith:';)'}, 
            {name:'Hmm', openWith:':/'}, 
            {name:'Tongue', openWith:':P'}, 
            {name:'Lol', openWith:':lol:'}, 
            {name:'Mad', openWith:':mad:'}, 
            {name:'Roll', openWith:':rolleyes:'}, 
            {name:'Cool', openWith:':cool:'}
        ]},
        {separator:'---------------' },
		{name:'Paste browser / operating system versions', openWith: _simple_http_agent, replaceWith: '', closeWith:'', className:'browser-os-button'},
        {name:'Scratchblocks', openWith:'', closeWith:'', dropMenu:[

            {name:'Motion // category=motion', dropMenu:[
                {name:'move (...) steps', openWith:'move (', closeWith:') steps'},
                {name:'turn right (...) degrees', openWith:'turn right (', closeWith:') degrees'},
                {name:'turn left (...) degrees', openWith:'turn left (', closeWith:') degrees'},
                // ---
                {name:'point in direction (...)', openWith:'point in direction (', closeWith:' v)'},
                {name:'point towards [... v]', openWith:'point towards [', closeWith:' v]'},
                // ---
                {name:'go to x: (...) y: ()', openWith:'go to x: (', closeWith:') y: ()'},
                {name:'go to [mouse-pointer v]', openWith:'go to [mouse-pointer', closeWith:' v]'},
                {name:'glide (...) secs to x: () y: ()', openWith:'glide (', closeWith:') secs to x: () y: ()'},
                // ---
                {name:'change x by (...)', openWith:'change x by (', closeWith:')'},
                {name:'set x to (...)', openWith:'set x to (', closeWith:')'},
                {name:'change y by (...)', openWith:'change y by (', closeWith:')'},
                {name:'set y to (...)', openWith:'set y to (', closeWith:')'},
                // ---
                {name:'if on edge, bounce', replaceWith:'if on edge, bounce'},
                // ---
                {name:'set rotation style [... v]', openWith:'set rotation style [', closeWith:' v]'},
                // ---
                {name:'(x position)', replaceWith:'(x position)'},
                {name:'(y position)', replaceWith:'(y position)'},
                {name:'(direction)', replaceWith:'(direction)'},
            ]},

            {name:'Looks // category=looks', dropMenu:[
                {name:'say [...] for () secs', openWith:'say [', closeWith:'] for (2) secs'},
                {name:'say [...]', openWith:'say [', closeWith:']'},
                {name:'think [...] for () secs', openWith:'think [', closeWith:'] for (2) secs'},
                {name:'think [...]', openWith:'think [', closeWith:']'},
                // ---
                {name:'show', replaceWith:'show'},
                {name:'hide', replaceWith:'hide'},
                // ---
                {name:'switch costume to [... v]', openWith:'switch costume to [', closeWith:' v]'},
                {name:'next costume', replaceWith:'next costume'},
                {name:'switch backdrop to [... v]', openWith:'switch backdrop to [', closeWith:' v]'},
                // ---
                {name:'change [... v] effect by ()', openWith:'change [', closeWith:' v] effect by (25)'},
                {name:'set [... v] effect to ()', openWith:'set [', closeWith:' v] effect to (0)'},
                {name:'clear graphic effects', replaceWith:'clear graphic effects'},
                // ---
                {name:'change size by (...)', openWith:'change size by (', closeWith:')'},
                {name:'set size to (...) %', openWith:'set size to (', closeWith:') %'},
                // ---
                {name:'go to front', replaceWith:'go to front'},
                {name:'go back (...) layers', openWith:'go back (', closeWith:') layers'},
                // ---
                {name:'(costume #)', replaceWith:'(costume #)'},
                {name:'(size)', replaceWith:'(size)'},
                // ---
                {name:'switch backdrop to [... v] and wait', openWith:'switch backdrop to [', closeWith:' v] and wait'},
                {name:'next backdrop', replaceWith:'next backdrop'},
                {name:'(backdrop name)', replaceWith:'(backdrop name)'},
            ]},

            {name:'Sound // category=sound', dropMenu:[
                {name:'play sound [... v]', openWith:'play sound [', closeWith:' v]'},
                {name:'play sound [... v] until done', openWith:'play sound [', closeWith:' v] until done'},
                {name:'stop all sounds', replaceWith:'stop all sounds'},
                // ---
                {name:'play drum (... v) for (0.25) beats', openWith:'play drum (', closeWith:' v) for (0.25) beats'},
                {name:'rest for (...) beats', openWith:'rest for (', closeWith:') beats'},
                // ---
                {name:'play note (... v) for (0.5) beats', openWith:'play note (', closeWith:' v) for (0.5) beats'},
                {name:'set instrument to (... v)', openWith:'set instrument to (', closeWith:' v)'},
                // ---
                {name:'change volume by (...)', openWith:'change volume by (', closeWith:')'},
                {name:'set volume to (...) %', openWith:'set volume to (', closeWith:') %'},
                {name:'(volume)', replaceWith:'(volume)'},
                // ---
                {name:'change tempo by (...)', openWith:'change tempo by (', closeWith:')'},
                {name:'set tempo to (...) bpm', openWith:'set tempo to (', closeWith:') bpm'},
                {name:'(tempo)', replaceWith:'(tempo)'},
            ]},

            {name:'Pen // category=pen', dropMenu:[
                {name:'clear', replaceWith:'clear'},
                // ---
                {name:'stamp', replaceWith:'stamp'},
                // ---
                {name:'pen down', replaceWith:'pen down'},
                {name:'pen up', replaceWith:'pen up'},
                // ---
                {name:'set pen color to [#f0f]', openWith:'set pen color to [#f0f', closeWith:']'},
                {name:'change pen color by (...)', openWith:'change pen color by (', closeWith:')'},
                {name:'set pen color to (...)', openWith:'set pen color to (', closeWith:')'},
                // ---
                {name:'change pen shade by (...)', openWith:'change pen shade by (', closeWith:')'},
                {name:'set pen shade to (...)', openWith:'set pen shade to (', closeWith:')'},
                // ---
                {name:'change pen size by (...)', openWith:'change pen size by (', closeWith:')'},
                {name:'set pen size to (...)', openWith:'set pen size to (', closeWith:')'},
            ]},

            {name:'Variables // category=variables', dropMenu:[
                {name:'(variable)', openWith:'(', closeWith:')'},
                {name:'set [... v] to [0]', openWith:'set [', closeWith:' v] to [0]'},
                {name:'change [... v] by (1)', openWith:'change [', closeWith:' v] by (1)'},
                {name:'show variable [... v]', openWith:'show variable [', closeWith:' v]'},
                {name:'hide variable [... v]', openWith:'hide variable [', closeWith:' v]'},
            ]},

            {name:'Lists // category=list', dropMenu:[
                {name:'(list) // category=list', openWith:'(', closeWith:')'},
                // ---
                {name:'add [...] to [list v]', openWith:'add [', closeWith:'] to [list v]'},
                // ---
                {name:'delete (... v) of [list v]', openWith:'delete (', closeWith:' v) of [list v]'},
                {name:'insert [...] at (1 v) of [list v]', openWith:'insert [', closeWith:'] at (1 v) of [list v]'},
                {name:'replace item (... v) of [list v] with [thing]', openWith:'replace item (', closeWith:' v) of [list v] with [thing]'},
                // ---
                {name:'(item (... v) of [list v])', openWith:'(item (', closeWith:' v) of [list v])'},
                {name:'(length of [... v])', openWith:'(length of [', closeWith:' v])'},
                {name:'<[... v] contains [thing]>', openWith:'<[', closeWith:' v] contains [thing]>'},
                // ---
                {name:'show list [... v]', openWith:'show list [', closeWith:' v]'},
                {name:'hide list [... v]', openWith:'hide list [', closeWith:' v]'},
            ]},

            {name:'Events // category=events', dropMenu:[
                {name:'when green flag clicked', replaceWith:'when green flag clicked'},
                {name:'when [... v] key pressed', openWith:'when [', closeWith:' v] key pressed'},
                {name:'when this sprite clicked', replaceWith:'when this sprite clicked'},
                {name:'when backdrop switches to [... v]', openWith:'when backdrop switches to [', closeWith:' v]'},
                // ---
                {name:'when [... v] > (20)', openWith:'when [', closeWith:' v] < (20)'},
                // ---
                {name:'when I receive [... v]', openWith:'when I receive [', closeWith:' v]'},
                {name:'broadcast [... v]', openWith:'broadcast [', closeWith:' v]'},
                {name:'broadcast [... v] and wait', openWith:'broadcast [', closeWith:' v] and wait'},
            ]},

            {name:'Control // category=control', dropMenu:[
                {name:'wait (...) secs', openWith:'wait (', closeWith:') secs'},
                // ---
                {name:'repeat (...)', openWith:'repeat (', closeWith:')\n    \nend'},
                // ---
                {name:'forever', openWith:'forever\n    ', closeWith:'\nend'},
                {name:'if <> then', openWith:'if <', closeWith:'> then\n    \nend'},
                {name:'else', replaceWith:'else'},
                {name:'wait until <>', openWith:'wait until <', closeWith:'>\n    \nend'},
                {name:'repeat until <>', openWith:'repeat until <', closeWith:'>\n    \nend'},
                // ---
                {name:'stop [... v]', openWith:'stop [', closeWith:' v]'},
                // ---
                {name:'when I start as a clone', replaceWith:'when I start as a clone'},
                {name:'create clone of [myself v]', openWith:'create clone of [myself', closeWith:' v]'},
                {name:'delete this clone', replaceWith:'delete this clone'},
            ]},

            {name:'Sensing // category=sensing', dropMenu:[
                {name:'&lt;touching [... v]?&gt;', openWith:'<touching [', closeWith:' v]?>'},
                {name:'&lt;touching color [#f0f]?&gt;', openWith:'<touching color [#f0f', closeWith:']?>'},
                {name:'&lt;color [#f0f] is touching [#0f0]?&gt;', openWith:'<color [#f0f', closeWith:'] is touching [#0f0]?>'},
                {name:'(distance to [... v])', openWith:'(distance to [', closeWith:' v])'},
                // ---
                {name:'ask [...] and wait', openWith:'ask [', closeWith:'] and wait'},
                {name:'(answer)', replaceWith:'(answer)'},
                // ---
                {name:'&lt;key [... v] pressed?&gt;', openWith:'<key [', closeWith:' v] pressed?>'},
                {name:'&lt;mouse down?&gt;', replaceWith:'<mouse down?>'},
                {name:'(mouse x)', replaceWith:'(mouse x)'},
                {name:'(mouse y)', replaceWith:'(mouse y)'},
                // ---
                {name:'(loudness)', replaceWith:'(loudness)'},
                // ---
                {name:'(video [... v] on [this sprite v])', openWith:'(video [', closeWith:' v] on [this sprite v])'},
                {name:'turn video [... v]', openWith:'turn video [', closeWith:' v]'},
                {name:'set video transparency to (...) %', openWith:'set video transparency to (', closeWith:') %'},
                // ---
                {name:'(timer)', replaceWith:'(timer)'},
                {name:'reset timer', replaceWith:'reset timer'},
                // ---
                {name:'([... v] of [Sprite1 v])', openWith:'([', closeWith:' v] of [Sprite1 v])'},
                // ---
                {name:'(current [... v])', openWith:'(current [', closeWith:' v])'},
                {name:'(days since 2000)', replaceWith:'(days since 2000)'},
                {name:'(username)', replaceWith:'(username)'},
            ]},

            {name:'Operators // category=operators', dropMenu:[
                {name:'(() + ())', openWith:'((', closeWith:') + ())'},
                {name:'(() - ())', openWith:'((', closeWith:') - ())'},
                {name:'(() * ())', openWith:'((', closeWith:') * ())'},
                {name:'(() / ())', openWith:'((', closeWith:') / ())'},
                // ---
                {name:'(pick random (...) to (10))', openWith:'(pick random (', closeWith:') to (10))'},
                // ---
                {name:'&lt;[] &lt; []&gt;', openWith:'<[', closeWith:'] < []>'},
                {name:'&lt;[] = []&gt;', openWith:'<[', closeWith:'] = []>'},
                {name:'&lt;[] &gt; []&gt;', openWith:'<[', closeWith:'] > []>'},
                // ---
                {name:'<<> and <>>', openWith:'<<', closeWith:'> and <>>'},
                {name:'<<> or <>>', openWith:'<<', closeWith:'> or <>>'},
                {name:'&lt;not <>>', openWith:'<not <', closeWith:'>>'},
                // ---
                {name:'(join [...] [world])', openWith:'(join [', closeWith:'] [world])'},
                {name:'(letter (...) of [world])', openWith:'(letter (', closeWith:') of [world])'},
                {name:'(length of [...])', openWith:'(length of [', closeWith:'])'},
                // ---
                {name:'(() mod ())', openWith:'((', closeWith:') mod ())'},
                {name:'(round (...))', openWith:'(round (', closeWith:'))'},
                // ---
                {name:'([sqrt v] of (9))', openWith:'([', closeWith:' v] of (9))'},
            ]},

            /*{name:'Extensions // category=purple', dropMenu:[
                {name:'', openWith:'when [', closeWith:' v]'},
                {name:'', openWith:'<sensor [', closeWith:' v]?>'},
                {name:'', openWith:'([', closeWith:' v] sensor value)'},
                // ---
                {name:'', openWith:'turn motor on for (', closeWith:') secs'},
                {name:'', openWith:'turn motor on'},
                {name:'', openWith:'turn motor off'},
                {name:'', openWith:'set motor power (', closeWith:')'},
                {name:'', openWith:'set motor direction [', closeWith:' v]'},
                // ---
                {name:'', openWith:'when distance < (', closeWith:')'},
                {name:'', openWith:'when tilt = (', closeWith:')'},
                {name:'', openWith:'(distance)'},
                {name:'', openWith:'(tilt)'},
            ]},*/

            {name:'Help! What is this? // category=grey', beforeInsert: function () { window.location = 'http://wiki.scratch.mit.edu/wiki/Block_Plugin/ForumHelp'; } }

        ]},
        {separator:'---------------' },
		{name:'Clean', className:"clean", replaceWith:function(markitup) { return markitup.selection.replace(/\[(.*?)\]/g, "") } },
		{name:'Preview', className:"preview", call:'preview' }
	],

    beforeInsert: function (h) {
        h.originalSelection = h.selection;
    },

    afterInsert: function (h) {
        if (!(h.hasOwnProperty('openWith') || h.hasOwnProperty('replaceWith'))
            || $.inArray(h.name, [
                'Bold', 'Italic', 'Underline', 'Stroke', 'Picture', 'Link',
                'Size', 'Big', 'Small', 'Bulleted list', 'Numeric list',
                'List item', 'Quotes', 'Smiles', 'Smile', 'Neutral', 'Sad',
                'Big smile', 'Yikes', 'Wink', 'Hmm', 'Tongue', 'Lol', 'Mad',
                'Roll', 'Cool', 'Clean', 'Preview']) > -1) {
            return;
        }

        var contents = $(h.textarea).attr('value'),
            cursor,
            originalCursor,
            lineStartCursor,
            OPEN_BRACKETS = "<([",
            CLOSE_BRACKETS = "])>";


        if('selectionStart' in h.textarea) {
            cursor = h.textarea.selectionStart;
        } else if('selection' in document) {
            h.textarea.focus();
            var sel = document.selection.createRange();
            var selLength = document.selection.createRange().text.length;
            sel.moveStart('character', -h.textarea.value.length);
            cursor = sel.text.length - selLength;
        }
        originalCursor = cursor;

        // Are we inserting inside a line?
        if (h.caretPosition > 0 && contents.charAt(h.caretPosition - 1) !== "\n") {
            var inserted = h.replaceWith || (h.openWith + (h.closeWith || ""));
            var open = h.replaceWith || h.openWith;

            if (h.originalSelection) {
                // Consume surrounding brackets.
                var testIndex = h.caretPosition,
                    endIndex = testIndex + inserted.length + h.originalSelection.length;
                var charBefore = contents.charAt(testIndex - 1),
                    charAfter = contents.charAt(endIndex);
                if (OPEN_BRACKETS.indexOf(charBefore) > -1 && CLOSE_BRACKETS.indexOf(charAfter) > -1) {
                    contents = (contents.slice(0, testIndex - 1) +
                                contents.slice(testIndex, endIndex) +
                                contents.slice(endIndex + 1));
                    originalCursor -= 1;
                }
            } else {
                contents = contents.slice(0, h.caretPosition) + contents.slice(h.caretPosition + inserted.length);

                if (contents.charAt(h.caretPosition) === "\n" && !contents.charAt(h.caretPosition - 1) === "\n") {
                    // At end of line. Insert newline
                    contents = contents.slice(0, h.caretPosition) + '\n' + inserted + contents.slice(h.caretPosition);
                    h.caretPosition += 1;
                    originalCursor += 1;
                } else {
                    // Inside line. Remove block and add on a new line.
                    if (OPEN_BRACKETS.indexOf(inserted.charAt(0)) === -1) { // stack block
                        // Look for newline
                        var eol = h.caretPosition;
                        while (contents.charAt(eol) !== "\n" && eol <= contents.length) {
                            eol += 1;
                        }

                        contents = contents.slice(0, eol) + '\n' + inserted + contents.slice(eol);
                        originalCursor = eol + open.length + 1;

                    } else { // reporter block
                        // Consume surrounding brackets.
                        var testIndex = h.caretPosition;
                        var charBefore = contents.charAt(testIndex - 1),
                            charAfter = contents.charAt(testIndex);
                        if (OPEN_BRACKETS.indexOf(charBefore) > -1 && CLOSE_BRACKETS.indexOf(charAfter) > -1) {
                            contents = contents.slice(0, testIndex - 1) + contents.slice(testIndex + 1);
                            testIndex -= 1;
                            originalCursor -= 1;
                        }

                        contents = contents.slice(0, testIndex) + inserted + contents.slice(testIndex);
                    }
                }
            }
        }

        // Look for scratchblocks tag
        cursor -= 15;
        while (!/\[\/?scratchblocks\]/.test(contents.slice(cursor, originalCursor)) && cursor >= 0) {
            cursor -= 1;
        }

        // Insert scratchblocks tag if needed
        if (!/\[scratchblocks\]/.test(contents.slice(cursor, originalCursor))) {
            contents = contents.slice(0, h.caretPosition) + '[scratchblocks]\n' + contents.slice(h.caretPosition);
            contents += '\n[/scratchblocks]';
            originalCursor += 16;
        }

        $(h.textarea).attr('value', contents);

        if (h.textarea.setSelectionRange) {
            h.textarea.focus();
            h.textarea.setSelectionRange(originalCursor, originalCursor);
        } else if (h.textarea.createTextRange) {
            var range = h.textarea.createTextRange();
            range.collapse(true);
            range.moveEnd('character', originalCursor);
            range.moveStart('character', originalCursor);
            range.select();
        }
    }
}
