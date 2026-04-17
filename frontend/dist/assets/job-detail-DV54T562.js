import{a as ve,d as J,h as r,N as ye,m as R,aQ as be,aR as _e,aS as xe,aT as Ce,aU as De,o as Y,g as x,i as A,u as Se,j as ie,l as ke,aq as ue,aV as Be,aW as Oe,a1 as Te,D as Le,r as B,aX as je,aY as We,a9 as Ee,M as G,L as o,I as a,J as i,aa as Ae,F as ee,U as Me,R as k,P as m,Q as Z,H as F,K as z,at as ae,O as U,ab as L,aP as oe,T as qe,X as I}from"./index-D6LB0ej7.js";import{a as Ge}from"./applications-Dy8uQOUo.js";import{r as te}from"./replays-Db3mHwRF.js";import{r as Fe}from"./recordings-C6L5psRw.js";import{t as Ue}from"./testcases-DgBFQO7e.js";import{f as se}from"./format-Adq5_zH5.js";import{_ as Ve}from"./SubCallPanel.vue_vue_type_script_setup_true_lang-DmB9ca8L.js";import{b as He,p as Xe}from"./recording-CQVwqkt9.js";import{u as Ye,N as j}from"./Space-JgVsnMPf.js";import{f as X}from"./get-I2R12OG2.js";import{u as Je}from"./index-B6sC-FX3.js";import{N as Ke,a as he}from"./BreadcrumbItem-Jhcozeie.js";import{N as ne,a as w}from"./DescriptionsItem-se0x1FqL.js";import{N as V,a as Qe}from"./Select-C5OqV45F.js";import{N as ce,a as H}from"./Grid-Db3RjpGB.js";import{N as re}from"./Statistic-CvgP2Lih.js";import{N as Ze}from"./DataTable-C6hf0yd5.js";import{_ as et}from"./_plugin-vue_export-helper-DlAUqK2U.js";import"./CollapseItem-BmromAe2.js";import"./Tooltip-B2js9o6V.js";import"./Dropdown-Bfvnp9d9.js";function tt(t){const{infoColor:y,successColor:f,warningColor:v,errorColor:h,textColor2:l,progressRailColor:n,fontSize:u,fontWeight:p}=t;return{fontSize:u,fontSizeCircle:"28px",fontWeightCircle:p,railColor:n,railHeight:"8px",iconSizeCircle:"36px",iconSizeLine:"18px",iconColor:y,iconColorInfo:y,iconColorSuccess:f,iconColorWarning:v,iconColorError:h,textColorCircle:l,textColorLineInner:"rgb(255, 255, 255)",textColorLineOuter:l,fillColor:y,fillColorInfo:y,fillColorSuccess:f,fillColorWarning:v,fillColorError:h,lineBgProcessing:"linear-gradient(90deg, rgba(255, 255, 255, .3) 0%, rgba(255, 255, 255, .5) 100%)"}}const rt={common:ve,self:tt};function it(t){const{opacityDisabled:y,heightTiny:f,heightSmall:v,heightMedium:h,heightLarge:l,heightHuge:n,primaryColor:u,fontSize:p}=t;return{fontSize:p,textColor:u,sizeTiny:f,sizeSmall:v,sizeMedium:h,sizeLarge:l,sizeHuge:n,color:u,opacitySpinning:y}}const lt={common:ve,self:it},at={success:r(Ce,null),error:r(xe,null),warning:r(_e,null),info:r(be,null)},ot=J({name:"ProgressCircle",props:{clsPrefix:{type:String,required:!0},status:{type:String,required:!0},strokeWidth:{type:Number,required:!0},fillColor:[String,Object],railColor:String,railStyle:[String,Object],percentage:{type:Number,default:0},offsetDegree:{type:Number,default:0},showIndicator:{type:Boolean,required:!0},indicatorTextColor:String,unit:String,viewBoxWidth:{type:Number,required:!0},gapDegree:{type:Number,required:!0},gapOffsetDegree:{type:Number,default:0}},setup(t,{slots:y}){const f=R(()=>{const l="gradient",{fillColor:n}=t;return typeof n=="object"?`${l}-${De(JSON.stringify(n))}`:l});function v(l,n,u,p){const{gapDegree:C,viewBoxWidth:$,strokeWidth:g}=t,b=50,N=0,_=b,d=0,D=2*b,O=50+g/2,P=`M ${O},${O} m ${N},${_}
      a ${b},${b} 0 1 1 ${d},${-D}
      a ${b},${b} 0 1 1 ${-d},${D}`,W=Math.PI*2*b,E={stroke:p==="rail"?u:typeof t.fillColor=="object"?`url(#${f.value})`:u,strokeDasharray:`${Math.min(l,100)/100*(W-C)}px ${$*8}px`,strokeDashoffset:`-${C/2}px`,transformOrigin:n?"center":void 0,transform:n?`rotate(${n}deg)`:void 0};return{pathString:P,pathStyle:E}}const h=()=>{const l=typeof t.fillColor=="object",n=l?t.fillColor.stops[0]:"",u=l?t.fillColor.stops[1]:"";return l&&r("defs",null,r("linearGradient",{id:f.value,x1:"0%",y1:"100%",x2:"100%",y2:"0%"},r("stop",{offset:"0%","stop-color":n}),r("stop",{offset:"100%","stop-color":u})))};return()=>{const{fillColor:l,railColor:n,strokeWidth:u,offsetDegree:p,status:C,percentage:$,showIndicator:g,indicatorTextColor:b,unit:N,gapOffsetDegree:_,clsPrefix:d}=t,{pathString:D,pathStyle:O}=v(100,0,n,"rail"),{pathString:P,pathStyle:W}=v($,p,l,"fill"),E=100+u;return r("div",{class:`${d}-progress-content`,role:"none"},r("div",{class:`${d}-progress-graph`,"aria-hidden":!0},r("div",{class:`${d}-progress-graph-circle`,style:{transform:_?`rotate(${_}deg)`:void 0}},r("svg",{viewBox:`0 0 ${E} ${E}`},h(),r("g",null,r("path",{class:`${d}-progress-graph-circle-rail`,d:D,"stroke-width":u,"stroke-linecap":"round",fill:"none",style:O})),r("g",null,r("path",{class:[`${d}-progress-graph-circle-fill`,$===0&&`${d}-progress-graph-circle-fill--empty`],d:P,"stroke-width":u,"stroke-linecap":"round",fill:"none",style:W}))))),g?r("div",null,y.default?r("div",{class:`${d}-progress-custom-content`,role:"none"},y.default()):C!=="default"?r("div",{class:`${d}-progress-icon`,"aria-hidden":!0},r(ye,{clsPrefix:d},{default:()=>at[C]})):r("div",{class:`${d}-progress-text`,style:{color:b},role:"none"},r("span",{class:`${d}-progress-text__percentage`},$),r("span",{class:`${d}-progress-text__unit`},N))):null)}}}),st={success:r(Ce,null),error:r(xe,null),warning:r(_e,null),info:r(be,null)},nt=J({name:"ProgressLine",props:{clsPrefix:{type:String,required:!0},percentage:{type:Number,default:0},railColor:String,railStyle:[String,Object],fillColor:[String,Object],status:{type:String,required:!0},indicatorPlacement:{type:String,required:!0},indicatorTextColor:String,unit:{type:String,default:"%"},processing:{type:Boolean,required:!0},showIndicator:{type:Boolean,required:!0},height:[String,Number],railBorderRadius:[String,Number],fillBorderRadius:[String,Number]},setup(t,{slots:y}){const f=R(()=>X(t.height)),v=R(()=>{var n,u;return typeof t.fillColor=="object"?`linear-gradient(to right, ${(n=t.fillColor)===null||n===void 0?void 0:n.stops[0]} , ${(u=t.fillColor)===null||u===void 0?void 0:u.stops[1]})`:t.fillColor}),h=R(()=>t.railBorderRadius!==void 0?X(t.railBorderRadius):t.height!==void 0?X(t.height,{c:.5}):""),l=R(()=>t.fillBorderRadius!==void 0?X(t.fillBorderRadius):t.railBorderRadius!==void 0?X(t.railBorderRadius):t.height!==void 0?X(t.height,{c:.5}):"");return()=>{const{indicatorPlacement:n,railColor:u,railStyle:p,percentage:C,unit:$,indicatorTextColor:g,status:b,showIndicator:N,processing:_,clsPrefix:d}=t;return r("div",{class:`${d}-progress-content`,role:"none"},r("div",{class:`${d}-progress-graph`,"aria-hidden":!0},r("div",{class:[`${d}-progress-graph-line`,{[`${d}-progress-graph-line--indicator-${n}`]:!0}]},r("div",{class:`${d}-progress-graph-line-rail`,style:[{backgroundColor:u,height:f.value,borderRadius:h.value},p]},r("div",{class:[`${d}-progress-graph-line-fill`,_&&`${d}-progress-graph-line-fill--processing`],style:{maxWidth:`${t.percentage}%`,background:v.value,height:f.value,lineHeight:f.value,borderRadius:l.value}},n==="inside"?r("div",{class:`${d}-progress-graph-line-indicator`,style:{color:g}},y.default?y.default():`${C}${$}`):null)))),N&&n==="outside"?r("div",null,y.default?r("div",{class:`${d}-progress-custom-content`,style:{color:g},role:"none"},y.default()):b==="default"?r("div",{role:"none",class:`${d}-progress-icon ${d}-progress-icon--as-text`,style:{color:g}},C,$):r("div",{class:`${d}-progress-icon`,"aria-hidden":!0},r(ye,{clsPrefix:d},{default:()=>st[b]}))):null)}}});function me(t,y,f=100){return`m ${f/2} ${f/2-t} a ${t} ${t} 0 1 1 0 ${2*t} a ${t} ${t} 0 1 1 0 -${2*t}`}const ct=J({name:"ProgressMultipleCircle",props:{clsPrefix:{type:String,required:!0},viewBoxWidth:{type:Number,required:!0},percentage:{type:Array,default:[0]},strokeWidth:{type:Number,required:!0},circleGap:{type:Number,required:!0},showIndicator:{type:Boolean,required:!0},fillColor:{type:Array,default:()=>[]},railColor:{type:Array,default:()=>[]},railStyle:{type:Array,default:()=>[]}},setup(t,{slots:y}){const f=R(()=>t.percentage.map((l,n)=>`${Math.PI*l/100*(t.viewBoxWidth/2-t.strokeWidth/2*(1+2*n)-t.circleGap*n)*2}, ${t.viewBoxWidth*8}`)),v=(h,l)=>{const n=t.fillColor[l],u=typeof n=="object"?n.stops[0]:"",p=typeof n=="object"?n.stops[1]:"";return typeof t.fillColor[l]=="object"&&r("linearGradient",{id:`gradient-${l}`,x1:"100%",y1:"0%",x2:"0%",y2:"100%"},r("stop",{offset:"0%","stop-color":u}),r("stop",{offset:"100%","stop-color":p}))};return()=>{const{viewBoxWidth:h,strokeWidth:l,circleGap:n,showIndicator:u,fillColor:p,railColor:C,railStyle:$,percentage:g,clsPrefix:b}=t;return r("div",{class:`${b}-progress-content`,role:"none"},r("div",{class:`${b}-progress-graph`,"aria-hidden":!0},r("div",{class:`${b}-progress-graph-circle`},r("svg",{viewBox:`0 0 ${h} ${h}`},r("defs",null,g.map((N,_)=>v(N,_))),g.map((N,_)=>r("g",{key:_},r("path",{class:`${b}-progress-graph-circle-rail`,d:me(h/2-l/2*(1+2*_)-n*_,l,h),"stroke-width":l,"stroke-linecap":"round",fill:"none",style:[{strokeDashoffset:0,stroke:C[_]},$[_]]}),r("path",{class:[`${b}-progress-graph-circle-fill`,N===0&&`${b}-progress-graph-circle-fill--empty`],d:me(h/2-l/2*(1+2*_)-n*_,l,h),"stroke-width":l,"stroke-linecap":"round",fill:"none",style:{strokeDasharray:f.value[_],strokeDashoffset:0,stroke:typeof p[_]=="object"?`url(#gradient-${_})`:p[_]}})))))),u&&y.default?r("div",null,r("div",{class:`${b}-progress-text`},y.default())):null)}}}),ut=Y([x("progress",{display:"inline-block"},[x("progress-icon",`
 color: var(--n-icon-color);
 transition: color .3s var(--n-bezier);
 `),A("line",`
 width: 100%;
 display: block;
 `,[x("progress-content",`
 display: flex;
 align-items: center;
 `,[x("progress-graph",{flex:1})]),x("progress-custom-content",{marginLeft:"14px"}),x("progress-icon",`
 width: 30px;
 padding-left: 14px;
 height: var(--n-icon-size-line);
 line-height: var(--n-icon-size-line);
 font-size: var(--n-icon-size-line);
 `,[A("as-text",`
 color: var(--n-text-color-line-outer);
 text-align: center;
 width: 40px;
 font-size: var(--n-font-size);
 padding-left: 4px;
 transition: color .3s var(--n-bezier);
 `)])]),A("circle, dashboard",{width:"120px"},[x("progress-custom-content",`
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 display: flex;
 align-items: center;
 justify-content: center;
 `),x("progress-text",`
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
 `),x("progress-icon",`
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 display: flex;
 align-items: center;
 color: var(--n-icon-color);
 font-size: var(--n-icon-size-circle);
 `)]),A("multiple-circle",`
 width: 200px;
 color: inherit;
 `,[x("progress-text",`
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
 `)]),x("progress-content",{position:"relative"}),x("progress-graph",{position:"relative"},[x("progress-graph-circle",[Y("svg",{verticalAlign:"bottom"}),x("progress-graph-circle-fill",`
 stroke: var(--n-fill-color);
 transition:
 opacity .3s var(--n-bezier),
 stroke .3s var(--n-bezier),
 stroke-dasharray .3s var(--n-bezier);
 `,[A("empty",{opacity:0})]),x("progress-graph-circle-rail",`
 transition: stroke .3s var(--n-bezier);
 overflow: hidden;
 stroke: var(--n-rail-color);
 `)]),x("progress-graph-line",[A("indicator-inside",[x("progress-graph-line-rail",`
 height: 16px;
 line-height: 16px;
 border-radius: 10px;
 `,[x("progress-graph-line-fill",`
 height: inherit;
 border-radius: 10px;
 `),x("progress-graph-line-indicator",`
 background: #0000;
 white-space: nowrap;
 text-align: right;
 margin-left: 14px;
 margin-right: 14px;
 height: inherit;
 font-size: 12px;
 color: var(--n-text-color-line-inner);
 transition: color .3s var(--n-bezier);
 `)])]),A("indicator-inside-label",`
 height: 16px;
 display: flex;
 align-items: center;
 `,[x("progress-graph-line-rail",`
 flex: 1;
 transition: background-color .3s var(--n-bezier);
 `),x("progress-graph-line-indicator",`
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
 `)]),x("progress-graph-line-rail",`
 position: relative;
 overflow: hidden;
 height: var(--n-rail-height);
 border-radius: 5px;
 background-color: var(--n-rail-color);
 transition: background-color .3s var(--n-bezier);
 `,[x("progress-graph-line-fill",`
 background: var(--n-fill-color);
 position: relative;
 border-radius: 5px;
 height: inherit;
 width: 100%;
 max-width: 0%;
 transition:
 background-color .3s var(--n-bezier),
 max-width .2s var(--n-bezier);
 `,[A("processing",[Y("&::after",`
 content: "";
 background-image: var(--n-line-bg-processing);
 animation: progress-processing-animation 2s var(--n-bezier) infinite;
 `)])])])])])]),Y("@keyframes progress-processing-animation",`
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
 `)]),dt=Object.assign(Object.assign({},ie.props),{processing:Boolean,type:{type:String,default:"line"},gapDegree:Number,gapOffsetDegree:Number,status:{type:String,default:"default"},railColor:[String,Array],railStyle:[String,Array],color:[String,Array,Object],viewBoxWidth:{type:Number,default:100},strokeWidth:{type:Number,default:7},percentage:[Number,Array],unit:{type:String,default:"%"},showIndicator:{type:Boolean,default:!0},indicatorPosition:{type:String,default:"outside"},indicatorPlacement:{type:String,default:"outside"},indicatorTextColor:String,circleGap:{type:Number,default:1},height:Number,borderRadius:[String,Number],fillBorderRadius:[String,Number],offsetDegree:Number}),ft=J({name:"Progress",props:dt,setup(t){const y=R(()=>t.indicatorPlacement||t.indicatorPosition),f=R(()=>{if(t.gapDegree||t.gapDegree===0)return t.gapDegree;if(t.type==="dashboard")return 75}),{mergedClsPrefixRef:v,inlineThemeDisabled:h}=Se(t),l=ie("Progress","-progress",ut,rt,t,v),n=R(()=>{const{status:p}=t,{common:{cubicBezierEaseInOut:C},self:{fontSize:$,fontSizeCircle:g,railColor:b,railHeight:N,iconSizeCircle:_,iconSizeLine:d,textColorCircle:D,textColorLineInner:O,textColorLineOuter:P,lineBgProcessing:W,fontWeightCircle:E,[ue("iconColor",p)]:K,[ue("fillColor",p)]:M}}=l.value;return{"--n-bezier":C,"--n-fill-color":M,"--n-font-size":$,"--n-font-size-circle":g,"--n-font-weight-circle":E,"--n-icon-color":K,"--n-icon-size-circle":_,"--n-icon-size-line":d,"--n-line-bg-processing":W,"--n-rail-color":b,"--n-rail-height":N,"--n-text-color-circle":D,"--n-text-color-line-inner":O,"--n-text-color-line-outer":P}}),u=h?ke("progress",R(()=>t.status[0]),n,t):void 0;return{mergedClsPrefix:v,mergedIndicatorPlacement:y,gapDeg:f,cssVars:h?void 0:n,themeClass:u==null?void 0:u.themeClass,onRender:u==null?void 0:u.onRender}},render(){const{type:t,cssVars:y,indicatorTextColor:f,showIndicator:v,status:h,railColor:l,railStyle:n,color:u,percentage:p,viewBoxWidth:C,strokeWidth:$,mergedIndicatorPlacement:g,unit:b,borderRadius:N,fillBorderRadius:_,height:d,processing:D,circleGap:O,mergedClsPrefix:P,gapDeg:W,gapOffsetDegree:E,themeClass:K,$slots:M,onRender:Q}=this;return Q==null||Q(),r("div",{class:[K,`${P}-progress`,`${P}-progress--${t}`,`${P}-progress--${h}`],style:y,"aria-valuemax":100,"aria-valuemin":0,"aria-valuenow":p,role:t==="circle"||t==="line"||t==="dashboard"?"progressbar":"none"},t==="circle"||t==="dashboard"?r(ot,{clsPrefix:P,status:h,showIndicator:v,indicatorTextColor:f,railColor:l,fillColor:u,railStyle:n,offsetDegree:this.offsetDegree,percentage:p,viewBoxWidth:C,strokeWidth:$,gapDegree:W===void 0?t==="dashboard"?75:0:W,gapOffsetDegree:E,unit:b},M):t==="line"?r(nt,{clsPrefix:P,status:h,showIndicator:v,indicatorTextColor:f,railColor:l,fillColor:u,railStyle:n,percentage:p,processing:D,indicatorPlacement:g,unit:b,fillBorderRadius:_,railBorderRadius:N,height:d},M):t==="multiple-circle"?r(ct,{clsPrefix:P,strokeWidth:$,railColor:l,fillColor:u,railStyle:n,viewBoxWidth:C,percentage:p,showIndicator:v,circleGap:O},M):null)}}),pt=Y([Y("@keyframes spin-rotate",`
 from {
 transform: rotate(0);
 }
 to {
 transform: rotate(360deg);
 }
 `),x("spin-container",`
 position: relative;
 `,[x("spin-body",`
 position: absolute;
 top: 50%;
 left: 50%;
 transform: translateX(-50%) translateY(-50%);
 `,[Be()])]),x("spin-body",`
 display: inline-flex;
 align-items: center;
 justify-content: center;
 flex-direction: column;
 `),x("spin",`
 display: inline-flex;
 height: var(--n-size);
 width: var(--n-size);
 font-size: var(--n-size);
 color: var(--n-color);
 `,[A("rotate",`
 animation: spin-rotate 2s linear infinite;
 `)]),x("spin-description",`
 display: inline-block;
 font-size: var(--n-font-size);
 color: var(--n-text-color);
 transition: color .3s var(--n-bezier);
 margin-top: 8px;
 `),x("spin-content",`
 opacity: 1;
 transition: opacity .3s var(--n-bezier);
 pointer-events: all;
 `,[A("spinning",`
 user-select: none;
 -webkit-user-select: none;
 pointer-events: none;
 opacity: var(--n-opacity-spinning);
 `)])]),gt={small:20,medium:18,large:16},ht=Object.assign(Object.assign(Object.assign({},ie.props),{contentClass:String,contentStyle:[Object,String],description:String,size:{type:[String,Number],default:"medium"},show:{type:Boolean,default:!0},rotate:{type:Boolean,default:!0},spinning:{type:Boolean,validator:()=>!0,default:void 0},delay:Number}),je),mt=J({name:"Spin",props:ht,slots:Object,setup(t){const{mergedClsPrefixRef:y,inlineThemeDisabled:f}=Se(t),v=ie("Spin","-spin",pt,lt,t,y),h=R(()=>{const{size:p}=t,{common:{cubicBezierEaseInOut:C},self:$}=v.value,{opacitySpinning:g,color:b,textColor:N}=$,_=typeof p=="number"?We(p):$[ue("size",p)];return{"--n-bezier":C,"--n-opacity-spinning":g,"--n-size":_,"--n-color":b,"--n-text-color":N}}),l=f?ke("spin",R(()=>{const{size:p}=t;return typeof p=="number"?String(p):p[0]}),h,t):void 0,n=Ye(t,["spinning","show"]),u=B(!1);return Le(p=>{let C;if(n.value){const{delay:$}=t;if($){C=window.setTimeout(()=>{u.value=!0},$),p(()=>{clearTimeout(C)});return}}u.value=n.value}),{mergedClsPrefix:y,active:u,mergedStrokeWidth:R(()=>{const{strokeWidth:p}=t;if(p!==void 0)return p;const{size:C}=t;return gt[typeof C=="number"?"medium":C]}),cssVars:f?void 0:h,themeClass:l==null?void 0:l.themeClass,onRender:l==null?void 0:l.onRender}},render(){var t,y;const{$slots:f,mergedClsPrefix:v,description:h}=this,l=f.icon&&this.rotate,n=(h||f.description)&&r("div",{class:`${v}-spin-description`},h||((t=f.description)===null||t===void 0?void 0:t.call(f))),u=f.icon?r("div",{class:[`${v}-spin-body`,this.themeClass]},r("div",{class:[`${v}-spin`,l&&`${v}-spin--rotate`],style:f.default?"":this.cssVars},f.icon()),n):r("div",{class:[`${v}-spin-body`,this.themeClass]},r(Oe,{clsPrefix:v,style:f.default?"":this.cssVars,stroke:this.stroke,"stroke-width":this.mergedStrokeWidth,radius:this.radius,scale:this.scale,class:`${v}-spin`}),n);return(y=this.onRender)===null||y===void 0||y.call(this),f.default?r("div",{class:[`${v}-spin-container`,this.themeClass],style:this.cssVars},r("div",{class:[`${v}-spin-content`,this.active&&`${v}-spin-content--spinning`,this.contentClass],style:this.contentStyle},f),r(Te,{name:"fade-in-transition"},{default:()=>this.active?u:null})):u}}),vt={style:{color:"#18a058","font-size":"28px","font-weight":"bold"}},yt={style:{color:"#d03050","font-size":"28px","font-weight":"bold"}},bt={class:"analysis-card"},_t={class:"analysis-icon"},xt={class:"analysis-label"},Ct={class:"analysis-pct"},St={class:"code-block"},kt={class:"code-block"},$t={style:{"margin-top":"12px"}},zt={class:"code-block compact"},Nt={key:0},wt={style:{"margin-left":"8px","font-size":"12px"}},Rt={key:1},Pt={class:"code-block compact"},It=J({__name:"job-detail",setup(t){const y=Me(),f=qe(),v=Je(),h=Number(y.params.jobId),l=B(null),n=B("-"),u=B([]),p=B(!1),C=B(null),$=B(!1),g=B(null),b=B(!1),N=B(null),_=B(null),d=B(null),D=B(""),O=R(()=>!l.value||!l.value.total?0:l.value.passed/l.value.total*100),P=R(()=>{var c;const s=(c=g.value)==null?void 0:c.assertion_results;if(!s)return[];try{const e=JSON.parse(s);return Array.isArray(e)?e:[]}catch{return[]}}),W=[{key:"ENVIRONMENT",label:"环境问题",icon:"🌐",color:"#f0a020"},{key:"DATA_ISSUE",label:"数据问题",icon:"📝",color:"#2080f0"},{key:"BUG",label:"代码缺陷",icon:"🐛",color:"#d03050"},{key:"PERFORMANCE",label:"性能问题",icon:"⚡",color:"#8a2be2"},{key:"UNKNOWN",label:"未知",icon:"❓",color:"#999"}],E=R(()=>{var c;const s=((c=N.value)==null?void 0:c.categories)||{};return W.map(e=>{var S,T;return{...e,count:((S=s[e.key])==null?void 0:S.count)||0,percentage:((T=s[e.key])==null?void 0:T.percentage)||0}})}),K={DONE:"success",RUNNING:"info",FAILED:"error",PENDING:"default",CANCELLED:"warning"},M={DONE:"已完成",RUNNING:"运行中",FAILED:"失败",PENDING:"待执行",CANCELLED:"已取消"},Q={PASS:"success",FAIL:"error",ERROR:"warning",TIMEOUT:"warning",PENDING:"default"},$e={PASS:"通过",FAIL:"失败",ERROR:"异常",TIMEOUT:"超时",PENDING:"待执行"},de={status_mismatch:"状态码不一致",response_diff:"响应内容差异",assertion_failed:"断言失败",performance:"性能超限",timeout:"请求超时",connection_error:"连接异常",mock_error:"Mock 异常"},ze=[{label:"通过",value:"PASS"},{label:"失败",value:"FAIL"},{label:"异常",value:"ERROR"},{label:"超时",value:"TIMEOUT"}];function fe(s){return s==null?"#999":s<=.1?"#18a058":s<=.5?"#f0a020":"#d03050"}const Ne=[{title:"接口",key:"request_uri",render:s=>r("div",{style:"line-height:1.6"},[r("div",[r("b",{style:"margin-right:4px;color:#666"},s.request_method||"GET"),r("span",s.request_uri||"-")]),s.transaction_code?r("div",{style:"display:inline-block;background:#e8f0fe;color:#1a73e8;border-radius:4px;padding:1px 7px;font-size:12px;margin-top:2px;font-weight:500"},s.transaction_code):null])},{title:"来源录制",key:"source_recording_id",width:170,render:s=>s.source_recording_id?r(j,{size:6,align:"center"},()=>[r(V,{type:s.use_sub_invocation_mocks?"success":"default",size:"small"},()=>s.use_sub_invocation_mocks?"Mock 开启":"Mock 关闭"),r("span",`#${s.source_recording_id}${s.source_recording_sub_call_count!=null?` / 子调用 ${s.source_recording_sub_call_count}`:""}`)]):r("span",{style:"color:#ccc"},"-")},{title:"状态",key:"status",width:80,render:s=>r(V,{type:Q[s.status]??"default",size:"small"},()=>$e[s.status]||s.status)},{title:"失败分类",key:"failure_category",width:120,render:s=>s.failure_category?r("span",de[s.failure_category]||s.failure_category):r("span",{style:"color:#ccc"},"-")},{title:"Diff Score",key:"diff_score",width:100,render:s=>s.diff_score==null?r("span",{style:"color:#ccc"},"-"):r("span",{style:`color:${fe(s.diff_score)};font-weight:bold`},s.diff_score.toFixed(3))},{title:"状态码",key:"actual_status_code",width:80,render:s=>{var c;return r("span",((c=s.actual_status_code)==null?void 0:c.toString())||"-")}},{title:"耗时",key:"latency_ms",width:80,render:s=>r("span",s.latency_ms!=null?`${s.latency_ms}ms`:"-")},{title:"时间",key:"created_at",width:145,render:s=>r("span",{style:"font-size:12px;color:#999"},se(s.created_at))},{title:"对比",key:"actions",width:70,render:s=>r(Z,{size:"tiny",type:"primary",ghost:!0,onClick:()=>we(s)},()=>"对比")}];function le(s){if(!s)return"-";try{return JSON.stringify(JSON.parse(s),null,2)}catch{return s}}function we(s){g.value=s,$.value=!0,Re(s)}async function Re(s){if(_.value=null,d.value=null,D.value="",!!s.test_case_id)try{const c=await Ue.get(s.test_case_id);if(_.value=c.data,c.data.source_recording_id){const e=await Fe.getRecording(c.data.source_recording_id);d.value=e.data,D.value=He(Xe(e.data.sub_calls))}}catch{_.value=null,d.value=null,D.value=""}}async function Pe(){var s,c;try{const e=await te.getReport(h),S=new Blob([e.data],{type:"text/html;charset=utf-8"}),T=URL.createObjectURL(S),q=document.createElement("a");q.href=T,q.download=`replay_report_${h}.html`,document.body.appendChild(q),q.click(),document.body.removeChild(q),setTimeout(()=>URL.revokeObjectURL(T),1e4)}catch(e){v.error(((c=(s=e.response)==null?void 0:s.data)==null?void 0:c.detail)||"导出报告失败")}}async function Ie(){if(!(!l.value||l.value.failed===0&&l.value.errored===0)){b.value=!0;try{const s=await te.getAnalysis(h);N.value=s.data}catch{N.value=null}finally{b.value=!1}}}async function pe(){var s,c;try{const e=await te.get(h);if(l.value=e.data,e.data.application_id!=null){const S=await Ge.get(e.data.application_id);n.value=S.data.name}else n.value="-"}catch(e){v.error(((c=(s=e.response)==null?void 0:s.data)==null?void 0:c.detail)||"加载回放任务失败")}await Promise.all([ge(),Ie()])}async function ge(){var s,c;p.value=!0;try{const e={limit:200};C.value&&(e.status=C.value);const S=await te.getResults(h,e);u.value=S.data}catch(e){u.value=[],v.error(((c=(s=e.response)==null?void 0:s.data)==null?void 0:c.detail)||"加载结果详情失败")}finally{p.value=!1}}return Ee(()=>{pe()}),(s,c)=>(I(),G(ee,null,[o(i(j),{vertical:"",size:16},{default:a(()=>[o(i(j),{justify:"space-between",align:"center"},{default:a(()=>[o(i(Ke),null,{default:a(()=>[o(i(he),{onClick:c[0]||(c[0]=e=>i(f).push("/replay/history"))},{default:a(()=>[...c[5]||(c[5]=[k("回放历史",-1)])]),_:1}),o(i(he),null,{default:a(()=>[k("任务 #"+m(i(h)),1)]),_:1})]),_:1}),o(i(j),null,{default:a(()=>[o(i(Z),{onClick:pe},{default:a(()=>[...c[6]||(c[6]=[k("刷新",-1)])]),_:1}),o(i(Z),{onClick:c[1]||(c[1]=e=>i(f).push("/replay/history"))},{default:a(()=>[...c[7]||(c[7]=[k("返回历史",-1)])]),_:1}),o(i(Z),{type:"info",onClick:Pe},{default:a(()=>[...c[8]||(c[8]=[k("导出 HTML 报告",-1)])]),_:1})]),_:1})]),_:1}),l.value?(I(),F(i(L),{key:0,title:l.value.name||`回放任务 #${i(h)}`},{"header-extra":a(()=>[o(i(V),{type:K[l.value.status]||"default"},{default:a(()=>[k(m(M[l.value.status]||l.value.status),1)]),_:1},8,["type"])]),default:a(()=>{var e;return[o(i(ne),{bordered:"",column:3,size:"small"},{default:a(()=>[o(i(w),{label:"回放应用"},{default:a(()=>[k(m(n.value),1)]),_:1}),o(i(w),{label:"开始时间"},{default:a(()=>[k(m(i(se)(l.value.started_at)),1)]),_:1}),o(i(w),{label:"完成时间"},{default:a(()=>[k(m(i(se)(l.value.finished_at)),1)]),_:1}),o(i(w),{label:"并发数"},{default:a(()=>[k(m(l.value.concurrency),1)]),_:1}),o(i(w),{label:"超时"},{default:a(()=>[k(m(l.value.timeout_ms)+"ms",1)]),_:1}),o(i(w),{label:"智能降噪"},{default:a(()=>[k(m(l.value.smart_noise_reduction?"开启":"关闭"),1)]),_:1})]),_:1}),(e=l.value.ignore_fields)!=null&&e.length?(I(),F(i(j),{key:0,style:{"margin-top":"12px"}},{default:a(()=>[c[9]||(c[9]=z("span",{style:{color:"#666","font-size":"13px"}},"忽略字段：",-1)),(I(!0),G(ee,null,ae(l.value.ignore_fields,S=>(I(),F(i(V),{key:S,size:"small",type:"default"},{default:a(()=>[k(m(S),1)]),_:2},1024))),128))]),_:1})):U("",!0)]}),_:1},8,["title"])):U("",!0),o(i(ce),{cols:4,"x-gap":16},{default:a(()=>[o(i(H),null,{default:a(()=>[o(i(L),{style:{"text-align":"center"}},{default:a(()=>{var e;return[o(i(re),{label:"总计",value:((e=l.value)==null?void 0:e.total)||0},null,8,["value"])]}),_:1})]),_:1}),o(i(H),null,{default:a(()=>[o(i(L),{style:{"text-align":"center"}},{default:a(()=>[o(i(re),{label:"通过"},{default:a(()=>{var e;return[z("span",vt,m(((e=l.value)==null?void 0:e.passed)||0),1)]}),_:1})]),_:1})]),_:1}),o(i(H),null,{default:a(()=>[o(i(L),{style:{"text-align":"center"}},{default:a(()=>[o(i(re),{label:"失败"},{default:a(()=>{var e;return[z("span",yt,m(((e=l.value)==null?void 0:e.failed)||0),1)]}),_:1})]),_:1})]),_:1}),o(i(H),null,{default:a(()=>[o(i(L),{style:{"text-align":"center"}},{default:a(()=>[o(i(re),{label:"通过率"},{default:a(()=>[z("span",{style:oe({color:O.value>=90?"#18a058":O.value>=60?"#f0a020":"#d03050",fontSize:"28px",fontWeight:"bold"})},m(O.value.toFixed(1))+"% ",5)]),_:1})]),_:1})]),_:1})]),_:1}),l.value&&(l.value.failed>0||l.value.errored>0)?(I(),F(i(L),{key:1,title:"失败原因分析"},{default:a(()=>[o(i(mt),{show:b.value},{default:a(()=>[o(i(ce),{cols:5,"x-gap":12},{default:a(()=>[(I(!0),G(ee,null,ae(E.value,e=>(I(),F(i(H),{key:e.key},{default:a(()=>[z("div",bt,[z("div",_t,m(e.icon),1),z("div",xt,m(e.label),1),z("div",{class:"analysis-count",style:oe({color:e.color})},m(e.count),5),o(i(ft),{type:"line",percentage:e.percentage,color:e.color,"rail-color":"#f0f0f0","indicator-placement":"inside",style:{"margin-top":"6px"}},null,8,["percentage","color"]),z("div",Ct,m(e.percentage.toFixed(0))+"%",1)])]),_:2},1024))),128))]),_:1})]),_:1},8,["show"])]),_:1})):U("",!0),o(i(L),{title:"逐条结果"},{"header-extra":a(()=>[o(i(j),null,{default:a(()=>[o(i(Qe),{value:C.value,"onUpdate:value":[c[2]||(c[2]=e=>C.value=e),ge],options:ze,clearable:"",placeholder:"按状态筛选",style:{width:"160px"}},null,8,["value"])]),_:1})]),default:a(()=>[o(i(Ze),{columns:Ne,data:u.value,loading:p.value,pagination:{pageSize:15},size:"small"},null,8,["data","loading"])]),_:1})]),_:1}),o(i(Ae),{show:$.value,"onUpdate:show":c[4]||(c[4]=e=>$.value=e),preset:"card",style:{width:"1000px"},title:"结果对比详情"},{default:a(()=>[o(i(j),{vertical:"",size:12},{default:a(()=>[o(i(ne),{bordered:"",column:3,size:"small"},{default:a(()=>[o(i(w),{label:"接口"},{default:a(()=>{var e,S;return[z("b",null,m((e=g.value)==null?void 0:e.request_method),1),k(" "+m((S=g.value)==null?void 0:S.request_uri),1)]}),_:1}),o(i(w),{label:"状态码"},{default:a(()=>{var e;return[k(m(((e=g.value)==null?void 0:e.actual_status_code)||"-"),1)]}),_:1}),o(i(w),{label:"Diff Score"},{default:a(()=>{var e,S;return[z("span",{style:oe({color:fe((e=g.value)==null?void 0:e.diff_score)})},m(((S=g.value)==null?void 0:S.diff_score)!=null?g.value.diff_score.toFixed(3):"-"),5)]}),_:1}),o(i(w),{label:"来源录制"},{default:a(()=>[o(i(j),{align:"center",size:8},{default:a(()=>{var e,S;return[o(i(V),{type:(e=g.value)!=null&&e.use_sub_invocation_mocks?"success":"default",size:"small"},{default:a(()=>{var T;return[k(m((T=g.value)!=null&&T.use_sub_invocation_mocks?"Mock 开启":"Mock 关闭"),1)]}),_:1},8,["type"]),z("span",null,m((S=g.value)!=null&&S.source_recording_id?`#${g.value.source_recording_id}`:"-"),1)]}),_:1})]),_:1}),o(i(w),{label:"子调用数"},{default:a(()=>{var e;return[k(m(((e=g.value)==null?void 0:e.source_recording_sub_call_count)??"-"),1)]}),_:1}),o(i(w),{label:"失败分类",span:2},{default:a(()=>{var e,S;return[k(m(de[((e=g.value)==null?void 0:e.failure_category)||""]||((S=g.value)==null?void 0:S.failure_category)||"-"),1)]}),_:1}),o(i(w),{label:"耗时"},{default:a(()=>{var e;return[k(m(((e=g.value)==null?void 0:e.latency_ms)!=null?`${g.value.latency_ms}ms`:"-"),1)]}),_:1})]),_:1}),o(i(ce),{cols:2,"x-gap":16},{default:a(()=>[o(i(H),null,{default:a(()=>[o(i(L),{title:"期望响应（PL2 录制）",size:"small"},{default:a(()=>{var e;return[z("pre",St,m(le((e=g.value)==null?void 0:e.expected_response)),1)]}),_:1})]),_:1}),o(i(H),null,{default:a(()=>[o(i(L),{title:"实际响应（VT 回放）",size:"small"},{default:a(()=>{var e;return[z("pre",kt,m(le((e=g.value)==null?void 0:e.actual_response)),1)]}),_:1})]),_:1})]),_:1}),d.value?(I(),F(i(L),{key:0,title:"来源录制链路",size:"small"},{"header-extra":a(()=>[o(i(j),{align:"center",size:8},{default:a(()=>[o(i(V),{type:"info",size:"small"},{default:a(()=>{var e;return[k("来源用例 #"+m(((e=_.value)==null?void 0:e.id)||"-"),1)]}),_:1}),d.value.id?(I(),F(i(Z),{key:0,size:"small",onClick:c[3]||(c[3]=e=>i(f).push(`/recording/recordings/${d.value.id}`))},{default:a(()=>[...c[10]||(c[10]=[k(" 打开录制详情 ",-1)])]),_:1})):U("",!0)]),_:1})]),default:a(()=>[o(i(ne),{bordered:"",column:2,size:"small"},{default:a(()=>[o(i(w),{label:"请求"},{default:a(()=>[k(m(d.value.request_method)+" "+m(d.value.request_uri),1)]),_:1}),o(i(w),{label:"交易码"},{default:a(()=>[k(m(d.value.transaction_code||"-"),1)]),_:1}),o(i(w),{label:"治理状态"},{default:a(()=>[k(m(d.value.governance_status),1)]),_:1}),o(i(w),{label:"子调用概览"},{default:a(()=>[k(m(D.value||"-"),1)]),_:1})]),_:1}),z("div",$t,[o(Ve,{"sub-calls":d.value.sub_calls},null,8,["sub-calls"])])]),_:1})):U("",!0),o(i(L),{title:"差异详情",size:"small"},{default:a(()=>[o(i(j),{vertical:""},{default:a(()=>{var e,S;return[z("div",null,[c[11]||(c[11]=z("div",{class:"section-title"},"Diff 结果",-1)),z("pre",zt,m(le((e=g.value)==null?void 0:e.diff_result)),1)]),P.value.length>0?(I(),G("div",Nt,[c[12]||(c[12]=z("div",{class:"section-title"},"断言结果",-1)),o(i(j),{vertical:"",size:6},{default:a(()=>[(I(!0),G(ee,null,ae(P.value,(T,q)=>(I(),G("div",{key:q},[o(i(V),{type:T.passed?"success":"error",size:"small"},{default:a(()=>[k(m(T.passed?"通过":"失败"),1)]),_:2},1032,["type"]),z("span",wt,m(T.message),1)]))),128))]),_:1})])):U("",!0),(S=g.value)!=null&&S.failure_reason?(I(),G("div",Rt,[c[13]||(c[13]=z("div",{class:"section-title"},"失败原因",-1)),z("pre",Pt,m(g.value.failure_reason),1)])):U("",!0)]}),_:1})]),_:1})]),_:1})]),_:1},8,["show"])],64))}}),Zt=et(It,[["__scopeId","data-v-21d3b5a2"]]);export{Zt as default};
