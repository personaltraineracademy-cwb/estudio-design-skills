'use client'
import { useEffect, useRef } from 'react'
import { whenIdle } from '@/lib/idle'
import marca from '@/content/marca.json'

/**
 * Grão/ruído em WebGL próprio (sem biblioteca; ~1,3 KB gzip) com reserva em CSS.
 * Base: skills/direcao-de-arte/assets/web/snippets/shader-grao.js.
 *
 * variant="field"    fundo de "fumaça" na cor de destaque + grão (opaco). Use dentro de uma seção `position: relative`.
 * variant="overlay"  só o grão, transparente, para pôr por cima de foto/seção (position: absolute/fixed pelo className).
 *
 * Comportamento:
 *  - 1 canvas, resolução `scale` (0,5) x CSS px, devicePixelRatio ignorado: nunca pesado.
 *  - Inicia em idle; pausa quando sai da tela e quando a aba fica em segundo plano; `fps` limitado (24).
 *  - prefers-reduced-motion: desenha UM quadro fixo (`frame`, em segundos) e não anima.
 *  - Sem WebGL / contexto perdido: o fundo CSS (gradiente + tile PNG do <body>) continua lá.
 * O grão FIXO da página inteira é CSS (`body::after` com public/img/grao-128.png), não este componente.
 */
export interface GrainProps {
  variant?: 'field' | 'overlay'
  /** cor das nuvens do campo (hex) */
  tint?: string
  /** cor de base (hex) */
  base?: string
  /** força do grão (0–0,2). Padrão: field 0,06 · overlay 0,10 */
  intensity?: number
  /** resolução relativa ao tamanho CSS (0,25–1) */
  scale?: number
  fps?: number
  /** instante (s) do quadro parado em reduced-motion */
  frame?: number
  /** false = um quadro só, nunca anima */
  animated?: boolean
  className?: string
}

const VERT = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}'
const FRAG = `#ifdef GL_FRAGMENT_PRECISION_HIGH
precision highp float;
#else
precision mediump float;
#endif
uniform vec2 r;uniform float t;uniform vec3 a;uniform vec3 b;uniform float k;uniform float m;
float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float n(vec2 p){vec2 i=floor(p),u=fract(p);u=u*u*(3.-2.*u);return mix(mix(h(i),h(i+vec2(1.,0.)),u.x),mix(h(i+vec2(0.,1.)),h(i+1.),u.x),u.y);}
void main(){
  float g=h(gl_FragCoord.xy+fract(t)*37.)-.5;
  if(m>.5){float al=abs(g)*2.*k;vec3 c=g>0.?vec3(1.):vec3(0.);gl_FragColor=vec4(c*al,al);return;}
  vec2 q=gl_FragCoord.xy/r;q.x*=r.x/r.y;
  float s=n(q*2.2+vec2(t*.05,-t*.03))*.6+n(q*5.1-t*.04)*.3+n(q*11.)*.1;
  vec3 c=mix(b,a,smoothstep(.45,.95,s)*.35)+g*k;
  gl_FragColor=vec4(c,1.);
}`

const hex = (v: string): [number, number, number] => {
  const m = v.replace('#', '')
  const n = m.length === 3 ? m.split('').map((c) => c + c).join('') : m
  const i = parseInt(n, 16)
  return [((i >> 16) & 255) / 255, ((i >> 8) & 255) / 255, (i & 255) / 255]
}

type Options = Required<Pick<GrainProps, 'variant' | 'tint' | 'base' | 'intensity' | 'scale' | 'fps' | 'frame' | 'animated'>>

/** Inicia o desenho. Devolve a função de limpeza, ou null se não houver WebGL. */
function start(canvas: HTMLCanvasElement, o: Options): (() => void) | null {
  const overlay = o.variant === 'overlay'
  const gl = canvas.getContext('webgl', {
    antialias: false,
    alpha: overlay,
    premultipliedAlpha: true,
    depth: false,
    powerPreference: 'low-power',
  })
  if (!gl) return null
  const sh = (type: number, src: string) => {
    const s = gl.createShader(type)
    if (!s) return null
    gl.shaderSource(s, src)
    gl.compileShader(s)
    return gl.getShaderParameter(s, gl.COMPILE_STATUS) ? s : null
  }
  const vs = sh(gl.VERTEX_SHADER, VERT)
  const fs = sh(gl.FRAGMENT_SHADER, FRAG)
  if (!vs || !fs) return null
  const prog = gl.createProgram()
  gl.attachShader(prog, vs)
  gl.attachShader(prog, fs)
  gl.linkProgram(prog)
  gl.useProgram(prog)
  const buf = gl.createBuffer()
  gl.bindBuffer(gl.ARRAY_BUFFER, buf)
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW)
  const loc = gl.getAttribLocation(prog, 'p')
  gl.enableVertexAttribArray(loc)
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0)
  const U = (n: string) => gl.getUniformLocation(prog, n)
  gl.uniform3fv(U('a'), hex(o.tint))
  gl.uniform3fv(U('b'), hex(o.base))
  gl.uniform1f(U('k'), o.intensity)
  gl.uniform1f(U('m'), overlay ? 1 : 0)
  if (overlay) gl.clearColor(0, 0, 0, 0)

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  const still = reduced || !o.animated
  let visible = true
  let tabVisible = !document.hidden
  let raf = 0
  let last = 0
  const t0 = performance.now()
  const minGap = 1000 / Math.max(1, o.fps)

  const size = () => {
    canvas.width = Math.max(2, Math.floor(canvas.clientWidth * o.scale))
    canvas.height = Math.max(2, Math.floor(canvas.clientHeight * o.scale))
    gl.viewport(0, 0, canvas.width, canvas.height)
    gl.uniform2f(U('r'), canvas.width, canvas.height)
  }
  const draw = (seconds: number) => {
    gl.uniform1f(U('t'), seconds)
    if (overlay) gl.clear(gl.COLOR_BUFFER_BIT)
    gl.drawArrays(gl.TRIANGLES, 0, 3)
  }
  const loop = (now: number) => {
    if (!visible || !tabVisible) return
    if (now - last >= minGap) {
      last = now
      draw((now - t0) / 1000)
    }
    raf = requestAnimationFrame(loop)
  }
  const resume = () => {
    cancelAnimationFrame(raf)
    if (!still && visible && tabVisible) raf = requestAnimationFrame(loop)
  }

  size()
  draw(still ? o.frame : (performance.now() - t0) / 1000 + o.frame)
  const ro = new ResizeObserver(() => {
    size()
    draw(still ? o.frame : (performance.now() - t0) / 1000 + o.frame)
  })
  ro.observe(canvas)
  const io = new IntersectionObserver((e) => {
    visible = e[0]?.isIntersecting ?? true
    resume()
  })
  io.observe(canvas)
  const onVis = () => {
    tabVisible = !document.hidden
    resume()
  }
  document.addEventListener('visibilitychange', onVis)
  const onLost = (e: Event) => {
    e.preventDefault()
    visible = false
    cancelAnimationFrame(raf)
    canvas.style.display = 'none'
    canvas.parentElement?.removeAttribute('data-gl')
  }
  canvas.addEventListener('webglcontextlost', onLost)
  resume()

  return () => {
    cancelAnimationFrame(raf)
    ro.disconnect()
    io.disconnect()
    document.removeEventListener('visibilitychange', onVis)
    canvas.removeEventListener('webglcontextlost', onLost)
    gl.getExtension('WEBGL_lose_context')?.loseContext()
  }
}

export function Grain({
  variant = 'field',
  tint = marca.cores.destaque,
  base = marca.cores.ink,
  intensity,
  scale = 0.5,
  fps = 24,
  frame = 3,
  animated = true,
  className,
}: GrainProps) {
  const wrap = useRef<HTMLDivElement>(null)
  const k = intensity ?? (variant === 'overlay' ? 0.1 : 0.06)

  useEffect(() => {
    const el = wrap.current
    const canvas = el?.querySelector('canvas')
    if (!el || !canvas) return
    let stop: (() => void) | null = null
    const cancel = whenIdle(() => {
      stop = start(canvas, { variant, tint, base, intensity: k, scale, fps, frame, animated })
      if (stop) el.setAttribute('data-gl', '1')
    })
    return () => {
      cancel()
      stop?.()
      el.removeAttribute('data-gl')
    }
  }, [variant, tint, base, k, scale, fps, frame, animated])

  return (
    <div ref={wrap} className={['est-grain', className].filter(Boolean).join(' ')} data-variant={variant} aria-hidden="true">
      <canvas />
    </div>
  )
}
