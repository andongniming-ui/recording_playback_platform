import{d as B,h as d,c as Ne,s as eo,a as ke,b as Ie,e as le,f as J,g as u,i as w,S as _e,u as te,j as U,k as Be,l as re,m as b,r as O,p as W,n as s,o as I,N as Oe,q as D,t as $,v as oe,w as X,x as oo,y as q,z as he,A as de,F as to,B as ie,C as ro,V as no,D as ze,E as lo,G as io,H as ao,I as V,J as F,K as M,L as we,M as Se,O as Ae,P as He,Q as co,R as so,T as uo,U as vo,W as ae}from"./index-DNXRX2vX.js";import{u as mo}from"./user-ChhqNL5w.js";import{d as ho,t as fo,C as po,N as go,a as bo,V as Co,u as xo,c as ce,b as yo}from"./Space-yGN031He.js";import{f as se,u as ue}from"./get-h59NEGKw.js";import{N as Io}from"./text-bTMGGu_L.js";import"./light-q7xaMC5L.js";const zo=B({name:"ChevronDownFilled",render(){return d("svg",{viewBox:"0 0 16 16",fill:"none",xmlns:"http://www.w3.org/2000/svg"},d("path",{d:"M3.20041 5.73966C3.48226 5.43613 3.95681 5.41856 4.26034 5.70041L8 9.22652L11.7397 5.70041C12.0432 5.41856 12.5177 5.43613 12.7996 5.73966C13.0815 6.0432 13.0639 6.51775 12.7603 6.7996L8.51034 10.7996C8.22258 11.0668 7.77743 11.0668 7.48967 10.7996L3.23966 6.7996C2.93613 6.51775 2.91856 6.0432 3.20041 5.73966Z",fill:"currentColor"}))}});function wo(e){const{baseColor:t,textColor2:o,bodyColor:n,cardColor:a,dividerColor:i,actionColor:v,scrollbarColor:f,scrollbarColorHover:c,invertedColor:p}=e;return{textColor:o,textColorInverted:"#FFF",color:n,colorEmbedded:v,headerColor:a,headerColorInverted:p,footerColor:v,footerColorInverted:p,headerBorderColor:i,headerBorderColorInverted:p,footerBorderColor:i,footerBorderColorInverted:p,siderBorderColor:i,siderBorderColorInverted:p,siderColor:a,siderColorInverted:p,siderToggleButtonBorder:`1px solid ${i}`,siderToggleButtonColor:t,siderToggleButtonIconColor:o,siderToggleButtonIconColorInverted:o,siderToggleBarColor:Ie(n,f),siderToggleBarColorHover:Ie(n,c),__invertScrollbar:"true"}}const fe=Ne({name:"Layout",common:ke,peers:{Scrollbar:eo},self:wo});function So(e,t,o,n){return{itemColorHoverInverted:"#0000",itemColorActiveInverted:t,itemColorActiveHoverInverted:t,itemColorActiveCollapsedInverted:t,itemTextColorInverted:e,itemTextColorHoverInverted:o,itemTextColorChildActiveInverted:o,itemTextColorChildActiveHoverInverted:o,itemTextColorActiveInverted:o,itemTextColorActiveHoverInverted:o,itemTextColorHorizontalInverted:e,itemTextColorHoverHorizontalInverted:o,itemTextColorChildActiveHorizontalInverted:o,itemTextColorChildActiveHoverHorizontalInverted:o,itemTextColorActiveHorizontalInverted:o,itemTextColorActiveHoverHorizontalInverted:o,itemIconColorInverted:e,itemIconColorHoverInverted:o,itemIconColorActiveInverted:o,itemIconColorActiveHoverInverted:o,itemIconColorChildActiveInverted:o,itemIconColorChildActiveHoverInverted:o,itemIconColorCollapsedInverted:e,itemIconColorHorizontalInverted:e,itemIconColorHoverHorizontalInverted:o,itemIconColorActiveHorizontalInverted:o,itemIconColorActiveHoverHorizontalInverted:o,itemIconColorChildActiveHorizontalInverted:o,itemIconColorChildActiveHoverHorizontalInverted:o,arrowColorInverted:e,arrowColorHoverInverted:o,arrowColorActiveInverted:o,arrowColorActiveHoverInverted:o,arrowColorChildActiveInverted:o,arrowColorChildActiveHoverInverted:o,groupTextColorInverted:n}}function Ao(e){const{borderRadius:t,textColor3:o,primaryColor:n,textColor2:a,textColor1:i,fontSize:v,dividerColor:f,hoverColor:c,primaryColorHover:p}=e;return Object.assign({borderRadius:t,color:"#0000",groupTextColor:o,itemColorHover:c,itemColorActive:le(n,{alpha:.1}),itemColorActiveHover:le(n,{alpha:.1}),itemColorActiveCollapsed:le(n,{alpha:.1}),itemTextColor:a,itemTextColorHover:a,itemTextColorActive:n,itemTextColorActiveHover:n,itemTextColorChildActive:n,itemTextColorChildActiveHover:n,itemTextColorHorizontal:a,itemTextColorHoverHorizontal:p,itemTextColorActiveHorizontal:n,itemTextColorActiveHoverHorizontal:n,itemTextColorChildActiveHorizontal:n,itemTextColorChildActiveHoverHorizontal:n,itemIconColor:i,itemIconColorHover:i,itemIconColorActive:n,itemIconColorActiveHover:n,itemIconColorChildActive:n,itemIconColorChildActiveHover:n,itemIconColorCollapsed:i,itemIconColorHorizontal:i,itemIconColorHoverHorizontal:p,itemIconColorActiveHorizontal:n,itemIconColorActiveHoverHorizontal:n,itemIconColorChildActiveHorizontal:n,itemIconColorChildActiveHoverHorizontal:n,itemHeight:"42px",arrowColor:a,arrowColorHover:a,arrowColorActive:n,arrowColorActiveHover:n,arrowColorChildActive:n,arrowColorChildActiveHover:n,colorInverted:"#0000",borderColorHorizontal:"#0000",fontSize:v,dividerColor:f},So("#BBB",n,"#FFF","#AAA"))}const Ho=Ne({name:"Menu",common:ke,peers:{Tooltip:fo,Dropdown:ho},self:Ao}),Ee=J("n-layout-sider"),pe={type:String,default:"static"},Ro=u("layout",`
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
 `),w("absolute-positioned",`
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 `)]),Po={embedded:Boolean,position:pe,nativeScrollbar:{type:Boolean,default:!0},scrollbarProps:Object,onScroll:Function,contentClass:String,contentStyle:{type:[String,Object],default:""},hasSider:Boolean,siderPlacement:{type:String,default:"left"}},$e=J("n-layout");function Fe(e){return B({name:e?"LayoutContent":"Layout",props:Object.assign(Object.assign({},U.props),Po),setup(t){const o=O(null),n=O(null),{mergedClsPrefixRef:a,inlineThemeDisabled:i}=te(t),v=U("Layout","-layout",Ro,fe,t,a);function f(z,S){if(t.nativeScrollbar){const{value:N}=o;N&&(S===void 0?N.scrollTo(z):N.scrollTo(z,S))}else{const{value:N}=n;N&&N.scrollTo(z,S)}}W($e,t);let c=0,p=0;const k=z=>{var S;const N=z.target;c=N.scrollLeft,p=N.scrollTop,(S=t.onScroll)===null||S===void 0||S.call(t,z)};Be(()=>{if(t.nativeScrollbar){const z=o.value;z&&(z.scrollTop=p,z.scrollLeft=c)}});const R={display:"flex",flexWrap:"nowrap",width:"100%",flexDirection:"row"},m={scrollTo:f},P=b(()=>{const{common:{cubicBezierEaseInOut:z},self:S}=v.value;return{"--n-bezier":z,"--n-color":t.embedded?S.colorEmbedded:S.color,"--n-text-color":S.textColor}}),H=i?re("layout",b(()=>t.embedded?"e":""),P,t):void 0;return Object.assign({mergedClsPrefix:a,scrollableElRef:o,scrollbarInstRef:n,hasSiderStyle:R,mergedTheme:v,handleNativeElScroll:k,cssVars:i?void 0:P,themeClass:H==null?void 0:H.themeClass,onRender:H==null?void 0:H.onRender},m)},render(){var t;const{mergedClsPrefix:o,hasSider:n}=this;(t=this.onRender)===null||t===void 0||t.call(this);const a=n?this.hasSiderStyle:void 0,i=[this.themeClass,e&&`${o}-layout-content`,`${o}-layout`,`${o}-layout--${this.position}-positioned`];return d("div",{class:i,style:this.cssVars},this.nativeScrollbar?d("div",{ref:"scrollableElRef",class:[`${o}-layout-scroll-container`,this.contentClass],style:[this.contentStyle,a],onScroll:this.handleNativeElScroll},this.$slots):d(_e,Object.assign({},this.scrollbarProps,{onScroll:this.onScroll,ref:"scrollbarInstRef",theme:this.mergedTheme.peers.Scrollbar,themeOverrides:this.mergedTheme.peerOverrides.Scrollbar,contentClass:this.contentClass,contentStyle:[this.contentStyle,a]}),this.$slots))}})}const Re=Fe(!1),To=Fe(!0),No=u("layout-header",`
 transition:
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 box-sizing: border-box;
 width: 100%;
 background-color: var(--n-color);
 color: var(--n-text-color);
`,[w("absolute-positioned",`
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 `),w("bordered",`
 border-bottom: solid 1px var(--n-border-color);
 `)]),ko={position:pe,inverted:Boolean,bordered:{type:Boolean,default:!1}},_o=B({name:"LayoutHeader",props:Object.assign(Object.assign({},U.props),ko),setup(e){const{mergedClsPrefixRef:t,inlineThemeDisabled:o}=te(e),n=U("Layout","-layout-header",No,fe,e,t),a=b(()=>{const{common:{cubicBezierEaseInOut:v},self:f}=n.value,c={"--n-bezier":v};return e.inverted?(c["--n-color"]=f.headerColorInverted,c["--n-text-color"]=f.textColorInverted,c["--n-border-color"]=f.headerBorderColorInverted):(c["--n-color"]=f.headerColor,c["--n-text-color"]=f.textColor,c["--n-border-color"]=f.headerBorderColor),c}),i=o?re("layout-header",b(()=>e.inverted?"a":"b"),a,e):void 0;return{mergedClsPrefix:t,cssVars:o?void 0:a,themeClass:i==null?void 0:i.themeClass,onRender:i==null?void 0:i.onRender}},render(){var e;const{mergedClsPrefix:t}=this;return(e=this.onRender)===null||e===void 0||e.call(this),d("div",{class:[`${t}-layout-header`,this.themeClass,this.position&&`${t}-layout-header--${this.position}-positioned`,this.bordered&&`${t}-layout-header--bordered`],style:this.cssVars},this.$slots)}}),Bo=u("layout-sider",`
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
`,[w("bordered",[s("border",`
 content: "";
 position: absolute;
 top: 0;
 bottom: 0;
 width: 1px;
 background-color: var(--n-border-color);
 transition: background-color .3s var(--n-bezier);
 `)]),s("left-placement",[w("bordered",[s("border",`
 right: 0;
 `)])]),w("right-placement",`
 justify-content: flex-start;
 `,[w("bordered",[s("border",`
 left: 0;
 `)]),w("collapsed",[u("layout-toggle-button",[u("base-icon",`
 transform: rotate(180deg);
 `)]),u("layout-toggle-bar",[I("&:hover",[s("top",{transform:"rotate(-12deg) scale(1.15) translateY(-2px)"}),s("bottom",{transform:"rotate(12deg) scale(1.15) translateY(2px)"})])])]),u("layout-toggle-button",`
 left: 0;
 transform: translateX(-50%) translateY(-50%);
 `,[u("base-icon",`
 transform: rotate(0);
 `)]),u("layout-toggle-bar",`
 left: -28px;
 transform: rotate(180deg);
 `,[I("&:hover",[s("top",{transform:"rotate(12deg) scale(1.15) translateY(-2px)"}),s("bottom",{transform:"rotate(-12deg) scale(1.15) translateY(2px)"})])])]),w("collapsed",[u("layout-toggle-bar",[I("&:hover",[s("top",{transform:"rotate(-12deg) scale(1.15) translateY(-2px)"}),s("bottom",{transform:"rotate(12deg) scale(1.15) translateY(2px)"})])]),u("layout-toggle-button",[u("base-icon",`
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
 `,[s("top, bottom",`
 position: absolute;
 width: 4px;
 border-radius: 2px;
 height: 38px;
 left: 14px;
 transition: 
 background-color .3s var(--n-bezier),
 transform .3s var(--n-bezier);
 `),s("bottom",`
 position: absolute;
 top: 34px;
 `),I("&:hover",[s("top",{transform:"rotate(12deg) scale(1.15) translateY(-2px)"}),s("bottom",{transform:"rotate(-12deg) scale(1.15) translateY(2px)"})]),s("top, bottom",{backgroundColor:"var(--n-toggle-bar-color)"}),I("&:hover",[s("top, bottom",{backgroundColor:"var(--n-toggle-bar-color-hover)"})])]),s("border",`
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
 `),w("show-content",[u("layout-sider-scroll-container",{opacity:1})]),w("absolute-positioned",`
 position: absolute;
 left: 0;
 top: 0;
 bottom: 0;
 `)]),Oo=B({props:{clsPrefix:{type:String,required:!0},onClick:Function},render(){const{clsPrefix:e}=this;return d("div",{onClick:this.onClick,class:`${e}-layout-toggle-bar`},d("div",{class:`${e}-layout-toggle-bar__top`}),d("div",{class:`${e}-layout-toggle-bar__bottom`}))}}),Eo=B({name:"LayoutToggleButton",props:{clsPrefix:{type:String,required:!0},onClick:Function},render(){const{clsPrefix:e}=this;return d("div",{class:`${e}-layout-toggle-button`,onClick:this.onClick},d(Oe,{clsPrefix:e},{default:()=>d(po,null)}))}}),$o={position:pe,bordered:Boolean,collapsedWidth:{type:Number,default:48},width:{type:[Number,String],default:272},contentClass:String,contentStyle:{type:[String,Object],default:""},collapseMode:{type:String,default:"transform"},collapsed:{type:Boolean,default:void 0},defaultCollapsed:Boolean,showCollapsedContent:{type:Boolean,default:!0},showTrigger:{type:[Boolean,String],default:!1},nativeScrollbar:{type:Boolean,default:!0},inverted:Boolean,scrollbarProps:Object,triggerClass:String,triggerStyle:[String,Object],collapsedTriggerClass:String,collapsedTriggerStyle:[String,Object],"onUpdate:collapsed":[Function,Array],onUpdateCollapsed:[Function,Array],onAfterEnter:Function,onAfterLeave:Function,onExpand:[Function,Array],onCollapse:[Function,Array],onScroll:Function},Fo=B({name:"LayoutSider",props:Object.assign(Object.assign({},U.props),$o),setup(e){const t=D($e),o=O(null),n=O(null),a=O(e.defaultCollapsed),i=ue(oe(e,"collapsed"),a),v=b(()=>se(i.value?e.collapsedWidth:e.width)),f=b(()=>e.collapseMode!=="transform"?{}:{minWidth:se(e.width)}),c=b(()=>t?t.siderPlacement:"left");function p(T,x){if(e.nativeScrollbar){const{value:y}=o;y&&(x===void 0?y.scrollTo(T):y.scrollTo(T,x))}else{const{value:y}=n;y&&y.scrollTo(T,x)}}function k(){const{"onUpdate:collapsed":T,onUpdateCollapsed:x,onExpand:y,onCollapse:K}=e,{value:L}=i;x&&$(x,!L),T&&$(T,!L),a.value=!L,L?y&&$(y):K&&$(K)}let R=0,m=0;const P=T=>{var x;const y=T.target;R=y.scrollLeft,m=y.scrollTop,(x=e.onScroll)===null||x===void 0||x.call(e,T)};Be(()=>{if(e.nativeScrollbar){const T=o.value;T&&(T.scrollTop=m,T.scrollLeft=R)}}),W(Ee,{collapsedRef:i,collapseModeRef:oe(e,"collapseMode")});const{mergedClsPrefixRef:H,inlineThemeDisabled:z}=te(e),S=U("Layout","-layout-sider",Bo,fe,e,H);function N(T){var x,y;T.propertyName==="max-width"&&(i.value?(x=e.onAfterLeave)===null||x===void 0||x.call(e):(y=e.onAfterEnter)===null||y===void 0||y.call(e))}const Y={scrollTo:p},j=b(()=>{const{common:{cubicBezierEaseInOut:T},self:x}=S.value,{siderToggleButtonColor:y,siderToggleButtonBorder:K,siderToggleBarColor:L,siderToggleBarColorHover:ne}=x,_={"--n-bezier":T,"--n-toggle-button-color":y,"--n-toggle-button-border":K,"--n-toggle-bar-color":L,"--n-toggle-bar-color-hover":ne};return e.inverted?(_["--n-color"]=x.siderColorInverted,_["--n-text-color"]=x.textColorInverted,_["--n-border-color"]=x.siderBorderColorInverted,_["--n-toggle-button-icon-color"]=x.siderToggleButtonIconColorInverted,_.__invertScrollbar=x.__invertScrollbar):(_["--n-color"]=x.siderColor,_["--n-text-color"]=x.textColor,_["--n-border-color"]=x.siderBorderColor,_["--n-toggle-button-icon-color"]=x.siderToggleButtonIconColor),_}),E=z?re("layout-sider",b(()=>e.inverted?"a":"b"),j,e):void 0;return Object.assign({scrollableElRef:o,scrollbarInstRef:n,mergedClsPrefix:H,mergedTheme:S,styleMaxWidth:v,mergedCollapsed:i,scrollContainerStyle:f,siderPlacement:c,handleNativeElScroll:P,handleTransitionend:N,handleTriggerClick:k,inlineThemeDisabled:z,cssVars:j,themeClass:E==null?void 0:E.themeClass,onRender:E==null?void 0:E.onRender},Y)},render(){var e;const{mergedClsPrefix:t,mergedCollapsed:o,showTrigger:n}=this;return(e=this.onRender)===null||e===void 0||e.call(this),d("aside",{class:[`${t}-layout-sider`,this.themeClass,`${t}-layout-sider--${this.position}-positioned`,`${t}-layout-sider--${this.siderPlacement}-placement`,this.bordered&&`${t}-layout-sider--bordered`,o&&`${t}-layout-sider--collapsed`,(!o||this.showCollapsedContent)&&`${t}-layout-sider--show-content`],onTransitionend:this.handleTransitionend,style:[this.inlineThemeDisabled?void 0:this.cssVars,{maxWidth:this.styleMaxWidth,width:se(this.width)}]},this.nativeScrollbar?d("div",{class:[`${t}-layout-sider-scroll-container`,this.contentClass],onScroll:this.handleNativeElScroll,style:[this.scrollContainerStyle,{overflow:"auto"},this.contentStyle],ref:"scrollableElRef"},this.$slots):d(_e,Object.assign({},this.scrollbarProps,{onScroll:this.onScroll,ref:"scrollbarInstRef",style:this.scrollContainerStyle,contentStyle:this.contentStyle,contentClass:this.contentClass,theme:this.mergedTheme.peers.Scrollbar,themeOverrides:this.mergedTheme.peerOverrides.Scrollbar,builtinThemeOverrides:this.inverted&&this.cssVars.__invertScrollbar==="true"?{colorHover:"rgba(255, 255, 255, .4)",color:"rgba(255, 255, 255, .3)"}:void 0}),this.$slots),n?n==="bar"?d(Oo,{clsPrefix:t,class:o?this.collapsedTriggerClass:this.triggerClass,style:o?this.collapsedTriggerStyle:this.triggerStyle,onClick:this.handleTriggerClick}):d(Eo,{clsPrefix:t,class:o?this.collapsedTriggerClass:this.triggerClass,style:o?this.collapsedTriggerStyle:this.triggerStyle,onClick:this.handleTriggerClick}):null,this.bordered?d("div",{class:`${t}-layout-sider__border`}):null)}}),Q=J("n-menu"),Le=J("n-submenu"),ge=J("n-menu-item-group"),Pe=[I("&::before","background-color: var(--n-item-color-hover);"),s("arrow",`
 color: var(--n-arrow-color-hover);
 `),s("icon",`
 color: var(--n-item-icon-color-hover);
 `),u("menu-item-content-header",`
 color: var(--n-item-text-color-hover);
 `,[I("a",`
 color: var(--n-item-text-color-hover);
 `),s("extra",`
 color: var(--n-item-text-color-hover);
 `)])],Te=[s("icon",`
 color: var(--n-item-icon-color-hover-horizontal);
 `),u("menu-item-content-header",`
 color: var(--n-item-text-color-hover-horizontal);
 `,[I("a",`
 color: var(--n-item-text-color-hover-horizontal);
 `),s("extra",`
 color: var(--n-item-text-color-hover-horizontal);
 `)])],Lo=I([u("menu",`
 background-color: var(--n-color);
 color: var(--n-item-text-color);
 overflow: hidden;
 transition: background-color .3s var(--n-bezier);
 box-sizing: border-box;
 font-size: var(--n-font-size);
 padding-bottom: 6px;
 `,[w("horizontal",`
 max-width: 100%;
 width: 100%;
 display: flex;
 overflow: hidden;
 padding-bottom: 0;
 `,[u("submenu","margin: 0;"),u("menu-item","margin: 0;"),u("menu-item-content",`
 padding: 0 20px;
 border-bottom: 2px solid #0000;
 `,[I("&::before","display: none;"),w("selected","border-bottom: 2px solid var(--n-border-color-horizontal)")]),u("menu-item-content",[w("selected",[s("icon","color: var(--n-item-icon-color-active-horizontal);"),u("menu-item-content-header",`
 color: var(--n-item-text-color-active-horizontal);
 `,[I("a","color: var(--n-item-text-color-active-horizontal);"),s("extra","color: var(--n-item-text-color-active-horizontal);")])]),w("child-active",`
 border-bottom: 2px solid var(--n-border-color-horizontal);
 `,[u("menu-item-content-header",`
 color: var(--n-item-text-color-child-active-horizontal);
 `,[I("a",`
 color: var(--n-item-text-color-child-active-horizontal);
 `),s("extra",`
 color: var(--n-item-text-color-child-active-horizontal);
 `)]),s("icon",`
 color: var(--n-item-icon-color-child-active-horizontal);
 `)]),X("disabled",[X("selected, child-active",[I("&:focus-within",Te)]),w("selected",[G(null,[s("icon","color: var(--n-item-icon-color-active-hover-horizontal);"),u("menu-item-content-header",`
 color: var(--n-item-text-color-active-hover-horizontal);
 `,[I("a","color: var(--n-item-text-color-active-hover-horizontal);"),s("extra","color: var(--n-item-text-color-active-hover-horizontal);")])])]),w("child-active",[G(null,[s("icon","color: var(--n-item-icon-color-child-active-hover-horizontal);"),u("menu-item-content-header",`
 color: var(--n-item-text-color-child-active-hover-horizontal);
 `,[I("a","color: var(--n-item-text-color-child-active-hover-horizontal);"),s("extra","color: var(--n-item-text-color-child-active-hover-horizontal);")])])]),G("border-bottom: 2px solid var(--n-border-color-horizontal);",Te)]),u("menu-item-content-header",[I("a","color: var(--n-item-text-color-horizontal);")])])]),X("responsive",[u("menu-item-content-header",`
 overflow: hidden;
 text-overflow: ellipsis;
 `)]),w("collapsed",[u("menu-item-content",[w("selected",[I("&::before",`
 background-color: var(--n-item-color-active-collapsed) !important;
 `)]),u("menu-item-content-header","opacity: 0;"),s("arrow","opacity: 0;"),s("icon","color: var(--n-item-icon-color-collapsed);")])]),u("menu-item",`
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
 `,[I("> *","z-index: 1;"),I("&::before",`
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
 `),w("disabled",`
 opacity: .45;
 cursor: not-allowed;
 `),w("collapsed",[s("arrow","transform: rotate(0);")]),w("selected",[I("&::before","background-color: var(--n-item-color-active);"),s("arrow","color: var(--n-arrow-color-active);"),s("icon","color: var(--n-item-icon-color-active);"),u("menu-item-content-header",`
 color: var(--n-item-text-color-active);
 `,[I("a","color: var(--n-item-text-color-active);"),s("extra","color: var(--n-item-text-color-active);")])]),w("child-active",[u("menu-item-content-header",`
 color: var(--n-item-text-color-child-active);
 `,[I("a",`
 color: var(--n-item-text-color-child-active);
 `),s("extra",`
 color: var(--n-item-text-color-child-active);
 `)]),s("arrow",`
 color: var(--n-arrow-color-child-active);
 `),s("icon",`
 color: var(--n-item-icon-color-child-active);
 `)]),X("disabled",[X("selected, child-active",[I("&:focus-within",Pe)]),w("selected",[G(null,[s("arrow","color: var(--n-arrow-color-active-hover);"),s("icon","color: var(--n-item-icon-color-active-hover);"),u("menu-item-content-header",`
 color: var(--n-item-text-color-active-hover);
 `,[I("a","color: var(--n-item-text-color-active-hover);"),s("extra","color: var(--n-item-text-color-active-hover);")])])]),w("child-active",[G(null,[s("arrow","color: var(--n-arrow-color-child-active-hover);"),s("icon","color: var(--n-item-icon-color-child-active-hover);"),u("menu-item-content-header",`
 color: var(--n-item-text-color-child-active-hover);
 `,[I("a","color: var(--n-item-text-color-child-active-hover);"),s("extra","color: var(--n-item-text-color-child-active-hover);")])])]),w("selected",[G(null,[I("&::before","background-color: var(--n-item-color-active-hover);")])]),G(null,Pe)]),s("icon",`
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
 `),s("arrow",`
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
 `,[I("a",`
 outline: none;
 text-decoration: none;
 transition: color .3s var(--n-bezier);
 color: var(--n-item-text-color);
 `,[I("&::before",`
 content: "";
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 `)]),s("extra",`
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
 `,[oo({duration:".2s"})])]),u("menu-item-group",[u("menu-item-group-title",`
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
 `)])]),u("menu-tooltip",[I("a",`
 color: inherit;
 text-decoration: none;
 `)]),u("menu-divider",`
 transition: background-color .3s var(--n-bezier);
 background-color: var(--n-divider-color);
 height: 1px;
 margin: 6px 18px;
 `)]);function G(e,t){return[w("hover",e,t),I("&:hover",e,t)]}const Me=B({name:"MenuOptionContent",props:{collapsed:Boolean,disabled:Boolean,title:[String,Function],icon:Function,extra:[String,Function],showArrow:Boolean,childActive:Boolean,hover:Boolean,paddingLeft:Number,selected:Boolean,maxIconSize:{type:Number,required:!0},activeIconSize:{type:Number,required:!0},iconMarginRight:{type:Number,required:!0},clsPrefix:{type:String,required:!0},onClick:Function,tmNode:{type:Object,required:!0},isEllipsisPlaceholder:Boolean},setup(e){const{props:t}=D(Q);return{menuProps:t,style:b(()=>{const{paddingLeft:o}=e;return{paddingLeft:o&&`${o}px`}}),iconStyle:b(()=>{const{maxIconSize:o,activeIconSize:n,iconMarginRight:a}=e;return{width:`${o}px`,height:`${o}px`,fontSize:`${n}px`,marginRight:`${a}px`}})}},render(){const{clsPrefix:e,tmNode:t,menuProps:{renderIcon:o,renderLabel:n,renderExtra:a,expandIcon:i}}=this,v=o?o(t.rawNode):q(this.icon);return d("div",{onClick:f=>{var c;(c=this.onClick)===null||c===void 0||c.call(this,f)},role:"none",class:[`${e}-menu-item-content`,{[`${e}-menu-item-content--selected`]:this.selected,[`${e}-menu-item-content--collapsed`]:this.collapsed,[`${e}-menu-item-content--child-active`]:this.childActive,[`${e}-menu-item-content--disabled`]:this.disabled,[`${e}-menu-item-content--hover`]:this.hover}],style:this.style},v&&d("div",{class:`${e}-menu-item-content__icon`,style:this.iconStyle,role:"none"},[v]),d("div",{class:`${e}-menu-item-content-header`,role:"none"},this.isEllipsisPlaceholder?this.title:n?n(t.rawNode):q(this.title),this.extra||a?d("span",{class:`${e}-menu-item-content-header__extra`}," ",a?a(t.rawNode):q(this.extra)):null),this.showArrow?d(Oe,{ariaHidden:!0,class:`${e}-menu-item-content__arrow`,clsPrefix:e},{default:()=>i?i(t.rawNode):d(zo,null)}):null)}}),ee=8;function be(e){const t=D(Q),{props:o,mergedCollapsedRef:n}=t,a=D(Le,null),i=D(ge,null),v=b(()=>o.mode==="horizontal"),f=b(()=>v.value?o.dropdownPlacement:"tmNodes"in e?"right-start":"right"),c=b(()=>{var m;return Math.max((m=o.collapsedIconSize)!==null&&m!==void 0?m:o.iconSize,o.iconSize)}),p=b(()=>{var m;return!v.value&&e.root&&n.value&&(m=o.collapsedIconSize)!==null&&m!==void 0?m:o.iconSize}),k=b(()=>{if(v.value)return;const{collapsedWidth:m,indent:P,rootIndent:H}=o,{root:z,isGroup:S}=e,N=H===void 0?P:H;return z?n.value?m/2-c.value/2:N:i&&typeof i.paddingLeftRef.value=="number"?P/2+i.paddingLeftRef.value:a&&typeof a.paddingLeftRef.value=="number"?(S?P/2:P)+a.paddingLeftRef.value:0}),R=b(()=>{const{collapsedWidth:m,indent:P,rootIndent:H}=o,{value:z}=c,{root:S}=e;return v.value||!S||!n.value?ee:(H===void 0?P:H)+z+ee-(m+z)/2});return{dropdownPlacement:f,activeIconSize:p,maxIconSize:c,paddingLeft:k,iconMarginRight:R,NMenu:t,NSubmenu:a,NMenuOptionGroup:i}}const Ce={internalKey:{type:[String,Number],required:!0},root:Boolean,isGroup:Boolean,level:{type:Number,required:!0},title:[String,Function],extra:[String,Function]},Mo=B({name:"MenuDivider",setup(){const e=D(Q),{mergedClsPrefixRef:t,isHorizontalRef:o}=e;return()=>o.value?null:d("div",{class:`${t.value}-menu-divider`})}}),je=Object.assign(Object.assign({},Ce),{tmNode:{type:Object,required:!0},disabled:Boolean,icon:Function,onClick:Function}),jo=he(je),Ko=B({name:"MenuOption",props:je,setup(e){const t=be(e),{NSubmenu:o,NMenu:n,NMenuOptionGroup:a}=t,{props:i,mergedClsPrefixRef:v,mergedCollapsedRef:f}=n,c=o?o.mergedDisabledRef:a?a.mergedDisabledRef:{value:!1},p=b(()=>c.value||e.disabled);function k(m){const{onClick:P}=e;P&&P(m)}function R(m){p.value||(n.doSelect(e.internalKey,e.tmNode.rawNode),k(m))}return{mergedClsPrefix:v,dropdownPlacement:t.dropdownPlacement,paddingLeft:t.paddingLeft,iconMarginRight:t.iconMarginRight,maxIconSize:t.maxIconSize,activeIconSize:t.activeIconSize,mergedTheme:n.mergedThemeRef,menuProps:i,dropdownEnabled:de(()=>e.root&&f.value&&i.mode!=="horizontal"&&!p.value),selected:de(()=>n.mergedValueRef.value===e.internalKey),mergedDisabled:p,handleClick:R}},render(){const{mergedClsPrefix:e,mergedTheme:t,tmNode:o,menuProps:{renderLabel:n,nodeProps:a}}=this,i=a==null?void 0:a(o.rawNode);return d("div",Object.assign({},i,{role:"menuitem",class:[`${e}-menu-item`,i==null?void 0:i.class]}),d(go,{theme:t.peers.Tooltip,themeOverrides:t.peerOverrides.Tooltip,trigger:"hover",placement:this.dropdownPlacement,disabled:!this.dropdownEnabled||this.title===void 0,internalExtraClass:["menu-tooltip"]},{default:()=>n?n(o.rawNode):q(this.title),trigger:()=>d(Me,{tmNode:o,clsPrefix:e,paddingLeft:this.paddingLeft,iconMarginRight:this.iconMarginRight,maxIconSize:this.maxIconSize,activeIconSize:this.activeIconSize,selected:this.selected,title:this.title,extra:this.extra,disabled:this.mergedDisabled,icon:this.icon,onClick:this.handleClick})}))}}),Ke=Object.assign(Object.assign({},Ce),{tmNode:{type:Object,required:!0},tmNodes:{type:Array,required:!0}}),Vo=he(Ke),Do=B({name:"MenuOptionGroup",props:Ke,setup(e){const t=be(e),{NSubmenu:o}=t,n=b(()=>o!=null&&o.mergedDisabledRef.value?!0:e.tmNode.disabled);W(ge,{paddingLeftRef:t.paddingLeft,mergedDisabledRef:n});const{mergedClsPrefixRef:a,props:i}=D(Q);return function(){const{value:v}=a,f=t.paddingLeft.value,{nodeProps:c}=i,p=c==null?void 0:c(e.tmNode.rawNode);return d("div",{class:`${v}-menu-item-group`,role:"group"},d("div",Object.assign({},p,{class:[`${v}-menu-item-group-title`,p==null?void 0:p.class],style:[(p==null?void 0:p.style)||"",f!==void 0?`padding-left: ${f}px;`:""]}),q(e.title),e.extra?d(to,null," ",q(e.extra)):null),d("div",null,e.tmNodes.map(k=>xe(k,i))))}}});function ve(e){return e.type==="divider"||e.type==="render"}function Uo(e){return e.type==="divider"}function xe(e,t){const{rawNode:o}=e,{show:n}=o;if(n===!1)return null;if(ve(o))return Uo(o)?d(Mo,Object.assign({key:e.key},o.props)):null;const{labelField:a}=t,{key:i,level:v,isGroup:f}=e,c=Object.assign(Object.assign({},o),{title:o.title||o[a],extra:o.titleExtra||o.extra,key:i,internalKey:i,level:v,root:v===0,isGroup:f});return e.children?e.isGroup?d(Do,ie(c,Vo,{tmNode:e,tmNodes:e.children,key:i})):d(me,ie(c,Go,{key:i,rawNodes:o[t.childrenField],tmNodes:e.children,tmNode:e})):d(Ko,ie(c,jo,{key:i,tmNode:e}))}const Ve=Object.assign(Object.assign({},Ce),{rawNodes:{type:Array,default:()=>[]},tmNodes:{type:Array,default:()=>[]},tmNode:{type:Object,required:!0},disabled:Boolean,icon:Function,onClick:Function,domId:String,virtualChildActive:{type:Boolean,default:void 0},isEllipsisPlaceholder:Boolean}),Go=he(Ve),me=B({name:"Submenu",props:Ve,setup(e){const t=be(e),{NMenu:o,NSubmenu:n}=t,{props:a,mergedCollapsedRef:i,mergedThemeRef:v}=o,f=b(()=>{const{disabled:m}=e;return n!=null&&n.mergedDisabledRef.value||a.disabled?!0:m}),c=O(!1);W(Le,{paddingLeftRef:t.paddingLeft,mergedDisabledRef:f}),W(ge,null);function p(){const{onClick:m}=e;m&&m()}function k(){f.value||(i.value||o.toggleExpand(e.internalKey),p())}function R(m){c.value=m}return{menuProps:a,mergedTheme:v,doSelect:o.doSelect,inverted:o.invertedRef,isHorizontal:o.isHorizontalRef,mergedClsPrefix:o.mergedClsPrefixRef,maxIconSize:t.maxIconSize,activeIconSize:t.activeIconSize,iconMarginRight:t.iconMarginRight,dropdownPlacement:t.dropdownPlacement,dropdownShow:c,paddingLeft:t.paddingLeft,mergedDisabled:f,mergedValue:o.mergedValueRef,childActive:de(()=>{var m;return(m=e.virtualChildActive)!==null&&m!==void 0?m:o.activePathRef.value.includes(e.internalKey)}),collapsed:b(()=>a.mode==="horizontal"?!1:i.value?!0:!o.mergedExpandedKeysRef.value.includes(e.internalKey)),dropdownEnabled:b(()=>!f.value&&(a.mode==="horizontal"||i.value)),handlePopoverShowChange:R,handleClick:k}},render(){var e;const{mergedClsPrefix:t,menuProps:{renderIcon:o,renderLabel:n}}=this,a=()=>{const{isHorizontal:v,paddingLeft:f,collapsed:c,mergedDisabled:p,maxIconSize:k,activeIconSize:R,title:m,childActive:P,icon:H,handleClick:z,menuProps:{nodeProps:S},dropdownShow:N,iconMarginRight:Y,tmNode:j,mergedClsPrefix:E,isEllipsisPlaceholder:T,extra:x}=this,y=S==null?void 0:S(j.rawNode);return d("div",Object.assign({},y,{class:[`${E}-menu-item`,y==null?void 0:y.class],role:"menuitem"}),d(Me,{tmNode:j,paddingLeft:f,collapsed:c,disabled:p,iconMarginRight:Y,maxIconSize:k,activeIconSize:R,title:m,extra:x,showArrow:!v,childActive:P,clsPrefix:E,icon:H,hover:N,onClick:z,isEllipsisPlaceholder:T}))},i=()=>d(ro,null,{default:()=>{const{tmNodes:v,collapsed:f}=this;return f?null:d("div",{class:`${t}-submenu-children`,role:"menu"},v.map(c=>xe(c,this.menuProps)))}});return this.root?d(bo,Object.assign({size:"large",trigger:"hover"},(e=this.menuProps)===null||e===void 0?void 0:e.dropdownProps,{themeOverrides:this.mergedTheme.peerOverrides.Dropdown,theme:this.mergedTheme.peers.Dropdown,builtinThemeOverrides:{fontSizeLarge:"14px",optionIconSizeLarge:"18px"},value:this.mergedValue,disabled:!this.dropdownEnabled,placement:this.dropdownPlacement,keyField:this.menuProps.keyField,labelField:this.menuProps.labelField,childrenField:this.menuProps.childrenField,onUpdateShow:this.handlePopoverShowChange,options:this.rawNodes,onSelect:this.doSelect,inverted:this.inverted,renderIcon:o,renderLabel:n}),{default:()=>d("div",{class:`${t}-submenu`,role:"menu","aria-expanded":!this.collapsed,id:this.domId},a(),this.isHorizontal?null:i())}):d("div",{class:`${t}-submenu`,role:"menu","aria-expanded":!this.collapsed,id:this.domId},a(),i())}}),qo=Object.assign(Object.assign({},U.props),{options:{type:Array,default:()=>[]},collapsed:{type:Boolean,default:void 0},collapsedWidth:{type:Number,default:48},iconSize:{type:Number,default:20},collapsedIconSize:{type:Number,default:24},rootIndent:Number,indent:{type:Number,default:32},labelField:{type:String,default:"label"},keyField:{type:String,default:"key"},childrenField:{type:String,default:"children"},disabledField:{type:String,default:"disabled"},defaultExpandAll:Boolean,defaultExpandedKeys:Array,expandedKeys:Array,value:[String,Number],defaultValue:{type:[String,Number],default:null},mode:{type:String,default:"vertical"},watchProps:{type:Array,default:void 0},disabled:Boolean,show:{type:Boolean,default:!0},inverted:Boolean,"onUpdate:expandedKeys":[Function,Array],onUpdateExpandedKeys:[Function,Array],onUpdateValue:[Function,Array],"onUpdate:value":[Function,Array],expandIcon:Function,renderIcon:Function,renderLabel:Function,renderExtra:Function,dropdownProps:Object,accordion:Boolean,nodeProps:Function,dropdownPlacement:{type:String,default:"bottom"},responsive:Boolean,items:Array,onOpenNamesChange:[Function,Array],onSelect:[Function,Array],onExpandedNamesChange:[Function,Array],expandedNames:Array,defaultExpandedNames:Array}),Wo=B({name:"Menu",inheritAttrs:!1,props:qo,setup(e){const{mergedClsPrefixRef:t,inlineThemeDisabled:o}=te(e),n=U("Menu","-menu",Lo,Ho,e,t),a=D(Ee,null),i=b(()=>{var h;const{collapsed:C}=e;if(C!==void 0)return C;if(a){const{collapseModeRef:r,collapsedRef:g}=a;if(r.value==="width")return(h=g.value)!==null&&h!==void 0?h:!1}return!1}),v=b(()=>{const{keyField:h,childrenField:C,disabledField:r}=e;return ce(e.items||e.options,{getIgnored(g){return ve(g)},getChildren(g){return g[C]},getDisabled(g){return g[r]},getKey(g){var A;return(A=g[h])!==null&&A!==void 0?A:g.name}})}),f=b(()=>new Set(v.value.treeNodes.map(h=>h.key))),{watchProps:c}=e,p=O(null);c!=null&&c.includes("defaultValue")?ze(()=>{p.value=e.defaultValue}):p.value=e.defaultValue;const k=oe(e,"value"),R=ue(k,p),m=O([]),P=()=>{m.value=e.defaultExpandAll?v.value.getNonLeafKeys():e.defaultExpandedNames||e.defaultExpandedKeys||v.value.getPath(R.value,{includeSelf:!1}).keyPath};c!=null&&c.includes("defaultExpandedKeys")?ze(P):P();const H=xo(e,["expandedNames","expandedKeys"]),z=ue(H,m),S=b(()=>v.value.treeNodes),N=b(()=>v.value.getPath(R.value).keyPath);W(Q,{props:e,mergedCollapsedRef:i,mergedThemeRef:n,mergedValueRef:R,mergedExpandedKeysRef:z,activePathRef:N,mergedClsPrefixRef:t,isHorizontalRef:b(()=>e.mode==="horizontal"),invertedRef:oe(e,"inverted"),doSelect:Y,toggleExpand:E});function Y(h,C){const{"onUpdate:value":r,onUpdateValue:g,onSelect:A}=e;g&&$(g,h,C),r&&$(r,h,C),A&&$(A,h,C),p.value=h}function j(h){const{"onUpdate:expandedKeys":C,onUpdateExpandedKeys:r,onExpandedNamesChange:g,onOpenNamesChange:A}=e;C&&$(C,h),r&&$(r,h),g&&$(g,h),A&&$(A,h),m.value=h}function E(h){const C=Array.from(z.value),r=C.findIndex(g=>g===h);if(~r)C.splice(r,1);else{if(e.accordion&&f.value.has(h)){const g=C.findIndex(A=>f.value.has(A));g>-1&&C.splice(g,1)}C.push(h)}j(C)}const T=h=>{const C=v.value.getPath(h??R.value,{includeSelf:!1}).keyPath;if(!C.length)return;const r=Array.from(z.value),g=new Set([...r,...C]);e.accordion&&f.value.forEach(A=>{g.has(A)&&!C.includes(A)&&g.delete(A)}),j(Array.from(g))},x=b(()=>{const{inverted:h}=e,{common:{cubicBezierEaseInOut:C},self:r}=n.value,{borderRadius:g,borderColorHorizontal:A,fontSize:Je,itemHeight:Qe,dividerColor:Ze}=r,l={"--n-divider-color":Ze,"--n-bezier":C,"--n-font-size":Je,"--n-border-color-horizontal":A,"--n-border-radius":g,"--n-item-height":Qe};return h?(l["--n-group-text-color"]=r.groupTextColorInverted,l["--n-color"]=r.colorInverted,l["--n-item-text-color"]=r.itemTextColorInverted,l["--n-item-text-color-hover"]=r.itemTextColorHoverInverted,l["--n-item-text-color-active"]=r.itemTextColorActiveInverted,l["--n-item-text-color-child-active"]=r.itemTextColorChildActiveInverted,l["--n-item-text-color-child-active-hover"]=r.itemTextColorChildActiveInverted,l["--n-item-text-color-active-hover"]=r.itemTextColorActiveHoverInverted,l["--n-item-icon-color"]=r.itemIconColorInverted,l["--n-item-icon-color-hover"]=r.itemIconColorHoverInverted,l["--n-item-icon-color-active"]=r.itemIconColorActiveInverted,l["--n-item-icon-color-active-hover"]=r.itemIconColorActiveHoverInverted,l["--n-item-icon-color-child-active"]=r.itemIconColorChildActiveInverted,l["--n-item-icon-color-child-active-hover"]=r.itemIconColorChildActiveHoverInverted,l["--n-item-icon-color-collapsed"]=r.itemIconColorCollapsedInverted,l["--n-item-text-color-horizontal"]=r.itemTextColorHorizontalInverted,l["--n-item-text-color-hover-horizontal"]=r.itemTextColorHoverHorizontalInverted,l["--n-item-text-color-active-horizontal"]=r.itemTextColorActiveHorizontalInverted,l["--n-item-text-color-child-active-horizontal"]=r.itemTextColorChildActiveHorizontalInverted,l["--n-item-text-color-child-active-hover-horizontal"]=r.itemTextColorChildActiveHoverHorizontalInverted,l["--n-item-text-color-active-hover-horizontal"]=r.itemTextColorActiveHoverHorizontalInverted,l["--n-item-icon-color-horizontal"]=r.itemIconColorHorizontalInverted,l["--n-item-icon-color-hover-horizontal"]=r.itemIconColorHoverHorizontalInverted,l["--n-item-icon-color-active-horizontal"]=r.itemIconColorActiveHorizontalInverted,l["--n-item-icon-color-active-hover-horizontal"]=r.itemIconColorActiveHoverHorizontalInverted,l["--n-item-icon-color-child-active-horizontal"]=r.itemIconColorChildActiveHorizontalInverted,l["--n-item-icon-color-child-active-hover-horizontal"]=r.itemIconColorChildActiveHoverHorizontalInverted,l["--n-arrow-color"]=r.arrowColorInverted,l["--n-arrow-color-hover"]=r.arrowColorHoverInverted,l["--n-arrow-color-active"]=r.arrowColorActiveInverted,l["--n-arrow-color-active-hover"]=r.arrowColorActiveHoverInverted,l["--n-arrow-color-child-active"]=r.arrowColorChildActiveInverted,l["--n-arrow-color-child-active-hover"]=r.arrowColorChildActiveHoverInverted,l["--n-item-color-hover"]=r.itemColorHoverInverted,l["--n-item-color-active"]=r.itemColorActiveInverted,l["--n-item-color-active-hover"]=r.itemColorActiveHoverInverted,l["--n-item-color-active-collapsed"]=r.itemColorActiveCollapsedInverted):(l["--n-group-text-color"]=r.groupTextColor,l["--n-color"]=r.color,l["--n-item-text-color"]=r.itemTextColor,l["--n-item-text-color-hover"]=r.itemTextColorHover,l["--n-item-text-color-active"]=r.itemTextColorActive,l["--n-item-text-color-child-active"]=r.itemTextColorChildActive,l["--n-item-text-color-child-active-hover"]=r.itemTextColorChildActiveHover,l["--n-item-text-color-active-hover"]=r.itemTextColorActiveHover,l["--n-item-icon-color"]=r.itemIconColor,l["--n-item-icon-color-hover"]=r.itemIconColorHover,l["--n-item-icon-color-active"]=r.itemIconColorActive,l["--n-item-icon-color-active-hover"]=r.itemIconColorActiveHover,l["--n-item-icon-color-child-active"]=r.itemIconColorChildActive,l["--n-item-icon-color-child-active-hover"]=r.itemIconColorChildActiveHover,l["--n-item-icon-color-collapsed"]=r.itemIconColorCollapsed,l["--n-item-text-color-horizontal"]=r.itemTextColorHorizontal,l["--n-item-text-color-hover-horizontal"]=r.itemTextColorHoverHorizontal,l["--n-item-text-color-active-horizontal"]=r.itemTextColorActiveHorizontal,l["--n-item-text-color-child-active-horizontal"]=r.itemTextColorChildActiveHorizontal,l["--n-item-text-color-child-active-hover-horizontal"]=r.itemTextColorChildActiveHoverHorizontal,l["--n-item-text-color-active-hover-horizontal"]=r.itemTextColorActiveHoverHorizontal,l["--n-item-icon-color-horizontal"]=r.itemIconColorHorizontal,l["--n-item-icon-color-hover-horizontal"]=r.itemIconColorHoverHorizontal,l["--n-item-icon-color-active-horizontal"]=r.itemIconColorActiveHorizontal,l["--n-item-icon-color-active-hover-horizontal"]=r.itemIconColorActiveHoverHorizontal,l["--n-item-icon-color-child-active-horizontal"]=r.itemIconColorChildActiveHorizontal,l["--n-item-icon-color-child-active-hover-horizontal"]=r.itemIconColorChildActiveHoverHorizontal,l["--n-arrow-color"]=r.arrowColor,l["--n-arrow-color-hover"]=r.arrowColorHover,l["--n-arrow-color-active"]=r.arrowColorActive,l["--n-arrow-color-active-hover"]=r.arrowColorActiveHover,l["--n-arrow-color-child-active"]=r.arrowColorChildActive,l["--n-arrow-color-child-active-hover"]=r.arrowColorChildActiveHover,l["--n-item-color-hover"]=r.itemColorHover,l["--n-item-color-active"]=r.itemColorActive,l["--n-item-color-active-hover"]=r.itemColorActiveHover,l["--n-item-color-active-collapsed"]=r.itemColorActiveCollapsed),l}),y=o?re("menu",b(()=>e.inverted?"a":"b"),x,e):void 0,K=lo(),L=O(null),ne=O(null);let _=!0;const ye=()=>{var h;_?_=!1:(h=L.value)===null||h===void 0||h.sync({showAllItemsBeforeCalculate:!0})};function De(){return document.getElementById(K)}const Z=O(-1);function Ue(h){Z.value=e.options.length-h}function Ge(h){h||(Z.value=-1)}const qe=b(()=>{const h=Z.value;return{children:h===-1?[]:e.options.slice(h)}}),We=b(()=>{const{childrenField:h,disabledField:C,keyField:r}=e;return ce([qe.value],{getIgnored(g){return ve(g)},getChildren(g){return g[h]},getDisabled(g){return g[C]},getKey(g){var A;return(A=g[r])!==null&&A!==void 0?A:g.name}})}),Ye=b(()=>ce([{}]).treeNodes[0]);function Xe(){var h;if(Z.value===-1)return d(me,{root:!0,level:0,key:"__ellpisisGroupPlaceholder__",internalKey:"__ellpisisGroupPlaceholder__",title:"···",tmNode:Ye.value,domId:K,isEllipsisPlaceholder:!0});const C=We.value.treeNodes[0],r=N.value,g=!!(!((h=C.children)===null||h===void 0)&&h.some(A=>r.includes(A.key)));return d(me,{level:0,root:!0,key:"__ellpisisGroup__",internalKey:"__ellpisisGroup__",title:"···",virtualChildActive:g,tmNode:C,domId:K,rawNodes:C.rawNode.children||[],tmNodes:C.children||[],isEllipsisPlaceholder:!0})}return{mergedClsPrefix:t,controlledExpandedKeys:H,uncontrolledExpanededKeys:m,mergedExpandedKeys:z,uncontrolledValue:p,mergedValue:R,activePath:N,tmNodes:S,mergedTheme:n,mergedCollapsed:i,cssVars:o?void 0:x,themeClass:y==null?void 0:y.themeClass,overflowRef:L,counterRef:ne,updateCounter:()=>{},onResize:ye,onUpdateOverflow:Ge,onUpdateCount:Ue,renderCounter:Xe,getCounter:De,onRender:y==null?void 0:y.onRender,showOption:T,deriveResponsiveState:ye}},render(){const{mergedClsPrefix:e,mode:t,themeClass:o,onRender:n}=this;n==null||n();const a=()=>this.tmNodes.map(c=>xe(c,this.$props)),v=t==="horizontal"&&this.responsive,f=()=>d("div",io(this.$attrs,{role:t==="horizontal"?"menubar":"menu",class:[`${e}-menu`,o,`${e}-menu--${t}`,v&&`${e}-menu--responsive`,this.mergedCollapsed&&`${e}-menu--collapsed`],style:this.cssVars}),v?d(Co,{ref:"overflowRef",onUpdateOverflow:this.onUpdateOverflow,getCounter:this.getCounter,onUpdateCount:this.onUpdateCount,updateCounter:this.updateCounter,style:{width:"100%",display:"flex",overflow:"hidden"}},{default:a,counter:this.renderCounter}):a());return v?d(no,{onResize:this.onResize},{default:f}):f()}}),Yo={class:"logo"},Xo={key:0},Jo={key:1},Qo={class:"title"},Zo=B({__name:"MainLayout",setup(e){const t=uo(),o=vo(),n=mo(),a=O(!1),i=[{label:"仪表盘",key:"dashboard"},{label:"应用管理",key:"applications"},{label:"录制中心",key:"recording"},{label:"测试用例",key:"testcases"},{label:"回放执行",key:"replay"},{label:"对比规则",key:"compare"},{label:"执行结果",key:"results"},{label:"定时任务",key:"schedule"},{label:"测试套件",key:"suites"},{label:"CI 集成",key:"ci"},{label:"用户管理",key:"users"},{label:"系统设置",key:"settings"}],v={dashboard:"仪表盘",applications:"应用管理",recording:"录制中心",testcases:"测试用例",replay:"回放执行",compare:"对比规则",results:"执行结果",schedule:"定时任务",suites:"测试套件",ci:"CI 集成",users:"用户管理",settings:"系统设置"},f=b(()=>o.path.split("/")[1]||"dashboard"),c=b(()=>v[f.value]||"AREX 录制平台");function p(R){t.push(`/${R}`)}function k(){n.clearUser(),t.push("/login")}return(R,m)=>{const P=so("router-view");return ae(),ao(F(Re),{"has-sider":"",style:{height:"100vh"}},{default:V(()=>[M(F(Fo),{bordered:"","collapse-mode":"width","collapsed-width":64,width:220,collapsed:a.value,"show-trigger":"",onCollapse:m[0]||(m[0]=H=>a.value=!0),onExpand:m[1]||(m[1]=H=>a.value=!1)},{default:V(()=>[we("div",Yo,[a.value?(ae(),Se("span",Jo,"AREX")):(ae(),Se("span",Xo,"AREX 录制平台"))]),M(F(Wo),{collapsed:a.value,"collapsed-width":64,"collapsed-icon-size":22,options:i,value:f.value,"onUpdate:value":p},null,8,["collapsed","value"])]),_:1},8,["collapsed"]),M(F(Re),null,{default:V(()=>[M(F(_o),{class:"header",bordered:""},{default:V(()=>[we("span",Qo,Ae(c.value),1),M(F(yo),null,{default:V(()=>[M(F(Io),null,{default:V(()=>[He(Ae(F(n).username),1)]),_:1}),M(F(co),{text:"",onClick:k},{default:V(()=>[...m[2]||(m[2]=[He("退出登录",-1)])]),_:1})]),_:1})]),_:1}),M(F(To),{style:{padding:"24px",overflow:"auto"}},{default:V(()=>[M(P)]),_:1})]),_:1})]),_:1})}}}),et=(e,t)=>{const o=e.__vccOpts||e;for(const[n,a]of t)o[n]=a;return o},at=et(Zo,[["__scopeId","data-v-8484b1b5"]]);export{at as default};
