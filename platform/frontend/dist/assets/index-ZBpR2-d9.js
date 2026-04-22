import{a as ba,o as te,g as v,i as B,n as pe,_ as Ie,$ as wa,a0 as ya,a1 as _a,d as We,h as b,a2 as xa,a3 as ka,u as Ca,j as Ye,a4 as Sa,r as x,a5 as Fe,I as Ra,l as He,a6 as za,m as T,t as he,a7 as me,a8 as ge,a9 as Ae,v as Na,H as Ta,P as Ee,O as l,K as s,L as t,aa as Da,F as je,W as Aa,Z as be,M as y,U as p,J as Pe,T as U,R as G,Q as Me,ab as Q}from"./index-DKfkuiLi.js";import{a as X}from"./applications-C9GHbAuo.js";import{f as Ma}from"./format-Adq5_zH5.js";import{u as Ba}from"./user-DjIfHAmW.js";import{t as Va,d as Ua,u as $a,r as Ia}from"./tableSort-BCDb-wUZ.js";import{u as Fa,N as R}from"./index-BZmDg5FO.js";import{N as Ha}from"./headers-BWz0Ui38.js";import{N as Oe}from"./text-BMtlWM7z.js";import{N as Ea,a as we}from"./Grid-DUchxvYI.js";import{N as ye}from"./Statistic-BycnHVZv.js";import{N as ja}from"./DataTable-Ck9AFGkd.js";import{N as Le,a as Pa}from"./Select-Dc2P8y1a.js";import{N as Z}from"./Alert-cz0mTpc-.js";import{N as Oa,a as _}from"./FormItem-zSy9Kh2q.js";import{N as Ke}from"./InputNumber-Cmy2Qx_M.js";import{B as La,a as Ka,b as Xa,d as Be,N as q}from"./Space-C_ahS7-l.js";import{u as qa}from"./get-C9z6N27c.js";import{N as Wa}from"./Popconfirm-L1ZhIU8b.js";import{_ as Ya}from"./_plugin-vue_export-helper-DlAUqK2U.js";import"./light-77MxVeTW.js";import"./Tooltip-Cx9wBadY.js";import"./Dropdown-BMHBmLUg.js";import"./Add-Dit9hlKf.js";const Ja={railHeight:"4px",railWidthVertical:"4px",handleSize:"18px",dotHeight:"8px",dotWidth:"8px",dotBorderRadius:"4px"};function Ga(i){const c="rgba(0, 0, 0, .85)",$="0 2px 8px 0 rgba(0, 0, 0, 0.12)",{railColor:w,primaryColor:g,baseColor:h,cardColor:I,modalColor:C,popoverColor:j,borderRadius:F,fontSize:P,opacityDisabled:H}=i;return Object.assign(Object.assign({},Ja),{fontSize:P,markFontSize:P,railColor:w,railColorHover:w,fillColor:g,fillColorHover:g,opacityDisabled:H,handleColor:"#FFF",dotColor:I,dotColorModal:C,dotColorPopover:j,handleBoxShadow:"0 1px 4px 0 rgba(0, 0, 0, 0.3), inset 0 0 1px 0 rgba(0, 0, 0, 0.05)",handleBoxShadowHover:"0 1px 4px 0 rgba(0, 0, 0, 0.3), inset 0 0 1px 0 rgba(0, 0, 0, 0.05)",handleBoxShadowActive:"0 1px 4px 0 rgba(0, 0, 0, 0.3), inset 0 0 1px 0 rgba(0, 0, 0, 0.05)",handleBoxShadowFocus:"0 1px 4px 0 rgba(0, 0, 0, 0.3), inset 0 0 1px 0 rgba(0, 0, 0, 0.05)",indicatorColor:c,indicatorBoxShadow:$,indicatorTextColor:h,indicatorBorderRadius:F,dotBorder:`2px solid ${w}`,dotBorderActive:`2px solid ${g}`,dotBoxShadow:""})}const Qa={common:ba,self:Ga},Za=te([v("slider",`
 display: block;
 padding: calc((var(--n-handle-size) - var(--n-rail-height)) / 2) 0;
 position: relative;
 z-index: 0;
 width: 100%;
 cursor: pointer;
 user-select: none;
 -webkit-user-select: none;
 `,[B("reverse",[v("slider-handles",[v("slider-handle-wrapper",`
 transform: translate(50%, -50%);
 `)]),v("slider-dots",[v("slider-dot",`
 transform: translateX(50%, -50%);
 `)]),B("vertical",[v("slider-handles",[v("slider-handle-wrapper",`
 transform: translate(-50%, -50%);
 `)]),v("slider-marks",[v("slider-mark",`
 transform: translateY(calc(-50% + var(--n-dot-height) / 2));
 `)]),v("slider-dots",[v("slider-dot",`
 transform: translateX(-50%) translateY(0);
 `)])])]),B("vertical",`
 box-sizing: content-box;
 padding: 0 calc((var(--n-handle-size) - var(--n-rail-height)) / 2);
 width: var(--n-rail-width-vertical);
 height: 100%;
 `,[v("slider-handles",`
 top: calc(var(--n-handle-size) / 2);
 right: 0;
 bottom: calc(var(--n-handle-size) / 2);
 left: 0;
 `,[v("slider-handle-wrapper",`
 top: unset;
 left: 50%;
 transform: translate(-50%, 50%);
 `)]),v("slider-rail",`
 height: 100%;
 `,[pe("fill",`
 top: unset;
 right: 0;
 bottom: unset;
 left: 0;
 `)]),B("with-mark",`
 width: var(--n-rail-width-vertical);
 margin: 0 32px 0 8px;
 `),v("slider-marks",`
 top: calc(var(--n-handle-size) / 2);
 right: unset;
 bottom: calc(var(--n-handle-size) / 2);
 left: 22px;
 font-size: var(--n-mark-font-size);
 `,[v("slider-mark",`
 transform: translateY(50%);
 white-space: nowrap;
 `)]),v("slider-dots",`
 top: calc(var(--n-handle-size) / 2);
 right: unset;
 bottom: calc(var(--n-handle-size) / 2);
 left: 50%;
 `,[v("slider-dot",`
 transform: translateX(-50%) translateY(50%);
 `)])]),B("disabled",`
 cursor: not-allowed;
 opacity: var(--n-opacity-disabled);
 `,[v("slider-handle",`
 cursor: not-allowed;
 `)]),B("with-mark",`
 width: 100%;
 margin: 8px 0 32px 0;
 `),te("&:hover",[v("slider-rail",{backgroundColor:"var(--n-rail-color-hover)"},[pe("fill",{backgroundColor:"var(--n-fill-color-hover)"})]),v("slider-handle",{boxShadow:"var(--n-handle-box-shadow-hover)"})]),B("active",[v("slider-rail",{backgroundColor:"var(--n-rail-color-hover)"},[pe("fill",{backgroundColor:"var(--n-fill-color-hover)"})]),v("slider-handle",{boxShadow:"var(--n-handle-box-shadow-hover)"})]),v("slider-marks",`
 position: absolute;
 top: 18px;
 left: calc(var(--n-handle-size) / 2);
 right: calc(var(--n-handle-size) / 2);
 `,[v("slider-mark",`
 position: absolute;
 transform: translateX(-50%);
 white-space: nowrap;
 `)]),v("slider-rail",`
 width: 100%;
 position: relative;
 height: var(--n-rail-height);
 background-color: var(--n-rail-color);
 transition: background-color .3s var(--n-bezier);
 border-radius: calc(var(--n-rail-height) / 2);
 `,[pe("fill",`
 position: absolute;
 top: 0;
 bottom: 0;
 border-radius: calc(var(--n-rail-height) / 2);
 transition: background-color .3s var(--n-bezier);
 background-color: var(--n-fill-color);
 `)]),v("slider-handles",`
 position: absolute;
 top: 0;
 right: calc(var(--n-handle-size) / 2);
 bottom: 0;
 left: calc(var(--n-handle-size) / 2);
 `,[v("slider-handle-wrapper",`
 outline: none;
 position: absolute;
 top: 50%;
 transform: translate(-50%, -50%);
 cursor: pointer;
 display: flex;
 `,[v("slider-handle",`
 height: var(--n-handle-size);
 width: var(--n-handle-size);
 border-radius: 50%;
 overflow: hidden;
 transition: box-shadow .2s var(--n-bezier), background-color .3s var(--n-bezier);
 background-color: var(--n-handle-color);
 box-shadow: var(--n-handle-box-shadow);
 `,[te("&:hover",`
 box-shadow: var(--n-handle-box-shadow-hover);
 `)]),te("&:focus",[v("slider-handle",`
 box-shadow: var(--n-handle-box-shadow-focus);
 `,[te("&:hover",`
 box-shadow: var(--n-handle-box-shadow-active);
 `)])])])]),v("slider-dots",`
 position: absolute;
 top: 50%;
 left: calc(var(--n-handle-size) / 2);
 right: calc(var(--n-handle-size) / 2);
 `,[B("transition-disabled",[v("slider-dot","transition: none;")]),v("slider-dot",`
 transition:
 border-color .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 position: absolute;
 transform: translate(-50%, -50%);
 height: var(--n-dot-height);
 width: var(--n-dot-width);
 border-radius: var(--n-dot-border-radius);
 overflow: hidden;
 box-sizing: border-box;
 border: var(--n-dot-border);
 background-color: var(--n-dot-color);
 `,[B("active","border: var(--n-dot-border-active);")])])]),v("slider-handle-indicator",`
 font-size: var(--n-font-size);
 padding: 6px 10px;
 border-radius: var(--n-indicator-border-radius);
 color: var(--n-indicator-text-color);
 background-color: var(--n-indicator-color);
 box-shadow: var(--n-indicator-box-shadow);
 `,[Ie()]),v("slider-handle-indicator",`
 font-size: var(--n-font-size);
 padding: 6px 10px;
 border-radius: var(--n-indicator-border-radius);
 color: var(--n-indicator-text-color);
 background-color: var(--n-indicator-color);
 box-shadow: var(--n-indicator-box-shadow);
 `,[B("top",`
 margin-bottom: 12px;
 `),B("right",`
 margin-left: 12px;
 `),B("bottom",`
 margin-top: 12px;
 `),B("left",`
 margin-right: 12px;
 `),Ie()]),wa(v("slider",[v("slider-dot","background-color: var(--n-dot-color-modal);")])),ya(v("slider",[v("slider-dot","background-color: var(--n-dot-color-popover);")]))]);function Xe(i){return window.TouchEvent&&i instanceof window.TouchEvent}function qe(){const i=new Map,c=$=>w=>{i.set($,w)};return _a(()=>{i.clear()}),[i,c]}const et=0,at=Object.assign(Object.assign({},Ye.props),{to:Be.propTo,defaultValue:{type:[Number,Array],default:0},marks:Object,disabled:{type:Boolean,default:void 0},formatTooltip:Function,keyboard:{type:Boolean,default:!0},min:{type:Number,default:0},max:{type:Number,default:100},step:{type:[Number,String],default:1},range:Boolean,value:[Number,Array],placement:String,showTooltip:{type:Boolean,default:void 0},tooltip:{type:Boolean,default:!0},vertical:Boolean,reverse:Boolean,"onUpdate:value":[Function,Array],onUpdateValue:[Function,Array],onDragstart:[Function],onDragend:[Function]}),tt=We({name:"Slider",props:at,slots:Object,setup(i){const{mergedClsPrefixRef:c,namespaceRef:$,inlineThemeDisabled:w}=Ca(i),g=Ye("Slider","-slider",Za,Qa,i,c),h=x(null),[I,C]=qe(),[j,F]=qe(),P=x(new Set),H=Sa(i),{mergedDisabledRef:O}=H,oe=T(()=>{const{step:a}=i;if(Number(a)<=0||a==="mark")return 0;const o=a.toString();let r=0;return o.includes(".")&&(r=o.length-o.indexOf(".")-1),r}),u=x(i.defaultValue),_e=Na(i,"value"),ee=qa(_e,u),D=T(()=>{const{value:a}=ee;return(i.range?a:[a]).map(M)}),L=T(()=>D.value.length>2),xe=T(()=>i.placement===void 0?i.vertical?"right":"top":i.placement),le=T(()=>{const{marks:a}=i;return a?Object.keys(a).map(Number.parseFloat):null}),A=x(-1),ne=x(-1),V=x(-1),z=x(!1),W=x(!1),ae=T(()=>{const{vertical:a,reverse:o}=i;return a?o?"top":"bottom":o?"right":"left"}),ke=T(()=>{if(L.value)return;const a=D.value,o=ie(i.range?Math.min(...a):i.min),r=ie(i.range?Math.max(...a):a[0]),{value:f}=ae;return i.vertical?{[f]:`${o}%`,height:`${r-o}%`}:{[f]:`${o}%`,width:`${r-o}%`}}),Ce=T(()=>{const a=[],{marks:o}=i;if(o){const r=D.value.slice();r.sort((N,S)=>N-S);const{value:f}=ae,{value:m}=L,{range:k}=i,E=m?()=>!1:N=>k?N>=r[0]&&N<=r[r.length-1]:N<=r[0];for(const N of Object.keys(o)){const S=Number(N);a.push({active:E(S),key:S,label:o[N],style:{[f]:`${ie(S)}%`}})}}return a});function Se(a,o){const r=ie(a),{value:f}=ae;return{[f]:`${r}%`,zIndex:o===A.value?1:0}}function re(a){return i.showTooltip||V.value===a||A.value===a&&z.value}function Re(a){return z.value?!(A.value===a&&ne.value===a):!0}function ze(a){var o;~a&&(A.value=a,(o=I.get(a))===null||o===void 0||o.focus())}function Ne(){j.forEach((a,o)=>{re(o)&&a.syncPosition()})}function se(a){const{"onUpdate:value":o,onUpdateValue:r}=i,{nTriggerFormInput:f,nTriggerFormChange:m}=H;r&&he(r,a),o&&he(o,a),u.value=a,f(),m()}function d(a){const{range:o}=i;if(o){if(Array.isArray(a)){const{value:r}=D;a.join()!==r.join()&&se(a)}}else Array.isArray(a)||D.value[0]!==a&&se(a)}function e(a,o){if(i.range){const r=D.value.slice();r.splice(o,1,a),d(r)}else d(a)}function n(a,o,r){const f=r!==void 0;r||(r=a-o>0?1:-1);const m=le.value||[],{step:k}=i;if(k==="mark"){const S=de(a,m.concat(o),f?r:void 0);return S?S.value:o}if(k<=0)return o;const{value:E}=oe;let N;if(f){const S=Number((o/k).toFixed(E)),K=Math.floor(S),Te=S>K?K:K-1,De=S<K?K:K+1;N=de(o,[Number((Te*k).toFixed(E)),Number((De*k).toFixed(E)),...m],r)}else{const S=Ge(a);N=de(a,[...m,S])}return N?M(N.value):o}function M(a){return Math.min(i.max,Math.max(i.min,a))}function ie(a){const{max:o,min:r}=i;return(a-r)/(o-r)*100}function Je(a){const{max:o,min:r}=i;return r+(o-r)*a}function Ge(a){const{step:o,min:r}=i;if(Number(o)<=0||o==="mark")return a;const f=Math.round((a-r)/o)*o+r;return Number(f.toFixed(oe.value))}function de(a,o=le.value,r){if(!(o!=null&&o.length))return null;let f=null,m=-1;for(;++m<o.length;){const k=o[m]-a,E=Math.abs(k);(r===void 0||k*r>0)&&(f===null||E<f.distance)&&(f={index:m,distance:E,value:o[m]})}return f}function Ve(a){const o=h.value;if(!o)return;const r=Xe(a)?a.touches[0]:a,f=o.getBoundingClientRect();let m;return i.vertical?m=(f.bottom-r.clientY)/f.height:m=(r.clientX-f.left)/f.width,i.reverse&&(m=1-m),Je(m)}function Qe(a){if(O.value||!i.keyboard)return;const{vertical:o,reverse:r}=i;switch(a.key){case"ArrowUp":a.preventDefault(),ue(o&&r?-1:1);break;case"ArrowRight":a.preventDefault(),ue(!o&&r?-1:1);break;case"ArrowDown":a.preventDefault(),ue(o&&r?1:-1);break;case"ArrowLeft":a.preventDefault(),ue(!o&&r?1:-1);break}}function ue(a){const o=A.value;if(o===-1)return;const{step:r}=i,f=D.value[o],m=Number(r)<=0||r==="mark"?f:f+r*a;e(n(m,f,a>0?1:-1),o)}function Ze(a){var o,r;if(O.value||!Xe(a)&&a.button!==et)return;const f=Ve(a);if(f===void 0)return;const m=D.value.slice(),k=i.range?(r=(o=de(f,m))===null||o===void 0?void 0:o.index)!==null&&r!==void 0?r:-1:0;k!==-1&&(a.preventDefault(),ze(k),ea(),e(n(f,D.value[k]),k))}function ea(){z.value||(z.value=!0,i.onDragstart&&he(i.onDragstart),me("touchend",document,fe),me("mouseup",document,fe),me("touchmove",document,ve),me("mousemove",document,ve))}function ce(){z.value&&(z.value=!1,i.onDragend&&he(i.onDragend),ge("touchend",document,fe),ge("mouseup",document,fe),ge("touchmove",document,ve),ge("mousemove",document,ve))}function ve(a){const{value:o}=A;if(!z.value||o===-1){ce();return}const r=Ve(a);r!==void 0&&e(n(r,D.value[o]),o)}function fe(){ce()}function aa(a){A.value=a,O.value||(V.value=a)}function ta(a){A.value===a&&(A.value=-1,ce()),V.value===a&&(V.value=-1)}function oa(a){V.value=a}function la(a){V.value===a&&(V.value=-1)}Fe(A,(a,o)=>void Ae(()=>ne.value=o)),Fe(ee,()=>{if(i.marks){if(W.value)return;W.value=!0,Ae(()=>{W.value=!1})}Ae(Ne)}),Ra(()=>{ce()});const Ue=T(()=>{const{self:{markFontSize:a,railColor:o,railColorHover:r,fillColor:f,fillColorHover:m,handleColor:k,opacityDisabled:E,dotColor:N,dotColorModal:S,handleBoxShadow:K,handleBoxShadowHover:Te,handleBoxShadowActive:De,handleBoxShadowFocus:na,dotBorder:ra,dotBoxShadow:sa,railHeight:ia,railWidthVertical:da,handleSize:ua,dotHeight:ca,dotWidth:va,dotBorderRadius:fa,fontSize:pa,dotBorderActive:ha,dotColorPopover:ma},common:{cubicBezierEaseInOut:ga}}=g.value;return{"--n-bezier":ga,"--n-dot-border":ra,"--n-dot-border-active":ha,"--n-dot-border-radius":fa,"--n-dot-box-shadow":sa,"--n-dot-color":N,"--n-dot-color-modal":S,"--n-dot-color-popover":ma,"--n-dot-height":ca,"--n-dot-width":va,"--n-fill-color":f,"--n-fill-color-hover":m,"--n-font-size":pa,"--n-handle-box-shadow":K,"--n-handle-box-shadow-active":De,"--n-handle-box-shadow-focus":na,"--n-handle-box-shadow-hover":Te,"--n-handle-color":k,"--n-handle-size":ua,"--n-opacity-disabled":E,"--n-rail-color":o,"--n-rail-color-hover":r,"--n-rail-height":ia,"--n-rail-width-vertical":da,"--n-mark-font-size":a}}),Y=w?He("slider",void 0,Ue,i):void 0,$e=T(()=>{const{self:{fontSize:a,indicatorColor:o,indicatorBoxShadow:r,indicatorTextColor:f,indicatorBorderRadius:m}}=g.value;return{"--n-font-size":a,"--n-indicator-border-radius":m,"--n-indicator-box-shadow":r,"--n-indicator-color":o,"--n-indicator-text-color":f}}),J=w?He("slider-indicator",void 0,$e,i):void 0;return{mergedClsPrefix:c,namespace:$,uncontrolledValue:u,mergedValue:ee,mergedDisabled:O,mergedPlacement:xe,isMounted:za(),adjustedTo:Be(i),dotTransitionDisabled:W,markInfos:Ce,isShowTooltip:re,shouldKeepTooltipTransition:Re,handleRailRef:h,setHandleRefs:C,setFollowerRefs:F,fillStyle:ke,getHandleStyle:Se,activeIndex:A,arrifiedValues:D,followerEnabledIndexSet:P,handleRailMouseDown:Ze,handleHandleFocus:aa,handleHandleBlur:ta,handleHandleMouseEnter:oa,handleHandleMouseLeave:la,handleRailKeyDown:Qe,indicatorCssVars:w?void 0:$e,indicatorThemeClass:J==null?void 0:J.themeClass,indicatorOnRender:J==null?void 0:J.onRender,cssVars:w?void 0:Ue,themeClass:Y==null?void 0:Y.themeClass,onRender:Y==null?void 0:Y.onRender}},render(){var i;const{mergedClsPrefix:c,themeClass:$,formatTooltip:w}=this;return(i=this.onRender)===null||i===void 0||i.call(this),b("div",{class:[`${c}-slider`,$,{[`${c}-slider--disabled`]:this.mergedDisabled,[`${c}-slider--active`]:this.activeIndex!==-1,[`${c}-slider--with-mark`]:this.marks,[`${c}-slider--vertical`]:this.vertical,[`${c}-slider--reverse`]:this.reverse}],style:this.cssVars,onKeydown:this.handleRailKeyDown,onMousedown:this.handleRailMouseDown,onTouchstart:this.handleRailMouseDown},b("div",{class:`${c}-slider-rail`},b("div",{class:`${c}-slider-rail__fill`,style:this.fillStyle}),this.marks?b("div",{class:[`${c}-slider-dots`,this.dotTransitionDisabled&&`${c}-slider-dots--transition-disabled`]},this.markInfos.map(g=>b("div",{key:g.key,class:[`${c}-slider-dot`,{[`${c}-slider-dot--active`]:g.active}],style:g.style}))):null,b("div",{ref:"handleRailRef",class:`${c}-slider-handles`},this.arrifiedValues.map((g,h)=>{const I=this.isShowTooltip(h);return b(La,null,{default:()=>[b(Ka,null,{default:()=>b("div",{ref:this.setHandleRefs(h),class:`${c}-slider-handle-wrapper`,tabindex:this.mergedDisabled?-1:0,role:"slider","aria-valuenow":g,"aria-valuemin":this.min,"aria-valuemax":this.max,"aria-orientation":this.vertical?"vertical":"horizontal","aria-disabled":this.disabled,style:this.getHandleStyle(g,h),onFocus:()=>{this.handleHandleFocus(h)},onBlur:()=>{this.handleHandleBlur(h)},onMouseenter:()=>{this.handleHandleMouseEnter(h)},onMouseleave:()=>{this.handleHandleMouseLeave(h)}},xa(this.$slots.thumb,()=>[b("div",{class:`${c}-slider-handle`})]))}),this.tooltip&&b(Xa,{ref:this.setFollowerRefs(h),show:I,to:this.adjustedTo,enabled:this.showTooltip&&!this.range||this.followerEnabledIndexSet.has(h),teleportDisabled:this.adjustedTo===Be.tdkey,placement:this.mergedPlacement,containerClass:this.namespace},{default:()=>b(ka,{name:"fade-in-scale-up-transition",appear:this.isMounted,css:this.shouldKeepTooltipTransition(h),onEnter:()=>{this.followerEnabledIndexSet.add(h)},onAfterLeave:()=>{this.followerEnabledIndexSet.delete(h)}},{default:()=>{var C;return I?((C=this.indicatorOnRender)===null||C===void 0||C.call(this),b("div",{class:[`${c}-slider-handle-indicator`,this.indicatorThemeClass,`${c}-slider-handle-indicator--${this.mergedPlacement}`],style:this.indicatorCssVars},typeof w=="function"?w(g):g)):null}})})]})})),this.marks?b("div",{class:`${c}-slider-marks`},this.markInfos.map(g=>b("div",{key:g.key,class:`${c}-slider-mark`,style:g.style},typeof g.label=="function"?g.label():g.label))):null))}}),ot={style:{color:"#18a058"}},lt={style:{color:"#d03050"}},nt={style:{color:"#f0a020"}},rt=We({__name:"index",setup(i){const c=Fa(),$=Aa(),w=Ba(),g=w.role==="admin"||w.role==="editor",h=x([]),I=x(!1),C=x([]),j=x(Ua("created_at")),F=x(!1),P=x(!1),H=x(null),O=x(!1),oe=x(),u=x(V()),_e=T(()=>h.value.filter(d=>L(d.agent_status)==="online").length),ee=T(()=>h.value.filter(d=>L(d.agent_status)==="offline").length),D=T(()=>h.value.filter(d=>L(d.agent_status)==="mounting").length);function L(d){const e=(d||"unknown").toLowerCase();return e==="attached"||e==="online"||e==="already_injected"?"online":e==="detached"||e==="offline"?"offline":e==="mounting"?"mounting":e==="error"?"error":"unknown"}const xe={online:"success",offline:"error",mounting:"warning",error:"error",unknown:"default"},le={online:"已挂载",offline:"未挂载",mounting:"挂载中",error:"挂载失败",unknown:"未知"},A=[{label:"宿主机脚本",value:"ssh_script"},{label:"Docker Compose",value:"docker_compose"}],ne=T(()=>[...w.role==="admin"?[{type:"selection"}]:[],{title:"名称",key:"name",width:220,render:d=>b(U,{text:!0,type:"primary",onClick:()=>$.push(`/applications/${d.id}`)},()=>d.name)},{title:"宿主机",key:"ssh_host",width:220},{title:"服务端口",key:"service_port",width:110},{title:"Agent 状态",key:"agent_status",width:130,render:d=>{const e=L(d.agent_status);return b(Le,{type:xe[e]||"default",size:"small"},()=>le[e]||"未知")}},{title:"创建时间",key:"created_at",width:180,sorter:!0,sortOrder:Ia(j.value,"created_at"),render:d=>Ma(d.created_at)},{title:"操作",key:"actions",width:w.role==="admin"?440:g?380:140,render:d=>{const e=L(d.agent_status);return b(q,{size:8,wrap:!0},()=>[b(U,{size:"tiny",onClick:()=>$.push(`/applications/${d.id}`)},()=>"查看详情"),...g?[b(U,{size:"tiny",onClick:()=>Se(d.id)},()=>"连接测试"),e==="online"?b(U,{size:"tiny",type:"warning",onClick:()=>Re(d.id)},()=>"卸载 Agent"):b(U,{size:"tiny",type:"info",onClick:()=>re(d.id)},()=>"挂载 Agent"),b(U,{size:"tiny",onClick:()=>ke(d)},()=>"编辑")]:[],...w.role==="admin"?[b(Wa,{onPositiveClick:()=>ze(d.id)},{default:()=>"确认删除？",trigger:()=>b(U,{size:"tiny",type:"error"},()=>"删除")})]:[]])}}]);function V(){return{name:"",description:"",ssh_host:"",ssh_user:"",ssh_port:22,launch_mode:"ssh_script",ssh_key_path:"",ssh_password:"",docker_workdir:"",docker_compose_file:"docker-compose.yml",docker_service_name:"",docker_storage_url:"",docker_agent_path:"/opt/arex/arex-agent.jar",service_port:8080,jvm_process_name:"",arex_app_id:"",arex_storage_url:"",sample_rate:1,transaction_code_fields:"",transaction_mappings:""}}async function z(){var d,e;I.value=!0;try{const n=await X.list({sort_by:j.value.columnKey,sort_order:Va(j.value.order)});h.value=n.data,C.value=[]}catch(n){h.value=[],c.error(((e=(d=n.response)==null?void 0:d.data)==null?void 0:e.detail)||"加载应用列表失败")}finally{I.value=!1}}function W(){u.value=V()}function ae(){H.value=null,O.value=!1,W(),F.value=!0}function ke(d){H.value=d.id,O.value=!!d.has_password,u.value={...V(),...d,ssh_password:"",transaction_code_fields:Array.isArray(d.transaction_code_fields)?d.transaction_code_fields.join(`
`):"",transaction_mappings:Array.isArray(d.transaction_mappings)?JSON.stringify(d.transaction_mappings,null,2):""},F.value=!0}async function Ce(){var d,e;P.value=!0;try{H.value?await X.update(H.value,u.value):await X.create(u.value),c.success("保存成功"),F.value=!1,await z()}catch(n){c.error(((e=(d=n.response)==null?void 0:d.data)==null?void 0:e.detail)||"保存失败")}finally{P.value=!1}}async function Se(d){var e,n;try{const M=await X.testConnection(d);M.data.success?c.success("连接成功"):c.error(`连接失败：${M.data.message}`)}catch(M){c.error(((n=(e=M.response)==null?void 0:e.data)==null?void 0:n.detail)||"连接测试失败")}}async function re(d){var e,n;try{await X.mountAgent(d),c.info("Agent 挂载已启动，请稍候..."),setTimeout(()=>{z()},3e3)}catch(M){c.error(((n=(e=M.response)==null?void 0:e.data)==null?void 0:n.detail)||"挂载失败")}}async function Re(d){var e,n;try{await X.unmountAgent(d),c.success("Agent 已卸载"),await z()}catch(M){c.error(((n=(e=M.response)==null?void 0:e.data)==null?void 0:n.detail)||"卸载失败")}}async function ze(d){var e,n;try{await X.delete(d),c.success("删除成功"),await z()}catch(M){c.error(((n=(e=M.response)==null?void 0:e.data)==null?void 0:n.detail)||"删除失败")}}async function Ne(){var d,e;if(C.value.length!==0)try{const n=await X.bulkDelete({ids:C.value.map(Number)});c.success(`已删除 ${n.data.deleted} 个应用`),await z()}catch(n){c.error(((e=(d=n.response)==null?void 0:d.data)==null?void 0:e.detail)||"批量删除失败")}}function se(d){j.value=$a(d,"created_at"),z()}return Ta(z),(d,e)=>(be(),Ee(je,null,[l(t(q),{vertical:"",size:16,class:"applications-page"},{default:s(()=>[l(t(q),{justify:"space-between",align:"center"},{default:s(()=>[y("div",null,[l(t(Ha),{style:{margin:"0"}},{default:s(()=>[...e[23]||(e[23]=[p("应用管理",-1)])]),_:1}),l(t(Oe),{depth:"3"},{default:s(()=>[...e[24]||(e[24]=[p("统一管理被测应用、接入配置和 Agent 状态。",-1)])]),_:1})]),l(t(q),null,{default:s(()=>[t(w).role==="admin"&&C.value.length>0?(be(),Pe(t(U),{key:0,type:"error",onClick:Ne},{default:s(()=>[p(" 批量删除"+G(C.value.length>0?` (${C.value.length})`:""),1)]),_:1})):Me("",!0),t(g)?(be(),Pe(t(U),{key:1,type:"primary",onClick:ae},{default:s(()=>[...e[25]||(e[25]=[p("+ 新增应用",-1)])]),_:1})):Me("",!0)]),_:1})]),_:1}),l(t(Ea),{cols:"1 s:2 l:4",responsive:"screen","x-gap":12,"y-gap":12},{default:s(()=>[l(t(we),null,{default:s(()=>[l(t(Q),null,{default:s(()=>[l(t(ye),{label:"应用总数",value:h.value.length},null,8,["value"])]),_:1})]),_:1}),l(t(we),null,{default:s(()=>[l(t(Q),null,{default:s(()=>[l(t(ye),{label:"已挂载"},{default:s(()=>[y("span",ot,G(_e.value),1)]),_:1})]),_:1})]),_:1}),l(t(we),null,{default:s(()=>[l(t(Q),null,{default:s(()=>[l(t(ye),{label:"未挂载"},{default:s(()=>[y("span",lt,G(ee.value),1)]),_:1})]),_:1})]),_:1}),l(t(we),null,{default:s(()=>[l(t(Q),null,{default:s(()=>[l(t(ye),{label:"挂载中"},{default:s(()=>[y("span",nt,G(D.value),1)]),_:1})]),_:1})]),_:1})]),_:1}),l(t(Q),{title:"应用列表"},{"header-extra":s(()=>[l(t(Le),{type:"info",size:"small"},{default:s(()=>[p("共 "+G(h.value.length)+" 个应用",1)]),_:1})]),default:s(()=>[l(t(ja),{class:"applications-table",columns:ne.value,data:h.value,loading:I.value,pagination:{pageSize:10},"row-key":n=>n.id,remote:"","checked-row-keys":C.value,"onUpdate:checkedRowKeys":e[0]||(e[0]=n=>C.value=n),"onUpdate:sorter":se},null,8,["columns","data","loading","row-key","checked-row-keys"])]),_:1}),l(t(Q),{title:"页面说明"},{default:s(()=>[l(t(q),{vertical:"",size:8},{default:s(()=>[l(t(Z),{type:"info","show-icon":!1},{default:s(()=>[...e[26]||(e[26]=[p(" 页面采用上下结构展示，表格列间距和左右留白已拉宽，便于大屏阅读。 ",-1)])]),_:1}),l(t(Z),{type:"warning","show-icon":!1},{default:s(()=>[...e[27]||(e[27]=[p(" 新增 / 编辑时只需要补充宿主机、端口、服务进程和 AREX 配置即可。 ",-1)])]),_:1})]),_:1})]),_:1})]),_:1}),l(t(Da),{show:F.value,"onUpdate:show":e[22]||(e[22]=n=>F.value=n),title:H.value?"编辑应用":"新增应用",preset:"card",style:{width:"600px"}},{footer:s(()=>[l(t(q),{justify:"end"},{default:s(()=>[l(t(U),{onClick:e[21]||(e[21]=n=>F.value=!1)},{default:s(()=>[...e[34]||(e[34]=[p("取消",-1)])]),_:1}),l(t(U),{type:"primary",loading:P.value,onClick:Ce},{default:s(()=>[...e[35]||(e[35]=[p("保存",-1)])]),_:1},8,["loading"])]),_:1})]),default:s(()=>[l(t(Oa),{ref_key:"formRef",ref:oe,model:u.value,"label-placement":"left","label-width":"120px"},{default:s(()=>[e[32]||(e[32]=y("input",{type:"text",style:{display:"none"},autocomplete:"username",tabindex:"-1","aria-hidden":"true"},null,-1)),e[33]||(e[33]=y("input",{type:"password",style:{display:"none"},autocomplete:"current-password",tabindex:"-1","aria-hidden":"true"},null,-1)),l(t(_),{label:"应用名称",path:"name",rule:{required:!0,message:"请输入应用名称"}},{default:s(()=>[l(t(R),{value:u.value.name,"onUpdate:value":e[1]||(e[1]=n=>u.value.name=n),placeholder:"例如：demo-service"},null,8,["value"])]),_:1}),l(t(_),{label:"描述"},{default:s(()=>[l(t(R),{value:u.value.description,"onUpdate:value":e[2]||(e[2]=n=>u.value.description=n),placeholder:"可选"},null,8,["value"])]),_:1}),l(t(_),{label:"宿主机地址",path:"ssh_host",rule:{required:!0,message:"请输入宿主机地址"}},{default:s(()=>[l(t(R),{value:u.value.ssh_host,"onUpdate:value":e[3]||(e[3]=n=>u.value.ssh_host=n),placeholder:"IP 或域名"},null,8,["value"])]),_:1}),l(t(_),{label:"宿主机用户",path:"ssh_user",rule:{required:!0,message:"请输入宿主机用户"}},{default:s(()=>[l(t(R),{value:u.value.ssh_user,"onUpdate:value":e[4]||(e[4]=n=>u.value.ssh_user=n),placeholder:"例如：ubuntu"},null,8,["value"])]),_:1}),l(t(_),{label:"宿主机端口"},{default:s(()=>[l(t(Ke),{value:u.value.ssh_port,"onUpdate:value":e[5]||(e[5]=n=>u.value.ssh_port=n)},null,8,["value"])]),_:1}),l(t(_),{label:"启动模式"},{default:s(()=>[l(t(Pa),{value:u.value.launch_mode,"onUpdate:value":e[6]||(e[6]=n=>u.value.launch_mode=n),options:A},null,8,["value"])]),_:1}),l(t(Z),{type:"info","show-icon":!1},{default:s(()=>[...e[28]||(e[28]=[p(" Docker 模式由平台生成启动模板并通过 docker compose 控制容器重建，不再修改 start.sh。 ",-1)])]),_:1}),u.value.launch_mode==="docker_compose"?(be(),Ee(je,{key:0},[l(t(_),{label:"Docker 工作目录",path:"docker_workdir",rule:{required:!0,message:"请输入 Docker 工作目录"}},{default:s(()=>[l(t(R),{value:u.value.docker_workdir,"onUpdate:value":e[7]||(e[7]=n=>u.value.docker_workdir=n),placeholder:"/home/test/N-LS"},null,8,["value"])]),_:1}),l(t(_),{label:"Docker Compose 文件"},{default:s(()=>[l(t(R),{value:u.value.docker_compose_file,"onUpdate:value":e[8]||(e[8]=n=>u.value.docker_compose_file=n),placeholder:"docker-compose.yml"},null,8,["value"])]),_:1}),l(t(_),{label:"Compose 服务名",path:"docker_service_name",rule:{required:!0,message:"请输入 Compose 服务名"}},{default:s(()=>[l(t(R),{value:u.value.docker_service_name,"onUpdate:value":e[9]||(e[9]=n=>u.value.docker_service_name=n),placeholder:"sat / uat / app-service"},null,8,["value"])]),_:1}),l(t(_),{label:"Docker Agent Storage"},{default:s(()=>[l(t(R),{value:u.value.docker_storage_url,"onUpdate:value":e[10]||(e[10]=n=>u.value.docker_storage_url=n),placeholder:"留空则使用平台默认 Docker storage URL"},null,8,["value"])]),_:1}),l(t(_),{label:"Agent 挂载路径"},{default:s(()=>[l(t(R),{value:u.value.docker_agent_path,"onUpdate:value":e[11]||(e[11]=n=>u.value.docker_agent_path=n),placeholder:"/opt/arex/arex-agent.jar"},null,8,["value"])]),_:1})],64)):Me("",!0),l(t(_),{label:"密钥路径"},{default:s(()=>[l(t(R),{value:u.value.ssh_key_path,"onUpdate:value":e[12]||(e[12]=n=>u.value.ssh_key_path=n),placeholder:"/path/to/key","input-props":{autocomplete:"new-password"}},null,8,["value"])]),_:1}),l(t(_),{label:"连接密码"},{default:s(()=>[l(t(R),{value:u.value.ssh_password,"onUpdate:value":e[13]||(e[13]=n=>u.value.ssh_password=n),type:"password","input-props":{autocomplete:"new-password"},placeholder:O.value?"已设置密码（留空不修改）":"可选"},null,8,["value","placeholder"])]),_:1}),l(t(_),{label:"服务端口"},{default:s(()=>[l(t(Ke),{value:u.value.service_port,"onUpdate:value":e[14]||(e[14]=n=>u.value.service_port=n)},null,8,["value"])]),_:1}),l(t(_),{label:"JVM 进程名"},{default:s(()=>[l(t(R),{value:u.value.jvm_process_name,"onUpdate:value":e[15]||(e[15]=n=>u.value.jvm_process_name=n),placeholder:"用于 pgrep 识别"},null,8,["value"])]),_:1}),l(t(_),{label:"AREX App ID"},{default:s(()=>[l(t(R),{value:u.value.arex_app_id,"onUpdate:value":e[16]||(e[16]=n=>u.value.arex_app_id=n)},null,8,["value"])]),_:1}),l(t(_),{label:"AREX Storage 地址"},{default:s(()=>[l(t(R),{value:u.value.arex_storage_url,"onUpdate:value":e[17]||(e[17]=n=>u.value.arex_storage_url=n),placeholder:"留空则使用全局配置"},null,8,["value"])]),_:1}),l(t(_),{label:"采样率"},{default:s(()=>[l(t(tt),{value:u.value.sample_rate,"onUpdate:value":e[18]||(e[18]=n=>u.value.sample_rate=n),min:0,max:1,step:.1,style:{width:"200px"}},null,8,["value"]),l(t(Oe),{style:{"margin-left":"12px"}},{default:s(()=>[p(G(u.value.sample_rate),1)]),_:1})]),_:1}),l(t(_),{label:"交易码提取字段"},{default:s(()=>[l(t(q),{vertical:"",style:{width:"100%"}},{default:s(()=>[l(t(Z),{type:"info","show-icon":!1},{default:s(()=>[...e[29]||(e[29]=[p(" 按应用维度配置交易码提取字段，录制时优先按这里的字段名从请求/响应报文里提取交易码。 推荐按优先级一行一个，例如 ",-1),y("code",null,"txnCode",-1),p("、",-1),y("code",null,"code",-1),p("、",-1),y("code",null,"sys_code",-1),p("。 ",-1)])]),_:1}),l(t(R),{value:u.value.transaction_code_fields,"onUpdate:value":e[19]||(e[19]=n=>u.value.transaction_code_fields=n),type:"textarea",autosize:{minRows:3,maxRows:8},placeholder:`txnCode
code
sys_code`},null,8,["value"])]),_:1})]),_:1}),l(t(_),{label:"交易码映射"},{default:s(()=>[l(t(q),{vertical:"",style:{width:"100%"}},{default:s(()=>[l(t(Z),{type:"info","show-icon":!1},{default:s(()=>[...e[30]||(e[30]=[p(" 以 JSON 数组配置，每个交易码一组规则。平台会在回放前自动按交易码加载对应映射。 推荐按 ",-1),y("code",null,"transaction_code",-1),p(" 一条一组填写。字段路径使用点号，例如 ",-1),y("code",null,"name",-1),p("、",-1),y("code",null,"customer.name",-1),p("、",-1),y("code",null,"items.0.name",-1),p("、",-1),y("code",null,"*.name",-1),p("。 ",-1)])]),_:1}),l(t(Z),{type:"warning","show-icon":!1},{default:s(()=>[...e[31]||(e[31]=[p(" 规则类型目前支持 ",-1),y("code",null,"rename",-1),p("（改名）、",-1),y("code",null,"delete",-1),p("（删除）、",-1),y("code",null,"default",-1),p("（补默认值）、",-1),y("code",null,"set",-1),p("（强制赋值）、",-1),y("code",null,"copy",-1),p("（复制到新字段）。 推荐先参考 ",-1),y("code",null,"docs/交易码映射模板.md",-1),p(" 再填写。 ",-1)])]),_:1}),l(t(R),{value:u.value.transaction_mappings,"onUpdate:value":e[20]||(e[20]=n=>u.value.transaction_mappings=n),type:"textarea",autosize:{minRows:6,maxRows:14},placeholder:`[
  {
    "transaction_code": "car001_open",
    "enabled": true,
    "description": "基础资料字段映射",
    "request_rules": [
      { "type": "rename", "source": "name", "target": "cst_name" },
      { "type": "rename", "source": "idNo", "target": "cert_no" },
      { "type": "default", "source": "branch_code", "value": "0101" },
      { "type": "delete", "source": "debug_flag" }
    ],
    "response_rules": [
      { "type": "rename", "source": "cst_name", "target": "name" },
      { "type": "delete", "source": "debug_flag" }
    ]
  },
  {
    "transaction_code": "car002_apply",
    "enabled": true,
    "description": "申请字段映射",
    "request_rules": [
      { "type": "rename", "source": "amount", "target": "loan_amount" }
    ],
    "response_rules": []
  }
]`},null,8,["value"])]),_:1})]),_:1})]),_:1},8,["model"])]),_:1},8,["show","title"])],64))}}),Dt=Ya(rt,[["__scopeId","data-v-0cae5baf"]]);export{Dt as default};
