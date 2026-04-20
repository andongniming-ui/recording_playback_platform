import{d as O,h as s,c as Te,s as oo,a as Ne,b as ze,e as le,f as Q,g as u,i as S,S as ke,u as pe,j as q,k as _e,l as fe,m as C,r as E,p as Y,n as d,o as w,N as Be,q as V,t as F,v as ne,w as J,x as to,y as G,z as ge,A as ue,F as ro,B as ae,C as no,V as io,D as we,E as lo,G as ao,H as Se,I as U,J as L,K as _,L as W,M as Ae,O as se,P as oe,Q as so,R as co,T as uo,U as vo,W as mo,X as te}from"./index-CEK4JRfn.js";import{u as ho}from"./user-Ct9mpNPC.js";import{t as po,N as fo}from"./Tooltip-B1DHO6tQ.js";import{d as go,N as bo}from"./Dropdown-DGgAQ_-i.js";import{f as ce,u as ve}from"./get-BRmAhlo2.js";import{C as Co,V as xo,u as yo,c as de,N as Io}from"./Space-C0zHjG0z.js";import{_ as zo}from"./_plugin-vue_export-helper-DlAUqK2U.js";const wo=O({name:"ChevronDownFilled",render(){return s("svg",{viewBox:"0 0 16 16",fill:"none",xmlns:"http://www.w3.org/2000/svg"},s("path",{d:"M3.20041 5.73966C3.48226 5.43613 3.95681 5.41856 4.26034 5.70041L8 9.22652L11.7397 5.70041C12.0432 5.41856 12.5177 5.43613 12.7996 5.73966C13.0815 6.0432 13.0639 6.51775 12.7603 6.7996L8.51034 10.7996C8.22258 11.0668 7.77743 11.0668 7.48967 10.7996L3.23966 6.7996C2.93613 6.51775 2.91856 6.0432 3.20041 5.73966Z",fill:"currentColor"}))}});function So(e){const{baseColor:t,textColor2:o,bodyColor:n,cardColor:c,dividerColor:a,actionColor:h,scrollbarColor:b,scrollbarColorHover:v,invertedColor:f}=e;return{textColor:o,textColorInverted:"#FFF",color:n,colorEmbedded:h,headerColor:c,headerColorInverted:f,footerColor:h,footerColorInverted:f,headerBorderColor:a,headerBorderColorInverted:f,footerBorderColor:a,footerBorderColorInverted:f,siderBorderColor:a,siderBorderColorInverted:f,siderColor:c,siderColorInverted:f,siderToggleButtonBorder:`1px solid ${a}`,siderToggleButtonColor:t,siderToggleButtonIconColor:o,siderToggleButtonIconColorInverted:o,siderToggleBarColor:ze(n,b),siderToggleBarColorHover:ze(n,v),__invertScrollbar:"true"}}const Ee=Te({name:"Layout",common:Ne,peers:{Scrollbar:oo},self:So});function Ao(e,t,o,n){return{itemColorHoverInverted:"#0000",itemColorActiveInverted:t,itemColorActiveHoverInverted:t,itemColorActiveCollapsedInverted:t,itemTextColorInverted:e,itemTextColorHoverInverted:o,itemTextColorChildActiveInverted:o,itemTextColorChildActiveHoverInverted:o,itemTextColorActiveInverted:o,itemTextColorActiveHoverInverted:o,itemTextColorHorizontalInverted:e,itemTextColorHoverHorizontalInverted:o,itemTextColorChildActiveHorizontalInverted:o,itemTextColorChildActiveHoverHorizontalInverted:o,itemTextColorActiveHorizontalInverted:o,itemTextColorActiveHoverHorizontalInverted:o,itemIconColorInverted:e,itemIconColorHoverInverted:o,itemIconColorActiveInverted:o,itemIconColorActiveHoverInverted:o,itemIconColorChildActiveInverted:o,itemIconColorChildActiveHoverInverted:o,itemIconColorCollapsedInverted:e,itemIconColorHorizontalInverted:e,itemIconColorHoverHorizontalInverted:o,itemIconColorActiveHorizontalInverted:o,itemIconColorActiveHoverHorizontalInverted:o,itemIconColorChildActiveHorizontalInverted:o,itemIconColorChildActiveHoverHorizontalInverted:o,arrowColorInverted:e,arrowColorHoverInverted:o,arrowColorActiveInverted:o,arrowColorActiveHoverInverted:o,arrowColorChildActiveInverted:o,arrowColorChildActiveHoverInverted:o,groupTextColorInverted:n}}function Ho(e){const{borderRadius:t,textColor3:o,primaryColor:n,textColor2:c,textColor1:a,fontSize:h,dividerColor:b,hoverColor:v,primaryColorHover:f}=e;return Object.assign({borderRadius:t,color:"#0000",groupTextColor:o,itemColorHover:v,itemColorActive:le(n,{alpha:.1}),itemColorActiveHover:le(n,{alpha:.1}),itemColorActiveCollapsed:le(n,{alpha:.1}),itemTextColor:c,itemTextColorHover:c,itemTextColorActive:n,itemTextColorActiveHover:n,itemTextColorChildActive:n,itemTextColorChildActiveHover:n,itemTextColorHorizontal:c,itemTextColorHoverHorizontal:f,itemTextColorActiveHorizontal:n,itemTextColorActiveHoverHorizontal:n,itemTextColorChildActiveHorizontal:n,itemTextColorChildActiveHoverHorizontal:n,itemIconColor:a,itemIconColorHover:a,itemIconColorActive:n,itemIconColorActiveHover:n,itemIconColorChildActive:n,itemIconColorChildActiveHover:n,itemIconColorCollapsed:a,itemIconColorHorizontal:a,itemIconColorHoverHorizontal:f,itemIconColorActiveHorizontal:n,itemIconColorActiveHoverHorizontal:n,itemIconColorChildActiveHorizontal:n,itemIconColorChildActiveHoverHorizontal:n,itemHeight:"42px",arrowColor:c,arrowColorHover:c,arrowColorActive:n,arrowColorActiveHover:n,arrowColorChildActive:n,arrowColorChildActiveHover:n,colorInverted:"#0000",borderColorHorizontal:"#0000",fontSize:h,dividerColor:b},Ao("#BBB",n,"#FFF","#AAA"))}const Ro=Te({name:"Menu",common:Ne,peers:{Tooltip:po,Dropdown:go},self:Ho}),Oe=Q("n-layout-sider"),$e={type:String,default:"static"},Po=u("layout",`
 color: var(--n-text-color);
 background-color: var(--n-color);
 box-sizing: border-box;
 position: relative;
 z-index: auto;
 flex: auto;
 overflow: hidden;
 transition:
 box-shadow .3s var(--n-bezier),
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
`,[u("layout-scroll-container",`
 overflow-x: hidden;
 box-sizing: border-box;
 height: 100%;
 `),S("absolute-positioned",`
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 `)]),To={embedded:Boolean,position:$e,nativeScrollbar:{type:Boolean,default:!0},scrollbarProps:Object,onScroll:Function,contentClass:String,contentStyle:{type:[String,Object],default:""},hasSider:Boolean,siderPlacement:{type:String,default:"left"}},Fe=Q("n-layout");function Me(e){return O({name:e?"LayoutContent":"Layout",props:Object.assign(Object.assign({},q.props),To),setup(t){const o=E(null),n=E(null),{mergedClsPrefixRef:c,inlineThemeDisabled:a}=pe(t),h=q("Layout","-layout",Po,Ee,t,c);function b(x,H){if(t.nativeScrollbar){const{value:N}=o;N&&(H===void 0?N.scrollTo(x):N.scrollTo(x,H))}else{const{value:N}=n;N&&N.scrollTo(x,H)}}Y(Fe,t);let v=0,f=0;const k=x=>{var H;const N=x.target;v=N.scrollLeft,f=N.scrollTop,(H=t.onScroll)===null||H===void 0||H.call(t,x)};_e(()=>{if(t.nativeScrollbar){const x=o.value;x&&(x.scrollTop=f,x.scrollLeft=v)}});const T={display:"flex",flexWrap:"nowrap",width:"100%",flexDirection:"row"},l={scrollTo:b},p=C(()=>{const{common:{cubicBezierEaseInOut:x},self:H}=h.value;return{"--n-bezier":x,"--n-color":t.embedded?H.colorEmbedded:H.color,"--n-text-color":H.textColor}}),A=a?fe("layout",C(()=>t.embedded?"e":""),p,t):void 0;return Object.assign({mergedClsPrefix:c,scrollableElRef:o,scrollbarInstRef:n,hasSiderStyle:T,mergedTheme:h,handleNativeElScroll:k,cssVars:a?void 0:p,themeClass:A==null?void 0:A.themeClass,onRender:A==null?void 0:A.onRender},l)},render(){var t;const{mergedClsPrefix:o,hasSider:n}=this;(t=this.onRender)===null||t===void 0||t.call(this);const c=n?this.hasSiderStyle:void 0,a=[this.themeClass,e&&`${o}-layout-content`,`${o}-layout`,`${o}-layout--${this.position}-positioned`];return s("div",{class:a,style:this.cssVars},this.nativeScrollbar?s("div",{ref:"scrollableElRef",class:[`${o}-layout-scroll-container`,this.contentClass],style:[this.contentStyle,c],onScroll:this.handleNativeElScroll},this.$slots):s(ke,Object.assign({},this.scrollbarProps,{onScroll:this.onScroll,ref:"scrollbarInstRef",theme:this.mergedTheme.peers.Scrollbar,themeOverrides:this.mergedTheme.peerOverrides.Scrollbar,contentClass:this.contentClass,contentStyle:[this.contentStyle,c]}),this.$slots))}})}const He=Me(!1),No=Me(!0),ko=u("layout-sider",`
 flex-shrink: 0;
 box-sizing: border-box;
 position: relative;
 z-index: 1;
 color: var(--n-text-color);
 transition:
 color .3s var(--n-bezier),
 border-color .3s var(--n-bezier),
 min-width .3s var(--n-bezier),
 max-width .3s var(--n-bezier),
 transform .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 background-color: var(--n-color);
 display: flex;
 justify-content: flex-end;
`,[S("bordered",[d("border",`
 content: "";
 position: absolute;
 top: 0;
 bottom: 0;
 width: 1px;
 background-color: var(--n-border-color);
 transition: background-color .3s var(--n-bezier);
 `)]),d("left-placement",[S("bordered",[d("border",`
 right: 0;
 `)])]),S("right-placement",`
 justify-content: flex-start;
 `,[S("bordered",[d("border",`
 left: 0;
 `)]),S("collapsed",[u("layout-toggle-button",[u("base-icon",`
 transform: rotate(180deg);
 `)]),u("layout-toggle-bar",[w("&:hover",[d("top",{transform:"rotate(-12deg) scale(1.15) translateY(-2px)"}),d("bottom",{transform:"rotate(12deg) scale(1.15) translateY(2px)"})])])]),u("layout-toggle-button",`
 left: 0;
 transform: translateX(-50%) translateY(-50%);
 `,[u("base-icon",`
 transform: rotate(0);
 `)]),u("layout-toggle-bar",`
 left: -28px;
 transform: rotate(180deg);
 `,[w("&:hover",[d("top",{transform:"rotate(12deg) scale(1.15) translateY(-2px)"}),d("bottom",{transform:"rotate(-12deg) scale(1.15) translateY(2px)"})])])]),S("collapsed",[u("layout-toggle-bar",[w("&:hover",[d("top",{transform:"rotate(-12deg) scale(1.15) translateY(-2px)"}),d("bottom",{transform:"rotate(12deg) scale(1.15) translateY(2px)"})])]),u("layout-toggle-button",[u("base-icon",`
 transform: rotate(0);
 `)])]),u("layout-toggle-button",`
 transition:
 color .3s var(--n-bezier),
 right .3s var(--n-bezier),
 left .3s var(--n-bezier),
 border-color .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 cursor: pointer;
 width: 24px;
 height: 24px;
 position: absolute;
 top: 50%;
 right: 0;
 border-radius: 50%;
 display: flex;
 align-items: center;
 justify-content: center;
 font-size: 18px;
 color: var(--n-toggle-button-icon-color);
 border: var(--n-toggle-button-border);
 background-color: var(--n-toggle-button-color);
 box-shadow: 0 2px 4px 0px rgba(0, 0, 0, .06);
 transform: translateX(50%) translateY(-50%);
 z-index: 1;
 `,[u("base-icon",`
 transition: transform .3s var(--n-bezier);
 transform: rotate(180deg);
 `)]),u("layout-toggle-bar",`
 cursor: pointer;
 height: 72px;
 width: 32px;
 position: absolute;
 top: calc(50% - 36px);
 right: -28px;
 `,[d("top, bottom",`
 position: absolute;
 width: 4px;
 border-radius: 2px;
 height: 38px;
 left: 14px;
 transition: 
 background-color .3s var(--n-bezier),
 transform .3s var(--n-bezier);
 `),d("bottom",`
 position: absolute;
 top: 34px;
 `),w("&:hover",[d("top",{transform:"rotate(12deg) scale(1.15) translateY(-2px)"}),d("bottom",{transform:"rotate(-12deg) scale(1.15) translateY(2px)"})]),d("top, bottom",{backgroundColor:"var(--n-toggle-bar-color)"}),w("&:hover",[d("top, bottom",{backgroundColor:"var(--n-toggle-bar-color-hover)"})])]),d("border",`
 position: absolute;
 top: 0;
 right: 0;
 bottom: 0;
 width: 1px;
 transition: background-color .3s var(--n-bezier);
 `),u("layout-sider-scroll-container",`
 flex-grow: 1;
 flex-shrink: 0;
 box-sizing: border-box;
 height: 100%;
 opacity: 0;
 transition: opacity .3s var(--n-bezier);
 max-width: 100%;
 `),S("show-content",[u("layout-sider-scroll-container",{opacity:1})]),S("absolute-positioned",`
 position: absolute;
 left: 0;
 top: 0;
 bottom: 0;
 `)]),_o=O({props:{clsPrefix:{type:String,required:!0},onClick:Function},render(){const{clsPrefix:e}=this;return s("div",{onClick:this.onClick,class:`${e}-layout-toggle-bar`},s("div",{class:`${e}-layout-toggle-bar__top`}),s("div",{class:`${e}-layout-toggle-bar__bottom`}))}}),Bo=O({name:"LayoutToggleButton",props:{clsPrefix:{type:String,required:!0},onClick:Function},render(){const{clsPrefix:e}=this;return s("div",{class:`${e}-layout-toggle-button`,onClick:this.onClick},s(Be,{clsPrefix:e},{default:()=>s(Co,null)}))}}),Eo={position:$e,bordered:Boolean,collapsedWidth:{type:Number,default:48},width:{type:[Number,String],default:272},contentClass:String,contentStyle:{type:[String,Object],default:""},collapseMode:{type:String,default:"transform"},collapsed:{type:Boolean,default:void 0},defaultCollapsed:Boolean,showCollapsedContent:{type:Boolean,default:!0},showTrigger:{type:[Boolean,String],default:!1},nativeScrollbar:{type:Boolean,default:!0},inverted:Boolean,scrollbarProps:Object,triggerClass:String,triggerStyle:[String,Object],collapsedTriggerClass:String,collapsedTriggerStyle:[String,Object],"onUpdate:collapsed":[Function,Array],onUpdateCollapsed:[Function,Array],onAfterEnter:Function,onAfterLeave:Function,onExpand:[Function,Array],onCollapse:[Function,Array],onScroll:Function},Oo=O({name:"LayoutSider",props:Object.assign(Object.assign({},q.props),Eo),setup(e){const t=V(Fe),o=E(null),n=E(null),c=E(e.defaultCollapsed),a=ve(ne(e,"collapsed"),c),h=C(()=>ce(a.value?e.collapsedWidth:e.width)),b=C(()=>e.collapseMode!=="transform"?{}:{minWidth:ce(e.width)}),v=C(()=>t?t.siderPlacement:"left");function f(P,I){if(e.nativeScrollbar){const{value:z}=o;z&&(I===void 0?z.scrollTo(P):z.scrollTo(P,I))}else{const{value:z}=n;z&&z.scrollTo(P,I)}}function k(){const{"onUpdate:collapsed":P,onUpdateCollapsed:I,onExpand:z,onCollapse:K}=e,{value:M}=a;I&&F(I,!M),P&&F(P,!M),c.value=!M,M?z&&F(z):K&&F(K)}let T=0,l=0;const p=P=>{var I;const z=P.target;T=z.scrollLeft,l=z.scrollTop,(I=e.onScroll)===null||I===void 0||I.call(e,P)};_e(()=>{if(e.nativeScrollbar){const P=o.value;P&&(P.scrollTop=l,P.scrollLeft=T)}}),Y(Oe,{collapsedRef:a,collapseModeRef:ne(e,"collapseMode")});const{mergedClsPrefixRef:A,inlineThemeDisabled:x}=pe(e),H=q("Layout","-layout-sider",ko,Ee,e,A);function N(P){var I,z;P.propertyName==="max-width"&&(a.value?(I=e.onAfterLeave)===null||I===void 0||I.call(e):(z=e.onAfterEnter)===null||z===void 0||z.call(e))}const X={scrollTo:f},j=C(()=>{const{common:{cubicBezierEaseInOut:P},self:I}=H.value,{siderToggleButtonColor:z,siderToggleButtonBorder:K,siderToggleBarColor:M,siderToggleBarColorHover:ie}=I,B={"--n-bezier":P,"--n-toggle-button-color":z,"--n-toggle-button-border":K,"--n-toggle-bar-color":M,"--n-toggle-bar-color-hover":ie};return e.inverted?(B["--n-color"]=I.siderColorInverted,B["--n-text-color"]=I.textColorInverted,B["--n-border-color"]=I.siderBorderColorInverted,B["--n-toggle-button-icon-color"]=I.siderToggleButtonIconColorInverted,B.__invertScrollbar=I.__invertScrollbar):(B["--n-color"]=I.siderColor,B["--n-text-color"]=I.textColor,B["--n-border-color"]=I.siderBorderColor,B["--n-toggle-button-icon-color"]=I.siderToggleButtonIconColor),B}),$=x?fe("layout-sider",C(()=>e.inverted?"a":"b"),j,e):void 0;return Object.assign({scrollableElRef:o,scrollbarInstRef:n,mergedClsPrefix:A,mergedTheme:H,styleMaxWidth:h,mergedCollapsed:a,scrollContainerStyle:b,siderPlacement:v,handleNativeElScroll:p,handleTransitionend:N,handleTriggerClick:k,inlineThemeDisabled:x,cssVars:j,themeClass:$==null?void 0:$.themeClass,onRender:$==null?void 0:$.onRender},X)},render(){var e;const{mergedClsPrefix:t,mergedCollapsed:o,showTrigger:n}=this;return(e=this.onRender)===null||e===void 0||e.call(this),s("aside",{class:[`${t}-layout-sider`,this.themeClass,`${t}-layout-sider--${this.position}-positioned`,`${t}-layout-sider--${this.siderPlacement}-placement`,this.bordered&&`${t}-layout-sider--bordered`,o&&`${t}-layout-sider--collapsed`,(!o||this.showCollapsedContent)&&`${t}-layout-sider--show-content`],onTransitionend:this.handleTransitionend,style:[this.inlineThemeDisabled?void 0:this.cssVars,{maxWidth:this.styleMaxWidth,width:ce(this.width)}]},this.nativeScrollbar?s("div",{class:[`${t}-layout-sider-scroll-container`,this.contentClass],onScroll:this.handleNativeElScroll,style:[this.scrollContainerStyle,{overflow:"auto"},this.contentStyle],ref:"scrollableElRef"},this.$slots):s(ke,Object.assign({},this.scrollbarProps,{onScroll:this.onScroll,ref:"scrollbarInstRef",style:this.scrollContainerStyle,contentStyle:this.contentStyle,contentClass:this.contentClass,theme:this.mergedTheme.peers.Scrollbar,themeOverrides:this.mergedTheme.peerOverrides.Scrollbar,builtinThemeOverrides:this.inverted&&this.cssVars.__invertScrollbar==="true"?{colorHover:"rgba(255, 255, 255, .4)",color:"rgba(255, 255, 255, .3)"}:void 0}),this.$slots),n?n==="bar"?s(_o,{clsPrefix:t,class:o?this.collapsedTriggerClass:this.triggerClass,style:o?this.collapsedTriggerStyle:this.triggerStyle,onClick:this.handleTriggerClick}):s(Bo,{clsPrefix:t,class:o?this.collapsedTriggerClass:this.triggerClass,style:o?this.collapsedTriggerStyle:this.triggerStyle,onClick:this.handleTriggerClick}):null,this.bordered?s("div",{class:`${t}-layout-sider__border`}):null)}}),Z=Q("n-menu"),Le=Q("n-submenu"),be=Q("n-menu-item-group"),Re=[w("&::before","background-color: var(--n-item-color-hover);"),d("arrow",`
 color: var(--n-arrow-color-hover);
 `),d("icon",`
 color: var(--n-item-icon-color-hover);
 `),u("menu-item-content-header",`
 color: var(--n-item-text-color-hover);
 `,[w("a",`
 color: var(--n-item-text-color-hover);
 `),d("extra",`
 color: var(--n-item-text-color-hover);
 `)])],Pe=[d("icon",`
 color: var(--n-item-icon-color-hover-horizontal);
 `),u("menu-item-content-header",`
 color: var(--n-item-text-color-hover-horizontal);
 `,[w("a",`
 color: var(--n-item-text-color-hover-horizontal);
 `),d("extra",`
 color: var(--n-item-text-color-hover-horizontal);
 `)])],$o=w([u("menu",`
 background-color: var(--n-color);
 color: var(--n-item-text-color);
 overflow: hidden;
 transition: background-color .3s var(--n-bezier);
 box-sizing: border-box;
 font-size: var(--n-font-size);
 padding-bottom: 6px;
 `,[S("horizontal",`
 max-width: 100%;
 width: 100%;
 display: flex;
 overflow: hidden;
 padding-bottom: 0;
 `,[u("submenu","margin: 0;"),u("menu-item","margin: 0;"),u("menu-item-content",`
 padding: 0 20px;
 border-bottom: 2px solid #0000;
 `,[w("&::before","display: none;"),S("selected","border-bottom: 2px solid var(--n-border-color-horizontal)")]),u("menu-item-content",[S("selected",[d("icon","color: var(--n-item-icon-color-active-horizontal);"),u("menu-item-content-header",`
 color: var(--n-item-text-color-active-horizontal);
 `,[w("a","color: var(--n-item-text-color-active-horizontal);"),d("extra","color: var(--n-item-text-color-active-horizontal);")])]),S("child-active",`
 border-bottom: 2px solid var(--n-border-color-horizontal);
 `,[u("menu-item-content-header",`
 color: var(--n-item-text-color-child-active-horizontal);
 `,[w("a",`
 color: var(--n-item-text-color-child-active-horizontal);
 `),d("extra",`
 color: var(--n-item-text-color-child-active-horizontal);
 `)]),d("icon",`
 color: var(--n-item-icon-color-child-active-horizontal);
 `)]),J("disabled",[J("selected, child-active",[w("&:focus-within",Pe)]),S("selected",[D(null,[d("icon","color: var(--n-item-icon-color-active-hover-horizontal);"),u("menu-item-content-header",`
 color: var(--n-item-text-color-active-hover-horizontal);
 `,[w("a","color: var(--n-item-text-color-active-hover-horizontal);"),d("extra","color: var(--n-item-text-color-active-hover-horizontal);")])])]),S("child-active",[D(null,[d("icon","color: var(--n-item-icon-color-child-active-hover-horizontal);"),u("menu-item-content-header",`
 color: var(--n-item-text-color-child-active-hover-horizontal);
 `,[w("a","color: var(--n-item-text-color-child-active-hover-horizontal);"),d("extra","color: var(--n-item-text-color-child-active-hover-horizontal);")])])]),D("border-bottom: 2px solid var(--n-border-color-horizontal);",Pe)]),u("menu-item-content-header",[w("a","color: var(--n-item-text-color-horizontal);")])])]),J("responsive",[u("menu-item-content-header",`
 overflow: hidden;
 text-overflow: ellipsis;
 `)]),S("collapsed",[u("menu-item-content",[S("selected",[w("&::before",`
 background-color: var(--n-item-color-active-collapsed) !important;
 `)]),u("menu-item-content-header","opacity: 0;"),d("arrow","opacity: 0;"),d("icon","color: var(--n-item-icon-color-collapsed);")])]),u("menu-item",`
 height: var(--n-item-height);
 margin-top: 6px;
 position: relative;
 `),u("menu-item-content",`
 box-sizing: border-box;
 line-height: 1.75;
 height: 100%;
 display: grid;
 grid-template-areas: "icon content arrow";
 grid-template-columns: auto 1fr auto;
 align-items: center;
 cursor: pointer;
 position: relative;
 padding-right: 18px;
 transition:
 background-color .3s var(--n-bezier),
 padding-left .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 `,[w("> *","z-index: 1;"),w("&::before",`
 z-index: auto;
 content: "";
 background-color: #0000;
 position: absolute;
 left: 8px;
 right: 8px;
 top: 0;
 bottom: 0;
 pointer-events: none;
 border-radius: var(--n-border-radius);
 transition: background-color .3s var(--n-bezier);
 `),S("disabled",`
 opacity: .45;
 cursor: not-allowed;
 `),S("collapsed",[d("arrow","transform: rotate(0);")]),S("selected",[w("&::before","background-color: var(--n-item-color-active);"),d("arrow","color: var(--n-arrow-color-active);"),d("icon","color: var(--n-item-icon-color-active);"),u("menu-item-content-header",`
 color: var(--n-item-text-color-active);
 `,[w("a","color: var(--n-item-text-color-active);"),d("extra","color: var(--n-item-text-color-active);")])]),S("child-active",[u("menu-item-content-header",`
 color: var(--n-item-text-color-child-active);
 `,[w("a",`
 color: var(--n-item-text-color-child-active);
 `),d("extra",`
 color: var(--n-item-text-color-child-active);
 `)]),d("arrow",`
 color: var(--n-arrow-color-child-active);
 `),d("icon",`
 color: var(--n-item-icon-color-child-active);
 `)]),J("disabled",[J("selected, child-active",[w("&:focus-within",Re)]),S("selected",[D(null,[d("arrow","color: var(--n-arrow-color-active-hover);"),d("icon","color: var(--n-item-icon-color-active-hover);"),u("menu-item-content-header",`
 color: var(--n-item-text-color-active-hover);
 `,[w("a","color: var(--n-item-text-color-active-hover);"),d("extra","color: var(--n-item-text-color-active-hover);")])])]),S("child-active",[D(null,[d("arrow","color: var(--n-arrow-color-child-active-hover);"),d("icon","color: var(--n-item-icon-color-child-active-hover);"),u("menu-item-content-header",`
 color: var(--n-item-text-color-child-active-hover);
 `,[w("a","color: var(--n-item-text-color-child-active-hover);"),d("extra","color: var(--n-item-text-color-child-active-hover);")])])]),S("selected",[D(null,[w("&::before","background-color: var(--n-item-color-active-hover);")])]),D(null,Re)]),d("icon",`
 grid-area: icon;
 color: var(--n-item-icon-color);
 transition:
 color .3s var(--n-bezier),
 font-size .3s var(--n-bezier),
 margin-right .3s var(--n-bezier);
 box-sizing: content-box;
 display: inline-flex;
 align-items: center;
 justify-content: center;
 `),d("arrow",`
 grid-area: arrow;
 font-size: 16px;
 color: var(--n-arrow-color);
 transform: rotate(180deg);
 opacity: 1;
 transition:
 color .3s var(--n-bezier),
 transform 0.2s var(--n-bezier),
 opacity 0.2s var(--n-bezier);
 `),u("menu-item-content-header",`
 grid-area: content;
 transition:
 color .3s var(--n-bezier),
 opacity .3s var(--n-bezier);
 opacity: 1;
 white-space: nowrap;
 color: var(--n-item-text-color);
 `,[w("a",`
 outline: none;
 text-decoration: none;
 transition: color .3s var(--n-bezier);
 color: var(--n-item-text-color);
 `,[w("&::before",`
 content: "";
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 `)]),d("extra",`
 font-size: .93em;
 color: var(--n-group-text-color);
 transition: color .3s var(--n-bezier);
 `)])]),u("submenu",`
 cursor: pointer;
 position: relative;
 margin-top: 6px;
 `,[u("menu-item-content",`
 height: var(--n-item-height);
 `),u("submenu-children",`
 overflow: hidden;
 padding: 0;
 `,[to({duration:".2s"})])]),u("menu-item-group",[u("menu-item-group-title",`
 margin-top: 6px;
 color: var(--n-group-text-color);
 cursor: default;
 font-size: .93em;
 height: 36px;
 display: flex;
 align-items: center;
 transition:
 padding-left .3s var(--n-bezier),
 color .3s var(--n-bezier);
 `)])]),u("menu-tooltip",[w("a",`
 color: inherit;
 text-decoration: none;
 `)]),u("menu-divider",`
 transition: background-color .3s var(--n-bezier);
 background-color: var(--n-divider-color);
 height: 1px;
 margin: 6px 18px;
 `)]);function D(e,t){return[S("hover",e,t),w("&:hover",e,t)]}const je=O({name:"MenuOptionContent",props:{collapsed:Boolean,disabled:Boolean,title:[String,Function],icon:Function,extra:[String,Function],showArrow:Boolean,childActive:Boolean,hover:Boolean,paddingLeft:Number,selected:Boolean,maxIconSize:{type:Number,required:!0},activeIconSize:{type:Number,required:!0},iconMarginRight:{type:Number,required:!0},clsPrefix:{type:String,required:!0},onClick:Function,tmNode:{type:Object,required:!0},isEllipsisPlaceholder:Boolean},setup(e){const{props:t}=V(Z);return{menuProps:t,style:C(()=>{const{paddingLeft:o}=e;return{paddingLeft:o&&`${o}px`}}),iconStyle:C(()=>{const{maxIconSize:o,activeIconSize:n,iconMarginRight:c}=e;return{width:`${o}px`,height:`${o}px`,fontSize:`${n}px`,marginRight:`${c}px`}})}},render(){const{clsPrefix:e,tmNode:t,menuProps:{renderIcon:o,renderLabel:n,renderExtra:c,expandIcon:a}}=this,h=o?o(t.rawNode):G(this.icon);return s("div",{onClick:b=>{var v;(v=this.onClick)===null||v===void 0||v.call(this,b)},role:"none",class:[`${e}-menu-item-content`,{[`${e}-menu-item-content--selected`]:this.selected,[`${e}-menu-item-content--collapsed`]:this.collapsed,[`${e}-menu-item-content--child-active`]:this.childActive,[`${e}-menu-item-content--disabled`]:this.disabled,[`${e}-menu-item-content--hover`]:this.hover}],style:this.style},h&&s("div",{class:`${e}-menu-item-content__icon`,style:this.iconStyle,role:"none"},[h]),s("div",{class:`${e}-menu-item-content-header`,role:"none"},this.isEllipsisPlaceholder?this.title:n?n(t.rawNode):G(this.title),this.extra||c?s("span",{class:`${e}-menu-item-content-header__extra`}," ",c?c(t.rawNode):G(this.extra)):null),this.showArrow?s(Be,{ariaHidden:!0,class:`${e}-menu-item-content__arrow`,clsPrefix:e},{default:()=>a?a(t.rawNode):s(wo,null)}):null)}}),re=8;function Ce(e){const t=V(Z),{props:o,mergedCollapsedRef:n}=t,c=V(Le,null),a=V(be,null),h=C(()=>o.mode==="horizontal"),b=C(()=>h.value?o.dropdownPlacement:"tmNodes"in e?"right-start":"right"),v=C(()=>{var l;return Math.max((l=o.collapsedIconSize)!==null&&l!==void 0?l:o.iconSize,o.iconSize)}),f=C(()=>{var l;return!h.value&&e.root&&n.value&&(l=o.collapsedIconSize)!==null&&l!==void 0?l:o.iconSize}),k=C(()=>{if(h.value)return;const{collapsedWidth:l,indent:p,rootIndent:A}=o,{root:x,isGroup:H}=e,N=A===void 0?p:A;return x?n.value?l/2-v.value/2:N:a&&typeof a.paddingLeftRef.value=="number"?p/2+a.paddingLeftRef.value:c&&typeof c.paddingLeftRef.value=="number"?(H?p/2:p)+c.paddingLeftRef.value:0}),T=C(()=>{const{collapsedWidth:l,indent:p,rootIndent:A}=o,{value:x}=v,{root:H}=e;return h.value||!H||!n.value?re:(A===void 0?p:A)+x+re-(l+x)/2});return{dropdownPlacement:b,activeIconSize:f,maxIconSize:v,paddingLeft:k,iconMarginRight:T,NMenu:t,NSubmenu:c,NMenuOptionGroup:a}}const xe={internalKey:{type:[String,Number],required:!0},root:Boolean,isGroup:Boolean,level:{type:Number,required:!0},title:[String,Function],extra:[String,Function]},Fo=O({name:"MenuDivider",setup(){const e=V(Z),{mergedClsPrefixRef:t,isHorizontalRef:o}=e;return()=>o.value?null:s("div",{class:`${t.value}-menu-divider`})}}),Ke=Object.assign(Object.assign({},xe),{tmNode:{type:Object,required:!0},disabled:Boolean,icon:Function,onClick:Function}),Mo=ge(Ke),Lo=O({name:"MenuOption",props:Ke,setup(e){const t=Ce(e),{NSubmenu:o,NMenu:n,NMenuOptionGroup:c}=t,{props:a,mergedClsPrefixRef:h,mergedCollapsedRef:b}=n,v=o?o.mergedDisabledRef:c?c.mergedDisabledRef:{value:!1},f=C(()=>v.value||e.disabled);function k(l){const{onClick:p}=e;p&&p(l)}function T(l){f.value||(n.doSelect(e.internalKey,e.tmNode.rawNode),k(l))}return{mergedClsPrefix:h,dropdownPlacement:t.dropdownPlacement,paddingLeft:t.paddingLeft,iconMarginRight:t.iconMarginRight,maxIconSize:t.maxIconSize,activeIconSize:t.activeIconSize,mergedTheme:n.mergedThemeRef,menuProps:a,dropdownEnabled:ue(()=>e.root&&b.value&&a.mode!=="horizontal"&&!f.value),selected:ue(()=>n.mergedValueRef.value===e.internalKey),mergedDisabled:f,handleClick:T}},render(){const{mergedClsPrefix:e,mergedTheme:t,tmNode:o,menuProps:{renderLabel:n,nodeProps:c}}=this,a=c==null?void 0:c(o.rawNode);return s("div",Object.assign({},a,{role:"menuitem",class:[`${e}-menu-item`,a==null?void 0:a.class]}),s(fo,{theme:t.peers.Tooltip,themeOverrides:t.peerOverrides.Tooltip,trigger:"hover",placement:this.dropdownPlacement,disabled:!this.dropdownEnabled||this.title===void 0,internalExtraClass:["menu-tooltip"]},{default:()=>n?n(o.rawNode):G(this.title),trigger:()=>s(je,{tmNode:o,clsPrefix:e,paddingLeft:this.paddingLeft,iconMarginRight:this.iconMarginRight,maxIconSize:this.maxIconSize,activeIconSize:this.activeIconSize,selected:this.selected,title:this.title,extra:this.extra,disabled:this.mergedDisabled,icon:this.icon,onClick:this.handleClick})}))}}),Ve=Object.assign(Object.assign({},xe),{tmNode:{type:Object,required:!0},tmNodes:{type:Array,required:!0}}),jo=ge(Ve),Ko=O({name:"MenuOptionGroup",props:Ve,setup(e){const t=Ce(e),{NSubmenu:o}=t,n=C(()=>o!=null&&o.mergedDisabledRef.value?!0:e.tmNode.disabled);Y(be,{paddingLeftRef:t.paddingLeft,mergedDisabledRef:n});const{mergedClsPrefixRef:c,props:a}=V(Z);return function(){const{value:h}=c,b=t.paddingLeft.value,{nodeProps:v}=a,f=v==null?void 0:v(e.tmNode.rawNode);return s("div",{class:`${h}-menu-item-group`,role:"group"},s("div",Object.assign({},f,{class:[`${h}-menu-item-group-title`,f==null?void 0:f.class],style:[(f==null?void 0:f.style)||"",b!==void 0?`padding-left: ${b}px;`:""]}),G(e.title),e.extra?s(ro,null," ",G(e.extra)):null),s("div",null,e.tmNodes.map(k=>ye(k,a))))}}});function me(e){return e.type==="divider"||e.type==="render"}function Vo(e){return e.type==="divider"}function ye(e,t){const{rawNode:o}=e,{show:n}=o;if(n===!1)return null;if(me(o))return Vo(o)?s(Fo,Object.assign({key:e.key},o.props)):null;const{labelField:c}=t,{key:a,level:h,isGroup:b}=e,v=Object.assign(Object.assign({},o),{title:o.title||o[c],extra:o.titleExtra||o.extra,key:a,internalKey:a,level:h,root:h===0,isGroup:b});return e.children?e.isGroup?s(Ko,ae(v,jo,{tmNode:e,tmNodes:e.children,key:a})):s(he,ae(v,Do,{key:a,rawNodes:o[t.childrenField],tmNodes:e.children,tmNode:e})):s(Lo,ae(v,Mo,{key:a,tmNode:e}))}const De=Object.assign(Object.assign({},xe),{rawNodes:{type:Array,default:()=>[]},tmNodes:{type:Array,default:()=>[]},tmNode:{type:Object,required:!0},disabled:Boolean,icon:Function,onClick:Function,domId:String,virtualChildActive:{type:Boolean,default:void 0},isEllipsisPlaceholder:Boolean}),Do=ge(De),he=O({name:"Submenu",props:De,setup(e){const t=Ce(e),{NMenu:o,NSubmenu:n}=t,{props:c,mergedCollapsedRef:a,mergedThemeRef:h}=o,b=C(()=>{const{disabled:l}=e;return n!=null&&n.mergedDisabledRef.value||c.disabled?!0:l}),v=E(!1);Y(Le,{paddingLeftRef:t.paddingLeft,mergedDisabledRef:b}),Y(be,null);function f(){const{onClick:l}=e;l&&l()}function k(){b.value||(a.value||o.toggleExpand(e.internalKey),f())}function T(l){v.value=l}return{menuProps:c,mergedTheme:h,doSelect:o.doSelect,inverted:o.invertedRef,isHorizontal:o.isHorizontalRef,mergedClsPrefix:o.mergedClsPrefixRef,maxIconSize:t.maxIconSize,activeIconSize:t.activeIconSize,iconMarginRight:t.iconMarginRight,dropdownPlacement:t.dropdownPlacement,dropdownShow:v,paddingLeft:t.paddingLeft,mergedDisabled:b,mergedValue:o.mergedValueRef,childActive:ue(()=>{var l;return(l=e.virtualChildActive)!==null&&l!==void 0?l:o.activePathRef.value.includes(e.internalKey)}),collapsed:C(()=>c.mode==="horizontal"?!1:a.value?!0:!o.mergedExpandedKeysRef.value.includes(e.internalKey)),dropdownEnabled:C(()=>!b.value&&(c.mode==="horizontal"||a.value)),handlePopoverShowChange:T,handleClick:k}},render(){var e;const{mergedClsPrefix:t,menuProps:{renderIcon:o,renderLabel:n}}=this,c=()=>{const{isHorizontal:h,paddingLeft:b,collapsed:v,mergedDisabled:f,maxIconSize:k,activeIconSize:T,title:l,childActive:p,icon:A,handleClick:x,menuProps:{nodeProps:H},dropdownShow:N,iconMarginRight:X,tmNode:j,mergedClsPrefix:$,isEllipsisPlaceholder:P,extra:I}=this,z=H==null?void 0:H(j.rawNode);return s("div",Object.assign({},z,{class:[`${$}-menu-item`,z==null?void 0:z.class],role:"menuitem"}),s(je,{tmNode:j,paddingLeft:b,collapsed:v,disabled:f,iconMarginRight:X,maxIconSize:k,activeIconSize:T,title:l,extra:I,showArrow:!h,childActive:p,clsPrefix:$,icon:A,hover:N,onClick:x,isEllipsisPlaceholder:P}))},a=()=>s(no,null,{default:()=>{const{tmNodes:h,collapsed:b}=this;return b?null:s("div",{class:`${t}-submenu-children`,role:"menu"},h.map(v=>ye(v,this.menuProps)))}});return this.root?s(bo,Object.assign({size:"large",trigger:"hover"},(e=this.menuProps)===null||e===void 0?void 0:e.dropdownProps,{themeOverrides:this.mergedTheme.peerOverrides.Dropdown,theme:this.mergedTheme.peers.Dropdown,builtinThemeOverrides:{fontSizeLarge:"14px",optionIconSizeLarge:"18px"},value:this.mergedValue,disabled:!this.dropdownEnabled,placement:this.dropdownPlacement,keyField:this.menuProps.keyField,labelField:this.menuProps.labelField,childrenField:this.menuProps.childrenField,onUpdateShow:this.handlePopoverShowChange,options:this.rawNodes,onSelect:this.doSelect,inverted:this.inverted,renderIcon:o,renderLabel:n}),{default:()=>s("div",{class:`${t}-submenu`,role:"menu","aria-expanded":!this.collapsed,id:this.domId},c(),this.isHorizontal?null:a())}):s("div",{class:`${t}-submenu`,role:"menu","aria-expanded":!this.collapsed,id:this.domId},c(),a())}}),Uo=Object.assign(Object.assign({},q.props),{options:{type:Array,default:()=>[]},collapsed:{type:Boolean,default:void 0},collapsedWidth:{type:Number,default:48},iconSize:{type:Number,default:20},collapsedIconSize:{type:Number,default:24},rootIndent:Number,indent:{type:Number,default:32},labelField:{type:String,default:"label"},keyField:{type:String,default:"key"},childrenField:{type:String,default:"children"},disabledField:{type:String,default:"disabled"},defaultExpandAll:Boolean,defaultExpandedKeys:Array,expandedKeys:Array,value:[String,Number],defaultValue:{type:[String,Number],default:null},mode:{type:String,default:"vertical"},watchProps:{type:Array,default:void 0},disabled:Boolean,show:{type:Boolean,default:!0},inverted:Boolean,"onUpdate:expandedKeys":[Function,Array],onUpdateExpandedKeys:[Function,Array],onUpdateValue:[Function,Array],"onUpdate:value":[Function,Array],expandIcon:Function,renderIcon:Function,renderLabel:Function,renderExtra:Function,dropdownProps:Object,accordion:Boolean,nodeProps:Function,dropdownPlacement:{type:String,default:"bottom"},responsive:Boolean,items:Array,onOpenNamesChange:[Function,Array],onSelect:[Function,Array],onExpandedNamesChange:[Function,Array],expandedNames:Array,defaultExpandedNames:Array}),Wo=O({name:"Menu",inheritAttrs:!1,props:Uo,setup(e){const{mergedClsPrefixRef:t,inlineThemeDisabled:o}=pe(e),n=q("Menu","-menu",$o,Ro,e,t),c=V(Oe,null),a=C(()=>{var m;const{collapsed:y}=e;if(y!==void 0)return y;if(c){const{collapseModeRef:r,collapsedRef:g}=c;if(r.value==="width")return(m=g.value)!==null&&m!==void 0?m:!1}return!1}),h=C(()=>{const{keyField:m,childrenField:y,disabledField:r}=e;return de(e.items||e.options,{getIgnored(g){return me(g)},getChildren(g){return g[y]},getDisabled(g){return g[r]},getKey(g){var R;return(R=g[m])!==null&&R!==void 0?R:g.name}})}),b=C(()=>new Set(h.value.treeNodes.map(m=>m.key))),{watchProps:v}=e,f=E(null);v!=null&&v.includes("defaultValue")?we(()=>{f.value=e.defaultValue}):f.value=e.defaultValue;const k=ne(e,"value"),T=ve(k,f),l=E([]),p=()=>{l.value=e.defaultExpandAll?h.value.getNonLeafKeys():e.defaultExpandedNames||e.defaultExpandedKeys||h.value.getPath(T.value,{includeSelf:!1}).keyPath};v!=null&&v.includes("defaultExpandedKeys")?we(p):p();const A=yo(e,["expandedNames","expandedKeys"]),x=ve(A,l),H=C(()=>h.value.treeNodes),N=C(()=>h.value.getPath(T.value).keyPath);Y(Z,{props:e,mergedCollapsedRef:a,mergedThemeRef:n,mergedValueRef:T,mergedExpandedKeysRef:x,activePathRef:N,mergedClsPrefixRef:t,isHorizontalRef:C(()=>e.mode==="horizontal"),invertedRef:ne(e,"inverted"),doSelect:X,toggleExpand:$});function X(m,y){const{"onUpdate:value":r,onUpdateValue:g,onSelect:R}=e;g&&F(g,m,y),r&&F(r,m,y),R&&F(R,m,y),f.value=m}function j(m){const{"onUpdate:expandedKeys":y,onUpdateExpandedKeys:r,onExpandedNamesChange:g,onOpenNamesChange:R}=e;y&&F(y,m),r&&F(r,m),g&&F(g,m),R&&F(R,m),l.value=m}function $(m){const y=Array.from(x.value),r=y.findIndex(g=>g===m);if(~r)y.splice(r,1);else{if(e.accordion&&b.value.has(m)){const g=y.findIndex(R=>b.value.has(R));g>-1&&y.splice(g,1)}y.push(m)}j(y)}const P=m=>{const y=h.value.getPath(m??T.value,{includeSelf:!1}).keyPath;if(!y.length)return;const r=Array.from(x.value),g=new Set([...r,...y]);e.accordion&&b.value.forEach(R=>{g.has(R)&&!y.includes(R)&&g.delete(R)}),j(Array.from(g))},I=C(()=>{const{inverted:m}=e,{common:{cubicBezierEaseInOut:y},self:r}=n.value,{borderRadius:g,borderColorHorizontal:R,fontSize:Qe,itemHeight:Ze,dividerColor:eo}=r,i={"--n-divider-color":eo,"--n-bezier":y,"--n-font-size":Qe,"--n-border-color-horizontal":R,"--n-border-radius":g,"--n-item-height":Ze};return m?(i["--n-group-text-color"]=r.groupTextColorInverted,i["--n-color"]=r.colorInverted,i["--n-item-text-color"]=r.itemTextColorInverted,i["--n-item-text-color-hover"]=r.itemTextColorHoverInverted,i["--n-item-text-color-active"]=r.itemTextColorActiveInverted,i["--n-item-text-color-child-active"]=r.itemTextColorChildActiveInverted,i["--n-item-text-color-child-active-hover"]=r.itemTextColorChildActiveInverted,i["--n-item-text-color-active-hover"]=r.itemTextColorActiveHoverInverted,i["--n-item-icon-color"]=r.itemIconColorInverted,i["--n-item-icon-color-hover"]=r.itemIconColorHoverInverted,i["--n-item-icon-color-active"]=r.itemIconColorActiveInverted,i["--n-item-icon-color-active-hover"]=r.itemIconColorActiveHoverInverted,i["--n-item-icon-color-child-active"]=r.itemIconColorChildActiveInverted,i["--n-item-icon-color-child-active-hover"]=r.itemIconColorChildActiveHoverInverted,i["--n-item-icon-color-collapsed"]=r.itemIconColorCollapsedInverted,i["--n-item-text-color-horizontal"]=r.itemTextColorHorizontalInverted,i["--n-item-text-color-hover-horizontal"]=r.itemTextColorHoverHorizontalInverted,i["--n-item-text-color-active-horizontal"]=r.itemTextColorActiveHorizontalInverted,i["--n-item-text-color-child-active-horizontal"]=r.itemTextColorChildActiveHorizontalInverted,i["--n-item-text-color-child-active-hover-horizontal"]=r.itemTextColorChildActiveHoverHorizontalInverted,i["--n-item-text-color-active-hover-horizontal"]=r.itemTextColorActiveHoverHorizontalInverted,i["--n-item-icon-color-horizontal"]=r.itemIconColorHorizontalInverted,i["--n-item-icon-color-hover-horizontal"]=r.itemIconColorHoverHorizontalInverted,i["--n-item-icon-color-active-horizontal"]=r.itemIconColorActiveHorizontalInverted,i["--n-item-icon-color-active-hover-horizontal"]=r.itemIconColorActiveHoverHorizontalInverted,i["--n-item-icon-color-child-active-horizontal"]=r.itemIconColorChildActiveHorizontalInverted,i["--n-item-icon-color-child-active-hover-horizontal"]=r.itemIconColorChildActiveHoverHorizontalInverted,i["--n-arrow-color"]=r.arrowColorInverted,i["--n-arrow-color-hover"]=r.arrowColorHoverInverted,i["--n-arrow-color-active"]=r.arrowColorActiveInverted,i["--n-arrow-color-active-hover"]=r.arrowColorActiveHoverInverted,i["--n-arrow-color-child-active"]=r.arrowColorChildActiveInverted,i["--n-arrow-color-child-active-hover"]=r.arrowColorChildActiveHoverInverted,i["--n-item-color-hover"]=r.itemColorHoverInverted,i["--n-item-color-active"]=r.itemColorActiveInverted,i["--n-item-color-active-hover"]=r.itemColorActiveHoverInverted,i["--n-item-color-active-collapsed"]=r.itemColorActiveCollapsedInverted):(i["--n-group-text-color"]=r.groupTextColor,i["--n-color"]=r.color,i["--n-item-text-color"]=r.itemTextColor,i["--n-item-text-color-hover"]=r.itemTextColorHover,i["--n-item-text-color-active"]=r.itemTextColorActive,i["--n-item-text-color-child-active"]=r.itemTextColorChildActive,i["--n-item-text-color-child-active-hover"]=r.itemTextColorChildActiveHover,i["--n-item-text-color-active-hover"]=r.itemTextColorActiveHover,i["--n-item-icon-color"]=r.itemIconColor,i["--n-item-icon-color-hover"]=r.itemIconColorHover,i["--n-item-icon-color-active"]=r.itemIconColorActive,i["--n-item-icon-color-active-hover"]=r.itemIconColorActiveHover,i["--n-item-icon-color-child-active"]=r.itemIconColorChildActive,i["--n-item-icon-color-child-active-hover"]=r.itemIconColorChildActiveHover,i["--n-item-icon-color-collapsed"]=r.itemIconColorCollapsed,i["--n-item-text-color-horizontal"]=r.itemTextColorHorizontal,i["--n-item-text-color-hover-horizontal"]=r.itemTextColorHoverHorizontal,i["--n-item-text-color-active-horizontal"]=r.itemTextColorActiveHorizontal,i["--n-item-text-color-child-active-horizontal"]=r.itemTextColorChildActiveHorizontal,i["--n-item-text-color-child-active-hover-horizontal"]=r.itemTextColorChildActiveHoverHorizontal,i["--n-item-text-color-active-hover-horizontal"]=r.itemTextColorActiveHoverHorizontal,i["--n-item-icon-color-horizontal"]=r.itemIconColorHorizontal,i["--n-item-icon-color-hover-horizontal"]=r.itemIconColorHoverHorizontal,i["--n-item-icon-color-active-horizontal"]=r.itemIconColorActiveHorizontal,i["--n-item-icon-color-active-hover-horizontal"]=r.itemIconColorActiveHoverHorizontal,i["--n-item-icon-color-child-active-horizontal"]=r.itemIconColorChildActiveHorizontal,i["--n-item-icon-color-child-active-hover-horizontal"]=r.itemIconColorChildActiveHoverHorizontal,i["--n-arrow-color"]=r.arrowColor,i["--n-arrow-color-hover"]=r.arrowColorHover,i["--n-arrow-color-active"]=r.arrowColorActive,i["--n-arrow-color-active-hover"]=r.arrowColorActiveHover,i["--n-arrow-color-child-active"]=r.arrowColorChildActive,i["--n-arrow-color-child-active-hover"]=r.arrowColorChildActiveHover,i["--n-item-color-hover"]=r.itemColorHover,i["--n-item-color-active"]=r.itemColorActive,i["--n-item-color-active-hover"]=r.itemColorActiveHover,i["--n-item-color-active-collapsed"]=r.itemColorActiveCollapsed),i}),z=o?fe("menu",C(()=>e.inverted?"a":"b"),I,e):void 0,K=lo(),M=E(null),ie=E(null);let B=!0;const Ie=()=>{var m;B?B=!1:(m=M.value)===null||m===void 0||m.sync({showAllItemsBeforeCalculate:!0})};function Ue(){return document.getElementById(K)}const ee=E(-1);function We(m){ee.value=e.options.length-m}function Ge(m){m||(ee.value=-1)}const qe=C(()=>{const m=ee.value;return{children:m===-1?[]:e.options.slice(m)}}),Ye=C(()=>{const{childrenField:m,disabledField:y,keyField:r}=e;return de([qe.value],{getIgnored(g){return me(g)},getChildren(g){return g[m]},getDisabled(g){return g[y]},getKey(g){var R;return(R=g[r])!==null&&R!==void 0?R:g.name}})}),Xe=C(()=>de([{}]).treeNodes[0]);function Je(){var m;if(ee.value===-1)return s(he,{root:!0,level:0,key:"__ellpisisGroupPlaceholder__",internalKey:"__ellpisisGroupPlaceholder__",title:"···",tmNode:Xe.value,domId:K,isEllipsisPlaceholder:!0});const y=Ye.value.treeNodes[0],r=N.value,g=!!(!((m=y.children)===null||m===void 0)&&m.some(R=>r.includes(R.key)));return s(he,{level:0,root:!0,key:"__ellpisisGroup__",internalKey:"__ellpisisGroup__",title:"···",virtualChildActive:g,tmNode:y,domId:K,rawNodes:y.rawNode.children||[],tmNodes:y.children||[],isEllipsisPlaceholder:!0})}return{mergedClsPrefix:t,controlledExpandedKeys:A,uncontrolledExpanededKeys:l,mergedExpandedKeys:x,uncontrolledValue:f,mergedValue:T,activePath:N,tmNodes:H,mergedTheme:n,mergedCollapsed:a,cssVars:o?void 0:I,themeClass:z==null?void 0:z.themeClass,overflowRef:M,counterRef:ie,updateCounter:()=>{},onResize:Ie,onUpdateOverflow:Ge,onUpdateCount:We,renderCounter:Je,getCounter:Ue,onRender:z==null?void 0:z.onRender,showOption:P,deriveResponsiveState:Ie}},render(){const{mergedClsPrefix:e,mode:t,themeClass:o,onRender:n}=this;n==null||n();const c=()=>this.tmNodes.map(v=>ye(v,this.$props)),h=t==="horizontal"&&this.responsive,b=()=>s("div",ao(this.$attrs,{role:t==="horizontal"?"menubar":"menu",class:[`${e}-menu`,o,`${e}-menu--${t}`,h&&`${e}-menu--responsive`,this.mergedCollapsed&&`${e}-menu--collapsed`],style:this.cssVars}),h?s(xo,{ref:"overflowRef",onUpdateOverflow:this.onUpdateOverflow,getCounter:this.getCounter,onUpdateCount:this.onUpdateCount,updateCounter:this.updateCounter,style:{width:"100%",display:"flex",overflow:"hidden"}},{default:c,counter:this.renderCounter}):c());return h?s(io,{onResize:this.onResize},{default:b}):b()}}),Go={key:0,class:"brand-copy"},qo={key:0,class:"brand-panel"},Yo={class:"brand-panel__value"},Xo={class:"brand-panel__meta"},Jo={class:"topbar"},Qo={class:"topbar-title-row"},Zo={class:"topbar-title"},et={class:"topbar-date"},ot={class:"content-shell"},tt=O({__name:"MainLayout",setup(e){const t=E(!1),o=uo(),n=vo(),c=ho(),a=C(()=>{const l=n.path;return l.startsWith("/dashboard")?"dashboard":l.startsWith("/applications")?"applications":l.startsWith("/recording")?"recording":l.startsWith("/testcases")?"testcases":l==="/replay"?"replay":l.startsWith("/replay/history")||l.startsWith("/results")?"replay-history":l.startsWith("/suites")?"suites":l.startsWith("/schedule")?"schedule":l.startsWith("/compare")?"compare":l.startsWith("/ci")?"ci":l.startsWith("/settings")?"settings":l.startsWith("/users")?"users":"applications"}),h={dashboard:"数据总览",applications:"应用管理",recording:"录制中心",testcases:"测试用例库",replay:"发起回放","replay-history":"回放历史",suites:"回放套件",schedule:"定时回放",compare:"双环境对比",ci:"CI 集成",settings:"平台指引",users:"用户管理"},b=C(()=>h[a.value]||"AREX Recorder"),v=C(()=>{const l=new Date,p=["周日","周一","周二","周三","周四","周五","周六"],A=String(l.getMonth()+1).padStart(2,"0"),x=String(l.getDate()).padStart(2,"0");return`${A}/${x} ${p[l.getDay()]}`}),f=[{label:"数据总览",key:"dashboard",icon:()=>s("span","概")},{label:"应用管理",key:"applications",icon:()=>s("span","应")},{label:"录制中心",key:"recording",icon:()=>s("span","录")},{label:"测试用例库",key:"testcases",icon:()=>s("span","例")},{label:"发起回放",key:"replay",icon:()=>s("span","回")},{label:"回放历史",key:"replay-history",icon:()=>s("span","史")},{label:"回放套件",key:"suites",icon:()=>s("span","套")},{label:"定时回放",key:"schedule",icon:()=>s("span","定")},{label:"双环境对比",key:"compare",icon:()=>s("span","比")},{label:"CI 集成",key:"ci",icon:()=>s("span","CI")},{label:"用户管理",key:"users",icon:()=>s("span","用")},{label:"平台指引",key:"settings",icon:()=>s("span","指")}],k=C(()=>f.filter(l=>l.key==="compare"||l.key==="ci"||l.key==="users"||l.key==="settings"?!1:!(l.key==="users"||l.key==="ci")||c.role==="admin"));function T(l){if(l==="replay-history"){o.push("/replay/history");return}o.push(`/${l}`)}return(l,p)=>{const A=mo("router-view");return te(),Se(L(He),{class:"app-shell","has-sider":""},{default:U(()=>[p[9]||(p[9]=_("div",{class:"shell-bg shell-bg--left"},null,-1)),p[10]||(p[10]=_("div",{class:"shell-bg shell-bg--right"},null,-1)),W(L(Oo),{class:"app-sider","collapse-mode":"width","collapsed-width":72,width:252,collapsed:t.value,onCollapse:p[1]||(p[1]=x=>t.value=!0),onExpand:p[2]||(p[2]=x=>t.value=!1)},{default:U(()=>[_("div",{class:"brand",onClick:p[0]||(p[0]=x=>t.value=!t.value)},[p[5]||(p[5]=_("div",{class:"brand-mark"},"AR",-1)),t.value?se("",!0):(te(),Ae("div",Go,[...p[4]||(p[4]=[_("div",{class:"brand-title"},"AREX Recorder",-1),_("div",{class:"brand-subtitle"},"录制、回放、对比",-1)])]))]),t.value?se("",!0):(te(),Ae("div",qo,[p[6]||(p[6]=_("div",{class:"brand-panel__label"},"当前页面",-1)),_("div",Yo,oe(b.value),1),_("div",Xo,oe(v.value),1)])),W(L(Wo),{class:"side-menu",collapsed:t.value,"collapsed-width":72,"collapsed-icon-size":20,options:k.value,value:a.value,"onUpdate:value":T},null,8,["collapsed","options","value"])]),_:1},8,["collapsed"]),W(L(He),{class:"app-main"},{default:U(()=>[_("div",Jo,[_("div",null,[_("div",Qo,[_("div",Zo,oe(b.value),1)]),p[7]||(p[7]=_("div",{class:"topbar-subtitle"},"面向录制同步、回放验证和双环境差异检查的统一平台",-1))]),W(L(Io),{align:"center",size:"small"},{default:U(()=>[_("div",et,oe(v.value),1),L(n).path!=="/dashboard"?(te(),Se(L(so),{key:0,quaternary:"",size:"small",onClick:p[3]||(p[3]=x=>L(o).push("/dashboard"))},{default:U(()=>[...p[8]||(p[8]=[co("总览",-1)])]),_:1})):se("",!0)]),_:1})]),W(L(No),{class:"app-content","content-style":"padding: 0 24px 24px;"},{default:U(()=>[_("div",ot,[W(A)])]),_:1})]),_:1})]),_:1})}}}),dt=zo(tt,[["__scopeId","data-v-2ad562c1"]]);export{dt as default};
