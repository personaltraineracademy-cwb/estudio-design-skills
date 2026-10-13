/* shader-grao.js — fundo de ruído/grão em WebGL puro, sem biblioteca. Uso: ShaderGrao(canvas,{cor:[.8,.66,.37],base:[.05,.045,.035]}) */
function ShaderGrao(c,o){o=o||{};var cor=o.cor||[.8,.66,.37],base=o.base||[.05,.045,.035],rm=matchMedia("(prefers-reduced-motion: reduce)").matches,
g=c.getContext("webgl",{antialias:false,alpha:false,depth:false,powerPreference:"low-power"});if(!g)return null;
function sh(t,s){var h=g.createShader(t);g.shaderSource(h,s);g.compileShader(h);return g.getShaderParameter(h,g.COMPILE_STATUS)?h:null}
var v=sh(g.VERTEX_SHADER,"attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}"),
f=sh(g.FRAGMENT_SHADER,"#ifdef GL_FRAGMENT_PRECISION_HIGH\nprecision highp float;\n#else\nprecision mediump float;\n#endif\n"+
"uniform vec2 r;uniform float t;uniform vec3 a,b;"+
"float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}"+
"float n(vec2 p){vec2 i=floor(p),u=fract(p);u=u*u*(3.-2.*u);return mix(mix(h(i),h(i+vec2(1,0)),u.x),mix(h(i+vec2(0,1)),h(i+1.),u.x),u.y);}"+
"void main(){vec2 q=gl_FragCoord.xy/r;q.x*=r.x/r.y;float s=n(q*2.2+vec2(t*.05,-t*.03))*.6+n(q*5.1-t*.04)*.3+n(q*11.)*.1;"+
"vec3 c=mix(b,a,smoothstep(.45,.95,s)*.35);c+=(h(gl_FragCoord.xy+fract(t)*37.)-.5)*.06;gl_FragColor=vec4(c,1.);}");
if(!v||!f)return null;var p=g.createProgram();g.attachShader(p,v);g.attachShader(p,f);g.linkProgram(p);g.useProgram(p);
var bf=g.createBuffer();g.bindBuffer(g.ARRAY_BUFFER,bf);g.bufferData(g.ARRAY_BUFFER,new Float32Array([-1,-1,3,-1,-1,3]),g.STATIC_DRAW);
var l=g.getAttribLocation(p,"p");g.enableVertexAttribArray(l);g.vertexAttribPointer(l,2,g.FLOAT,false,0,0);
var U=function(n){return g.getUniformLocation(p,n)};g.uniform3fv(U("a"),cor);g.uniform3fv(U("b"),base);
var on=true,vis=true,raf=0,t0=performance.now(),sc=o.escala||.5;
function size(){c.width=Math.max(2,c.clientWidth*sc|0);c.height=Math.max(2,c.clientHeight*sc|0);g.viewport(0,0,c.width,c.height);g.uniform2f(U("r"),c.width,c.height)}
function draw(now){g.uniform1f(U("t"),rm?3:(now-t0)/1000);g.drawArrays(g.TRIANGLES,0,3)}
function loop(now){if(on&&vis&&!rm){draw(now);raf=requestAnimationFrame(loop)}}
size();draw(t0+3000);addEventListener("resize",function(){size();draw(performance.now())});
new IntersectionObserver(function(e){on=e[0].isIntersecting;if(on&&vis&&!rm){cancelAnimationFrame(raf);raf=requestAnimationFrame(loop)}}).observe(c);
document.addEventListener("visibilitychange",function(){vis=!document.hidden;if(vis&&on&&!rm){cancelAnimationFrame(raf);raf=requestAnimationFrame(loop)}});
c.addEventListener("webglcontextlost",function(e){e.preventDefault();on=false;c.style.display="none"});
if(!rm)raf=requestAnimationFrame(loop);return{draw:draw,g:g}}
