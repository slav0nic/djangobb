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
		{name:'Жирный', key:'B', openWith:'[b]', closeWith:'[/b]'},
		{name:'Курсив', key:'I', openWith:'[i]', closeWith:'[/i]'},
		{name:'Подчеркнутый', key:'U', openWith:'[u]', closeWith:'[/u]'},
		{name:'Зачеркнутый', key:'S', openWith:'[s]', closeWith:'[/s]' },
		{name:'Споилер', openWith:'[spoiler]', closeWith:'[/spoiler]'},
		{name:'Споилерблок', openWith:'[spoilerblock]', closeWith:'[/spoilerblock]'},
		{separator:'---------------' },
		{name:'Размер шрифта', key:'S', openWith:'', closeWith:'',
		dropMenu :[
			{name:'Большой', openWith:'[size 32]', closeWith:'[/size]' },
			{name:'Маленький', openWith:'[size 10]', closeWith:'[/size]' }
		]},
		{separator:'---------------' },
		{name:'Список', openWith:'', closeWith:'', dropMenu:[
			{name:'Простой', openWith:'[list]\n', closeWith:'\n[/list]'},
			{name:'Нумерованный', openWith:'[list=[![Starting number]!]]\n', closeWith:'\n[/list]'}, 
			{name:'Элемент', openWith:'[*] '},
		]},
		{separator:'---------------' },
		{name:'Вставить ссылку', key:'L', openWith:'[url=[![Url]!]]', closeWith:'[/url]', placeHolder:'Введите свой текст здесь'},
		{name:'Вставить изображение', key:'P', replaceWith:'[img][![Url]!][/img]'},
		{name:'Вставить ссылку с YouToBe', key:'Y', replaceWith:'[youtobe][![Url]!][/youtobe]'},
		{separator:'---------------' },
		{name:'Цитата', openWith:'[quote]', closeWith:'[/quote]'},
		//{name:'Code', openWith:'[code]', closeWith:'[/code]', dropMenu:[
		    // here we can list all languages which pygments support
		    // see 'short name' here: http://pygments.org/docs/lexers/
            //{name:'Python', openWith:'[code python]', closeWith:'[/code]'}, 
            //{name:'html', openWith:'[code html]', closeWith:'[/code]'}, 
            //{name:'html+django', openWith:'[code html+django]', closeWith:'[/code]'}, 
            //{name:'JavaScript', openWith:'[code javascript]', closeWith:'[/code]'}, 
            //{name:'css', openWith:'[code css]', closeWith:'[/code]'}, 
            //{name:'Bash', openWith:'[code bash]', closeWith:'[/code]'}, 
            //{name:'MySQL', openWith:'[code mysql]', closeWith:'[/code]'}, 
            //{name:'PostgreSQL', openWith:'[code postgres]', closeWith:'[/code]'}, 
            //{name:'Apache config', openWith:'[code apacheconf]', closeWith:'[/code]'}, 
            //{name:'INI files', openWith:'[code ini]', closeWith:'[/code]'}, 
        //]}, 
        {name:'Смайлы', openWith:'', closeWith:'', dropMenu:[
            {name:'Smile', openWith:':)'}, 
            {name:'Poker Face', openWith:':|'}, 
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
	//{separator:'---------------' },
		//{name:'Очистить', className:"clean", replaceWith:function(markitup) { return markitup.selection.replace(/\[(.*?)\]/g, "") } },
		//{name:'Предпросмотр', className:"preview", call:'preview' }
	]
}