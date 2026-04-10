import{a as $}from"./applications-Bw8RHhhg.js";import{u as la,N as ra,a as R}from"./FormItem-Bu_b7pEg.js";import{a as sa,o as X,g as r,i as _,n as te,a5 as Se,a6 as ia,a7 as da,a8 as ua,d as Me,h as p,a9 as ca,aa as va,u as ha,j as De,ab as fa,r as k,Z as _e,$ as ma,l as Ce,ac as pa,m as D,t as oe,ad as ne,ae as le,a1 as fe,v as ba,_ as ga,M as wa,K as i,I as m,J as d,af as xa,F as ya,P as K,Q as N,O as ka,W as Sa}from"./index-DNXRX2vX.js";import{N as _a}from"./headers-DUENlote.js";import{N as B}from"./index-Dg7fYjcV.js";import{N as Re}from"./InputNumber-DjeLQYCv.js";import{B as Ca,e as Ra,f as za,g as me,b as re}from"./Space-yGN031He.js";import{u as Ta}from"./get-h59NEGKw.js";import{N as Ma}from"./Popconfirm-BchWzOG_.js";import{b as Da,c as Va}from"./index-DTEWPgGI.js";import{N as Ba}from"./text-bTMGGu_L.js";import"./light-q7xaMC5L.js";const Ha={railHeight:"4px",railWidthVertical:"4px",handleSize:"18px",dotHeight:"8px",dotWidth:"8px",dotBorderRadius:"4px"};function Na(n){const l="rgba(0, 0, 0, .85)",z="0 2px 8px 0 rgba(0, 0, 0, 0.12)",{railColor:g,primaryColor:h,baseColor:b,cardColor:C,modalColor:V,popoverColor:u,borderRadius:P,fontSize:I,opacityDisabled:T}=n;return Object.assign(Object.assign({},Ha),{fontSize:I,markFontSize:I,railColor:g,railColorHover:g,fillColor:h,fillColorHover:h,opacityDisabled:T,handleColor:"#FFF",dotColor:C,dotColorModal:V,dotColorPopover:u,handleBoxShadow:"0 1px 4px 0 rgba(0, 0, 0, 0.3), inset 0 0 1px 0 rgba(0, 0, 0, 0.05)",handleBoxShadowHover:"0 1px 4px 0 rgba(0, 0, 0, 0.3), inset 0 0 1px 0 rgba(0, 0, 0, 0.05)",handleBoxShadowActive:"0 1px 4px 0 rgba(0, 0, 0, 0.3), inset 0 0 1px 0 rgba(0, 0, 0, 0.05)",handleBoxShadowFocus:"0 1px 4px 0 rgba(0, 0, 0, 0.3), inset 0 0 1px 0 rgba(0, 0, 0, 0.05)",indicatorColor:l,indicatorBoxShadow:z,indicatorTextColor:b,indicatorBorderRadius:P,dotBorder:`2px solid ${g}`,dotBorderActive:`2px solid ${h}`,dotBoxShadow:""})}const Aa={common:sa,self:Na},Fa=X([r("slider",`
 display: block;
 padding: calc((var(--n-handle-size) - var(--n-rail-height)) / 2) 0;
 position: relative;
 z-index: 0;
 width: 100%;
 cursor: pointer;
 user-select: none;
 -webkit-user-select: none;
 `,[_("reverse",[r("slider-handles",[r("slider-handle-wrapper",`
 transform: translate(50%, -50%);
 `)]),r("slider-dots",[r("slider-dot",`
 transform: translateX(50%, -50%);
 `)]),_("vertical",[r("slider-handles",[r("slider-handle-wrapper",`
 transform: translate(-50%, -50%);
 `)]),r("slider-marks",[r("slider-mark",`
 transform: translateY(calc(-50% + var(--n-dot-height) / 2));
 `)]),r("slider-dots",[r("slider-dot",`
 transform: translateX(-50%) translateY(0);
 `)])])]),_("vertical",`
 box-sizing: content-box;
 padding: 0 calc((var(--n-handle-size) - var(--n-rail-height)) / 2);
 width: var(--n-rail-width-vertical);
 height: 100%;
 `,[r("slider-handles",`
 top: calc(var(--n-handle-size) / 2);
 right: 0;
 bottom: calc(var(--n-handle-size) / 2);
 left: 0;
 `,[r("slider-handle-wrapper",`
 top: unset;
 left: 50%;
 transform: translate(-50%, 50%);
 `)]),r("slider-rail",`
 height: 100%;
 `,[te("fill",`
 top: unset;
 right: 0;
 bottom: unset;
 left: 0;
 `)]),_("with-mark",`
 width: var(--n-rail-width-vertical);
 margin: 0 32px 0 8px;
 `),r("slider-marks",`
 top: calc(var(--n-handle-size) / 2);
 right: unset;
 bottom: calc(var(--n-handle-size) / 2);
 left: 22px;
 font-size: var(--n-mark-font-size);
 `,[r("slider-mark",`
 transform: translateY(50%);
 white-space: nowrap;
 `)]),r("slider-dots",`
 top: calc(var(--n-handle-size) / 2);
 right: unset;
 bottom: calc(var(--n-handle-size) / 2);
 left: 50%;
 `,[r("slider-dot",`
 transform: translateX(-50%) translateY(50%);
 `)])]),_("disabled",`
 cursor: not-allowed;
 opacity: var(--n-opacity-disabled);
 `,[r("slider-handle",`
 cursor: not-allowed;
 `)]),_("with-mark",`
 width: 100%;
 margin: 8px 0 32px 0;
 `),X("&:hover",[r("slider-rail",{backgroundColor:"var(--n-rail-color-hover)"},[te("fill",{backgroundColor:"var(--n-fill-color-hover)"})]),r("slider-handle",{boxShadow:"var(--n-handle-box-shadow-hover)"})]),_("active",[r("slider-rail",{backgroundColor:"var(--n-rail-color-hover)"},[te("fill",{backgroundColor:"var(--n-fill-color-hover)"})]),r("slider-handle",{boxShadow:"var(--n-handle-box-shadow-hover)"})]),r("slider-marks",`
 position: absolute;
 top: 18px;
 left: calc(var(--n-handle-size) / 2);
 right: calc(var(--n-handle-size) / 2);
 `,[r("slider-mark",`
 position: absolute;
 transform: translateX(-50%);
 white-space: nowrap;
 `)]),r("slider-rail",`
 width: 100%;
 position: relative;
 height: var(--n-rail-height);
 background-color: var(--n-rail-color);
 transition: background-color .3s var(--n-bezier);
 border-radius: calc(var(--n-rail-height) / 2);
 `,[te("fill",`
 position: absolute;
 top: 0;
 bottom: 0;
 border-radius: calc(var(--n-rail-height) / 2);
 transition: background-color .3s var(--n-bezier);
 background-color: var(--n-fill-color);
 `)]),r("slider-handles",`
 position: absolute;
 top: 0;
 right: calc(var(--n-handle-size) / 2);
 bottom: 0;
 left: calc(var(--n-handle-size) / 2);
 `,[r("slider-handle-wrapper",`
 outline: none;
 position: absolute;
 top: 50%;
 transform: translate(-50%, -50%);
 cursor: pointer;
 display: flex;
 `,[r("slider-handle",`
 height: var(--n-handle-size);
 width: var(--n-handle-size);
 border-radius: 50%;
 overflow: hidden;
 transition: box-shadow .2s var(--n-bezier), background-color .3s var(--n-bezier);
 background-color: var(--n-handle-color);
 box-shadow: var(--n-handle-box-shadow);
 `,[X("&:hover",`
 box-shadow: var(--n-handle-box-shadow-hover);
 `)]),X("&:focus",[r("slider-handle",`
 box-shadow: var(--n-handle-box-shadow-focus);
 `,[X("&:hover",`
 box-shadow: var(--n-handle-box-shadow-active);
 `)])])])]),r("slider-dots",`
 position: absolute;
 top: 50%;
 left: calc(var(--n-handle-size) / 2);
 right: calc(var(--n-handle-size) / 2);
 `,[_("transition-disabled",[r("slider-dot","transition: none;")]),r("slider-dot",`
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
 `,[_("active","border: var(--n-dot-border-active);")])])]),r("slider-handle-indicator",`
 font-size: var(--n-font-size);
 padding: 6px 10px;
 border-radius: var(--n-indicator-border-radius);
 color: var(--n-indicator-text-color);
 background-color: var(--n-indicator-color);
 box-shadow: var(--n-indicator-box-shadow);
 `,[Se()]),r("slider-handle-indicator",`
 font-size: var(--n-font-size);
 padding: 6px 10px;
 border-radius: var(--n-indicator-border-radius);
 color: var(--n-indicator-text-color);
 background-color: var(--n-indicator-color);
 box-shadow: var(--n-indicator-box-shadow);
 `,[_("top",`
 margin-bottom: 12px;
 `),_("right",`
 margin-left: 12px;
 `),_("bottom",`
 margin-top: 12px;
 `),_("left",`
 margin-right: 12px;
 `),Se()]),ia(r("slider",[r("slider-dot","background-color: var(--n-dot-color-modal);")])),da(r("slider",[r("slider-dot","background-color: var(--n-dot-color-popover);")]))]);function ze(n){return window.TouchEvent&&n instanceof window.TouchEvent}function Te(){const n=new Map,l=z=>g=>{n.set(z,g)};return ua(()=>{n.clear()}),[n,l]}const $a=0,Ia=Object.assign(Object.assign({},De.props),{to:me.propTo,defaultValue:{type:[Number,Array],default:0},marks:Object,disabled:{type:Boolean,default:void 0},formatTooltip:Function,keyboard:{type:Boolean,default:!0},min:{type:Number,default:0},max:{type:Number,default:100},step:{type:[Number,String],default:1},range:Boolean,value:[Number,Array],placement:String,showTooltip:{type:Boolean,default:void 0},tooltip:{type:Boolean,default:!0},vertical:Boolean,reverse:Boolean,"onUpdate:value":[Function,Array],onUpdateValue:[Function,Array],onDragstart:[Function],onDragend:[Function]}),Ua=Me({name:"Slider",props:Ia,slots:Object,setup(n){const{mergedClsPrefixRef:l,namespaceRef:z,inlineThemeDisabled:g}=ha(n),h=De("Slider","-slider",Fa,Aa,n,l),b=k(null),[C,V]=Te(),[u,P]=Te(),I=k(new Set),T=fa(n),{mergedDisabledRef:U}=T,W=D(()=>{const{step:e}=n;if(Number(e)<=0||e==="mark")return 0;const a=e.toString();let t=0;return a.includes(".")&&(t=a.length-a.indexOf(".")-1),t}),O=k(n.defaultValue),se=ba(n,"value"),L=Ta(se,O),S=D(()=>{const{value:e}=L;return(n.range?e:[e]).map(we)}),Y=D(()=>S.value.length>2),ie=D(()=>n.placement===void 0?n.vertical?"right":"top":n.placement),c=D(()=>{const{marks:e}=n;return e?Object.keys(e).map(Number.parseFloat):null}),o=k(-1),v=k(-1),A=k(-1),F=k(!1),q=k(!1),de=D(()=>{const{vertical:e,reverse:a}=n;return e?a?"top":"bottom":a?"right":"left"}),Ve=D(()=>{if(Y.value)return;const e=S.value,a=J(n.range?Math.min(...e):n.min),t=J(n.range?Math.max(...e):e[0]),{value:s}=de;return n.vertical?{[s]:`${a}%`,height:`${t-a}%`}:{[s]:`${a}%`,width:`${t-a}%`}}),Be=D(()=>{const e=[],{marks:a}=n;if(a){const t=S.value.slice();t.sort((y,x)=>y-x);const{value:s}=de,{value:f}=Y,{range:w}=n,M=f?()=>!1:y=>w?y>=t[0]&&y<=t[t.length-1]:y<=t[0];for(const y of Object.keys(a)){const x=Number(y);e.push({active:M(x),key:x,label:a[y],style:{[s]:`${J(x)}%`}})}}return e});function He(e,a){const t=J(e),{value:s}=de;return{[s]:`${t}%`,zIndex:a===o.value?1:0}}function pe(e){return n.showTooltip||A.value===e||o.value===e&&F.value}function Ne(e){return F.value?!(o.value===e&&v.value===e):!0}function Ae(e){var a;~e&&(o.value=e,(a=C.get(e))===null||a===void 0||a.focus())}function Fe(){u.forEach((e,a)=>{pe(a)&&e.syncPosition()})}function be(e){const{"onUpdate:value":a,onUpdateValue:t}=n,{nTriggerFormInput:s,nTriggerFormChange:f}=T;t&&oe(t,e),a&&oe(a,e),O.value=e,s(),f()}function ge(e){const{range:a}=n;if(a){if(Array.isArray(e)){const{value:t}=S;e.join()!==t.join()&&be(e)}}else Array.isArray(e)||S.value[0]!==e&&be(e)}function ue(e,a){if(n.range){const t=S.value.slice();t.splice(a,1,e),ge(t)}else ge(e)}function ce(e,a,t){const s=t!==void 0;t||(t=e-a>0?1:-1);const f=c.value||[],{step:w}=n;if(w==="mark"){const x=Q(e,f.concat(a),s?t:void 0);return x?x.value:a}if(w<=0)return a;const{value:M}=W;let y;if(s){const x=Number((a/w).toFixed(M)),H=Math.floor(x),ve=x>H?H:H-1,he=x<H?H:H+1;y=Q(a,[Number((ve*w).toFixed(M)),Number((he*w).toFixed(M)),...f],t)}else{const x=Ie(e);y=Q(e,[...f,x])}return y?we(y.value):a}function we(e){return Math.min(n.max,Math.max(n.min,e))}function J(e){const{max:a,min:t}=n;return(e-t)/(a-t)*100}function $e(e){const{max:a,min:t}=n;return t+(a-t)*e}function Ie(e){const{step:a,min:t}=n;if(Number(a)<=0||a==="mark")return e;const s=Math.round((e-t)/a)*a+t;return Number(s.toFixed(W.value))}function Q(e,a=c.value,t){if(!(a!=null&&a.length))return null;let s=null,f=-1;for(;++f<a.length;){const w=a[f]-e,M=Math.abs(w);(t===void 0||w*t>0)&&(s===null||M<s.distance)&&(s={index:f,distance:M,value:a[f]})}return s}function xe(e){const a=b.value;if(!a)return;const t=ze(e)?e.touches[0]:e,s=a.getBoundingClientRect();let f;return n.vertical?f=(s.bottom-t.clientY)/s.height:f=(t.clientX-s.left)/s.width,n.reverse&&(f=1-f),$e(f)}function Ue(e){if(U.value||!n.keyboard)return;const{vertical:a,reverse:t}=n;switch(e.key){case"ArrowUp":e.preventDefault(),Z(a&&t?-1:1);break;case"ArrowRight":e.preventDefault(),Z(!a&&t?-1:1);break;case"ArrowDown":e.preventDefault(),Z(a&&t?1:-1);break;case"ArrowLeft":e.preventDefault(),Z(!a&&t?1:-1);break}}function Z(e){const a=o.value;if(a===-1)return;const{step:t}=n,s=S.value[a],f=Number(t)<=0||t==="mark"?s:s+t*e;ue(ce(f,s,e>0?1:-1),a)}function je(e){var a,t;if(U.value||!ze(e)&&e.button!==$a)return;const s=xe(e);if(s===void 0)return;const f=S.value.slice(),w=n.range?(t=(a=Q(s,f))===null||a===void 0?void 0:a.index)!==null&&t!==void 0?t:-1:0;w!==-1&&(e.preventDefault(),Ae(w),Ee(),ue(ce(s,S.value[w]),w))}function Ee(){F.value||(F.value=!0,n.onDragstart&&oe(n.onDragstart),ne("touchend",document,ae),ne("mouseup",document,ae),ne("touchmove",document,ee),ne("mousemove",document,ee))}function G(){F.value&&(F.value=!1,n.onDragend&&oe(n.onDragend),le("touchend",document,ae),le("mouseup",document,ae),le("touchmove",document,ee),le("mousemove",document,ee))}function ee(e){const{value:a}=o;if(!F.value||a===-1){G();return}const t=xe(e);t!==void 0&&ue(ce(t,S.value[a]),a)}function ae(){G()}function Pe(e){o.value=e,U.value||(A.value=e)}function Oe(e){o.value===e&&(o.value=-1,G()),A.value===e&&(A.value=-1)}function Le(e){A.value=e}function Xe(e){A.value===e&&(A.value=-1)}_e(o,(e,a)=>void fe(()=>v.value=a)),_e(L,()=>{if(n.marks){if(q.value)return;q.value=!0,fe(()=>{q.value=!1})}fe(Fe)}),ma(()=>{G()});const ye=D(()=>{const{self:{markFontSize:e,railColor:a,railColorHover:t,fillColor:s,fillColorHover:f,handleColor:w,opacityDisabled:M,dotColor:y,dotColorModal:x,handleBoxShadow:H,handleBoxShadowHover:ve,handleBoxShadowActive:he,handleBoxShadowFocus:Ke,dotBorder:We,dotBoxShadow:Ye,railHeight:qe,railWidthVertical:Je,handleSize:Qe,dotHeight:Ze,dotWidth:Ge,dotBorderRadius:ea,fontSize:aa,dotBorderActive:ta,dotColorPopover:oa},common:{cubicBezierEaseInOut:na}}=h.value;return{"--n-bezier":na,"--n-dot-border":We,"--n-dot-border-active":ta,"--n-dot-border-radius":ea,"--n-dot-box-shadow":Ye,"--n-dot-color":y,"--n-dot-color-modal":x,"--n-dot-color-popover":oa,"--n-dot-height":Ze,"--n-dot-width":Ge,"--n-fill-color":s,"--n-fill-color-hover":f,"--n-font-size":aa,"--n-handle-box-shadow":H,"--n-handle-box-shadow-active":he,"--n-handle-box-shadow-focus":Ke,"--n-handle-box-shadow-hover":ve,"--n-handle-color":w,"--n-handle-size":Qe,"--n-opacity-disabled":M,"--n-rail-color":a,"--n-rail-color-hover":t,"--n-rail-height":qe,"--n-rail-width-vertical":Je,"--n-mark-font-size":e}}),j=g?Ce("slider",void 0,ye,n):void 0,ke=D(()=>{const{self:{fontSize:e,indicatorColor:a,indicatorBoxShadow:t,indicatorTextColor:s,indicatorBorderRadius:f}}=h.value;return{"--n-font-size":e,"--n-indicator-border-radius":f,"--n-indicator-box-shadow":t,"--n-indicator-color":a,"--n-indicator-text-color":s}}),E=g?Ce("slider-indicator",void 0,ke,n):void 0;return{mergedClsPrefix:l,namespace:z,uncontrolledValue:O,mergedValue:L,mergedDisabled:U,mergedPlacement:ie,isMounted:pa(),adjustedTo:me(n),dotTransitionDisabled:q,markInfos:Be,isShowTooltip:pe,shouldKeepTooltipTransition:Ne,handleRailRef:b,setHandleRefs:V,setFollowerRefs:P,fillStyle:Ve,getHandleStyle:He,activeIndex:o,arrifiedValues:S,followerEnabledIndexSet:I,handleRailMouseDown:je,handleHandleFocus:Pe,handleHandleBlur:Oe,handleHandleMouseEnter:Le,handleHandleMouseLeave:Xe,handleRailKeyDown:Ue,indicatorCssVars:g?void 0:ke,indicatorThemeClass:E==null?void 0:E.themeClass,indicatorOnRender:E==null?void 0:E.onRender,cssVars:g?void 0:ye,themeClass:j==null?void 0:j.themeClass,onRender:j==null?void 0:j.onRender}},render(){var n;const{mergedClsPrefix:l,themeClass:z,formatTooltip:g}=this;return(n=this.onRender)===null||n===void 0||n.call(this),p("div",{class:[`${l}-slider`,z,{[`${l}-slider--disabled`]:this.mergedDisabled,[`${l}-slider--active`]:this.activeIndex!==-1,[`${l}-slider--with-mark`]:this.marks,[`${l}-slider--vertical`]:this.vertical,[`${l}-slider--reverse`]:this.reverse}],style:this.cssVars,onKeydown:this.handleRailKeyDown,onMousedown:this.handleRailMouseDown,onTouchstart:this.handleRailMouseDown},p("div",{class:`${l}-slider-rail`},p("div",{class:`${l}-slider-rail__fill`,style:this.fillStyle}),this.marks?p("div",{class:[`${l}-slider-dots`,this.dotTransitionDisabled&&`${l}-slider-dots--transition-disabled`]},this.markInfos.map(h=>p("div",{key:h.key,class:[`${l}-slider-dot`,{[`${l}-slider-dot--active`]:h.active}],style:h.style}))):null,p("div",{ref:"handleRailRef",class:`${l}-slider-handles`},this.arrifiedValues.map((h,b)=>{const C=this.isShowTooltip(b);return p(Ca,null,{default:()=>[p(Ra,null,{default:()=>p("div",{ref:this.setHandleRefs(b),class:`${l}-slider-handle-wrapper`,tabindex:this.mergedDisabled?-1:0,role:"slider","aria-valuenow":h,"aria-valuemin":this.min,"aria-valuemax":this.max,"aria-orientation":this.vertical?"vertical":"horizontal","aria-disabled":this.disabled,style:this.getHandleStyle(h,b),onFocus:()=>{this.handleHandleFocus(b)},onBlur:()=>{this.handleHandleBlur(b)},onMouseenter:()=>{this.handleHandleMouseEnter(b)},onMouseleave:()=>{this.handleHandleMouseLeave(b)}},ca(this.$slots.thumb,()=>[p("div",{class:`${l}-slider-handle`})]))}),this.tooltip&&p(za,{ref:this.setFollowerRefs(b),show:C,to:this.adjustedTo,enabled:this.showTooltip&&!this.range||this.followerEnabledIndexSet.has(b),teleportDisabled:this.adjustedTo===me.tdkey,placement:this.mergedPlacement,containerClass:this.namespace},{default:()=>p(va,{name:"fade-in-scale-up-transition",appear:this.isMounted,css:this.shouldKeepTooltipTransition(b),onEnter:()=>{this.followerEnabledIndexSet.add(b)},onAfterLeave:()=>{this.followerEnabledIndexSet.delete(b)}},{default:()=>{var V;return C?((V=this.indicatorOnRender)===null||V===void 0||V.call(this),p("div",{class:[`${l}-slider-handle-indicator`,this.indicatorThemeClass,`${l}-slider-handle-indicator--${this.mergedPlacement}`],style:this.indicatorCssVars},typeof g=="function"?g(h):h)):null}})})]})})),this.marks?p("div",{class:`${l}-slider-marks`},this.markInfos.map(h=>p("div",{key:h.key,class:`${l}-slider-mark`,style:h.style},typeof h.label=="function"?h.label():h.label))):null))}}),Za=Me({__name:"index",setup(n){const l=la(),z=k([]),g=k(!1),h=k(!1),b=k(!1),C=k(null),V=k(),u=k({name:"",description:"",ssh_host:"",ssh_user:"",ssh_port:22,ssh_key_path:"",ssh_password:"",service_port:8080,jvm_process_name:"",arex_app_id:"",arex_storage_url:"",sample_rate:1}),P={online:"success",offline:"error",mounting:"warning",unknown:"default"},I=[{title:"名称",key:"name"},{title:"SSH主机",key:"ssh_host"},{title:"服务端口",key:"service_port",width:90},{title:"Agent状态",key:"agent_status",width:110,render:c=>p(Va,{type:P[c.agent_status]||"default",size:"small"},()=>c.agent_status||"unknown")},{title:"创建时间",key:"created_at",width:160,render:c=>{var o;return(o=c.created_at)==null?void 0:o.slice(0,19).replace("T"," ")}},{title:"操作",key:"actions",render:c=>p(re,{size:4},()=>[p(N,{size:"tiny",onClick:()=>L(c.id)},()=>"连接测试"),c.agent_status==="online"?p(N,{size:"tiny",type:"warning",onClick:()=>Y(c.id)},()=>"卸载Agent"):p(N,{size:"tiny",type:"info",onClick:()=>S(c.id)},()=>"挂载Agent"),p(N,{size:"tiny",onClick:()=>O(c)},()=>"编辑"),p(Ma,{onPositiveClick:()=>ie(c.id)},{default:()=>"确认删除?",trigger:()=>p(N,{size:"tiny",type:"error"},()=>"删除")})])}];async function T(){g.value=!0;try{const c=await $.list();z.value=c.data}catch{l.error("加载应用列表失败")}finally{g.value=!1}}function U(){u.value={name:"",description:"",ssh_host:"",ssh_user:"",ssh_port:22,ssh_key_path:"",ssh_password:"",service_port:8080,jvm_process_name:"",arex_app_id:"",arex_storage_url:"",sample_rate:1}}function W(){C.value=null,U(),h.value=!0}function O(c){C.value=c.id,Object.assign(u.value,c),h.value=!0}async function se(){var c,o;b.value=!0;try{C.value?await $.update(C.value,u.value):await $.create(u.value),l.success("保存成功"),h.value=!1,await T()}catch(v){l.error(((o=(c=v.response)==null?void 0:c.data)==null?void 0:o.detail)||"保存失败")}finally{b.value=!1}}async function L(c){try{const o=await $.testConnection(c);o.data.success?l.success("SSH 连接成功"):l.error("连接失败: "+o.data.message)}catch{l.error("连接测试失败")}}async function S(c){try{await $.mountAgent(c),l.info("Agent 挂载已启动，请稍候..."),setTimeout(T,3e3)}catch{l.error("挂载失败")}}async function Y(c){try{await $.unmountAgent(c),l.success("Agent 已卸载"),await T()}catch{l.error("卸载失败")}}async function ie(c){try{await $.delete(c),l.success("删除成功"),await T()}catch{l.error("删除失败")}}return ga(T),(c,o)=>(Sa(),wa(ya,null,[i(d(re),{vertical:"",size:12},{default:m(()=>[i(d(re),{justify:"space-between"},{default:m(()=>[i(d(_a),{style:{margin:"0"}},{default:m(()=>[...o[14]||(o[14]=[K("应用管理",-1)])]),_:1}),i(d(N),{type:"primary",onClick:W},{default:m(()=>[...o[15]||(o[15]=[K("+ 新增应用",-1)])]),_:1})]),_:1}),i(d(Da),{columns:I,data:z.value,loading:g.value,pagination:{pageSize:10}},null,8,["data","loading"])]),_:1}),i(d(xa),{show:h.value,"onUpdate:show":o[13]||(o[13]=v=>h.value=v),title:C.value?"编辑应用":"新增应用",preset:"card",style:{width:"600px"}},{footer:m(()=>[i(d(re),{justify:"end"},{default:m(()=>[i(d(N),{onClick:o[12]||(o[12]=v=>h.value=!1)},{default:m(()=>[...o[16]||(o[16]=[K("取消",-1)])]),_:1}),i(d(N),{type:"primary",loading:b.value,onClick:se},{default:m(()=>[...o[17]||(o[17]=[K("保存",-1)])]),_:1},8,["loading"])]),_:1})]),default:m(()=>[i(d(ra),{ref_key:"formRef",ref:V,model:u.value,"label-placement":"left","label-width":"120px"},{default:m(()=>[i(d(R),{label:"应用名称",path:"name",rule:{required:!0,message:"请输入应用名称"}},{default:m(()=>[i(d(B),{value:u.value.name,"onUpdate:value":o[0]||(o[0]=v=>u.value.name=v),placeholder:"如: demo-service"},null,8,["value"])]),_:1}),i(d(R),{label:"描述"},{default:m(()=>[i(d(B),{value:u.value.description,"onUpdate:value":o[1]||(o[1]=v=>u.value.description=v),placeholder:"可选"},null,8,["value"])]),_:1}),i(d(R),{label:"SSH 主机",path:"ssh_host",rule:{required:!0,message:"请输入SSH主机"}},{default:m(()=>[i(d(B),{value:u.value.ssh_host,"onUpdate:value":o[2]||(o[2]=v=>u.value.ssh_host=v),placeholder:"IP或域名"},null,8,["value"])]),_:1}),i(d(R),{label:"SSH 用户",path:"ssh_user",rule:{required:!0,message:"请输入SSH用户"}},{default:m(()=>[i(d(B),{value:u.value.ssh_user,"onUpdate:value":o[3]||(o[3]=v=>u.value.ssh_user=v),placeholder:"如: ubuntu"},null,8,["value"])]),_:1}),i(d(R),{label:"SSH 端口"},{default:m(()=>[i(d(Re),{value:u.value.ssh_port,"onUpdate:value":o[4]||(o[4]=v=>u.value.ssh_port=v)},null,8,["value"])]),_:1}),i(d(R),{label:"SSH 密钥路径"},{default:m(()=>[i(d(B),{value:u.value.ssh_key_path,"onUpdate:value":o[5]||(o[5]=v=>u.value.ssh_key_path=v),placeholder:"/path/to/key"},null,8,["value"])]),_:1}),i(d(R),{label:"SSH 密码"},{default:m(()=>[i(d(B),{value:u.value.ssh_password,"onUpdate:value":o[6]||(o[6]=v=>u.value.ssh_password=v),type:"password"},null,8,["value"])]),_:1}),i(d(R),{label:"服务端口"},{default:m(()=>[i(d(Re),{value:u.value.service_port,"onUpdate:value":o[7]||(o[7]=v=>u.value.service_port=v)},null,8,["value"])]),_:1}),i(d(R),{label:"JVM 进程名"},{default:m(()=>[i(d(B),{value:u.value.jvm_process_name,"onUpdate:value":o[8]||(o[8]=v=>u.value.jvm_process_name=v),placeholder:"用于 pgrep 识别"},null,8,["value"])]),_:1}),i(d(R),{label:"AREX App ID"},{default:m(()=>[i(d(B),{value:u.value.arex_app_id,"onUpdate:value":o[9]||(o[9]=v=>u.value.arex_app_id=v)},null,8,["value"])]),_:1}),i(d(R),{label:"AREX Storage URL"},{default:m(()=>[i(d(B),{value:u.value.arex_storage_url,"onUpdate:value":o[10]||(o[10]=v=>u.value.arex_storage_url=v),placeholder:"留空使用全局配置"},null,8,["value"])]),_:1}),i(d(R),{label:"采样率"},{default:m(()=>[i(d(Ua),{value:u.value.sample_rate,"onUpdate:value":o[11]||(o[11]=v=>u.value.sample_rate=v),min:0,max:1,step:.1,style:{width:"200px"}},null,8,["value"]),i(d(Ba),{style:{"margin-left":"12px"}},{default:m(()=>[K(ka(u.value.sample_rate),1)]),_:1})]),_:1})]),_:1},8,["model"])]),_:1},8,["show","title"])],64))}});export{Za as default};
