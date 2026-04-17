import{A as ke,m as I,r as B,p as Ye,d as he,q as fo,h as d,V as po,G as ht,a9 as Je,bv as ft,bn as vt,al as uo,ac as gt,v as le,aY as He,bw as lo,a3 as Te,a4 as Po,a as Ae,g as H,n as $,o as ce,N as Fo,u as De,j as Ce,l as Ne,aq as Z,c as vo,s as bt,y as Ie,a1 as Io,i as J,w as Re,Y as Oo,ak as Xe,aW as pt,S as mt,a0 as Ct,b1 as go,a8 as Mo,ar as Oe,e as L,ah as xt,t as ge,bx as mo,f as yt,by as wt,F as St,D as zt,am as Rt,an as kt,aK as Co,a2 as Tt,a5 as Pt,aL as Ft,aM as It}from"./index-D6LB0ej7.js";import{e as Ot,i as Mt,f as ro,l as bo,h as Le,m as Bt,n as $t,p as _t,V as xo,j as Et,B as Ht,a as Lt,b as At,d as ho,u as Dt,c as Nt}from"./Space-JgVsnMPf.js";import{a as Bo,d as Wt}from"./index-B6sC-FX3.js";import{u as yo}from"./get-I2R12OG2.js";function wo(e){return e&-e}class $o{constructor(t,n){this.l=t,this.min=n;const l=new Array(t+1);for(let r=0;r<t+1;++r)l[r]=0;this.ft=l}add(t,n){if(n===0)return;const{l,ft:r}=this;for(t+=1;t<=l;)r[t]+=n,t+=wo(t)}get(t){return this.sum(t+1)-this.sum(t)}sum(t){if(t===void 0&&(t=this.l),t<=0)return 0;const{ft:n,min:l,l:r}=this;if(t>r)throw new Error("[FinweckTree.sum]: `i` is larger than length.");let s=t*l;for(;t>0;)s+=n[t],t-=wo(t);return s}getBound(t){let n=0,l=this.l;for(;l>n;){const r=Math.floor((n+l)/2),s=this.sum(r);if(s>t){l=r;continue}else if(s<t){if(n===r)return this.sum(n+1)<=t?n+1:r;n=r}else return r}return n}}let Ge;function Vt(){return typeof document>"u"?!1:(Ge===void 0&&("matchMedia"in window?Ge=window.matchMedia("(pointer:coarse)").matches:Ge=!1),Ge)}let io;function So(){return typeof document>"u"?1:(io===void 0&&(io="chrome"in window?window.devicePixelRatio:1),io)}const _o="VVirtualListXScroll";function jt({columnsRef:e,renderColRef:t,renderItemWithColsRef:n}){const l=B(0),r=B(0),s=I(()=>{const g=e.value;if(g.length===0)return null;const m=new $o(g.length,0);return g.forEach((b,P)=>{m.add(P,b.width)}),m}),a=ke(()=>{const g=s.value;return g!==null?Math.max(g.getBound(r.value)-1,0):0}),i=g=>{const m=s.value;return m!==null?m.sum(g):0},f=ke(()=>{const g=s.value;return g!==null?Math.min(g.getBound(r.value+l.value)+1,e.value.length-1):0});return Ye(_o,{startIndexRef:a,endIndexRef:f,columnsRef:e,renderColRef:t,renderItemWithColsRef:n,getLeft:i}),{listWidthRef:l,scrollLeftRef:r}}const zo=he({name:"VirtualListRow",props:{index:{type:Number,required:!0},item:{type:Object,required:!0}},setup(){const{startIndexRef:e,endIndexRef:t,columnsRef:n,getLeft:l,renderColRef:r,renderItemWithColsRef:s}=fo(_o);return{startIndex:e,endIndex:t,columns:n,renderCol:r,renderItemWithCols:s,getLeft:l}},render(){const{startIndex:e,endIndex:t,columns:n,renderCol:l,renderItemWithCols:r,getLeft:s,item:a}=this;if(r!=null)return r({itemIndex:this.index,startColIndex:e,endColIndex:t,allColumns:n,item:a,getLeft:s});if(l!=null){const i=[];for(let f=e;f<=t;++f){const g=n[f];i.push(l({column:g,left:s(f),item:a}))}return i}return null}}),Kt=ro(".v-vl",{maxHeight:"inherit",height:"100%",overflow:"auto",minWidth:"1px"},[ro("&:not(.v-vl--show-scrollbar)",{scrollbarWidth:"none"},[ro("&::-webkit-scrollbar, &::-webkit-scrollbar-track-piece, &::-webkit-scrollbar-thumb",{width:0,height:0,display:"none"})])]),Ut=he({name:"VirtualList",inheritAttrs:!1,props:{showScrollbar:{type:Boolean,default:!0},columns:{type:Array,default:()=>[]},renderCol:Function,renderItemWithCols:Function,items:{type:Array,default:()=>[]},itemSize:{type:Number,required:!0},itemResizable:Boolean,itemsStyle:[String,Object],visibleItemsTag:{type:[String,Object],default:"div"},visibleItemsProps:Object,ignoreItemResize:Boolean,onScroll:Function,onWheel:Function,onResize:Function,defaultScrollKey:[Number,String],defaultScrollIndex:Number,keyField:{type:String,default:"key"},paddingTop:{type:[Number,String],default:0},paddingBottom:{type:[Number,String],default:0}},setup(e){const t=gt();Kt.mount({id:"vueuc/virtual-list",head:!0,anchorMetaName:Ot,ssr:t}),Je(()=>{const{defaultScrollIndex:h,defaultScrollKey:w}=e;h!=null?T({index:h}):w!=null&&T({key:w})});let n=!1,l=!1;ft(()=>{if(n=!1,!l){l=!0;return}T({top:k.value,left:a.value})}),vt(()=>{n=!0,l||(l=!0)});const r=ke(()=>{if(e.renderCol==null&&e.renderItemWithCols==null||e.columns.length===0)return;let h=0;return e.columns.forEach(w=>{h+=w.width}),h}),s=I(()=>{const h=new Map,{keyField:w}=e;return e.items.forEach((E,N)=>{h.set(E[w],N)}),h}),{scrollLeftRef:a,listWidthRef:i}=jt({columnsRef:le(e,"columns"),renderColRef:le(e,"renderCol"),renderItemWithColsRef:le(e,"renderItemWithCols")}),f=B(null),g=B(void 0),m=new Map,b=I(()=>{const{items:h,itemSize:w,keyField:E}=e,N=new $o(h.length,w);return h.forEach((j,G)=>{const W=j[E],U=m.get(W);U!==void 0&&N.add(G,U)}),N}),P=B(0),k=B(0),C=ke(()=>Math.max(b.value.getBound(k.value-uo(e.paddingTop))-1,0)),x=I(()=>{const{value:h}=g;if(h===void 0)return[];const{items:w,itemSize:E}=e,N=C.value,j=Math.min(N+Math.ceil(h/E+1),w.length-1),G=[];for(let W=N;W<=j;++W)G.push(w[W]);return G}),T=(h,w)=>{if(typeof h=="number"){K(h,w,"auto");return}const{left:E,top:N,index:j,key:G,position:W,behavior:U,debounce:q=!0}=h;if(E!==void 0||N!==void 0)K(E,N,U);else if(j!==void 0)A(j,U,q);else if(G!==void 0){const re=s.value.get(G);re!==void 0&&A(re,U,q)}else W==="bottom"?K(0,Number.MAX_SAFE_INTEGER,U):W==="top"&&K(0,0,U)};let R,S=null;function A(h,w,E){const{value:N}=b,j=N.sum(h)+uo(e.paddingTop);if(!E)f.value.scrollTo({left:0,top:j,behavior:w});else{R=h,S!==null&&window.clearTimeout(S),S=window.setTimeout(()=>{R=void 0,S=null},16);const{scrollTop:G,offsetHeight:W}=f.value;if(j>G){const U=N.get(h);j+U<=G+W||f.value.scrollTo({left:0,top:j+U-W,behavior:w})}else f.value.scrollTo({left:0,top:j,behavior:w})}}function K(h,w,E){f.value.scrollTo({left:h,top:w,behavior:E})}function V(h,w){var E,N,j;if(n||e.ignoreItemResize||Q(w.target))return;const{value:G}=b,W=s.value.get(h),U=G.get(W),q=(j=(N=(E=w.borderBoxSize)===null||E===void 0?void 0:E[0])===null||N===void 0?void 0:N.blockSize)!==null&&j!==void 0?j:w.contentRect.height;if(q===U)return;q-e.itemSize===0?m.delete(h):m.set(h,q-e.itemSize);const ae=q-U;if(ae===0)return;G.add(W,ae);const c=f.value;if(c!=null){if(R===void 0){const p=G.sum(W);c.scrollTop>p&&c.scrollBy(0,ae)}else if(W<R)c.scrollBy(0,ae);else if(W===R){const p=G.sum(W);q+p>c.scrollTop+c.offsetHeight&&c.scrollBy(0,ae)}X()}P.value++}const D=!Vt();let oe=!1;function te(h){var w;(w=e.onScroll)===null||w===void 0||w.call(e,h),(!D||!oe)&&X()}function ie(h){var w;if((w=e.onWheel)===null||w===void 0||w.call(e,h),D){const E=f.value;if(E!=null){if(h.deltaX===0&&(E.scrollTop===0&&h.deltaY<=0||E.scrollTop+E.offsetHeight>=E.scrollHeight&&h.deltaY>=0))return;h.preventDefault(),E.scrollTop+=h.deltaY/So(),E.scrollLeft+=h.deltaX/So(),X(),oe=!0,Mt(()=>{oe=!1})}}}function de(h){if(n||Q(h.target))return;if(e.renderCol==null&&e.renderItemWithCols==null){if(h.contentRect.height===g.value)return}else if(h.contentRect.height===g.value&&h.contentRect.width===i.value)return;g.value=h.contentRect.height,i.value=h.contentRect.width;const{onResize:w}=e;w!==void 0&&w(h)}function X(){const{value:h}=f;h!=null&&(k.value=h.scrollTop,a.value=h.scrollLeft)}function Q(h){let w=h;for(;w!==null;){if(w.style.display==="none")return!0;w=w.parentElement}return!1}return{listHeight:g,listStyle:{overflow:"auto"},keyToIndex:s,itemsStyle:I(()=>{const{itemResizable:h}=e,w=He(b.value.sum());return P.value,[e.itemsStyle,{boxSizing:"content-box",width:He(r.value),height:h?"":w,minHeight:h?w:"",paddingTop:He(e.paddingTop),paddingBottom:He(e.paddingBottom)}]}),visibleItemsStyle:I(()=>(P.value,{transform:`translateY(${He(b.value.sum(C.value))})`})),viewportItems:x,listElRef:f,itemsElRef:B(null),scrollTo:T,handleListResize:de,handleListScroll:te,handleListWheel:ie,handleItemResize:V}},render(){const{itemResizable:e,keyField:t,keyToIndex:n,visibleItemsTag:l}=this;return d(po,{onResize:this.handleListResize},{default:()=>{var r,s;return d("div",ht(this.$attrs,{class:["v-vl",this.showScrollbar&&"v-vl--show-scrollbar"],onScroll:this.handleListScroll,onWheel:this.handleListWheel,ref:"listElRef"}),[this.items.length!==0?d("div",{ref:"itemsElRef",class:"v-vl-items",style:this.itemsStyle},[d(l,Object.assign({class:"v-vl-visible-items",style:this.visibleItemsStyle},this.visibleItemsProps),{default:()=>{const{renderCol:a,renderItemWithCols:i}=this;return this.viewportItems.map(f=>{const g=f[t],m=n.get(g),b=a!=null?d(zo,{index:m,item:f}):void 0,P=i!=null?d(zo,{index:m,item:f}):void 0,k=this.$slots.default({item:f,renderedCols:b,renderedItemWithCols:P,index:m})[0];return e?d(po,{key:g,onResize:C=>this.handleItemResize(g,C)},{default:()=>k}):(k.key=g,k)})}})]):(s=(r=this.$slots).empty)===null||s===void 0?void 0:s.call(r)])}})}});function Eo(e,t){t&&(Je(()=>{const{value:n}=e;n&&lo.registerHandler(n,t)}),Te(e,(n,l)=>{l&&lo.unregisterHandler(l)},{deep:!1}),Po(()=>{const{value:n}=e;n&&lo.unregisterHandler(n)}))}function Ro(e){switch(typeof e){case"string":return e||void 0;case"number":return String(e);default:return}}function ao(e){const t=e.filter(n=>n!==void 0);if(t.length!==0)return t.length===1?t[0]:n=>{e.forEach(l=>{l&&l(n)})}}const qt=he({name:"Checkmark",render(){return d("svg",{xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 16 16"},d("g",{fill:"none"},d("path",{d:"M14.046 3.486a.75.75 0 0 1-.032 1.06l-7.93 7.474a.85.85 0 0 1-1.188-.022l-2.68-2.72a.75.75 0 1 1 1.068-1.053l2.234 2.267l7.468-7.038a.75.75 0 0 1 1.06.032z",fill:"currentColor"})))}}),Gt=he({name:"Empty",render(){return d("svg",{viewBox:"0 0 28 28",fill:"none",xmlns:"http://www.w3.org/2000/svg"},d("path",{d:"M26 7.5C26 11.0899 23.0899 14 19.5 14C15.9101 14 13 11.0899 13 7.5C13 3.91015 15.9101 1 19.5 1C23.0899 1 26 3.91015 26 7.5ZM16.8536 4.14645C16.6583 3.95118 16.3417 3.95118 16.1464 4.14645C15.9512 4.34171 15.9512 4.65829 16.1464 4.85355L18.7929 7.5L16.1464 10.1464C15.9512 10.3417 15.9512 10.6583 16.1464 10.8536C16.3417 11.0488 16.6583 11.0488 16.8536 10.8536L19.5 8.20711L22.1464 10.8536C22.3417 11.0488 22.6583 11.0488 22.8536 10.8536C23.0488 10.6583 23.0488 10.3417 22.8536 10.1464L20.2071 7.5L22.8536 4.85355C23.0488 4.65829 23.0488 4.34171 22.8536 4.14645C22.6583 3.95118 22.3417 3.95118 22.1464 4.14645L19.5 6.79289L16.8536 4.14645Z",fill:"currentColor"}),d("path",{d:"M25 22.75V12.5991C24.5572 13.0765 24.053 13.4961 23.5 13.8454V16H17.5L17.3982 16.0068C17.0322 16.0565 16.75 16.3703 16.75 16.75C16.75 18.2688 15.5188 19.5 14 19.5C12.4812 19.5 11.25 18.2688 11.25 16.75L11.2432 16.6482C11.1935 16.2822 10.8797 16 10.5 16H4.5V7.25C4.5 6.2835 5.2835 5.5 6.25 5.5H12.2696C12.4146 4.97463 12.6153 4.47237 12.865 4H6.25C4.45507 4 3 5.45507 3 7.25V22.75C3 24.5449 4.45507 26 6.25 26H21.75C23.5449 26 25 24.5449 25 22.75ZM4.5 22.75V17.5H9.81597L9.85751 17.7041C10.2905 19.5919 11.9808 21 14 21L14.215 20.9947C16.2095 20.8953 17.842 19.4209 18.184 17.5H23.5V22.75C23.5 23.7165 22.7165 24.5 21.75 24.5H6.25C5.2835 24.5 4.5 23.7165 4.5 22.75Z",fill:"currentColor"}))}}),Yt=he({props:{onFocus:Function,onBlur:Function},setup(e){return()=>d("div",{style:"width: 0; height: 0",tabindex:0,onFocus:e.onFocus,onBlur:e.onBlur})}}),Xt={iconSizeTiny:"28px",iconSizeSmall:"34px",iconSizeMedium:"40px",iconSizeLarge:"46px",iconSizeHuge:"52px"};function Zt(e){const{textColorDisabled:t,iconColor:n,textColor2:l,fontSizeTiny:r,fontSizeSmall:s,fontSizeMedium:a,fontSizeLarge:i,fontSizeHuge:f}=e;return Object.assign(Object.assign({},Xt),{fontSizeTiny:r,fontSizeSmall:s,fontSizeMedium:a,fontSizeLarge:i,fontSizeHuge:f,textColor:t,iconColor:n,extraTextColor:l})}const Ho={name:"Empty",common:Ae,self:Zt},Jt=H("empty",`
 display: flex;
 flex-direction: column;
 align-items: center;
 font-size: var(--n-font-size);
`,[$("icon",`
 width: var(--n-icon-size);
 height: var(--n-icon-size);
 font-size: var(--n-icon-size);
 line-height: var(--n-icon-size);
 color: var(--n-icon-color);
 transition:
 color .3s var(--n-bezier);
 `,[ce("+",[$("description",`
 margin-top: 8px;
 `)])]),$("description",`
 transition: color .3s var(--n-bezier);
 color: var(--n-text-color);
 `),$("extra",`
 text-align: center;
 transition: color .3s var(--n-bezier);
 margin-top: 12px;
 color: var(--n-extra-text-color);
 `)]),Qt=Object.assign(Object.assign({},Ce.props),{description:String,showDescription:{type:Boolean,default:!0},showIcon:{type:Boolean,default:!0},size:{type:String,default:"medium"},renderIcon:Function}),en=he({name:"Empty",props:Qt,slots:Object,setup(e){const{mergedClsPrefixRef:t,inlineThemeDisabled:n,mergedComponentPropsRef:l}=De(e),r=Ce("Empty","-empty",Jt,Ho,e,t),{localeRef:s}=Bo("Empty"),a=I(()=>{var m,b,P;return(m=e.description)!==null&&m!==void 0?m:(P=(b=l==null?void 0:l.value)===null||b===void 0?void 0:b.Empty)===null||P===void 0?void 0:P.description}),i=I(()=>{var m,b;return((b=(m=l==null?void 0:l.value)===null||m===void 0?void 0:m.Empty)===null||b===void 0?void 0:b.renderIcon)||(()=>d(Gt,null))}),f=I(()=>{const{size:m}=e,{common:{cubicBezierEaseInOut:b},self:{[Z("iconSize",m)]:P,[Z("fontSize",m)]:k,textColor:C,iconColor:x,extraTextColor:T}}=r.value;return{"--n-icon-size":P,"--n-font-size":k,"--n-bezier":b,"--n-text-color":C,"--n-icon-color":x,"--n-extra-text-color":T}}),g=n?Ne("empty",I(()=>{let m="";const{size:b}=e;return m+=b[0],m}),f,e):void 0;return{mergedClsPrefix:t,mergedRenderIcon:i,localizedDescription:I(()=>a.value||s.value.description),cssVars:n?void 0:f,themeClass:g==null?void 0:g.themeClass,onRender:g==null?void 0:g.onRender}},render(){const{$slots:e,mergedClsPrefix:t,onRender:n}=this;return n==null||n(),d("div",{class:[`${t}-empty`,this.themeClass],style:this.cssVars},this.showIcon?d("div",{class:`${t}-empty__icon`},e.icon?e.icon():d(Fo,{clsPrefix:t},{default:this.mergedRenderIcon})):null,this.showDescription?d("div",{class:`${t}-empty__description`},e.default?e.default():this.localizedDescription):null,e.extra?d("div",{class:`${t}-empty__extra`},e.extra()):null)}}),on={height:"calc(var(--n-option-height) * 7.6)",paddingTiny:"4px 0",paddingSmall:"4px 0",paddingMedium:"4px 0",paddingLarge:"4px 0",paddingHuge:"4px 0",optionPaddingTiny:"0 12px",optionPaddingSmall:"0 12px",optionPaddingMedium:"0 12px",optionPaddingLarge:"0 12px",optionPaddingHuge:"0 12px",loadingSize:"18px"};function tn(e){const{borderRadius:t,popoverColor:n,textColor3:l,dividerColor:r,textColor2:s,primaryColorPressed:a,textColorDisabled:i,primaryColor:f,opacityDisabled:g,hoverColor:m,fontSizeTiny:b,fontSizeSmall:P,fontSizeMedium:k,fontSizeLarge:C,fontSizeHuge:x,heightTiny:T,heightSmall:R,heightMedium:S,heightLarge:A,heightHuge:K}=e;return Object.assign(Object.assign({},on),{optionFontSizeTiny:b,optionFontSizeSmall:P,optionFontSizeMedium:k,optionFontSizeLarge:C,optionFontSizeHuge:x,optionHeightTiny:T,optionHeightSmall:R,optionHeightMedium:S,optionHeightLarge:A,optionHeightHuge:K,borderRadius:t,color:n,groupHeaderTextColor:l,actionDividerColor:r,optionTextColor:s,optionTextColorPressed:a,optionTextColorDisabled:i,optionTextColorActive:f,optionOpacityDisabled:g,optionCheckColor:f,optionColorPending:m,optionColorActive:"rgba(0, 0, 0, 0)",optionColorActivePending:m,actionTextColor:s,loadingColor:f})}const Lo=vo({name:"InternalSelectMenu",common:Ae,peers:{Scrollbar:bt,Empty:Ho},self:tn}),ko=he({name:"NBaseSelectGroupHeader",props:{clsPrefix:{type:String,required:!0},tmNode:{type:Object,required:!0}},setup(){const{renderLabelRef:e,renderOptionRef:t,labelFieldRef:n,nodePropsRef:l}=fo(bo);return{labelField:n,nodeProps:l,renderLabel:e,renderOption:t}},render(){const{clsPrefix:e,renderLabel:t,renderOption:n,nodeProps:l,tmNode:{rawNode:r}}=this,s=l==null?void 0:l(r),a=t?t(r,!1):Ie(r[this.labelField],r,!1),i=d("div",Object.assign({},s,{class:[`${e}-base-select-group-header`,s==null?void 0:s.class]}),a);return r.render?r.render({node:i,option:r}):n?n({node:i,option:r,selected:!1}):i}});function nn(e,t){return d(Io,{name:"fade-in-scale-up-transition"},{default:()=>e?d(Fo,{clsPrefix:t,class:`${t}-base-select-option__check`},{default:()=>d(qt)}):null})}const To=he({name:"NBaseSelectOption",props:{clsPrefix:{type:String,required:!0},tmNode:{type:Object,required:!0}},setup(e){const{valueRef:t,pendingTmNodeRef:n,multipleRef:l,valueSetRef:r,renderLabelRef:s,renderOptionRef:a,labelFieldRef:i,valueFieldRef:f,showCheckmarkRef:g,nodePropsRef:m,handleOptionClick:b,handleOptionMouseEnter:P}=fo(bo),k=ke(()=>{const{value:R}=n;return R?e.tmNode.key===R.key:!1});function C(R){const{tmNode:S}=e;S.disabled||b(R,S)}function x(R){const{tmNode:S}=e;S.disabled||P(R,S)}function T(R){const{tmNode:S}=e,{value:A}=k;S.disabled||A||P(R,S)}return{multiple:l,isGrouped:ke(()=>{const{tmNode:R}=e,{parent:S}=R;return S&&S.rawNode.type==="group"}),showCheckmark:g,nodeProps:m,isPending:k,isSelected:ke(()=>{const{value:R}=t,{value:S}=l;if(R===null)return!1;const A=e.tmNode.rawNode[f.value];if(S){const{value:K}=r;return K.has(A)}else return R===A}),labelField:i,renderLabel:s,renderOption:a,handleMouseMove:T,handleMouseEnter:x,handleClick:C}},render(){const{clsPrefix:e,tmNode:{rawNode:t},isSelected:n,isPending:l,isGrouped:r,showCheckmark:s,nodeProps:a,renderOption:i,renderLabel:f,handleClick:g,handleMouseEnter:m,handleMouseMove:b}=this,P=nn(n,e),k=f?[f(t,n),s&&P]:[Ie(t[this.labelField],t,n),s&&P],C=a==null?void 0:a(t),x=d("div",Object.assign({},C,{class:[`${e}-base-select-option`,t.class,C==null?void 0:C.class,{[`${e}-base-select-option--disabled`]:t.disabled,[`${e}-base-select-option--selected`]:n,[`${e}-base-select-option--grouped`]:r,[`${e}-base-select-option--pending`]:l,[`${e}-base-select-option--show-checkmark`]:s}],style:[(C==null?void 0:C.style)||"",t.style||""],onClick:ao([g,C==null?void 0:C.onClick]),onMouseenter:ao([m,C==null?void 0:C.onMouseenter]),onMousemove:ao([b,C==null?void 0:C.onMousemove])}),d("div",{class:`${e}-base-select-option__content`},k));return t.render?t.render({node:x,option:t,selected:n}):i?i({node:x,option:t,selected:n}):x}}),ln=H("base-select-menu",`
 line-height: 1.5;
 outline: none;
 z-index: 0;
 position: relative;
 border-radius: var(--n-border-radius);
 transition:
 background-color .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier);
 background-color: var(--n-color);
`,[H("scrollbar",`
 max-height: var(--n-height);
 `),H("virtual-list",`
 max-height: var(--n-height);
 `),H("base-select-option",`
 min-height: var(--n-option-height);
 font-size: var(--n-option-font-size);
 display: flex;
 align-items: center;
 `,[$("content",`
 z-index: 1;
 white-space: nowrap;
 text-overflow: ellipsis;
 overflow: hidden;
 `)]),H("base-select-group-header",`
 min-height: var(--n-option-height);
 font-size: .93em;
 display: flex;
 align-items: center;
 `),H("base-select-menu-option-wrapper",`
 position: relative;
 width: 100%;
 `),$("loading, empty",`
 display: flex;
 padding: 12px 32px;
 flex: 1;
 justify-content: center;
 `),$("loading",`
 color: var(--n-loading-color);
 font-size: var(--n-loading-size);
 `),$("header",`
 padding: 8px var(--n-option-padding-left);
 font-size: var(--n-option-font-size);
 transition: 
 color .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 border-bottom: 1px solid var(--n-action-divider-color);
 color: var(--n-action-text-color);
 `),$("action",`
 padding: 8px var(--n-option-padding-left);
 font-size: var(--n-option-font-size);
 transition: 
 color .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 border-top: 1px solid var(--n-action-divider-color);
 color: var(--n-action-text-color);
 `),H("base-select-group-header",`
 position: relative;
 cursor: default;
 padding: var(--n-option-padding);
 color: var(--n-group-header-text-color);
 `),H("base-select-option",`
 cursor: pointer;
 position: relative;
 padding: var(--n-option-padding);
 transition:
 color .3s var(--n-bezier),
 opacity .3s var(--n-bezier);
 box-sizing: border-box;
 color: var(--n-option-text-color);
 opacity: 1;
 `,[J("show-checkmark",`
 padding-right: calc(var(--n-option-padding-right) + 20px);
 `),ce("&::before",`
 content: "";
 position: absolute;
 left: 4px;
 right: 4px;
 top: 0;
 bottom: 0;
 border-radius: var(--n-border-radius);
 transition: background-color .3s var(--n-bezier);
 `),ce("&:active",`
 color: var(--n-option-text-color-pressed);
 `),J("grouped",`
 padding-left: calc(var(--n-option-padding-left) * 1.5);
 `),J("pending",[ce("&::before",`
 background-color: var(--n-option-color-pending);
 `)]),J("selected",`
 color: var(--n-option-text-color-active);
 `,[ce("&::before",`
 background-color: var(--n-option-color-active);
 `),J("pending",[ce("&::before",`
 background-color: var(--n-option-color-active-pending);
 `)])]),J("disabled",`
 cursor: not-allowed;
 `,[Re("selected",`
 color: var(--n-option-text-color-disabled);
 `),J("selected",`
 opacity: var(--n-option-opacity-disabled);
 `)]),$("check",`
 font-size: 16px;
 position: absolute;
 right: calc(var(--n-option-padding-right) - 4px);
 top: calc(50% - 7px);
 color: var(--n-option-check-color);
 transition: color .3s var(--n-bezier);
 `,[Oo({enterScale:"0.5"})])])]),rn=he({name:"InternalSelectMenu",props:Object.assign(Object.assign({},Ce.props),{clsPrefix:{type:String,required:!0},scrollable:{type:Boolean,default:!0},treeMate:{type:Object,required:!0},multiple:Boolean,size:{type:String,default:"medium"},value:{type:[String,Number,Array],default:null},autoPending:Boolean,virtualScroll:{type:Boolean,default:!0},show:{type:Boolean,default:!0},labelField:{type:String,default:"label"},valueField:{type:String,default:"value"},loading:Boolean,focusable:Boolean,renderLabel:Function,renderOption:Function,nodeProps:Function,showCheckmark:{type:Boolean,default:!0},onMousedown:Function,onScroll:Function,onFocus:Function,onBlur:Function,onKeyup:Function,onKeydown:Function,onTabOut:Function,onMouseenter:Function,onMouseleave:Function,onResize:Function,resetMenuOnOptionsChange:{type:Boolean,default:!0},inlineThemeDisabled:Boolean,scrollbarProps:Object,onToggle:Function}),setup(e){const{mergedClsPrefixRef:t,mergedRtlRef:n,mergedComponentPropsRef:l}=De(e),r=go("InternalSelectMenu",n,t),s=Ce("InternalSelectMenu","-internal-select-menu",ln,Lo,e,le(e,"clsPrefix")),a=B(null),i=B(null),f=B(null),g=I(()=>e.treeMate.getFlattenedNodes()),m=I(()=>Bt(g.value)),b=B(null);function P(){const{treeMate:c}=e;let p=null;const{value:Y}=e;Y===null?p=c.getFirstAvailableNode():(e.multiple?p=c.getNode((Y||[])[(Y||[]).length-1]):p=c.getNode(Y),(!p||p.disabled)&&(p=c.getFirstAvailableNode())),N(p||null)}function k(){const{value:c}=b;c&&!e.treeMate.getNode(c.key)&&(b.value=null)}let C;Te(()=>e.show,c=>{c?C=Te(()=>e.treeMate,()=>{e.resetMenuOnOptionsChange?(e.autoPending?P():k(),Mo(j)):k()},{immediate:!0}):C==null||C()},{immediate:!0}),Po(()=>{C==null||C()});const x=I(()=>uo(s.value.self[Z("optionHeight",e.size)])),T=I(()=>Oe(s.value.self[Z("padding",e.size)])),R=I(()=>e.multiple&&Array.isArray(e.value)?new Set(e.value):new Set),S=I(()=>{const c=g.value;return c&&c.length===0}),A=I(()=>{var c,p;return(p=(c=l==null?void 0:l.value)===null||c===void 0?void 0:c.Select)===null||p===void 0?void 0:p.renderEmpty});function K(c){const{onToggle:p}=e;p&&p(c)}function V(c){const{onScroll:p}=e;p&&p(c)}function D(c){var p;(p=f.value)===null||p===void 0||p.sync(),V(c)}function oe(){var c;(c=f.value)===null||c===void 0||c.sync()}function te(){const{value:c}=b;return c||null}function ie(c,p){p.disabled||N(p,!1)}function de(c,p){p.disabled||K(p)}function X(c){var p;Le(c,"action")||(p=e.onKeyup)===null||p===void 0||p.call(e,c)}function Q(c){var p;Le(c,"action")||(p=e.onKeydown)===null||p===void 0||p.call(e,c)}function h(c){var p;(p=e.onMousedown)===null||p===void 0||p.call(e,c),!e.focusable&&c.preventDefault()}function w(){const{value:c}=b;c&&N(c.getNext({loop:!0}),!0)}function E(){const{value:c}=b;c&&N(c.getPrev({loop:!0}),!0)}function N(c,p=!1){b.value=c,p&&j()}function j(){var c,p;const Y=b.value;if(!Y)return;const ue=m.value(Y.key);ue!==null&&(e.virtualScroll?(c=i.value)===null||c===void 0||c.scrollTo({index:ue}):(p=f.value)===null||p===void 0||p.scrollTo({index:ue,elSize:x.value}))}function G(c){var p,Y;!((p=a.value)===null||p===void 0)&&p.contains(c.target)&&((Y=e.onFocus)===null||Y===void 0||Y.call(e,c))}function W(c){var p,Y;!((p=a.value)===null||p===void 0)&&p.contains(c.relatedTarget)||(Y=e.onBlur)===null||Y===void 0||Y.call(e,c)}Ye(bo,{handleOptionMouseEnter:ie,handleOptionClick:de,valueSetRef:R,pendingTmNodeRef:b,nodePropsRef:le(e,"nodeProps"),showCheckmarkRef:le(e,"showCheckmark"),multipleRef:le(e,"multiple"),valueRef:le(e,"value"),renderLabelRef:le(e,"renderLabel"),renderOptionRef:le(e,"renderOption"),labelFieldRef:le(e,"labelField"),valueFieldRef:le(e,"valueField")}),Ye($t,a),Je(()=>{const{value:c}=f;c&&c.sync()});const U=I(()=>{const{size:c}=e,{common:{cubicBezierEaseInOut:p},self:{height:Y,borderRadius:ue,color:xe,groupHeaderTextColor:fe,actionDividerColor:se,optionTextColorPressed:ye,optionTextColor:be,optionTextColorDisabled:pe,optionTextColorActive:Me,optionOpacityDisabled:Be,optionCheckColor:Se,actionTextColor:ze,optionColorPending:$e,optionColorActive:_e,loadingColor:Ee,loadingSize:Pe,optionColorActivePending:Fe,[Z("optionFontSize",c)]:ve,[Z("optionHeight",c)]:u,[Z("optionPadding",c)]:y}}=s.value;return{"--n-height":Y,"--n-action-divider-color":se,"--n-action-text-color":ze,"--n-bezier":p,"--n-border-radius":ue,"--n-color":xe,"--n-option-font-size":ve,"--n-group-header-text-color":fe,"--n-option-check-color":Se,"--n-option-color-pending":$e,"--n-option-color-active":_e,"--n-option-color-active-pending":Fe,"--n-option-height":u,"--n-option-opacity-disabled":Be,"--n-option-text-color":be,"--n-option-text-color-active":Me,"--n-option-text-color-disabled":pe,"--n-option-text-color-pressed":ye,"--n-option-padding":y,"--n-option-padding-left":Oe(y,"left"),"--n-option-padding-right":Oe(y,"right"),"--n-loading-color":Ee,"--n-loading-size":Pe}}),{inlineThemeDisabled:q}=e,re=q?Ne("internal-select-menu",I(()=>e.size[0]),U,e):void 0,ae={selfRef:a,next:w,prev:E,getPendingTmNode:te};return Eo(a,e.onResize),Object.assign({mergedTheme:s,mergedClsPrefix:t,rtlEnabled:r,virtualListRef:i,scrollbarRef:f,itemSize:x,padding:T,flattenedNodes:g,empty:S,mergedRenderEmpty:A,virtualListContainer(){const{value:c}=i;return c==null?void 0:c.listElRef},virtualListContent(){const{value:c}=i;return c==null?void 0:c.itemsElRef},doScroll:V,handleFocusin:G,handleFocusout:W,handleKeyUp:X,handleKeyDown:Q,handleMouseDown:h,handleVirtualListResize:oe,handleVirtualListScroll:D,cssVars:q?void 0:U,themeClass:re==null?void 0:re.themeClass,onRender:re==null?void 0:re.onRender},ae)},render(){const{$slots:e,virtualScroll:t,clsPrefix:n,mergedTheme:l,themeClass:r,onRender:s}=this;return s==null||s(),d("div",{ref:"selfRef",tabindex:this.focusable?0:-1,class:[`${n}-base-select-menu`,`${n}-base-select-menu--${this.size}-size`,this.rtlEnabled&&`${n}-base-select-menu--rtl`,r,this.multiple&&`${n}-base-select-menu--multiple`],style:this.cssVars,onFocusin:this.handleFocusin,onFocusout:this.handleFocusout,onKeyup:this.handleKeyUp,onKeydown:this.handleKeyDown,onMousedown:this.handleMouseDown,onMouseenter:this.onMouseenter,onMouseleave:this.onMouseleave},Xe(e.header,a=>a&&d("div",{class:`${n}-base-select-menu__header`,"data-header":!0,key:"header"},a)),this.loading?d("div",{class:`${n}-base-select-menu__loading`},d(pt,{clsPrefix:n,strokeWidth:20})):this.empty?d("div",{class:`${n}-base-select-menu__empty`,"data-empty":!0},Ct(e.empty,()=>{var a;return[((a=this.mergedRenderEmpty)===null||a===void 0?void 0:a.call(this))||d(en,{theme:l.peers.Empty,themeOverrides:l.peerOverrides.Empty,size:this.size})]})):d(mt,Object.assign({ref:"scrollbarRef",theme:l.peers.Scrollbar,themeOverrides:l.peerOverrides.Scrollbar,scrollable:this.scrollable,container:t?this.virtualListContainer:void 0,content:t?this.virtualListContent:void 0,onScroll:t?void 0:this.doScroll},this.scrollbarProps),{default:()=>t?d(Ut,{ref:"virtualListRef",class:`${n}-virtual-list`,items:this.flattenedNodes,itemSize:this.itemSize,showScrollbar:!1,paddingTop:this.padding.top,paddingBottom:this.padding.bottom,onResize:this.handleVirtualListResize,onScroll:this.handleVirtualListScroll,itemResizable:!0},{default:({item:a})=>a.isGroup?d(ko,{key:a.key,clsPrefix:n,tmNode:a}):a.ignored?null:d(To,{clsPrefix:n,key:a.key,tmNode:a})}):d("div",{class:`${n}-base-select-menu-option-wrapper`,style:{paddingTop:this.padding.top,paddingBottom:this.padding.bottom}},this.flattenedNodes.map(a=>a.isGroup?d(ko,{key:a.key,clsPrefix:n,tmNode:a}):d(To,{clsPrefix:n,key:a.key,tmNode:a})))}),Xe(e.action,a=>a&&[d("div",{class:`${n}-base-select-menu__action`,"data-action":!0,key:"action"},a),d(Yt,{onFocus:this.onTabOut,key:"focus-detector"})]))}}),an={closeIconSizeTiny:"12px",closeIconSizeSmall:"12px",closeIconSizeMedium:"14px",closeIconSizeLarge:"14px",closeSizeTiny:"16px",closeSizeSmall:"16px",closeSizeMedium:"18px",closeSizeLarge:"18px",padding:"0 7px",closeMargin:"0 0 0 4px"};function sn(e){const{textColor2:t,primaryColorHover:n,primaryColorPressed:l,primaryColor:r,infoColor:s,successColor:a,warningColor:i,errorColor:f,baseColor:g,borderColor:m,opacityDisabled:b,tagColor:P,closeIconColor:k,closeIconColorHover:C,closeIconColorPressed:x,borderRadiusSmall:T,fontSizeMini:R,fontSizeTiny:S,fontSizeSmall:A,fontSizeMedium:K,heightMini:V,heightTiny:D,heightSmall:oe,heightMedium:te,closeColorHover:ie,closeColorPressed:de,buttonColor2Hover:X,buttonColor2Pressed:Q,fontWeightStrong:h}=e;return Object.assign(Object.assign({},an),{closeBorderRadius:T,heightTiny:V,heightSmall:D,heightMedium:oe,heightLarge:te,borderRadius:T,opacityDisabled:b,fontSizeTiny:R,fontSizeSmall:S,fontSizeMedium:A,fontSizeLarge:K,fontWeightStrong:h,textColorCheckable:t,textColorHoverCheckable:t,textColorPressedCheckable:t,textColorChecked:g,colorCheckable:"#0000",colorHoverCheckable:X,colorPressedCheckable:Q,colorChecked:r,colorCheckedHover:n,colorCheckedPressed:l,border:`1px solid ${m}`,textColor:t,color:P,colorBordered:"rgb(250, 250, 252)",closeIconColor:k,closeIconColorHover:C,closeIconColorPressed:x,closeColorHover:ie,closeColorPressed:de,borderPrimary:`1px solid ${L(r,{alpha:.3})}`,textColorPrimary:r,colorPrimary:L(r,{alpha:.12}),colorBorderedPrimary:L(r,{alpha:.1}),closeIconColorPrimary:r,closeIconColorHoverPrimary:r,closeIconColorPressedPrimary:r,closeColorHoverPrimary:L(r,{alpha:.12}),closeColorPressedPrimary:L(r,{alpha:.18}),borderInfo:`1px solid ${L(s,{alpha:.3})}`,textColorInfo:s,colorInfo:L(s,{alpha:.12}),colorBorderedInfo:L(s,{alpha:.1}),closeIconColorInfo:s,closeIconColorHoverInfo:s,closeIconColorPressedInfo:s,closeColorHoverInfo:L(s,{alpha:.12}),closeColorPressedInfo:L(s,{alpha:.18}),borderSuccess:`1px solid ${L(a,{alpha:.3})}`,textColorSuccess:a,colorSuccess:L(a,{alpha:.12}),colorBorderedSuccess:L(a,{alpha:.1}),closeIconColorSuccess:a,closeIconColorHoverSuccess:a,closeIconColorPressedSuccess:a,closeColorHoverSuccess:L(a,{alpha:.12}),closeColorPressedSuccess:L(a,{alpha:.18}),borderWarning:`1px solid ${L(i,{alpha:.35})}`,textColorWarning:i,colorWarning:L(i,{alpha:.15}),colorBorderedWarning:L(i,{alpha:.12}),closeIconColorWarning:i,closeIconColorHoverWarning:i,closeIconColorPressedWarning:i,closeColorHoverWarning:L(i,{alpha:.12}),closeColorPressedWarning:L(i,{alpha:.18}),borderError:`1px solid ${L(f,{alpha:.23})}`,textColorError:f,colorError:L(f,{alpha:.1}),colorBorderedError:L(f,{alpha:.08}),closeIconColorError:f,closeIconColorHoverError:f,closeIconColorPressedError:f,closeColorHoverError:L(f,{alpha:.12}),closeColorPressedError:L(f,{alpha:.18})})}const cn={name:"Tag",common:Ae,self:sn},dn={color:Object,type:{type:String,default:"default"},round:Boolean,size:String,closable:Boolean,disabled:{type:Boolean,default:void 0}},un=H("tag",`
 --n-close-margin: var(--n-close-margin-top) var(--n-close-margin-right) var(--n-close-margin-bottom) var(--n-close-margin-left);
 white-space: nowrap;
 position: relative;
 box-sizing: border-box;
 cursor: default;
 display: inline-flex;
 align-items: center;
 flex-wrap: nowrap;
 padding: var(--n-padding);
 border-radius: var(--n-border-radius);
 color: var(--n-text-color);
 background-color: var(--n-color);
 transition: 
 border-color .3s var(--n-bezier),
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier),
 opacity .3s var(--n-bezier);
 line-height: 1;
 height: var(--n-height);
 font-size: var(--n-font-size);
`,[J("strong",`
 font-weight: var(--n-font-weight-strong);
 `),$("border",`
 pointer-events: none;
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 border-radius: inherit;
 border: var(--n-border);
 transition: border-color .3s var(--n-bezier);
 `),$("icon",`
 display: flex;
 margin: 0 4px 0 0;
 color: var(--n-text-color);
 transition: color .3s var(--n-bezier);
 font-size: var(--n-avatar-size-override);
 `),$("avatar",`
 display: flex;
 margin: 0 6px 0 0;
 `),$("close",`
 margin: var(--n-close-margin);
 transition:
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
 `),J("round",`
 padding: 0 calc(var(--n-height) / 3);
 border-radius: calc(var(--n-height) / 2);
 `,[$("icon",`
 margin: 0 4px 0 calc((var(--n-height) - 8px) / -2);
 `),$("avatar",`
 margin: 0 6px 0 calc((var(--n-height) - 8px) / -2);
 `),J("closable",`
 padding: 0 calc(var(--n-height) / 4) 0 calc(var(--n-height) / 3);
 `)]),J("icon, avatar",[J("round",`
 padding: 0 calc(var(--n-height) / 3) 0 calc(var(--n-height) / 2);
 `)]),J("disabled",`
 cursor: not-allowed !important;
 opacity: var(--n-opacity-disabled);
 `),J("checkable",`
 cursor: pointer;
 box-shadow: none;
 color: var(--n-text-color-checkable);
 background-color: var(--n-color-checkable);
 `,[Re("disabled",[ce("&:hover","background-color: var(--n-color-hover-checkable);",[Re("checked","color: var(--n-text-color-hover-checkable);")]),ce("&:active","background-color: var(--n-color-pressed-checkable);",[Re("checked","color: var(--n-text-color-pressed-checkable);")])]),J("checked",`
 color: var(--n-text-color-checked);
 background-color: var(--n-color-checked);
 `,[Re("disabled",[ce("&:hover","background-color: var(--n-color-checked-hover);"),ce("&:active","background-color: var(--n-color-checked-pressed);")])])])]),hn=Object.assign(Object.assign(Object.assign({},Ce.props),dn),{bordered:{type:Boolean,default:void 0},checked:Boolean,checkable:Boolean,strong:Boolean,triggerClickOnClose:Boolean,onClose:[Array,Function],onMouseenter:Function,onMouseleave:Function,"onUpdate:checked":Function,onUpdateChecked:Function,internalCloseFocusable:{type:Boolean,default:!0},internalCloseIsButtonTag:{type:Boolean,default:!0},onCheckedChange:Function}),fn=yt("n-tag"),so=he({name:"Tag",props:hn,slots:Object,setup(e){const t=B(null),{mergedBorderedRef:n,mergedClsPrefixRef:l,inlineThemeDisabled:r,mergedRtlRef:s,mergedComponentPropsRef:a}=De(e),i=I(()=>{var x,T;return e.size||((T=(x=a==null?void 0:a.value)===null||x===void 0?void 0:x.Tag)===null||T===void 0?void 0:T.size)||"medium"}),f=Ce("Tag","-tag",un,cn,e,l);Ye(fn,{roundRef:le(e,"round")});function g(){if(!e.disabled&&e.checkable){const{checked:x,onCheckedChange:T,onUpdateChecked:R,"onUpdate:checked":S}=e;R&&R(!x),S&&S(!x),T&&T(!x)}}function m(x){if(e.triggerClickOnClose||x.stopPropagation(),!e.disabled){const{onClose:T}=e;T&&ge(T,x)}}const b={setTextContent(x){const{value:T}=t;T&&(T.textContent=x)}},P=go("Tag",s,l),k=I(()=>{const{type:x,color:{color:T,textColor:R}={}}=e,S=i.value,{common:{cubicBezierEaseInOut:A},self:{padding:K,closeMargin:V,borderRadius:D,opacityDisabled:oe,textColorCheckable:te,textColorHoverCheckable:ie,textColorPressedCheckable:de,textColorChecked:X,colorCheckable:Q,colorHoverCheckable:h,colorPressedCheckable:w,colorChecked:E,colorCheckedHover:N,colorCheckedPressed:j,closeBorderRadius:G,fontWeightStrong:W,[Z("colorBordered",x)]:U,[Z("closeSize",S)]:q,[Z("closeIconSize",S)]:re,[Z("fontSize",S)]:ae,[Z("height",S)]:c,[Z("color",x)]:p,[Z("textColor",x)]:Y,[Z("border",x)]:ue,[Z("closeIconColor",x)]:xe,[Z("closeIconColorHover",x)]:fe,[Z("closeIconColorPressed",x)]:se,[Z("closeColorHover",x)]:ye,[Z("closeColorPressed",x)]:be}}=f.value,pe=Oe(V);return{"--n-font-weight-strong":W,"--n-avatar-size-override":`calc(${c} - 8px)`,"--n-bezier":A,"--n-border-radius":D,"--n-border":ue,"--n-close-icon-size":re,"--n-close-color-pressed":be,"--n-close-color-hover":ye,"--n-close-border-radius":G,"--n-close-icon-color":xe,"--n-close-icon-color-hover":fe,"--n-close-icon-color-pressed":se,"--n-close-icon-color-disabled":xe,"--n-close-margin-top":pe.top,"--n-close-margin-right":pe.right,"--n-close-margin-bottom":pe.bottom,"--n-close-margin-left":pe.left,"--n-close-size":q,"--n-color":T||(n.value?U:p),"--n-color-checkable":Q,"--n-color-checked":E,"--n-color-checked-hover":N,"--n-color-checked-pressed":j,"--n-color-hover-checkable":h,"--n-color-pressed-checkable":w,"--n-font-size":ae,"--n-height":c,"--n-opacity-disabled":oe,"--n-padding":K,"--n-text-color":R||Y,"--n-text-color-checkable":te,"--n-text-color-checked":X,"--n-text-color-hover-checkable":ie,"--n-text-color-pressed-checkable":de}}),C=r?Ne("tag",I(()=>{let x="";const{type:T,color:{color:R,textColor:S}={}}=e;return x+=T[0],x+=i.value[0],R&&(x+=`a${mo(R)}`),S&&(x+=`b${mo(S)}`),n.value&&(x+="c"),x}),k,e):void 0;return Object.assign(Object.assign({},b),{rtlEnabled:P,mergedClsPrefix:l,contentRef:t,mergedBordered:n,handleClick:g,handleCloseClick:m,cssVars:r?void 0:k,themeClass:C==null?void 0:C.themeClass,onRender:C==null?void 0:C.onRender})},render(){var e,t;const{mergedClsPrefix:n,rtlEnabled:l,closable:r,color:{borderColor:s}={},round:a,onRender:i,$slots:f}=this;i==null||i();const g=Xe(f.avatar,b=>b&&d("div",{class:`${n}-tag__avatar`},b)),m=Xe(f.icon,b=>b&&d("div",{class:`${n}-tag__icon`},b));return d("div",{class:[`${n}-tag`,this.themeClass,{[`${n}-tag--rtl`]:l,[`${n}-tag--strong`]:this.strong,[`${n}-tag--disabled`]:this.disabled,[`${n}-tag--checkable`]:this.checkable,[`${n}-tag--checked`]:this.checkable&&this.checked,[`${n}-tag--round`]:a,[`${n}-tag--avatar`]:g,[`${n}-tag--icon`]:m,[`${n}-tag--closable`]:r}],style:this.cssVars,onClick:this.handleClick,onMouseenter:this.onMouseenter,onMouseleave:this.onMouseleave},m||g,d("span",{class:`${n}-tag__content`,ref:"contentRef"},(t=(e=this.$slots).default)===null||t===void 0?void 0:t.call(e)),!this.checkable&&r?d(xt,{clsPrefix:n,class:`${n}-tag__close`,disabled:this.disabled,onClick:this.handleCloseClick,focusable:this.internalCloseFocusable,round:a,isButtonTag:this.internalCloseIsButtonTag,absolute:!0}):null,!this.checkable&&this.mergedBordered?d("div",{class:`${n}-tag__border`,style:{borderColor:s}}):null)}}),vn={paddingSingle:"0 26px 0 12px",paddingMultiple:"3px 26px 0 12px",clearSize:"16px",arrowSize:"16px"};function gn(e){const{borderRadius:t,textColor2:n,textColorDisabled:l,inputColor:r,inputColorDisabled:s,primaryColor:a,primaryColorHover:i,warningColor:f,warningColorHover:g,errorColor:m,errorColorHover:b,borderColor:P,iconColor:k,iconColorDisabled:C,clearColor:x,clearColorHover:T,clearColorPressed:R,placeholderColor:S,placeholderColorDisabled:A,fontSizeTiny:K,fontSizeSmall:V,fontSizeMedium:D,fontSizeLarge:oe,heightTiny:te,heightSmall:ie,heightMedium:de,heightLarge:X,fontWeight:Q}=e;return Object.assign(Object.assign({},vn),{fontSizeTiny:K,fontSizeSmall:V,fontSizeMedium:D,fontSizeLarge:oe,heightTiny:te,heightSmall:ie,heightMedium:de,heightLarge:X,borderRadius:t,fontWeight:Q,textColor:n,textColorDisabled:l,placeholderColor:S,placeholderColorDisabled:A,color:r,colorDisabled:s,colorActive:r,border:`1px solid ${P}`,borderHover:`1px solid ${i}`,borderActive:`1px solid ${a}`,borderFocus:`1px solid ${i}`,boxShadowHover:"none",boxShadowActive:`0 0 0 2px ${L(a,{alpha:.2})}`,boxShadowFocus:`0 0 0 2px ${L(a,{alpha:.2})}`,caretColor:a,arrowColor:k,arrowColorDisabled:C,loadingColor:a,borderWarning:`1px solid ${f}`,borderHoverWarning:`1px solid ${g}`,borderActiveWarning:`1px solid ${f}`,borderFocusWarning:`1px solid ${g}`,boxShadowHoverWarning:"none",boxShadowActiveWarning:`0 0 0 2px ${L(f,{alpha:.2})}`,boxShadowFocusWarning:`0 0 0 2px ${L(f,{alpha:.2})}`,colorActiveWarning:r,caretColorWarning:f,borderError:`1px solid ${m}`,borderHoverError:`1px solid ${b}`,borderActiveError:`1px solid ${m}`,borderFocusError:`1px solid ${b}`,boxShadowHoverError:"none",boxShadowActiveError:`0 0 0 2px ${L(m,{alpha:.2})}`,boxShadowFocusError:`0 0 0 2px ${L(m,{alpha:.2})}`,colorActiveError:r,caretColorError:m,clearColor:x,clearColorHover:T,clearColorPressed:R})}const Ao=vo({name:"InternalSelection",common:Ae,peers:{Popover:_t},self:gn}),bn=ce([H("base-selection",`
 --n-padding-single: var(--n-padding-single-top) var(--n-padding-single-right) var(--n-padding-single-bottom) var(--n-padding-single-left);
 --n-padding-multiple: var(--n-padding-multiple-top) var(--n-padding-multiple-right) var(--n-padding-multiple-bottom) var(--n-padding-multiple-left);
 position: relative;
 z-index: auto;
 box-shadow: none;
 width: 100%;
 max-width: 100%;
 display: inline-block;
 vertical-align: bottom;
 border-radius: var(--n-border-radius);
 min-height: var(--n-height);
 line-height: 1.5;
 font-size: var(--n-font-size);
 `,[H("base-loading",`
 color: var(--n-loading-color);
 `),H("base-selection-tags","min-height: var(--n-height);"),$("border, state-border",`
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 pointer-events: none;
 border: var(--n-border);
 border-radius: inherit;
 transition:
 box-shadow .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 `),$("state-border",`
 z-index: 1;
 border-color: #0000;
 `),H("base-suffix",`
 cursor: pointer;
 position: absolute;
 top: 50%;
 transform: translateY(-50%);
 right: 10px;
 `,[$("arrow",`
 font-size: var(--n-arrow-size);
 color: var(--n-arrow-color);
 transition: color .3s var(--n-bezier);
 `)]),H("base-selection-overlay",`
 display: flex;
 align-items: center;
 white-space: nowrap;
 pointer-events: none;
 position: absolute;
 top: 0;
 right: 0;
 bottom: 0;
 left: 0;
 padding: var(--n-padding-single);
 transition: color .3s var(--n-bezier);
 `,[$("wrapper",`
 flex-basis: 0;
 flex-grow: 1;
 overflow: hidden;
 text-overflow: ellipsis;
 `)]),H("base-selection-placeholder",`
 color: var(--n-placeholder-color);
 `,[$("inner",`
 max-width: 100%;
 overflow: hidden;
 `)]),H("base-selection-tags",`
 cursor: pointer;
 outline: none;
 box-sizing: border-box;
 position: relative;
 z-index: auto;
 display: flex;
 padding: var(--n-padding-multiple);
 flex-wrap: wrap;
 align-items: center;
 width: 100%;
 vertical-align: bottom;
 background-color: var(--n-color);
 border-radius: inherit;
 transition:
 color .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 `),H("base-selection-label",`
 height: var(--n-height);
 display: inline-flex;
 width: 100%;
 vertical-align: bottom;
 cursor: pointer;
 outline: none;
 z-index: auto;
 box-sizing: border-box;
 position: relative;
 transition:
 color .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 border-radius: inherit;
 background-color: var(--n-color);
 align-items: center;
 `,[H("base-selection-input",`
 font-size: inherit;
 line-height: inherit;
 outline: none;
 cursor: pointer;
 box-sizing: border-box;
 border:none;
 width: 100%;
 padding: var(--n-padding-single);
 background-color: #0000;
 color: var(--n-text-color);
 transition: color .3s var(--n-bezier);
 caret-color: var(--n-caret-color);
 `,[$("content",`
 text-overflow: ellipsis;
 overflow: hidden;
 white-space: nowrap; 
 `)]),$("render-label",`
 color: var(--n-text-color);
 `)]),Re("disabled",[ce("&:hover",[$("state-border",`
 box-shadow: var(--n-box-shadow-hover);
 border: var(--n-border-hover);
 `)]),J("focus",[$("state-border",`
 box-shadow: var(--n-box-shadow-focus);
 border: var(--n-border-focus);
 `)]),J("active",[$("state-border",`
 box-shadow: var(--n-box-shadow-active);
 border: var(--n-border-active);
 `),H("base-selection-label","background-color: var(--n-color-active);"),H("base-selection-tags","background-color: var(--n-color-active);")])]),J("disabled","cursor: not-allowed;",[$("arrow",`
 color: var(--n-arrow-color-disabled);
 `),H("base-selection-label",`
 cursor: not-allowed;
 background-color: var(--n-color-disabled);
 `,[H("base-selection-input",`
 cursor: not-allowed;
 color: var(--n-text-color-disabled);
 `),$("render-label",`
 color: var(--n-text-color-disabled);
 `)]),H("base-selection-tags",`
 cursor: not-allowed;
 background-color: var(--n-color-disabled);
 `),H("base-selection-placeholder",`
 cursor: not-allowed;
 color: var(--n-placeholder-color-disabled);
 `)]),H("base-selection-input-tag",`
 height: calc(var(--n-height) - 6px);
 line-height: calc(var(--n-height) - 6px);
 outline: none;
 display: none;
 position: relative;
 margin-bottom: 3px;
 max-width: 100%;
 vertical-align: bottom;
 `,[$("input",`
 font-size: inherit;
 font-family: inherit;
 min-width: 1px;
 padding: 0;
 background-color: #0000;
 outline: none;
 border: none;
 max-width: 100%;
 overflow: hidden;
 width: 1em;
 line-height: inherit;
 cursor: pointer;
 color: var(--n-text-color);
 caret-color: var(--n-caret-color);
 `),$("mirror",`
 position: absolute;
 left: 0;
 top: 0;
 white-space: pre;
 visibility: hidden;
 user-select: none;
 -webkit-user-select: none;
 opacity: 0;
 `)]),["warning","error"].map(e=>J(`${e}-status`,[$("state-border",`border: var(--n-border-${e});`),Re("disabled",[ce("&:hover",[$("state-border",`
 box-shadow: var(--n-box-shadow-hover-${e});
 border: var(--n-border-hover-${e});
 `)]),J("active",[$("state-border",`
 box-shadow: var(--n-box-shadow-active-${e});
 border: var(--n-border-active-${e});
 `),H("base-selection-label",`background-color: var(--n-color-active-${e});`),H("base-selection-tags",`background-color: var(--n-color-active-${e});`)]),J("focus",[$("state-border",`
 box-shadow: var(--n-box-shadow-focus-${e});
 border: var(--n-border-focus-${e});
 `)])])]))]),H("base-selection-popover",`
 margin-bottom: -3px;
 display: flex;
 flex-wrap: wrap;
 margin-right: -8px;
 `),H("base-selection-tag-wrapper",`
 max-width: 100%;
 display: inline-flex;
 padding: 0 7px 3px 0;
 `,[ce("&:last-child","padding-right: 0;"),H("tag",`
 font-size: 14px;
 max-width: 100%;
 `,[$("content",`
 line-height: 1.25;
 text-overflow: ellipsis;
 overflow: hidden;
 `)])])]),pn=he({name:"InternalSelection",props:Object.assign(Object.assign({},Ce.props),{clsPrefix:{type:String,required:!0},bordered:{type:Boolean,default:void 0},active:Boolean,pattern:{type:String,default:""},placeholder:String,selectedOption:{type:Object,default:null},selectedOptions:{type:Array,default:null},labelField:{type:String,default:"label"},valueField:{type:String,default:"value"},multiple:Boolean,filterable:Boolean,clearable:Boolean,disabled:Boolean,size:{type:String,default:"medium"},loading:Boolean,autofocus:Boolean,showArrow:{type:Boolean,default:!0},inputProps:Object,focused:Boolean,renderTag:Function,onKeydown:Function,onClick:Function,onBlur:Function,onFocus:Function,onDeleteOption:Function,maxTagCount:[String,Number],ellipsisTagPopoverProps:Object,onClear:Function,onPatternInput:Function,onPatternFocus:Function,onPatternBlur:Function,renderLabel:Function,status:String,inlineThemeDisabled:Boolean,ignoreComposition:{type:Boolean,default:!0},onResize:Function}),setup(e){const{mergedClsPrefixRef:t,mergedRtlRef:n}=De(e),l=go("InternalSelection",n,t),r=B(null),s=B(null),a=B(null),i=B(null),f=B(null),g=B(null),m=B(null),b=B(null),P=B(null),k=B(null),C=B(!1),x=B(!1),T=B(!1),R=Ce("InternalSelection","-internal-selection",bn,Ao,e,le(e,"clsPrefix")),S=I(()=>e.clearable&&!e.disabled&&(T.value||e.active)),A=I(()=>e.selectedOption?e.renderTag?e.renderTag({option:e.selectedOption,handleClose:()=>{}}):e.renderLabel?e.renderLabel(e.selectedOption,!0):Ie(e.selectedOption[e.labelField],e.selectedOption,!0):e.placeholder),K=I(()=>{const u=e.selectedOption;if(u)return u[e.labelField]}),V=I(()=>e.multiple?!!(Array.isArray(e.selectedOptions)&&e.selectedOptions.length):e.selectedOption!==null);function D(){var u;const{value:y}=r;if(y){const{value:ee}=s;ee&&(ee.style.width=`${y.offsetWidth}px`,e.maxTagCount!=="responsive"&&((u=P.value)===null||u===void 0||u.sync({showAllItemsBeforeCalculate:!1})))}}function oe(){const{value:u}=k;u&&(u.style.display="none")}function te(){const{value:u}=k;u&&(u.style.display="inline-block")}Te(le(e,"active"),u=>{u||oe()}),Te(le(e,"pattern"),()=>{e.multiple&&Mo(D)});function ie(u){const{onFocus:y}=e;y&&y(u)}function de(u){const{onBlur:y}=e;y&&y(u)}function X(u){const{onDeleteOption:y}=e;y&&y(u)}function Q(u){const{onClear:y}=e;y&&y(u)}function h(u){const{onPatternInput:y}=e;y&&y(u)}function w(u){var y;(!u.relatedTarget||!(!((y=a.value)===null||y===void 0)&&y.contains(u.relatedTarget)))&&ie(u)}function E(u){var y;!((y=a.value)===null||y===void 0)&&y.contains(u.relatedTarget)||de(u)}function N(u){Q(u)}function j(){T.value=!0}function G(){T.value=!1}function W(u){!e.active||!e.filterable||u.target!==s.value&&u.preventDefault()}function U(u){X(u)}const q=B(!1);function re(u){if(u.key==="Backspace"&&!q.value&&!e.pattern.length){const{selectedOptions:y}=e;y!=null&&y.length&&U(y[y.length-1])}}let ae=null;function c(u){const{value:y}=r;if(y){const ee=u.target.value;y.textContent=ee,D()}e.ignoreComposition&&q.value?ae=u:h(u)}function p(){q.value=!0}function Y(){q.value=!1,e.ignoreComposition&&h(ae),ae=null}function ue(u){var y;x.value=!0,(y=e.onPatternFocus)===null||y===void 0||y.call(e,u)}function xe(u){var y;x.value=!1,(y=e.onPatternBlur)===null||y===void 0||y.call(e,u)}function fe(){var u,y;if(e.filterable)x.value=!1,(u=g.value)===null||u===void 0||u.blur(),(y=s.value)===null||y===void 0||y.blur();else if(e.multiple){const{value:ee}=i;ee==null||ee.blur()}else{const{value:ee}=f;ee==null||ee.blur()}}function se(){var u,y,ee;e.filterable?(x.value=!1,(u=g.value)===null||u===void 0||u.focus()):e.multiple?(y=i.value)===null||y===void 0||y.focus():(ee=f.value)===null||ee===void 0||ee.focus()}function ye(){const{value:u}=s;u&&(te(),u.focus())}function be(){const{value:u}=s;u&&u.blur()}function pe(u){const{value:y}=m;y&&y.setTextContent(`+${u}`)}function Me(){const{value:u}=b;return u}function Be(){return s.value}let Se=null;function ze(){Se!==null&&window.clearTimeout(Se)}function $e(){e.active||(ze(),Se=window.setTimeout(()=>{V.value&&(C.value=!0)},100))}function _e(){ze()}function Ee(u){u||(ze(),C.value=!1)}Te(V,u=>{u||(C.value=!1)}),Je(()=>{zt(()=>{const u=g.value;u&&(e.disabled?u.removeAttribute("tabindex"):u.tabIndex=x.value?-1:0)})}),Eo(a,e.onResize);const{inlineThemeDisabled:Pe}=e,Fe=I(()=>{const{size:u}=e,{common:{cubicBezierEaseInOut:y},self:{fontWeight:ee,borderRadius:Qe,color:eo,placeholderColor:oo,textColor:We,paddingSingle:Ve,paddingMultiple:je,caretColor:to,colorDisabled:no,textColorDisabled:Ke,placeholderColorDisabled:we,colorActive:o,boxShadowFocus:v,boxShadowActive:z,boxShadowHover:M,border:F,borderFocus:O,borderHover:_,borderActive:ne,arrowColor:me,arrowColorDisabled:No,loadingColor:Wo,colorActiveWarning:Vo,boxShadowFocusWarning:jo,boxShadowActiveWarning:Ko,boxShadowHoverWarning:Uo,borderWarning:qo,borderFocusWarning:Go,borderHoverWarning:Yo,borderActiveWarning:Xo,colorActiveError:Zo,boxShadowFocusError:Jo,boxShadowActiveError:Qo,boxShadowHoverError:et,borderError:ot,borderFocusError:tt,borderHoverError:nt,borderActiveError:lt,clearColor:rt,clearColorHover:it,clearColorPressed:at,clearSize:st,arrowSize:ct,[Z("height",u)]:dt,[Z("fontSize",u)]:ut}}=R.value,Ue=Oe(Ve),qe=Oe(je);return{"--n-bezier":y,"--n-border":F,"--n-border-active":ne,"--n-border-focus":O,"--n-border-hover":_,"--n-border-radius":Qe,"--n-box-shadow-active":z,"--n-box-shadow-focus":v,"--n-box-shadow-hover":M,"--n-caret-color":to,"--n-color":eo,"--n-color-active":o,"--n-color-disabled":no,"--n-font-size":ut,"--n-height":dt,"--n-padding-single-top":Ue.top,"--n-padding-multiple-top":qe.top,"--n-padding-single-right":Ue.right,"--n-padding-multiple-right":qe.right,"--n-padding-single-left":Ue.left,"--n-padding-multiple-left":qe.left,"--n-padding-single-bottom":Ue.bottom,"--n-padding-multiple-bottom":qe.bottom,"--n-placeholder-color":oo,"--n-placeholder-color-disabled":we,"--n-text-color":We,"--n-text-color-disabled":Ke,"--n-arrow-color":me,"--n-arrow-color-disabled":No,"--n-loading-color":Wo,"--n-color-active-warning":Vo,"--n-box-shadow-focus-warning":jo,"--n-box-shadow-active-warning":Ko,"--n-box-shadow-hover-warning":Uo,"--n-border-warning":qo,"--n-border-focus-warning":Go,"--n-border-hover-warning":Yo,"--n-border-active-warning":Xo,"--n-color-active-error":Zo,"--n-box-shadow-focus-error":Jo,"--n-box-shadow-active-error":Qo,"--n-box-shadow-hover-error":et,"--n-border-error":ot,"--n-border-focus-error":tt,"--n-border-hover-error":nt,"--n-border-active-error":lt,"--n-clear-size":st,"--n-clear-color":rt,"--n-clear-color-hover":it,"--n-clear-color-pressed":at,"--n-arrow-size":ct,"--n-font-weight":ee}}),ve=Pe?Ne("internal-selection",I(()=>e.size[0]),Fe,e):void 0;return{mergedTheme:R,mergedClearable:S,mergedClsPrefix:t,rtlEnabled:l,patternInputFocused:x,filterablePlaceholder:A,label:K,selected:V,showTagsPanel:C,isComposing:q,counterRef:m,counterWrapperRef:b,patternInputMirrorRef:r,patternInputRef:s,selfRef:a,multipleElRef:i,singleElRef:f,patternInputWrapperRef:g,overflowRef:P,inputTagElRef:k,handleMouseDown:W,handleFocusin:w,handleClear:N,handleMouseEnter:j,handleMouseLeave:G,handleDeleteOption:U,handlePatternKeyDown:re,handlePatternInputInput:c,handlePatternInputBlur:xe,handlePatternInputFocus:ue,handleMouseEnterCounter:$e,handleMouseLeaveCounter:_e,handleFocusout:E,handleCompositionEnd:Y,handleCompositionStart:p,onPopoverUpdateShow:Ee,focus:se,focusInput:ye,blur:fe,blurInput:be,updateCounter:pe,getCounter:Me,getTail:Be,renderLabel:e.renderLabel,cssVars:Pe?void 0:Fe,themeClass:ve==null?void 0:ve.themeClass,onRender:ve==null?void 0:ve.onRender}},render(){const{status:e,multiple:t,size:n,disabled:l,filterable:r,maxTagCount:s,bordered:a,clsPrefix:i,ellipsisTagPopoverProps:f,onRender:g,renderTag:m,renderLabel:b}=this;g==null||g();const P=s==="responsive",k=typeof s=="number",C=P||k,x=d(wt,null,{default:()=>d(Wt,{clsPrefix:i,loading:this.loading,showArrow:this.showArrow,showClear:this.mergedClearable&&this.selected,onClear:this.handleClear},{default:()=>{var R,S;return(S=(R=this.$slots).arrow)===null||S===void 0?void 0:S.call(R)}})});let T;if(t){const{labelField:R}=this,S=h=>d("div",{class:`${i}-base-selection-tag-wrapper`,key:h.value},m?m({option:h,handleClose:()=>{this.handleDeleteOption(h)}}):d(so,{size:n,closable:!h.disabled,disabled:l,onClose:()=>{this.handleDeleteOption(h)},internalCloseIsButtonTag:!1,internalCloseFocusable:!1},{default:()=>b?b(h,!0):Ie(h[R],h,!0)})),A=()=>(k?this.selectedOptions.slice(0,s):this.selectedOptions).map(S),K=r?d("div",{class:`${i}-base-selection-input-tag`,ref:"inputTagElRef",key:"__input-tag__"},d("input",Object.assign({},this.inputProps,{ref:"patternInputRef",tabindex:-1,disabled:l,value:this.pattern,autofocus:this.autofocus,class:`${i}-base-selection-input-tag__input`,onBlur:this.handlePatternInputBlur,onFocus:this.handlePatternInputFocus,onKeydown:this.handlePatternKeyDown,onInput:this.handlePatternInputInput,onCompositionstart:this.handleCompositionStart,onCompositionend:this.handleCompositionEnd})),d("span",{ref:"patternInputMirrorRef",class:`${i}-base-selection-input-tag__mirror`},this.pattern)):null,V=P?()=>d("div",{class:`${i}-base-selection-tag-wrapper`,ref:"counterWrapperRef"},d(so,{size:n,ref:"counterRef",onMouseenter:this.handleMouseEnterCounter,onMouseleave:this.handleMouseLeaveCounter,disabled:l})):void 0;let D;if(k){const h=this.selectedOptions.length-s;h>0&&(D=d("div",{class:`${i}-base-selection-tag-wrapper`,key:"__counter__"},d(so,{size:n,ref:"counterRef",onMouseenter:this.handleMouseEnterCounter,disabled:l},{default:()=>`+${h}`})))}const oe=P?r?d(xo,{ref:"overflowRef",updateCounter:this.updateCounter,getCounter:this.getCounter,getTail:this.getTail,style:{width:"100%",display:"flex",overflow:"hidden"}},{default:A,counter:V,tail:()=>K}):d(xo,{ref:"overflowRef",updateCounter:this.updateCounter,getCounter:this.getCounter,style:{width:"100%",display:"flex",overflow:"hidden"}},{default:A,counter:V}):k&&D?A().concat(D):A(),te=C?()=>d("div",{class:`${i}-base-selection-popover`},P?A():this.selectedOptions.map(S)):void 0,ie=C?Object.assign({show:this.showTagsPanel,trigger:"hover",overlap:!0,placement:"top",width:"trigger",onUpdateShow:this.onPopoverUpdateShow,theme:this.mergedTheme.peers.Popover,themeOverrides:this.mergedTheme.peerOverrides.Popover},f):null,X=(this.selected?!1:this.active?!this.pattern&&!this.isComposing:!0)?d("div",{class:`${i}-base-selection-placeholder ${i}-base-selection-overlay`},d("div",{class:`${i}-base-selection-placeholder__inner`},this.placeholder)):null,Q=r?d("div",{ref:"patternInputWrapperRef",class:`${i}-base-selection-tags`},oe,P?null:K,x):d("div",{ref:"multipleElRef",class:`${i}-base-selection-tags`,tabindex:l?void 0:0},oe,x);T=d(St,null,C?d(Et,Object.assign({},ie,{scrollable:!0,style:"max-height: calc(var(--v-target-height) * 6.6);"}),{trigger:()=>Q,default:te}):Q,X)}else if(r){const R=this.pattern||this.isComposing,S=this.active?!R:!this.selected,A=this.active?!1:this.selected;T=d("div",{ref:"patternInputWrapperRef",class:`${i}-base-selection-label`,title:this.patternInputFocused?void 0:Ro(this.label)},d("input",Object.assign({},this.inputProps,{ref:"patternInputRef",class:`${i}-base-selection-input`,value:this.active?this.pattern:"",placeholder:"",readonly:l,disabled:l,tabindex:-1,autofocus:this.autofocus,onFocus:this.handlePatternInputFocus,onBlur:this.handlePatternInputBlur,onInput:this.handlePatternInputInput,onCompositionstart:this.handleCompositionStart,onCompositionend:this.handleCompositionEnd})),A?d("div",{class:`${i}-base-selection-label__render-label ${i}-base-selection-overlay`,key:"input"},d("div",{class:`${i}-base-selection-overlay__wrapper`},m?m({option:this.selectedOption,handleClose:()=>{}}):b?b(this.selectedOption,!0):Ie(this.label,this.selectedOption,!0))):null,S?d("div",{class:`${i}-base-selection-placeholder ${i}-base-selection-overlay`,key:"placeholder"},d("div",{class:`${i}-base-selection-overlay__wrapper`},this.filterablePlaceholder)):null,x)}else T=d("div",{ref:"singleElRef",class:`${i}-base-selection-label`,tabindex:this.disabled?void 0:0},this.label!==void 0?d("div",{class:`${i}-base-selection-input`,title:Ro(this.label),key:"input"},d("div",{class:`${i}-base-selection-input__content`},m?m({option:this.selectedOption,handleClose:()=>{}}):b?b(this.selectedOption,!0):Ie(this.label,this.selectedOption,!0))):d("div",{class:`${i}-base-selection-placeholder ${i}-base-selection-overlay`,key:"placeholder"},d("div",{class:`${i}-base-selection-placeholder__inner`},this.placeholder)),x);return d("div",{ref:"selfRef",class:[`${i}-base-selection`,this.rtlEnabled&&`${i}-base-selection--rtl`,this.themeClass,e&&`${i}-base-selection--${e}-status`,{[`${i}-base-selection--active`]:this.active,[`${i}-base-selection--selected`]:this.selected||this.active&&this.pattern,[`${i}-base-selection--disabled`]:this.disabled,[`${i}-base-selection--multiple`]:this.multiple,[`${i}-base-selection--focus`]:this.focused}],style:this.cssVars,onClick:this.onClick,onMouseenter:this.handleMouseEnter,onMouseleave:this.handleMouseLeave,onKeydown:this.onKeydown,onFocusin:this.handleFocusin,onFocusout:this.handleFocusout,onMousedown:this.handleMouseDown},T,a?d("div",{class:`${i}-base-selection__border`}):null,a?d("div",{class:`${i}-base-selection__state-border`}):null)}});function Ze(e){return e.type==="group"}function Do(e){return e.type==="ignored"}function co(e,t){try{return!!(1+t.toString().toLowerCase().indexOf(e.trim().toLowerCase()))}catch{return!1}}function mn(e,t){return{getIsGroup:Ze,getIgnored:Do,getKey(l){return Ze(l)?l.name||l.key||"key-required":l[e]},getChildren(l){return l[t]}}}function Cn(e,t,n,l){if(!t)return e;function r(s){if(!Array.isArray(s))return[];const a=[];for(const i of s)if(Ze(i)){const f=r(i[l]);f.length&&a.push(Object.assign({},i,{[l]:f}))}else{if(Do(i))continue;t(n,i)&&a.push(i)}return a}return r(e)}function xn(e,t,n){const l=new Map;return e.forEach(r=>{Ze(r)?r[n].forEach(s=>{l.set(s[t],s)}):l.set(r[t],r)}),l}function yn(e){const{boxShadow2:t}=e;return{menuBoxShadow:t}}const wn=vo({name:"Select",common:Ae,peers:{InternalSelection:Ao,InternalSelectMenu:Lo},self:yn}),Sn=ce([H("select",`
 z-index: auto;
 outline: none;
 width: 100%;
 position: relative;
 font-weight: var(--n-font-weight);
 `),H("select-menu",`
 margin: 4px 0;
 box-shadow: var(--n-menu-box-shadow);
 `,[Oo({originalTransition:"background-color .3s var(--n-bezier), box-shadow .3s var(--n-bezier)"})])]),zn=Object.assign(Object.assign({},Ce.props),{to:ho.propTo,bordered:{type:Boolean,default:void 0},clearable:Boolean,clearCreatedOptionsOnClear:{type:Boolean,default:!0},clearFilterAfterSelect:{type:Boolean,default:!0},options:{type:Array,default:()=>[]},defaultValue:{type:[String,Number,Array],default:null},keyboard:{type:Boolean,default:!0},value:[String,Number,Array],placeholder:String,menuProps:Object,multiple:Boolean,size:String,menuSize:{type:String},filterable:Boolean,disabled:{type:Boolean,default:void 0},remote:Boolean,loading:Boolean,filter:Function,placement:{type:String,default:"bottom-start"},widthMode:{type:String,default:"trigger"},tag:Boolean,onCreate:Function,fallbackOption:{type:[Function,Boolean],default:void 0},show:{type:Boolean,default:void 0},showArrow:{type:Boolean,default:!0},maxTagCount:[Number,String],ellipsisTagPopoverProps:Object,consistentMenuWidth:{type:Boolean,default:!0},virtualScroll:{type:Boolean,default:!0},labelField:{type:String,default:"label"},valueField:{type:String,default:"value"},childrenField:{type:String,default:"children"},renderLabel:Function,renderOption:Function,renderTag:Function,"onUpdate:value":[Function,Array],inputProps:Object,nodeProps:Function,ignoreComposition:{type:Boolean,default:!0},showOnFocus:Boolean,onUpdateValue:[Function,Array],onBlur:[Function,Array],onClear:[Function,Array],onFocus:[Function,Array],onScroll:[Function,Array],onSearch:[Function,Array],onUpdateShow:[Function,Array],"onUpdate:show":[Function,Array],displayDirective:{type:String,default:"show"},resetMenuOnOptionsChange:{type:Boolean,default:!0},status:String,showCheckmark:{type:Boolean,default:!0},scrollbarProps:Object,onChange:[Function,Array],items:Array}),Fn=he({name:"Select",props:zn,slots:Object,setup(e){const{mergedClsPrefixRef:t,mergedBorderedRef:n,namespaceRef:l,inlineThemeDisabled:r,mergedComponentPropsRef:s}=De(e),a=Ce("Select","-select",Sn,wn,e,t),i=B(e.defaultValue),f=le(e,"value"),g=yo(f,i),m=B(!1),b=B(""),P=Dt(e,["items","options"]),k=B([]),C=B([]),x=I(()=>C.value.concat(k.value).concat(P.value)),T=I(()=>{const{filter:o}=e;if(o)return o;const{labelField:v,valueField:z}=e;return(M,F)=>{if(!F)return!1;const O=F[v];if(typeof O=="string")return co(M,O);const _=F[z];return typeof _=="string"?co(M,_):typeof _=="number"?co(M,String(_)):!1}}),R=I(()=>{if(e.remote)return P.value;{const{value:o}=x,{value:v}=b;return!v.length||!e.filterable?o:Cn(o,T.value,v,e.childrenField)}}),S=I(()=>{const{valueField:o,childrenField:v}=e,z=mn(o,v);return Nt(R.value,z)}),A=I(()=>xn(x.value,e.valueField,e.childrenField)),K=B(!1),V=yo(le(e,"show"),K),D=B(null),oe=B(null),te=B(null),{localeRef:ie}=Bo("Select"),de=I(()=>{var o;return(o=e.placeholder)!==null&&o!==void 0?o:ie.value.placeholder}),X=[],Q=B(new Map),h=I(()=>{const{fallbackOption:o}=e;if(o===void 0){const{labelField:v,valueField:z}=e;return M=>({[v]:String(M),[z]:M})}return o===!1?!1:v=>Object.assign(o(v),{value:v})});function w(o){const v=e.remote,{value:z}=Q,{value:M}=A,{value:F}=h,O=[];return o.forEach(_=>{if(M.has(_))O.push(M.get(_));else if(v&&z.has(_))O.push(z.get(_));else if(F){const ne=F(_);ne&&O.push(ne)}}),O}const E=I(()=>{if(e.multiple){const{value:o}=g;return Array.isArray(o)?w(o):[]}return null}),N=I(()=>{const{value:o}=g;return!e.multiple&&!Array.isArray(o)?o===null?null:w([o])[0]||null:null}),j=Tt(e,{mergedSize:o=>{var v,z;const{size:M}=e;if(M)return M;const{mergedSize:F}=o||{};if(F!=null&&F.value)return F.value;const O=(z=(v=s==null?void 0:s.value)===null||v===void 0?void 0:v.Select)===null||z===void 0?void 0:z.size;return O||"medium"}}),{mergedSizeRef:G,mergedDisabledRef:W,mergedStatusRef:U}=j;function q(o,v){const{onChange:z,"onUpdate:value":M,onUpdateValue:F}=e,{nTriggerFormChange:O,nTriggerFormInput:_}=j;z&&ge(z,o,v),F&&ge(F,o,v),M&&ge(M,o,v),i.value=o,O(),_()}function re(o){const{onBlur:v}=e,{nTriggerFormBlur:z}=j;v&&ge(v,o),z()}function ae(){const{onClear:o}=e;o&&ge(o)}function c(o){const{onFocus:v,showOnFocus:z}=e,{nTriggerFormFocus:M}=j;v&&ge(v,o),M(),z&&fe()}function p(o){const{onSearch:v}=e;v&&ge(v,o)}function Y(o){const{onScroll:v}=e;v&&ge(v,o)}function ue(){var o;const{remote:v,multiple:z}=e;if(v){const{value:M}=Q;if(z){const{valueField:F}=e;(o=E.value)===null||o===void 0||o.forEach(O=>{M.set(O[F],O)})}else{const F=N.value;F&&M.set(F[e.valueField],F)}}}function xe(o){const{onUpdateShow:v,"onUpdate:show":z}=e;v&&ge(v,o),z&&ge(z,o),K.value=o}function fe(){W.value||(xe(!0),K.value=!0,e.filterable&&je())}function se(){xe(!1)}function ye(){b.value="",C.value=X}const be=B(!1);function pe(){e.filterable&&(be.value=!0)}function Me(){e.filterable&&(be.value=!1,V.value||ye())}function Be(){W.value||(V.value?e.filterable?je():se():fe())}function Se(o){var v,z;!((z=(v=te.value)===null||v===void 0?void 0:v.selfRef)===null||z===void 0)&&z.contains(o.relatedTarget)||(m.value=!1,re(o),se())}function ze(o){c(o),m.value=!0}function $e(){m.value=!0}function _e(o){var v;!((v=D.value)===null||v===void 0)&&v.$el.contains(o.relatedTarget)||(m.value=!1,re(o),se())}function Ee(){var o;(o=D.value)===null||o===void 0||o.focus(),se()}function Pe(o){var v;V.value&&(!((v=D.value)===null||v===void 0)&&v.$el.contains(Ft(o))||se())}function Fe(o){if(!Array.isArray(o))return[];if(h.value)return Array.from(o);{const{remote:v}=e,{value:z}=A;if(v){const{value:M}=Q;return o.filter(F=>z.has(F)||M.has(F))}else return o.filter(M=>z.has(M))}}function ve(o){u(o.rawNode)}function u(o){if(W.value)return;const{tag:v,remote:z,clearFilterAfterSelect:M,valueField:F}=e;if(v&&!z){const{value:O}=C,_=O[0]||null;if(_){const ne=k.value;ne.length?ne.push(_):k.value=[_],C.value=X}}if(z&&Q.value.set(o[F],o),e.multiple){const O=Fe(g.value),_=O.findIndex(ne=>ne===o[F]);if(~_){if(O.splice(_,1),v&&!z){const ne=y(o[F]);~ne&&(k.value.splice(ne,1),M&&(b.value=""))}}else O.push(o[F]),M&&(b.value="");q(O,w(O))}else{if(v&&!z){const O=y(o[F]);~O?k.value=[k.value[O]]:k.value=X}Ve(),se(),q(o[F],o)}}function y(o){return k.value.findIndex(z=>z[e.valueField]===o)}function ee(o){V.value||fe();const{value:v}=o.target;b.value=v;const{tag:z,remote:M}=e;if(p(v),z&&!M){if(!v){C.value=X;return}const{onCreate:F}=e,O=F?F(v):{[e.labelField]:v,[e.valueField]:v},{valueField:_,labelField:ne}=e;P.value.some(me=>me[_]===O[_]||me[ne]===O[ne])||k.value.some(me=>me[_]===O[_]||me[ne]===O[ne])?C.value=X:C.value=[O]}}function Qe(o){o.stopPropagation();const{multiple:v,tag:z,remote:M,clearCreatedOptionsOnClear:F}=e;!v&&e.filterable&&se(),z&&!M&&F&&(k.value=X),ae(),v?q([],[]):q(null,null)}function eo(o){!Le(o,"action")&&!Le(o,"empty")&&!Le(o,"header")&&o.preventDefault()}function oo(o){Y(o)}function We(o){var v,z,M,F,O;if(!e.keyboard){o.preventDefault();return}switch(o.key){case" ":if(e.filterable)break;o.preventDefault();case"Enter":if(!(!((v=D.value)===null||v===void 0)&&v.isComposing)){if(V.value){const _=(z=te.value)===null||z===void 0?void 0:z.getPendingTmNode();_?ve(_):e.filterable||(se(),Ve())}else if(fe(),e.tag&&be.value){const _=C.value[0];if(_){const ne=_[e.valueField],{value:me}=g;e.multiple&&Array.isArray(me)&&me.includes(ne)||u(_)}}}o.preventDefault();break;case"ArrowUp":if(o.preventDefault(),e.loading)return;V.value&&((M=te.value)===null||M===void 0||M.prev());break;case"ArrowDown":if(o.preventDefault(),e.loading)return;V.value?(F=te.value)===null||F===void 0||F.next():fe();break;case"Escape":V.value&&(It(o),se()),(O=D.value)===null||O===void 0||O.focus();break}}function Ve(){var o;(o=D.value)===null||o===void 0||o.focus()}function je(){var o;(o=D.value)===null||o===void 0||o.focusInput()}function to(){var o;V.value&&((o=oe.value)===null||o===void 0||o.syncPosition())}ue(),Te(le(e,"options"),ue);const no={focus:()=>{var o;(o=D.value)===null||o===void 0||o.focus()},focusInput:()=>{var o;(o=D.value)===null||o===void 0||o.focusInput()},blur:()=>{var o;(o=D.value)===null||o===void 0||o.blur()},blurInput:()=>{var o;(o=D.value)===null||o===void 0||o.blurInput()}},Ke=I(()=>{const{self:{menuBoxShadow:o}}=a.value;return{"--n-menu-box-shadow":o}}),we=r?Ne("select",void 0,Ke,e):void 0;return Object.assign(Object.assign({},no),{mergedStatus:U,mergedClsPrefix:t,mergedBordered:n,namespace:l,treeMate:S,isMounted:Pt(),triggerRef:D,menuRef:te,pattern:b,uncontrolledShow:K,mergedShow:V,adjustedTo:ho(e),uncontrolledValue:i,mergedValue:g,followerRef:oe,localizedPlaceholder:de,selectedOption:N,selectedOptions:E,mergedSize:G,mergedDisabled:W,focused:m,activeWithoutMenuOpen:be,inlineThemeDisabled:r,onTriggerInputFocus:pe,onTriggerInputBlur:Me,handleTriggerOrMenuResize:to,handleMenuFocus:$e,handleMenuBlur:_e,handleMenuTabOut:Ee,handleTriggerClick:Be,handleToggle:ve,handleDeleteOption:u,handlePatternInput:ee,handleClear:Qe,handleTriggerBlur:Se,handleTriggerFocus:ze,handleKeydown:We,handleMenuAfterLeave:ye,handleMenuClickOutside:Pe,handleMenuScroll:oo,handleMenuKeydown:We,handleMenuMousedown:eo,mergedTheme:a,cssVars:r?void 0:Ke,themeClass:we==null?void 0:we.themeClass,onRender:we==null?void 0:we.onRender})},render(){return d("div",{class:`${this.mergedClsPrefix}-select`},d(Ht,null,{default:()=>[d(Lt,null,{default:()=>d(pn,{ref:"triggerRef",inlineThemeDisabled:this.inlineThemeDisabled,status:this.mergedStatus,inputProps:this.inputProps,clsPrefix:this.mergedClsPrefix,showArrow:this.showArrow,maxTagCount:this.maxTagCount,ellipsisTagPopoverProps:this.ellipsisTagPopoverProps,bordered:this.mergedBordered,active:this.activeWithoutMenuOpen||this.mergedShow,pattern:this.pattern,placeholder:this.localizedPlaceholder,selectedOption:this.selectedOption,selectedOptions:this.selectedOptions,multiple:this.multiple,renderTag:this.renderTag,renderLabel:this.renderLabel,filterable:this.filterable,clearable:this.clearable,disabled:this.mergedDisabled,size:this.mergedSize,theme:this.mergedTheme.peers.InternalSelection,labelField:this.labelField,valueField:this.valueField,themeOverrides:this.mergedTheme.peerOverrides.InternalSelection,loading:this.loading,focused:this.focused,onClick:this.handleTriggerClick,onDeleteOption:this.handleDeleteOption,onPatternInput:this.handlePatternInput,onClear:this.handleClear,onBlur:this.handleTriggerBlur,onFocus:this.handleTriggerFocus,onKeydown:this.handleKeydown,onPatternBlur:this.onTriggerInputBlur,onPatternFocus:this.onTriggerInputFocus,onResize:this.handleTriggerOrMenuResize,ignoreComposition:this.ignoreComposition},{arrow:()=>{var e,t;return[(t=(e=this.$slots).arrow)===null||t===void 0?void 0:t.call(e)]}})}),d(At,{ref:"followerRef",show:this.mergedShow,to:this.adjustedTo,teleportDisabled:this.adjustedTo===ho.tdkey,containerClass:this.namespace,width:this.consistentMenuWidth?"target":void 0,minWidth:"target",placement:this.placement},{default:()=>d(Io,{name:"fade-in-scale-up-transition",appear:this.isMounted,onAfterLeave:this.handleMenuAfterLeave},{default:()=>{var e,t,n;return this.mergedShow||this.displayDirective==="show"?((e=this.onRender)===null||e===void 0||e.call(this),Rt(d(rn,Object.assign({},this.menuProps,{ref:"menuRef",onResize:this.handleTriggerOrMenuResize,inlineThemeDisabled:this.inlineThemeDisabled,virtualScroll:this.consistentMenuWidth&&this.virtualScroll,class:[`${this.mergedClsPrefix}-select-menu`,this.themeClass,(t=this.menuProps)===null||t===void 0?void 0:t.class],clsPrefix:this.mergedClsPrefix,focusable:!0,labelField:this.labelField,valueField:this.valueField,autoPending:!0,nodeProps:this.nodeProps,theme:this.mergedTheme.peers.InternalSelectMenu,themeOverrides:this.mergedTheme.peerOverrides.InternalSelectMenu,treeMate:this.treeMate,multiple:this.multiple,size:this.menuSize,renderOption:this.renderOption,renderLabel:this.renderLabel,value:this.mergedValue,style:[(n=this.menuProps)===null||n===void 0?void 0:n.style,this.cssVars],onToggle:this.handleToggle,onScroll:this.handleMenuScroll,onFocus:this.handleMenuFocus,onBlur:this.handleMenuBlur,onKeydown:this.handleMenuKeydown,onTabOut:this.handleMenuTabOut,onMousedown:this.handleMenuMousedown,show:this.mergedShow,showCheckmark:this.showCheckmark,resetMenuOnOptionsChange:this.resetMenuOnOptionsChange,scrollbarProps:this.scrollbarProps}),{empty:()=>{var l,r;return[(r=(l=this.$slots).empty)===null||r===void 0?void 0:r.call(l)]},header:()=>{var l,r;return[(r=(l=this.$slots).header)===null||r===void 0?void 0:r.call(l)]},action:()=>{var l,r;return[(r=(l=this.$slots).action)===null||r===void 0?void 0:r.call(l)]}}),this.displayDirective==="show"?[[kt,this.mergedShow],[Co,this.handleMenuClickOutside,void 0,{capture:!0}]]:[[Co,this.handleMenuClickOutside,void 0,{capture:!0}]])):null}})})]}))}});export{Yt as F,so as N,Ut as V,Fn as a,en as b,dn as c,rn as d,mn as e,Ho as f,Lo as i,ao as m,wn as s,cn as t};
