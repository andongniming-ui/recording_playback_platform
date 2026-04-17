import{d as Ce,h as f,r as P,ac as Ft,ad as Ut,ae as We,af as Xt,a as qt,f as Jt,ag as Kt,q as ht,G as Yt,F as Qt,N as Zt,y as ea,ah as ta,m as K,ai as aa,g as d,i as y,o as E,n as O,w as ra,aj as Ue,ak as it,V as Xe,u as na,j as xt,a3 as qe,a9 as yt,D as oa,l as ia,al as la,am as sa,an as da,ao as ca,ap as ua,a8 as Je,aq as Z,ar as Re,p as pa,v as ee,t as Pe,H as de,I as i,J as a,U as ba,L as l,R as g,P as A,Q as R,O as ce,M as fa,ab as J,K as H,T as va,X as se}from"./index-D6LB0ej7.js";import{a as Le}from"./applications-Dy8uQOUo.js";import{r as Ae}from"./recordings-C6L5psRw.js";import{r as lt}from"./replays-Db3mHwRF.js";import{t as ga}from"./testcases-DgBFQO7e.js";import{f as Be}from"./format-Adq5_zH5.js";import{u as ma}from"./user-D9e99449.js";import{N as ha,a as st}from"./BreadcrumbItem-Jhcozeie.js";import{N as Ke,a as G}from"./DescriptionsItem-se0x1FqL.js";import{N as xa,a as dt}from"./CollapseItem-BmromAe2.js";import{A as ya}from"./Add--q_lcfUf.js";import{e as Ca,f as ct,o as Sa,u as ut,N as ne}from"./Space-JgVsnMPf.js";import{u as _a}from"./get-I2R12OG2.js";import{u as wa}from"./index-B6sC-FX3.js";import{a as te,N as pt}from"./Grid-Db3RjpGB.js";import{N as Ee}from"./Statistic-CvgP2Lih.js";import{N as Ye}from"./Select-C5OqV45F.js";import{N as Ne}from"./Alert-DJgzMnL0.js";import{N as Qe}from"./DataTable-C6hf0yd5.js";import{_ as ka}from"./_plugin-vue_export-helper-DlAUqK2U.js";import"./Tooltip-B2js9o6V.js";import"./Dropdown-Bfvnp9d9.js";const $a=ct(".v-x-scroll",{overflow:"auto",scrollbarWidth:"none"},[ct("&::-webkit-scrollbar",{width:0,height:0})]),Ta=Ce({name:"XScroll",props:{disabled:Boolean,onScroll:Function},setup(){const e=P(null);function c(x){!(x.currentTarget.offsetWidth<x.currentTarget.scrollWidth)||x.deltaY===0||(x.currentTarget.scrollLeft+=x.deltaY+x.deltaX,x.preventDefault())}const u=Ft();return $a.mount({id:"vueuc/x-scroll",head:!0,anchorMetaName:Ca,ssr:u}),Object.assign({selfRef:e,handleWheel:c},{scrollTo(...x){var _;(_=e.value)===null||_===void 0||_.scrollTo(...x)}})},render(){return f("div",{ref:"selfRef",onScroll:this.onScroll,onWheel:this.disabled?void 0:this.handleWheel,class:"v-x-scroll"},this.$slots)}});var za=/\s/;function Ra(e){for(var c=e.length;c--&&za.test(e.charAt(c)););return c}var Pa=/^\s+/;function La(e){return e&&e.slice(0,Ra(e)+1).replace(Pa,"")}var bt=NaN,Aa=/^[-+]0x[0-9a-f]+$/i,Ba=/^0b[01]+$/i,Ea=/^0o[0-7]+$/i,Na=parseInt;function ft(e){if(typeof e=="number")return e;if(Ut(e))return bt;if(We(e)){var c=typeof e.valueOf=="function"?e.valueOf():e;e=We(c)?c+"":c}if(typeof e!="string")return e===0?e:+e;e=La(e);var u=Ba.test(e);return u||Ea.test(e)?Na(e.slice(2),u?2:8):Aa.test(e)?bt:+e}var Ze=function(){return Xt.Date.now()},Wa="Expected a function",ja=Math.max,Da=Math.min;function Ma(e,c,u){var v,x,_,m,s,S,k=0,$=!1,B=!1,N=!0;if(typeof e!="function")throw new TypeError(Wa);c=ft(c)||0,We(u)&&($=!!u.leading,B="maxWait"in u,_=B?ja(ft(u.maxWait)||0,c):_,N="trailing"in u?!!u.trailing:N);function T(h){var V=v,ae=x;return v=x=void 0,k=h,m=e.apply(ae,V),m}function z(h){return k=h,s=setTimeout(M,c),$?T(h):m}function L(h){var V=h-S,ae=h-k,re=c-V;return B?Da(re,_-ae):re}function W(h){var V=h-S,ae=h-k;return S===void 0||V>=c||V<0||B&&ae>=_}function M(){var h=Ze();if(W(h))return j(h);s=setTimeout(M,L(h))}function j(h){return s=void 0,N&&v?T(h):(v=x=void 0,m)}function Y(){s!==void 0&&clearTimeout(s),k=0,v=S=x=s=void 0}function F(){return s===void 0?m:j(Ze())}function w(){var h=Ze(),V=W(h);if(v=arguments,x=this,S=h,V){if(s===void 0)return z(S);if(B)return clearTimeout(s),s=setTimeout(M,c),T(S)}return s===void 0&&(s=setTimeout(M,c)),m}return w.cancel=Y,w.flush=F,w}var Ia="Expected a function";function Va(e,c,u){var v=!0,x=!0;if(typeof e!="function")throw new TypeError(Ia);return We(u)&&(v="leading"in u?!!u.leading:v,x="trailing"in u?!!u.trailing:x),Ma(e,c,{leading:v,maxWait:c,trailing:x})}const Oa={tabFontSizeSmall:"14px",tabFontSizeMedium:"14px",tabFontSizeLarge:"16px",tabGapSmallLine:"36px",tabGapMediumLine:"36px",tabGapLargeLine:"36px",tabGapSmallLineVertical:"8px",tabGapMediumLineVertical:"8px",tabGapLargeLineVertical:"8px",tabPaddingSmallLine:"6px 0",tabPaddingMediumLine:"10px 0",tabPaddingLargeLine:"14px 0",tabPaddingVerticalSmallLine:"6px 12px",tabPaddingVerticalMediumLine:"8px 16px",tabPaddingVerticalLargeLine:"10px 20px",tabGapSmallBar:"36px",tabGapMediumBar:"36px",tabGapLargeBar:"36px",tabGapSmallBarVertical:"8px",tabGapMediumBarVertical:"8px",tabGapLargeBarVertical:"8px",tabPaddingSmallBar:"4px 0",tabPaddingMediumBar:"6px 0",tabPaddingLargeBar:"10px 0",tabPaddingVerticalSmallBar:"6px 12px",tabPaddingVerticalMediumBar:"8px 16px",tabPaddingVerticalLargeBar:"10px 20px",tabGapSmallCard:"4px",tabGapMediumCard:"4px",tabGapLargeCard:"4px",tabGapSmallCardVertical:"4px",tabGapMediumCardVertical:"4px",tabGapLargeCardVertical:"4px",tabPaddingSmallCard:"8px 16px",tabPaddingMediumCard:"10px 20px",tabPaddingLargeCard:"12px 24px",tabPaddingSmallSegment:"4px 0",tabPaddingMediumSegment:"6px 0",tabPaddingLargeSegment:"8px 0",tabPaddingVerticalLargeSegment:"0 8px",tabPaddingVerticalSmallCard:"8px 12px",tabPaddingVerticalMediumCard:"10px 16px",tabPaddingVerticalLargeCard:"12px 20px",tabPaddingVerticalSmallSegment:"0 4px",tabPaddingVerticalMediumSegment:"0 6px",tabGapSmallSegment:"0",tabGapMediumSegment:"0",tabGapLargeSegment:"0",tabGapSmallSegmentVertical:"0",tabGapMediumSegmentVertical:"0",tabGapLargeSegmentVertical:"0",panePaddingSmall:"8px 0 0 0",panePaddingMedium:"12px 0 0 0",panePaddingLarge:"16px 0 0 0",closeSize:"18px",closeIconSize:"14px"};function Ha(e){const{textColor2:c,primaryColor:u,textColorDisabled:v,closeIconColor:x,closeIconColorHover:_,closeIconColorPressed:m,closeColorHover:s,closeColorPressed:S,tabColor:k,baseColor:$,dividerColor:B,fontWeight:N,textColor1:T,borderRadius:z,fontSize:L,fontWeightStrong:W}=e;return Object.assign(Object.assign({},Oa),{colorSegment:k,tabFontSizeCard:L,tabTextColorLine:T,tabTextColorActiveLine:u,tabTextColorHoverLine:u,tabTextColorDisabledLine:v,tabTextColorSegment:T,tabTextColorActiveSegment:c,tabTextColorHoverSegment:c,tabTextColorDisabledSegment:v,tabTextColorBar:T,tabTextColorActiveBar:u,tabTextColorHoverBar:u,tabTextColorDisabledBar:v,tabTextColorCard:T,tabTextColorHoverCard:T,tabTextColorActiveCard:u,tabTextColorDisabledCard:v,barColor:u,closeIconColor:x,closeIconColorHover:_,closeIconColorPressed:m,closeColorHover:s,closeColorPressed:S,closeBorderRadius:z,tabColor:k,tabColorSegment:$,tabBorderColor:B,tabFontWeightActive:N,tabFontWeight:N,tabBorderRadius:z,paneTextColor:c,fontWeightStrong:W})}const Ga={common:qt,self:Ha},ot=Jt("n-tabs"),Ct={tab:[String,Number,Object,Function],name:{type:[String,Number],required:!0},disabled:Boolean,displayDirective:{type:String,default:"if"},closable:{type:Boolean,default:void 0},tabProps:Object,label:[String,Number,Object,Function]},et=Ce({__TAB_PANE__:!0,name:"TabPane",alias:["TabPanel"],props:Ct,slots:Object,setup(e){const c=ht(ot,null);return c||Kt("tab-pane","`n-tab-pane` must be placed inside `n-tabs`."),{style:c.paneStyleRef,class:c.paneClassRef,mergedClsPrefix:c.mergedClsPrefixRef}},render(){return f("div",{class:[`${this.mergedClsPrefix}-tab-pane`,this.class],style:this.style},this.$slots)}}),Fa=Object.assign({internalLeftPadded:Boolean,internalAddable:Boolean,internalCreatedByPane:Boolean},aa(Ct,["displayDirective"])),nt=Ce({__TAB__:!0,inheritAttrs:!1,name:"Tab",props:Fa,setup(e){const{mergedClsPrefixRef:c,valueRef:u,typeRef:v,closableRef:x,tabStyleRef:_,addTabStyleRef:m,tabClassRef:s,addTabClassRef:S,tabChangeIdRef:k,onBeforeLeaveRef:$,triggerRef:B,handleAdd:N,activateTab:T,handleClose:z}=ht(ot);return{trigger:B,mergedClosable:K(()=>{if(e.internalAddable)return!1;const{closable:L}=e;return L===void 0?x.value:L}),style:_,addStyle:m,tabClass:s,addTabClass:S,clsPrefix:c,value:u,type:v,handleClose(L){L.stopPropagation(),!e.disabled&&z(e.name)},activateTab(){if(e.disabled)return;if(e.internalAddable){N();return}const{name:L}=e,W=++k.id;if(L!==u.value){const{value:M}=$;M?Promise.resolve(M(e.name,u.value)).then(j=>{j&&k.id===W&&T(L)}):T(L)}}}},render(){const{internalAddable:e,clsPrefix:c,name:u,disabled:v,label:x,tab:_,value:m,mergedClosable:s,trigger:S,$slots:{default:k}}=this,$=x??_;return f("div",{class:`${c}-tabs-tab-wrapper`},this.internalLeftPadded?f("div",{class:`${c}-tabs-tab-pad`}):null,f("div",Object.assign({key:u,"data-name":u,"data-disabled":v?!0:void 0},Yt({class:[`${c}-tabs-tab`,m===u&&`${c}-tabs-tab--active`,v&&`${c}-tabs-tab--disabled`,s&&`${c}-tabs-tab--closable`,e&&`${c}-tabs-tab--addable`,e?this.addTabClass:this.tabClass],onClick:S==="click"?this.activateTab:void 0,onMouseenter:S==="hover"?this.activateTab:void 0,style:e?this.addStyle:this.style},this.internalCreatedByPane?this.tabProps||{}:this.$attrs)),f("span",{class:`${c}-tabs-tab__label`},e?f(Qt,null,f("div",{class:`${c}-tabs-tab__height-placeholder`}," "),f(Zt,{clsPrefix:c},{default:()=>f(ya,null)})):k?k():typeof $=="object"?$:ea($??u)),s&&this.type==="card"?f(ta,{clsPrefix:c,class:`${c}-tabs-tab__close`,onClick:this.handleClose,disabled:v}):null))}}),Ua=d("tabs",`
 box-sizing: border-box;
 width: 100%;
 display: flex;
 flex-direction: column;
 transition:
 background-color .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
`,[y("segment-type",[d("tabs-rail",[E("&.transition-disabled",[d("tabs-capsule",`
 transition: none;
 `)])])]),y("top",[d("tab-pane",`
 padding: var(--n-pane-padding-top) var(--n-pane-padding-right) var(--n-pane-padding-bottom) var(--n-pane-padding-left);
 `)]),y("left",[d("tab-pane",`
 padding: var(--n-pane-padding-right) var(--n-pane-padding-bottom) var(--n-pane-padding-left) var(--n-pane-padding-top);
 `)]),y("left, right",`
 flex-direction: row;
 `,[d("tabs-bar",`
 width: 2px;
 right: 0;
 transition:
 top .2s var(--n-bezier),
 max-height .2s var(--n-bezier),
 background-color .3s var(--n-bezier);
 `),d("tabs-tab",`
 padding: var(--n-tab-padding-vertical); 
 `)]),y("right",`
 flex-direction: row-reverse;
 `,[d("tab-pane",`
 padding: var(--n-pane-padding-left) var(--n-pane-padding-top) var(--n-pane-padding-right) var(--n-pane-padding-bottom);
 `),d("tabs-bar",`
 left: 0;
 `)]),y("bottom",`
 flex-direction: column-reverse;
 justify-content: flex-end;
 `,[d("tab-pane",`
 padding: var(--n-pane-padding-bottom) var(--n-pane-padding-right) var(--n-pane-padding-top) var(--n-pane-padding-left);
 `),d("tabs-bar",`
 top: 0;
 `)]),d("tabs-rail",`
 position: relative;
 padding: 3px;
 border-radius: var(--n-tab-border-radius);
 width: 100%;
 background-color: var(--n-color-segment);
 transition: background-color .3s var(--n-bezier);
 display: flex;
 align-items: center;
 `,[d("tabs-capsule",`
 border-radius: var(--n-tab-border-radius);
 position: absolute;
 pointer-events: none;
 background-color: var(--n-tab-color-segment);
 box-shadow: 0 1px 3px 0 rgba(0, 0, 0, .08);
 transition: transform 0.3s var(--n-bezier);
 `),d("tabs-tab-wrapper",`
 flex-basis: 0;
 flex-grow: 1;
 display: flex;
 align-items: center;
 justify-content: center;
 `,[d("tabs-tab",`
 overflow: hidden;
 border-radius: var(--n-tab-border-radius);
 width: 100%;
 display: flex;
 align-items: center;
 justify-content: center;
 `,[y("active",`
 font-weight: var(--n-font-weight-strong);
 color: var(--n-tab-text-color-active);
 `),E("&:hover",`
 color: var(--n-tab-text-color-hover);
 `)])])]),y("flex",[d("tabs-nav",`
 width: 100%;
 position: relative;
 `,[d("tabs-wrapper",`
 width: 100%;
 `,[d("tabs-tab",`
 margin-right: 0;
 `)])])]),d("tabs-nav",`
 box-sizing: border-box;
 line-height: 1.5;
 display: flex;
 transition: border-color .3s var(--n-bezier);
 `,[O("prefix, suffix",`
 display: flex;
 align-items: center;
 `),O("prefix","padding-right: 16px;"),O("suffix","padding-left: 16px;")]),y("top, bottom",[E(">",[d("tabs-nav",[d("tabs-nav-scroll-wrapper",[E("&::before",`
 top: 0;
 bottom: 0;
 left: 0;
 width: 20px;
 `),E("&::after",`
 top: 0;
 bottom: 0;
 right: 0;
 width: 20px;
 `),y("shadow-start",[E("&::before",`
 box-shadow: inset 10px 0 8px -8px rgba(0, 0, 0, .12);
 `)]),y("shadow-end",[E("&::after",`
 box-shadow: inset -10px 0 8px -8px rgba(0, 0, 0, .12);
 `)])])])])]),y("left, right",[d("tabs-nav-scroll-content",`
 flex-direction: column;
 `),E(">",[d("tabs-nav",[d("tabs-nav-scroll-wrapper",[E("&::before",`
 top: 0;
 left: 0;
 right: 0;
 height: 20px;
 `),E("&::after",`
 bottom: 0;
 left: 0;
 right: 0;
 height: 20px;
 `),y("shadow-start",[E("&::before",`
 box-shadow: inset 0 10px 8px -8px rgba(0, 0, 0, .12);
 `)]),y("shadow-end",[E("&::after",`
 box-shadow: inset 0 -10px 8px -8px rgba(0, 0, 0, .12);
 `)])])])])]),d("tabs-nav-scroll-wrapper",`
 flex: 1;
 position: relative;
 overflow: hidden;
 `,[d("tabs-nav-y-scroll",`
 height: 100%;
 width: 100%;
 overflow-y: auto; 
 scrollbar-width: none;
 `,[E("&::-webkit-scrollbar, &::-webkit-scrollbar-track-piece, &::-webkit-scrollbar-thumb",`
 width: 0;
 height: 0;
 display: none;
 `)]),E("&::before, &::after",`
 transition: box-shadow .3s var(--n-bezier);
 pointer-events: none;
 content: "";
 position: absolute;
 z-index: 1;
 `)]),d("tabs-nav-scroll-content",`
 display: flex;
 position: relative;
 min-width: 100%;
 min-height: 100%;
 width: fit-content;
 box-sizing: border-box;
 `),d("tabs-wrapper",`
 display: inline-flex;
 flex-wrap: nowrap;
 position: relative;
 `),d("tabs-tab-wrapper",`
 display: flex;
 flex-wrap: nowrap;
 flex-shrink: 0;
 flex-grow: 0;
 `),d("tabs-tab",`
 cursor: pointer;
 white-space: nowrap;
 flex-wrap: nowrap;
 display: inline-flex;
 align-items: center;
 color: var(--n-tab-text-color);
 font-size: var(--n-tab-font-size);
 background-clip: padding-box;
 padding: var(--n-tab-padding);
 transition:
 box-shadow .3s var(--n-bezier),
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 `,[y("disabled",{cursor:"not-allowed"}),O("close",`
 margin-left: 6px;
 transition:
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
 `),O("label",`
 display: flex;
 align-items: center;
 z-index: 1;
 `)]),d("tabs-bar",`
 position: absolute;
 bottom: 0;
 height: 2px;
 border-radius: 1px;
 background-color: var(--n-bar-color);
 transition:
 left .2s var(--n-bezier),
 max-width .2s var(--n-bezier),
 opacity .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 `,[E("&.transition-disabled",`
 transition: none;
 `),y("disabled",`
 background-color: var(--n-tab-text-color-disabled)
 `)]),d("tabs-pane-wrapper",`
 position: relative;
 overflow: hidden;
 transition: max-height .2s var(--n-bezier);
 `),d("tab-pane",`
 color: var(--n-pane-text-color);
 width: 100%;
 transition:
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier),
 opacity .2s var(--n-bezier);
 left: 0;
 right: 0;
 top: 0;
 `,[E("&.next-transition-leave-active, &.prev-transition-leave-active, &.next-transition-enter-active, &.prev-transition-enter-active",`
 transition:
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier),
 transform .2s var(--n-bezier),
 opacity .2s var(--n-bezier);
 `),E("&.next-transition-leave-active, &.prev-transition-leave-active",`
 position: absolute;
 `),E("&.next-transition-enter-from, &.prev-transition-leave-to",`
 transform: translateX(32px);
 opacity: 0;
 `),E("&.next-transition-leave-to, &.prev-transition-enter-from",`
 transform: translateX(-32px);
 opacity: 0;
 `),E("&.next-transition-leave-from, &.next-transition-enter-to, &.prev-transition-leave-from, &.prev-transition-enter-to",`
 transform: translateX(0);
 opacity: 1;
 `)]),d("tabs-tab-pad",`
 box-sizing: border-box;
 width: var(--n-tab-gap);
 flex-grow: 0;
 flex-shrink: 0;
 `),y("line-type, bar-type",[d("tabs-tab",`
 font-weight: var(--n-tab-font-weight);
 box-sizing: border-box;
 vertical-align: bottom;
 `,[E("&:hover",{color:"var(--n-tab-text-color-hover)"}),y("active",`
 color: var(--n-tab-text-color-active);
 font-weight: var(--n-tab-font-weight-active);
 `),y("disabled",{color:"var(--n-tab-text-color-disabled)"})])]),d("tabs-nav",[y("line-type",[y("top",[O("prefix, suffix",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `),d("tabs-nav-scroll-content",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `),d("tabs-bar",`
 bottom: -1px;
 `)]),y("left",[O("prefix, suffix",`
 border-right: 1px solid var(--n-tab-border-color);
 `),d("tabs-nav-scroll-content",`
 border-right: 1px solid var(--n-tab-border-color);
 `),d("tabs-bar",`
 right: -1px;
 `)]),y("right",[O("prefix, suffix",`
 border-left: 1px solid var(--n-tab-border-color);
 `),d("tabs-nav-scroll-content",`
 border-left: 1px solid var(--n-tab-border-color);
 `),d("tabs-bar",`
 left: -1px;
 `)]),y("bottom",[O("prefix, suffix",`
 border-top: 1px solid var(--n-tab-border-color);
 `),d("tabs-nav-scroll-content",`
 border-top: 1px solid var(--n-tab-border-color);
 `),d("tabs-bar",`
 top: -1px;
 `)]),O("prefix, suffix",`
 transition: border-color .3s var(--n-bezier);
 `),d("tabs-nav-scroll-content",`
 transition: border-color .3s var(--n-bezier);
 `),d("tabs-bar",`
 border-radius: 0;
 `)]),y("card-type",[O("prefix, suffix",`
 transition: border-color .3s var(--n-bezier);
 `),d("tabs-pad",`
 flex-grow: 1;
 transition: border-color .3s var(--n-bezier);
 `),d("tabs-tab-pad",`
 transition: border-color .3s var(--n-bezier);
 `),d("tabs-tab",`
 font-weight: var(--n-tab-font-weight);
 border: 1px solid var(--n-tab-border-color);
 background-color: var(--n-tab-color);
 box-sizing: border-box;
 position: relative;
 vertical-align: bottom;
 display: flex;
 justify-content: space-between;
 font-size: var(--n-tab-font-size);
 color: var(--n-tab-text-color);
 `,[y("addable",`
 padding-left: 8px;
 padding-right: 8px;
 font-size: 16px;
 justify-content: center;
 `,[O("height-placeholder",`
 width: 0;
 font-size: var(--n-tab-font-size);
 `),ra("disabled",[E("&:hover",`
 color: var(--n-tab-text-color-hover);
 `)])]),y("closable","padding-right: 8px;"),y("active",`
 background-color: #0000;
 font-weight: var(--n-tab-font-weight-active);
 color: var(--n-tab-text-color-active);
 `),y("disabled","color: var(--n-tab-text-color-disabled);")])]),y("left, right",`
 flex-direction: column; 
 `,[O("prefix, suffix",`
 padding: var(--n-tab-padding-vertical);
 `),d("tabs-wrapper",`
 flex-direction: column;
 `),d("tabs-tab-wrapper",`
 flex-direction: column;
 `,[d("tabs-tab-pad",`
 height: var(--n-tab-gap-vertical);
 width: 100%;
 `)])]),y("top",[y("card-type",[d("tabs-scroll-padding","border-bottom: 1px solid var(--n-tab-border-color);"),O("prefix, suffix",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `),d("tabs-tab",`
 border-top-left-radius: var(--n-tab-border-radius);
 border-top-right-radius: var(--n-tab-border-radius);
 `,[y("active",`
 border-bottom: 1px solid #0000;
 `)]),d("tabs-tab-pad",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `),d("tabs-pad",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `)])]),y("left",[y("card-type",[d("tabs-scroll-padding","border-right: 1px solid var(--n-tab-border-color);"),O("prefix, suffix",`
 border-right: 1px solid var(--n-tab-border-color);
 `),d("tabs-tab",`
 border-top-left-radius: var(--n-tab-border-radius);
 border-bottom-left-radius: var(--n-tab-border-radius);
 `,[y("active",`
 border-right: 1px solid #0000;
 `)]),d("tabs-tab-pad",`
 border-right: 1px solid var(--n-tab-border-color);
 `),d("tabs-pad",`
 border-right: 1px solid var(--n-tab-border-color);
 `)])]),y("right",[y("card-type",[d("tabs-scroll-padding","border-left: 1px solid var(--n-tab-border-color);"),O("prefix, suffix",`
 border-left: 1px solid var(--n-tab-border-color);
 `),d("tabs-tab",`
 border-top-right-radius: var(--n-tab-border-radius);
 border-bottom-right-radius: var(--n-tab-border-radius);
 `,[y("active",`
 border-left: 1px solid #0000;
 `)]),d("tabs-tab-pad",`
 border-left: 1px solid var(--n-tab-border-color);
 `),d("tabs-pad",`
 border-left: 1px solid var(--n-tab-border-color);
 `)])]),y("bottom",[y("card-type",[d("tabs-scroll-padding","border-top: 1px solid var(--n-tab-border-color);"),O("prefix, suffix",`
 border-top: 1px solid var(--n-tab-border-color);
 `),d("tabs-tab",`
 border-bottom-left-radius: var(--n-tab-border-radius);
 border-bottom-right-radius: var(--n-tab-border-radius);
 `,[y("active",`
 border-top: 1px solid #0000;
 `)]),d("tabs-tab-pad",`
 border-top: 1px solid var(--n-tab-border-color);
 `),d("tabs-pad",`
 border-top: 1px solid var(--n-tab-border-color);
 `)])])])]),tt=Va,Xa=Object.assign(Object.assign({},xt.props),{value:[String,Number],defaultValue:[String,Number],trigger:{type:String,default:"click"},type:{type:String,default:"bar"},closable:Boolean,justifyContent:String,size:String,placement:{type:String,default:"top"},tabStyle:[String,Object],tabClass:String,addTabStyle:[String,Object],addTabClass:String,barWidth:Number,paneClass:String,paneStyle:[String,Object],paneWrapperClass:String,paneWrapperStyle:[String,Object],addable:[Boolean,Object],tabsPadding:{type:Number,default:0},animated:Boolean,onBeforeLeave:Function,onAdd:Function,"onUpdate:value":[Function,Array],onUpdateValue:[Function,Array],onClose:[Function,Array],labelSize:String,activeName:[String,Number],onActiveNameChange:[Function,Array]}),qa=Ce({name:"Tabs",props:Xa,slots:Object,setup(e,{slots:c}){var u,v,x,_;const{mergedClsPrefixRef:m,inlineThemeDisabled:s,mergedComponentPropsRef:S}=na(e),k=xt("Tabs","-tabs",Ua,Ga,e,m),$=P(null),B=P(null),N=P(null),T=P(null),z=P(null),L=P(null),W=P(!0),M=P(!0),j=ut(e,["labelSize","size"]),Y=K(()=>{var n,o;if(j.value)return j.value;const b=(o=(n=S==null?void 0:S.value)===null||n===void 0?void 0:n.Tabs)===null||o===void 0?void 0:o.size;return b||"medium"}),F=ut(e,["activeName","value"]),w=P((v=(u=F.value)!==null&&u!==void 0?u:e.defaultValue)!==null&&v!==void 0?v:c.default?(_=(x=Ue(c.default())[0])===null||x===void 0?void 0:x.props)===null||_===void 0?void 0:_.name:null),h=_a(F,w),V={id:0},ae=K(()=>{if(!(!e.justifyContent||e.type==="card"))return{display:"flex",justifyContent:e.justifyContent}});qe(h,()=>{V.id=0,ue(),_e()});function re(){var n;const{value:o}=h;return o===null?null:(n=$.value)===null||n===void 0?void 0:n.querySelector(`[data-name="${o}"]`)}function je(n){if(e.type==="card")return;const{value:o}=B;if(!o)return;const b=o.style.opacity==="0";if(n){const C=`${m.value}-tabs-bar--disabled`,{barWidth:D,placement:X}=e;if(n.dataset.disabled==="true"?o.classList.add(C):o.classList.remove(C),["top","bottom"].includes(X)){if(Se(["top","maxHeight","height"]),typeof D=="number"&&n.offsetWidth>=D){const q=Math.floor((n.offsetWidth-D)/2)+n.offsetLeft;o.style.left=`${q}px`,o.style.maxWidth=`${D}px`}else o.style.left=`${n.offsetLeft}px`,o.style.maxWidth=`${n.offsetWidth}px`;o.style.width="8192px",b&&(o.style.transition="none"),o.offsetWidth,b&&(o.style.transition="",o.style.opacity="1")}else{if(Se(["left","maxWidth","width"]),typeof D=="number"&&n.offsetHeight>=D){const q=Math.floor((n.offsetHeight-D)/2)+n.offsetTop;o.style.top=`${q}px`,o.style.maxHeight=`${D}px`}else o.style.top=`${n.offsetTop}px`,o.style.maxHeight=`${n.offsetHeight}px`;o.style.height="8192px",b&&(o.style.transition="none"),o.offsetHeight,b&&(o.style.transition="",o.style.opacity="1")}}}function De(){if(e.type==="card")return;const{value:n}=B;n&&(n.style.opacity="0")}function Se(n){const{value:o}=B;if(o)for(const b of n)o.style[b]=""}function ue(){if(e.type==="card")return;const n=re();n?je(n):De()}function _e(){var n;const o=(n=z.value)===null||n===void 0?void 0:n.$el;if(!o)return;const b=re();if(!b)return;const{scrollLeft:C,offsetWidth:D}=o,{offsetLeft:X,offsetWidth:q}=b;C>X?o.scrollTo({top:0,left:X,behavior:"smooth"}):X+q>C+D&&o.scrollTo({top:0,left:X+q-D,behavior:"smooth"})}const pe=P(null);let ge=0,Q=null;function Me(n){const o=pe.value;if(o){ge=n.getBoundingClientRect().height;const b=`${ge}px`,C=()=>{o.style.height=b,o.style.maxHeight=b};Q?(C(),Q(),Q=null):Q=C}}function Ie(n){const o=pe.value;if(o){const b=n.getBoundingClientRect().height,C=()=>{document.body.offsetHeight,o.style.maxHeight=`${b}px`,o.style.height=`${Math.max(ge,b)}px`};Q?(Q(),Q=null,C()):Q=C}}function Ve(){const n=pe.value;if(n){n.style.maxHeight="",n.style.height="";const{paneWrapperStyle:o}=e;if(typeof o=="string")n.style.cssText=o;else if(o){const{maxHeight:b,height:C}=o;b!==void 0&&(n.style.maxHeight=b),C!==void 0&&(n.style.height=C)}}}const be={value:[]},fe=P("next");function me(n){const o=h.value;let b="next";for(const C of be.value){if(C===o)break;if(C===n){b="prev";break}}fe.value=b,Oe(n)}function Oe(n){const{onActiveNameChange:o,onUpdateValue:b,"onUpdate:value":C}=e;o&&Pe(o,n),b&&Pe(b,n),C&&Pe(C,n),w.value=n}function He(n){const{onClose:o}=e;o&&Pe(o,n)}function we(){const{value:n}=B;if(!n)return;const o="transition-disabled";n.classList.add(o),ue(),n.classList.remove(o)}const oe=P(null);function he({transitionDisabled:n}){const o=$.value;if(!o)return;n&&o.classList.add("transition-disabled");const b=re();b&&oe.value&&(oe.value.style.width=`${b.offsetWidth}px`,oe.value.style.height=`${b.offsetHeight}px`,oe.value.style.transform=`translateX(${b.offsetLeft-la(getComputedStyle(o).paddingLeft)}px)`,n&&oe.value.offsetWidth),n&&o.classList.remove("transition-disabled")}qe([h],()=>{e.type==="segment"&&Je(()=>{he({transitionDisabled:!1})})}),yt(()=>{e.type==="segment"&&he({transitionDisabled:!0})});let ke=0;function Ge(n){var o;if(n.contentRect.width===0&&n.contentRect.height===0||ke===n.contentRect.width)return;ke=n.contentRect.width;const{type:b}=e;if((b==="line"||b==="bar")&&we(),b!=="segment"){const{placement:C}=e;U((C==="top"||C==="bottom"?(o=z.value)===null||o===void 0?void 0:o.$el:L.value)||null)}}const $e=tt(Ge,64);qe([()=>e.justifyContent,()=>e.size],()=>{Je(()=>{const{type:n}=e;(n==="line"||n==="bar")&&we()})});const r=P(!1);function t(n){var o;const{target:b,contentRect:{width:C,height:D}}=n,X=b.parentElement.parentElement.offsetWidth,q=b.parentElement.parentElement.offsetHeight,{placement:ve}=e;if(!r.value)ve==="top"||ve==="bottom"?X<C&&(r.value=!0):q<D&&(r.value=!0);else{const{value:ye}=T;if(!ye)return;ve==="top"||ve==="bottom"?X-C>ye.$el.offsetWidth&&(r.value=!1):q-D>ye.$el.offsetHeight&&(r.value=!1)}U(((o=z.value)===null||o===void 0?void 0:o.$el)||null)}const p=tt(t,64);function I(){const{onAdd:n}=e;n&&n(),Je(()=>{const o=re(),{value:b}=z;!o||!b||b.scrollTo({left:o.offsetLeft,top:0,behavior:"smooth"})})}function U(n){if(!n)return;const{placement:o}=e;if(o==="top"||o==="bottom"){const{scrollLeft:b,scrollWidth:C,offsetWidth:D}=n;W.value=b<=0,M.value=b+D>=C}else{const{scrollTop:b,scrollHeight:C,offsetHeight:D}=n;W.value=b<=0,M.value=b+D>=C}}const ie=tt(n=>{U(n.target)},64);pa(ot,{triggerRef:ee(e,"trigger"),tabStyleRef:ee(e,"tabStyle"),tabClassRef:ee(e,"tabClass"),addTabStyleRef:ee(e,"addTabStyle"),addTabClassRef:ee(e,"addTabClass"),paneClassRef:ee(e,"paneClass"),paneStyleRef:ee(e,"paneStyle"),mergedClsPrefixRef:m,typeRef:ee(e,"type"),closableRef:ee(e,"closable"),valueRef:h,tabChangeIdRef:V,onBeforeLeaveRef:ee(e,"onBeforeLeave"),activateTab:me,handleClose:He,handleAdd:I}),Sa(()=>{ue(),_e()}),oa(()=>{const{value:n}=N;if(!n)return;const{value:o}=m,b=`${o}-tabs-nav-scroll-wrapper--shadow-start`,C=`${o}-tabs-nav-scroll-wrapper--shadow-end`;W.value?n.classList.remove(b):n.classList.add(b),M.value?n.classList.remove(C):n.classList.add(C)});const Fe={syncBarPosition:()=>{ue()}},xe=()=>{he({transitionDisabled:!0})},Te=K(()=>{const{value:n}=Y,{type:o}=e,b={card:"Card",bar:"Bar",line:"Line",segment:"Segment"}[o],C=`${n}${b}`,{self:{barColor:D,closeIconColor:X,closeIconColorHover:q,closeIconColorPressed:ve,tabColor:ye,tabBorderColor:St,paneTextColor:_t,tabFontWeight:wt,tabBorderRadius:kt,tabFontWeightActive:$t,colorSegment:Tt,fontWeightStrong:zt,tabColorSegment:Rt,closeSize:Pt,closeIconSize:Lt,closeColorHover:At,closeColorPressed:Bt,closeBorderRadius:Et,[Z("panePadding",n)]:ze,[Z("tabPadding",C)]:Nt,[Z("tabPaddingVertical",C)]:Wt,[Z("tabGap",C)]:jt,[Z("tabGap",`${C}Vertical`)]:Dt,[Z("tabTextColor",o)]:Mt,[Z("tabTextColorActive",o)]:It,[Z("tabTextColorHover",o)]:Vt,[Z("tabTextColorDisabled",o)]:Ot,[Z("tabFontSize",n)]:Ht},common:{cubicBezierEaseInOut:Gt}}=k.value;return{"--n-bezier":Gt,"--n-color-segment":Tt,"--n-bar-color":D,"--n-tab-font-size":Ht,"--n-tab-text-color":Mt,"--n-tab-text-color-active":It,"--n-tab-text-color-disabled":Ot,"--n-tab-text-color-hover":Vt,"--n-pane-text-color":_t,"--n-tab-border-color":St,"--n-tab-border-radius":kt,"--n-close-size":Pt,"--n-close-icon-size":Lt,"--n-close-color-hover":At,"--n-close-color-pressed":Bt,"--n-close-border-radius":Et,"--n-close-icon-color":X,"--n-close-icon-color-hover":q,"--n-close-icon-color-pressed":ve,"--n-tab-color":ye,"--n-tab-font-weight":wt,"--n-tab-font-weight-active":$t,"--n-tab-padding":Nt,"--n-tab-padding-vertical":Wt,"--n-tab-gap":jt,"--n-tab-gap-vertical":Dt,"--n-pane-padding-left":Re(ze,"left"),"--n-pane-padding-right":Re(ze,"right"),"--n-pane-padding-top":Re(ze,"top"),"--n-pane-padding-bottom":Re(ze,"bottom"),"--n-font-weight-strong":zt,"--n-tab-color-segment":Rt}}),le=s?ia("tabs",K(()=>`${Y.value[0]}${e.type[0]}`),Te,e):void 0;return Object.assign({mergedClsPrefix:m,mergedValue:h,renderedNames:new Set,segmentCapsuleElRef:oe,tabsPaneWrapperRef:pe,tabsElRef:$,barElRef:B,addTabInstRef:T,xScrollInstRef:z,scrollWrapperElRef:N,addTabFixed:r,tabWrapperStyle:ae,handleNavResize:$e,mergedSize:Y,handleScroll:ie,handleTabsResize:p,cssVars:s?void 0:Te,themeClass:le==null?void 0:le.themeClass,animationDirection:fe,renderNameListRef:be,yScrollElRef:L,handleSegmentResize:xe,onAnimationBeforeLeave:Me,onAnimationEnter:Ie,onAnimationAfterEnter:Ve,onRender:le==null?void 0:le.onRender},Fe)},render(){const{mergedClsPrefix:e,type:c,placement:u,addTabFixed:v,addable:x,mergedSize:_,renderNameListRef:m,onRender:s,paneWrapperClass:S,paneWrapperStyle:k,$slots:{default:$,prefix:B,suffix:N}}=this;s==null||s();const T=$?Ue($()).filter(w=>w.type.__TAB_PANE__===!0):[],z=$?Ue($()).filter(w=>w.type.__TAB__===!0):[],L=!z.length,W=c==="card",M=c==="segment",j=!W&&!M&&this.justifyContent;m.value=[];const Y=()=>{const w=f("div",{style:this.tabWrapperStyle,class:`${e}-tabs-wrapper`},j?null:f("div",{class:`${e}-tabs-scroll-padding`,style:u==="top"||u==="bottom"?{width:`${this.tabsPadding}px`}:{height:`${this.tabsPadding}px`}}),L?T.map((h,V)=>(m.value.push(h.props.name),at(f(nt,Object.assign({},h.props,{internalCreatedByPane:!0,internalLeftPadded:V!==0&&(!j||j==="center"||j==="start"||j==="end")}),h.children?{default:h.children.tab}:void 0)))):z.map((h,V)=>(m.value.push(h.props.name),at(V!==0&&!j?mt(h):h))),!v&&x&&W?gt(x,(L?T.length:z.length)!==0):null,j?null:f("div",{class:`${e}-tabs-scroll-padding`,style:{width:`${this.tabsPadding}px`}}));return f("div",{ref:"tabsElRef",class:`${e}-tabs-nav-scroll-content`},W&&x?f(Xe,{onResize:this.handleTabsResize},{default:()=>w}):w,W?f("div",{class:`${e}-tabs-pad`}):null,W?null:f("div",{ref:"barElRef",class:`${e}-tabs-bar`}))},F=M?"top":u;return f("div",{class:[`${e}-tabs`,this.themeClass,`${e}-tabs--${c}-type`,`${e}-tabs--${_}-size`,j&&`${e}-tabs--flex`,`${e}-tabs--${F}`],style:this.cssVars},f("div",{class:[`${e}-tabs-nav--${c}-type`,`${e}-tabs-nav--${F}`,`${e}-tabs-nav`]},it(B,w=>w&&f("div",{class:`${e}-tabs-nav__prefix`},w)),M?f(Xe,{onResize:this.handleSegmentResize},{default:()=>f("div",{class:`${e}-tabs-rail`,ref:"tabsElRef"},f("div",{class:`${e}-tabs-capsule`,ref:"segmentCapsuleElRef"},f("div",{class:`${e}-tabs-wrapper`},f("div",{class:`${e}-tabs-tab`}))),L?T.map((w,h)=>(m.value.push(w.props.name),f(nt,Object.assign({},w.props,{internalCreatedByPane:!0,internalLeftPadded:h!==0}),w.children?{default:w.children.tab}:void 0))):z.map((w,h)=>(m.value.push(w.props.name),h===0?w:mt(w))))}):f(Xe,{onResize:this.handleNavResize},{default:()=>f("div",{class:`${e}-tabs-nav-scroll-wrapper`,ref:"scrollWrapperElRef"},["top","bottom"].includes(F)?f(Ta,{ref:"xScrollInstRef",onScroll:this.handleScroll},{default:Y}):f("div",{class:`${e}-tabs-nav-y-scroll`,onScroll:this.handleScroll,ref:"yScrollElRef"},Y()))}),v&&x&&W?gt(x,!0):null,it(N,w=>w&&f("div",{class:`${e}-tabs-nav__suffix`},w))),L&&(this.animated&&(F==="top"||F==="bottom")?f("div",{ref:"tabsPaneWrapperRef",style:k,class:[`${e}-tabs-pane-wrapper`,S]},vt(T,this.mergedValue,this.renderedNames,this.onAnimationBeforeLeave,this.onAnimationEnter,this.onAnimationAfterEnter,this.animationDirection)):vt(T,this.mergedValue,this.renderedNames)))}});function vt(e,c,u,v,x,_,m){const s=[];return e.forEach(S=>{const{name:k,displayDirective:$,"display-directive":B}=S.props,N=z=>$===z||B===z,T=c===k;if(S.key!==void 0&&(S.key=k),T||N("show")||N("show:lazy")&&u.has(k)){u.has(k)||u.add(k);const z=!N("if");s.push(z?sa(S,[[da,T]]):S)}}),m?f(ca,{name:`${m}-transition`,onBeforeLeave:v,onEnter:x,onAfterEnter:_},{default:()=>s}):s}function gt(e,c){return f(nt,{ref:"addTabInstRef",key:"__addable",name:"__addable",internalCreatedByPane:!0,internalAddable:!0,internalLeftPadded:c,disabled:typeof e=="object"&&e.disabled})}function mt(e){const c=ua(e);return c.props?c.props.internalLeftPadded=!0:c.props={internalLeftPadded:!0},c}function at(e){return Array.isArray(e.dynamicProps)?e.dynamicProps.includes("internalLeftPadded")||e.dynamicProps.push("internalLeftPadded"):e.dynamicProps=["internalLeftPadded"],e}const Ja={key:0,class:"detail-stack"},Ka={style:{color:"#18a058"}},Ya={style:{color:"#d03050"}},Qa={class:"mapping-preview"},Za={class:"mapping-preview"},rt="8093",er=Ce({__name:"detail",setup(e){const c=ba(),u=va(),v=wa(),x=ma(),_=x.role==="admin"||x.role==="editor",m=Number(c.params.id),s=P(null),S=P([]),k=P([]),$=P([]),B=P("sessions"),N=P(!1),T=P(!1),z=P(!1),L=P(!1),W=P(!1),M=P(!1),j=P(!1),Y={online:"success",offline:"error",mounting:"warning",error:"error",unknown:"default"},F={online:"已挂载",offline:"未挂载",mounting:"挂载中",error:"挂载失败",unknown:"未知"},w={ssh_script:"宿主机脚本",docker_compose:"Docker Compose"},h=K(()=>{var t;const r=(((t=s.value)==null?void 0:t.agent_status)||"unknown").toLowerCase();return r==="attached"||r==="online"||r==="already_injected"?"online":r==="detached"||r==="offline"?"offline":r==="mounting"?"mounting":r==="error"?"error":"unknown"}),V=K(()=>{var t;const r=(((t=s.value)==null?void 0:t.launch_mode)||"ssh_script").toLowerCase();return w[r]||r}),ae=K(()=>{var r;return!((r=s.value)!=null&&r.transaction_mappings)||!Array.isArray(s.value.transaction_mappings)||s.value.transaction_mappings.length===0?"暂无交易码映射配置":JSON.stringify(s.value.transaction_mappings,null,2)});function re(r){const t={host:"host.docker.internal",port:rt},p=r.trim();if(!p)return t;try{const I=/^https?:\/\//i.test(p)?p:`http://${p}`,U=new URL(I);return{host:U.hostname||t.host,port:U.port||rt}}catch{const I=p.replace(/^https?:\/\//i,""),[U,ie]=I.split(":");return{host:U||t.host,port:ie||rt}}}const je=K(()=>{if(!s.value||(s.value.launch_mode||"ssh_script").toLowerCase()!=="docker_compose")return"当前应用不是 Docker Compose 模式。";const r=s.value.docker_service_name||s.value.name,t=s.value.docker_workdir||".",p=s.value.docker_compose_file||"docker-compose.yml",I=`${t.replace(/\/$/,"")}/.arex-recorder/arex-agent.jar`,U=s.value.docker_agent_path||"/opt/arex/arex-agent.jar",{host:ie,port:Fe}=re(s.value.docker_storage_url||"http://host.docker.internal:8093"),xe=r,Te=s.value.arex_app_id||s.value.name,le=Math.max(0,Math.min(100,Math.round((s.value.sample_rate??1)*100)));return["# Docker Compose AREX 启动模板",`workdir: ${t}`,`compose_file: ${p}`,`service_name: ${xe}`,"","override:","  services:",`    ${xe}:`,"      extra_hosts:",'        - "host.docker.internal:host-gateway"',"      environment:",`        JAVA_TOOL_OPTIONS: "-javaagent:${U} -Darex.service.name=${Te} -Darex.storage.service.host=${ie} -Darex.storage.service.port=${Fe} -Darex.record.rate=${le}"`,"      volumes:",`        - "${I}:${U}:ro"`,"","platform command:",`  cd ${t} && docker compose -f ${p} -f .arex-recorder/docker-compose.arex.override.yml up -d --force-recreate ${xe}`].join(`
`)}),De=K(()=>S.value.filter(r=>r.status==="done").length),Se=K(()=>S.value.filter(r=>r.status==="error").length),ue={idle:"default",active:"info",collecting:"warning",done:"success",error:"error"},_e={idle:"待开始",active:"录制中",collecting:"收集中",done:"已完成",error:"异常"},pe=[{title:"会话名称",key:"name",ellipsis:{tooltip:!0}},{title:"状态",key:"status",width:100,render:r=>f(Ye,{type:ue[r.status]??"default",size:"small"},()=>_e[r.status]||r.status)},{title:"录制数",key:"total_count",width:90},{title:"创建时间",key:"created_at",width:170,render:r=>Be(r.created_at)},{title:"操作",key:"actions",width:220,render:r=>f(ne,{size:4},()=>[f(R,{size:"tiny",onClick:()=>u.push(`/recording/sessions/${r.id}`)},()=>"查看详情"),..._&&r.status==="idle"?[f(R,{size:"tiny",type:"primary",onClick:()=>we(r.id)},()=>"开始录制")]:[],..._&&r.status==="active"?[f(R,{size:"tiny",type:"warning",onClick:()=>oe(r.id)},()=>"停止录制")]:[],f(R,{size:"tiny",onClick:()=>u.push(`/recording?application_id=${m}`)},()=>"全部会话")])}],ge=[{title:"名称",key:"name",render:r=>f(R,{text:!0,type:"primary",onClick:()=>u.push(`/testcases/${r.id}`)},()=>r.name)},{title:"请求",key:"request_uri",render:r=>f("span",[f("b",{style:"margin-right:4px"},r.request_method||"GET"),r.request_uri||"-"])},{title:"状态",key:"status",width:90},{title:"创建时间",key:"created_at",width:160,render:r=>Be(r.created_at)},{title:"操作",key:"actions",width:150,render:r=>f(ne,{size:4},()=>[f(R,{size:"tiny",onClick:()=>u.push(`/testcases/${r.id}`)},()=>"详情"),..._?[f(R,{size:"tiny",type:"primary",onClick:()=>u.push(`/replay?application_id=${m}&case_id=${r.id}`)},()=>"回放")]:[]])}],Q={DONE:"success",RUNNING:"info",FAILED:"error",PENDING:"default",CANCELLED:"warning"},Me={DONE:"已完成",RUNNING:"运行中",FAILED:"失败",PENDING:"待执行",CANCELLED:"已取消"},Ie=[{title:"任务名称",key:"name",render:r=>f(R,{text:!0,type:"primary",onClick:()=>u.push(`/results/${r.id}`)},()=>r.name||`任务 #${r.id}`)},{title:"状态",key:"status",width:90,render:r=>f(Ye,{type:Q[r.status]??"default",size:"small"},()=>Me[r.status]||r.status)},{title:"通过率",key:"pass_rate",width:90,render:r=>{const t=r.total||0;return t?`${((r.passed||0)/t*100).toFixed(1)}%`:"-"}},{title:"统计",key:"counts",width:120,render:r=>`${r.total||0}/${r.passed||0}/${r.failed||0}`},{title:"创建时间",key:"created_at",width:160,render:r=>Be(r.created_at)},{title:"操作",key:"actions",width:160,render:r=>f(ne,{size:4},()=>[f(R,{size:"tiny",onClick:()=>u.push(`/results/${r.id}`)},()=>"结果"),f(R,{size:"tiny",type:"info",onClick:()=>Ve(r.id)},()=>"报告")])}];async function Ve(r){var t,p;try{const I=await lt.getReport(r),U=new Blob([I.data],{type:"text/html;charset=utf-8"}),ie=URL.createObjectURL(U);window.open(ie,"_blank","noopener"),setTimeout(()=>URL.revokeObjectURL(ie),6e4)}catch(I){v.error(((p=(t=I.response)==null?void 0:t.data)==null?void 0:p.detail)||"加载报告失败")}}async function be(){await Promise.all([fe(),me(),Oe(),He()])}async function fe(){var r,t;try{const p=await Le.get(m);s.value=p.data}catch(p){v.error(((t=(r=p.response)==null?void 0:r.data)==null?void 0:t.detail)||"加载应用详情失败")}}async function me(){var r,t;N.value=!0;try{const p=await Ae.listSessions({application_id:m,limit:20});S.value=p.data}catch(p){S.value=[],v.error(((t=(r=p.response)==null?void 0:r.data)==null?void 0:t.detail)||"加载录制会话失败")}finally{N.value=!1}}async function Oe(){var r,t;T.value=!0;try{const p=await ga.list({application_id:m,limit:10});k.value=p.data}catch(p){k.value=[],v.error(((t=(r=p.response)==null?void 0:r.data)==null?void 0:t.detail)||"加载测试用例失败")}finally{T.value=!1}}async function He(){var r,t;z.value=!0;try{const p=await lt.list({application_id:m,limit:10});$.value=p.data}catch(p){$.value=[],v.error(((t=(r=p.response)==null?void 0:r.data)==null?void 0:t.detail)||"加载回放任务失败")}finally{z.value=!1}}async function we(r){var t,p;try{await Ae.startSession(r),v.success("录制已开始"),await me()}catch(I){v.error(((p=(t=I.response)==null?void 0:t.data)==null?void 0:p.detail)||"开始录制失败")}}async function oe(r){var t,p;try{await Ae.stopSession(r,{}),v.success("已停止录制，平台开始收集数据"),await me()}catch(I){v.error(((p=(t=I.response)==null?void 0:t.data)==null?void 0:p.detail)||"停止录制失败")}}async function he(){var r,t;L.value=!0;try{const p=await Le.testConnection(m);p.data.success?v.success("连接成功"):v.error(`连接失败：${p.data.message}`)}catch(p){v.error(((t=(r=p.response)==null?void 0:r.data)==null?void 0:t.detail)||"连接测试失败")}finally{L.value=!1}}async function ke(){var r,t;W.value=!0;try{await Le.mountAgent(m),v.info("Agent 挂载已启动，请稍候刷新状态"),setTimeout(()=>void fe(),3e3)}catch(p){v.error(((t=(r=p.response)==null?void 0:r.data)==null?void 0:t.detail)||"挂载失败")}finally{W.value=!1}}async function Ge(){var r,t;M.value=!0;try{await Le.unmountAgent(m),v.success("Agent 已卸载"),await fe()}catch(p){v.error(((t=(r=p.response)==null?void 0:r.data)==null?void 0:t.detail)||"卸载失败")}finally{M.value=!1}}async function $e(){var r,t,p;j.value=!0;try{const I=await Ae.createSession({application_id:m,name:`${((r=s.value)==null?void 0:r.name)||"应用"}-${new Date().toLocaleString("zh-CN",{hour12:!1}).replace(/[/: ]/g,"-")}`});v.success("录制会话已创建"),u.push(`/recording/sessions/${I.data.id}`)}catch(I){v.error(((p=(t=I.response)==null?void 0:t.data)==null?void 0:p.detail)||"创建录制会话失败")}finally{j.value=!1}}return yt(()=>{be()}),(r,t)=>(se(),de(a(ne),{vertical:"",size:16,class:"application-detail-page"},{default:i(()=>[l(a(ne),{justify:"space-between",align:"center",class:"page-toolbar"},{default:i(()=>[l(a(ha),null,{default:i(()=>[l(a(st),{onClick:t[0]||(t[0]=p=>a(u).push("/applications"))},{default:i(()=>[...t[11]||(t[11]=[g("应用管理",-1)])]),_:1}),l(a(st),null,{default:i(()=>{var p;return[g(A(((p=s.value)==null?void 0:p.name)||`应用 #${a(m)}`),1)]}),_:1})]),_:1}),l(a(ne),null,{default:i(()=>[l(a(R),{onClick:be},{default:i(()=>[...t[12]||(t[12]=[g("刷新",-1)])]),_:1}),l(a(R),{onClick:t[1]||(t[1]=p=>a(u).push(`/recording?application_id=${a(m)}`))},{default:i(()=>[...t[13]||(t[13]=[g("查看录制",-1)])]),_:1}),l(a(R),{onClick:t[2]||(t[2]=p=>a(u).push(`/replay?application_id=${a(m)}`))},{default:i(()=>[...t[14]||(t[14]=[g("发起回放",-1)])]),_:1}),a(_)?(se(),de(a(R),{key:0,type:"primary",onClick:$e,loading:j.value},{default:i(()=>[...t[15]||(t[15]=[g("+ 新建会话",-1)])]),_:1},8,["loading"])):ce("",!0)]),_:1})]),_:1}),s.value?(se(),fa("div",Ja,[l(a(pt),{cols:4,"x-gap":12,"y-gap":12},{default:i(()=>[l(a(te),null,{default:i(()=>[l(a(J),null,{default:i(()=>[l(a(Ee),{label:"最近会话数",value:S.value.length},null,8,["value"])]),_:1})]),_:1}),l(a(te),null,{default:i(()=>[l(a(J),null,{default:i(()=>[l(a(Ee),{label:"已完成会话"},{default:i(()=>[H("span",Ka,A(De.value),1)]),_:1})]),_:1})]),_:1}),l(a(te),null,{default:i(()=>[l(a(J),null,{default:i(()=>[l(a(Ee),{label:"异常会话"},{default:i(()=>[H("span",Ya,A(Se.value),1)]),_:1})]),_:1})]),_:1}),l(a(te),null,{default:i(()=>[l(a(J),null,{default:i(()=>[l(a(Ee),{label:"最新回放任务",value:$.value.length},null,8,["value"])]),_:1})]),_:1})]),_:1}),l(a(J),{title:"应用概览"},{"header-extra":i(()=>[l(a(ne),null,{default:i(()=>[l(a(Ye),{type:Y[h.value]||"default"},{default:i(()=>[g(A(F[h.value]||"未知"),1)]),_:1},8,["type"]),a(_)?(se(),de(a(R),{key:0,size:"small",onClick:he,loading:L.value},{default:i(()=>[...t[16]||(t[16]=[g("测试连接",-1)])]),_:1},8,["loading"])):ce("",!0),a(_)&&h.value!=="online"?(se(),de(a(R),{key:1,size:"small",type:"primary",onClick:ke,loading:W.value},{default:i(()=>[...t[17]||(t[17]=[g(" 挂载 Agent ",-1)])]),_:1},8,["loading"])):ce("",!0),a(_)&&h.value==="online"?(se(),de(a(R),{key:2,size:"small",type:"warning",onClick:Ge,loading:M.value},{default:i(()=>[...t[18]||(t[18]=[g(" 卸载 Agent ",-1)])]),_:1},8,["loading"])):ce("",!0)]),_:1})]),default:i(()=>[l(a(Ke),{bordered:"",column:2,"label-placement":"left"},{default:i(()=>[l(a(G),{label:"应用名称"},{default:i(()=>[g(A(s.value.name),1)]),_:1}),l(a(G),{label:"描述"},{default:i(()=>[g(A(s.value.description||"-"),1)]),_:1}),l(a(G),{label:"采样率"},{default:i(()=>[g(A(s.value.sample_rate??"-"),1)]),_:1}),l(a(G),{label:"创建时间"},{default:i(()=>[g(A(a(Be)(s.value.created_at)),1)]),_:1})]),_:1})]),_:1}),l(a(J),{title:"接入信息"},{default:i(()=>[l(a(Ke),{bordered:"",column:2,"label-placement":"left"},{default:i(()=>[l(a(G),{label:"宿主机"},{default:i(()=>[g(A(s.value.ssh_user)+"@"+A(s.value.ssh_host)+":"+A(s.value.ssh_port),1)]),_:1}),l(a(G),{label:"服务端口"},{default:i(()=>[g(A(s.value.service_port),1)]),_:1})]),_:1}),l(a(xa),{"arrow-placement":"right",style:{"margin-top":"12px"}},{default:i(()=>[l(a(dt),{title:"更多接入信息",name:"more-access"},{default:i(()=>[l(a(Ke),{bordered:"",column:2,"label-placement":"left"},{default:i(()=>[l(a(G),{label:"启动模式"},{default:i(()=>[g(A(V.value),1)]),_:1}),l(a(G),{label:"JVM 进程名"},{default:i(()=>[g(A(s.value.jvm_process_name||"-"),1)]),_:1}),l(a(G),{label:"AREX App ID"},{default:i(()=>[g(A(s.value.arex_app_id||s.value.name),1)]),_:1}),l(a(G),{label:"AREX Storage"},{default:i(()=>[g(A(s.value.arex_storage_url||"使用全局配置"),1)]),_:1}),l(a(G),{label:"Docker 工作目录"},{default:i(()=>[g(A(s.value.docker_workdir||"-"),1)]),_:1}),l(a(G),{label:"Compose 文件"},{default:i(()=>[g(A(s.value.docker_compose_file||"docker-compose.yml"),1)]),_:1}),l(a(G),{label:"Compose 服务名"},{default:i(()=>[g(A(s.value.docker_service_name||"-"),1)]),_:1}),l(a(G),{label:"Docker Storage"},{default:i(()=>[g(A(s.value.docker_storage_url||"使用平台默认 Docker storage URL"),1)]),_:1}),l(a(G),{label:"Agent 挂载路径"},{default:i(()=>[g(A(s.value.docker_agent_path||"/opt/arex/arex-agent.jar"),1)]),_:1}),l(a(G),{label:"Agent 状态"},{default:i(()=>[g(A(F[h.value]||"未知"),1)]),_:1})]),_:1})]),_:1}),l(a(dt),{title:"交易码映射",name:"tx-mappings"},{default:i(()=>[l(a(ne),{vertical:"",size:12},{default:i(()=>[l(a(Ne),{type:"info","show-icon":!1},{default:i(()=>[...t[19]||(t[19]=[g(" 回放时会按当前应用配置自动加载这份交易码映射。每个交易码一组规则，主要用于 SAT -> UAT 的字段适配。 字段路径支持 ",-1),H("code",null,"name",-1),g("、",-1),H("code",null,"customer.name",-1),g("、",-1),H("code",null,"items.0.name",-1),g("、",-1),H("code",null,"*.name",-1),g(" 这种写法。 ",-1)])]),_:1}),l(a(Ne),{type:"warning","show-icon":!1},{default:i(()=>[...t[20]||(t[20]=[g(" 规则类型支持 ",-1),H("code",null,"rename",-1),g("、",-1),H("code",null,"delete",-1),g("、",-1),H("code",null,"default",-1),g("、",-1),H("code",null,"set",-1),g("、",-1),H("code",null,"copy",-1),g("。 如果映射规则比较多，建议直接参考 ",-1),H("code",null,"docs/交易码映射模板.md",-1),g(" 的示例模板再填写。 ",-1)])]),_:1}),H("div",Qa,[H("pre",null,A(ae.value),1)])]),_:1})]),_:1})]),_:1}),l(a(Ne),{type:"info","show-icon":!1,style:{"margin-top":"16px"}},{default:i(()=>[...t[21]||(t[21]=[g(" 录制数据由目标 JVM 中的 AREX Agent 采集后同步到平台，页面仅展示已同步结果。 ",-1)])]),_:1})]),_:1}),s.value.launch_mode==="docker_compose"?(se(),de(a(J),{key:0,title:"Docker 启动模板"},{default:i(()=>[l(a(ne),{vertical:"",size:12},{default:i(()=>[l(a(Ne),{type:"info","show-icon":!1},{default:i(()=>[...t[22]||(t[22]=[g(" 这个模板由平台生成，目标容器只需要接受标准 Compose 约定，不需要修改业务代码或 start.sh。 ",-1)])]),_:1}),H("div",Za,[H("pre",null,A(je.value),1)])]),_:1})]),_:1})):ce("",!0),l(a(J),{title:"快捷操作"},{default:i(()=>[l(a(pt),{cols:3,"x-gap":12,"y-gap":12},{default:i(()=>[l(a(te),null,{default:i(()=>[l(a(R),{block:"",onClick:t[3]||(t[3]=p=>a(u).push(`/recording?application_id=${a(m)}`))},{default:i(()=>[...t[23]||(t[23]=[g("进入录制中心",-1)])]),_:1})]),_:1}),l(a(te),null,{default:i(()=>[l(a(R),{block:"",onClick:t[4]||(t[4]=p=>a(u).push(`/replay?application_id=${a(m)}`))},{default:i(()=>[...t[24]||(t[24]=[g("发起回放",-1)])]),_:1})]),_:1}),l(a(te),null,{default:i(()=>[a(_)?(se(),de(a(R),{key:0,block:"",type:"primary",onClick:$e,loading:j.value},{default:i(()=>[...t[25]||(t[25]=[g(" 新建会话 ",-1)])]),_:1},8,["loading"])):ce("",!0)]),_:1}),l(a(te),null,{default:i(()=>[l(a(R),{block:"",onClick:t[5]||(t[5]=p=>a(u).push("/replay/history"))},{default:i(()=>[...t[26]||(t[26]=[g("查看回放历史",-1)])]),_:1})]),_:1}),l(a(te),null,{default:i(()=>[l(a(R),{block:"",onClick:t[6]||(t[6]=p=>a(u).push(`/testcases?application_id=${a(m)}`))},{default:i(()=>[...t[27]||(t[27]=[g("查看测试用例",-1)])]),_:1})]),_:1}),l(a(te),null,{default:i(()=>[l(a(R),{block:"",onClick:be},{default:i(()=>[...t[28]||(t[28]=[g("刷新当前页",-1)])]),_:1})]),_:1})]),_:1})]),_:1}),l(a(qa),{value:B.value,"onUpdate:value":t[10]||(t[10]=p=>B.value=p),type:"line",animated:""},{default:i(()=>[l(a(et),{name:"sessions",tab:"最近录制会话"},{default:i(()=>[l(a(J),null,{"header-extra":i(()=>[l(a(R),{size:"small",onClick:t[7]||(t[7]=p=>a(u).push(`/recording?application_id=${a(m)}`))},{default:i(()=>[...t[29]||(t[29]=[g("进入录制中心",-1)])]),_:1})]),default:i(()=>[l(a(Qe),{columns:pe,data:S.value,loading:N.value,pagination:{pageSize:8}},null,8,["data","loading"])]),_:1})]),_:1}),l(a(et),{name:"cases",tab:"最近测试用例"},{default:i(()=>[l(a(J),null,{"header-extra":i(()=>[l(a(R),{size:"small",onClick:t[8]||(t[8]=p=>a(u).push(`/testcases?application_id=${a(m)}`))},{default:i(()=>[...t[30]||(t[30]=[g("全部用例",-1)])]),_:1})]),default:i(()=>[l(a(Qe),{columns:ge,data:k.value,loading:T.value,pagination:{pageSize:6}},null,8,["data","loading"])]),_:1})]),_:1}),l(a(et),{name:"replays",tab:"最近回放任务"},{default:i(()=>[l(a(J),null,{"header-extra":i(()=>[l(a(R),{size:"small",onClick:t[9]||(t[9]=p=>a(u).push("/replay/history"))},{default:i(()=>[...t[31]||(t[31]=[g("回放历史",-1)])]),_:1})]),default:i(()=>[l(a(Qe),{columns:Ie,data:$.value,loading:z.value,pagination:{pageSize:6}},null,8,["data","loading"])]),_:1})]),_:1})]),_:1},8,["value"])])):ce("",!0)]),_:1}))}}),_r=ka(er,[["__scopeId","data-v-98acf8d1"]]);export{_r as default};
