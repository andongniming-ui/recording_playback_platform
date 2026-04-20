import{a as xe,d as J,h as a,N as Ce,m as I,aE as ke,aF as Se,aG as $e,aH as ze,aI as qe,o as K,g as z,i as q,u as Ne,j as oe,l as we,aB as ce,aJ as Ge,aK as Fe,a1 as Ue,D as Ve,r as T,aL as He,aM as Xe,M as w,H as F,I as r,R as k,P as p,J as e,F as V,ad as re,X as C,ab as E,aD as ae,L as i,K as S,O as M,aN as me,a9 as Je,aa as Ye,U as Ke,Q as ee,T as Qe}from"./index-CEK4JRfn.js";import{a as Ze}from"./applications-EDlKi7K3.js";import{r as te}from"./replays-KumMiSR2.js";import{r as et}from"./recordings-BSFsU7N_.js";import{t as tt}from"./testcases-CwwziLzj.js";import{f as se}from"./format-Adq5_zH5.js";import{_ as rt}from"./SubCallPanel.vue_vue_type_script_setup_true_lang-YIci--Cc.js";import{N as lt}from"./Alert-CbFZJgr4.js";import{u as at,N as L}from"./Space-C0zHjG0z.js";import{N as ie,a as U}from"./Grid-Cka2M7qL.js";import{N as G,a as it}from"./Select-CzhOXaeF.js";import{_ as Re}from"./_plugin-vue_export-helper-DlAUqK2U.js";import{b as ot,p as st}from"./recording-Dk1tlToW.js";import{f as Y}from"./get-BRmAhlo2.js";import{u as nt}from"./index-DsCuBKb3.js";import{N as ct,a as he}from"./BreadcrumbItem-BArlcjyl.js";import{N as ne,a as P}from"./DescriptionsItem-BXEBMBpt.js";import{N as le}from"./Statistic-LQUJEi1a.js";import{N as ut}from"./DataTable-Cx5uZjVm.js";import{a as dt,N as ve}from"./Tabs-QiUskKco.js";import"./CollapseItem-bO8RwmbR.js";import"./Tooltip-B1DHO6tQ.js";import"./Dropdown-DGgAQ_-i.js";import"./Add-BGIy_YTw.js";function ft(l){const{infoColor:b,successColor:m,warningColor:v,errorColor:h,textColor2:o,progressRailColor:f,fontSize:n,fontWeight:c}=l;return{fontSize:n,fontSizeCircle:"28px",fontWeightCircle:c,railColor:f,railHeight:"8px",iconSizeCircle:"36px",iconSizeLine:"18px",iconColor:b,iconColorInfo:b,iconColorSuccess:m,iconColorWarning:v,iconColorError:h,textColorCircle:o,textColorLineInner:"rgb(255, 255, 255)",textColorLineOuter:o,fillColor:b,fillColorInfo:b,fillColorSuccess:m,fillColorWarning:v,fillColorError:h,lineBgProcessing:"linear-gradient(90deg, rgba(255, 255, 255, .3) 0%, rgba(255, 255, 255, .5) 100%)"}}const pt={common:xe,self:ft};function gt(l){const{opacityDisabled:b,heightTiny:m,heightSmall:v,heightMedium:h,heightLarge:o,heightHuge:f,primaryColor:n,fontSize:c}=l;return{fontSize:c,textColor:n,sizeTiny:m,sizeSmall:v,sizeMedium:h,sizeLarge:o,sizeHuge:f,color:n,opacitySpinning:b}}const yt={common:xe,self:gt},mt={success:a(ze,null),error:a($e,null),warning:a(Se,null),info:a(ke,null)},ht=J({name:"ProgressCircle",props:{clsPrefix:{type:String,required:!0},status:{type:String,required:!0},strokeWidth:{type:Number,required:!0},fillColor:[String,Object],railColor:String,railStyle:[String,Object],percentage:{type:Number,default:0},offsetDegree:{type:Number,default:0},showIndicator:{type:Boolean,required:!0},indicatorTextColor:String,unit:String,viewBoxWidth:{type:Number,required:!0},gapDegree:{type:Number,required:!0},gapOffsetDegree:{type:Number,default:0}},setup(l,{slots:b}){const m=I(()=>{const o="gradient",{fillColor:f}=l;return typeof f=="object"?`${o}-${qe(JSON.stringify(f))}`:o});function v(o,f,n,c){const{gapDegree:d,viewBoxWidth:N,strokeWidth:y}=l,_=50,R=0,x=_,g=0,A=2*_,O=50+y/2,D=`M ${O},${O} m ${R},${x}
      a ${_},${_} 0 1 1 ${g},${-A}
      a ${_},${_} 0 1 1 ${-g},${A}`,j=Math.PI*2*_,W={stroke:c==="rail"?n:typeof l.fillColor=="object"?`url(#${m.value})`:n,strokeDasharray:`${Math.min(o,100)/100*(j-d)}px ${N*8}px`,strokeDashoffset:`-${d/2}px`,transformOrigin:f?"center":void 0,transform:f?`rotate(${f}deg)`:void 0};return{pathString:D,pathStyle:W}}const h=()=>{const o=typeof l.fillColor=="object",f=o?l.fillColor.stops[0]:"",n=o?l.fillColor.stops[1]:"";return o&&a("defs",null,a("linearGradient",{id:m.value,x1:"0%",y1:"100%",x2:"100%",y2:"0%"},a("stop",{offset:"0%","stop-color":f}),a("stop",{offset:"100%","stop-color":n})))};return()=>{const{fillColor:o,railColor:f,strokeWidth:n,offsetDegree:c,status:d,percentage:N,showIndicator:y,indicatorTextColor:_,unit:R,gapOffsetDegree:x,clsPrefix:g}=l,{pathString:A,pathStyle:O}=v(100,0,f,"rail"),{pathString:D,pathStyle:j}=v(N,c,o,"fill"),W=100+n;return a("div",{class:`${g}-progress-content`,role:"none"},a("div",{class:`${g}-progress-graph`,"aria-hidden":!0},a("div",{class:`${g}-progress-graph-circle`,style:{transform:x?`rotate(${x}deg)`:void 0}},a("svg",{viewBox:`0 0 ${W} ${W}`},h(),a("g",null,a("path",{class:`${g}-progress-graph-circle-rail`,d:A,"stroke-width":n,"stroke-linecap":"round",fill:"none",style:O})),a("g",null,a("path",{class:[`${g}-progress-graph-circle-fill`,N===0&&`${g}-progress-graph-circle-fill--empty`],d:D,"stroke-width":n,"stroke-linecap":"round",fill:"none",style:j}))))),y?a("div",null,b.default?a("div",{class:`${g}-progress-custom-content`,role:"none"},b.default()):d!=="default"?a("div",{class:`${g}-progress-icon`,"aria-hidden":!0},a(Ce,{clsPrefix:g},{default:()=>mt[d]})):a("div",{class:`${g}-progress-text`,style:{color:_},role:"none"},a("span",{class:`${g}-progress-text__percentage`},N),a("span",{class:`${g}-progress-text__unit`},R))):null)}}}),vt={success:a(ze,null),error:a($e,null),warning:a(Se,null),info:a(ke,null)},bt=J({name:"ProgressLine",props:{clsPrefix:{type:String,required:!0},percentage:{type:Number,default:0},railColor:String,railStyle:[String,Object],fillColor:[String,Object],status:{type:String,required:!0},indicatorPlacement:{type:String,required:!0},indicatorTextColor:String,unit:{type:String,default:"%"},processing:{type:Boolean,required:!0},showIndicator:{type:Boolean,required:!0},height:[String,Number],railBorderRadius:[String,Number],fillBorderRadius:[String,Number]},setup(l,{slots:b}){const m=I(()=>Y(l.height)),v=I(()=>{var f,n;return typeof l.fillColor=="object"?`linear-gradient(to right, ${(f=l.fillColor)===null||f===void 0?void 0:f.stops[0]} , ${(n=l.fillColor)===null||n===void 0?void 0:n.stops[1]})`:l.fillColor}),h=I(()=>l.railBorderRadius!==void 0?Y(l.railBorderRadius):l.height!==void 0?Y(l.height,{c:.5}):""),o=I(()=>l.fillBorderRadius!==void 0?Y(l.fillBorderRadius):l.railBorderRadius!==void 0?Y(l.railBorderRadius):l.height!==void 0?Y(l.height,{c:.5}):"");return()=>{const{indicatorPlacement:f,railColor:n,railStyle:c,percentage:d,unit:N,indicatorTextColor:y,status:_,showIndicator:R,processing:x,clsPrefix:g}=l;return a("div",{class:`${g}-progress-content`,role:"none"},a("div",{class:`${g}-progress-graph`,"aria-hidden":!0},a("div",{class:[`${g}-progress-graph-line`,{[`${g}-progress-graph-line--indicator-${f}`]:!0}]},a("div",{class:`${g}-progress-graph-line-rail`,style:[{backgroundColor:n,height:m.value,borderRadius:h.value},c]},a("div",{class:[`${g}-progress-graph-line-fill`,x&&`${g}-progress-graph-line-fill--processing`],style:{maxWidth:`${l.percentage}%`,background:v.value,height:m.value,lineHeight:m.value,borderRadius:o.value}},f==="inside"?a("div",{class:`${g}-progress-graph-line-indicator`,style:{color:y}},b.default?b.default():`${d}${N}`):null)))),R&&f==="outside"?a("div",null,b.default?a("div",{class:`${g}-progress-custom-content`,style:{color:y},role:"none"},b.default()):_==="default"?a("div",{role:"none",class:`${g}-progress-icon ${g}-progress-icon--as-text`,style:{color:y}},d,N):a("div",{class:`${g}-progress-icon`,"aria-hidden":!0},a(Ce,{clsPrefix:g},{default:()=>vt[_]}))):null)}}});function be(l,b,m=100){return`m ${m/2} ${m/2-l} a ${l} ${l} 0 1 1 0 ${2*l} a ${l} ${l} 0 1 1 0 -${2*l}`}const _t=J({name:"ProgressMultipleCircle",props:{clsPrefix:{type:String,required:!0},viewBoxWidth:{type:Number,required:!0},percentage:{type:Array,default:[0]},strokeWidth:{type:Number,required:!0},circleGap:{type:Number,required:!0},showIndicator:{type:Boolean,required:!0},fillColor:{type:Array,default:()=>[]},railColor:{type:Array,default:()=>[]},railStyle:{type:Array,default:()=>[]}},setup(l,{slots:b}){const m=I(()=>l.percentage.map((o,f)=>`${Math.PI*o/100*(l.viewBoxWidth/2-l.strokeWidth/2*(1+2*f)-l.circleGap*f)*2}, ${l.viewBoxWidth*8}`)),v=(h,o)=>{const f=l.fillColor[o],n=typeof f=="object"?f.stops[0]:"",c=typeof f=="object"?f.stops[1]:"";return typeof l.fillColor[o]=="object"&&a("linearGradient",{id:`gradient-${o}`,x1:"100%",y1:"0%",x2:"0%",y2:"100%"},a("stop",{offset:"0%","stop-color":n}),a("stop",{offset:"100%","stop-color":c}))};return()=>{const{viewBoxWidth:h,strokeWidth:o,circleGap:f,showIndicator:n,fillColor:c,railColor:d,railStyle:N,percentage:y,clsPrefix:_}=l;return a("div",{class:`${_}-progress-content`,role:"none"},a("div",{class:`${_}-progress-graph`,"aria-hidden":!0},a("div",{class:`${_}-progress-graph-circle`},a("svg",{viewBox:`0 0 ${h} ${h}`},a("defs",null,y.map((R,x)=>v(R,x))),y.map((R,x)=>a("g",{key:x},a("path",{class:`${_}-progress-graph-circle-rail`,d:be(h/2-o/2*(1+2*x)-f*x,o,h),"stroke-width":o,"stroke-linecap":"round",fill:"none",style:[{strokeDashoffset:0,stroke:d[x]},N[x]]}),a("path",{class:[`${_}-progress-graph-circle-fill`,R===0&&`${_}-progress-graph-circle-fill--empty`],d:be(h/2-o/2*(1+2*x)-f*x,o,h),"stroke-width":o,"stroke-linecap":"round",fill:"none",style:{strokeDasharray:m.value[x],strokeDashoffset:0,stroke:typeof c[x]=="object"?`url(#gradient-${x})`:c[x]}})))))),n&&b.default?a("div",null,a("div",{class:`${_}-progress-text`},b.default())):null)}}}),xt=K([z("progress",{display:"inline-block"},[z("progress-icon",`
 color: var(--n-icon-color);
 transition: color .3s var(--n-bezier);
 `),q("line",`
 width: 100%;
 display: block;
 `,[z("progress-content",`
 display: flex;
 align-items: center;
 `,[z("progress-graph",{flex:1})]),z("progress-custom-content",{marginLeft:"14px"}),z("progress-icon",`
 width: 30px;
 padding-left: 14px;
 height: var(--n-icon-size-line);
 line-height: var(--n-icon-size-line);
 font-size: var(--n-icon-size-line);
 `,[q("as-text",`
 color: var(--n-text-color-line-outer);
 text-align: center;
 width: 40px;
 font-size: var(--n-font-size);
 padding-left: 4px;
 transition: color .3s var(--n-bezier);
 `)])]),q("circle, dashboard",{width:"120px"},[z("progress-custom-content",`
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 display: flex;
 align-items: center;
 justify-content: center;
 `),z("progress-text",`
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
 `),z("progress-icon",`
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 display: flex;
 align-items: center;
 color: var(--n-icon-color);
 font-size: var(--n-icon-size-circle);
 `)]),q("multiple-circle",`
 width: 200px;
 color: inherit;
 `,[z("progress-text",`
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
 `)]),z("progress-content",{position:"relative"}),z("progress-graph",{position:"relative"},[z("progress-graph-circle",[K("svg",{verticalAlign:"bottom"}),z("progress-graph-circle-fill",`
 stroke: var(--n-fill-color);
 transition:
 opacity .3s var(--n-bezier),
 stroke .3s var(--n-bezier),
 stroke-dasharray .3s var(--n-bezier);
 `,[q("empty",{opacity:0})]),z("progress-graph-circle-rail",`
 transition: stroke .3s var(--n-bezier);
 overflow: hidden;
 stroke: var(--n-rail-color);
 `)]),z("progress-graph-line",[q("indicator-inside",[z("progress-graph-line-rail",`
 height: 16px;
 line-height: 16px;
 border-radius: 10px;
 `,[z("progress-graph-line-fill",`
 height: inherit;
 border-radius: 10px;
 `),z("progress-graph-line-indicator",`
 background: #0000;
 white-space: nowrap;
 text-align: right;
 margin-left: 14px;
 margin-right: 14px;
 height: inherit;
 font-size: 12px;
 color: var(--n-text-color-line-inner);
 transition: color .3s var(--n-bezier);
 `)])]),q("indicator-inside-label",`
 height: 16px;
 display: flex;
 align-items: center;
 `,[z("progress-graph-line-rail",`
 flex: 1;
 transition: background-color .3s var(--n-bezier);
 `),z("progress-graph-line-indicator",`
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
 `)]),z("progress-graph-line-rail",`
 position: relative;
 overflow: hidden;
 height: var(--n-rail-height);
 border-radius: 5px;
 background-color: var(--n-rail-color);
 transition: background-color .3s var(--n-bezier);
 `,[z("progress-graph-line-fill",`
 background: var(--n-fill-color);
 position: relative;
 border-radius: 5px;
 height: inherit;
 width: 100%;
 max-width: 0%;
 transition:
 background-color .3s var(--n-bezier),
 max-width .2s var(--n-bezier);
 `,[q("processing",[K("&::after",`
 content: "";
 background-image: var(--n-line-bg-processing);
 animation: progress-processing-animation 2s var(--n-bezier) infinite;
 `)])])])])])]),K("@keyframes progress-processing-animation",`
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
 `)]),Ct=Object.assign(Object.assign({},oe.props),{processing:Boolean,type:{type:String,default:"line"},gapDegree:Number,gapOffsetDegree:Number,status:{type:String,default:"default"},railColor:[String,Array],railStyle:[String,Array],color:[String,Array,Object],viewBoxWidth:{type:Number,default:100},strokeWidth:{type:Number,default:7},percentage:[Number,Array],unit:{type:String,default:"%"},showIndicator:{type:Boolean,default:!0},indicatorPosition:{type:String,default:"outside"},indicatorPlacement:{type:String,default:"outside"},indicatorTextColor:String,circleGap:{type:Number,default:1},height:Number,borderRadius:[String,Number],fillBorderRadius:[String,Number],offsetDegree:Number}),kt=J({name:"Progress",props:Ct,setup(l){const b=I(()=>l.indicatorPlacement||l.indicatorPosition),m=I(()=>{if(l.gapDegree||l.gapDegree===0)return l.gapDegree;if(l.type==="dashboard")return 75}),{mergedClsPrefixRef:v,inlineThemeDisabled:h}=Ne(l),o=oe("Progress","-progress",xt,pt,l,v),f=I(()=>{const{status:c}=l,{common:{cubicBezierEaseInOut:d},self:{fontSize:N,fontSizeCircle:y,railColor:_,railHeight:R,iconSizeCircle:x,iconSizeLine:g,textColorCircle:A,textColorLineInner:O,textColorLineOuter:D,lineBgProcessing:j,fontWeightCircle:W,[ce("iconColor",c)]:Q,[ce("fillColor",c)]:H}}=o.value;return{"--n-bezier":d,"--n-fill-color":H,"--n-font-size":N,"--n-font-size-circle":y,"--n-font-weight-circle":W,"--n-icon-color":Q,"--n-icon-size-circle":x,"--n-icon-size-line":g,"--n-line-bg-processing":j,"--n-rail-color":_,"--n-rail-height":R,"--n-text-color-circle":A,"--n-text-color-line-inner":O,"--n-text-color-line-outer":D}}),n=h?we("progress",I(()=>l.status[0]),f,l):void 0;return{mergedClsPrefix:v,mergedIndicatorPlacement:b,gapDeg:m,cssVars:h?void 0:f,themeClass:n==null?void 0:n.themeClass,onRender:n==null?void 0:n.onRender}},render(){const{type:l,cssVars:b,indicatorTextColor:m,showIndicator:v,status:h,railColor:o,railStyle:f,color:n,percentage:c,viewBoxWidth:d,strokeWidth:N,mergedIndicatorPlacement:y,unit:_,borderRadius:R,fillBorderRadius:x,height:g,processing:A,circleGap:O,mergedClsPrefix:D,gapDeg:j,gapOffsetDegree:W,themeClass:Q,$slots:H,onRender:Z}=this;return Z==null||Z(),a("div",{class:[Q,`${D}-progress`,`${D}-progress--${l}`,`${D}-progress--${h}`],style:b,"aria-valuemax":100,"aria-valuemin":0,"aria-valuenow":c,role:l==="circle"||l==="line"||l==="dashboard"?"progressbar":"none"},l==="circle"||l==="dashboard"?a(ht,{clsPrefix:D,status:h,showIndicator:v,indicatorTextColor:m,railColor:o,fillColor:n,railStyle:f,offsetDegree:this.offsetDegree,percentage:c,viewBoxWidth:d,strokeWidth:N,gapDegree:j===void 0?l==="dashboard"?75:0:j,gapOffsetDegree:W,unit:_},H):l==="line"?a(bt,{clsPrefix:D,status:h,showIndicator:v,indicatorTextColor:m,railColor:o,fillColor:n,railStyle:f,percentage:c,processing:A,indicatorPlacement:y,unit:_,fillBorderRadius:x,railBorderRadius:R,height:g},H):l==="multiple-circle"?a(_t,{clsPrefix:D,strokeWidth:N,railColor:o,fillColor:n,railStyle:f,viewBoxWidth:d,percentage:c,showIndicator:v,circleGap:O},H):null)}}),St=K([K("@keyframes spin-rotate",`
 from {
 transform: rotate(0);
 }
 to {
 transform: rotate(360deg);
 }
 `),z("spin-container",`
 position: relative;
 `,[z("spin-body",`
 position: absolute;
 top: 50%;
 left: 50%;
 transform: translateX(-50%) translateY(-50%);
 `,[Ge()])]),z("spin-body",`
 display: inline-flex;
 align-items: center;
 justify-content: center;
 flex-direction: column;
 `),z("spin",`
 display: inline-flex;
 height: var(--n-size);
 width: var(--n-size);
 font-size: var(--n-size);
 color: var(--n-color);
 `,[q("rotate",`
 animation: spin-rotate 2s linear infinite;
 `)]),z("spin-description",`
 display: inline-block;
 font-size: var(--n-font-size);
 color: var(--n-text-color);
 transition: color .3s var(--n-bezier);
 margin-top: 8px;
 `),z("spin-content",`
 opacity: 1;
 transition: opacity .3s var(--n-bezier);
 pointer-events: all;
 `,[q("spinning",`
 user-select: none;
 -webkit-user-select: none;
 pointer-events: none;
 opacity: var(--n-opacity-spinning);
 `)])]),$t={small:20,medium:18,large:16},zt=Object.assign(Object.assign(Object.assign({},oe.props),{contentClass:String,contentStyle:[Object,String],description:String,size:{type:[String,Number],default:"medium"},show:{type:Boolean,default:!0},rotate:{type:Boolean,default:!0},spinning:{type:Boolean,validator:()=>!0,default:void 0},delay:Number}),He),_e=J({name:"Spin",props:zt,slots:Object,setup(l){const{mergedClsPrefixRef:b,inlineThemeDisabled:m}=Ne(l),v=oe("Spin","-spin",St,yt,l,b),h=I(()=>{const{size:c}=l,{common:{cubicBezierEaseInOut:d},self:N}=v.value,{opacitySpinning:y,color:_,textColor:R}=N,x=typeof c=="number"?Xe(c):N[ce("size",c)];return{"--n-bezier":d,"--n-opacity-spinning":y,"--n-size":x,"--n-color":_,"--n-text-color":R}}),o=m?we("spin",I(()=>{const{size:c}=l;return typeof c=="number"?String(c):c[0]}),h,l):void 0,f=at(l,["spinning","show"]),n=T(!1);return Ve(c=>{let d;if(f.value){const{delay:N}=l;if(N){d=window.setTimeout(()=>{n.value=!0},N),c(()=>{clearTimeout(d)});return}}n.value=f.value}),{mergedClsPrefix:b,active:n,mergedStrokeWidth:I(()=>{const{strokeWidth:c}=l;if(c!==void 0)return c;const{size:d}=l;return $t[typeof d=="number"?"medium":d]}),cssVars:m?void 0:h,themeClass:o==null?void 0:o.themeClass,onRender:o==null?void 0:o.onRender}},render(){var l,b;const{$slots:m,mergedClsPrefix:v,description:h}=this,o=m.icon&&this.rotate,f=(h||m.description)&&a("div",{class:`${v}-spin-description`},h||((l=m.description)===null||l===void 0?void 0:l.call(m))),n=m.icon?a("div",{class:[`${v}-spin-body`,this.themeClass]},a("div",{class:[`${v}-spin`,o&&`${v}-spin--rotate`],style:m.default?"":this.cssVars},m.icon()),f):a("div",{class:[`${v}-spin-body`,this.themeClass]},a(Fe,{clsPrefix:v,style:m.default?"":this.cssVars,stroke:this.stroke,"stroke-width":this.mergedStrokeWidth,radius:this.radius,scale:this.scale,class:`${v}-spin`}),f);return(b=this.onRender)===null||b===void 0||b.call(this),m.default?a("div",{class:[`${v}-spin-container`,this.themeClass],style:this.cssVars},a("div",{class:[`${v}-spin-content`,this.active&&`${v}-spin-content--spinning`,this.contentClass],style:this.contentStyle},m),a(Ue,{name:"fade-in-transition"},{default:()=>this.active?n:null})):n}}),Nt={style:{"font-weight":"600"}},wt={style:{color:"#666","font-size":"13px"}},Rt={key:0,class:"field-label"},Pt={key:1,class:"code-block compact"},Dt={key:1,class:"empty-side"},It={key:0,class:"field-label"},Bt={key:1,class:"code-block compact"},Tt={key:1,class:"empty-side"},Ot=J({__name:"SubCallDiffPanel",props:{pairs:{},replayed:{}},setup(l){function b(n){if(n==null)return"-";if(typeof n=="string")try{return JSON.stringify(JSON.parse(n),null,2)}catch{return n}return JSON.stringify(n,null,2)}function m(n){var d,N;const c=((d=n.recorded)==null?void 0:d.operation)||((N=n.replayed)==null?void 0:N.operation)||"";return c.length>60?c.slice(0,60)+"…":c}function v(n){return n.side==="recorded_only"||n.side==="replayed_only"?"#f0a020":n.response_matched===!1?"#d03050":"#18a058"}function h(n){return n.side==="recorded_only"||n.side==="replayed_only"?"warning":n.response_matched===!1?"error":"success"}function o(n){return n.side==="recorded_only"?"仅录制侧":n.side==="replayed_only"?"仅回放侧":n.response_matched===!1?"响应差异":"一致"}function f(n){const c=(n||"").toLowerCase();return c.includes("mysql")||c.includes("jdbc")?"warning":c.includes("redis")?"info":"default"}return(n,c)=>(C(),w("div",null,[l.pairs.length?(C(),F(e(L),{key:1,vertical:"",size:12},{default:r(()=>[(C(!0),w(V,null,re(l.pairs,d=>(C(),F(e(E),{key:d.index,size:"small",style:ae({borderLeft:`3px solid ${v(d)}`})},{header:r(()=>[i(e(L),{align:"center",size:8},{default:r(()=>[S("span",Nt,"#"+p(d.index),1),i(e(G),{size:"small",type:f(d.type)},{default:r(()=>[k(p(d.type||"未知"),1)]),_:2},1032,["type"]),S("span",wt,p(m(d)),1)]),_:2},1024)]),"header-extra":r(()=>[i(e(G),{type:h(d),size:"small"},{default:r(()=>[k(p(o(d)),1)]),_:2},1032,["type"])]),default:r(()=>[i(e(ie),{cols:2,"x-gap":12},{default:r(()=>[i(e(U),null,{default:r(()=>[c[1]||(c[1]=S("div",{class:"col-title"},"录制（System A）",-1)),d.recorded?(C(),w(V,{key:0},[d.recorded.operation?(C(),w("div",Rt,"操作")):M("",!0),d.recorded.operation?(C(),w("pre",Pt,p(d.recorded.operation),1)):M("",!0),c[0]||(c[0]=S("div",{class:"field-label"},"响应",-1)),S("pre",{class:me(["code-block",{diff:d.side==="both"&&d.response_matched===!1}])},p(b(d.recorded.response)),3)],64)):(C(),w("div",Dt,"— 仅回放侧有此调用 —"))]),_:2},1024),i(e(U),null,{default:r(()=>[c[3]||(c[3]=S("div",{class:"col-title"},"回放（System B）",-1)),d.replayed?(C(),w(V,{key:0},[d.replayed.operation?(C(),w("div",It,"操作")):M("",!0),d.replayed.operation?(C(),w("pre",Bt,p(d.replayed.operation),1)):M("",!0),c[2]||(c[2]=S("div",{class:"field-label"},"响应",-1)),S("pre",{class:me(["code-block",{diff:d.side==="both"&&d.response_matched===!1}])},p(b(d.replayed.response)),3)],64)):(C(),w("div",Tt,"— 仅录制侧有此调用 —"))]),_:2},1024)]),_:2},1024)]),_:2},1032,["style"]))),128))]),_:1})):(C(),F(e(lt),{key:0,type:"default","show-icon":!1,style:{color:"#999"}},{default:r(()=>[k(p(l.replayed.length===0?"Agent 未上报子调用（回放时 AREX Agent 可能未启动或未配置录制模式）":"暂无子调用数据"),1)]),_:1}))]))}}),Lt=Re(Ot,[["__scopeId","data-v-781e48b5"]]),At={style:{color:"#18a058","font-size":"28px","font-weight":"bold"}},jt={style:{color:"#d03050","font-size":"28px","font-weight":"bold"}},Et={class:"analysis-card"},Wt={class:"analysis-icon"},Mt={class:"analysis-label"},qt={class:"analysis-pct"},Gt={class:"code-block"},Ft={class:"code-block"},Ut={style:{"margin-top":"12px"}},Vt={class:"code-block compact"},Ht={key:0},Xt={style:{"margin-left":"8px","font-size":"12px"}},Jt={key:1},Yt={style:{"font-size":"13px",color:"#555","margin-bottom":"8px"}},Kt={key:1,class:"code-block compact"},Qt=J({__name:"job-detail",setup(l){const b=Ke(),m=Qe(),v=nt(),h=Number(b.params.jobId),o=T(null),f=T("-"),n=T([]),c=T(!1),d=T(null),N=T(!1),y=T(null),_=T(!1),R=T(null),x=T(null),g=T(null),A=T(""),O=T(null),D=T(!1),j=I(()=>!o.value||!o.value.total?0:o.value.passed/o.value.total*100),W=I(()=>{var u;const s=(u=y.value)==null?void 0:u.assertion_results;if(!s)return[];try{const t=JSON.parse(s);return Array.isArray(t)?t:[]}catch{return[]}}),Q=[{key:"ENVIRONMENT",label:"环境问题",icon:"🌐",color:"#f0a020"},{key:"DATA_ISSUE",label:"数据问题",icon:"📝",color:"#2080f0"},{key:"BUG",label:"代码缺陷",icon:"🐛",color:"#d03050"},{key:"PERFORMANCE",label:"性能问题",icon:"⚡",color:"#8a2be2"},{key:"UNKNOWN",label:"未知",icon:"❓",color:"#999"}],H=I(()=>{var u;const s=((u=R.value)==null?void 0:u.categories)||{};return Q.map(t=>{var $,B;return{...t,count:(($=s[t.key])==null?void 0:$.count)||0,percentage:((B=s[t.key])==null?void 0:B.percentage)||0}})}),Z={DONE:"success",RUNNING:"info",FAILED:"error",PENDING:"default",CANCELLED:"warning"},Pe={DONE:"已完成",RUNNING:"运行中",FAILED:"失败",PENDING:"待执行",CANCELLED:"已取消"},De={PASS:"success",FAIL:"error",ERROR:"warning",TIMEOUT:"warning",PENDING:"default"},Ie={PASS:"通过",FAIL:"失败",ERROR:"异常",TIMEOUT:"超时",PENDING:"待执行"},ue={status_mismatch:"状态码不一致",response_diff:"响应内容差异",assertion_failed:"断言失败",performance:"性能超限",timeout:"请求超时",connection_error:"连接异常",mock_error:"Mock 异常"},Be=[{label:"通过",value:"PASS"},{label:"失败",value:"FAIL"},{label:"异常",value:"ERROR"},{label:"超时",value:"TIMEOUT"}];function de(s){return s==null?"#999":s<=.1?"#18a058":s<=.5?"#f0a020":"#d03050"}const Te=[{title:"接口",key:"request_uri",render:s=>a("div",{style:"line-height:1.6"},[a("div",[a("b",{style:"margin-right:4px;color:#666"},s.request_method||"GET"),a("span",s.request_uri||"-")]),s.transaction_code?a("div",{style:"display:inline-block;background:#e8f0fe;color:#1a73e8;border-radius:4px;padding:1px 7px;font-size:12px;margin-top:2px;font-weight:500"},s.transaction_code):null])},{title:"来源录制",key:"source_recording_id",width:170,render:s=>s.source_recording_id?a(L,{size:6,align:"center"},()=>[a(G,{type:s.use_sub_invocation_mocks?"success":"default",size:"small"},()=>s.use_sub_invocation_mocks?"Mock 开启":"Mock 关闭"),a("span",`#${s.source_recording_id}${s.source_recording_sub_call_count!=null?` / 子调用 ${s.source_recording_sub_call_count}`:""}`)]):a("span",{style:"color:#ccc"},"-")},{title:"状态",key:"status",width:80,render:s=>a(G,{type:De[s.status]??"default",size:"small"},()=>Ie[s.status]||s.status)},{title:"失败分类",key:"failure_category",width:120,render:s=>s.failure_category?a("span",ue[s.failure_category]||s.failure_category):a("span",{style:"color:#ccc"},"-")},{title:"Diff Score",key:"diff_score",width:100,render:s=>s.diff_score==null?a("span",{style:"color:#ccc"},"-"):a("span",{style:`color:${de(s.diff_score)};font-weight:bold`},s.diff_score.toFixed(3))},{title:"状态码",key:"actual_status_code",width:80,render:s=>{var u;return a("span",((u=s.actual_status_code)==null?void 0:u.toString())||"-")}},{title:"耗时",key:"latency_ms",width:80,render:s=>a("span",s.latency_ms!=null?`${s.latency_ms}ms`:"-")},{title:"时间",key:"created_at",width:145,render:s=>a("span",{style:"font-size:12px;color:#999"},se(s.created_at))},{title:"对比",key:"actions",width:70,render:s=>a(ee,{size:"tiny",type:"primary",ghost:!0,onClick:()=>Ae(s)},()=>"对比")}];function Oe(s){if(!s)return"-";try{return JSON.stringify(JSON.parse(s),null,2)}catch{return s}}function fe(s){return s||"-"}function pe(s){if(!s)return null;const u=s.match(/差异字段\s+(.+)$/);return u?u[1].split(",").map(t=>t.trim()).filter(Boolean):null}function Le(s){return s.replace(/差异字段.+$/,"").trim().replace(/:$/,"").trim()}function Ae(s){y.value=s,N.value=!0,Ee(s),je(s.id)}async function je(s){O.value=null,D.value=!0;try{const u=await te.getSubCallDiff(s);O.value=u.data}catch{O.value=null}finally{D.value=!1}}async function Ee(s){if(x.value=null,g.value=null,A.value="",!!s.test_case_id)try{const u=await tt.get(s.test_case_id);if(x.value=u.data,u.data.source_recording_id){const t=await et.getRecording(u.data.source_recording_id);g.value=t.data,A.value=ot(st(t.data.sub_calls))}}catch{x.value=null,g.value=null,A.value=""}}async function We(){var s,u;try{const t=await te.getReport(h),$=new Blob([t.data],{type:"text/html;charset=utf-8"}),B=URL.createObjectURL($),X=document.createElement("a");X.href=B,X.download=`replay_report_${h}.html`,document.body.appendChild(X),X.click(),document.body.removeChild(X),setTimeout(()=>URL.revokeObjectURL(B),1e4)}catch(t){v.error(((u=(s=t.response)==null?void 0:s.data)==null?void 0:u.detail)||"导出报告失败")}}async function Me(){if(!(!o.value||o.value.failed===0&&o.value.errored===0)){_.value=!0;try{const s=await te.getAnalysis(h);R.value=s.data}catch{R.value=null}finally{_.value=!1}}}async function ge(){var s,u;try{const t=await te.get(h);if(o.value=t.data,t.data.application_id!=null){const $=await Ze.get(t.data.application_id);f.value=$.data.name}else f.value="-"}catch(t){v.error(((u=(s=t.response)==null?void 0:s.data)==null?void 0:u.detail)||"加载回放任务失败")}await Promise.all([ye(),Me()])}async function ye(){var s,u;c.value=!0;try{const t={limit:200};d.value&&(t.status=d.value);const $=await te.getResults(h,t);n.value=$.data}catch(t){n.value=[],v.error(((u=(s=t.response)==null?void 0:s.data)==null?void 0:u.detail)||"加载结果详情失败")}finally{c.value=!1}}return Je(()=>{ge()}),(s,u)=>(C(),w(V,null,[i(e(L),{vertical:"",size:16},{default:r(()=>[i(e(L),{justify:"space-between",align:"center"},{default:r(()=>[i(e(ct),null,{default:r(()=>[i(e(he),{onClick:u[0]||(u[0]=t=>e(m).push("/replay/history"))},{default:r(()=>[...u[5]||(u[5]=[k("回放历史",-1)])]),_:1}),i(e(he),null,{default:r(()=>[k("任务 #"+p(e(h)),1)]),_:1})]),_:1}),i(e(L),null,{default:r(()=>[i(e(ee),{onClick:ge},{default:r(()=>[...u[6]||(u[6]=[k("刷新",-1)])]),_:1}),i(e(ee),{onClick:u[1]||(u[1]=t=>e(m).push("/replay/history"))},{default:r(()=>[...u[7]||(u[7]=[k("返回历史",-1)])]),_:1}),i(e(ee),{type:"info",onClick:We},{default:r(()=>[...u[8]||(u[8]=[k("导出 HTML 报告",-1)])]),_:1})]),_:1})]),_:1}),o.value?(C(),F(e(E),{key:0,title:o.value.name||`回放任务 #${e(h)}`},{"header-extra":r(()=>[i(e(G),{type:Z[o.value.status]||"default"},{default:r(()=>[k(p(Pe[o.value.status]||o.value.status),1)]),_:1},8,["type"])]),default:r(()=>{var t;return[i(e(ne),{bordered:"",column:3,size:"small"},{default:r(()=>[i(e(P),{label:"回放应用"},{default:r(()=>[k(p(f.value),1)]),_:1}),i(e(P),{label:"开始时间"},{default:r(()=>[k(p(e(se)(o.value.started_at)),1)]),_:1}),i(e(P),{label:"完成时间"},{default:r(()=>[k(p(e(se)(o.value.finished_at)),1)]),_:1}),i(e(P),{label:"并发数"},{default:r(()=>[k(p(o.value.concurrency),1)]),_:1}),i(e(P),{label:"超时"},{default:r(()=>[k(p(o.value.timeout_ms)+"ms",1)]),_:1}),i(e(P),{label:"智能降噪"},{default:r(()=>[k(p(o.value.smart_noise_reduction?"开启":"关闭"),1)]),_:1})]),_:1}),(t=o.value.ignore_fields)!=null&&t.length?(C(),F(e(L),{key:0,style:{"margin-top":"12px"}},{default:r(()=>[u[9]||(u[9]=S("span",{style:{color:"#666","font-size":"13px"}},"忽略字段：",-1)),(C(!0),w(V,null,re(o.value.ignore_fields,$=>(C(),F(e(G),{key:$,size:"small",type:"default"},{default:r(()=>[k(p($),1)]),_:2},1024))),128))]),_:1})):M("",!0)]}),_:1},8,["title"])):M("",!0),i(e(ie),{cols:4,"x-gap":16},{default:r(()=>[i(e(U),null,{default:r(()=>[i(e(E),{style:{"text-align":"center"}},{default:r(()=>{var t;return[i(e(le),{label:"总计",value:((t=o.value)==null?void 0:t.total)||0},null,8,["value"])]}),_:1})]),_:1}),i(e(U),null,{default:r(()=>[i(e(E),{style:{"text-align":"center"}},{default:r(()=>[i(e(le),{label:"通过"},{default:r(()=>{var t;return[S("span",At,p(((t=o.value)==null?void 0:t.passed)||0),1)]}),_:1})]),_:1})]),_:1}),i(e(U),null,{default:r(()=>[i(e(E),{style:{"text-align":"center"}},{default:r(()=>[i(e(le),{label:"失败"},{default:r(()=>{var t;return[S("span",jt,p(((t=o.value)==null?void 0:t.failed)||0),1)]}),_:1})]),_:1})]),_:1}),i(e(U),null,{default:r(()=>[i(e(E),{style:{"text-align":"center"}},{default:r(()=>[i(e(le),{label:"通过率"},{default:r(()=>[S("span",{style:ae({color:j.value>=90?"#18a058":j.value>=60?"#f0a020":"#d03050",fontSize:"28px",fontWeight:"bold"})},p(j.value.toFixed(1))+"% ",5)]),_:1})]),_:1})]),_:1})]),_:1}),o.value&&(o.value.failed>0||o.value.errored>0)?(C(),F(e(E),{key:1,title:"失败原因分析"},{default:r(()=>[i(e(_e),{show:_.value},{default:r(()=>[i(e(ie),{cols:5,"x-gap":12},{default:r(()=>[(C(!0),w(V,null,re(H.value,t=>(C(),F(e(U),{key:t.key},{default:r(()=>[S("div",Et,[S("div",Wt,p(t.icon),1),S("div",Mt,p(t.label),1),S("div",{class:"analysis-count",style:ae({color:t.color})},p(t.count),5),i(e(kt),{type:"line",percentage:t.percentage,color:t.color,"rail-color":"#f0f0f0","indicator-placement":"inside",style:{"margin-top":"6px"}},null,8,["percentage","color"]),S("div",qt,p(t.percentage.toFixed(0))+"%",1)])]),_:2},1024))),128))]),_:1})]),_:1},8,["show"])]),_:1})):M("",!0),i(e(E),{title:"逐条结果"},{"header-extra":r(()=>[i(e(L),null,{default:r(()=>[i(e(it),{value:d.value,"onUpdate:value":[u[2]||(u[2]=t=>d.value=t),ye],options:Be,clearable:"",placeholder:"按状态筛选",style:{width:"160px"}},null,8,["value"])]),_:1})]),default:r(()=>[i(e(ut),{columns:Te,data:n.value,loading:c.value,pagination:{pageSize:15},size:"small"},null,8,["data","loading"])]),_:1})]),_:1}),i(e(Ye),{show:N.value,"onUpdate:show":u[4]||(u[4]=t=>N.value=t),preset:"card",style:{width:"1000px"},title:"结果对比详情"},{default:r(()=>[i(e(L),{vertical:"",size:12},{default:r(()=>[i(e(ne),{bordered:"",column:3,size:"small"},{default:r(()=>[i(e(P),{label:"接口"},{default:r(()=>{var t,$;return[S("b",null,p((t=y.value)==null?void 0:t.request_method),1),k(" "+p(($=y.value)==null?void 0:$.request_uri),1)]}),_:1}),i(e(P),{label:"状态码"},{default:r(()=>{var t;return[k(p(((t=y.value)==null?void 0:t.actual_status_code)||"-"),1)]}),_:1}),i(e(P),{label:"Diff Score"},{default:r(()=>{var t,$;return[S("span",{style:ae({color:de((t=y.value)==null?void 0:t.diff_score)})},p((($=y.value)==null?void 0:$.diff_score)!=null?y.value.diff_score.toFixed(3):"-"),5)]}),_:1}),i(e(P),{label:"来源录制"},{default:r(()=>[i(e(L),{align:"center",size:8},{default:r(()=>{var t,$;return[i(e(G),{type:(t=y.value)!=null&&t.use_sub_invocation_mocks?"success":"default",size:"small"},{default:r(()=>{var B;return[k(p((B=y.value)!=null&&B.use_sub_invocation_mocks?"Mock 开启":"Mock 关闭"),1)]}),_:1},8,["type"]),S("span",null,p(($=y.value)!=null&&$.source_recording_id?`#${y.value.source_recording_id}`:"-"),1)]}),_:1})]),_:1}),i(e(P),{label:"子调用数"},{default:r(()=>{var t;return[k(p(((t=y.value)==null?void 0:t.source_recording_sub_call_count)??"-"),1)]}),_:1}),i(e(P),{label:"失败分类",span:2},{default:r(()=>{var t,$;return[k(p(ue[((t=y.value)==null?void 0:t.failure_category)||""]||(($=y.value)==null?void 0:$.failure_category)||"-"),1)]}),_:1}),i(e(P),{label:"耗时"},{default:r(()=>{var t;return[k(p(((t=y.value)==null?void 0:t.latency_ms)!=null?`${y.value.latency_ms}ms`:"-"),1)]}),_:1})]),_:1}),i(e(ie),{cols:2,"x-gap":16},{default:r(()=>[i(e(U),null,{default:r(()=>[i(e(E),{title:"期望响应（SIT 录制）",size:"small"},{default:r(()=>{var t;return[S("pre",Gt,p(fe((t=y.value)==null?void 0:t.expected_response)),1)]}),_:1})]),_:1}),i(e(U),null,{default:r(()=>[i(e(E),{title:"实际响应（UAT 回放）",size:"small"},{default:r(()=>{var t;return[S("pre",Ft,p(fe((t=y.value)==null?void 0:t.actual_response)),1)]}),_:1})]),_:1})]),_:1}),g.value?(C(),F(e(E),{key:0,title:"来源录制链路",size:"small"},{"header-extra":r(()=>[i(e(L),{align:"center",size:8},{default:r(()=>[i(e(G),{type:"info",size:"small"},{default:r(()=>{var t;return[k("来源用例 #"+p(((t=x.value)==null?void 0:t.id)||"-"),1)]}),_:1}),g.value.id?(C(),F(e(ee),{key:0,size:"small",onClick:u[3]||(u[3]=t=>e(m).push(`/recording/recordings/${g.value.id}`))},{default:r(()=>[...u[10]||(u[10]=[k(" 打开录制详情 ",-1)])]),_:1})):M("",!0)]),_:1})]),default:r(()=>[i(e(ne),{bordered:"",column:2,size:"small"},{default:r(()=>[i(e(P),{label:"请求"},{default:r(()=>[k(p(g.value.request_method)+" "+p(g.value.request_uri),1)]),_:1}),i(e(P),{label:"交易码"},{default:r(()=>[k(p(g.value.transaction_code||"-"),1)]),_:1}),i(e(P),{label:"治理状态"},{default:r(()=>[k(p(g.value.governance_status),1)]),_:1}),i(e(P),{label:"子调用概览"},{default:r(()=>[k(p(A.value||"-"),1)]),_:1})]),_:1}),S("div",Ut,[i(rt,{"sub-calls":g.value.sub_calls},null,8,["sub-calls"])])]),_:1})):M("",!0),i(e(dt),{type:"line",animated:""},{default:r(()=>[i(e(ve),{name:"diff",tab:"差异详情"},{default:r(()=>[i(e(E),{size:"small",bordered:!1},{default:r(()=>[i(e(L),{vertical:""},{default:r(()=>{var t,$;return[S("div",null,[u[11]||(u[11]=S("div",{class:"section-title"},"Diff 结果",-1)),S("pre",Vt,p(Oe((t=y.value)==null?void 0:t.diff_result)),1)]),W.value.length>0?(C(),w("div",Ht,[u[12]||(u[12]=S("div",{class:"section-title"},"断言结果",-1)),i(e(L),{vertical:"",size:6},{default:r(()=>[(C(!0),w(V,null,re(W.value,(B,X)=>(C(),w("div",{key:X},[i(e(G),{type:B.passed?"success":"error",size:"small"},{default:r(()=>[k(p(B.passed?"通过":"失败"),1)]),_:2},1032,["type"]),S("span",Xt,p(B.message),1)]))),128))]),_:1})])):M("",!0),($=y.value)!=null&&$.failure_reason?(C(),w("div",Jt,[u[13]||(u[13]=S("div",{class:"section-title"},"失败原因",-1)),pe(y.value.failure_reason)?(C(),w(V,{key:0},[S("div",Yt,p(Le(y.value.failure_reason)),1),i(e(L),{vertical:"",size:4},{default:r(()=>[(C(!0),w(V,null,re(pe(y.value.failure_reason),B=>(C(),w("div",{key:B,style:{display:"flex","align-items":"center",gap:"8px"}},[i(e(G),{type:"error",size:"small",style:{"font-family":"monospace"}},{default:r(()=>[k(p(B),1)]),_:2},1024)]))),128))]),_:1})],64)):(C(),w("pre",Kt,p(y.value.failure_reason),1))])):M("",!0)]}),_:1})]),_:1})]),_:1}),i(e(ve),{name:"subcall",tab:"子调用对比"},{default:r(()=>[i(e(_e),{show:D.value},{default:r(()=>{var t,$;return[i(Lt,{pairs:((t=O.value)==null?void 0:t.pairs)??[],replayed:(($=O.value)==null?void 0:$.replayed)??[]},null,8,["pairs","replayed"])]}),_:1},8,["show"])]),_:1})]),_:1})]),_:1})]),_:1},8,["show"])],64))}}),kr=Re(Qt,[["__scopeId","data-v-96f171b7"]]);export{kr as default};
