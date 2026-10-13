"""PLANO (pré-voo): a ficha de planejamento de uma peça, checada ANTES de montar qualquer HTML.

Por que existe: verificar só depois do render gera retrabalho. A pessoa disse: "você tem que planejar tudo isso na hora
de fazer ou antes de fazer, para evitar retrabalho". O plano fecha as restrições primeiro:
  formato → área útil (margem ∩ fora da interface do app) → grade → hierarquia → camadas → cada TEXTO medido na
  fonte, no tamanho e na coluna escolhidos (quebra pelas regras do PT-BR) → pilha vertical somada → contraste previsto
  contra a cor de fundo planejada → zonas extras (ícones do Reels).
Se o plano tem problema, não se monta a peça. O verificador e a prova de camadas depois só CONFIRMAM.

Uso:
  pl = Plano(1080, 1920, "story", nome="rompe-visor 9:16", objetivo="lembrar a noite 3 da live")
  pl.camadas("fundo estúdio verde", "painel degradê", "professor P&B (sujeito)", "visor (frente)", "texto/logo")
  t = pl.texto("nome", "NOME DA PESSOA", "Schibsted Grotesk:900", cap=92, cols=(1, 6), linhas=2, heroi=True,
               cor="#FFFFFF", sobre="#0B0B0B")
  d = pl.texto("data", "QUA 11/11, 20H30", "Martian Mono:800:wdth=75", cap=40, cols=(1, 6), ler=True, ...)
  pl.pilha([("logo", 170), 1, t, 1, d], topo=True)   # números soltos = respiros em U
  print(pl.ficha()); pl.esboco("plano.png"); assert not pl.problemas
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compor as K  # noqa: E402


def _lum(hexa):
    c = [int(hexa.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contraste(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


class Plano:
    def __init__(self, W, H, formato, nome="", objetivo="", colunas=6, gutter=24, margem=None):
        self.W, self.H, self.formato, self.nome, self.objetivo = W, H, formato, nome, objetivo
        self.s = min(W, H)
        m0 = round(0.074 * self.s)
        f = K.FORMATOS.get(formato, {})
        self.zona = f.get("zona", (0, 0, 0, 0))
        self.excl = f.get("excl", [])
        zt, zb, zl, zr = self.zona
        self.m = max(m0, zl, zr) if margem is None else margem
        self.my = m0
        self.area = (self.m, max(self.my, zt), W - self.m, H - max(self.my, zb))
        self.U = round(0.022 * self.s)
        self.ncol, self.gut = colunas, gutter
        self.col = (self.area[2] - self.area[0] - (colunas - 1) * gutter) / colunas
        self.blocos, self.lista_camadas, self.problemas = [], [], []

    # ------------------------------------------------------------------ grade
    def colunas(self, c0, c1):
        """x0, x1 das colunas c0..c1 (1 = primeira), incluindo os vãos internos."""
        x0 = self.area[0] + (c0 - 1) * (self.col + self.gut)
        return x0, x0 + (c1 - c0 + 1) * self.col + (c1 - c0) * self.gut

    def camadas(self, *nomes):
        """Pilha planejada, de trás para a frente (fundo → … → texto/acabamento). Cada uma com função."""
        self.lista_camadas = list(nomes)

    # ------------------------------------------------------------------ texto medido
    def texto(self, nome, texto, spec, cap, cols=(1, 6), linhas=1, ler=False, cor=None, sobre=None, tr=0.0,
              heroi=False, peso_negrito=None):
        """Mede o texto na fonte/tamanho REAIS, quebra pelas regras do PT-BR na largura das colunas e confere:
        cabe em `linhas`? maiúscula ≥ mínimo (≥ 34 px se `ler`)? contraste previsto contra `sobre` (uma cor ou
        lista de cores = os tons do fundo naquela região) ≥ 4,5:1 (3:1 se texto grande)?"""
        x0, x1 = self.colunas(*cols)
        larg_disp = x1 - x0
        f = K.font(spec)
        corpo = cap / f.cap
        ls = K.quebra(spec, texto, larg_disp, cap, tr, max_lines=max(linhas, 6))
        larg = 0.0
        for ln in ls:
            l_, _, r_, _ = K.ink(spec, ln, tr)
            larg = max(larg, (r_ - l_) * corpo)
        passo = K.entrelinha(spec, ls, cap, tr) if len(ls) > 1 else cap
        alt = passo * (len(ls) - 1) + cap
        b = dict(nome=nome, texto=texto, spec=spec, cap=cap, corpo=corpo, cols=cols, x0=x0, x1=x1,
                 larg=larg, disp=larg_disp, linhas=ls, passo=passo, altura=alt, ler=ler, heroi=heroi, cor=cor,
                 sobre=sobre, contraste=None)
        esc = 1080 / self.s
        if len(ls) > linhas:
            self.problemas.append(f"'{nome}' precisa de {len(ls)} linhas (planejado {linhas}) em {larg_disp:.0f} px")
        if larg > larg_disp + 0.5:
            self.problemas.append(f"'{nome}' não cabe: {larg:.0f} px de tinta > {larg_disp:.0f} px de coluna")
        if cap < K.CAP_MIN * self.s - 0.5:
            self.problemas.append(f"'{nome}' pequeno: maiúscula {cap:.0f} < {K.CAP_MIN * self.s:.0f} px")
        if ler and cap < K.CAP_LER * self.s - 0.5:
            self.problemas.append(f"'{nome}' precisa ser lido: maiúscula {cap:.0f} < {K.CAP_LER * self.s:.0f} px")
        if cor and sobre:
            fundos = sobre if isinstance(sobre, (list, tuple)) else [sobre]
            cr = min(contraste(cor, c) for c in fundos)
            negrito = (peso_negrito if peso_negrito is not None else
                       any(w in spec for w in (":700", ":800", ":900")))
            grande = corpo * esc >= 72 or (corpo * esc >= 56 and negrito)
            lim = 3.0 if grande else 4.5
            b["contraste"] = (round(cr, 2), lim)
            if cr < lim:
                self.problemas.append(f"'{nome}' contraste previsto {cr:.1f}:1 < {lim}:1 (cor {cor} sobre {fundos})")
        self.blocos.append(b)
        return b

    def caixa(self, nome, w, h, cols=None, x0=None):
        """Bloco não-texto (logo, foto, tarja) com tamanho já decidido."""
        if cols:
            x0, _ = self.colunas(*cols)
        b = dict(nome=nome, x0=x0 if x0 is not None else self.area[0], x1=(x0 if x0 is not None else self.area[0]) + w,
                 altura=h, larg=w, disp=w, linhas=None)
        self.blocos.append(b)
        return b

    # ------------------------------------------------------------------ pilha vertical
    def pilha(self, itens, topo=True, y0=None, y1=None):
        """Empilha blocos com respiros em U (números soltos). Soma as alturas ANTES de montar: cabe na área?
        Posiciona (y0/y1 de cada bloco) a partir do topo da área (topo=True) ou da base. Confere a coluna de ícones."""
        a0, a1 = (y0 if y0 is not None else self.area[1]), (y1 if y1 is not None else self.area[3])
        tot = sum(self.U * i if isinstance(i, (int, float)) else i["altura"] for i in itens)
        if tot > a1 - a0 + 0.5:
            self.problemas.append(f"pilha não cabe: {tot:.0f} px > {a1 - a0:.0f} px disponíveis")
        y = a0 if topo else a1 - tot
        for i in itens:
            if isinstance(i, (int, float)):
                y += self.U * i
                continue
            i["y0"], i["y1"] = y, y + i["altura"]
            y += i["altura"]
            for z in self.excl:
                if K._inter((i["x0"], i["y0"], i["x0"] + i["larg"], i["y1"]), z, 0.5):
                    self.problemas.append(f"'{i['nome']}' cai sob os ícones do app {z}")
        return tot, (a1 - a0) - tot

    # ------------------------------------------------------------------ saídas
    def ficha(self):
        L = [f"# Plano: {self.nome}", f"- Objetivo: {self.objetivo}",
             f"- Formato: {self.formato} {self.W}×{self.H} · área útil x {self.area[0]:.0f}–{self.area[2]:.0f}, "
             f"y {self.area[1]:.0f}–{self.area[3]:.0f} · U = {self.U} px · grade {self.ncol} col de "
             f"{self.col:.0f} + vão {self.gut}",
             f"- Ícones do app (proibido texto): {self.excl or '—'}",
             "- Camadas (trás → frente): " + (" → ".join(self.lista_camadas) or "—"),
             "- Hierarquia: herói = " + (", ".join(b["nome"] for b in self.blocos if b.get("heroi")) or "—"),
             "", "| bloco | texto | fonte | maiúscula/corpo | colunas | linhas | tinta/disp. | contraste |",
             "|---|---|---|---|---|---|---|---|"]
        for b in self.blocos:
            if b.get("linhas") is None:
                L.append(f"| {b['nome']} | — | — | — | — | — | {b['larg']:.0f} | — |")
                continue
            c = f"{b['contraste'][0]}:1 (≥{b['contraste'][1]})" if b.get("contraste") else "—"
            L.append(f"| {b['nome']}{' ★' if b['heroi'] else ''} | {' / '.join(b['linhas'])} | {b['spec']} | "
                     f"{b['cap']:.0f}/{b['corpo']:.0f} px{' (ler)' if b['ler'] else ''} | {b['cols'][0]}–{b['cols'][1]} | "
                     f"{len(b['linhas'])} | {b['larg']:.0f}/{b['disp']:.0f} | {c} |")
        L += ["", "**Problemas:** " + ("nenhum" if not self.problemas else "")] + [f"- {p}" for p in self.problemas]
        return "\n".join(L)

    def esboco(self, out):
        """Esboço (wireframe) do plano: zonas do app, grade, blocos posicionados — para olhar ANTES de montar."""
        from PIL import Image, ImageDraw
        W, H = self.W, self.H
        im = Image.new("RGB", (W, H), (236, 236, 232))
        d = ImageDraw.Draw(im, "RGBA")
        zt, zb, zl, zr = self.zona
        for r in ((0, 0, W, zt), (0, H - zb, W, H), (0, 0, zl, H), (W - zr, 0, W, H), *self.excl):
            if r[2] > r[0] and r[3] > r[1]:
                d.rectangle(r, fill=(255, 60, 60, 60))
        for i in range(self.ncol):
            x0, x1 = self.colunas(i + 1, i + 1)
            d.rectangle((x0, self.area[1], x1, self.area[3]), fill=(0, 160, 255, 28))
        d.rectangle(self.area, outline=(0, 120, 255, 255), width=2)
        for b in self.blocos:
            if "y0" not in b:
                continue
            cor = (20, 20, 20, 210) if b.get("heroi") else (90, 90, 90, 170)
            d.rectangle((b["x0"], b["y0"], b["x0"] + b["larg"], b["y1"]), fill=cor)
            d.text((b["x0"] + 6, b["y0"] + 4), b["nome"], fill=(255, 255, 255))
        im.save(out)
        return out
