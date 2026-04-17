import{p as ze,C as Ke,B as Oe,a as _e,b as $e,h as ce,r as De,j as Be,k as fe,c as Ae}from"./Space-JgVsnMPf.js";import{br as Te,aO as Fe,a6 as q,a3 as de,bs as He,bt as je,a4 as Me,a7 as V,r as F,c as Le,a as he,e as We,f as ae,d as D,h as s,y as X,q as H,g as k,i as N,o as $,aN as ve,G as le,u as me,j as Y,l as be,m as y,a1 as Ee,A as G,b6 as ye,p as L,F as Ue,bu as qe,b7 as Ve,b5 as Ge,Y as Xe,w as ue,n as _,B as Ye,t as re,v as K,aq as T}from"./index-D6LB0ej7.js";import{f as Je,u as Qe}from"./get-I2R12OG2.js";function Ze(e={},n){const i=Fe({ctrl:!1,command:!1,win:!1,shift:!1,tab:!1}),{keydown:r,keyup:t}=e,o=a=>{switch(a.key){case"Control":i.ctrl=!0;break;case"Meta":i.command=!0,i.win=!0;break;case"Shift":i.shift=!0;break;case"Tab":i.tab=!0;break}r!==void 0&&Object.keys(r).forEach(b=>{if(b!==a.key)return;const v=r[b];if(typeof v=="function")v(a);else{const{stop:g=!1,prevent:x=!1}=v;g&&a.stopPropagation(),x&&a.preventDefault(),v.handler(a)}})},l=a=>{switch(a.key){case"Control":i.ctrl=!1;break;case"Meta":i.command=!1,i.win=!1;break;case"Shift":i.shift=!1;break;case"Tab":i.tab=!1;break}t!==void 0&&Object.keys(t).forEach(b=>{if(b!==a.key)return;const v=t[b];if(typeof v=="function")v(a);else{const{stop:g=!1,prevent:x=!1}=v;g&&a.stopPropagation(),x&&a.preventDefault(),v.handler(a)}})},u=()=>{(n===void 0||n.value)&&(q("keydown",document,o),q("keyup",document,l)),n!==void 0&&de(n,a=>{a?(q("keydown",document,o),q("keyup",document,l)):(V("keydown",document,o),V("keyup",document,l))})};return He()?(je(u),Me(()=>{(n===void 0||n.value)&&(V("keydown",document,o),V("keyup",document,l))})):u(),Te(i)}function eo(e,n,i){const r=F(e.value);let t=null;return de(e,o=>{t!==null&&window.clearTimeout(t),o===!0?i&&!i.value?r.value=!0:t=window.setTimeout(()=>{r.value=!0},n):r.value=!1}),r}function oo(e){return n=>{n?e.value=n.$el:e.value=null}}const no={padding:"4px 0",optionIconSizeSmall:"14px",optionIconSizeMedium:"16px",optionIconSizeLarge:"16px",optionIconSizeHuge:"18px",optionSuffixWidthSmall:"14px",optionSuffixWidthMedium:"14px",optionSuffixWidthLarge:"16px",optionSuffixWidthHuge:"16px",optionIconSuffixWidthSmall:"32px",optionIconSuffixWidthMedium:"32px",optionIconSuffixWidthLarge:"36px",optionIconSuffixWidthHuge:"36px",optionPrefixWidthSmall:"14px",optionPrefixWidthMedium:"14px",optionPrefixWidthLarge:"16px",optionPrefixWidthHuge:"16px",optionIconPrefixWidthSmall:"36px",optionIconPrefixWidthMedium:"36px",optionIconPrefixWidthLarge:"40px",optionIconPrefixWidthHuge:"40px"};function to(e){const{primaryColor:n,textColor2:i,dividerColor:r,hoverColor:t,popoverColor:o,invertedColor:l,borderRadius:u,fontSizeSmall:a,fontSizeMedium:b,fontSizeLarge:v,fontSizeHuge:g,heightSmall:x,heightMedium:P,heightLarge:C,heightHuge:I,textColor3:S,opacityDisabled:R}=e;return Object.assign(Object.assign({},no),{optionHeightSmall:x,optionHeightMedium:P,optionHeightLarge:C,optionHeightHuge:I,borderRadius:u,fontSizeSmall:a,fontSizeMedium:b,fontSizeLarge:v,fontSizeHuge:g,optionTextColor:i,optionTextColorHover:i,optionTextColorActive:n,optionTextColorChildActive:n,color:o,dividerColor:r,suffixColor:i,prefixColor:i,optionColorHover:t,optionColorActive:We(n,{alpha:.1}),groupHeaderTextColor:S,optionTextColorInverted:"#BBB",optionTextColorHoverInverted:"#FFF",optionTextColorActiveInverted:"#FFF",optionTextColorChildActiveInverted:"#FFF",colorInverted:l,dividerColorInverted:"#BBB",suffixColorInverted:"#BBB",prefixColorInverted:"#BBB",optionColorHoverInverted:n,optionColorActiveInverted:n,groupHeaderTextColorInverted:"#AAA",optionOpacityDisabled:R})}const ro=Le({name:"Dropdown",common:he,peers:{Popover:ze},self:to}),se=ae("n-dropdown-menu"),J=ae("n-dropdown"),pe=ae("n-dropdown-option"),we=D({name:"DropdownDivider",props:{clsPrefix:{type:String,required:!0}},render(){return s("div",{class:`${this.clsPrefix}-dropdown-divider`})}}),io=D({name:"DropdownGroupHeader",props:{clsPrefix:{type:String,required:!0},tmNode:{type:Object,required:!0}},setup(){const{showIconRef:e,hasSubmenuRef:n}=H(se),{renderLabelRef:i,labelFieldRef:r,nodePropsRef:t,renderOptionRef:o}=H(J);return{labelField:r,showIcon:e,hasSubmenu:n,renderLabel:i,nodeProps:t,renderOption:o}},render(){var e;const{clsPrefix:n,hasSubmenu:i,showIcon:r,nodeProps:t,renderLabel:o,renderOption:l}=this,{rawNode:u}=this.tmNode,a=s("div",Object.assign({class:`${n}-dropdown-option`},t==null?void 0:t(u)),s("div",{class:`${n}-dropdown-option-body ${n}-dropdown-option-body--group`},s("div",{"data-dropdown-option":!0,class:[`${n}-dropdown-option-body__prefix`,r&&`${n}-dropdown-option-body__prefix--show-icon`]},X(u.icon)),s("div",{class:`${n}-dropdown-option-body__label`,"data-dropdown-option":!0},o?o(u):X((e=u.title)!==null&&e!==void 0?e:u[this.labelField])),s("div",{class:[`${n}-dropdown-option-body__suffix`,i&&`${n}-dropdown-option-body__suffix--has-submenu`],"data-dropdown-option":!0})));return l?l({node:a,option:u}):a}});function ao(e){const{textColorBase:n,opacity1:i,opacity2:r,opacity3:t,opacity4:o,opacity5:l}=e;return{color:n,opacity1Depth:i,opacity2Depth:r,opacity3Depth:t,opacity4Depth:o,opacity5Depth:l}}const lo={common:he,self:ao},so=k("icon",`
 height: 1em;
 width: 1em;
 line-height: 1em;
 text-align: center;
 display: inline-block;
 position: relative;
 fill: currentColor;
`,[N("color-transition",{transition:"color .3s var(--n-bezier)"}),N("depth",{color:"var(--n-color)"},[$("svg",{opacity:"var(--n-opacity)",transition:"opacity .3s var(--n-bezier)"})]),$("svg",{height:"1em",width:"1em"})]),co=Object.assign(Object.assign({},Y.props),{depth:[String,Number],size:[Number,String],color:String,component:[Object,Function]}),uo=D({_n_icon__:!0,name:"Icon",inheritAttrs:!1,props:co,setup(e){const{mergedClsPrefixRef:n,inlineThemeDisabled:i}=me(e),r=Y("Icon","-icon",so,lo,e,n),t=y(()=>{const{depth:l}=e,{common:{cubicBezierEaseInOut:u},self:a}=r.value;if(l!==void 0){const{color:b,[`opacity${l}Depth`]:v}=a;return{"--n-bezier":u,"--n-color":b,"--n-opacity":v}}return{"--n-bezier":u,"--n-color":"","--n-opacity":""}}),o=i?be("icon",y(()=>`${e.depth||"d"}`),t,e):void 0;return{mergedClsPrefix:n,mergedStyle:y(()=>{const{size:l,color:u}=e;return{fontSize:Je(l),color:u}}),cssVars:i?void 0:t,themeClass:o==null?void 0:o.themeClass,onRender:o==null?void 0:o.onRender}},render(){var e;const{$parent:n,depth:i,mergedClsPrefix:r,component:t,onRender:o,themeClass:l}=this;return!((e=n==null?void 0:n.$options)===null||e===void 0)&&e._n_icon__&&ve("icon","don't wrap `n-icon` inside `n-icon`"),o==null||o(),s("i",le(this.$attrs,{role:"img",class:[`${r}-icon`,l,{[`${r}-icon--depth`]:i,[`${r}-icon--color-transition`]:i!==void 0}],style:[this.cssVars,this.mergedStyle]}),t?s(t):this.$slots)}});function ie(e,n){return e.type==="submenu"||e.type===void 0&&e[n]!==void 0}function po(e){return e.type==="group"}function ge(e){return e.type==="divider"}function fo(e){return e.type==="render"}const xe=D({name:"DropdownOption",props:{clsPrefix:{type:String,required:!0},tmNode:{type:Object,required:!0},parentKey:{type:[String,Number],default:null},placement:{type:String,default:"right-start"},props:Object,scrollable:Boolean},setup(e){const n=H(J),{hoverKeyRef:i,keyboardKeyRef:r,lastToggledSubmenuKeyRef:t,pendingKeyPathRef:o,activeKeyPathRef:l,animatedRef:u,mergedShowRef:a,renderLabelRef:b,renderIconRef:v,labelFieldRef:g,childrenFieldRef:x,renderOptionRef:P,nodePropsRef:C,menuPropsRef:I}=n,S=H(pe,null),R=H(se),O=H(ye),E=y(()=>e.tmNode.rawNode),W=y(()=>{const{value:d}=x;return ie(e.tmNode.rawNode,d)}),Q=y(()=>{const{disabled:d}=e.tmNode;return d}),Z=y(()=>{if(!W.value)return!1;const{key:d,disabled:f}=e.tmNode;if(f)return!1;const{value:w}=i,{value:B}=r,{value:te}=t,{value:A}=o;return w!==null?A.includes(d):B!==null?A.includes(d)&&A[A.length-1]!==d:te!==null?A.includes(d):!1}),ee=y(()=>r.value===null&&!u.value),oe=eo(Z,300,ee),ne=y(()=>!!(S!=null&&S.enteringSubmenuRef.value)),j=F(!1);L(pe,{enteringSubmenuRef:j});function M(){j.value=!0}function U(){j.value=!1}function z(){const{parentKey:d,tmNode:f}=e;f.disabled||a.value&&(t.value=d,r.value=null,i.value=f.key)}function c(){const{tmNode:d}=e;d.disabled||a.value&&i.value!==d.key&&z()}function p(d){if(e.tmNode.disabled||!a.value)return;const{relatedTarget:f}=d;f&&!ce({target:f},"dropdownOption")&&!ce({target:f},"scrollbarRail")&&(i.value=null)}function h(){const{value:d}=W,{tmNode:f}=e;a.value&&!d&&!f.disabled&&(n.doSelect(f.key,f.rawNode),n.doUpdateShow(!1))}return{labelField:g,renderLabel:b,renderIcon:v,siblingHasIcon:R.showIconRef,siblingHasSubmenu:R.hasSubmenuRef,menuProps:I,popoverBody:O,animated:u,mergedShowSubmenu:y(()=>oe.value&&!ne.value),rawNode:E,hasSubmenu:W,pending:G(()=>{const{value:d}=o,{key:f}=e.tmNode;return d.includes(f)}),childActive:G(()=>{const{value:d}=l,{key:f}=e.tmNode,w=d.findIndex(B=>f===B);return w===-1?!1:w<d.length-1}),active:G(()=>{const{value:d}=l,{key:f}=e.tmNode,w=d.findIndex(B=>f===B);return w===-1?!1:w===d.length-1}),mergedDisabled:Q,renderOption:P,nodeProps:C,handleClick:h,handleMouseMove:c,handleMouseEnter:z,handleMouseLeave:p,handleSubmenuBeforeEnter:M,handleSubmenuAfterEnter:U}},render(){var e,n;const{animated:i,rawNode:r,mergedShowSubmenu:t,clsPrefix:o,siblingHasIcon:l,siblingHasSubmenu:u,renderLabel:a,renderIcon:b,renderOption:v,nodeProps:g,props:x,scrollable:P}=this;let C=null;if(t){const O=(e=this.menuProps)===null||e===void 0?void 0:e.call(this,r,r.children);C=s(Se,Object.assign({},O,{clsPrefix:o,scrollable:this.scrollable,tmNodes:this.tmNode.children,parentKey:this.tmNode.key}))}const I={class:[`${o}-dropdown-option-body`,this.pending&&`${o}-dropdown-option-body--pending`,this.active&&`${o}-dropdown-option-body--active`,this.childActive&&`${o}-dropdown-option-body--child-active`,this.mergedDisabled&&`${o}-dropdown-option-body--disabled`],onMousemove:this.handleMouseMove,onMouseenter:this.handleMouseEnter,onMouseleave:this.handleMouseLeave,onClick:this.handleClick},S=g==null?void 0:g(r),R=s("div",Object.assign({class:[`${o}-dropdown-option`,S==null?void 0:S.class],"data-dropdown-option":!0},S),s("div",le(I,x),[s("div",{class:[`${o}-dropdown-option-body__prefix`,l&&`${o}-dropdown-option-body__prefix--show-icon`]},[b?b(r):X(r.icon)]),s("div",{"data-dropdown-option":!0,class:`${o}-dropdown-option-body__label`},a?a(r):X((n=r[this.labelField])!==null&&n!==void 0?n:r.title)),s("div",{"data-dropdown-option":!0,class:[`${o}-dropdown-option-body__suffix`,u&&`${o}-dropdown-option-body__suffix--has-submenu`]},this.hasSubmenu?s(uo,null,{default:()=>s(Ke,null)}):null)]),this.hasSubmenu?s(Oe,null,{default:()=>[s(_e,null,{default:()=>s("div",{class:`${o}-dropdown-offset-container`},s($e,{show:this.mergedShowSubmenu,placement:this.placement,to:P&&this.popoverBody||void 0,teleportDisabled:!P},{default:()=>s("div",{class:`${o}-dropdown-menu-wrapper`},i?s(Ee,{onBeforeEnter:this.handleSubmenuBeforeEnter,onAfterEnter:this.handleSubmenuAfterEnter,name:"fade-in-scale-up-transition",appear:!0},{default:()=>C}):C)}))})]}):null);return v?v({node:R,option:r}):R}}),ho=D({name:"NDropdownGroup",props:{clsPrefix:{type:String,required:!0},tmNode:{type:Object,required:!0},parentKey:{type:[String,Number],default:null}},render(){const{tmNode:e,parentKey:n,clsPrefix:i}=this,{children:r}=e;return s(Ue,null,s(io,{clsPrefix:i,tmNode:e,key:e.key}),r==null?void 0:r.map(t=>{const{rawNode:o}=t;return o.show===!1?null:ge(o)?s(we,{clsPrefix:i,key:t.key}):t.isGroup?(ve("dropdown","`group` node is not allowed to be put in `group` node."),null):s(xe,{clsPrefix:i,tmNode:t,parentKey:n,key:t.key})}))}}),vo=D({name:"DropdownRenderOption",props:{tmNode:{type:Object,required:!0}},render(){const{rawNode:{render:e,props:n}}=this.tmNode;return s("div",n,[e==null?void 0:e()])}}),Se=D({name:"DropdownMenu",props:{scrollable:Boolean,showArrow:Boolean,arrowStyle:[String,Object],clsPrefix:{type:String,required:!0},tmNodes:{type:Array,default:()=>[]},parentKey:{type:[String,Number],default:null}},setup(e){const{renderIconRef:n,childrenFieldRef:i}=H(J);L(se,{showIconRef:y(()=>{const t=n.value;return e.tmNodes.some(o=>{var l;if(o.isGroup)return(l=o.children)===null||l===void 0?void 0:l.some(({rawNode:a})=>t?t(a):a.icon);const{rawNode:u}=o;return t?t(u):u.icon})}),hasSubmenuRef:y(()=>{const{value:t}=i;return e.tmNodes.some(o=>{var l;if(o.isGroup)return(l=o.children)===null||l===void 0?void 0:l.some(({rawNode:a})=>ie(a,t));const{rawNode:u}=o;return ie(u,t)})})});const r=F(null);return L(Ve,null),L(Ge,null),L(ye,r),{bodyRef:r}},render(){const{parentKey:e,clsPrefix:n,scrollable:i}=this,r=this.tmNodes.map(t=>{const{rawNode:o}=t;return o.show===!1?null:fo(o)?s(vo,{tmNode:t,key:t.key}):ge(o)?s(we,{clsPrefix:n,key:t.key}):po(o)?s(ho,{clsPrefix:n,tmNode:t,parentKey:e,key:t.key}):s(xe,{clsPrefix:n,tmNode:t,parentKey:e,key:t.key,props:o.props,scrollable:i})});return s("div",{class:[`${n}-dropdown-menu`,i&&`${n}-dropdown-menu--scrollable`],ref:"bodyRef"},i?s(qe,{contentClass:`${n}-dropdown-menu__content`},{default:()=>r}):r,this.showArrow?De({clsPrefix:n,arrowStyle:this.arrowStyle,arrowClass:void 0,arrowWrapperClass:void 0,arrowWrapperStyle:void 0}):null)}}),mo=k("dropdown-menu",`
 transform-origin: var(--v-transform-origin);
 background-color: var(--n-color);
 border-radius: var(--n-border-radius);
 box-shadow: var(--n-box-shadow);
 position: relative;
 transition:
 background-color .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier);
`,[Xe(),k("dropdown-option",`
 position: relative;
 `,[$("a",`
 text-decoration: none;
 color: inherit;
 outline: none;
 `,[$("&::before",`
 content: "";
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 `)]),k("dropdown-option-body",`
 display: flex;
 cursor: pointer;
 position: relative;
 height: var(--n-option-height);
 line-height: var(--n-option-height);
 font-size: var(--n-font-size);
 color: var(--n-option-text-color);
 transition: color .3s var(--n-bezier);
 `,[$("&::before",`
 content: "";
 position: absolute;
 top: 0;
 bottom: 0;
 left: 4px;
 right: 4px;
 transition: background-color .3s var(--n-bezier);
 border-radius: var(--n-border-radius);
 `),ue("disabled",[N("pending",`
 color: var(--n-option-text-color-hover);
 `,[_("prefix, suffix",`
 color: var(--n-option-text-color-hover);
 `),$("&::before","background-color: var(--n-option-color-hover);")]),N("active",`
 color: var(--n-option-text-color-active);
 `,[_("prefix, suffix",`
 color: var(--n-option-text-color-active);
 `),$("&::before","background-color: var(--n-option-color-active);")]),N("child-active",`
 color: var(--n-option-text-color-child-active);
 `,[_("prefix, suffix",`
 color: var(--n-option-text-color-child-active);
 `)])]),N("disabled",`
 cursor: not-allowed;
 opacity: var(--n-option-opacity-disabled);
 `),N("group",`
 font-size: calc(var(--n-font-size) - 1px);
 color: var(--n-group-header-text-color);
 `,[_("prefix",`
 width: calc(var(--n-option-prefix-width) / 2);
 `,[N("show-icon",`
 width: calc(var(--n-option-icon-prefix-width) / 2);
 `)])]),_("prefix",`
 width: var(--n-option-prefix-width);
 display: flex;
 justify-content: center;
 align-items: center;
 color: var(--n-prefix-color);
 transition: color .3s var(--n-bezier);
 z-index: 1;
 `,[N("show-icon",`
 width: var(--n-option-icon-prefix-width);
 `),k("icon",`
 font-size: var(--n-option-icon-size);
 `)]),_("label",`
 white-space: nowrap;
 flex: 1;
 z-index: 1;
 `),_("suffix",`
 box-sizing: border-box;
 flex-grow: 0;
 flex-shrink: 0;
 display: flex;
 justify-content: flex-end;
 align-items: center;
 min-width: var(--n-option-suffix-width);
 padding: 0 8px;
 transition: color .3s var(--n-bezier);
 color: var(--n-suffix-color);
 z-index: 1;
 `,[N("has-submenu",`
 width: var(--n-option-icon-suffix-width);
 `),k("icon",`
 font-size: var(--n-option-icon-size);
 `)]),k("dropdown-menu","pointer-events: all;")]),k("dropdown-offset-container",`
 pointer-events: none;
 position: absolute;
 left: 0;
 right: 0;
 top: -4px;
 bottom: -4px;
 `)]),k("dropdown-divider",`
 transition: background-color .3s var(--n-bezier);
 background-color: var(--n-divider-color);
 height: 1px;
 margin: 4px 0;
 `),k("dropdown-menu-wrapper",`
 transform-origin: var(--v-transform-origin);
 width: fit-content;
 `),$(">",[k("scrollbar",`
 height: inherit;
 max-height: inherit;
 `)]),ue("scrollable",`
 padding: var(--n-padding);
 `),N("scrollable",[_("content",`
 padding: var(--n-padding);
 `)])]),bo={animated:{type:Boolean,default:!0},keyboard:{type:Boolean,default:!0},size:String,inverted:Boolean,placement:{type:String,default:"bottom"},onSelect:[Function,Array],options:{type:Array,default:()=>[]},menuProps:Function,showArrow:Boolean,renderLabel:Function,renderIcon:Function,renderOption:Function,nodeProps:Function,labelField:{type:String,default:"label"},keyField:{type:String,default:"key"},childrenField:{type:String,default:"children"},value:[String,Number]},yo=Object.keys(fe),wo=Object.assign(Object.assign(Object.assign({},fe),bo),Y.props),Po=D({name:"Dropdown",inheritAttrs:!1,props:wo,setup(e){const n=F(!1),i=Qe(K(e,"show"),n),r=y(()=>{const{keyField:c,childrenField:p}=e;return Ae(e.options,{getKey(h){return h[c]},getDisabled(h){return h.disabled===!0},getIgnored(h){return h.type==="divider"||h.type==="render"},getChildren(h){return h[p]}})}),t=y(()=>r.value.treeNodes),o=F(null),l=F(null),u=F(null),a=y(()=>{var c,p,h;return(h=(p=(c=o.value)!==null&&c!==void 0?c:l.value)!==null&&p!==void 0?p:u.value)!==null&&h!==void 0?h:null}),b=y(()=>r.value.getPath(a.value).keyPath),v=y(()=>r.value.getPath(e.value).keyPath),g=G(()=>e.keyboard&&i.value);Ze({keydown:{ArrowUp:{prevent:!0,handler:ee},ArrowRight:{prevent:!0,handler:Z},ArrowDown:{prevent:!0,handler:oe},ArrowLeft:{prevent:!0,handler:Q},Enter:{prevent:!0,handler:ne},Escape:W}},g);const{mergedClsPrefixRef:x,inlineThemeDisabled:P,mergedComponentPropsRef:C}=me(e),I=y(()=>{var c,p;return e.size||((p=(c=C==null?void 0:C.value)===null||c===void 0?void 0:c.Dropdown)===null||p===void 0?void 0:p.size)||"medium"}),S=Y("Dropdown","-dropdown",mo,ro,e,x);L(J,{labelFieldRef:K(e,"labelField"),childrenFieldRef:K(e,"childrenField"),renderLabelRef:K(e,"renderLabel"),renderIconRef:K(e,"renderIcon"),hoverKeyRef:o,keyboardKeyRef:l,lastToggledSubmenuKeyRef:u,pendingKeyPathRef:b,activeKeyPathRef:v,animatedRef:K(e,"animated"),mergedShowRef:i,nodePropsRef:K(e,"nodeProps"),renderOptionRef:K(e,"renderOption"),menuPropsRef:K(e,"menuProps"),doSelect:R,doUpdateShow:O}),de(i,c=>{!e.animated&&!c&&E()});function R(c,p){const{onSelect:h}=e;h&&re(h,c,p)}function O(c){const{"onUpdate:show":p,onUpdateShow:h}=e;p&&re(p,c),h&&re(h,c),n.value=c}function E(){o.value=null,l.value=null,u.value=null}function W(){O(!1)}function Q(){M("left")}function Z(){M("right")}function ee(){M("up")}function oe(){M("down")}function ne(){const c=j();c!=null&&c.isLeaf&&i.value&&(R(c.key,c.rawNode),O(!1))}function j(){var c;const{value:p}=r,{value:h}=a;return!p||h===null?null:(c=p.getNode(h))!==null&&c!==void 0?c:null}function M(c){const{value:p}=a,{value:{getFirstAvailableNode:h}}=r;let d=null;if(p===null){const f=h();f!==null&&(d=f.key)}else{const f=j();if(f){let w;switch(c){case"down":w=f.getNext();break;case"up":w=f.getPrev();break;case"right":w=f.getChild();break;case"left":w=f.getParent();break}w&&(d=w.key)}}d!==null&&(o.value=null,l.value=d)}const U=y(()=>{const{inverted:c}=e,p=I.value,{common:{cubicBezierEaseInOut:h},self:d}=S.value,{padding:f,dividerColor:w,borderRadius:B,optionOpacityDisabled:te,[T("optionIconSuffixWidth",p)]:A,[T("optionSuffixWidth",p)]:Pe,[T("optionIconPrefixWidth",p)]:Ce,[T("optionPrefixWidth",p)]:ke,[T("fontSize",p)]:Ne,[T("optionHeight",p)]:Re,[T("optionIconSize",p)]:Ie}=d,m={"--n-bezier":h,"--n-font-size":Ne,"--n-padding":f,"--n-border-radius":B,"--n-option-height":Re,"--n-option-prefix-width":ke,"--n-option-icon-prefix-width":Ce,"--n-option-suffix-width":Pe,"--n-option-icon-suffix-width":A,"--n-option-icon-size":Ie,"--n-divider-color":w,"--n-option-opacity-disabled":te};return c?(m["--n-color"]=d.colorInverted,m["--n-option-color-hover"]=d.optionColorHoverInverted,m["--n-option-color-active"]=d.optionColorActiveInverted,m["--n-option-text-color"]=d.optionTextColorInverted,m["--n-option-text-color-hover"]=d.optionTextColorHoverInverted,m["--n-option-text-color-active"]=d.optionTextColorActiveInverted,m["--n-option-text-color-child-active"]=d.optionTextColorChildActiveInverted,m["--n-prefix-color"]=d.prefixColorInverted,m["--n-suffix-color"]=d.suffixColorInverted,m["--n-group-header-text-color"]=d.groupHeaderTextColorInverted):(m["--n-color"]=d.color,m["--n-option-color-hover"]=d.optionColorHover,m["--n-option-color-active"]=d.optionColorActive,m["--n-option-text-color"]=d.optionTextColor,m["--n-option-text-color-hover"]=d.optionTextColorHover,m["--n-option-text-color-active"]=d.optionTextColorActive,m["--n-option-text-color-child-active"]=d.optionTextColorChildActive,m["--n-prefix-color"]=d.prefixColor,m["--n-suffix-color"]=d.suffixColor,m["--n-group-header-text-color"]=d.groupHeaderTextColor),m}),z=P?be("dropdown",y(()=>`${I.value[0]}${e.inverted?"i":""}`),U,e):void 0;return{mergedClsPrefix:x,mergedTheme:S,mergedSize:I,tmNodes:t,mergedShow:i,handleAfterLeave:()=>{e.animated&&E()},doUpdateShow:O,cssVars:P?void 0:U,themeClass:z==null?void 0:z.themeClass,onRender:z==null?void 0:z.onRender}},render(){const e=(r,t,o,l,u)=>{var a;const{mergedClsPrefix:b,menuProps:v}=this;(a=this.onRender)===null||a===void 0||a.call(this);const g=(v==null?void 0:v(void 0,this.tmNodes.map(P=>P.rawNode)))||{},x={ref:oo(t),class:[r,`${b}-dropdown`,`${b}-dropdown--${this.mergedSize}-size`,this.themeClass],clsPrefix:b,tmNodes:this.tmNodes,style:[...o,this.cssVars],showArrow:this.showArrow,arrowStyle:this.arrowStyle,scrollable:this.scrollable,onMouseenter:l,onMouseleave:u};return s(Se,le(this.$attrs,x,g))},{mergedTheme:n}=this,i={show:this.mergedShow,theme:n.peers.Popover,themeOverrides:n.peerOverrides.Popover,internalOnAfterLeave:this.handleAfterLeave,internalRenderBody:e,onUpdateShow:this.doUpdateShow,"onUpdate:show":void 0};return s(Be,Object.assign({},Ye(this.$props,yo),i),{trigger:()=>{var r,t;return(t=(r=this.$slots).default)===null||t===void 0?void 0:t.call(r)}})}});export{Po as N,oo as c,ro as d,Ze as u};
