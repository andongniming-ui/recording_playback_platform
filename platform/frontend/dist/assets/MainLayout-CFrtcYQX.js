import{d as O,h as l,c as Te,s as oo,a as Ne,b as ze,e as le,f as J,g as m,i as H,S as ke,u as pe,j as q,k as _e,l as fe,m as x,r as E,p as Y,n as d,o as w,N as Be,q as V,t as F,v as ne,w as Z,x as to,y as G,z as ge,A as ue,F as ro,B as ae,C as no,V as io,D as we,E as lo,G as ao,H as so,I as co,J as Se,K as U,L,M as _,O as W,P as Ae,Q as se,R as oe,T as uo,U as vo,W as mo,X as ho,Y as po,Z as te}from"./index-DKfkuiLi.js";import{t as fo,N as go}from"./Tooltip-Cx9wBadY.js";import{d as bo,N as Co}from"./Dropdown-BMHBmLUg.js";import{f as ce,u as ve}from"./get-C9z6N27c.js";import{C as xo,V as yo,u as Io,c as de,N as zo}from"./Space-C_ahS7-l.js";import{_ as wo}from"./_plugin-vue_export-helper-DlAUqK2U.js";const So=O({name:"ChevronDownFilled",render(){return l("svg",{viewBox:"0 0 16 16",fill:"none",xmlns:"http://www.w3.org/2000/svg"},l("path",{d:"M3.20041 5.73966C3.48226 5.43613 3.95681 5.41856 4.26034 5.70041L8 9.22652L11.7397 5.70041C12.0432 5.41856 12.5177 5.43613 12.7996 5.73966C13.0815 6.0432 13.0639 6.51775 12.7603 6.7996L8.51034 10.7996C8.22258 11.0668 7.77743 11.0668 7.48967 10.7996L3.23966 6.7996C2.93613 6.51775 2.91856 6.0432 3.20041 5.73966Z",fill:"currentColor"}))}});function Ao(e){const{baseColor:t,textColor2:o,bodyColor:n,cardColor:s,dividerColor:a,actionColor:v,scrollbarColor:C,scrollbarColorHover:p,invertedColor:f}=e;return{textColor:o,textColorInverted:"#FFF",color:n,colorEmbedded:v,headerColor:s,headerColorInverted:f,footerColor:v,footerColorInverted:f,headerBorderColor:a,headerBorderColorInverted:f,footerBorderColor:a,footerBorderColorInverted:f,siderBorderColor:a,siderBorderColorInverted:f,siderColor:s,siderColorInverted:f,siderToggleButtonBorder:`1px solid ${a}`,siderToggleButtonColor:t,siderToggleButtonIconColor:o,siderToggleButtonIconColorInverted:o,siderToggleBarColor:ze(n,C),siderToggleBarColorHover:ze(n,p),__invertScrollbar:"true"}}const Ee=Te({name:"Layout",common:Ne,peers:{Scrollbar:oo},self:Ao});function Ho(e,t,o,n){return{itemColorHoverInverted:"#0000",itemColorActiveInverted:t,itemColorActiveHoverInverted:t,itemColorActiveCollapsedInverted:t,itemTextColorInverted:e,itemTextColorHoverInverted:o,itemTextColorChildActiveInverted:o,itemTextColorChildActiveHoverInverted:o,itemTextColorActiveInverted:o,itemTextColorActiveHoverInverted:o,itemTextColorHorizontalInverted:e,itemTextColorHoverHorizontalInverted:o,itemTextColorChildActiveHorizontalInverted:o,itemTextColorChildActiveHoverHorizontalInverted:o,itemTextColorActiveHorizontalInverted:o,itemTextColorActiveHoverHorizontalInverted:o,itemIconColorInverted:e,itemIconColorHoverInverted:o,itemIconColorActiveInverted:o,itemIconColorActiveHoverInverted:o,itemIconColorChildActiveInverted:o,itemIconColorChildActiveHoverInverted:o,itemIconColorCollapsedInverted:e,itemIconColorHorizontalInverted:e,itemIconColorHoverHorizontalInverted:o,itemIconColorActiveHorizontalInverted:o,itemIconColorActiveHoverHorizontalInverted:o,itemIconColorChildActiveHorizontalInverted:o,itemIconColorChildActiveHoverHorizontalInverted:o,arrowColorInverted:e,arrowColorHoverInverted:o,arrowColorActiveInverted:o,arrowColorActiveHoverInverted:o,arrowColorChildActiveInverted:o,arrowColorChildActiveHoverInverted:o,groupTextColorInverted:n}}function Ro(e){const{borderRadius:t,textColor3:o,primaryColor:n,textColor2:s,textColor1:a,fontSize:v,dividerColor:C,hoverColor:p,primaryColorHover:f}=e;return Object.assign({borderRadius:t,color:"#0000",groupTextColor:o,itemColorHover:p,itemColorActive:le(n,{alpha:.1}),itemColorActiveHover:le(n,{alpha:.1}),itemColorActiveCollapsed:le(n,{alpha:.1}),itemTextColor:s,itemTextColorHover:s,itemTextColorActive:n,itemTextColorActiveHover:n,itemTextColorChildActive:n,itemTextColorChildActiveHover:n,itemTextColorHorizontal:s,itemTextColorHoverHorizontal:f,itemTextColorActiveHorizontal:n,itemTextColorActiveHoverHorizontal:n,itemTextColorChildActiveHorizontal:n,itemTextColorChildActiveHoverHorizontal:n,itemIconColor:a,itemIconColorHover:a,itemIconColorActive:n,itemIconColorActiveHover:n,itemIconColorChildActive:n,itemIconColorChildActiveHover:n,itemIconColorCollapsed:a,itemIconColorHorizontal:a,itemIconColorHoverHorizontal:f,itemIconColorActiveHorizontal:n,itemIconColorActiveHoverHorizontal:n,itemIconColorChildActiveHorizontal:n,itemIconColorChildActiveHoverHorizontal:n,itemHeight:"42px",arrowColor:s,arrowColorHover:s,arrowColorActive:n,arrowColorActiveHover:n,arrowColorChildActive:n,arrowColorChildActiveHover:n,colorInverted:"#0000",borderColorHorizontal:"#0000",fontSize:v,dividerColor:C},Ho("#BBB",n,"#FFF","#AAA"))}const Po=Te({name:"Menu",common:Ne,peers:{Tooltip:fo,Dropdown:bo},self:Ro}),Oe=J("n-layout-sider"),$e={type:String,default:"static"},To=m("layout",`
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
`,[m("layout-scroll-container",`
 overflow-x: hidden;
 box-sizing: border-box;
 height: 100%;
 `),H("absolute-positioned",`
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 `)]),No={embedded:Boolean,position:$e,nativeScrollbar:{type:Boolean,default:!0},scrollbarProps:Object,onScroll:Function,contentClass:String,contentStyle:{type:[String,Object],default:""},hasSider:Boolean,siderPlacement:{type:String,default:"left"}},Fe=J("n-layout");function Me(e){return O({name:e?"LayoutContent":"Layout",props:Object.assign(Object.assign({},q.props),No),setup(t){const o=E(null),n=E(null),{mergedClsPrefixRef:s,inlineThemeDisabled:a}=pe(t),v=q("Layout","-layout",To,Ee,t,s);function C(c,S){if(t.nativeScrollbar){const{value:A}=o;A&&(S===void 0?A.scrollTo(c):A.scrollTo(c,S))}else{const{value:A}=n;A&&A.scrollTo(c,S)}}Y(Fe,t);let p=0,f=0;const k=c=>{var S;const A=c.target;p=A.scrollLeft,f=A.scrollTop,(S=t.onScroll)===null||S===void 0||S.call(t,c)};_e(()=>{if(t.nativeScrollbar){const c=o.value;c&&(c.scrollTop=f,c.scrollLeft=p)}});const N={display:"flex",flexWrap:"nowrap",width:"100%",flexDirection:"row"},g={scrollTo:C},P=x(()=>{const{common:{cubicBezierEaseInOut:c},self:S}=v.value;return{"--n-bezier":c,"--n-color":t.embedded?S.colorEmbedded:S.color,"--n-text-color":S.textColor}}),u=a?fe("layout",x(()=>t.embedded?"e":""),P,t):void 0;return Object.assign({mergedClsPrefix:s,scrollableElRef:o,scrollbarInstRef:n,hasSiderStyle:N,mergedTheme:v,handleNativeElScroll:k,cssVars:a?void 0:P,themeClass:u==null?void 0:u.themeClass,onRender:u==null?void 0:u.onRender},g)},render(){var t;const{mergedClsPrefix:o,hasSider:n}=this;(t=this.onRender)===null||t===void 0||t.call(this);const s=n?this.hasSiderStyle:void 0,a=[this.themeClass,e&&`${o}-layout-content`,`${o}-layout`,`${o}-layout--${this.position}-positioned`];return l("div",{class:a,style:this.cssVars},this.nativeScrollbar?l("div",{ref:"scrollableElRef",class:[`${o}-layout-scroll-container`,this.contentClass],style:[this.contentStyle,s],onScroll:this.handleNativeElScroll},this.$slots):l(ke,Object.assign({},this.scrollbarProps,{onScroll:this.onScroll,ref:"scrollbarInstRef",theme:this.mergedTheme.peers.Scrollbar,themeOverrides:this.mergedTheme.peerOverrides.Scrollbar,contentClass:this.contentClass,contentStyle:[this.contentStyle,s]}),this.$slots))}})}const He=Me(!1),ko=Me(!0),_o=m("layout-sider",`
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
`,[H("bordered",[d("border",`
 content: "";
 position: absolute;
 top: 0;
 bottom: 0;
 width: 1px;
 background-color: var(--n-border-color);
 transition: background-color .3s var(--n-bezier);
 `)]),d("left-placement",[H("bordered",[d("border",`
 right: 0;
 `)])]),H("right-placement",`
 justify-content: flex-start;
 `,[H("bordered",[d("border",`
 left: 0;
 `)]),H("collapsed",[m("layout-toggle-button",[m("base-icon",`
 transform: rotate(180deg);
 `)]),m("layout-toggle-bar",[w("&:hover",[d("top",{transform:"rotate(-12deg) scale(1.15) translateY(-2px)"}),d("bottom",{transform:"rotate(12deg) scale(1.15) translateY(2px)"})])])]),m("layout-toggle-button",`
 left: 0;
 transform: translateX(-50%) translateY(-50%);
 `,[m("base-icon",`
 transform: rotate(0);
 `)]),m("layout-toggle-bar",`
 left: -28px;
 transform: rotate(180deg);
 `,[w("&:hover",[d("top",{transform:"rotate(12deg) scale(1.15) translateY(-2px)"}),d("bottom",{transform:"rotate(-12deg) scale(1.15) translateY(2px)"})])])]),H("collapsed",[m("layout-toggle-bar",[w("&:hover",[d("top",{transform:"rotate(-12deg) scale(1.15) translateY(-2px)"}),d("bottom",{transform:"rotate(12deg) scale(1.15) translateY(2px)"})])]),m("layout-toggle-button",[m("base-icon",`
 transform: rotate(0);
 `)])]),m("layout-toggle-button",`
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
 `,[m("base-icon",`
 transition: transform .3s var(--n-bezier);
 transform: rotate(180deg);
 `)]),m("layout-toggle-bar",`
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
 `),m("layout-sider-scroll-container",`
 flex-grow: 1;
 flex-shrink: 0;
 box-sizing: border-box;
 height: 100%;
 opacity: 0;
 transition: opacity .3s var(--n-bezier);
 max-width: 100%;
 `),H("show-content",[m("layout-sider-scroll-container",{opacity:1})]),H("absolute-positioned",`
 position: absolute;
 left: 0;
 top: 0;
 bottom: 0;
 `)]),Bo=O({props:{clsPrefix:{type:String,required:!0},onClick:Function},render(){const{clsPrefix:e}=this;return l("div",{onClick:this.onClick,class:`${e}-layout-toggle-bar`},l("div",{class:`${e}-layout-toggle-bar__top`}),l("div",{class:`${e}-layout-toggle-bar__bottom`}))}}),Eo=O({name:"LayoutToggleButton",props:{clsPrefix:{type:String,required:!0},onClick:Function},render(){const{clsPrefix:e}=this;return l("div",{class:`${e}-layout-toggle-button`,onClick:this.onClick},l(Be,{clsPrefix:e},{default:()=>l(xo,null)}))}}),Oo={position:$e,bordered:Boolean,collapsedWidth:{type:Number,default:48},width:{type:[Number,String],default:272},contentClass:String,contentStyle:{type:[String,Object],default:""},collapseMode:{type:String,default:"transform"},collapsed:{type:Boolean,default:void 0},defaultCollapsed:Boolean,showCollapsedContent:{type:Boolean,default:!0},showTrigger:{type:[Boolean,String],default:!1},nativeScrollbar:{type:Boolean,default:!0},inverted:Boolean,scrollbarProps:Object,triggerClass:String,triggerStyle:[String,Object],collapsedTriggerClass:String,collapsedTriggerStyle:[String,Object],"onUpdate:collapsed":[Function,Array],onUpdateCollapsed:[Function,Array],onAfterEnter:Function,onAfterLeave:Function,onExpand:[Function,Array],onCollapse:[Function,Array],onScroll:Function},$o=O({name:"LayoutSider",props:Object.assign(Object.assign({},q.props),Oo),setup(e){const t=V(Fe),o=E(null),n=E(null),s=E(e.defaultCollapsed),a=ve(ne(e,"collapsed"),s),v=x(()=>ce(a.value?e.collapsedWidth:e.width)),C=x(()=>e.collapseMode!=="transform"?{}:{minWidth:ce(e.width)}),p=x(()=>t?t.siderPlacement:"left");function f(T,I){if(e.nativeScrollbar){const{value:z}=o;z&&(I===void 0?z.scrollTo(T):z.scrollTo(T,I))}else{const{value:z}=n;z&&z.scrollTo(T,I)}}function k(){const{"onUpdate:collapsed":T,onUpdateCollapsed:I,onExpand:z,onCollapse:K}=e,{value:M}=a;I&&F(I,!M),T&&F(T,!M),s.value=!M,M?z&&F(z):K&&F(K)}let N=0,g=0;const P=T=>{var I;const z=T.target;N=z.scrollLeft,g=z.scrollTop,(I=e.onScroll)===null||I===void 0||I.call(e,T)};_e(()=>{if(e.nativeScrollbar){const T=o.value;T&&(T.scrollTop=g,T.scrollLeft=N)}}),Y(Oe,{collapsedRef:a,collapseModeRef:ne(e,"collapseMode")});const{mergedClsPrefixRef:u,inlineThemeDisabled:c}=pe(e),S=q("Layout","-layout-sider",_o,Ee,e,u);function A(T){var I,z;T.propertyName==="max-width"&&(a.value?(I=e.onAfterLeave)===null||I===void 0||I.call(e):(z=e.onAfterEnter)===null||z===void 0||z.call(e))}const X={scrollTo:f},j=x(()=>{const{common:{cubicBezierEaseInOut:T},self:I}=S.value,{siderToggleButtonColor:z,siderToggleButtonBorder:K,siderToggleBarColor:M,siderToggleBarColorHover:ie}=I,B={"--n-bezier":T,"--n-toggle-button-color":z,"--n-toggle-button-border":K,"--n-toggle-bar-color":M,"--n-toggle-bar-color-hover":ie};return e.inverted?(B["--n-color"]=I.siderColorInverted,B["--n-text-color"]=I.textColorInverted,B["--n-border-color"]=I.siderBorderColorInverted,B["--n-toggle-button-icon-color"]=I.siderToggleButtonIconColorInverted,B.__invertScrollbar=I.__invertScrollbar):(B["--n-color"]=I.siderColor,B["--n-text-color"]=I.textColor,B["--n-border-color"]=I.siderBorderColor,B["--n-toggle-button-icon-color"]=I.siderToggleButtonIconColor),B}),$=c?fe("layout-sider",x(()=>e.inverted?"a":"b"),j,e):void 0;return Object.assign({scrollableElRef:o,scrollbarInstRef:n,mergedClsPrefix:u,mergedTheme:S,styleMaxWidth:v,mergedCollapsed:a,scrollContainerStyle:C,siderPlacement:p,handleNativeElScroll:P,handleTransitionend:A,handleTriggerClick:k,inlineThemeDisabled:c,cssVars:j,themeClass:$==null?void 0:$.themeClass,onRender:$==null?void 0:$.onRender},X)},render(){var e;const{mergedClsPrefix:t,mergedCollapsed:o,showTrigger:n}=this;return(e=this.onRender)===null||e===void 0||e.call(this),l("aside",{class:[`${t}-layout-sider`,this.themeClass,`${t}-layout-sider--${this.position}-positioned`,`${t}-layout-sider--${this.siderPlacement}-placement`,this.bordered&&`${t}-layout-sider--bordered`,o&&`${t}-layout-sider--collapsed`,(!o||this.showCollapsedContent)&&`${t}-layout-sider--show-content`],onTransitionend:this.handleTransitionend,style:[this.inlineThemeDisabled?void 0:this.cssVars,{maxWidth:this.styleMaxWidth,width:ce(this.width)}]},this.nativeScrollbar?l("div",{class:[`${t}-layout-sider-scroll-container`,this.contentClass],onScroll:this.handleNativeElScroll,style:[this.scrollContainerStyle,{overflow:"auto"},this.contentStyle],ref:"scrollableElRef"},this.$slots):l(ke,Object.assign({},this.scrollbarProps,{onScroll:this.onScroll,ref:"scrollbarInstRef",style:this.scrollContainerStyle,contentStyle:this.contentStyle,contentClass:this.contentClass,theme:this.mergedTheme.peers.Scrollbar,themeOverrides:this.mergedTheme.peerOverrides.Scrollbar,builtinThemeOverrides:this.inverted&&this.cssVars.__invertScrollbar==="true"?{colorHover:"rgba(255, 255, 255, .4)",color:"rgba(255, 255, 255, .3)"}:void 0}),this.$slots),n?n==="bar"?l(Bo,{clsPrefix:t,class:o?this.collapsedTriggerClass:this.triggerClass,style:o?this.collapsedTriggerStyle:this.triggerStyle,onClick:this.handleTriggerClick}):l(Eo,{clsPrefix:t,class:o?this.collapsedTriggerClass:this.triggerClass,style:o?this.collapsedTriggerStyle:this.triggerStyle,onClick:this.handleTriggerClick}):null,this.bordered?l("div",{class:`${t}-layout-sider__border`}):null)}}),Q=J("n-menu"),Le=J("n-submenu"),be=J("n-menu-item-group"),Re=[w("&::before","background-color: var(--n-item-color-hover);"),d("arrow",`
 color: var(--n-arrow-color-hover);
 `),d("icon",`
 color: var(--n-item-icon-color-hover);
 `),m("menu-item-content-header",`
 color: var(--n-item-text-color-hover);
 `,[w("a",`
 color: var(--n-item-text-color-hover);
 `),d("extra",`
 color: var(--n-item-text-color-hover);
 `)])],Pe=[d("icon",`
 color: var(--n-item-icon-color-hover-horizontal);
 `),m("menu-item-content-header",`
 color: var(--n-item-text-color-hover-horizontal);
 `,[w("a",`
 color: var(--n-item-text-color-hover-horizontal);
 `),d("extra",`
 color: var(--n-item-text-color-hover-horizontal);
 `)])],Fo=w([m("menu",`
 background-color: var(--n-color);
 color: var(--n-item-text-color);
 overflow: hidden;
 transition: background-color .3s var(--n-bezier);
 box-sizing: border-box;
 font-size: var(--n-font-size);
 padding-bottom: 6px;
 `,[H("horizontal",`
 max-width: 100%;
 width: 100%;
 display: flex;
 overflow: hidden;
 padding-bottom: 0;
 `,[m("submenu","margin: 0;"),m("menu-item","margin: 0;"),m("menu-item-content",`
 padding: 0 20px;
 border-bottom: 2px solid #0000;
 `,[w("&::before","display: none;"),H("selected","border-bottom: 2px solid var(--n-border-color-horizontal)")]),m("menu-item-content",[H("selected",[d("icon","color: var(--n-item-icon-color-active-horizontal);"),m("menu-item-content-header",`
 color: var(--n-item-text-color-active-horizontal);
 `,[w("a","color: var(--n-item-text-color-active-horizontal);"),d("extra","color: var(--n-item-text-color-active-horizontal);")])]),H("child-active",`
 border-bottom: 2px solid var(--n-border-color-horizontal);
 `,[m("menu-item-content-header",`
 color: var(--n-item-text-color-child-active-horizontal);
 `,[w("a",`
 color: var(--n-item-text-color-child-active-horizontal);
 `),d("extra",`
 color: var(--n-item-text-color-child-active-horizontal);
 `)]),d("icon",`
 color: var(--n-item-icon-color-child-active-horizontal);
 `)]),Z("disabled",[Z("selected, child-active",[w("&:focus-within",Pe)]),H("selected",[D(null,[d("icon","color: var(--n-item-icon-color-active-hover-horizontal);"),m("menu-item-content-header",`
 color: var(--n-item-text-color-active-hover-horizontal);
 `,[w("a","color: var(--n-item-text-color-active-hover-horizontal);"),d("extra","color: var(--n-item-text-color-active-hover-horizontal);")])])]),H("child-active",[D(null,[d("icon","color: var(--n-item-icon-color-child-active-hover-horizontal);"),m("menu-item-content-header",`
 color: var(--n-item-text-color-child-active-hover-horizontal);
 `,[w("a","color: var(--n-item-text-color-child-active-hover-horizontal);"),d("extra","color: var(--n-item-text-color-child-active-hover-horizontal);")])])]),D("border-bottom: 2px solid var(--n-border-color-horizontal);",Pe)]),m("menu-item-content-header",[w("a","color: var(--n-item-text-color-horizontal);")])])]),Z("responsive",[m("menu-item-content-header",`
 overflow: hidden;
 text-overflow: ellipsis;
 `)]),H("collapsed",[m("menu-item-content",[H("selected",[w("&::before",`
 background-color: var(--n-item-color-active-collapsed) !important;
 `)]),m("menu-item-content-header","opacity: 0;"),d("arrow","opacity: 0;"),d("icon","color: var(--n-item-icon-color-collapsed);")])]),m("menu-item",`
 height: var(--n-item-height);
 margin-top: 6px;
 position: relative;
 `),m("menu-item-content",`
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
 `),H("disabled",`
 opacity: .45;
 cursor: not-allowed;
 `),H("collapsed",[d("arrow","transform: rotate(0);")]),H("selected",[w("&::before","background-color: var(--n-item-color-active);"),d("arrow","color: var(--n-arrow-color-active);"),d("icon","color: var(--n-item-icon-color-active);"),m("menu-item-content-header",`
 color: var(--n-item-text-color-active);
 `,[w("a","color: var(--n-item-text-color-active);"),d("extra","color: var(--n-item-text-color-active);")])]),H("child-active",[m("menu-item-content-header",`
 color: var(--n-item-text-color-child-active);
 `,[w("a",`
 color: var(--n-item-text-color-child-active);
 `),d("extra",`
 color: var(--n-item-text-color-child-active);
 `)]),d("arrow",`
 color: var(--n-arrow-color-child-active);
 `),d("icon",`
 color: var(--n-item-icon-color-child-active);
 `)]),Z("disabled",[Z("selected, child-active",[w("&:focus-within",Re)]),H("selected",[D(null,[d("arrow","color: var(--n-arrow-color-active-hover);"),d("icon","color: var(--n-item-icon-color-active-hover);"),m("menu-item-content-header",`
 color: var(--n-item-text-color-active-hover);
 `,[w("a","color: var(--n-item-text-color-active-hover);"),d("extra","color: var(--n-item-text-color-active-hover);")])])]),H("child-active",[D(null,[d("arrow","color: var(--n-arrow-color-child-active-hover);"),d("icon","color: var(--n-item-icon-color-child-active-hover);"),m("menu-item-content-header",`
 color: var(--n-item-text-color-child-active-hover);
 `,[w("a","color: var(--n-item-text-color-child-active-hover);"),d("extra","color: var(--n-item-text-color-child-active-hover);")])])]),H("selected",[D(null,[w("&::before","background-color: var(--n-item-color-active-hover);")])]),D(null,Re)]),d("icon",`
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
 `),m("menu-item-content-header",`
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
 `)])]),m("submenu",`
 cursor: pointer;
 position: relative;
 margin-top: 6px;
 `,[m("menu-item-content",`
 height: var(--n-item-height);
 `),m("submenu-children",`
 overflow: hidden;
 padding: 0;
 `,[to({duration:".2s"})])]),m("menu-item-group",[m("menu-item-group-title",`
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
 `)])]),m("menu-tooltip",[w("a",`
 color: inherit;
 text-decoration: none;
 `)]),m("menu-divider",`
 transition: background-color .3s var(--n-bezier);
 background-color: var(--n-divider-color);
 height: 1px;
 margin: 6px 18px;
 `)]);function D(e,t){return[H("hover",e,t),w("&:hover",e,t)]}const je=O({name:"MenuOptionContent",props:{collapsed:Boolean,disabled:Boolean,title:[String,Function],icon:Function,extra:[String,Function],showArrow:Boolean,childActive:Boolean,hover:Boolean,paddingLeft:Number,selected:Boolean,maxIconSize:{type:Number,required:!0},activeIconSize:{type:Number,required:!0},iconMarginRight:{type:Number,required:!0},clsPrefix:{type:String,required:!0},onClick:Function,tmNode:{type:Object,required:!0},isEllipsisPlaceholder:Boolean},setup(e){const{props:t}=V(Q);return{menuProps:t,style:x(()=>{const{paddingLeft:o}=e;return{paddingLeft:o&&`${o}px`}}),iconStyle:x(()=>{const{maxIconSize:o,activeIconSize:n,iconMarginRight:s}=e;return{width:`${o}px`,height:`${o}px`,fontSize:`${n}px`,marginRight:`${s}px`}})}},render(){const{clsPrefix:e,tmNode:t,menuProps:{renderIcon:o,renderLabel:n,renderExtra:s,expandIcon:a}}=this,v=o?o(t.rawNode):G(this.icon);return l("div",{onClick:C=>{var p;(p=this.onClick)===null||p===void 0||p.call(this,C)},role:"none",class:[`${e}-menu-item-content`,{[`${e}-menu-item-content--selected`]:this.selected,[`${e}-menu-item-content--collapsed`]:this.collapsed,[`${e}-menu-item-content--child-active`]:this.childActive,[`${e}-menu-item-content--disabled`]:this.disabled,[`${e}-menu-item-content--hover`]:this.hover}],style:this.style},v&&l("div",{class:`${e}-menu-item-content__icon`,style:this.iconStyle,role:"none"},[v]),l("div",{class:`${e}-menu-item-content-header`,role:"none"},this.isEllipsisPlaceholder?this.title:n?n(t.rawNode):G(this.title),this.extra||s?l("span",{class:`${e}-menu-item-content-header__extra`}," ",s?s(t.rawNode):G(this.extra)):null),this.showArrow?l(Be,{ariaHidden:!0,class:`${e}-menu-item-content__arrow`,clsPrefix:e},{default:()=>a?a(t.rawNode):l(So,null)}):null)}}),re=8;function Ce(e){const t=V(Q),{props:o,mergedCollapsedRef:n}=t,s=V(Le,null),a=V(be,null),v=x(()=>o.mode==="horizontal"),C=x(()=>v.value?o.dropdownPlacement:"tmNodes"in e?"right-start":"right"),p=x(()=>{var g;return Math.max((g=o.collapsedIconSize)!==null&&g!==void 0?g:o.iconSize,o.iconSize)}),f=x(()=>{var g;return!v.value&&e.root&&n.value&&(g=o.collapsedIconSize)!==null&&g!==void 0?g:o.iconSize}),k=x(()=>{if(v.value)return;const{collapsedWidth:g,indent:P,rootIndent:u}=o,{root:c,isGroup:S}=e,A=u===void 0?P:u;return c?n.value?g/2-p.value/2:A:a&&typeof a.paddingLeftRef.value=="number"?P/2+a.paddingLeftRef.value:s&&typeof s.paddingLeftRef.value=="number"?(S?P/2:P)+s.paddingLeftRef.value:0}),N=x(()=>{const{collapsedWidth:g,indent:P,rootIndent:u}=o,{value:c}=p,{root:S}=e;return v.value||!S||!n.value?re:(u===void 0?P:u)+c+re-(g+c)/2});return{dropdownPlacement:C,activeIconSize:f,maxIconSize:p,paddingLeft:k,iconMarginRight:N,NMenu:t,NSubmenu:s,NMenuOptionGroup:a}}const xe={internalKey:{type:[String,Number],required:!0},root:Boolean,isGroup:Boolean,level:{type:Number,required:!0},title:[String,Function],extra:[String,Function]},Mo=O({name:"MenuDivider",setup(){const e=V(Q),{mergedClsPrefixRef:t,isHorizontalRef:o}=e;return()=>o.value?null:l("div",{class:`${t.value}-menu-divider`})}}),Ke=Object.assign(Object.assign({},xe),{tmNode:{type:Object,required:!0},disabled:Boolean,icon:Function,onClick:Function}),Lo=ge(Ke),jo=O({name:"MenuOption",props:Ke,setup(e){const t=Ce(e),{NSubmenu:o,NMenu:n,NMenuOptionGroup:s}=t,{props:a,mergedClsPrefixRef:v,mergedCollapsedRef:C}=n,p=o?o.mergedDisabledRef:s?s.mergedDisabledRef:{value:!1},f=x(()=>p.value||e.disabled);function k(g){const{onClick:P}=e;P&&P(g)}function N(g){f.value||(n.doSelect(e.internalKey,e.tmNode.rawNode),k(g))}return{mergedClsPrefix:v,dropdownPlacement:t.dropdownPlacement,paddingLeft:t.paddingLeft,iconMarginRight:t.iconMarginRight,maxIconSize:t.maxIconSize,activeIconSize:t.activeIconSize,mergedTheme:n.mergedThemeRef,menuProps:a,dropdownEnabled:ue(()=>e.root&&C.value&&a.mode!=="horizontal"&&!f.value),selected:ue(()=>n.mergedValueRef.value===e.internalKey),mergedDisabled:f,handleClick:N}},render(){const{mergedClsPrefix:e,mergedTheme:t,tmNode:o,menuProps:{renderLabel:n,nodeProps:s}}=this,a=s==null?void 0:s(o.rawNode);return l("div",Object.assign({},a,{role:"menuitem",class:[`${e}-menu-item`,a==null?void 0:a.class]}),l(go,{theme:t.peers.Tooltip,themeOverrides:t.peerOverrides.Tooltip,trigger:"hover",placement:this.dropdownPlacement,disabled:!this.dropdownEnabled||this.title===void 0,internalExtraClass:["menu-tooltip"]},{default:()=>n?n(o.rawNode):G(this.title),trigger:()=>l(je,{tmNode:o,clsPrefix:e,paddingLeft:this.paddingLeft,iconMarginRight:this.iconMarginRight,maxIconSize:this.maxIconSize,activeIconSize:this.activeIconSize,selected:this.selected,title:this.title,extra:this.extra,disabled:this.mergedDisabled,icon:this.icon,onClick:this.handleClick})}))}}),Ve=Object.assign(Object.assign({},xe),{tmNode:{type:Object,required:!0},tmNodes:{type:Array,required:!0}}),Ko=ge(Ve),Vo=O({name:"MenuOptionGroup",props:Ve,setup(e){const t=Ce(e),{NSubmenu:o}=t,n=x(()=>o!=null&&o.mergedDisabledRef.value?!0:e.tmNode.disabled);Y(be,{paddingLeftRef:t.paddingLeft,mergedDisabledRef:n});const{mergedClsPrefixRef:s,props:a}=V(Q);return function(){const{value:v}=s,C=t.paddingLeft.value,{nodeProps:p}=a,f=p==null?void 0:p(e.tmNode.rawNode);return l("div",{class:`${v}-menu-item-group`,role:"group"},l("div",Object.assign({},f,{class:[`${v}-menu-item-group-title`,f==null?void 0:f.class],style:[(f==null?void 0:f.style)||"",C!==void 0?`padding-left: ${C}px;`:""]}),G(e.title),e.extra?l(ro,null," ",G(e.extra)):null),l("div",null,e.tmNodes.map(k=>ye(k,a))))}}});function me(e){return e.type==="divider"||e.type==="render"}function Do(e){return e.type==="divider"}function ye(e,t){const{rawNode:o}=e,{show:n}=o;if(n===!1)return null;if(me(o))return Do(o)?l(Mo,Object.assign({key:e.key},o.props)):null;const{labelField:s}=t,{key:a,level:v,isGroup:C}=e,p=Object.assign(Object.assign({},o),{title:o.title||o[s],extra:o.titleExtra||o.extra,key:a,internalKey:a,level:v,root:v===0,isGroup:C});return e.children?e.isGroup?l(Vo,ae(p,Ko,{tmNode:e,tmNodes:e.children,key:a})):l(he,ae(p,Uo,{key:a,rawNodes:o[t.childrenField],tmNodes:e.children,tmNode:e})):l(jo,ae(p,Lo,{key:a,tmNode:e}))}const De=Object.assign(Object.assign({},xe),{rawNodes:{type:Array,default:()=>[]},tmNodes:{type:Array,default:()=>[]},tmNode:{type:Object,required:!0},disabled:Boolean,icon:Function,onClick:Function,domId:String,virtualChildActive:{type:Boolean,default:void 0},isEllipsisPlaceholder:Boolean}),Uo=ge(De),he=O({name:"Submenu",props:De,setup(e){const t=Ce(e),{NMenu:o,NSubmenu:n}=t,{props:s,mergedCollapsedRef:a,mergedThemeRef:v}=o,C=x(()=>{const{disabled:g}=e;return n!=null&&n.mergedDisabledRef.value||s.disabled?!0:g}),p=E(!1);Y(Le,{paddingLeftRef:t.paddingLeft,mergedDisabledRef:C}),Y(be,null);function f(){const{onClick:g}=e;g&&g()}function k(){C.value||(a.value||o.toggleExpand(e.internalKey),f())}function N(g){p.value=g}return{menuProps:s,mergedTheme:v,doSelect:o.doSelect,inverted:o.invertedRef,isHorizontal:o.isHorizontalRef,mergedClsPrefix:o.mergedClsPrefixRef,maxIconSize:t.maxIconSize,activeIconSize:t.activeIconSize,iconMarginRight:t.iconMarginRight,dropdownPlacement:t.dropdownPlacement,dropdownShow:p,paddingLeft:t.paddingLeft,mergedDisabled:C,mergedValue:o.mergedValueRef,childActive:ue(()=>{var g;return(g=e.virtualChildActive)!==null&&g!==void 0?g:o.activePathRef.value.includes(e.internalKey)}),collapsed:x(()=>s.mode==="horizontal"?!1:a.value?!0:!o.mergedExpandedKeysRef.value.includes(e.internalKey)),dropdownEnabled:x(()=>!C.value&&(s.mode==="horizontal"||a.value)),handlePopoverShowChange:N,handleClick:k}},render(){var e;const{mergedClsPrefix:t,menuProps:{renderIcon:o,renderLabel:n}}=this,s=()=>{const{isHorizontal:v,paddingLeft:C,collapsed:p,mergedDisabled:f,maxIconSize:k,activeIconSize:N,title:g,childActive:P,icon:u,handleClick:c,menuProps:{nodeProps:S},dropdownShow:A,iconMarginRight:X,tmNode:j,mergedClsPrefix:$,isEllipsisPlaceholder:T,extra:I}=this,z=S==null?void 0:S(j.rawNode);return l("div",Object.assign({},z,{class:[`${$}-menu-item`,z==null?void 0:z.class],role:"menuitem"}),l(je,{tmNode:j,paddingLeft:C,collapsed:p,disabled:f,iconMarginRight:X,maxIconSize:k,activeIconSize:N,title:g,extra:I,showArrow:!v,childActive:P,clsPrefix:$,icon:u,hover:A,onClick:c,isEllipsisPlaceholder:T}))},a=()=>l(no,null,{default:()=>{const{tmNodes:v,collapsed:C}=this;return C?null:l("div",{class:`${t}-submenu-children`,role:"menu"},v.map(p=>ye(p,this.menuProps)))}});return this.root?l(Co,Object.assign({size:"large",trigger:"hover"},(e=this.menuProps)===null||e===void 0?void 0:e.dropdownProps,{themeOverrides:this.mergedTheme.peerOverrides.Dropdown,theme:this.mergedTheme.peers.Dropdown,builtinThemeOverrides:{fontSizeLarge:"14px",optionIconSizeLarge:"18px"},value:this.mergedValue,disabled:!this.dropdownEnabled,placement:this.dropdownPlacement,keyField:this.menuProps.keyField,labelField:this.menuProps.labelField,childrenField:this.menuProps.childrenField,onUpdateShow:this.handlePopoverShowChange,options:this.rawNodes,onSelect:this.doSelect,inverted:this.inverted,renderIcon:o,renderLabel:n}),{default:()=>l("div",{class:`${t}-submenu`,role:"menu","aria-expanded":!this.collapsed,id:this.domId},s(),this.isHorizontal?null:a())}):l("div",{class:`${t}-submenu`,role:"menu","aria-expanded":!this.collapsed,id:this.domId},s(),a())}}),Wo=Object.assign(Object.assign({},q.props),{options:{type:Array,default:()=>[]},collapsed:{type:Boolean,default:void 0},collapsedWidth:{type:Number,default:48},iconSize:{type:Number,default:20},collapsedIconSize:{type:Number,default:24},rootIndent:Number,indent:{type:Number,default:32},labelField:{type:String,default:"label"},keyField:{type:String,default:"key"},childrenField:{type:String,default:"children"},disabledField:{type:String,default:"disabled"},defaultExpandAll:Boolean,defaultExpandedKeys:Array,expandedKeys:Array,value:[String,Number],defaultValue:{type:[String,Number],default:null},mode:{type:String,default:"vertical"},watchProps:{type:Array,default:void 0},disabled:Boolean,show:{type:Boolean,default:!0},inverted:Boolean,"onUpdate:expandedKeys":[Function,Array],onUpdateExpandedKeys:[Function,Array],onUpdateValue:[Function,Array],"onUpdate:value":[Function,Array],expandIcon:Function,renderIcon:Function,renderLabel:Function,renderExtra:Function,dropdownProps:Object,accordion:Boolean,nodeProps:Function,dropdownPlacement:{type:String,default:"bottom"},responsive:Boolean,items:Array,onOpenNamesChange:[Function,Array],onSelect:[Function,Array],onExpandedNamesChange:[Function,Array],expandedNames:Array,defaultExpandedNames:Array}),Go=O({name:"Menu",inheritAttrs:!1,props:Wo,setup(e){const{mergedClsPrefixRef:t,inlineThemeDisabled:o}=pe(e),n=q("Menu","-menu",Fo,Po,e,t),s=V(Oe,null),a=x(()=>{var h;const{collapsed:y}=e;if(y!==void 0)return y;if(s){const{collapseModeRef:r,collapsedRef:b}=s;if(r.value==="width")return(h=b.value)!==null&&h!==void 0?h:!1}return!1}),v=x(()=>{const{keyField:h,childrenField:y,disabledField:r}=e;return de(e.items||e.options,{getIgnored(b){return me(b)},getChildren(b){return b[y]},getDisabled(b){return b[r]},getKey(b){var R;return(R=b[h])!==null&&R!==void 0?R:b.name}})}),C=x(()=>new Set(v.value.treeNodes.map(h=>h.key))),{watchProps:p}=e,f=E(null);p!=null&&p.includes("defaultValue")?we(()=>{f.value=e.defaultValue}):f.value=e.defaultValue;const k=ne(e,"value"),N=ve(k,f),g=E([]),P=()=>{g.value=e.defaultExpandAll?v.value.getNonLeafKeys():e.defaultExpandedNames||e.defaultExpandedKeys||v.value.getPath(N.value,{includeSelf:!1}).keyPath};p!=null&&p.includes("defaultExpandedKeys")?we(P):P();const u=Io(e,["expandedNames","expandedKeys"]),c=ve(u,g),S=x(()=>v.value.treeNodes),A=x(()=>v.value.getPath(N.value).keyPath);Y(Q,{props:e,mergedCollapsedRef:a,mergedThemeRef:n,mergedValueRef:N,mergedExpandedKeysRef:c,activePathRef:A,mergedClsPrefixRef:t,isHorizontalRef:x(()=>e.mode==="horizontal"),invertedRef:ne(e,"inverted"),doSelect:X,toggleExpand:$});function X(h,y){const{"onUpdate:value":r,onUpdateValue:b,onSelect:R}=e;b&&F(b,h,y),r&&F(r,h,y),R&&F(R,h,y),f.value=h}function j(h){const{"onUpdate:expandedKeys":y,onUpdateExpandedKeys:r,onExpandedNamesChange:b,onOpenNamesChange:R}=e;y&&F(y,h),r&&F(r,h),b&&F(b,h),R&&F(R,h),g.value=h}function $(h){const y=Array.from(c.value),r=y.findIndex(b=>b===h);if(~r)y.splice(r,1);else{if(e.accordion&&C.value.has(h)){const b=y.findIndex(R=>C.value.has(R));b>-1&&y.splice(b,1)}y.push(h)}j(y)}const T=h=>{const y=v.value.getPath(h??N.value,{includeSelf:!1}).keyPath;if(!y.length)return;const r=Array.from(c.value),b=new Set([...r,...y]);e.accordion&&C.value.forEach(R=>{b.has(R)&&!y.includes(R)&&b.delete(R)}),j(Array.from(b))},I=x(()=>{const{inverted:h}=e,{common:{cubicBezierEaseInOut:y},self:r}=n.value,{borderRadius:b,borderColorHorizontal:R,fontSize:Je,itemHeight:Qe,dividerColor:eo}=r,i={"--n-divider-color":eo,"--n-bezier":y,"--n-font-size":Je,"--n-border-color-horizontal":R,"--n-border-radius":b,"--n-item-height":Qe};return h?(i["--n-group-text-color"]=r.groupTextColorInverted,i["--n-color"]=r.colorInverted,i["--n-item-text-color"]=r.itemTextColorInverted,i["--n-item-text-color-hover"]=r.itemTextColorHoverInverted,i["--n-item-text-color-active"]=r.itemTextColorActiveInverted,i["--n-item-text-color-child-active"]=r.itemTextColorChildActiveInverted,i["--n-item-text-color-child-active-hover"]=r.itemTextColorChildActiveInverted,i["--n-item-text-color-active-hover"]=r.itemTextColorActiveHoverInverted,i["--n-item-icon-color"]=r.itemIconColorInverted,i["--n-item-icon-color-hover"]=r.itemIconColorHoverInverted,i["--n-item-icon-color-active"]=r.itemIconColorActiveInverted,i["--n-item-icon-color-active-hover"]=r.itemIconColorActiveHoverInverted,i["--n-item-icon-color-child-active"]=r.itemIconColorChildActiveInverted,i["--n-item-icon-color-child-active-hover"]=r.itemIconColorChildActiveHoverInverted,i["--n-item-icon-color-collapsed"]=r.itemIconColorCollapsedInverted,i["--n-item-text-color-horizontal"]=r.itemTextColorHorizontalInverted,i["--n-item-text-color-hover-horizontal"]=r.itemTextColorHoverHorizontalInverted,i["--n-item-text-color-active-horizontal"]=r.itemTextColorActiveHorizontalInverted,i["--n-item-text-color-child-active-horizontal"]=r.itemTextColorChildActiveHorizontalInverted,i["--n-item-text-color-child-active-hover-horizontal"]=r.itemTextColorChildActiveHoverHorizontalInverted,i["--n-item-text-color-active-hover-horizontal"]=r.itemTextColorActiveHoverHorizontalInverted,i["--n-item-icon-color-horizontal"]=r.itemIconColorHorizontalInverted,i["--n-item-icon-color-hover-horizontal"]=r.itemIconColorHoverHorizontalInverted,i["--n-item-icon-color-active-horizontal"]=r.itemIconColorActiveHorizontalInverted,i["--n-item-icon-color-active-hover-horizontal"]=r.itemIconColorActiveHoverHorizontalInverted,i["--n-item-icon-color-child-active-horizontal"]=r.itemIconColorChildActiveHorizontalInverted,i["--n-item-icon-color-child-active-hover-horizontal"]=r.itemIconColorChildActiveHoverHorizontalInverted,i["--n-arrow-color"]=r.arrowColorInverted,i["--n-arrow-color-hover"]=r.arrowColorHoverInverted,i["--n-arrow-color-active"]=r.arrowColorActiveInverted,i["--n-arrow-color-active-hover"]=r.arrowColorActiveHoverInverted,i["--n-arrow-color-child-active"]=r.arrowColorChildActiveInverted,i["--n-arrow-color-child-active-hover"]=r.arrowColorChildActiveHoverInverted,i["--n-item-color-hover"]=r.itemColorHoverInverted,i["--n-item-color-active"]=r.itemColorActiveInverted,i["--n-item-color-active-hover"]=r.itemColorActiveHoverInverted,i["--n-item-color-active-collapsed"]=r.itemColorActiveCollapsedInverted):(i["--n-group-text-color"]=r.groupTextColor,i["--n-color"]=r.color,i["--n-item-text-color"]=r.itemTextColor,i["--n-item-text-color-hover"]=r.itemTextColorHover,i["--n-item-text-color-active"]=r.itemTextColorActive,i["--n-item-text-color-child-active"]=r.itemTextColorChildActive,i["--n-item-text-color-child-active-hover"]=r.itemTextColorChildActiveHover,i["--n-item-text-color-active-hover"]=r.itemTextColorActiveHover,i["--n-item-icon-color"]=r.itemIconColor,i["--n-item-icon-color-hover"]=r.itemIconColorHover,i["--n-item-icon-color-active"]=r.itemIconColorActive,i["--n-item-icon-color-active-hover"]=r.itemIconColorActiveHover,i["--n-item-icon-color-child-active"]=r.itemIconColorChildActive,i["--n-item-icon-color-child-active-hover"]=r.itemIconColorChildActiveHover,i["--n-item-icon-color-collapsed"]=r.itemIconColorCollapsed,i["--n-item-text-color-horizontal"]=r.itemTextColorHorizontal,i["--n-item-text-color-hover-horizontal"]=r.itemTextColorHoverHorizontal,i["--n-item-text-color-active-horizontal"]=r.itemTextColorActiveHorizontal,i["--n-item-text-color-child-active-horizontal"]=r.itemTextColorChildActiveHorizontal,i["--n-item-text-color-child-active-hover-horizontal"]=r.itemTextColorChildActiveHoverHorizontal,i["--n-item-text-color-active-hover-horizontal"]=r.itemTextColorActiveHoverHorizontal,i["--n-item-icon-color-horizontal"]=r.itemIconColorHorizontal,i["--n-item-icon-color-hover-horizontal"]=r.itemIconColorHoverHorizontal,i["--n-item-icon-color-active-horizontal"]=r.itemIconColorActiveHorizontal,i["--n-item-icon-color-active-hover-horizontal"]=r.itemIconColorActiveHoverHorizontal,i["--n-item-icon-color-child-active-horizontal"]=r.itemIconColorChildActiveHorizontal,i["--n-item-icon-color-child-active-hover-horizontal"]=r.itemIconColorChildActiveHoverHorizontal,i["--n-arrow-color"]=r.arrowColor,i["--n-arrow-color-hover"]=r.arrowColorHover,i["--n-arrow-color-active"]=r.arrowColorActive,i["--n-arrow-color-active-hover"]=r.arrowColorActiveHover,i["--n-arrow-color-child-active"]=r.arrowColorChildActive,i["--n-arrow-color-child-active-hover"]=r.arrowColorChildActiveHover,i["--n-item-color-hover"]=r.itemColorHover,i["--n-item-color-active"]=r.itemColorActive,i["--n-item-color-active-hover"]=r.itemColorActiveHover,i["--n-item-color-active-collapsed"]=r.itemColorActiveCollapsed),i}),z=o?fe("menu",x(()=>e.inverted?"a":"b"),I,e):void 0,K=lo(),M=E(null),ie=E(null);let B=!0;const Ie=()=>{var h;B?B=!1:(h=M.value)===null||h===void 0||h.sync({showAllItemsBeforeCalculate:!0})};function Ue(){return document.getElementById(K)}const ee=E(-1);function We(h){ee.value=e.options.length-h}function Ge(h){h||(ee.value=-1)}const qe=x(()=>{const h=ee.value;return{children:h===-1?[]:e.options.slice(h)}}),Ye=x(()=>{const{childrenField:h,disabledField:y,keyField:r}=e;return de([qe.value],{getIgnored(b){return me(b)},getChildren(b){return b[h]},getDisabled(b){return b[y]},getKey(b){var R;return(R=b[r])!==null&&R!==void 0?R:b.name}})}),Xe=x(()=>de([{}]).treeNodes[0]);function Ze(){var h;if(ee.value===-1)return l(he,{root:!0,level:0,key:"__ellpisisGroupPlaceholder__",internalKey:"__ellpisisGroupPlaceholder__",title:"···",tmNode:Xe.value,domId:K,isEllipsisPlaceholder:!0});const y=Ye.value.treeNodes[0],r=A.value,b=!!(!((h=y.children)===null||h===void 0)&&h.some(R=>r.includes(R.key)));return l(he,{level:0,root:!0,key:"__ellpisisGroup__",internalKey:"__ellpisisGroup__",title:"···",virtualChildActive:b,tmNode:y,domId:K,rawNodes:y.rawNode.children||[],tmNodes:y.children||[],isEllipsisPlaceholder:!0})}return{mergedClsPrefix:t,controlledExpandedKeys:u,uncontrolledExpanededKeys:g,mergedExpandedKeys:c,uncontrolledValue:f,mergedValue:N,activePath:A,tmNodes:S,mergedTheme:n,mergedCollapsed:a,cssVars:o?void 0:I,themeClass:z==null?void 0:z.themeClass,overflowRef:M,counterRef:ie,updateCounter:()=>{},onResize:Ie,onUpdateOverflow:Ge,onUpdateCount:We,renderCounter:Ze,getCounter:Ue,onRender:z==null?void 0:z.onRender,showOption:T,deriveResponsiveState:Ie}},render(){const{mergedClsPrefix:e,mode:t,themeClass:o,onRender:n}=this;n==null||n();const s=()=>this.tmNodes.map(p=>ye(p,this.$props)),v=t==="horizontal"&&this.responsive,C=()=>l("div",ao(this.$attrs,{role:t==="horizontal"?"menubar":"menu",class:[`${e}-menu`,o,`${e}-menu--${t}`,v&&`${e}-menu--responsive`,this.mergedCollapsed&&`${e}-menu--collapsed`],style:this.cssVars}),v?l(yo,{ref:"overflowRef",onUpdateOverflow:this.onUpdateOverflow,getCounter:this.getCounter,onUpdateCount:this.onUpdateCount,updateCounter:this.updateCounter,style:{width:"100%",display:"flex",overflow:"hidden"}},{default:s,counter:this.renderCounter}):s());return v?l(io,{onResize:this.onResize},{default:C}):C()}}),qo={key:0,class:"brand-copy"},Yo={key:0,class:"brand-panel"},Xo={class:"brand-panel__value"},Zo={class:"brand-panel__meta"},Jo={class:"topbar"},Qo={class:"topbar-title-row"},et={class:"topbar-title"},ot={class:"topbar-date"},tt={class:"content-shell"},rt=O({__name:"MainLayout",setup(e){const t=E(!1),o=E(!1),n=mo(),s=ho(),a=x(()=>o.value?72:252);function v(){const u=window.innerWidth<900;o.value=u,u&&(t.value=!0)}so(()=>{v(),window.addEventListener("resize",v)}),co(()=>{window.removeEventListener("resize",v)});const C=x(()=>{const u=s.path;return u.startsWith("/dashboard")?"dashboard":u.startsWith("/applications")?"applications":u.startsWith("/recording")?"recording":u.startsWith("/testcases")?"testcases":u==="/replay"?"replay":u.startsWith("/replay/history")||u.startsWith("/results")?"replay-history":u.startsWith("/suites")?"suites":u.startsWith("/schedule")?"schedule":u.startsWith("/compare")?"compare":u.startsWith("/ci")?"ci":u.startsWith("/settings")?"settings":u.startsWith("/users")?"users":"applications"}),p={dashboard:"数据总览",applications:"应用管理",recording:"录制中心",testcases:"测试用例库",replay:"发起回放","replay-history":"回放历史",suites:"回放套件",schedule:"定时回放",compare:"双环境对比",ci:"CI 集成",settings:"平台指引",users:"用户管理"},f=x(()=>p[C.value]||"AREX Recorder"),k=x(()=>{const u=new Date,c=["周日","周一","周二","周三","周四","周五","周六"],S=String(u.getMonth()+1).padStart(2,"0"),A=String(u.getDate()).padStart(2,"0");return`${S}/${A} ${c[u.getDay()]}`}),N=[{label:"数据总览",key:"dashboard",icon:()=>l("span","概")},{label:"应用管理",key:"applications",icon:()=>l("span","应")},{label:"录制中心",key:"recording",icon:()=>l("span","录")},{label:"测试用例库",key:"testcases",icon:()=>l("span","例")},{label:"发起回放",key:"replay",icon:()=>l("span","回")},{label:"回放历史",key:"replay-history",icon:()=>l("span","史")},{label:"回放套件",key:"suites",icon:()=>l("span","套")},{label:"定时回放",key:"schedule",icon:()=>l("span","定")},{label:"双环境对比",key:"compare",icon:()=>l("span","比")},{label:"CI 集成",key:"ci",icon:()=>l("span","CI")},{label:"用户管理",key:"users",icon:()=>l("span","用")},{label:"平台指引",key:"settings",icon:()=>l("span","指")}],g=x(()=>N.filter(u=>!["compare","ci","users","settings"].includes(String(u.key))));function P(u){if(u==="replay-history"){n.push("/replay/history");return}n.push(`/${u}`)}return(u,c)=>{const S=po("router-view");return te(),Se(L(He),{class:"app-shell","has-sider":""},{default:U(()=>[c[9]||(c[9]=_("div",{class:"shell-bg shell-bg--left"},null,-1)),c[10]||(c[10]=_("div",{class:"shell-bg shell-bg--right"},null,-1)),W(L($o),{class:"app-sider","collapse-mode":"width","collapsed-width":72,width:a.value,collapsed:t.value,onCollapse:c[1]||(c[1]=A=>t.value=!0),onExpand:c[2]||(c[2]=A=>t.value=!1)},{default:U(()=>[_("div",{class:"brand",onClick:c[0]||(c[0]=A=>t.value=!t.value)},[c[5]||(c[5]=_("div",{class:"brand-mark"},"AR",-1)),t.value?se("",!0):(te(),Ae("div",qo,[...c[4]||(c[4]=[_("div",{class:"brand-title"},"AREX Recorder",-1),_("div",{class:"brand-subtitle"},"录制、回放、对比",-1)])]))]),t.value?se("",!0):(te(),Ae("div",Yo,[c[6]||(c[6]=_("div",{class:"brand-panel__label"},"当前页面",-1)),_("div",Xo,oe(f.value),1),_("div",Zo,oe(k.value),1)])),W(L(Go),{class:"side-menu",collapsed:t.value,"collapsed-width":72,"collapsed-icon-size":20,options:g.value,value:C.value,"onUpdate:value":P},null,8,["collapsed","options","value"])]),_:1},8,["width","collapsed"]),W(L(He),{class:"app-main"},{default:U(()=>[_("header",Jo,[_("div",null,[_("div",Qo,[_("h1",et,oe(f.value),1)]),c[7]||(c[7]=_("div",{class:"topbar-subtitle"},"面向录制同步、回放验证和双环境差异检查的统一平台",-1))]),W(L(zo),{align:"center",size:"small"},{default:U(()=>[_("div",ot,oe(k.value),1),L(s).path!=="/dashboard"?(te(),Se(L(uo),{key:0,quaternary:"",size:"small",onClick:c[3]||(c[3]=A=>L(n).push("/dashboard"))},{default:U(()=>[...c[8]||(c[8]=[vo("总览",-1)])]),_:1})):se("",!0)]),_:1})]),W(L(ko),{class:"app-content","content-style":"padding: 0 24px 24px;"},{default:U(()=>[_("main",tt,[W(S)])]),_:1})]),_:1})]),_:1})}}}),dt=wo(rt,[["__scopeId","data-v-e450c4b0"]]);export{dt as default};
