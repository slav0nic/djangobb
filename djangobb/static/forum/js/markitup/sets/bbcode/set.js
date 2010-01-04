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
mySettings = {
	previewParserPath:	POST_PREVIEW_URL, // path to your BBCode parser
	markupSet: [
		{name:'Bold', key:'B', openWith:'[b]', closeWith:'[/b]'},
		{name:'Italic', key:'I', openWith:'[i]', closeWith:'[/i]'},
		{name:'Underline', key:'U', openWith:'[u]', closeWith:'[/u]'},
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
		{name:'Code', openWith:'[code]', closeWith:'[/code]'}, 
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
            {name:'Cool', openWith:':cool:'},
        ]},
		{name:'Clean', className:"clean", replaceWith:function(markitup) { return markitup.selection.replace(/\[(.*?)\]/g, "") } },
		{name:'Preview', className:"preview", call:'preview' }
	]
}