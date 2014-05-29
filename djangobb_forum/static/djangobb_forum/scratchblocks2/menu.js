/* This should be loaded:
 *   - after scratchblocks2.js
 *   - after markitup.js
 *   - after scratchblocks2._currentLanguage is set
 *   - before markItUp() is run
 *   - before any scratchblocks2.parse() calls
 */

// TODO (function($){

function capitalise(text) {
    return text[0].toUpperCase() + text.slice(1);
}

var scratchblocksMenu;
mySettings.markupSet.forEach(function(item) {
    if (item.name === 'Scratchblocks') scratchblocksMenu = item;
});

var language = scratchblocks2.languages[scratchblocks2._currentLanguage];

var specs = [["move %n steps"," ",1,10],["turn @turnRight %n degrees"," ",1,15],["turn @turnLeft %n degrees"," ",1,15],["point in direction %d.direction"," ",1,90],["point towards %m.spriteOrMouse"," ",1,""],["go to x:%n y:%n"," ",1],["go to %m.spriteOrMouse"," ",1,"mouse-pointer"],["glide %n secs to x:%n y:%n"," ",1],["change x by %n"," ",1,10],["set x to %n"," ",1,0],["change y by %n"," ",1,10],["set y to %n"," ",1,0],["if on edge, bounce"," ",1],["set rotation style %m.rotationStyle"," ",1,"left-right"],["x position","r",1],["y position","r",1],["direction","r",1],["say %s for %n secs"," ",2,"Hello!",2],["say %s"," ",2,"Hello!"],["think %s for %n secs"," ",2,"Hmm...",2],["think %s"," ",2,"Hmm..."],["show"," ",2],["hide"," ",2],["switch costume to %m.costume"," ",2,"costume1"],["next costume"," ",2],["switch backdrop to %m.backdrop"," ",2,"backdrop1"],["change %m.effect effect by %n"," ",2,"color",25],["set %m.effect effect to %n"," ",2,"color",0],["clear graphic effects"," ",2],["change size by %n"," ",2,10],["set size to %n%"," ",2,100],["go to front"," ",2],["go back %n layers"," ",2,1],["costume #","r",2],["backdrop name","r",2],["size","r",2],["switch backdrop to %m.backdrop"," ",102,"backdrop1"],["switch backdrop to %m.backdrop and wait"," ",102,"backdrop1"],["next backdrop"," ",102],["change %m.effect effect by %n"," ",102,"color",25],["set %m.effect effect to %n"," ",102,"color",0],["clear graphic effects"," ",102],["backdrop name","r",102],["backdrop #","r",102],["play sound %m.sound"," ",3,"pop"],["play sound %m.sound until done"," ",3,"pop"],["stop all sounds"," ",3],["play drum %d.drum for %n beats"," ",3,1,0.2],["rest for %n beats"," ",3,0.2],["play note %d.note for %n beats"," ",3,60,0.5],["set instrument to %d.instrument"," ",3,1],["change volume by %n"," ",3,-10],["set volume to %n%"," ",3,100],["volume","r",3],["change tempo by %n"," ",3,20],["set tempo to %n bpm"," ",3,60],["tempo","r",3],["clear"," ",4],["stamp"," ",4],["pen down"," ",4],["pen up"," ",4],["set pen color to %c"," ",4],["change pen color by %n"," ",4],["set pen color to %n"," ",4,0],["change pen shade by %n"," ",4],["set pen shade to %n"," ",4,50],["change pen size by %n"," ",4,1],["set pen size to %n"," ",4,1],["clear"," ",104],["when @greenFlag clicked","h",5],["when %m.key key pressed","h",5,"space"],["when this sprite clicked","h",5],["when backdrop switches to %m.backdrop","h",5,"backdrop1"],["when %m.triggerSensor > %n","h",5,"loudness",10],["when I receive %m.broadcast","h",5,""],["broadcast %m.broadcast"," ",5,""],["broadcast %m.broadcast and wait"," ",5,""],["wait %n secs"," ",6,1],["repeat %n","c",6,10],["forever","cf",6],["if %b then","c",6],["if %b then","e",6],["wait until %b"," ",6],["repeat until %b","c",6],["stop %m.stop","f",6,"all"],["when I start as a clone","h",6],["create clone of %m.spriteOnly"," ",6],["delete this clone","f",6],["wait %n secs"," ",106,1],["repeat %n","c",106,10],["forever","cf",106],["if %b then","c",106],["if %b then","e",106],["wait until %b"," ",106],["repeat until %b","c",106],["stop %m.stop","f",106,"all"],["create clone of %m.spriteOnly"," ",106],["touching %m.touching?","b",7,""],["touching color %c?","b",7],["color %c is touching %c?","b",7],["distance to %m.spriteOrMouse","r",7,""],["ask %s and wait"," ",7,"What's your name?"],["answer","r",7],["key %m.key pressed?","b",7,"space"],["mouse down?","b",7],["mouse x","r",7],["mouse y","r",7],["loudness","r",7],["video %m.videoMotionType on %m.stageOrThis","r",7,"motion"],["turn video %m.videoState"," ",7,"on"],["set video transparency to %n%"," ",7,50],["timer","r",7],["reset timer"," ",7],["%m.attribute of %m.spriteOrStage","r",7],["current %m.timeAndDate","r",7,"minute"],["days since 2000","r",7],["username","r",7],["ask %s and wait"," ",107,"What's your name?"],["answer","r",107],["key %m.key pressed?","b",107,"space"],["mouse down?","b",107],["mouse x","r",107],["mouse y","r",107],["loudness","r",107],["video %m.videoMotionType on %m.stageOrThis","r",107,"motion","Stage"],["turn video %m.videoState"," ",107,"on"],["set video transparency to %n%"," ",107,50],["timer","r",107],["reset timer"," ",107],["%m.attribute of %m.spriteOrStage","r",107],["current %m.timeAndDate","r",107,"minute"],["days since 2000","r",107],["username","r",107],["%n + %n","r",8,"",""],["%n - %n","r",8,"",""],["%n * %n","r",8,"",""],["%n / %n","r",8,"",""],["pick random %n to %n","r",8,1,10],["%s < %s","b",8,"",""],["%s = %s","b",8,"",""],["%s > %s","b",8,"",""],["%b and %b","b",8],["%b or %b","b",8],["not %b","b",8],["join %s %s","r",8,"hello ","world"],["letter %n of %s","r",8,1,"world"],["length of %s","r",8,"world"],["%n mod %n","r",8,"",""],["round %n","r",8,""],["%m.mathOp of %n","r",8,"sqrt",9],["set %m.var to %s"," ",9],["change %m.var by %n"," ",9],["show variable %m.var"," ",9],["hide variable %m.var"," ",9],["add %s to %m.list"," ",12],["delete %d.listDeleteItem of %m.list"," ",12],["insert %s at %d.listItem of %m.list"," ",12],["replace item %d.listItem of %m.list with %s"," ",12],["item %d.listItem of %m.list","r",12],["length of %m.list","r",12],["%m.list contains %s","b",12],["show list %m.list"," ",12],["hide list %m.list"," ",12]];

var foo = '';

var spec_shapes = {
    'b': '<_>',
    's': '[_]',
    'n': '(_)',
    'd': '(_ v)',
    'm': '[_ v]',
    'c': '[#ff0088]',
};

var shape_ids = {
    'r': '(_)',
    'b': '<_>',
};

var category_ids = {
    1:  "motion",
    2:  "looks",
    3:  "sound",
    4:  "pen",
    5:  "events",
    6:  "control",
    7:  "sensing",
    8:  "operators",
    9:  "variables",
    12: "list",

    102: "looks",
    104: "pen",
    106: "control",
    107: "sensing",
};

// TODO translate palette names

var currentCategory = null;
var currentSubMenu = null;
var doneBlockText = [];

specs.forEach(function(spec) {
    var text = spec[0],
        shape = shape_ids[spec[1]],
        category = category_ids[spec[2]],
        defaults = spec.slice(3);

    if (doneBlockText.indexOf(text) > -1) return;
    doneBlockText.push(text);

    var blockid = text.replace(/%.(?:\.[A-z]+)?/g, '_')
                      .replace('@greenFlag', '@green-flag')
                      .replace('@turnLeft', '@arrow-cw')
                      .replace('@turnRight', '@arrow-ccw');
    var info = scratchblocks2.block_info_by_id[blockid];
    if (info.flag && info.flag !== 'cstart') return;

    var args = [];
    var pat = /%(.)(?:\.[A-z]+)?/g;
    var match;
    while (match = pat.exec(text)) {
        args.push(spec_shapes[match[1]]);
        if (args.length > 1 && match[1] == 'c') {
            args[0] = '[#00ff00]';
            args[1] = '[#0000ff]';
        }
    }
    defaults[0] = '...';
    args = args.map(function(item) {
        var fallback = (item[0] === '(') ? '0' : ' ';
        return item.replace('_', defaults.shift() || fallback);
    });

    var output = language.blocks[blockid] || blockid;
    if (blockid.indexOf('@') > -1) {
        for (otherid in language.aliases) {
            if (language.aliases[otherid] === blockid) {
                output = otherid;
            }
        }
    }


    var preview = '';
    output = output.replace(/_/g, ' _ ').replace(/ +/g, ' ').trim();
    if (blockid === '_ of _' || blockid === 'length of _') {
        preview = ' :: ' + category;
    } else if ((scratchblocks2.find_block(output, []) || {}).category !== category) {
        output += ' :: ' + category;
    }

    while (args.length) {
        output = output.replace('_', args.shift());
    }

    if (currentCategory != category) {
        foo += '\n// ' + category + '\n\n';
        currentCategory = category;

        name = (language.palette[capitalise(category)] ||
                language.palette[category]);
        currentSubMenu = {name: name + ' :: ' + category,
                          dropMenu: []};
        scratchblocksMenu.dropMenu.push(currentSubMenu);

        if (category === 'variables') {
            currentSubMenu.dropMenu.push({
                name:'(variable)',
                openWith:'(',
                // placeHolder: 'variable',
                closeWith:')',
            });
        } else if (category === 'list') {
            currentSubMenu.dropMenu.push({
                name:'(list :: list)',
                openWith:'(',
                // placeHolder: 'list',
                closeWith:' :: list)',
            });
        }
    }

    var preview = output.replace('<...>', '<>') + preview;

    if (shape) {
        output = shape.replace('_', output);
        preview = shape.replace('_', preview);
    }

    if (info.flag === 'cstart') output += '\n    |\nend\n';
    if (info.shape === 'hat') output = '\n' + output;

    preview = preview.replace(/&/g, '&amp;')
                     .replace(/</g, '&lt;')
                     .replace(/>/g, '&gt;');

    // Put the cursor at the first input if possible,
    // otherwise the first C mouth,
    // otherwise at the end.
    var splitIndex = output.indexOf('...');
    var offset = 3;
    if (splitIndex === -1) {
        splitIndex = output.indexOf('|');
        offset = 1;
    } else {
        output = output.replace('|', '');
    }
    if (splitIndex > -1) {
        currentSubMenu.dropMenu.push({
            name: preview,
            openWith: output.slice(0, splitIndex),
            closeWith: output.slice(splitIndex + offset)
        });
        foo += output.slice(0, splitIndex) + output.slice(splitIndex + offset) + '\n';
    } else {
        currentSubMenu.dropMenu.push({
            name: preview,
            replaceWith: output,
        });
        foo += output + '\n';
    }

});

// TODO this whole thing stinks. Just rewrite scratchblocks to use proper block specs!

scratchblocksMenu.dropMenu.push({
    name: language.palette['More Blocks'] + ' :: custom',
    dropMenu: [
        {name: language.define, openWith: language.define + ' '},
        {name: '(input :: custom-arg)', openWith: '(', closeWith: ')'},
    ],
});

scratchblocksMenu.dropMenu.push({
    name: (language.palette.Tips || 'Help') + ' :: grey',
    beforeInsert: function () {
        window.location = 'http://wiki.scratch.mit.edu/wiki/Block_Plugin/ForumHelp';
    },
});


mySettings.beforeInsert = function(h) {
    h.originalSelection = h.selection;
};

mySettings.afterInsert = function(h) {
    if (!(h.hasOwnProperty('openWith') || h.hasOwnProperty('replaceWith'))
        || $.inArray(h.name, [
            'Bold', 'Italic', 'Underline', 'Stroke', 'Picture', 'Link',
            'Size', 'Big', 'Small', 'Bulleted list', 'Numeric list',
            'List item', 'Quotes', 'Smiles', 'Smile', 'Neutral', 'Sad',
            'Big smile', 'Yikes', 'Wink', 'Hmm', 'Tongue', 'Lol', 'Mad',
            'Roll', 'Cool', 'Clean', 'Preview',
            'Paste browser / operating system versions']) > -1) {
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
};
