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
	{separator:'---------------' },
    {name:'Scratchblocks', openWith:'', closeWith:'', className:'scratchblocks-button', dropMenu:[]}, // Generated in scratchblocks2/markitup.js
    {separator:'---------------' },
		{name:'Clean', className:"clean", replaceWith:function(markitup) { return markitup.selection.replace(/\[(.*?)\]/g, "") } },
		{name:'Preview', className:"preview", call:'preview' }
	],
}
