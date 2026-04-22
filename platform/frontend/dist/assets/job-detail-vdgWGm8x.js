import{a as xe,d as K,h as s,N as Ce,m as T,aE as ke,aF as Se,aG as $e,aH as ze,aI as qe,o as Z,g as R,i as F,u as Ne,j as ie,l as we,aB as ce,aJ as Ge,aK as Fe,a3 as Ue,D as Ve,r as j,aL as He,aM as Je,P as I,J as G,K as r,U as S,R as g,L as e,F as U,ad as Q,Z as C,ab as E,aD as se,M as $,O as o,Q as M,aN as he,H as Xe,aa as Ke,X as Ye,T as te,W as Ze}from"./index-DKfkuiLi.js";import{a as Qe}from"./applications-C9GHbAuo.js";import{r as re}from"./replays-BrsPPtbD.js";import{r as et}from"./recordings-CXuYwPgF.js";import{t as tt}from"./testcases-CANJB1fH.js";import{f as ae}from"./format-Adq5_zH5.js";import{_ as rt}from"./SubCallPanel.vue_vue_type_script_setup_true_lang-Dviuc8ux.js";import{N as lt}from"./Alert-cz0mTpc-.js";import{u as st,N as W}from"./Space-C_ahS7-l.js";import{N as q,a as ot}from"./Select-Dc2P8y1a.js";import{N as oe,a as J}from"./Grid-DUchxvYI.js";import{_ as Re}from"./_plugin-vue_export-helper-DlAUqK2U.js";import{b as it,p as at}from"./recording-C9VFCHLc.js";import{f as Y}from"./get-C9z6N27c.js";import{u as nt}from"./index-BZmDg5FO.js";import{N as ct,a as me}from"./BreadcrumbItem-zIVv4wM_.js";import{N as ne,a as A}from"./DescriptionsItem-BjVNAIQv.js";import{N as le}from"./Statistic-BycnHVZv.js";import{N as ut}from"./DataTable-Ck9AFGkd.js";import{a as dt,N as ve}from"./Tabs-zmZKvq6Q.js";import"./CollapseItem-C0K8k6QH.js";import"./Tooltip-Cx9wBadY.js";import"./Dropdown-BMHBmLUg.js";import"./Add-Dit9hlKf.js";function ft(l){const{infoColor:x,successColor:h,warningColor:_,errorColor:v,textColor2:n,progressRailColor:p,fontSize:y,fontWeight:b}=l;return{fontSize:y,fontSizeCircle:"28px",fontWeightCircle:b,railColor:p,railHeight:"8px",iconSizeCircle:"36px",iconSizeLine:"18px",iconColor:x,iconColorInfo:x,iconColorSuccess:h,iconColorWarning:_,iconColorError:v,textColorCircle:n,textColorLineInner:"rgb(255, 255, 255)",textColorLineOuter:n,fillColor:x,fillColorInfo:x,fillColorSuccess:h,fillColorWarning:_,fillColorError:v,lineBgProcessing:"linear-gradient(90deg, rgba(255, 255, 255, .3) 0%, rgba(255, 255, 255, .5) 100%)"}}const pt={common:xe,self:ft};function gt(l){const{opacityDisabled:x,heightTiny:h,heightSmall:_,heightMedium:v,heightLarge:n,heightHuge:p,primaryColor:y,fontSize:b}=l;return{fontSize:b,textColor:y,sizeTiny:h,sizeSmall:_,sizeMedium:v,sizeLarge:n,sizeHuge:p,color:y,opacitySpinning:x}}const yt={common:xe,self:gt},ht={success:s(ze,null),error:s($e,null),warning:s(Se,null),info:s(ke,null)},mt=K({name:"ProgressCircle",props:{clsPrefix:{type:String,required:!0},status:{type:String,required:!0},strokeWidth:{type:Number,required:!0},fillColor:[String,Object],railColor:String,railStyle:[String,Object],percentage:{type:Number,default:0},offsetDegree:{type:Number,default:0},showIndicator:{type:Boolean,required:!0},indicatorTextColor:String,unit:String,viewBoxWidth:{type:Number,required:!0},gapDegree:{type:Number,required:!0},gapOffsetDegree:{type:Number,default:0}},setup(l,{slots:x}){const h=T(()=>{const n="gradient",{fillColor:p}=l;return typeof p=="object"?`${n}-${qe(JSON.stringify(p))}`:n});function _(n,p,y,b){const{gapDegree:z,viewBoxWidth:D,strokeWidth:m}=l,a=50,d=0,i=a,c=0,P=2*a,B=50+m/2,N=`M ${B},${B} m ${d},${i}
      a ${a},${a} 0 1 1 ${c},${-P}
      a ${a},${a} 0 1 1 ${-c},${P}`,k=Math.PI*2*a,O={stroke:b==="rail"?y:typeof l.fillColor=="object"?`url(#${h.value})`:y,strokeDasharray:`${Math.min(n,100)/100*(k-z)}px ${D*8}px`,strokeDashoffset:`-${z/2}px`,transformOrigin:p?"center":void 0,transform:p?`rotate(${p}deg)`:void 0};return{pathString:N,pathStyle:O}}const v=()=>{const n=typeof l.fillColor=="object",p=n?l.fillColor.stops[0]:"",y=n?l.fillColor.stops[1]:"";return n&&s("defs",null,s("linearGradient",{id:h.value,x1:"0%",y1:"100%",x2:"100%",y2:"0%"},s("stop",{offset:"0%","stop-color":p}),s("stop",{offset:"100%","stop-color":y})))};return()=>{const{fillColor:n,railColor:p,strokeWidth:y,offsetDegree:b,status:z,percentage:D,showIndicator:m,indicatorTextColor:a,unit:d,gapOffsetDegree:i,clsPrefix:c}=l,{pathString:P,pathStyle:B}=_(100,0,p,"rail"),{pathString:N,pathStyle:k}=_(D,b,n,"fill"),O=100+y;return s("div",{class:`${c}-progress-content`,role:"none"},s("div",{class:`${c}-progress-graph`,"aria-hidden":!0},s("div",{class:`${c}-progress-graph-circle`,style:{transform:i?`rotate(${i}deg)`:void 0}},s("svg",{viewBox:`0 0 ${O} ${O}`},v(),s("g",null,s("path",{class:`${c}-progress-graph-circle-rail`,d:P,"stroke-width":y,"stroke-linecap":"round",fill:"none",style:B})),s("g",null,s("path",{class:[`${c}-progress-graph-circle-fill`,D===0&&`${c}-progress-graph-circle-fill--empty`],d:N,"stroke-width":y,"stroke-linecap":"round",fill:"none",style:k}))))),m?s("div",null,x.default?s("div",{class:`${c}-progress-custom-content`,role:"none"},x.default()):z!=="default"?s("div",{class:`${c}-progress-icon`,"aria-hidden":!0},s(Ce,{clsPrefix:c},{default:()=>ht[z]})):s("div",{class:`${c}-progress-text`,style:{color:a},role:"none"},s("span",{class:`${c}-progress-text__percentage`},D),s("span",{class:`${c}-progress-text__unit`},d))):null)}}}),vt={success:s(ze,null),error:s($e,null),warning:s(Se,null),info:s(ke,null)},bt=K({name:"ProgressLine",props:{clsPrefix:{type:String,required:!0},percentage:{type:Number,default:0},railColor:String,railStyle:[String,Object],fillColor:[String,Object],status:{type:String,required:!0},indicatorPlacement:{type:String,required:!0},indicatorTextColor:String,unit:{type:String,default:"%"},processing:{type:Boolean,required:!0},showIndicator:{type:Boolean,required:!0},height:[String,Number],railBorderRadius:[String,Number],fillBorderRadius:[String,Number]},setup(l,{slots:x}){const h=T(()=>Y(l.height)),_=T(()=>{var p,y;return typeof l.fillColor=="object"?`linear-gradient(to right, ${(p=l.fillColor)===null||p===void 0?void 0:p.stops[0]} , ${(y=l.fillColor)===null||y===void 0?void 0:y.stops[1]})`:l.fillColor}),v=T(()=>l.railBorderRadius!==void 0?Y(l.railBorderRadius):l.height!==void 0?Y(l.height,{c:.5}):""),n=T(()=>l.fillBorderRadius!==void 0?Y(l.fillBorderRadius):l.railBorderRadius!==void 0?Y(l.railBorderRadius):l.height!==void 0?Y(l.height,{c:.5}):"");return()=>{const{indicatorPlacement:p,railColor:y,railStyle:b,percentage:z,unit:D,indicatorTextColor:m,status:a,showIndicator:d,processing:i,clsPrefix:c}=l;return s("div",{class:`${c}-progress-content`,role:"none"},s("div",{class:`${c}-progress-graph`,"aria-hidden":!0},s("div",{class:[`${c}-progress-graph-line`,{[`${c}-progress-graph-line--indicator-${p}`]:!0}]},s("div",{class:`${c}-progress-graph-line-rail`,style:[{backgroundColor:y,height:h.value,borderRadius:v.value},b]},s("div",{class:[`${c}-progress-graph-line-fill`,i&&`${c}-progress-graph-line-fill--processing`],style:{maxWidth:`${l.percentage}%`,background:_.value,height:h.value,lineHeight:h.value,borderRadius:n.value}},p==="inside"?s("div",{class:`${c}-progress-graph-line-indicator`,style:{color:m}},x.default?x.default():`${z}${D}`):null)))),d&&p==="outside"?s("div",null,x.default?s("div",{class:`${c}-progress-custom-content`,style:{color:m},role:"none"},x.default()):a==="default"?s("div",{role:"none",class:`${c}-progress-icon ${c}-progress-icon--as-text`,style:{color:m}},z,D):s("div",{class:`${c}-progress-icon`,"aria-hidden":!0},s(Ce,{clsPrefix:c},{default:()=>vt[a]}))):null)}}});function be(l,x,h=100){return`m ${h/2} ${h/2-l} a ${l} ${l} 0 1 1 0 ${2*l} a ${l} ${l} 0 1 1 0 -${2*l}`}const _t=K({name:"ProgressMultipleCircle",props:{clsPrefix:{type:String,required:!0},viewBoxWidth:{type:Number,required:!0},percentage:{type:Array,default:[0]},strokeWidth:{type:Number,required:!0},circleGap:{type:Number,required:!0},showIndicator:{type:Boolean,required:!0},fillColor:{type:Array,default:()=>[]},railColor:{type:Array,default:()=>[]},railStyle:{type:Array,default:()=>[]}},setup(l,{slots:x}){const h=T(()=>l.percentage.map((n,p)=>`${Math.PI*n/100*(l.viewBoxWidth/2-l.strokeWidth/2*(1+2*p)-l.circleGap*p)*2}, ${l.viewBoxWidth*8}`)),_=(v,n)=>{const p=l.fillColor[n],y=typeof p=="object"?p.stops[0]:"",b=typeof p=="object"?p.stops[1]:"";return typeof l.fillColor[n]=="object"&&s("linearGradient",{id:`gradient-${n}`,x1:"100%",y1:"0%",x2:"0%",y2:"100%"},s("stop",{offset:"0%","stop-color":y}),s("stop",{offset:"100%","stop-color":b}))};return()=>{const{viewBoxWidth:v,strokeWidth:n,circleGap:p,showIndicator:y,fillColor:b,railColor:z,railStyle:D,percentage:m,clsPrefix:a}=l;return s("div",{class:`${a}-progress-content`,role:"none"},s("div",{class:`${a}-progress-graph`,"aria-hidden":!0},s("div",{class:`${a}-progress-graph-circle`},s("svg",{viewBox:`0 0 ${v} ${v}`},s("defs",null,m.map((d,i)=>_(d,i))),m.map((d,i)=>s("g",{key:i},s("path",{class:`${a}-progress-graph-circle-rail`,d:be(v/2-n/2*(1+2*i)-p*i,n,v),"stroke-width":n,"stroke-linecap":"round",fill:"none",style:[{strokeDashoffset:0,stroke:z[i]},D[i]]}),s("path",{class:[`${a}-progress-graph-circle-fill`,d===0&&`${a}-progress-graph-circle-fill--empty`],d:be(v/2-n/2*(1+2*i)-p*i,n,v),"stroke-width":n,"stroke-linecap":"round",fill:"none",style:{strokeDasharray:h.value[i],strokeDashoffset:0,stroke:typeof b[i]=="object"?`url(#gradient-${i})`:b[i]}})))))),y&&x.default?s("div",null,s("div",{class:`${a}-progress-text`},x.default())):null)}}}),xt=Z([R("progress",{display:"inline-block"},[R("progress-icon",`
 color: var(--n-icon-color);
 transition: color .3s var(--n-bezier);
 `),F("line",`
 width: 100%;
 display: block;
 `,[R("progress-content",`
 display: flex;
 align-items: center;
 `,[R("progress-graph",{flex:1})]),R("progress-custom-content",{marginLeft:"14px"}),R("progress-icon",`
 width: 30px;
 padding-left: 14px;
 height: var(--n-icon-size-line);
 line-height: var(--n-icon-size-line);
 font-size: var(--n-icon-size-line);
 `,[F("as-text",`
 color: var(--n-text-color-line-outer);
 text-align: center;
 width: 40px;
 font-size: var(--n-font-size);
 padding-left: 4px;
 transition: color .3s var(--n-bezier);
 `)])]),F("circle, dashboard",{width:"120px"},[R("progress-custom-content",`
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 display: flex;
 align-items: center;
 justify-content: center;
 `),R("progress-text",`
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 display: flex;
 align-items: center;
 color: inherit;
 font-size: var(--n-font-size-circle);
 color: var(--n-text-color-circle);
 font-weight: var(--n-font-weight-circle);
 transition: color .3s var(--n-bezier);
 white-space: nowrap;
 `),R("progress-icon",`
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 display: flex;
 align-items: center;
 color: var(--n-icon-color);
 font-size: var(--n-icon-size-circle);
 `)]),F("multiple-circle",`
 width: 200px;
 color: inherit;
 `,[R("progress-text",`
 font-weight: var(--n-font-weight-circle);
 color: var(--n-text-color-circle);
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 display: flex;
 align-items: center;
 justify-content: center;
 transition: color .3s var(--n-bezier);
 `)]),R("progress-content",{position:"relative"}),R("progress-graph",{position:"relative"},[R("progress-graph-circle",[Z("svg",{verticalAlign:"bottom"}),R("progress-graph-circle-fill",`
 stroke: var(--n-fill-color);
 transition:
 opacity .3s var(--n-bezier),
 stroke .3s var(--n-bezier),
 stroke-dasharray .3s var(--n-bezier);
 `,[F("empty",{opacity:0})]),R("progress-graph-circle-rail",`
 transition: stroke .3s var(--n-bezier);
 overflow: hidden;
 stroke: var(--n-rail-color);
 `)]),R("progress-graph-line",[F("indicator-inside",[R("progress-graph-line-rail",`
 height: 16px;
 line-height: 16px;
 border-radius: 10px;
 `,[R("progress-graph-line-fill",`
 height: inherit;
 border-radius: 10px;
 `),R("progress-graph-line-indicator",`
 background: #0000;
 white-space: nowrap;
 text-align: right;
 margin-left: 14px;
 margin-right: 14px;
 height: inherit;
 font-size: 12px;
 color: var(--n-text-color-line-inner);
 transition: color .3s var(--n-bezier);
 `)])]),F("indicator-inside-label",`
 height: 16px;
 display: flex;
 align-items: center;
 `,[R("progress-graph-line-rail",`
 flex: 1;
 transition: background-color .3s var(--n-bezier);
 `),R("progress-graph-line-indicator",`
 background: var(--n-fill-color);
 font-size: 12px;
 transform: translateZ(0);
 display: flex;
 vertical-align: middle;
 height: 16px;
 line-height: 16px;
 padding: 0 10px;
 border-radius: 10px;
 position: absolute;
 white-space: nowrap;
 color: var(--n-text-color-line-inner);
 transition:
 right .2s var(--n-bezier),
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 `)]),R("progress-graph-line-rail",`
 position: relative;
 overflow: hidden;
 height: var(--n-rail-height);
 border-radius: 5px;
 background-color: var(--n-rail-color);
 transition: background-color .3s var(--n-bezier);
 `,[R("progress-graph-line-fill",`
 background: var(--n-fill-color);
 position: relative;
 border-radius: 5px;
 height: inherit;
 width: 100%;
 max-width: 0%;
 transition:
 background-color .3s var(--n-bezier),
 max-width .2s var(--n-bezier);
 `,[F("processing",[Z("&::after",`
 content: "";
 background-image: var(--n-line-bg-processing);
 animation: progress-processing-animation 2s var(--n-bezier) infinite;
 `)])])])])])]),Z("@keyframes progress-processing-animation",`
 0% {
 position: absolute;
 left: 0;
 top: 0;
 bottom: 0;
 right: 100%;
 opacity: 1;
 }
 66% {
 position: absolute;
 left: 0;
 top: 0;
 bottom: 0;
 right: 0;
 opacity: 0;
 }
 100% {
 position: absolute;
 left: 0;
 top: 0;
 bottom: 0;
 right: 0;
 opacity: 0;
 }
 `)]),Ct=Object.assign(Object.assign({},ie.props),{processing:Boolean,type:{type:String,default:"line"},gapDegree:Number,gapOffsetDegree:Number,status:{type:String,default:"default"},railColor:[String,Array],railStyle:[String,Array],color:[String,Array,Object],viewBoxWidth:{type:Number,default:100},strokeWidth:{type:Number,default:7},percentage:[Number,Array],unit:{type:String,default:"%"},showIndicator:{type:Boolean,default:!0},indicatorPosition:{type:String,default:"outside"},indicatorPlacement:{type:String,default:"outside"},indicatorTextColor:String,circleGap:{type:Number,default:1},height:Number,borderRadius:[String,Number],fillBorderRadius:[String,Number],offsetDegree:Number}),kt=K({name:"Progress",props:Ct,setup(l){const x=T(()=>l.indicatorPlacement||l.indicatorPosition),h=T(()=>{if(l.gapDegree||l.gapDegree===0)return l.gapDegree;if(l.type==="dashboard")return 75}),{mergedClsPrefixRef:_,inlineThemeDisabled:v}=Ne(l),n=ie("Progress","-progress",xt,pt,l,_),p=T(()=>{const{status:b}=l,{common:{cubicBezierEaseInOut:z},self:{fontSize:D,fontSizeCircle:m,railColor:a,railHeight:d,iconSizeCircle:i,iconSizeLine:c,textColorCircle:P,textColorLineInner:B,textColorLineOuter:N,lineBgProcessing:k,fontWeightCircle:O,[ce("iconColor",b)]:V,[ce("fillColor",b)]:H}}=n.value;return{"--n-bezier":z,"--n-fill-color":H,"--n-font-size":D,"--n-font-size-circle":m,"--n-font-weight-circle":O,"--n-icon-color":V,"--n-icon-size-circle":i,"--n-icon-size-line":c,"--n-line-bg-processing":k,"--n-rail-color":a,"--n-rail-height":d,"--n-text-color-circle":P,"--n-text-color-line-inner":B,"--n-text-color-line-outer":N}}),y=v?we("progress",T(()=>l.status[0]),p,l):void 0;return{mergedClsPrefix:_,mergedIndicatorPlacement:x,gapDeg:h,cssVars:v?void 0:p,themeClass:y==null?void 0:y.themeClass,onRender:y==null?void 0:y.onRender}},render(){const{type:l,cssVars:x,indicatorTextColor:h,showIndicator:_,status:v,railColor:n,railStyle:p,color:y,percentage:b,viewBoxWidth:z,strokeWidth:D,mergedIndicatorPlacement:m,unit:a,borderRadius:d,fillBorderRadius:i,height:c,processing:P,circleGap:B,mergedClsPrefix:N,gapDeg:k,gapOffsetDegree:O,themeClass:V,$slots:H,onRender:ee}=this;return ee==null||ee(),s("div",{class:[V,`${N}-progress`,`${N}-progress--${l}`,`${N}-progress--${v}`],style:x,"aria-valuemax":100,"aria-valuemin":0,"aria-valuenow":b,role:l==="circle"||l==="line"||l==="dashboard"?"progressbar":"none"},l==="circle"||l==="dashboard"?s(mt,{clsPrefix:N,status:v,showIndicator:_,indicatorTextColor:h,railColor:n,fillColor:y,railStyle:p,offsetDegree:this.offsetDegree,percentage:b,viewBoxWidth:z,strokeWidth:D,gapDegree:k===void 0?l==="dashboard"?75:0:k,gapOffsetDegree:O,unit:a},H):l==="line"?s(bt,{clsPrefix:N,status:v,showIndicator:_,indicatorTextColor:h,railColor:n,fillColor:y,railStyle:p,percentage:b,processing:P,indicatorPlacement:m,unit:a,fillBorderRadius:i,railBorderRadius:d,height:c},H):l==="multiple-circle"?s(_t,{clsPrefix:N,strokeWidth:D,railColor:n,fillColor:y,railStyle:p,viewBoxWidth:z,percentage:b,showIndicator:_,circleGap:B},H):null)}}),St=Z([Z("@keyframes spin-rotate",`
 from {
 transform: rotate(0);
 }
 to {
 transform: rotate(360deg);
 }
 `),R("spin-container",`
 position: relative;
 `,[R("spin-body",`
 position: absolute;
 top: 50%;
 left: 50%;
 transform: translateX(-50%) translateY(-50%);
 `,[Ge()])]),R("spin-body",`
 display: inline-flex;
 align-items: center;
 justify-content: center;
 flex-direction: column;
 `),R("spin",`
 display: inline-flex;
 height: var(--n-size);
 width: var(--n-size);
 font-size: var(--n-size);
 color: var(--n-color);
 `,[F("rotate",`
 animation: spin-rotate 2s linear infinite;
 `)]),R("spin-description",`
 display: inline-block;
 font-size: var(--n-font-size);
 color: var(--n-text-color);
 transition: color .3s var(--n-bezier);
 margin-top: 8px;
 `),R("spin-content",`
 opacity: 1;
 transition: opacity .3s var(--n-bezier);
 pointer-events: all;
 `,[F("spinning",`
 user-select: none;
 -webkit-user-select: none;
 pointer-events: none;
 opacity: var(--n-opacity-spinning);
 `)])]),$t={small:20,medium:18,large:16},zt=Object.assign(Object.assign(Object.assign({},ie.props),{contentClass:String,contentStyle:[Object,String],description:String,size:{type:[String,Number],default:"medium"},show:{type:Boolean,default:!0},rotate:{type:Boolean,default:!0},spinning:{type:Boolean,validator:()=>!0,default:void 0},delay:Number}),He),_e=K({name:"Spin",props:zt,slots:Object,setup(l){const{mergedClsPrefixRef:x,inlineThemeDisabled:h}=Ne(l),_=ie("Spin","-spin",St,yt,l,x),v=T(()=>{const{size:b}=l,{common:{cubicBezierEaseInOut:z},self:D}=_.value,{opacitySpinning:m,color:a,textColor:d}=D,i=typeof b=="number"?Je(b):D[ce("size",b)];return{"--n-bezier":z,"--n-opacity-spinning":m,"--n-size":i,"--n-color":a,"--n-text-color":d}}),n=h?we("spin",T(()=>{const{size:b}=l;return typeof b=="number"?String(b):b[0]}),v,l):void 0,p=st(l,["spinning","show"]),y=j(!1);return Ve(b=>{let z;if(p.value){const{delay:D}=l;if(D){z=window.setTimeout(()=>{y.value=!0},D),b(()=>{clearTimeout(z)});return}}y.value=p.value}),{mergedClsPrefix:x,active:y,mergedStrokeWidth:T(()=>{const{strokeWidth:b}=l;if(b!==void 0)return b;const{size:z}=l;return $t[typeof z=="number"?"medium":z]}),cssVars:h?void 0:v,themeClass:n==null?void 0:n.themeClass,onRender:n==null?void 0:n.onRender}},render(){var l,x;const{$slots:h,mergedClsPrefix:_,description:v}=this,n=h.icon&&this.rotate,p=(v||h.description)&&s("div",{class:`${_}-spin-description`},v||((l=h.description)===null||l===void 0?void 0:l.call(h))),y=h.icon?s("div",{class:[`${_}-spin-body`,this.themeClass]},s("div",{class:[`${_}-spin`,n&&`${_}-spin--rotate`],style:h.default?"":this.cssVars},h.icon()),p):s("div",{class:[`${_}-spin-body`,this.themeClass]},s(Fe,{clsPrefix:_,style:h.default?"":this.cssVars,stroke:this.stroke,"stroke-width":this.mergedStrokeWidth,radius:this.radius,scale:this.scale,class:`${_}-spin`}),p);return(x=this.onRender)===null||x===void 0||x.call(this),h.default?s("div",{class:[`${_}-spin-container`,this.themeClass],style:this.cssVars},s("div",{class:[`${_}-spin-content`,this.active&&`${_}-spin-content--spinning`,this.contentClass],style:this.contentStyle},h),s(Ue,{name:"fade-in-transition"},{default:()=>this.active?y:null})):y}}),Nt={style:{"font-weight":"600"}},wt={style:{color:"#666","font-size":"13px"}},Rt={key:0,class:"diff-summary"},Pt={key:0,class:"field-label"},Dt={key:1,class:"code-block compact"},It={key:1,class:"empty-side"},Ot={key:0,class:"field-label"},Bt={key:1,class:"code-block compact"},At={key:1,class:"empty-side"},Tt=K({__name:"SubCallDiffPanel",props:{pairs:{},replayed:{}},setup(l){function x(a){if(a==null)return"-";if(typeof a=="string")try{return JSON.stringify(JSON.parse(a),null,2)}catch{return a}return JSON.stringify(a,null,2)}function h(a){if(typeof a!="string")return a;const d=a.trim();if(!d||!(d.startsWith("{")&&d.endsWith("}")||d.startsWith("[")&&d.endsWith("]")))return a;try{return JSON.parse(d)}catch{return a}}function _(a){if(typeof a=="number"&&Number.isFinite(a))return a;if(typeof a!="string")return null;const d=a.trim();if(!/^[+-]?\d+(\.\d+)?$/.test(d))return null;const i=Number(d);return Number.isFinite(i)?i:null}function v(a,d){const i=h(a),c=h(d);if(Array.isArray(i)&&Array.isArray(c))return i.length===c.length&&i.every((N,k)=>v(N,c[k]));if(i!==null&&c!==null&&typeof i=="object"&&typeof c=="object"&&!Array.isArray(i)&&!Array.isArray(c)){const N=Object.keys(i).sort(),k=Object.keys(c).sort();return N.length!==k.length||N.some((O,V)=>O!==k[V])?!1:N.every(O=>v(i[O],c[O]))}const P=_(i),B=_(c);return P!==null&&B!==null?P===B:i===c}function n(a,d,i="response"){const c=h(a),P=h(d);if(v(c,P))return[];if(Array.isArray(c)&&Array.isArray(P)){const B=Math.max(c.length,P.length),N=[];for(let k=0;k<B;k+=1){const O=`${i}[${k}]`;if(k>=c.length||k>=P.length){N.push(O);continue}N.push(...n(c[k],P[k],O))}return N}if(c!==null&&P!==null&&typeof c=="object"&&typeof P=="object"&&!Array.isArray(c)&&!Array.isArray(P)){const B=Array.from(new Set([...Object.keys(c),...Object.keys(P)])).sort(),N=[];for(const k of B){const O=`${i}.${k}`,V=Object.prototype.hasOwnProperty.call(c,k),H=Object.prototype.hasOwnProperty.call(P,k);if(!V||!H){N.push(O);continue}N.push(...n(c[k],P[k],O))}return N}return[i]}function p(a){if(!a.recorded||!a.replayed)return[];const d=n(a.recorded.response,a.replayed.response);return d.length?d:["response"]}function y(a){var i,c;const d=((i=a.recorded)==null?void 0:i.operation)||((c=a.replayed)==null?void 0:c.operation)||"";return d.length>60?d.slice(0,60)+"…":d}function b(a){return a.side==="recorded_only"||a.side==="replayed_only"?"#f0a020":a.response_matched===!1?"#d03050":"#18a058"}function z(a){return a.side==="recorded_only"||a.side==="replayed_only"?"warning":a.response_matched===!1?"error":"success"}function D(a){return a.side==="recorded_only"?"仅录制侧":a.side==="replayed_only"?"仅回放侧":a.response_matched===!1?"响应差异":"一致"}function m(a){const d=(a||"").toLowerCase();return d.includes("mysql")||d.includes("jdbc")?"warning":d.includes("redis")?"info":"default"}return(a,d)=>(C(),I("div",null,[l.pairs.length?(C(),G(e(W),{key:1,vertical:"",size:12},{default:r(()=>[(C(!0),I(U,null,Q(l.pairs,i=>(C(),G(e(E),{key:i.index,size:"small",style:se({borderLeft:`3px solid ${b(i)}`})},{header:r(()=>[o(e(W),{align:"center",size:8},{default:r(()=>[$("span",Nt,"#"+g(i.index),1),o(e(q),{size:"small",type:m(i.type)},{default:r(()=>[S(g(i.type||"未知"),1)]),_:2},1032,["type"]),$("span",wt,g(y(i)),1)]),_:2},1024)]),"header-extra":r(()=>[o(e(q),{type:z(i),size:"small"},{default:r(()=>[S(g(D(i)),1)]),_:2},1032,["type"])]),default:r(()=>[i.side==="both"&&i.response_matched===!1?(C(),I("div",Rt,[d[0]||(d[0]=$("div",{class:"field-label"},"差异字段",-1)),o(e(W),{size:6,wrap:""},{default:r(()=>[(C(!0),I(U,null,Q(p(i),c=>(C(),G(e(q),{key:c,type:"error",size:"small",style:{"font-family":"monospace"}},{default:r(()=>[S(g(c),1)]),_:2},1024))),128))]),_:2},1024)])):M("",!0),o(e(oe),{cols:2,"x-gap":12},{default:r(()=>[o(e(J),null,{default:r(()=>[d[2]||(d[2]=$("div",{class:"col-title"},"录制侧",-1)),i.recorded?(C(),I(U,{key:0},[i.recorded.operation?(C(),I("div",Pt,"操作")):M("",!0),i.recorded.operation?(C(),I("pre",Dt,g(i.recorded.operation),1)):M("",!0),d[1]||(d[1]=$("div",{class:"field-label"},"响应",-1)),$("pre",{class:he(["code-block",{diff:i.side==="both"&&i.response_matched===!1}])},g(x(i.recorded.response)),3)],64)):(C(),I("div",It,"— 仅回放侧有此调用 —"))]),_:2},1024),o(e(J),null,{default:r(()=>[d[4]||(d[4]=$("div",{class:"col-title"},"回放侧",-1)),i.replayed?(C(),I(U,{key:0},[i.replayed.operation?(C(),I("div",Ot,"操作")):M("",!0),i.replayed.operation?(C(),I("pre",Bt,g(i.replayed.operation),1)):M("",!0),d[3]||(d[3]=$("div",{class:"field-label"},"响应",-1)),$("pre",{class:he(["code-block",{diff:i.side==="both"&&i.response_matched===!1}])},g(x(i.replayed.response)),3)],64)):(C(),I("div",At,"— 仅录制侧有此调用 —"))]),_:2},1024)]),_:2},1024)]),_:2},1032,["style"]))),128))]),_:1})):(C(),G(e(lt),{key:0,type:"default","show-icon":!1,style:{color:"#999"}},{default:r(()=>[S(g(l.replayed.length===0?"Agent 未上报子调用（回放时 AREX Agent 可能未启动或未配置录制模式）":"暂无子调用数据"),1)]),_:1}))]))}}),Lt=Re(Tt,[["__scopeId","data-v-2543995c"]]),jt={style:{color:"#18a058","font-size":"28px","font-weight":"bold"}},Wt={style:{color:"#d03050","font-size":"28px","font-weight":"bold"}},Et={class:"analysis-card"},Mt={class:"analysis-icon"},qt={class:"analysis-label"},Gt={class:"analysis-pct"},Ft={class:"code-block"},Ut={class:"code-block"},Vt={style:{"margin-top":"12px"}},Ht={class:"code-block compact"},Jt={key:0},Xt={style:{"margin-left":"8px","font-size":"12px"}},Kt={key:1},Yt={style:{"font-size":"13px",color:"#555","margin-bottom":"8px"}},Zt={key:1,class:"code-block compact"},Qt=K({__name:"job-detail",setup(l){const x=Ye(),h=Ze(),_=nt(),v=Number(x.params.jobId),n=j(null),p=j("-"),y=j([]),b=j(!1),z=j(null),D=j(!1),m=j(null),a=j(!1),d=j(null),i=j(null),c=j(null),P=j(""),B=j(null),N=j(!1),k=T(()=>!n.value||!n.value.total?0:n.value.passed/n.value.total*100),O=T(()=>{var f;const u=(f=m.value)==null?void 0:f.assertion_results;if(!u)return[];try{const t=JSON.parse(u);return Array.isArray(t)?t:[]}catch{return[]}}),V=[{key:"ENVIRONMENT",label:"环境问题",icon:"🌐",color:"#f0a020"},{key:"DATA_ISSUE",label:"数据问题",icon:"📝",color:"#2080f0"},{key:"BUG",label:"代码缺陷",icon:"🐛",color:"#d03050"},{key:"PERFORMANCE",label:"性能问题",icon:"⚡",color:"#8a2be2"},{key:"UNKNOWN",label:"未知",icon:"❓",color:"#999"}],H=T(()=>{var f;const u=((f=d.value)==null?void 0:f.categories)||{};return V.map(t=>{var w,L;return{...t,count:((w=u[t.key])==null?void 0:w.count)||0,percentage:((L=u[t.key])==null?void 0:L.percentage)||0}})}),ee={DONE:"success",RUNNING:"info",FAILED:"error",PENDING:"default",CANCELLED:"warning"},Pe={DONE:"已完成",RUNNING:"运行中",FAILED:"存在失败",PENDING:"待执行",CANCELLED:"已取消"},De={PASS:"success",FAIL:"error",ERROR:"warning",TIMEOUT:"warning",PENDING:"default"},Ie={PASS:"通过",FAIL:"失败",ERROR:"异常",TIMEOUT:"超时",PENDING:"待执行"},ue={status_mismatch:"状态码不一致",response_diff:"响应内容差异",assertion_failed:"断言失败",performance:"性能超限",timeout:"请求超时",connection_error:"连接异常",mock_error:"Mock 异常"},Oe=[{label:"通过",value:"PASS"},{label:"失败",value:"FAIL"},{label:"异常",value:"ERROR"},{label:"超时",value:"TIMEOUT"}];function de(u){return u==null?"#999":u<=.1?"#18a058":u<=.5?"#f0a020":"#d03050"}const Be=[{title:"接口",key:"request_uri",render:u=>s("div",{style:"line-height:1.6"},[s("div",[s("b",{style:"margin-right:4px;color:#666"},u.request_method||"GET"),s("span",u.request_uri||"-")]),u.transaction_code?s("div",{style:"display:inline-block;background:#e8f0fe;color:#1a73e8;border-radius:4px;padding:1px 7px;font-size:12px;margin-top:2px;font-weight:500"},u.transaction_code):null])},{title:"来源录制",key:"source_recording_id",width:170,render:u=>u.source_recording_id?s(W,{size:6,align:"center"},()=>[s(q,{type:u.use_sub_invocation_mocks?"success":"default",size:"small"},()=>u.use_sub_invocation_mocks?"Mock 开启":"Mock 关闭"),s("span",`#${u.source_recording_id}${u.source_recording_sub_call_count!=null?` / 子调用 ${u.source_recording_sub_call_count}`:""}`)]):s("span",{style:"color:#ccc"},"-")},{title:"状态",key:"status",width:80,render:u=>s(q,{type:De[u.status]??"default",size:"small"},()=>Ie[u.status]||u.status)},{title:"失败分类",key:"failure_category",width:120,render:u=>u.failure_category?s("span",ue[u.failure_category]||u.failure_category):s("span",{style:"color:#ccc"},"-")},{title:"Diff Score",key:"diff_score",width:100,render:u=>u.diff_score==null?s("span",{style:"color:#ccc"},"-"):s("span",{style:`color:${de(u.diff_score)};font-weight:bold`},u.diff_score.toFixed(3))},{title:"状态码",key:"actual_status_code",width:80,render:u=>{var f;return s("span",((f=u.actual_status_code)==null?void 0:f.toString())||"-")}},{title:"耗时",key:"latency_ms",width:80,render:u=>s("span",u.latency_ms!=null?`${u.latency_ms}ms`:"-")},{title:"时间",key:"created_at",width:145,render:u=>s("span",{style:"font-size:12px;color:#999"},ae(u.created_at))},{title:"对比",key:"actions",width:70,render:u=>s(te,{size:"tiny",type:"primary",ghost:!0,onClick:()=>Le(u)},()=>"对比")}];function Ae(u){if(!u)return"-";try{return JSON.stringify(JSON.parse(u),null,2)}catch{return u}}function fe(u){return u||"-"}function pe(u){if(!u)return null;const f=u.match(/差异字段\s+(.+)$/);return f?f[1].split(",").map(t=>t.trim()).filter(Boolean):null}function Te(u){return u.replace(/差异字段.+$/,"").trim().replace(/:$/,"").trim()}function Le(u){m.value=u,D.value=!0,We(u),je(u.id)}async function je(u){B.value=null,N.value=!0;try{const f=await re.getSubCallDiff(u);B.value=f.data}catch{B.value=null}finally{N.value=!1}}async function We(u){if(i.value=null,c.value=null,P.value="",!!u.test_case_id)try{const f=await tt.get(u.test_case_id);if(i.value=f.data,f.data.source_recording_id){const t=await et.getRecording(f.data.source_recording_id);c.value=t.data,P.value=it(at(t.data.sub_calls))}}catch{i.value=null,c.value=null,P.value=""}}async function Ee(){var u,f;try{const t=await re.getReport(v),w=new Blob([t.data],{type:"text/html;charset=utf-8"}),L=URL.createObjectURL(w),X=document.createElement("a");X.href=L,X.download=`replay_report_${v}.html`,document.body.appendChild(X),X.click(),document.body.removeChild(X),setTimeout(()=>URL.revokeObjectURL(L),1e4)}catch(t){_.error(((f=(u=t.response)==null?void 0:u.data)==null?void 0:f.detail)||"导出报告失败")}}async function Me(){if(!(!n.value||n.value.failed===0&&n.value.errored===0)){a.value=!0;try{const u=await re.getAnalysis(v);d.value=u.data}catch{d.value=null}finally{a.value=!1}}}async function ge(){var u,f;try{const t=await re.get(v);if(n.value=t.data,t.data.application_id!=null){const w=await Qe.get(t.data.application_id);p.value=w.data.name}else p.value="-"}catch(t){_.error(((f=(u=t.response)==null?void 0:u.data)==null?void 0:f.detail)||"加载回放任务失败")}await Promise.all([ye(),Me()])}async function ye(){var u,f;b.value=!0;try{const t={limit:200};z.value&&(t.status=z.value);const w=await re.getResults(v,t);y.value=w.data}catch(t){y.value=[],_.error(((f=(u=t.response)==null?void 0:u.data)==null?void 0:f.detail)||"加载结果详情失败")}finally{b.value=!1}}return Xe(()=>{ge()}),(u,f)=>(C(),I(U,null,[o(e(W),{vertical:"",size:16},{default:r(()=>[o(e(W),{justify:"space-between",align:"center"},{default:r(()=>[o(e(ct),null,{default:r(()=>[o(e(me),{onClick:f[0]||(f[0]=t=>e(h).push("/replay/history"))},{default:r(()=>[...f[5]||(f[5]=[S("回放历史",-1)])]),_:1}),o(e(me),null,{default:r(()=>[S("任务 #"+g(e(v)),1)]),_:1})]),_:1}),o(e(W),null,{default:r(()=>[o(e(te),{onClick:ge},{default:r(()=>[...f[6]||(f[6]=[S("刷新",-1)])]),_:1}),o(e(te),{onClick:f[1]||(f[1]=t=>e(h).push("/replay/history"))},{default:r(()=>[...f[7]||(f[7]=[S("返回历史",-1)])]),_:1}),o(e(te),{type:"info",onClick:Ee},{default:r(()=>[...f[8]||(f[8]=[S("导出 HTML 报告",-1)])]),_:1})]),_:1})]),_:1}),n.value?(C(),G(e(E),{key:0,title:n.value.name||`回放任务 #${e(v)}`},{"header-extra":r(()=>[o(e(q),{type:ee[n.value.status]||"default"},{default:r(()=>[S(g(Pe[n.value.status]||n.value.status),1)]),_:1},8,["type"])]),default:r(()=>{var t;return[o(e(ne),{bordered:"",column:3,size:"small"},{default:r(()=>[o(e(A),{label:"回放应用"},{default:r(()=>[S(g(p.value),1)]),_:1}),o(e(A),{label:"开始时间"},{default:r(()=>[S(g(e(ae)(n.value.started_at)),1)]),_:1}),o(e(A),{label:"完成时间"},{default:r(()=>[S(g(e(ae)(n.value.finished_at)),1)]),_:1}),o(e(A),{label:"并发数"},{default:r(()=>[S(g(n.value.concurrency),1)]),_:1}),o(e(A),{label:"超时"},{default:r(()=>[S(g(n.value.timeout_ms)+"ms",1)]),_:1}),o(e(A),{label:"智能降噪"},{default:r(()=>[S(g(n.value.smart_noise_reduction?"开启":"关闭"),1)]),_:1})]),_:1}),(t=n.value.ignore_fields)!=null&&t.length?(C(),G(e(W),{key:0,style:{"margin-top":"12px"}},{default:r(()=>[f[9]||(f[9]=$("span",{style:{color:"#666","font-size":"13px"}},"忽略字段：",-1)),(C(!0),I(U,null,Q(n.value.ignore_fields,w=>(C(),G(e(q),{key:w,size:"small",type:"default"},{default:r(()=>[S(g(w),1)]),_:2},1024))),128))]),_:1})):M("",!0)]}),_:1},8,["title"])):M("",!0),o(e(oe),{cols:"1 s:2 l:4",responsive:"screen","x-gap":16},{default:r(()=>[o(e(J),null,{default:r(()=>[o(e(E),{style:{"text-align":"center"}},{default:r(()=>{var t;return[o(e(le),{label:"总计",value:((t=n.value)==null?void 0:t.total)||0},null,8,["value"])]}),_:1})]),_:1}),o(e(J),null,{default:r(()=>[o(e(E),{style:{"text-align":"center"}},{default:r(()=>[o(e(le),{label:"通过"},{default:r(()=>{var t;return[$("span",jt,g(((t=n.value)==null?void 0:t.passed)||0),1)]}),_:1})]),_:1})]),_:1}),o(e(J),null,{default:r(()=>[o(e(E),{style:{"text-align":"center"}},{default:r(()=>[o(e(le),{label:"失败"},{default:r(()=>{var t;return[$("span",Wt,g(((t=n.value)==null?void 0:t.failed)||0),1)]}),_:1})]),_:1})]),_:1}),o(e(J),null,{default:r(()=>[o(e(E),{style:{"text-align":"center"}},{default:r(()=>[o(e(le),{label:"通过率"},{default:r(()=>[$("span",{style:se({color:k.value>=90?"#18a058":k.value>=60?"#f0a020":"#d03050",fontSize:"28px",fontWeight:"bold"})},g(k.value.toFixed(1))+"% ",5)]),_:1})]),_:1})]),_:1})]),_:1}),n.value&&(n.value.failed>0||n.value.errored>0)?(C(),G(e(E),{key:1,title:"失败原因分析"},{default:r(()=>[o(e(_e),{show:a.value},{default:r(()=>[o(e(oe),{cols:"1 s:2 l:5",responsive:"screen","x-gap":12},{default:r(()=>[(C(!0),I(U,null,Q(H.value,t=>(C(),G(e(J),{key:t.key},{default:r(()=>[$("div",Et,[$("div",Mt,g(t.icon),1),$("div",qt,g(t.label),1),$("div",{class:"analysis-count",style:se({color:t.color})},g(t.count),5),o(e(kt),{type:"line",percentage:t.percentage,color:t.color,"rail-color":"#f0f0f0","indicator-placement":"inside",style:{"margin-top":"6px"}},null,8,["percentage","color"]),$("div",Gt,g(t.percentage.toFixed(0))+"%",1)])]),_:2},1024))),128))]),_:1})]),_:1},8,["show"])]),_:1})):M("",!0),o(e(E),{title:"逐条结果"},{"header-extra":r(()=>[o(e(W),null,{default:r(()=>[o(e(ot),{value:z.value,"onUpdate:value":[f[2]||(f[2]=t=>z.value=t),ye],options:Oe,clearable:"",placeholder:"按状态筛选",style:{width:"160px"}},null,8,["value"])]),_:1})]),default:r(()=>[o(e(ut),{columns:Be,data:y.value,loading:b.value,pagination:{pageSize:15},size:"small"},null,8,["data","loading"])]),_:1})]),_:1}),o(e(Ke),{show:D.value,"onUpdate:show":f[4]||(f[4]=t=>D.value=t),preset:"card",style:{width:"1000px"},title:"结果对比详情"},{default:r(()=>[o(e(W),{vertical:"",size:12},{default:r(()=>[o(e(ne),{bordered:"",column:3,size:"small"},{default:r(()=>[o(e(A),{label:"接口"},{default:r(()=>{var t,w;return[$("b",null,g((t=m.value)==null?void 0:t.request_method),1),S(" "+g((w=m.value)==null?void 0:w.request_uri),1)]}),_:1}),o(e(A),{label:"状态码"},{default:r(()=>{var t;return[S(g(((t=m.value)==null?void 0:t.actual_status_code)||"-"),1)]}),_:1}),o(e(A),{label:"Diff Score"},{default:r(()=>{var t,w;return[$("span",{style:se({color:de((t=m.value)==null?void 0:t.diff_score)})},g(((w=m.value)==null?void 0:w.diff_score)!=null?m.value.diff_score.toFixed(3):"-"),5)]}),_:1}),o(e(A),{label:"来源录制"},{default:r(()=>[o(e(W),{align:"center",size:8},{default:r(()=>{var t,w;return[o(e(q),{type:(t=m.value)!=null&&t.use_sub_invocation_mocks?"success":"default",size:"small"},{default:r(()=>{var L;return[S(g((L=m.value)!=null&&L.use_sub_invocation_mocks?"Mock 开启":"Mock 关闭"),1)]}),_:1},8,["type"]),$("span",null,g((w=m.value)!=null&&w.source_recording_id?`#${m.value.source_recording_id}`:"-"),1)]}),_:1})]),_:1}),o(e(A),{label:"子调用数"},{default:r(()=>{var t;return[S(g(((t=m.value)==null?void 0:t.source_recording_sub_call_count)??"-"),1)]}),_:1}),o(e(A),{label:"失败分类",span:2},{default:r(()=>{var t,w;return[S(g(ue[((t=m.value)==null?void 0:t.failure_category)||""]||((w=m.value)==null?void 0:w.failure_category)||"-"),1)]}),_:1}),o(e(A),{label:"耗时"},{default:r(()=>{var t;return[S(g(((t=m.value)==null?void 0:t.latency_ms)!=null?`${m.value.latency_ms}ms`:"-"),1)]}),_:1})]),_:1}),o(e(oe),{cols:"1 l:2",responsive:"screen","x-gap":16},{default:r(()=>[o(e(J),null,{default:r(()=>[o(e(E),{title:"期望响应（SIT 录制）",size:"small"},{default:r(()=>{var t;return[$("pre",Ft,g(fe((t=m.value)==null?void 0:t.expected_response)),1)]}),_:1})]),_:1}),o(e(J),null,{default:r(()=>[o(e(E),{title:"实际响应（UAT 回放）",size:"small"},{default:r(()=>{var t;return[$("pre",Ut,g(fe((t=m.value)==null?void 0:t.actual_response)),1)]}),_:1})]),_:1})]),_:1}),c.value?(C(),G(e(E),{key:0,title:"来源录制链路",size:"small"},{"header-extra":r(()=>[o(e(W),{align:"center",size:8},{default:r(()=>[o(e(q),{type:"info",size:"small"},{default:r(()=>{var t;return[S("来源用例 #"+g(((t=i.value)==null?void 0:t.id)||"-"),1)]}),_:1}),c.value.id?(C(),G(e(te),{key:0,size:"small",onClick:f[3]||(f[3]=t=>e(h).push(`/recording/recordings/${c.value.id}`))},{default:r(()=>[...f[10]||(f[10]=[S(" 打开录制详情 ",-1)])]),_:1})):M("",!0)]),_:1})]),default:r(()=>[o(e(ne),{bordered:"",column:2,size:"small"},{default:r(()=>[o(e(A),{label:"请求"},{default:r(()=>[S(g(c.value.request_method)+" "+g(c.value.request_uri),1)]),_:1}),o(e(A),{label:"交易码"},{default:r(()=>[S(g(c.value.transaction_code||"-"),1)]),_:1}),o(e(A),{label:"治理状态"},{default:r(()=>[S(g(c.value.governance_status),1)]),_:1}),o(e(A),{label:"子调用概览"},{default:r(()=>[S(g(P.value||"-"),1)]),_:1})]),_:1}),$("div",Vt,[o(rt,{"sub-calls":c.value.sub_calls},null,8,["sub-calls"])])]),_:1})):M("",!0),o(e(dt),{type:"line",animated:""},{default:r(()=>[o(e(ve),{name:"diff",tab:"差异详情"},{default:r(()=>[o(e(E),{size:"small",bordered:!1},{default:r(()=>[o(e(W),{vertical:""},{default:r(()=>{var t,w;return[$("div",null,[f[11]||(f[11]=$("div",{class:"section-title"},"Diff 结果",-1)),$("pre",Ht,g(Ae((t=m.value)==null?void 0:t.diff_result)),1)]),O.value.length>0?(C(),I("div",Jt,[f[12]||(f[12]=$("div",{class:"section-title"},"断言结果",-1)),o(e(W),{vertical:"",size:6},{default:r(()=>[(C(!0),I(U,null,Q(O.value,(L,X)=>(C(),I("div",{key:X},[o(e(q),{type:L.passed?"success":"error",size:"small"},{default:r(()=>[S(g(L.passed?"通过":"失败"),1)]),_:2},1032,["type"]),$("span",Xt,g(L.message),1)]))),128))]),_:1})])):M("",!0),(w=m.value)!=null&&w.failure_reason?(C(),I("div",Kt,[f[13]||(f[13]=$("div",{class:"section-title"},"失败原因",-1)),pe(m.value.failure_reason)?(C(),I(U,{key:0},[$("div",Yt,g(Te(m.value.failure_reason)),1),o(e(W),{vertical:"",size:4},{default:r(()=>[(C(!0),I(U,null,Q(pe(m.value.failure_reason),L=>(C(),I("div",{key:L,style:{display:"flex","align-items":"center",gap:"8px"}},[o(e(q),{type:"error",size:"small",style:{"font-family":"monospace"}},{default:r(()=>[S(g(L),1)]),_:2},1024)]))),128))]),_:1})],64)):(C(),I("pre",Zt,g(m.value.failure_reason),1))])):M("",!0)]}),_:1})]),_:1})]),_:1}),o(e(ve),{name:"subcall",tab:"子调用对比"},{default:r(()=>[o(e(_e),{show:N.value},{default:r(()=>{var t,w;return[o(Lt,{pairs:((t=B.value)==null?void 0:t.pairs)??[],replayed:((w=B.value)==null?void 0:w.replayed)??[]},null,8,["pairs","replayed"])]}),_:1},8,["show"])]),_:1})]),_:1})]),_:1})]),_:1},8,["show"])],64))}}),Sr=Re(Qt,[["__scopeId","data-v-5835a55f"]]);export{Sr as default};
