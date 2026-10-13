import { LOGOS, type LogoKey } from '@/lib/logos.generated'
import marca from '@/content/marca.json'

/**
 * Logo do cliente, SVG inline. Componente de SERVIDOR (a tabela de logos nunca vai para o JavaScript do navegador).
 *
 * - `name`: nome do arquivo em `assets-src/logos/` sem `.svg` (padrão: "logo"; o símbolo costuma ser "logo-simbolo").
 * - Logo MONOCROMÁTICA recebe `currentColor`: `tone` escolhe a cor (claro = tinta, destaque, escuro = ink).
 *   Logo MULTICOR mantém as cores do arquivo (`tone` não se aplica): confira o fundo.
 * - O logo nunca arredonda, nunca recebe sombra nem efeito, nunca é recolorido fora destes tons. Área de respiro
 *   mínima = altura da maiúscula. Nunca mais de UMA logo na 1ª dobra (padrao-de-pagina.md §2).
 * - `data-logo` é o que o verificador (`check_pagina.py`) usa para contar logos.
 * - `label=""` = decorativo (aria-hidden).
 */
export interface LogoProps {
  name?: LogoKey
  tone?: 'claro' | 'destaque' | 'escuro'
  /** altura em px (ou qualquer valor CSS). A largura sai da proporção. */
  height?: number | string
  label?: string
  className?: string
}

const NOME = (marca.nome ?? '').trim()

export function Logo({ name = 'logo' as LogoKey, tone = 'claro', height, label, className }: LogoProps) {
  const logo = LOGOS[name]
  if (!logo) throw new Error(`[Logo] "${String(name)}" não existe em assets-src/logos/ (rode npm run assets)`)
  const mono = logo.mono
  const cls = ['est-logo', mono && `est-logo--${tone}`, className].filter(Boolean).join(' ')
  const style = {
    aspectRatio: `${logo.w} / ${logo.h}`,
    ...(height !== undefined ? { ['--logo-h' as string]: typeof height === 'number' ? `${height}px` : height } : null),
  }
  const nome = label ?? NOME
  const a11y = nome === '' ? { 'aria-hidden': true as const } : { role: 'img' as const, 'aria-label': nome }
  return (
    <svg
      className={cls}
      viewBox={logo.viewBox}
      fill={mono ? 'currentColor' : undefined}
      focusable="false"
      data-logo=""
      style={style}
      {...a11y}
      dangerouslySetInnerHTML={{ __html: logo.inner }}
    />
  )
}
