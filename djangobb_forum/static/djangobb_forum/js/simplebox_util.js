if(typeof Box==="undefined"){
Box={};
}
Array.isArray=Array.isArray||function(o){
return Object.prototype.toString.call(o)==="[object Array]";
};
(function(K){
K.scripts={};
K.styles={};
K.getScripts=_1(_2,1);
K.getStyles=_1(_2,0);
function _2(){
var _3,ss,_4=null;
_3=Array.prototype.slice.call(arguments,0);
ss=_3.shift();
for(var i=_3.length-1;i>0;--i){
if(Array.isArray(_3[i])){
_4=_3.slice(i,i);
delete _3[i];
break;
}
}
if(_4){
(function(_5){
var _6=arguments.callee,t;
if(t=_5.shift()){
_2(ss,t,function(){
_6(_5);
});
}else{
_7(_3,ss);
}
})(_4);
}else{
_7(_3,ss);
}
};
function _7(_8,ss){
var t,s,_9,_a,_b,_c,_d;
_9=_8.shift();
if((t=_8[_8.length-1])&&typeof t=="function"){
_c=_8.pop();
}
if(t=_8.shift()){
_a=t;
}
if(t=_8.shift()){
_b=t;
}
if(_a){
K.scripts[_9]=_a;
}else{
_a=K.scripts[_9];
if(!_a){
return;
}
}
if(ss){
s=document.createElement("script");
s.setAttribute("type","text/javascript");
_c&&(s.onload=_c);
}else{
s=document.createElement("link");
s.setAttribute("rel","stylesheet");
}
document.getElementsByTagName("head")[0].appendChild(s);
t=_b?_a+_b:_a;
ss?(s.src=t):(s.href=t);
};
K.addEvent=(function(){
if(document.addEventListener){
return function(_e,_f,fn){
_e.addEventListener(_f,fn,false);
};
}else{
if(document.attachEvent){
return function(obj,_10,fn){
obj.attachEvent("on"+_10,fn);
};
}
}
})();
K.removeEvent=(function(){
if(document.removeEventListener){
return function(obj,_11,fn){
obj.removeEventListener(_11,fn,false);
};
}else{
if(document.detachEvent){
return function(obj,_12,fn){
obj.detachEvent("on"+_12,fn);
};
}
}
})();
K.$=function(obj){
return document.getElementById(obj);
};
function _13(obj){
return obj instanceof Object;
};
K.extend=function(){
var i,_14=true,_15,_16,_17;
_16=Array.prototype.slice.call(arguments,0);
typeof _16[0]==="boolean"&&(_14=_16.shift());
_15=_16.shift();
function _18(_19,_1a){
if(!_1a||!_19){
return;
}
for(i in _1a){
if(i in _19){
if(_14&&_13(_19[i])&&_13(_1a[i])){
_18(_19[i],_1a[i]);
}else{
_19[i]=_1a[i];
}
}else{
if(typeof _1a[i]!=="undefined"){
_19[i]=_1a[i];
}
}
}
};
while(_17=_16.shift()){
_18(_15,_17);
}
return _15;
};
K.contentLoad=function(fn){
if(document.addEventListener){
document.addEventListener("DOMContentLoaded",fn,false);
}else{
if(/MSIE/i.test(navigator.userAgent)){
document.write("<script id='__ie_onload' defer src='javascript:void(0);'></script>");
var _1b=document.getElementById("__ie_onload");
_1b.onreadystatechange=function(){
if(this.readyState=="complete"){
fn();
}
};
}else{
if(/WebKit/i.test(navigator.userAgent)){
var _1c=setInterval(function(){
if(/loaded|complete/.test(document.readyState)){
clearInterval(_1c);
fn();
}
},10);
}else{
window.onload=function(e){
fn();
};
}
}
}
};
K.createElement=function(tag,_1d){
var t=document.createElement(tag),ret;
ret=_1d?K.extend(t,_1d):t;
return ret;
};
K.getComputedStyleValue=function(_1e,_1f){
return window.getComputedStyle(_1e,null).getPropertyValue(_1f);
};
K.extendStyle=function(el,_20){
var i,_21={};
for(i in _20){
_21[i]=_20[i]+"px";
}
K.extend(el.style,_21);
};
K.fadeOut=_1(_22,0);
K.fadeIn=_1(_22,1);
function _22(io,el,_23,_24){
var _25=Array.prototype.slice.call(arguments,0),_26,t,cb;
if(_25.length==3&&typeof _25[2]=="function"){
_24=_25[2];
_23=null;
}
cb=function(){
_24&&_24();
};
if(io){
if(K.getComputedStyleValue(el,"display")!="none"){
cb();
return;
}
el.style.opacity=0;
el.style.display=el.getAttribute("data-display")||"block";
new Animate(el,"opacity",{to:1,time:_23,callback:function(){
_24();
}});
}else{
if((t=K.getComputedStyleValue(el,"display"))=="none"){
cb();
return;
}
el.setAttribute("data-display",t);
new Animate(el,"opacity",{to:0,time:_23,callback:function(){
el.style.display="none";
cb();
}});
}
};
function _1(){
var _27=Array.prototype.slice.call(arguments,0),fn=_27.shift();
return function(){
var io=Array.prototype.slice.call(arguments,0);
io=_27.concat(io);
return fn.apply(null,io);
};
};
})(Box);
function Animate(elm,_28,_29){
this.elm=elm;
this.prop=_28;
this.to=parseInt(_29.to);
this.from=typeof _29.from!="undefined"?_29.from:Box.getComputedStyleValue(elm,_28);
this.from=parseInt(this.from);
this.callback=_29.callback;
this.diff=this.to-this.from;
this.time=parseInt(_29.time)||Animate.timeShorts[_29.time]||400;
this.step=_29.step;
this.start();
};
Animate.timeShorts={slow:600,fast:200};
Animate.prototype={start:function(){
var _2a=this;
this.startTime=new Date();
this.timer=setInterval(function(){
_2a._animate.call(_2a);
},4);
return this;
},_animate:function(){
var _2b=new Date()-this.startTime,val,_2c;
if(_2b>=this.time){
this._setStyle(this.to);
typeof this.step=="function"&&this.step(1);
clearInterval(this.timer);
typeof this.callback=="function"&&this.callback();
return;
}
_2c=Math.floor((_2b/this.time)*100)/100;
val=this.diff*_2c+this.from;
this._setStyle(val);
typeof this.step=="function"&&this.step(_2c);
},_setStyle:function(val){
var _2d=this.elm.style;
switch(this.prop){
case "opacity":
_2d[this.prop]=val;
break;
default:
_2d[this.prop]=val+"px";
break;
}
}};

