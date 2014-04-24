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
		{name:'Stroke', key:'S', openWith:'[s]', closeWith:'[/s]' },
		{separator:'---------------' },
		{name:'Picture', key:'P', replaceWith:'[img][![Url]!][/img]'},
		{name:'Link', key:'L', openWith:'[url=[![Url]!]]', closeWith:'[/url]', placeHolder:'Your text to link here...'},
		{separator:'---------------' },
		{name:'Size', key:'S', openWith:'', closeWith:'',
		dropMenu :[
			{name:'Big', openWith:'[size 32]', closeWith:'[/size]' },
			{name:'Small', openWith:'[size 10]', closeWith:'[/size]' }
		]},
		{separator:'---------------' },
		{name:'Bulleted list', openWith:'[list]\n', closeWith:'\n[/list]'},
		{name:'Numeric list', openWith:'[list=[![Starting number]!]]\n', closeWith:'\n[/list]'}, 
		{name:'List item', openWith:'[*] '},
		{separator:'---------------' },
		{name:'Quotes', openWith:'[quote]', closeWith:'[/quote]'},
		{name:'Code', openWith:'[code]', closeWith:'[/code]', dropMenu:[
		    // here we can list all languages which pygments support
		    // see 'short name' here: http://pygments.org/docs/lexers/
            {name:'Python', openWith:'[code python]', closeWith:'[/code]'}, 
            {name:'html', openWith:'[code html]', closeWith:'[/code]'}, 
            {name:'html+django', openWith:'[code html+django]', closeWith:'[/code]'}, 
            {name:'JavaScript', openWith:'[code javascript]', closeWith:'[/code]'}, 
            {name:'css', openWith:'[code css]', closeWith:'[/code]'}, 
            {name:'Bash', openWith:'[code bash]', closeWith:'[/code]'}, 
            {name:'MySQL', openWith:'[code mysql]', closeWith:'[/code]'}, 
            {name:'PostgreSQL', openWith:'[code postgres]', closeWith:'[/code]'}, 
            {name:'Apache config', openWith:'[code apacheconf]', closeWith:'[/code]'}, 
            {name:'INI files', openWith:'[code ini]', closeWith:'[/code]'}, 
        ]}, 
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
	{separator:'---------------' },
		{name:'Clean', className:"clean", replaceWith:function(markitup) { return markitup.selection.replace(/\[(.*?)\]/g, "") } },
		{name:'Preview', className:"preview", call:'preview' }
	]
}