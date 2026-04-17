import{a as ga,o as ee,g as v,i as M,n as fe,Y as $e,Z as ba,_ as wa,$ as ya,d as Ke,h as m,a0 as xa,a1 as _a,u as ka,j as Ye,a2 as Ca,r as C,a3 as Ie,a4 as Ra,l as Fe,a5 as za,m as A,t as he,a6 as pe,a7 as me,a8 as Ne,v as Sa,a9 as Na,M as He,L as l,I as i,J as o,aa as Ta,F as Ee,T as Da,X as Te,K as _,R as b,H as Ma,Q as $,O as je,ab as W,P as ae}from"./index-D6LB0ej7.js";import{a as X}from"./applications-Dy8uQOUo.js";import{f as Aa}from"./format-Adq5_zH5.js";import{u as Ba}from"./user-D9e99449.js";import{u as Va,N as S}from"./index-B6sC-FX3.js";import{N as Ua}from"./headers-V4EArN97.js";import{N as Pe}from"./text-CRjEex7h.js";import{N as $a,a as ge}from"./Grid-Db3RjpGB.js";import{N as be}from"./Statistic-CvgP2Lih.js";import{N as Ia}from"./DataTable-C6hf0yd5.js";import{N as Oe,a as Fa}from"./Select-C5OqV45F.js";import{N as te}from"./Alert-DJgzMnL0.js";import{N as Ha,a as w}from"./FormItem-C3cxdKJ9.js";import{N as Le}from"./InputNumber-BYwqFy12.js";import{B as Ea,a as ja,b as Pa,d as De,N as G}from"./Space-JgVsnMPf.js";import{u as Oa}from"./get-I2R12OG2.js";import{N as La}from"./Popconfirm-D0srH-Q6.js";import{_ as Xa}from"./_plugin-vue_export-helper-DlAUqK2U.js";import"./light-DxWD4W-X.js";import"./Tooltip-B2js9o6V.js";import"./Dropdown-Bfvnp9d9.js";import"./Add--q_lcfUf.js";const qa={railHeight:"4px",railWidthVertical:"4px",handleSize:"18px",dotHeight:"8px",dotWidth:"8px",dotBorderRadius:"4px"};function Ka(s){const c="rgba(0, 0, 0, .85)",B="0 2px 8px 0 rgba(0, 0, 0, 0.12)",{railColor:y,primaryColor:g,baseColor:h,cardColor:V,modalColor:N,popoverColor:L,borderRadius:I,fontSize:j,opacityDisabled:q}=s;return Object.assign(Object.assign({},qa),{fontSize:j,markFontSize:j,railColor:y,railColorHover:y,fillColor:g,fillColorHover:g,opacityDisabled:q,handleColor:"#FFF",dotColor:V,dotColorModal:N,dotColorPopover:L,handleBoxShadow:"0 1px 4px 0 rgba(0, 0, 0, 0.3), inset 0 0 1px 0 rgba(0, 0, 0, 0.05)",handleBoxShadowHover:"0 1px 4px 0 rgba(0, 0, 0, 0.3), inset 0 0 1px 0 rgba(0, 0, 0, 0.05)",handleBoxShadowActive:"0 1px 4px 0 rgba(0, 0, 0, 0.3), inset 0 0 1px 0 rgba(0, 0, 0, 0.05)",handleBoxShadowFocus:"0 1px 4px 0 rgba(0, 0, 0, 0.3), inset 0 0 1px 0 rgba(0, 0, 0, 0.05)",indicatorColor:c,indicatorBoxShadow:B,indicatorTextColor:h,indicatorBorderRadius:I,dotBorder:`2px solid ${y}`,dotBorderActive:`2px solid ${g}`,dotBoxShadow:""})}const Ya={common:ga,self:Ka},Ja=ee([v("slider",`
 display: block;
 padding: calc((var(--n-handle-size) - var(--n-rail-height)) / 2) 0;
 position: relative;
 z-index: 0;
 width: 100%;
 cursor: pointer;
 user-select: none;
 -webkit-user-select: none;
 `,[M("reverse",[v("slider-handles",[v("slider-handle-wrapper",`
 transform: translate(50%, -50%);
 `)]),v("slider-dots",[v("slider-dot",`
 transform: translateX(50%, -50%);
 `)]),M("vertical",[v("slider-handles",[v("slider-handle-wrapper",`
 transform: translate(-50%, -50%);
 `)]),v("slider-marks",[v("slider-mark",`
 transform: translateY(calc(-50% + var(--n-dot-height) / 2));
 `)]),v("slider-dots",[v("slider-dot",`
 transform: translateX(-50%) translateY(0);
 `)])])]),M("vertical",`
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
 `,[fe("fill",`
 top: unset;
 right: 0;
 bottom: unset;
 left: 0;
 `)]),M("with-mark",`
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
 `)])]),M("disabled",`
 cursor: not-allowed;
 opacity: var(--n-opacity-disabled);
 `,[v("slider-handle",`
 cursor: not-allowed;
 `)]),M("with-mark",`
 width: 100%;
 margin: 8px 0 32px 0;
 `),ee("&:hover",[v("slider-rail",{backgroundColor:"var(--n-rail-color-hover)"},[fe("fill",{backgroundColor:"var(--n-fill-color-hover)"})]),v("slider-handle",{boxShadow:"var(--n-handle-box-shadow-hover)"})]),M("active",[v("slider-rail",{backgroundColor:"var(--n-rail-color-hover)"},[fe("fill",{backgroundColor:"var(--n-fill-color-hover)"})]),v("slider-handle",{boxShadow:"var(--n-handle-box-shadow-hover)"})]),v("slider-marks",`
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
 `,[fe("fill",`
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
 `,[ee("&:hover",`
 box-shadow: var(--n-handle-box-shadow-hover);
 `)]),ee("&:focus",[v("slider-handle",`
 box-shadow: var(--n-handle-box-shadow-focus);
 `,[ee("&:hover",`
 box-shadow: var(--n-handle-box-shadow-active);
 `)])])])]),v("slider-dots",`
 position: absolute;
 top: 50%;
 left: calc(var(--n-handle-size) / 2);
 right: calc(var(--n-handle-size) / 2);
 `,[M("transition-disabled",[v("slider-dot","transition: none;")]),v("slider-dot",`
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
 `,[M("active","border: var(--n-dot-border-active);")])])]),v("slider-handle-indicator",`
 font-size: var(--n-font-size);
 padding: 6px 10px;
 border-radius: var(--n-indicator-border-radius);
 color: var(--n-indicator-text-color);
 background-color: var(--n-indicator-color);
 box-shadow: var(--n-indicator-box-shadow);
 `,[$e()]),v("slider-handle-indicator",`
 font-size: var(--n-font-size);
 padding: 6px 10px;
 border-radius: var(--n-indicator-border-radius);
 color: var(--n-indicator-text-color);
 background-color: var(--n-indicator-color);
 box-shadow: var(--n-indicator-box-shadow);
 `,[M("top",`
 margin-bottom: 12px;
 `),M("right",`
 margin-left: 12px;
 `),M("bottom",`
 margin-top: 12px;
 `),M("left",`
 margin-right: 12px;
 `),$e()]),ba(v("slider",[v("slider-dot","background-color: var(--n-dot-color-modal);")])),wa(v("slider",[v("slider-dot","background-color: var(--n-dot-color-popover);")]))]);function Xe(s){return window.TouchEvent&&s instanceof window.TouchEvent}function qe(){const s=new Map,c=B=>y=>{s.set(B,y)};return ya(()=>{s.clear()}),[s,c]}const Wa=0,Ga=Object.assign(Object.assign({},Ye.props),{to:De.propTo,defaultValue:{type:[Number,Array],default:0},marks:Object,disabled:{type:Boolean,default:void 0},formatTooltip:Function,keyboard:{type:Boolean,default:!0},min:{type:Number,default:0},max:{type:Number,default:100},step:{type:[Number,String],default:1},range:Boolean,value:[Number,Array],placement:String,showTooltip:{type:Boolean,default:void 0},tooltip:{type:Boolean,default:!0},vertical:Boolean,reverse:Boolean,"onUpdate:value":[Function,Array],onUpdateValue:[Function,Array],onDragstart:[Function],onDragend:[Function]}),Qa=Ke({name:"Slider",props:Ga,slots:Object,setup(s){const{mergedClsPrefixRef:c,namespaceRef:B,inlineThemeDisabled:y}=ka(s),g=Ye("Slider","-slider",Ja,Ya,s,c),h=C(null),[V,N]=qe(),[L,I]=qe(),j=C(new Set),q=Ca(s),{mergedDisabledRef:d}=q,oe=A(()=>{const{step:a}=s;if(Number(a)<=0||a==="mark")return 0;const t=a.toString();let n=0;return t.includes(".")&&(n=t.length-t.indexOf(".")-1),n}),Q=C(s.defaultValue),we=Sa(s,"value"),F=Oa(we,Q),T=A(()=>{const{value:a}=F;return(s.range?a:[a]).map(Ae)}),le=A(()=>T.value.length>2),ye=A(()=>s.placement===void 0?s.vertical?"right":"top":s.placement),ne=A(()=>{const{marks:a}=s;return a?Object.keys(a).map(Number.parseFloat):null}),R=C(-1),P=C(-1),H=C(-1),E=C(!1),K=C(!1),Z=A(()=>{const{vertical:a,reverse:t}=s;return a?t?"top":"bottom":t?"right":"left"}),xe=A(()=>{if(le.value)return;const a=T.value,t=se(s.range?Math.min(...a):s.min),n=se(s.range?Math.max(...a):a[0]),{value:f}=Z;return s.vertical?{[f]:`${t}%`,height:`${n-t}%`}:{[f]:`${t}%`,width:`${n-t}%`}}),_e=A(()=>{const a=[],{marks:t}=s;if(t){const n=T.value.slice();n.sort((z,k)=>z-k);const{value:f}=Z,{value:p}=le,{range:x}=s,U=p?()=>!1:z=>x?z>=n[0]&&z<=n[n.length-1]:z<=n[0];for(const z of Object.keys(t)){const k=Number(z);a.push({active:U(k),key:k,label:t[z],style:{[f]:`${se(k)}%`}})}}return a});function ke(a,t){const n=se(a),{value:f}=Z;return{[f]:`${n}%`,zIndex:t===R.value?1:0}}function re(a){return s.showTooltip||H.value===a||R.value===a&&E.value}function u(a){return E.value?!(R.value===a&&P.value===a):!0}function e(a){var t;~a&&(R.value=a,(t=V.get(a))===null||t===void 0||t.focus())}function r(){L.forEach((a,t)=>{re(t)&&a.syncPosition()})}function D(a){const{"onUpdate:value":t,onUpdateValue:n}=s,{nTriggerFormInput:f,nTriggerFormChange:p}=q;n&&he(n,a),t&&he(t,a),Q.value=a,f(),p()}function Me(a){const{range:t}=s;if(t){if(Array.isArray(a)){const{value:n}=T;a.join()!==n.join()&&D(a)}}else Array.isArray(a)||T.value[0]!==a&&D(a)}function Ce(a,t){if(s.range){const n=T.value.slice();n.splice(t,1,a),Me(n)}else Me(a)}function Re(a,t,n){const f=n!==void 0;n||(n=a-t>0?1:-1);const p=ne.value||[],{step:x}=s;if(x==="mark"){const k=ie(a,p.concat(t),f?n:void 0);return k?k.value:t}if(x<=0)return t;const{value:U}=oe;let z;if(f){const k=Number((t/x).toFixed(U)),O=Math.floor(k),ze=k>O?O:O-1,Se=k<O?O:O+1;z=ie(t,[Number((ze*x).toFixed(U)),Number((Se*x).toFixed(U)),...p],n)}else{const k=We(a);z=ie(a,[...p,k])}return z?Ae(z.value):t}function Ae(a){return Math.min(s.max,Math.max(s.min,a))}function se(a){const{max:t,min:n}=s;return(a-n)/(t-n)*100}function Je(a){const{max:t,min:n}=s;return n+(t-n)*a}function We(a){const{step:t,min:n}=s;if(Number(t)<=0||t==="mark")return a;const f=Math.round((a-n)/t)*t+n;return Number(f.toFixed(oe.value))}function ie(a,t=ne.value,n){if(!(t!=null&&t.length))return null;let f=null,p=-1;for(;++p<t.length;){const x=t[p]-a,U=Math.abs(x);(n===void 0||x*n>0)&&(f===null||U<f.distance)&&(f={index:p,distance:U,value:t[p]})}return f}function Be(a){const t=h.value;if(!t)return;const n=Xe(a)?a.touches[0]:a,f=t.getBoundingClientRect();let p;return s.vertical?p=(f.bottom-n.clientY)/f.height:p=(n.clientX-f.left)/f.width,s.reverse&&(p=1-p),Je(p)}function Ge(a){if(d.value||!s.keyboard)return;const{vertical:t,reverse:n}=s;switch(a.key){case"ArrowUp":a.preventDefault(),de(t&&n?-1:1);break;case"ArrowRight":a.preventDefault(),de(!t&&n?-1:1);break;case"ArrowDown":a.preventDefault(),de(t&&n?1:-1);break;case"ArrowLeft":a.preventDefault(),de(!t&&n?1:-1);break}}function de(a){const t=R.value;if(t===-1)return;const{step:n}=s,f=T.value[t],p=Number(n)<=0||n==="mark"?f:f+n*a;Ce(Re(p,f,a>0?1:-1),t)}function Qe(a){var t,n;if(d.value||!Xe(a)&&a.button!==Wa)return;const f=Be(a);if(f===void 0)return;const p=T.value.slice(),x=s.range?(n=(t=ie(f,p))===null||t===void 0?void 0:t.index)!==null&&n!==void 0?n:-1:0;x!==-1&&(a.preventDefault(),e(x),Ze(),Ce(Re(f,T.value[x]),x))}function Ze(){E.value||(E.value=!0,s.onDragstart&&he(s.onDragstart),pe("touchend",document,ve),pe("mouseup",document,ve),pe("touchmove",document,ce),pe("mousemove",document,ce))}function ue(){E.value&&(E.value=!1,s.onDragend&&he(s.onDragend),me("touchend",document,ve),me("mouseup",document,ve),me("touchmove",document,ce),me("mousemove",document,ce))}function ce(a){const{value:t}=R;if(!E.value||t===-1){ue();return}const n=Be(a);n!==void 0&&Ce(Re(n,T.value[t]),t)}function ve(){ue()}function ea(a){R.value=a,d.value||(H.value=a)}function aa(a){R.value===a&&(R.value=-1,ue()),H.value===a&&(H.value=-1)}function ta(a){H.value=a}function oa(a){H.value===a&&(H.value=-1)}Ie(R,(a,t)=>void Ne(()=>P.value=t)),Ie(F,()=>{if(s.marks){if(K.value)return;K.value=!0,Ne(()=>{K.value=!1})}Ne(r)}),Ra(()=>{ue()});const Ve=A(()=>{const{self:{markFontSize:a,railColor:t,railColorHover:n,fillColor:f,fillColorHover:p,handleColor:x,opacityDisabled:U,dotColor:z,dotColorModal:k,handleBoxShadow:O,handleBoxShadowHover:ze,handleBoxShadowActive:Se,handleBoxShadowFocus:la,dotBorder:na,dotBoxShadow:ra,railHeight:sa,railWidthVertical:ia,handleSize:da,dotHeight:ua,dotWidth:ca,dotBorderRadius:va,fontSize:fa,dotBorderActive:ha,dotColorPopover:pa},common:{cubicBezierEaseInOut:ma}}=g.value;return{"--n-bezier":ma,"--n-dot-border":na,"--n-dot-border-active":ha,"--n-dot-border-radius":va,"--n-dot-box-shadow":ra,"--n-dot-color":z,"--n-dot-color-modal":k,"--n-dot-color-popover":pa,"--n-dot-height":ua,"--n-dot-width":ca,"--n-fill-color":f,"--n-fill-color-hover":p,"--n-font-size":fa,"--n-handle-box-shadow":O,"--n-handle-box-shadow-active":Se,"--n-handle-box-shadow-focus":la,"--n-handle-box-shadow-hover":ze,"--n-handle-color":x,"--n-handle-size":da,"--n-opacity-disabled":U,"--n-rail-color":t,"--n-rail-color-hover":n,"--n-rail-height":sa,"--n-rail-width-vertical":ia,"--n-mark-font-size":a}}),Y=y?Fe("slider",void 0,Ve,s):void 0,Ue=A(()=>{const{self:{fontSize:a,indicatorColor:t,indicatorBoxShadow:n,indicatorTextColor:f,indicatorBorderRadius:p}}=g.value;return{"--n-font-size":a,"--n-indicator-border-radius":p,"--n-indicator-box-shadow":n,"--n-indicator-color":t,"--n-indicator-text-color":f}}),J=y?Fe("slider-indicator",void 0,Ue,s):void 0;return{mergedClsPrefix:c,namespace:B,uncontrolledValue:Q,mergedValue:F,mergedDisabled:d,mergedPlacement:ye,isMounted:za(),adjustedTo:De(s),dotTransitionDisabled:K,markInfos:_e,isShowTooltip:re,shouldKeepTooltipTransition:u,handleRailRef:h,setHandleRefs:N,setFollowerRefs:I,fillStyle:xe,getHandleStyle:ke,activeIndex:R,arrifiedValues:T,followerEnabledIndexSet:j,handleRailMouseDown:Qe,handleHandleFocus:ea,handleHandleBlur:aa,handleHandleMouseEnter:ta,handleHandleMouseLeave:oa,handleRailKeyDown:Ge,indicatorCssVars:y?void 0:Ue,indicatorThemeClass:J==null?void 0:J.themeClass,indicatorOnRender:J==null?void 0:J.onRender,cssVars:y?void 0:Ve,themeClass:Y==null?void 0:Y.themeClass,onRender:Y==null?void 0:Y.onRender}},render(){var s;const{mergedClsPrefix:c,themeClass:B,formatTooltip:y}=this;return(s=this.onRender)===null||s===void 0||s.call(this),m("div",{class:[`${c}-slider`,B,{[`${c}-slider--disabled`]:this.mergedDisabled,[`${c}-slider--active`]:this.activeIndex!==-1,[`${c}-slider--with-mark`]:this.marks,[`${c}-slider--vertical`]:this.vertical,[`${c}-slider--reverse`]:this.reverse}],style:this.cssVars,onKeydown:this.handleRailKeyDown,onMousedown:this.handleRailMouseDown,onTouchstart:this.handleRailMouseDown},m("div",{class:`${c}-slider-rail`},m("div",{class:`${c}-slider-rail__fill`,style:this.fillStyle}),this.marks?m("div",{class:[`${c}-slider-dots`,this.dotTransitionDisabled&&`${c}-slider-dots--transition-disabled`]},this.markInfos.map(g=>m("div",{key:g.key,class:[`${c}-slider-dot`,{[`${c}-slider-dot--active`]:g.active}],style:g.style}))):null,m("div",{ref:"handleRailRef",class:`${c}-slider-handles`},this.arrifiedValues.map((g,h)=>{const V=this.isShowTooltip(h);return m(Ea,null,{default:()=>[m(ja,null,{default:()=>m("div",{ref:this.setHandleRefs(h),class:`${c}-slider-handle-wrapper`,tabindex:this.mergedDisabled?-1:0,role:"slider","aria-valuenow":g,"aria-valuemin":this.min,"aria-valuemax":this.max,"aria-orientation":this.vertical?"vertical":"horizontal","aria-disabled":this.disabled,style:this.getHandleStyle(g,h),onFocus:()=>{this.handleHandleFocus(h)},onBlur:()=>{this.handleHandleBlur(h)},onMouseenter:()=>{this.handleHandleMouseEnter(h)},onMouseleave:()=>{this.handleHandleMouseLeave(h)}},xa(this.$slots.thumb,()=>[m("div",{class:`${c}-slider-handle`})]))}),this.tooltip&&m(Pa,{ref:this.setFollowerRefs(h),show:V,to:this.adjustedTo,enabled:this.showTooltip&&!this.range||this.followerEnabledIndexSet.has(h),teleportDisabled:this.adjustedTo===De.tdkey,placement:this.mergedPlacement,containerClass:this.namespace},{default:()=>m(_a,{name:"fade-in-scale-up-transition",appear:this.isMounted,css:this.shouldKeepTooltipTransition(h),onEnter:()=>{this.followerEnabledIndexSet.add(h)},onAfterLeave:()=>{this.followerEnabledIndexSet.delete(h)}},{default:()=>{var N;return V?((N=this.indicatorOnRender)===null||N===void 0||N.call(this),m("div",{class:[`${c}-slider-handle-indicator`,this.indicatorThemeClass,`${c}-slider-handle-indicator--${this.mergedPlacement}`],style:this.indicatorCssVars},typeof y=="function"?y(g):g)):null}})})]})})),this.marks?m("div",{class:`${c}-slider-marks`},this.markInfos.map(g=>m("div",{key:g.key,class:`${c}-slider-mark`,style:g.style},typeof g.label=="function"?g.label():g.label))):null))}}),Za={style:{color:"#18a058"}},et={style:{color:"#d03050"}},at={style:{color:"#f0a020"}},tt=Ke({__name:"index",setup(s){const c=Va(),B=Da(),y=Ba(),g=y.role==="admin"||y.role==="editor",h=C([]),V=C(!1),N=C(!1),L=C(!1),I=C(null),j=C(!1),q=C(),d=C(R()),oe=A(()=>h.value.filter(u=>F(u.agent_status)==="online").length),Q=A(()=>h.value.filter(u=>F(u.agent_status)==="offline").length),we=A(()=>h.value.filter(u=>F(u.agent_status)==="mounting").length);function F(u){const e=(u||"unknown").toLowerCase();return e==="attached"||e==="online"||e==="already_injected"?"online":e==="detached"||e==="offline"?"offline":e==="mounting"?"mounting":e==="error"?"error":"unknown"}const T={online:"success",offline:"error",mounting:"warning",error:"error",unknown:"default"},le={online:"已挂载",offline:"未挂载",mounting:"挂载中",error:"挂载失败",unknown:"未知"},ye=[{label:"宿主机脚本",value:"ssh_script"},{label:"Docker Compose",value:"docker_compose"}],ne=[{title:"名称",key:"name",width:220,render:u=>m($,{text:!0,type:"primary",onClick:()=>B.push(`/applications/${u.id}`)},()=>u.name)},{title:"宿主机",key:"ssh_host",width:220},{title:"服务端口",key:"service_port",width:110},{title:"Agent 状态",key:"agent_status",width:130,render:u=>{const e=F(u.agent_status);return m(Oe,{type:T[e]||"default",size:"small"},()=>le[e]||"未知")}},{title:"创建时间",key:"created_at",width:180,render:u=>Aa(u.created_at)},{title:"操作",key:"actions",width:320,render:u=>{const e=F(u.agent_status);return m(G,{size:8,wrap:!0},()=>[m($,{size:"tiny",onClick:()=>B.push(`/applications/${u.id}`)},()=>"查看详情"),...g?[m($,{size:"tiny",onClick:()=>xe(u.id)},()=>"连接测试"),e==="online"?m($,{size:"tiny",type:"warning",onClick:()=>ke(u.id)},()=>"卸载 Agent"):m($,{size:"tiny",type:"info",onClick:()=>_e(u.id)},()=>"挂载 Agent"),m($,{size:"tiny",onClick:()=>K(u)},()=>"编辑")]:[],...y.role==="admin"?[m(La,{onPositiveClick:()=>re(u.id)},{default:()=>"确认删除？",trigger:()=>m($,{size:"tiny",type:"error"},()=>"删除")})]:[]])}}];function R(){return{name:"",description:"",ssh_host:"",ssh_user:"",ssh_port:22,launch_mode:"ssh_script",ssh_key_path:"",ssh_password:"",docker_workdir:"",docker_compose_file:"docker-compose.yml",docker_service_name:"",docker_storage_url:"",docker_agent_path:"/opt/arex/arex-agent.jar",service_port:8080,jvm_process_name:"",arex_app_id:"",arex_storage_url:"",sample_rate:1,transaction_mappings:""}}async function P(){var u,e;V.value=!0;try{const r=await X.list();h.value=r.data}catch(r){h.value=[],c.error(((e=(u=r.response)==null?void 0:u.data)==null?void 0:e.detail)||"加载应用列表失败")}finally{V.value=!1}}function H(){d.value=R()}function E(){I.value=null,j.value=!1,H(),N.value=!0}function K(u){I.value=u.id,j.value=!!u.has_password,d.value={...R(),...u,ssh_password:"",transaction_mappings:Array.isArray(u.transaction_mappings)?JSON.stringify(u.transaction_mappings,null,2):""},N.value=!0}async function Z(){var u,e;L.value=!0;try{I.value?await X.update(I.value,d.value):await X.create(d.value),c.success("保存成功"),N.value=!1,await P()}catch(r){c.error(((e=(u=r.response)==null?void 0:u.data)==null?void 0:e.detail)||"保存失败")}finally{L.value=!1}}async function xe(u){var e,r;try{const D=await X.testConnection(u);D.data.success?c.success("连接成功"):c.error(`连接失败：${D.data.message}`)}catch(D){c.error(((r=(e=D.response)==null?void 0:e.data)==null?void 0:r.detail)||"连接测试失败")}}async function _e(u){var e,r;try{await X.mountAgent(u),c.info("Agent 挂载已启动，请稍候..."),setTimeout(()=>{P()},3e3)}catch(D){c.error(((r=(e=D.response)==null?void 0:e.data)==null?void 0:r.detail)||"挂载失败")}}async function ke(u){var e,r;try{await X.unmountAgent(u),c.success("Agent 已卸载"),await P()}catch(D){c.error(((r=(e=D.response)==null?void 0:e.data)==null?void 0:r.detail)||"卸载失败")}}async function re(u){var e,r;try{await X.delete(u),c.success("删除成功"),await P()}catch(D){c.error(((r=(e=D.response)==null?void 0:e.data)==null?void 0:r.detail)||"删除失败")}}return Na(P),(u,e)=>(Te(),He(Ee,null,[l(o(G),{vertical:"",size:16,class:"applications-page"},{default:i(()=>[l(o(G),{justify:"space-between",align:"center"},{default:i(()=>[_("div",null,[l(o(Ua),{style:{margin:"0"}},{default:i(()=>[...e[21]||(e[21]=[b("应用管理",-1)])]),_:1}),l(o(Pe),{depth:"3"},{default:i(()=>[...e[22]||(e[22]=[b("统一管理被测应用、接入配置和 Agent 状态。",-1)])]),_:1})]),o(g)?(Te(),Ma(o($),{key:0,type:"primary",onClick:E},{default:i(()=>[...e[23]||(e[23]=[b("+ 新增应用",-1)])]),_:1})):je("",!0)]),_:1}),l(o($a),{cols:4,"x-gap":12,"y-gap":12},{default:i(()=>[l(o(ge),null,{default:i(()=>[l(o(W),null,{default:i(()=>[l(o(be),{label:"应用总数",value:h.value.length},null,8,["value"])]),_:1})]),_:1}),l(o(ge),null,{default:i(()=>[l(o(W),null,{default:i(()=>[l(o(be),{label:"已挂载"},{default:i(()=>[_("span",Za,ae(oe.value),1)]),_:1})]),_:1})]),_:1}),l(o(ge),null,{default:i(()=>[l(o(W),null,{default:i(()=>[l(o(be),{label:"未挂载"},{default:i(()=>[_("span",et,ae(Q.value),1)]),_:1})]),_:1})]),_:1}),l(o(ge),null,{default:i(()=>[l(o(W),null,{default:i(()=>[l(o(be),{label:"挂载中"},{default:i(()=>[_("span",at,ae(we.value),1)]),_:1})]),_:1})]),_:1})]),_:1}),l(o(W),{title:"应用列表"},{"header-extra":i(()=>[l(o(Oe),{type:"info",size:"small"},{default:i(()=>[b("共 "+ae(h.value.length)+" 个应用",1)]),_:1})]),default:i(()=>[l(o(Ia),{class:"applications-table",columns:ne,data:h.value,loading:V.value,pagination:{pageSize:10}},null,8,["data","loading"])]),_:1}),l(o(W),{title:"页面说明"},{default:i(()=>[l(o(G),{vertical:"",size:8},{default:i(()=>[l(o(te),{type:"info","show-icon":!1},{default:i(()=>[...e[24]||(e[24]=[b(" 页面采用上下结构展示，表格列间距和左右留白已拉宽，便于大屏阅读。 ",-1)])]),_:1}),l(o(te),{type:"warning","show-icon":!1},{default:i(()=>[...e[25]||(e[25]=[b(" 新增 / 编辑时只需要补充宿主机、端口、服务进程和 AREX 配置即可。 ",-1)])]),_:1})]),_:1})]),_:1})]),_:1}),l(o(Ta),{show:N.value,"onUpdate:show":e[20]||(e[20]=r=>N.value=r),title:I.value?"编辑应用":"新增应用",preset:"card",style:{width:"600px"}},{footer:i(()=>[l(o(G),{justify:"end"},{default:i(()=>[l(o($),{onClick:e[19]||(e[19]=r=>N.value=!1)},{default:i(()=>[...e[31]||(e[31]=[b("取消",-1)])]),_:1}),l(o($),{type:"primary",loading:L.value,onClick:Z},{default:i(()=>[...e[32]||(e[32]=[b("保存",-1)])]),_:1},8,["loading"])]),_:1})]),default:i(()=>[l(o(Ha),{ref_key:"formRef",ref:q,model:d.value,"label-placement":"left","label-width":"120px"},{default:i(()=>[e[29]||(e[29]=_("input",{type:"text",style:{display:"none"},autocomplete:"username",tabindex:"-1","aria-hidden":"true"},null,-1)),e[30]||(e[30]=_("input",{type:"password",style:{display:"none"},autocomplete:"current-password",tabindex:"-1","aria-hidden":"true"},null,-1)),l(o(w),{label:"应用名称",path:"name",rule:{required:!0,message:"请输入应用名称"}},{default:i(()=>[l(o(S),{value:d.value.name,"onUpdate:value":e[0]||(e[0]=r=>d.value.name=r),placeholder:"例如：demo-service"},null,8,["value"])]),_:1}),l(o(w),{label:"描述"},{default:i(()=>[l(o(S),{value:d.value.description,"onUpdate:value":e[1]||(e[1]=r=>d.value.description=r),placeholder:"可选"},null,8,["value"])]),_:1}),l(o(w),{label:"宿主机地址",path:"ssh_host",rule:{required:!0,message:"请输入宿主机地址"}},{default:i(()=>[l(o(S),{value:d.value.ssh_host,"onUpdate:value":e[2]||(e[2]=r=>d.value.ssh_host=r),placeholder:"IP 或域名"},null,8,["value"])]),_:1}),l(o(w),{label:"宿主机用户",path:"ssh_user",rule:{required:!0,message:"请输入宿主机用户"}},{default:i(()=>[l(o(S),{value:d.value.ssh_user,"onUpdate:value":e[3]||(e[3]=r=>d.value.ssh_user=r),placeholder:"例如：ubuntu"},null,8,["value"])]),_:1}),l(o(w),{label:"宿主机端口"},{default:i(()=>[l(o(Le),{value:d.value.ssh_port,"onUpdate:value":e[4]||(e[4]=r=>d.value.ssh_port=r)},null,8,["value"])]),_:1}),l(o(w),{label:"启动模式"},{default:i(()=>[l(o(Fa),{value:d.value.launch_mode,"onUpdate:value":e[5]||(e[5]=r=>d.value.launch_mode=r),options:ye},null,8,["value"])]),_:1}),l(o(te),{type:"info","show-icon":!1},{default:i(()=>[...e[26]||(e[26]=[b(" Docker 模式由平台生成启动模板并通过 docker compose 控制容器重建，不再修改 start.sh。 ",-1)])]),_:1}),d.value.launch_mode==="docker_compose"?(Te(),He(Ee,{key:0},[l(o(w),{label:"Docker 工作目录",path:"docker_workdir",rule:{required:!0,message:"请输入 Docker 工作目录"}},{default:i(()=>[l(o(S),{value:d.value.docker_workdir,"onUpdate:value":e[6]||(e[6]=r=>d.value.docker_workdir=r),placeholder:"/home/test/N-LS"},null,8,["value"])]),_:1}),l(o(w),{label:"Docker Compose 文件"},{default:i(()=>[l(o(S),{value:d.value.docker_compose_file,"onUpdate:value":e[7]||(e[7]=r=>d.value.docker_compose_file=r),placeholder:"docker-compose.yml"},null,8,["value"])]),_:1}),l(o(w),{label:"Compose 服务名",path:"docker_service_name",rule:{required:!0,message:"请输入 Compose 服务名"}},{default:i(()=>[l(o(S),{value:d.value.docker_service_name,"onUpdate:value":e[8]||(e[8]=r=>d.value.docker_service_name=r),placeholder:"sat / uat / app-service"},null,8,["value"])]),_:1}),l(o(w),{label:"Docker Agent Storage"},{default:i(()=>[l(o(S),{value:d.value.docker_storage_url,"onUpdate:value":e[9]||(e[9]=r=>d.value.docker_storage_url=r),placeholder:"留空则使用平台默认 Docker storage URL"},null,8,["value"])]),_:1}),l(o(w),{label:"Agent 挂载路径"},{default:i(()=>[l(o(S),{value:d.value.docker_agent_path,"onUpdate:value":e[10]||(e[10]=r=>d.value.docker_agent_path=r),placeholder:"/opt/arex/arex-agent.jar"},null,8,["value"])]),_:1})],64)):je("",!0),l(o(w),{label:"密钥路径"},{default:i(()=>[l(o(S),{value:d.value.ssh_key_path,"onUpdate:value":e[11]||(e[11]=r=>d.value.ssh_key_path=r),placeholder:"/path/to/key","input-props":{autocomplete:"new-password"}},null,8,["value"])]),_:1}),l(o(w),{label:"连接密码"},{default:i(()=>[l(o(S),{value:d.value.ssh_password,"onUpdate:value":e[12]||(e[12]=r=>d.value.ssh_password=r),type:"password","input-props":{autocomplete:"new-password"},placeholder:j.value?"已设置密码（留空不修改）":"可选"},null,8,["value","placeholder"])]),_:1}),l(o(w),{label:"服务端口"},{default:i(()=>[l(o(Le),{value:d.value.service_port,"onUpdate:value":e[13]||(e[13]=r=>d.value.service_port=r)},null,8,["value"])]),_:1}),l(o(w),{label:"JVM 进程名"},{default:i(()=>[l(o(S),{value:d.value.jvm_process_name,"onUpdate:value":e[14]||(e[14]=r=>d.value.jvm_process_name=r),placeholder:"用于 pgrep 识别"},null,8,["value"])]),_:1}),l(o(w),{label:"AREX App ID"},{default:i(()=>[l(o(S),{value:d.value.arex_app_id,"onUpdate:value":e[15]||(e[15]=r=>d.value.arex_app_id=r)},null,8,["value"])]),_:1}),l(o(w),{label:"AREX Storage 地址"},{default:i(()=>[l(o(S),{value:d.value.arex_storage_url,"onUpdate:value":e[16]||(e[16]=r=>d.value.arex_storage_url=r),placeholder:"留空则使用全局配置"},null,8,["value"])]),_:1}),l(o(w),{label:"采样率"},{default:i(()=>[l(o(Qa),{value:d.value.sample_rate,"onUpdate:value":e[17]||(e[17]=r=>d.value.sample_rate=r),min:0,max:1,step:.1,style:{width:"200px"}},null,8,["value"]),l(o(Pe),{style:{"margin-left":"12px"}},{default:i(()=>[b(ae(d.value.sample_rate),1)]),_:1})]),_:1}),l(o(w),{label:"交易码映射"},{default:i(()=>[l(o(G),{vertical:"",style:{width:"100%"}},{default:i(()=>[l(o(te),{type:"info","show-icon":!1},{default:i(()=>[...e[27]||(e[27]=[b(" 以 JSON 数组配置，每个交易码一组规则。平台会在回放前自动按交易码加载对应映射。 推荐按 ",-1),_("code",null,"transaction_code",-1),b(" 一条一组填写。字段路径使用点号，例如 ",-1),_("code",null,"name",-1),b("、",-1),_("code",null,"customer.name",-1),b("、",-1),_("code",null,"items.0.name",-1),b("、",-1),_("code",null,"*.name",-1),b("。 ",-1)])]),_:1}),l(o(te),{type:"warning","show-icon":!1},{default:i(()=>[...e[28]||(e[28]=[b(" 规则类型目前支持 ",-1),_("code",null,"rename",-1),b("（改名）、",-1),_("code",null,"delete",-1),b("（删除）、",-1),_("code",null,"default",-1),b("（补默认值）、",-1),_("code",null,"set",-1),b("（强制赋值）、",-1),_("code",null,"copy",-1),b("（复制到新字段）。 推荐先参考 ",-1),_("code",null,"docs/交易码映射模板.md",-1),b(" 再填写。 ",-1)])]),_:1}),l(o(S),{value:d.value.transaction_mappings,"onUpdate:value":e[18]||(e[18]=r=>d.value.transaction_mappings=r),type:"textarea",autosize:{minRows:6,maxRows:14},placeholder:`[
  {
    "transaction_code": "A0201M14I",
    "enabled": true,
    "description": "开户字段映射",
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
    "transaction_code": "A0201D008",
    "enabled": true,
    "description": "支用字段映射",
    "request_rules": [
      { "type": "rename", "source": "amount", "target": "loan_amount" }
    ],
    "response_rules": []
  }
]`},null,8,["value"])]),_:1})]),_:1})]),_:1},8,["model"])]),_:1},8,["show","title"])],64))}}),Rt=Xa(tt,[["__scopeId","data-v-30bcf404"]]);export{Rt as default};
