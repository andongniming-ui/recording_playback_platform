import{a as E}from"./applications-s_MpUk7y.js";import{u as la}from"./user-DGvab7w1.js";import{a as ia,o as q,g as i,i as R,n as ie,a5 as Re,a6 as sa,a7 as da,a8 as ua,d as He,h as p,a9 as ca,aa as va,u as fa,j as Ne,ab as ha,r as S,Z as _e,$ as ma,l as Te,ac as pa,m as B,t as se,ad as de,ae as ue,a1 as ge,v as ga,_ as ba,M as wa,K as v,I as m,J as u,af as xa,F as ya,P as J,H as ka,Q as I,ag as Sa,O as Ca,W as Me}from"./index-GkL_KtkI.js";import{N as za}from"./headers-C2xm6X6p.js";import{N as Ra,a as T}from"./FormItem-YnegaOie.js";import{u as _a,N as F}from"./index-C0fvwfCu.js";import{N as De}from"./InputNumber-C-X5XmoP.js";import{B as Ta,e as Ma,f as Da,g as be,b as ce}from"./Space-7jIUoFvJ.js";import{u as Va}from"./get-DYzmg4KD.js";import{N as Ba}from"./Popconfirm-DHveAGts.js";import{b as Ha,c as Na}from"./index-CXjJCXf5.js";import{N as Aa}from"./text-BBTcA4bH.js";import"./light-DWLIveho.js";const Fa={railHeight:"4px",railWidthVertical:"4px",handleSize:"18px",dotHeight:"8px",dotWidth:"8px",dotBorderRadius:"4px"};function $a(n){const l="rgba(0, 0, 0, .85)",M="0 2px 8px 0 rgba(0, 0, 0, 0.12)",{railColor:x,primaryColor:h,baseColor:g,cardColor:C,modalColor:D,popoverColor:H,borderRadius:X,fontSize:c,opacityDisabled:U}=n;return Object.assign(Object.assign({},Fa),{fontSize:c,markFontSize:c,railColor:x,railColorHover:x,fillColor:h,fillColorHover:h,opacityDisabled:U,handleColor:"#FFF",dotColor:C,dotColorModal:D,dotColorPopover:H,handleBoxShadow:"0 1px 4px 0 rgba(0, 0, 0, 0.3), inset 0 0 1px 0 rgba(0, 0, 0, 0.05)",handleBoxShadowHover:"0 1px 4px 0 rgba(0, 0, 0, 0.3), inset 0 0 1px 0 rgba(0, 0, 0, 0.05)",handleBoxShadowActive:"0 1px 4px 0 rgba(0, 0, 0, 0.3), inset 0 0 1px 0 rgba(0, 0, 0, 0.05)",handleBoxShadowFocus:"0 1px 4px 0 rgba(0, 0, 0, 0.3), inset 0 0 1px 0 rgba(0, 0, 0, 0.05)",indicatorColor:l,indicatorBoxShadow:M,indicatorTextColor:g,indicatorBorderRadius:X,dotBorder:`2px solid ${x}`,dotBorderActive:`2px solid ${h}`,dotBoxShadow:""})}const Ia={common:ia,self:$a},Ua=q([i("slider",`
 display: block;
 padding: calc((var(--n-handle-size) - var(--n-rail-height)) / 2) 0;
 position: relative;
 z-index: 0;
 width: 100%;
 cursor: pointer;
 user-select: none;
 -webkit-user-select: none;
 `,[R("reverse",[i("slider-handles",[i("slider-handle-wrapper",`
 transform: translate(50%, -50%);
 `)]),i("slider-dots",[i("slider-dot",`
 transform: translateX(50%, -50%);
 `)]),R("vertical",[i("slider-handles",[i("slider-handle-wrapper",`
 transform: translate(-50%, -50%);
 `)]),i("slider-marks",[i("slider-mark",`
 transform: translateY(calc(-50% + var(--n-dot-height) / 2));
 `)]),i("slider-dots",[i("slider-dot",`
 transform: translateX(-50%) translateY(0);
 `)])])]),R("vertical",`
 box-sizing: content-box;
 padding: 0 calc((var(--n-handle-size) - var(--n-rail-height)) / 2);
 width: var(--n-rail-width-vertical);
 height: 100%;
 `,[i("slider-handles",`
 top: calc(var(--n-handle-size) / 2);
 right: 0;
 bottom: calc(var(--n-handle-size) / 2);
 left: 0;
 `,[i("slider-handle-wrapper",`
 top: unset;
 left: 50%;
 transform: translate(-50%, 50%);
 `)]),i("slider-rail",`
 height: 100%;
 `,[ie("fill",`
 top: unset;
 right: 0;
 bottom: unset;
 left: 0;
 `)]),R("with-mark",`
 width: var(--n-rail-width-vertical);
 margin: 0 32px 0 8px;
 `),i("slider-marks",`
 top: calc(var(--n-handle-size) / 2);
 right: unset;
 bottom: calc(var(--n-handle-size) / 2);
 left: 22px;
 font-size: var(--n-mark-font-size);
 `,[i("slider-mark",`
 transform: translateY(50%);
 white-space: nowrap;
 `)]),i("slider-dots",`
 top: calc(var(--n-handle-size) / 2);
 right: unset;
 bottom: calc(var(--n-handle-size) / 2);
 left: 50%;
 `,[i("slider-dot",`
 transform: translateX(-50%) translateY(50%);
 `)])]),R("disabled",`
 cursor: not-allowed;
 opacity: var(--n-opacity-disabled);
 `,[i("slider-handle",`
 cursor: not-allowed;
 `)]),R("with-mark",`
 width: 100%;
 margin: 8px 0 32px 0;
 `),q("&:hover",[i("slider-rail",{backgroundColor:"var(--n-rail-color-hover)"},[ie("fill",{backgroundColor:"var(--n-fill-color-hover)"})]),i("slider-handle",{boxShadow:"var(--n-handle-box-shadow-hover)"})]),R("active",[i("slider-rail",{backgroundColor:"var(--n-rail-color-hover)"},[ie("fill",{backgroundColor:"var(--n-fill-color-hover)"})]),i("slider-handle",{boxShadow:"var(--n-handle-box-shadow-hover)"})]),i("slider-marks",`
 position: absolute;
 top: 18px;
 left: calc(var(--n-handle-size) / 2);
 right: calc(var(--n-handle-size) / 2);
 `,[i("slider-mark",`
 position: absolute;
 transform: translateX(-50%);
 white-space: nowrap;
 `)]),i("slider-rail",`
 width: 100%;
 position: relative;
 height: var(--n-rail-height);
 background-color: var(--n-rail-color);
 transition: background-color .3s var(--n-bezier);
 border-radius: calc(var(--n-rail-height) / 2);
 `,[ie("fill",`
 position: absolute;
 top: 0;
 bottom: 0;
 border-radius: calc(var(--n-rail-height) / 2);
 transition: background-color .3s var(--n-bezier);
 background-color: var(--n-fill-color);
 `)]),i("slider-handles",`
 position: absolute;
 top: 0;
 right: calc(var(--n-handle-size) / 2);
 bottom: 0;
 left: calc(var(--n-handle-size) / 2);
 `,[i("slider-handle-wrapper",`
 outline: none;
 position: absolute;
 top: 50%;
 transform: translate(-50%, -50%);
 cursor: pointer;
 display: flex;
 `,[i("slider-handle",`
 height: var(--n-handle-size);
 width: var(--n-handle-size);
 border-radius: 50%;
 overflow: hidden;
 transition: box-shadow .2s var(--n-bezier), background-color .3s var(--n-bezier);
 background-color: var(--n-handle-color);
 box-shadow: var(--n-handle-box-shadow);
 `,[q("&:hover",`
 box-shadow: var(--n-handle-box-shadow-hover);
 `)]),q("&:focus",[i("slider-handle",`
 box-shadow: var(--n-handle-box-shadow-focus);
 `,[q("&:hover",`
 box-shadow: var(--n-handle-box-shadow-active);
 `)])])])]),i("slider-dots",`
 position: absolute;
 top: 50%;
 left: calc(var(--n-handle-size) / 2);
 right: calc(var(--n-handle-size) / 2);
 `,[R("transition-disabled",[i("slider-dot","transition: none;")]),i("slider-dot",`
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
 `,[R("active","border: var(--n-dot-border-active);")])])]),i("slider-handle-indicator",`
 font-size: var(--n-font-size);
 padding: 6px 10px;
 border-radius: var(--n-indicator-border-radius);
 color: var(--n-indicator-text-color);
 background-color: var(--n-indicator-color);
 box-shadow: var(--n-indicator-box-shadow);
 `,[Re()]),i("slider-handle-indicator",`
 font-size: var(--n-font-size);
 padding: 6px 10px;
 border-radius: var(--n-indicator-border-radius);
 color: var(--n-indicator-text-color);
 background-color: var(--n-indicator-color);
 box-shadow: var(--n-indicator-box-shadow);
 `,[R("top",`
 margin-bottom: 12px;
 `),R("right",`
 margin-left: 12px;
 `),R("bottom",`
 margin-top: 12px;
 `),R("left",`
 margin-right: 12px;
 `),Re()]),sa(i("slider",[i("slider-dot","background-color: var(--n-dot-color-modal);")])),da(i("slider",[i("slider-dot","background-color: var(--n-dot-color-popover);")]))]);function Ve(n){return window.TouchEvent&&n instanceof window.TouchEvent}function Be(){const n=new Map,l=M=>x=>{n.set(M,x)};return ua(()=>{n.clear()}),[n,l]}const Ea=0,ja=Object.assign(Object.assign({},Ne.props),{to:be.propTo,defaultValue:{type:[Number,Array],default:0},marks:Object,disabled:{type:Boolean,default:void 0},formatTooltip:Function,keyboard:{type:Boolean,default:!0},min:{type:Number,default:0},max:{type:Number,default:100},step:{type:[Number,String],default:1},range:Boolean,value:[Number,Array],placement:String,showTooltip:{type:Boolean,default:void 0},tooltip:{type:Boolean,default:!0},vertical:Boolean,reverse:Boolean,"onUpdate:value":[Function,Array],onUpdateValue:[Function,Array],onDragstart:[Function],onDragend:[Function]}),Pa=He({name:"Slider",props:ja,slots:Object,setup(n){const{mergedClsPrefixRef:l,namespaceRef:M,inlineThemeDisabled:x}=fa(n),h=Ne("Slider","-slider",Ua,Ia,n,l),g=S(null),[C,D]=Be(),[H,X]=Be(),c=S(new Set),U=ha(n),{mergedDisabledRef:j}=U,Q=B(()=>{const{step:e}=n;if(Number(e)<=0||e==="mark")return 0;const a=e.toString();let o=0;return a.includes(".")&&(o=a.length-a.indexOf(".")-1),o}),K=S(n.defaultValue),W=ga(n,"value"),Y=Va(W,K),b=B(()=>{const{value:e}=Y;return(n.range?e:[e]).map(ke)}),Z=B(()=>b.value.length>2),ve=B(()=>n.placement===void 0?n.vertical?"right":"top":n.placement),G=B(()=>{const{marks:e}=n;return e?Object.keys(e).map(Number.parseFloat):null}),z=S(-1),ee=S(-1),N=S(-1),A=S(!1),P=S(!1),s=B(()=>{const{vertical:e,reverse:a}=n;return e?a?"top":"bottom":a?"right":"left"}),t=B(()=>{if(Z.value)return;const e=b.value,a=ae(n.range?Math.min(...e):n.min),o=ae(n.range?Math.max(...e):e[0]),{value:d}=s;return n.vertical?{[d]:`${a}%`,height:`${o-a}%`}:{[d]:`${a}%`,width:`${o-a}%`}}),r=B(()=>{const e=[],{marks:a}=n;if(a){const o=b.value.slice();o.sort((k,y)=>k-y);const{value:d}=s,{value:f}=Z,{range:w}=n,V=f?()=>!1:k=>w?k>=o[0]&&k<=o[o.length-1]:k<=o[0];for(const k of Object.keys(a)){const y=Number(k);e.push({active:V(y),key:y,label:a[k],style:{[d]:`${ae(y)}%`}})}}return e});function _(e,a){const o=ae(e),{value:d}=s;return{[d]:`${o}%`,zIndex:a===z.value?1:0}}function we(e){return n.showTooltip||N.value===e||z.value===e&&A.value}function Ae(e){return A.value?!(z.value===e&&ee.value===e):!0}function Fe(e){var a;~e&&(z.value=e,(a=C.get(e))===null||a===void 0||a.focus())}function $e(){H.forEach((e,a)=>{we(a)&&e.syncPosition()})}function xe(e){const{"onUpdate:value":a,onUpdateValue:o}=n,{nTriggerFormInput:d,nTriggerFormChange:f}=U;o&&se(o,e),a&&se(a,e),K.value=e,d(),f()}function ye(e){const{range:a}=n;if(a){if(Array.isArray(e)){const{value:o}=b;e.join()!==o.join()&&xe(e)}}else Array.isArray(e)||b.value[0]!==e&&xe(e)}function fe(e,a){if(n.range){const o=b.value.slice();o.splice(a,1,e),ye(o)}else ye(e)}function he(e,a,o){const d=o!==void 0;o||(o=e-a>0?1:-1);const f=G.value||[],{step:w}=n;if(w==="mark"){const y=te(e,f.concat(a),d?o:void 0);return y?y.value:a}if(w<=0)return a;const{value:V}=Q;let k;if(d){const y=Number((a/w).toFixed(V)),$=Math.floor(y),me=y>$?$:$-1,pe=y<$?$:$+1;k=te(a,[Number((me*w).toFixed(V)),Number((pe*w).toFixed(V)),...f],o)}else{const y=Ue(e);k=te(e,[...f,y])}return k?ke(k.value):a}function ke(e){return Math.min(n.max,Math.max(n.min,e))}function ae(e){const{max:a,min:o}=n;return(e-o)/(a-o)*100}function Ie(e){const{max:a,min:o}=n;return o+(a-o)*e}function Ue(e){const{step:a,min:o}=n;if(Number(a)<=0||a==="mark")return e;const d=Math.round((e-o)/a)*a+o;return Number(d.toFixed(Q.value))}function te(e,a=G.value,o){if(!(a!=null&&a.length))return null;let d=null,f=-1;for(;++f<a.length;){const w=a[f]-e,V=Math.abs(w);(o===void 0||w*o>0)&&(d===null||V<d.distance)&&(d={index:f,distance:V,value:a[f]})}return d}function Se(e){const a=g.value;if(!a)return;const o=Ve(e)?e.touches[0]:e,d=a.getBoundingClientRect();let f;return n.vertical?f=(d.bottom-o.clientY)/d.height:f=(o.clientX-d.left)/d.width,n.reverse&&(f=1-f),Ie(f)}function Ee(e){if(j.value||!n.keyboard)return;const{vertical:a,reverse:o}=n;switch(e.key){case"ArrowUp":e.preventDefault(),oe(a&&o?-1:1);break;case"ArrowRight":e.preventDefault(),oe(!a&&o?-1:1);break;case"ArrowDown":e.preventDefault(),oe(a&&o?1:-1);break;case"ArrowLeft":e.preventDefault(),oe(!a&&o?1:-1);break}}function oe(e){const a=z.value;if(a===-1)return;const{step:o}=n,d=b.value[a],f=Number(o)<=0||o==="mark"?d:d+o*e;fe(he(f,d,e>0?1:-1),a)}function je(e){var a,o;if(j.value||!Ve(e)&&e.button!==Ea)return;const d=Se(e);if(d===void 0)return;const f=b.value.slice(),w=n.range?(o=(a=te(d,f))===null||a===void 0?void 0:a.index)!==null&&o!==void 0?o:-1:0;w!==-1&&(e.preventDefault(),Fe(w),Pe(),fe(he(d,b.value[w]),w))}function Pe(){A.value||(A.value=!0,n.onDragstart&&se(n.onDragstart),de("touchend",document,le),de("mouseup",document,le),de("touchmove",document,re),de("mousemove",document,re))}function ne(){A.value&&(A.value=!1,n.onDragend&&se(n.onDragend),ue("touchend",document,le),ue("mouseup",document,le),ue("touchmove",document,re),ue("mousemove",document,re))}function re(e){const{value:a}=z;if(!A.value||a===-1){ne();return}const o=Se(e);o!==void 0&&fe(he(o,b.value[a]),a)}function le(){ne()}function Oe(e){z.value=e,j.value||(N.value=e)}function Le(e){z.value===e&&(z.value=-1,ne()),N.value===e&&(N.value=-1)}function Xe(e){N.value=e}function Ke(e){N.value===e&&(N.value=-1)}_e(z,(e,a)=>void ge(()=>ee.value=a)),_e(Y,()=>{if(n.marks){if(P.value)return;P.value=!0,ge(()=>{P.value=!1})}ge($e)}),ma(()=>{ne()});const Ce=B(()=>{const{self:{markFontSize:e,railColor:a,railColorHover:o,fillColor:d,fillColorHover:f,handleColor:w,opacityDisabled:V,dotColor:k,dotColorModal:y,handleBoxShadow:$,handleBoxShadowHover:me,handleBoxShadowActive:pe,handleBoxShadowFocus:We,dotBorder:Ye,dotBoxShadow:qe,railHeight:Je,railWidthVertical:Qe,handleSize:Ze,dotHeight:Ge,dotWidth:ea,dotBorderRadius:aa,fontSize:ta,dotBorderActive:oa,dotColorPopover:na},common:{cubicBezierEaseInOut:ra}}=h.value;return{"--n-bezier":ra,"--n-dot-border":Ye,"--n-dot-border-active":oa,"--n-dot-border-radius":aa,"--n-dot-box-shadow":qe,"--n-dot-color":k,"--n-dot-color-modal":y,"--n-dot-color-popover":na,"--n-dot-height":Ge,"--n-dot-width":ea,"--n-fill-color":d,"--n-fill-color-hover":f,"--n-font-size":ta,"--n-handle-box-shadow":$,"--n-handle-box-shadow-active":pe,"--n-handle-box-shadow-focus":We,"--n-handle-box-shadow-hover":me,"--n-handle-color":w,"--n-handle-size":Ze,"--n-opacity-disabled":V,"--n-rail-color":a,"--n-rail-color-hover":o,"--n-rail-height":Je,"--n-rail-width-vertical":Qe,"--n-mark-font-size":e}}),O=x?Te("slider",void 0,Ce,n):void 0,ze=B(()=>{const{self:{fontSize:e,indicatorColor:a,indicatorBoxShadow:o,indicatorTextColor:d,indicatorBorderRadius:f}}=h.value;return{"--n-font-size":e,"--n-indicator-border-radius":f,"--n-indicator-box-shadow":o,"--n-indicator-color":a,"--n-indicator-text-color":d}}),L=x?Te("slider-indicator",void 0,ze,n):void 0;return{mergedClsPrefix:l,namespace:M,uncontrolledValue:K,mergedValue:Y,mergedDisabled:j,mergedPlacement:ve,isMounted:pa(),adjustedTo:be(n),dotTransitionDisabled:P,markInfos:r,isShowTooltip:we,shouldKeepTooltipTransition:Ae,handleRailRef:g,setHandleRefs:D,setFollowerRefs:X,fillStyle:t,getHandleStyle:_,activeIndex:z,arrifiedValues:b,followerEnabledIndexSet:c,handleRailMouseDown:je,handleHandleFocus:Oe,handleHandleBlur:Le,handleHandleMouseEnter:Xe,handleHandleMouseLeave:Ke,handleRailKeyDown:Ee,indicatorCssVars:x?void 0:ze,indicatorThemeClass:L==null?void 0:L.themeClass,indicatorOnRender:L==null?void 0:L.onRender,cssVars:x?void 0:Ce,themeClass:O==null?void 0:O.themeClass,onRender:O==null?void 0:O.onRender}},render(){var n;const{mergedClsPrefix:l,themeClass:M,formatTooltip:x}=this;return(n=this.onRender)===null||n===void 0||n.call(this),p("div",{class:[`${l}-slider`,M,{[`${l}-slider--disabled`]:this.mergedDisabled,[`${l}-slider--active`]:this.activeIndex!==-1,[`${l}-slider--with-mark`]:this.marks,[`${l}-slider--vertical`]:this.vertical,[`${l}-slider--reverse`]:this.reverse}],style:this.cssVars,onKeydown:this.handleRailKeyDown,onMousedown:this.handleRailMouseDown,onTouchstart:this.handleRailMouseDown},p("div",{class:`${l}-slider-rail`},p("div",{class:`${l}-slider-rail__fill`,style:this.fillStyle}),this.marks?p("div",{class:[`${l}-slider-dots`,this.dotTransitionDisabled&&`${l}-slider-dots--transition-disabled`]},this.markInfos.map(h=>p("div",{key:h.key,class:[`${l}-slider-dot`,{[`${l}-slider-dot--active`]:h.active}],style:h.style}))):null,p("div",{ref:"handleRailRef",class:`${l}-slider-handles`},this.arrifiedValues.map((h,g)=>{const C=this.isShowTooltip(g);return p(Ta,null,{default:()=>[p(Ma,null,{default:()=>p("div",{ref:this.setHandleRefs(g),class:`${l}-slider-handle-wrapper`,tabindex:this.mergedDisabled?-1:0,role:"slider","aria-valuenow":h,"aria-valuemin":this.min,"aria-valuemax":this.max,"aria-orientation":this.vertical?"vertical":"horizontal","aria-disabled":this.disabled,style:this.getHandleStyle(h,g),onFocus:()=>{this.handleHandleFocus(g)},onBlur:()=>{this.handleHandleBlur(g)},onMouseenter:()=>{this.handleHandleMouseEnter(g)},onMouseleave:()=>{this.handleHandleMouseLeave(g)}},ca(this.$slots.thumb,()=>[p("div",{class:`${l}-slider-handle`})]))}),this.tooltip&&p(Da,{ref:this.setFollowerRefs(g),show:C,to:this.adjustedTo,enabled:this.showTooltip&&!this.range||this.followerEnabledIndexSet.has(g),teleportDisabled:this.adjustedTo===be.tdkey,placement:this.mergedPlacement,containerClass:this.namespace},{default:()=>p(va,{name:"fade-in-scale-up-transition",appear:this.isMounted,css:this.shouldKeepTooltipTransition(g),onEnter:()=>{this.followerEnabledIndexSet.add(g)},onAfterLeave:()=>{this.followerEnabledIndexSet.delete(g)}},{default:()=>{var D;return C?((D=this.indicatorOnRender)===null||D===void 0||D.call(this),p("div",{class:[`${l}-slider-handle-indicator`,this.indicatorThemeClass,`${l}-slider-handle-indicator--${this.mergedPlacement}`],style:this.indicatorCssVars},typeof x=="function"?x(h):h)):null}})})]})})),this.marks?p("div",{class:`${l}-slider-marks`},this.markInfos.map(h=>p("div",{key:h.key,class:`${l}-slider-mark`,style:h.style},typeof h.label=="function"?h.label():h.label))):null))}}),tt=He({__name:"index",setup(n){const l=_a(),M=la(),x=M.role==="admin"||M.role==="editor",h=S([]),g=S(!1),C=S(!1),D=S(!1),H=S(null),X=S(),c=S(W());function U(s){const t=(s||"unknown").toLowerCase();return t==="attached"||t==="online"||t==="already_injected"?"online":t==="detached"||t==="offline"?"offline":t==="mounting"?"mounting":t==="error"?"error":"unknown"}const j={online:"success",offline:"error",mounting:"warning",error:"error",unknown:"default"},Q={online:"已挂载",offline:"未挂载",mounting:"挂载中",error:"挂载失败",unknown:"未知"},K=[{title:"名称",key:"name"},{title:"SSH 主机",key:"ssh_host"},{title:"服务端口",key:"service_port",width:90},{title:"Agent 状态",key:"agent_status",width:110,render:s=>{const t=U(s.agent_status);return p(Na,{type:j[t]||"default",size:"small"},()=>Q[t]||"未知")}},{title:"创建时间",key:"created_at",width:160,render:s=>Y(s.created_at)},{title:"操作",key:"actions",render:s=>{const t=U(s.agent_status);return p(ce,{size:4},()=>[...x?[p(I,{size:"tiny",onClick:()=>ee(s.id)},()=>"连接测试"),t==="online"?p(I,{size:"tiny",type:"warning",onClick:()=>A(s.id)},()=>"卸载 Agent"):p(I,{size:"tiny",type:"info",onClick:()=>N(s.id)},()=>"挂载 Agent"),p(I,{size:"tiny",onClick:()=>G(s)},()=>"编辑")]:[],...M.role==="admin"?[p(Ba,{onPositiveClick:()=>P(s.id)},{default:()=>"确认删除？",trigger:()=>p(I,{size:"tiny",type:"error"},()=>"删除")})]:[]])}}];function W(){return{name:"",description:"",ssh_host:"",ssh_user:"",ssh_port:22,ssh_key_path:"",ssh_password:"",service_port:8080,jvm_process_name:"",arex_app_id:"",arex_storage_url:"",sample_rate:1}}function Y(s){return s?s.slice(0,19).replace("T"," "):"-"}async function b(){var s,t;g.value=!0;try{const r=await E.list();h.value=r.data}catch(r){h.value=[],l.error(((t=(s=r.response)==null?void 0:s.data)==null?void 0:t.detail)||"加载应用列表失败")}finally{g.value=!1}}function Z(){c.value=W()}function ve(){H.value=null,Z(),C.value=!0}function G(s){H.value=s.id,c.value={...W(),...s},C.value=!0}async function z(){var s,t;D.value=!0;try{H.value?await E.update(H.value,c.value):await E.create(c.value),l.success("保存成功"),C.value=!1,await b()}catch(r){l.error(((t=(s=r.response)==null?void 0:s.data)==null?void 0:t.detail)||"保存失败")}finally{D.value=!1}}async function ee(s){var t,r;try{const _=await E.testConnection(s);_.data.success?l.success("SSH 连接成功"):l.error(`连接失败：${_.data.message}`)}catch(_){l.error(((r=(t=_.response)==null?void 0:t.data)==null?void 0:r.detail)||"连接测试失败")}}async function N(s){var t,r;try{await E.mountAgent(s),l.info("Agent 挂载已启动，请稍候..."),setTimeout(()=>{b()},3e3)}catch(_){l.error(((r=(t=_.response)==null?void 0:t.data)==null?void 0:r.detail)||"挂载失败")}}async function A(s){var t,r;try{await E.unmountAgent(s),l.success("Agent 已卸载"),await b()}catch(_){l.error(((r=(t=_.response)==null?void 0:t.data)==null?void 0:r.detail)||"卸载失败")}}async function P(s){var t,r;try{await E.delete(s),l.success("删除成功"),await b()}catch(_){l.error(((r=(t=_.response)==null?void 0:t.data)==null?void 0:r.detail)||"删除失败")}}return ba(b),(s,t)=>(Me(),wa(ya,null,[v(u(ce),{vertical:"",size:12},{default:m(()=>[v(u(ce),{justify:"space-between"},{default:m(()=>[v(u(za),{style:{margin:"0"}},{default:m(()=>[...t[14]||(t[14]=[J("应用管理",-1)])]),_:1}),u(x)?(Me(),ka(u(I),{key:0,type:"primary",onClick:ve},{default:m(()=>[...t[15]||(t[15]=[J("+ 新增应用",-1)])]),_:1})):Sa("",!0)]),_:1}),v(u(Ha),{columns:K,data:h.value,loading:g.value,pagination:{pageSize:10}},null,8,["data","loading"])]),_:1}),v(u(xa),{show:C.value,"onUpdate:show":t[13]||(t[13]=r=>C.value=r),title:H.value?"编辑应用":"新增应用",preset:"card",style:{width:"600px"}},{footer:m(()=>[v(u(ce),{justify:"end"},{default:m(()=>[v(u(I),{onClick:t[12]||(t[12]=r=>C.value=!1)},{default:m(()=>[...t[16]||(t[16]=[J("取消",-1)])]),_:1}),v(u(I),{type:"primary",loading:D.value,onClick:z},{default:m(()=>[...t[17]||(t[17]=[J("保存",-1)])]),_:1},8,["loading"])]),_:1})]),default:m(()=>[v(u(Ra),{ref_key:"formRef",ref:X,model:c.value,"label-placement":"left","label-width":"120px"},{default:m(()=>[v(u(T),{label:"应用名称",path:"name",rule:{required:!0,message:"请输入应用名称"}},{default:m(()=>[v(u(F),{value:c.value.name,"onUpdate:value":t[0]||(t[0]=r=>c.value.name=r),placeholder:"例如：demo-service"},null,8,["value"])]),_:1}),v(u(T),{label:"描述"},{default:m(()=>[v(u(F),{value:c.value.description,"onUpdate:value":t[1]||(t[1]=r=>c.value.description=r),placeholder:"可选"},null,8,["value"])]),_:1}),v(u(T),{label:"SSH 主机",path:"ssh_host",rule:{required:!0,message:"请输入 SSH 主机"}},{default:m(()=>[v(u(F),{value:c.value.ssh_host,"onUpdate:value":t[2]||(t[2]=r=>c.value.ssh_host=r),placeholder:"IP 或域名"},null,8,["value"])]),_:1}),v(u(T),{label:"SSH 用户",path:"ssh_user",rule:{required:!0,message:"请输入 SSH 用户"}},{default:m(()=>[v(u(F),{value:c.value.ssh_user,"onUpdate:value":t[3]||(t[3]=r=>c.value.ssh_user=r),placeholder:"例如：ubuntu"},null,8,["value"])]),_:1}),v(u(T),{label:"SSH 端口"},{default:m(()=>[v(u(De),{value:c.value.ssh_port,"onUpdate:value":t[4]||(t[4]=r=>c.value.ssh_port=r)},null,8,["value"])]),_:1}),v(u(T),{label:"SSH 密钥路径"},{default:m(()=>[v(u(F),{value:c.value.ssh_key_path,"onUpdate:value":t[5]||(t[5]=r=>c.value.ssh_key_path=r),placeholder:"/path/to/key"},null,8,["value"])]),_:1}),v(u(T),{label:"SSH 密码"},{default:m(()=>[v(u(F),{value:c.value.ssh_password,"onUpdate:value":t[6]||(t[6]=r=>c.value.ssh_password=r),type:"password"},null,8,["value"])]),_:1}),v(u(T),{label:"服务端口"},{default:m(()=>[v(u(De),{value:c.value.service_port,"onUpdate:value":t[7]||(t[7]=r=>c.value.service_port=r)},null,8,["value"])]),_:1}),v(u(T),{label:"JVM 进程名"},{default:m(()=>[v(u(F),{value:c.value.jvm_process_name,"onUpdate:value":t[8]||(t[8]=r=>c.value.jvm_process_name=r),placeholder:"用于 pgrep 识别"},null,8,["value"])]),_:1}),v(u(T),{label:"AREX App ID"},{default:m(()=>[v(u(F),{value:c.value.arex_app_id,"onUpdate:value":t[9]||(t[9]=r=>c.value.arex_app_id=r)},null,8,["value"])]),_:1}),v(u(T),{label:"AREX Storage 地址"},{default:m(()=>[v(u(F),{value:c.value.arex_storage_url,"onUpdate:value":t[10]||(t[10]=r=>c.value.arex_storage_url=r),placeholder:"留空则使用全局配置"},null,8,["value"])]),_:1}),v(u(T),{label:"采样率"},{default:m(()=>[v(u(Pa),{value:c.value.sample_rate,"onUpdate:value":t[11]||(t[11]=r=>c.value.sample_rate=r),min:0,max:1,step:.1,style:{width:"200px"}},null,8,["value"]),v(u(Aa),{style:{"margin-left":"12px"}},{default:m(()=>[J(Ca(c.value.sample_rate),1)]),_:1})]),_:1})]),_:1},8,["model"])]),_:1},8,["show","title"])],64))}});export{tt as default};
