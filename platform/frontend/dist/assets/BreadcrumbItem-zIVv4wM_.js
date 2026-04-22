import{a as T,g as d,o as s,i as L,n as u,d as g,h as v,u as y,j as C,l as j,m as p,f as H,p as S,v as w,r as E,H as I,ae as O,be as _,a2 as $,q as A}from"./index-DKfkuiLi.js";const N={fontWeightActive:"400"};function V(e){const{fontSize:o,textColor3:a,textColor2:r,borderRadius:n,buttonColor2Hover:t,buttonColor2Pressed:l}=e;return Object.assign(Object.assign({},N),{fontSize:o,itemLineHeight:"1.25",itemTextColor:a,itemTextColorHover:r,itemTextColorPressed:r,itemTextColorActive:r,itemBorderRadius:n,itemColorHover:t,itemColorPressed:l,separatorColor:a})}const K={common:T,self:V},M=d("breadcrumb",`
 white-space: nowrap;
 cursor: default;
 line-height: var(--n-item-line-height);
`,[s("ul",`
 list-style: none;
 padding: 0;
 margin: 0;
 `),s("a",`
 color: inherit;
 text-decoration: inherit;
 `),d("breadcrumb-item",`
 font-size: var(--n-font-size);
 transition: color .3s var(--n-bezier);
 display: inline-flex;
 align-items: center;
 `,[d("icon",`
 font-size: 18px;
 vertical-align: -.2em;
 transition: color .3s var(--n-bezier);
 color: var(--n-item-text-color);
 `),s("&:not(:last-child)",[L("clickable",[u("link",`
 cursor: pointer;
 `,[s("&:hover",`
 background-color: var(--n-item-color-hover);
 `),s("&:active",`
 background-color: var(--n-item-color-pressed); 
 `)])])]),u("link",`
 padding: 4px;
 border-radius: var(--n-item-border-radius);
 transition:
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
 color: var(--n-item-text-color);
 position: relative;
 `,[s("&:hover",`
 color: var(--n-item-text-color-hover);
 `,[d("icon",`
 color: var(--n-item-text-color-hover);
 `)]),s("&:active",`
 color: var(--n-item-text-color-pressed);
 `,[d("icon",`
 color: var(--n-item-text-color-pressed);
 `)])]),u("separator",`
 margin: 0 8px;
 color: var(--n-separator-color);
 transition: color .3s var(--n-bezier);
 user-select: none;
 -webkit-user-select: none;
 `),s("&:last-child",[u("link",`
 font-weight: var(--n-font-weight-active);
 cursor: unset;
 color: var(--n-item-text-color-active);
 `,[d("icon",`
 color: var(--n-item-text-color-active);
 `)]),u("separator",`
 display: none;
 `)])])]),x=H("n-breadcrumb"),q=Object.assign(Object.assign({},C.props),{separator:{type:String,default:"/"}}),G=g({name:"Breadcrumb",props:q,setup(e){const{mergedClsPrefixRef:o,inlineThemeDisabled:a}=y(e),r=C("Breadcrumb","-breadcrumb",M,K,e,o);S(x,{separatorRef:w(e,"separator"),mergedClsPrefixRef:o});const n=p(()=>{const{common:{cubicBezierEaseInOut:l},self:{separatorColor:m,itemTextColor:i,itemTextColorHover:c,itemTextColorPressed:b,itemTextColorActive:h,fontSize:f,fontWeightActive:R,itemBorderRadius:k,itemColorHover:B,itemColorPressed:z,itemLineHeight:P}}=r.value;return{"--n-font-size":f,"--n-bezier":l,"--n-item-text-color":i,"--n-item-text-color-hover":c,"--n-item-text-color-pressed":b,"--n-item-text-color-active":h,"--n-separator-color":m,"--n-item-color-hover":B,"--n-item-color-pressed":z,"--n-item-border-radius":k,"--n-font-weight-active":R,"--n-item-line-height":P}}),t=a?j("breadcrumb",void 0,n,e):void 0;return{mergedClsPrefix:o,cssVars:a?void 0:n,themeClass:t==null?void 0:t.themeClass,onRender:t==null?void 0:t.onRender}},render(){var e;return(e=this.onRender)===null||e===void 0||e.call(this),v("nav",{class:[`${this.mergedClsPrefix}-breadcrumb`,this.themeClass],style:this.cssVars,"aria-label":"Breadcrumb"},v("ul",null,this.$slots))}});function D(e=_?window:null){const o=()=>{const{hash:n,host:t,hostname:l,href:m,origin:i,pathname:c,port:b,protocol:h,search:f}=(e==null?void 0:e.location)||{};return{hash:n,host:t,hostname:l,href:m,origin:i,pathname:c,port:b,protocol:h,search:f}},a=E(o()),r=()=>{a.value=o()};return I(()=>{e&&(e.addEventListener("popstate",r),e.addEventListener("hashchange",r))}),O(()=>{e&&(e.removeEventListener("popstate",r),e.removeEventListener("hashchange",r))}),a}const F={separator:String,href:String,clickable:{type:Boolean,default:!0},showSeparator:{type:Boolean,default:!0},onClick:Function},J=g({name:"BreadcrumbItem",props:F,slots:Object,setup(e,{slots:o}){const a=A(x,null);if(!a)return()=>null;const{separatorRef:r,mergedClsPrefixRef:n}=a,t=D(),l=p(()=>e.href?"a":"span"),m=p(()=>t.value.href===e.href?"location":null);return()=>{const{value:i}=n;return v("li",{class:[`${i}-breadcrumb-item`,e.clickable&&`${i}-breadcrumb-item--clickable`]},v(l.value,{class:`${i}-breadcrumb-item__link`,"aria-current":m.value,href:e.href,onClick:e.onClick},o),e.showSeparator&&v("span",{class:`${i}-breadcrumb-item__separator`,"aria-hidden":"true"},$(o.separator,()=>{var c;return[(c=e.separator)!==null&&c!==void 0?c:r.value]})))}}});export{G as N,J as a};
