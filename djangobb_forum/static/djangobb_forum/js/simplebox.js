var simplebox=(function(){
var _1,_2,_3,_4,_5,_6,_7,_8,_9=null,_a=false,_b,_c,_d,_e,_f,_10=1,_11=20,_12=new Image,fx={style:{}},_13,_14,_15,_16=/\.(jpg|gif|png|bmp|jpeg)(.*)?$/i,_17=/[^\.]\.(swf)\s*$/i,_18,_19=[],_1a={padding:10,margin:20,width:560,height:340,cyclic:false,overlayShow:true,hideOnOverlayClick:true,hideOnContentClick:false,swf:{wmode:"opaque"},h5video:{controls:"controls",preload:"metadata",autoplay:false},flashPlayer:"http://releases.flowplayer.org/swf/flowplayer-3.2.1.swf",titlePosition:"inside",titleShow:true,titleFormat:null,transitionIn:"fade",transitionOut:"fade",speedIn:500,speedOut:500,changeSpeed:500,changeFade:500,scrolling:"auto",autoScale:true,autoDimension:true,enableCenter:true,enableMouseWheel:true,showCloseButton:true,showNavArrows:true,enableEscapeButton:true,overlayColor:"#666",overlayOpacity:"0.3",preloadIndent:1};
function _1b(){
_5.style.display="none";
_12.onerror=_12.onload=null;
};
function _1c(){
if(_a){
return;
}
_a=true;
_1b();
_a=false;
};
function _1d(){
simplebox.start({content:"Sorry! the request cann't be reached"},{transitionIn:"none",transitionOut:"none"});
};
function _1e(){
var _1f=function(){
_4.innerHTML=_2.innerHTML="";
Box.fadeOut(_1,"fast",function(){
_a=false;
});
},t;
if(_a){
return;
}
_a=true;
_1b();
Box.removeEvent(document,"keydown",_54);
Box.removeEvent(window,"resize",_3e);
_6.style.display="none";
_7.style.display="none";
_8.style.display="none";
_4.style.overflow="hidden";
if(_9){
_9.parentNode.removeChild(_9);
_9=null;
}
if(_e.transitionOut=="fade"){
Box.fadeOut(_3,_1f);
}else{
if(_e.transitionOut=="elastic"){
t=_14;
_14=_13;
_13=t;
new Animate(fx,"fx",{from:0,to:1,step:_3a,time:_e.speedOut,callback:function(){
_3.style.display="none";
_1f();
}});
}else{
_3.style.display="none";
_1f();
}
}
};
function _20(){
var d=document.createDocumentFragment(),t=Box.createElement("div",{"id":"simplebox"});
d.appendChild(t);
_2=Box.createElement("div",{"id":"simple-tmp"});
t.appendChild(_2);
_5=_2.cloneNode(false);
_5.id="simple-loading";
_5.appendChild(document.createElement("div"));
t.appendChild(_5);
_1=_2.cloneNode(false);
_1.id="simple-overlay";
t.appendChild(_1);
_3=_2.cloneNode(false);
_3.id="simple-outer";
t.appendChild(_3);
_4=_2.cloneNode(false);
_4.id="simple-inner";
_3.appendChild(_4);
_6=Box.createElement("a",{"id":"simple-close"});
_3.appendChild(_6);
_7=Box.createElement("a",{"id":"simple-left"});
var _21=Box.createElement("span",{"id":"simple-left-ico","className":"simple-ico"});
_7.appendChild(_21);
_3.appendChild(_7);
_8=_7.cloneNode(true);
_8.id="simple-right";
_8.querySelector("span").id="simple-right-ico";
_3.appendChild(_8);
document.body.appendChild(d);
Box.addEvent(_6,"click",_1e);
Box.addEvent(_7,"click",_22);
Box.addEvent(_8,"click",_23);
Box.addEvent(_5,"click",_1c);
};
function _24(){
if(_a){
return;
}
_a=true;
_1b();
_e=Box.extend({},_d);
var obj=_b[_c],_25,_26,_27=_e.orig,t,arr;
typeof _27=="string"&&(_27=document.querySelector(_27));
obj.getElementsByTagName&&!_27&&(_e.orig=_27=obj.getElementsByTagName("img")[0]);
_e.title=obj.title||(_27&&(_27.title||_27.alt))||"";
_25=_e.href||obj.href||null;
if(_e.type){
_26=_e.type;
if(_26=="html"){
_25=_e.content;
}
}else{
if(_25){
if(_25.match(_16)){
_26="image";
}else{
if(_25.match(_17)){
_26="swf";
}
}
}
if(typeof _e.content!=="undefined"){
_26="html";
_25=_e.content;
}else{
if((t=_e.video)&&(arr=t.split(";"))&&arr.length>0){
var _28={mp4:"video/mp4; codecs=\"avc1.42E01E, mp4a.40.2\"",webm:"video/webm; codecs=\"vp8, vorbis\"",ogv:"video/ogg; codecs=\"theora, vorbis\"",ogg:"video/ogg; codecs=\"theora, vorbis\""},swf=[],_29,_2a=null;
_26="h5video";
_29=document.createElement("video");
document.body.appendChild(_29);
arr.forEach(function(el,_2b,arr){
var _2c=el.slice(-3),_2d;
if(_2c!="flv"&&(t=_28[_2c])){
if(_2c=="mp4"){
swf.push(el);
if(!_29.play){
swf.push(el);
return;
}
}
_2d=_29.canPlayType(t);
if((_2d=="probably"||_2d=="maybe")&&!_2a){
_2a="<source src=\""+el+"\" type='"+t+"'>";
}
}else{
swf.push(el);
}
});
swf.length>0&&(_25=swf[0]);
_2a&&(_25=_2a);
}
}
}
if(!_25||!_26){
_a=false;
return;
}
_e.href=_25;
_e.type=_26;
var str="",emb="",key,_2e;
switch(_26){
case "image":
_a=false;
_5a();
_12=new Image();
_12.onload=function(){
_12.onerror=null;
_12.onload=null;
_2f();
};
_12.onerror=_1d;
_12.src=_25;
break;
case "h5video":
if(_29.play&&_2a){
str+="<video id=\"simple-video\" ";
for(key in _e.h5video){
str+=key+"="+_e.h5video[key]+" ";
}
str+="width=\""+_e.width+"\" height=\""+_e.height+"\">";
str+=_2a;
str+="</video>";
_2.innerHTML=str;
document.body.removeChild(_29);
_30();
break;
}
if(swf.length>0){
document.body.removeChild(_29);
_e.swf["flashvars"]=_31();
_e.href=_e.flashPlayer;
}
case "swf":
str+="<object classid=\"clsid:d27cdb6e-ae6d-11cf-96b8-444553540000\" width=\""+_e.width+"\" height=\""+_e.height+"\"><param name=\"movie\" value=\""+_e.href+"\"></param>";
for(key in _e.swf){
str+="<param name=\""+key+"\" value='"+_e.swf[key]+"'></param>";
emb+=" "+key+"='"+_e.swf[key]+"'";
}
str+="<embed src=\""+_e.href+"\" type=\"application/x-shockwave-flash\" width=\""+_e.width+"\" height=\""+_e.height+"\""+emb+"></embed></object>";
_2.innerHTML=str;
_30();
break;
case "html":
_2.innerHTML=_e.href;
if(_e.autoDimension){
Box.extend(_2.style,{display:"block",position:"absolute"});
_e.width=parseInt(Box.getComputedStyleValue(_2,"width"));
_e.height=parseInt(Box.getComputedStyleValue(_2,"height"));
Box.extend(_2.style,{display:"none",position:"auto"});
}
_30();
}
};
function _31(){
var _32={},t,p;
p=_32["playlist"]=[];
(t=_e["h5video"]["poster"])&&p.push(t);
t={};
t.url=_e.href;
t.autoPlay=_e.h5video.autoplay;
t.autoBuffering=(_e.h5video.preload!=="none");
p.push(t);
return "config="+JSON.stringify(_32);
};
function _2f(){
_a=true;
_2.innerHTML="";
_e.width=_12.width;
_e.height=_12.height;
_12.alt=_e.title;
_12.id="simple-img";
_2.appendChild(_12);
_30();
};
function _30(){
var w,h,_33,_34=_e.fadeSpeed;
_5.style.display="none";
_33=Box.extend({},_14);
_14=_35();
_36();
w=_14.width-2*_e.padding;
h=_14.height-2*_e.padding-_15;
if(Box.getComputedStyleValue(_3,"display")!="none"){
_6.style.display="none";
_7.style.display="none";
_8.style.display="none";
Box.fadeOut(_4,_34,function(){
_4.style.overflow="hidden";
_4.innerHTML=_2.innerHTML;
_13={width:parseInt(_4.style.width),height:parseInt(_4.style.height),};
if(_13.width==w&&_13.height==h){
Box.fadeIn(_4,_34,function(){
Box.extendStyle(_3,_14);
_39();
});
}else{
function _37(_38){
Box.fadeIn(_4,_34,_39);
};
_13=_33;
new Animate(fx,"fx",{from:0,to:1,time:_e.changeSpeed,step:_3a,callback:_37});
}
});
return;
}
_13=_3b();
_4.innerHTML=_2.innerHTML;
if(_e.overlayShow){
_1.style.backgroundColor=_e.overlayColor;
_1.style.opacity=_e.overlayOpacity;
_1.style.display="block";
}
if(_e.transitionIn=="elastic"){
Box.extend(_4.style,{top:_e.padding+"px",left:_e.padding+"px",width:Math.max(_13.width-(_e.padding*2),1)+"px",height:Math.max(_13.height-(_e.padding*2),1)+"px"});
Box.extendStyle(_3,_13);
_3.style.opacity=1;
_3.style.display="block";
new Animate(fx,"fx",{from:0,to:1,step:_3a,time:_e.speedIn,callback:_39});
}else{
Box.extendStyle(_3,_14);
Box.extend(_4.style,{top:_e.padding+"px",left:_e.padding+"px",width:Math.max(_14.width-(_e.padding*2),1)+"px",height:Math.max(_14.height-(_e.padding*2)-_15,1)+"px"});
if(_e.transitionIn=="fade"){
Box.fadeIn(_3,_34,_39);
}else{
_3.style.opacity=1;
_3.style.display="block";
_39();
}
}
};
function _39(){
var _3c=_e.scrolling;
_3c=_3c=="auto"?(_e.type=="html"?"auto":"hidden"):(_3c=="yes"?"auto":"visible");
_4.style.overflow=_3c;
if(_9){
_9.style.display="block";
}
if(_e.showCloseButton){
_6.style.display="block";
}
if(_e.hideOnContentClick){
Box.removeEvent(_4,"click",_1e);
Box.addEvent(_4,"click",_1e);
}
if(_e.hideOnOverlayClick&&_e.overlayShow){
Box.removeEvent(_1,"click",_1e);
Box.addEvent(_1,"click",_1e);
}
_b.length>1&&_3d();
if(_e.enableCenter){
Box.addEvent(window,"resize",_3e);
}
_a=false;
_3f();
};
function _3a(_40){
var _41=Math.round(_13.width+(_14.width-_13.width)*_40),_42=Math.round(_13.height+(_14.height-_13.height)*_40),top=Math.round(_13.top+(_14.top-_13.top)*_40),_43=Math.round(_13.left+(_14.left-_13.left)*_40);
Box.extendStyle(_3,{width:_41,height:_42,left:_43,top:top});
_41=Math.max(_41-_e.padding*2,0);
_42=Math.max(_42-(_e.padding*2+(_15*_40)),0);
_4.style.width=_41+"px";
_4.style.height=_42+"px";
};
function _44(){
var de=document.documentElement;
return {"width":(window.innerWidth||(de&&de.clientWidth)||document.body.clientWidth),"height":(window.innerHeight||(de&&de.clientHeight)||document.body.clientHeight)};
};
function _45(){
var win=_44();
return [win.width,win.height,document.documentElement.scrollLeft||document.body.scrollLeft,document.documentElement.scrollTop||document.body.scrollTop];
};
function _46(elm){
var h,w,t=0,l=0;
h=elm.offsetHeight;
w=elm.offsetWidth;
do{
l+=elm.offsetLeft;
t+=elm.offsetTop;
}while(elm=elm.offsetParent);
return {width:w,height:h,left:l,top:t};
};
function _3b(){
var _47=_e.orig,_48={},pos,_49,p=_e.padding;
if(_47){
pos=_46(_47);
_48={width:(pos.width+(p*2)),height:(pos.height+(p*2)),top:(pos.top-p),left:(pos.left-p)};
}else{
_49=_45();
_48={width:1,height:1,top:_49[3]+_49[1]*0.5,left:_49[2]+_49[0]*0.5};
}
return _48;
};
function _35(){
var _4a=_45(),to={},_4b=_e.margin,_4c=_e.autoScale,_4d=_e.padding*2,_4e=(_e.margin+_11)*2,_4f=(_e.margin+_11)*2;
if(_e.width.toString().indexOf("%")>-1){
to.width=((_4a[0]*parseFloat(_e.width))/100)-(2*_11);
_4c=false;
}else{
to.width=_e.width+_4d;
}
if(_e.height.toString().indexOf("%")>-1){
to.height=((_4a[1]*parseFloat(_e.height))/100)-(2*_11);
_4c=false;
}else{
to.height=_e.height+_4d;
}
if(_4c&&(to.width>(_4a[0]-_4e)||to.height>(_4a[1]-_4f))){
if(_e.type=="image"){
_4e+=_4d;
_4f+=_4d;
var _50=Math.min(Math.min(_4a[0]-_4e,_e.width)/_e.width,Math.min(_4a[1]-_4f,_e.height)/_e.height);
to.width=Math.round(_50*(to.width-_4d))+_4d;
to.height=Math.round(_50*(to.height-_4d))+_4d;
}else{
to.width=Math.min(to.width,(_4a[0]-_4e));
to.height=Math.min(to.height,(_4a[1]-_4f));
}
}
to.left=_4a[2]+(_4a[0]-to.width)*0.5;
to.top=_4a[3]+(_4a[1]-to.height)*0.5;
if(_e.autoScale==false){
to.top=Math.max(_4a[3]+_4b,to.top);
to.left=Math.max(_4a[2]+_4b,to.left);
}
return to;
};
function _36(){
var t=_e.title,w,p=_e.padding;
if(_9){
_9.parentNode.removeChild(_9);
_9=null;
}
_15=0;
if(!_e.titleShow){
return;
}
if(!t){
return;
}
t=typeof (_e.titleFormat)==="function"?_e.titleFormat(t,_b,_c,_e):_51(t);
w=Math.max(_14.width-2*p,1);
_9=Box.createElement("div",{"id":"simple-title","innerHTML":t,"className":"simple-title-"+_e.titlePosition});
Box.extend(_9.style,{width:w+"px",paddingLeft:p+"px",paddingRight:p+"px"});
document.body.appendChild(_9);
switch(_e.titlePosition){
case "over":
_9.style.bottom=p+"px";
break;
default:
_15=_9.offsetHeight-_e.padding;
_14.height+=_15;
break;
}
_3.appendChild(_9);
_9.style.display="none";
};
function _51(_52){
var ret=false;
if(_52&&_52.length){
switch(_e.titlePosition){
case "over":
ret="<span id=\"simple-title-over\">"+_52+"</span>";
break;
default:
ret=_52;
break;
}
}
return ret;
};
function _3d(){
var _53=navigator.userAgent.match(/firefox/i)?"DOMMouseScroll":"mousewheel";
Box.addEvent(document,"keydown",_54);
if(_e.enableMouseWheel){
Box.removeEvent(_3,_53,_55);
Box.addEvent(_3,_53,_55);
}
if(!_e.showNavArrows){
return;
}
if((_e.cyclic&&_b.length>1)||_c!=0){
_7.style.display="block";
}
if((_e.cyclic&&_b.length>1)||_c!=(_b.length-1)){
_8.style.display="block";
}
};
function _55(e){
var _56;
e=e||window.event;
_56=e.wheelDelta?(e.wheelDelta/120):(-e.detail/3);
_56<0?_23():_22();
e.preventDefault();
};
function _3e(){
console.log(_45());
_13=_3b();
_14=_35();
if(_9){
_9.style.width=_14.width-2*_e.padding+"px";
if(_e.titlePosition=="inside"){
_15=_9.offsetHeight-_e.padding;
_14.height+=_15;
}
}
Box.extendStyle(_3,_14);
Box.extend(_4.style,{top:_e.padding+"px",left:_e.padding+"px",width:Math.max(_14.width-(_e.padding*2),1)+"px",height:Math.max(_14.height-(_e.padding*2)-_15,1)+"px"});
};
function _54(e){
var _57=e||window.event;
if(e.keyCode==27&&_e.enableEscapeButton){
e.preventDefault();
_1e();
}else{
if(e.keyCode==37){
e.preventDefault();
_22();
}else{
if(e.keyCode==39){
e.preventDefault();
_23();
}
}
}
};
function _22(){
return pos(_c-1);
};
function _23(){
return pos(_c+1);
};
function pos(pos){
if(_a){
return;
}
if(pos>-1&&_b.length>pos){
_c=pos;
_24();
}
if(_e.cyclic&&_b.length>1&&pos<0){
_c=_b.length-1;
_24();
}
if(_e.cyclic&&_b.length>1&&pos>=_b.length){
_c=0;
_24();
}
};
function _58(){
if(_5.style.display!="block"){
clearInterval(_f);
return;
}
_5.childNodes[0].style.top=(_10*-40)+"px";
_10=(_10+1)%12;
};
function _3f(){
var i,l,t=_b.length,img,_59;
for(i=_c+1,l=_c+_e.preloadIndent;i<=l;++i){
if(i>t-1){
break;
}
_59=_b[i].href;
if(typeof _59!=="undefined"&&!_19[i]&&_59.match(_16)){
img=new Image();
img.src=_b[i].href;
_19[i]=img;
}
}
for(i=l+1;i<t-1;++i){
delete _19[i];
}
for(i=_c-1,l=_c-_e.preloadIndent;i>=l;i--){
if(i<0){
break;
}
_59=_b[i].href;
if(typeof _59!=="undefined"&&!_19[i]&&_59.match(_16)){
img=new Image();
img.src=_b[i].href;
_19[i]=img;
}
}
for(i=0;i<l;++i){
delete _19[i];
}
};
function _5a(){
clearInterval(_f);
_5.style.display="block";
_f=setInterval(_58,66);
};
return {init:_20,start:function(el,_5b,now){
var _5c,_5d;
if(typeof el==="string"){
_5c=document.querySelectorAll(el);
_5c=Array.prototype.slice.call(_5c,0);
}else{
_5c=!Array.isArray(el)&&[el];
}
if(arguments.length==2&&typeof arguments[1]=="boolean"){
now=_5b;
_5b=null;
}
if(_5c.length==0){
return;
}
function go(_5e,_5f){
_b=_5f;
_c=_5e;
_d=Box.extend({},_1a);
var _60=el.attributes,_61,t;
if(_60){
for(var i=0,l=_60.length;i<l;++i){
_61=_60[i].nodeName;
if(_61.indexOf("data-")==0){
_61=_61.split("-");
t=_61.pop();
for(var j=1,_62=_61.length,_63=_d;j<_62;++j){
_63[_61[j]]&&(_63=_63[_61[j]]);
}
_63[t]=_60[i].nodeValue;
}
}
}
_5b&&(Box.extend(_d,_5b));
_d["width"]=parseInt(_d["width"]);
_d["height"]=parseInt(_d["height"]);
_24();
};
if(now){
el=_5c[0];
go(0,_5c);
return;
}
_5c.forEach(function(m,_64,arr){
Box.addEvent(m,"click",function(e){
el=m;
e.preventDefault();
go(_64,arr);
});
});
}};
})();

