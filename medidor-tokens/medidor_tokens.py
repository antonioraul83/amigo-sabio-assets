#!/usr/bin/env python3
"""Medidor de tokens por agente.

Lee las conversaciones que Claude Code guarda en tu PC
(~/.claude/projects/**/*.jsonl), suma los tokens de cada sesión
(incluidos sus subagentes) y crea medidor-tokens.html con una barra por agente.

Uso:  python medidor_tokens.py            (últimos 30 días)
      python medidor_tokens.py --dias 7
      python medidor_tokens.py --dias 0   (todo el historial)
"""
import argparse
import html
import json
import os
import webbrowser
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Peso de cada tipo de token respecto a un token de entrada normal
# (proporciones de precio de la API: escribir caché 1,25x; leer caché 0,1x; salida 5x).
PESOS = {"entrada": 1.0, "cache_escrita": 1.25, "cache_leida": 0.1, "salida": 5.0}


def fecha(ts):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def leer_sesiones(raiz, desde):
    sesiones = defaultdict(lambda: {
        "entrada": 0, "cache_escrita": 0, "cache_leida": 0, "salida": 0,
        "mensajes": 0, "titulo": None, "primer_texto": None, "carpeta": None,
        "inicio": None, "fin": None, "subagentes": defaultdict(int),
    })
    vistos = set()
    for fichero in raiz.rglob("*.jsonl"):
        # Los subagentes viven en <proyecto>/<id-sesión>/subagents/agent-*.jsonl
        partes = fichero.relative_to(raiz).parts
        es_sub = "subagents" in partes
        sid = partes[-3] if es_sub and len(partes) >= 3 else fichero.stem
        s = sesiones[sid]
        tipo_sub = None
        if es_sub:
            meta = fichero.with_suffix(".meta.json")
            if meta.exists():
                try:
                    tipo_sub = json.loads(meta.read_text(encoding="utf-8")).get("agentType")
                except Exception:
                    pass
            tipo_sub = tipo_sub or "subagente"
        try:
            lineas = fichero.open(encoding="utf-8", errors="replace")
        except OSError:
            continue
        with lineas:
            for linea in lineas:
                try:
                    e = json.loads(linea)
                except Exception:
                    continue
                if not isinstance(e, dict):
                    continue
                t = e.get("type")
                if not es_sub:
                    for clave in ("customTitle", "agentName", "title"):
                        if e.get(clave) and t in ("custom-title", "agent-name", "title", "ai-title"):
                            s["titulo"] = e[clave]
                    if t == "summary" and e.get("summary") and not s["titulo"]:
                        s["titulo"] = e["summary"]
                    if e.get("cwd") and not s["carpeta"]:
                        s["carpeta"] = e["cwd"]
                    if t == "user" and not s["primer_texto"]:
                        c = (e.get("message") or {}).get("content")
                        if isinstance(c, str) and c.strip():
                            s["primer_texto"] = c.strip()[:80]
                if t != "assistant":
                    continue
                msg = e.get("message") or {}
                u = msg.get("usage")
                if not u:
                    continue
                cuando = fecha(e.get("timestamp", ""))
                if desde and cuando and cuando < desde:
                    continue
                # Una respuesta se guarda en varias líneas con el mismo uso: contarla una vez.
                clave = (sid, msg.get("id"), e.get("requestId"))
                if msg.get("id") and clave in vistos:
                    continue
                vistos.add(clave)
                tok = {
                    "entrada": u.get("input_tokens") or 0,
                    "cache_escrita": u.get("cache_creation_input_tokens") or 0,
                    "cache_leida": u.get("cache_read_input_tokens") or 0,
                    "salida": u.get("output_tokens") or 0,
                }
                for k, v in tok.items():
                    s[k] += v
                s["mensajes"] += 1
                if tipo_sub:
                    s["subagentes"][tipo_sub] += sum(tok[k] * PESOS[k] for k in tok)
                if cuando:
                    s["inicio"] = min(s["inicio"] or cuando, cuando)
                    s["fin"] = max(s["fin"] or cuando, cuando)
    return {k: v for k, v in sesiones.items() if v["mensajes"]}


def nombre(sid, s):
    if s["titulo"]:
        return s["titulo"]
    carpeta = Path(s["carpeta"]).name if s["carpeta"] else "?"
    texto = s["primer_texto"] or sid[:8]
    return f"{carpeta} · {texto}"


def millones(n):
    return f"{n / 1e6:.1f} M" if n >= 1e5 else f"{n / 1e3:.0f} k"


def pintar(sesiones, dias, salida):
    filas = []
    for sid, s in sesiones.items():
        peso = sum(s[k] * PESOS[k] for k in PESOS)
        filas.append((peso, sid, s))
    filas.sort(reverse=True)
    total = sum(f[0] for f in filas) or 1
    maximo = filas[0][0] if filas else 1
    cuerpo = []
    for peso, sid, s in filas:
        pct = peso / total * 100
        ancho = peso / maximo * 100
        subs = ", ".join(f"{html.escape(k)} {millones(v)}" for k, v in
                         sorted(s["subagentes"].items(), key=lambda x: -x[1]))
        fechas = ""
        if s["inicio"]:
            fechas = f'{s["inicio"]:%d/%m} – {s["fin"]:%d/%m}'
        cuerpo.append(f"""
<div class="fila">
  <div class="cab"><b>{html.escape(nombre(sid, s))}</b><span>{pct:.1f} %</span></div>
  <div class="barra"><div style="width:{ancho:.1f}%"></div></div>
  <div class="det">Cómputo {millones(peso)} · salida {millones(s['salida'])} · entrada nueva {millones(s['entrada'] + s['cache_escrita'])} · releído de caché {millones(s['cache_leida'])} · {s['mensajes']} respuestas · {fechas}{('<br>Subagentes: ' + subs) if subs else ''}</div>
</div>""")
    periodo = "todo el historial" if not dias else f"últimos {dias} días"
    pagina = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Medidor de tokens</title>
<style>
:root{{--bg:#f7f6f2;--fg:#1d1d1b;--suave:#6b6a64;--barra:#e4e1d8;--lleno:#c4622d}}
@media (prefers-color-scheme:dark){{:root{{--bg:#1b1a18;--fg:#eceae4;--suave:#a3a199;--barra:#34322e;--lleno:#e0814f}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.4 system-ui,sans-serif;margin:0;padding:24px 16px;max-width:860px;margin:auto}}
h1{{font-size:22px;margin:0 0 4px}} .sub{{color:var(--suave);margin-bottom:24px}}
.fila{{margin-bottom:18px}} .cab{{display:flex;justify-content:space-between;gap:12px}}
.barra{{background:var(--barra);border-radius:6px;height:14px;margin:6px 0;overflow:hidden}}
.barra div{{background:var(--lleno);height:100%}} .det{{color:var(--suave);font-size:13px}}
</style></head><body>
<h1>Medidor de tokens por agente</h1>
<div class="sub">{periodo} · {len(filas)} sesiones · cómputo total {millones(total)} ·
generado {datetime.now():%d/%m/%Y %H:%M}<br>
«Cómputo» pondera como el precio: salida ×5, entrada ×1, escribir caché ×1,25, releer caché ×0,1.</div>
{''.join(cuerpo) or '<p>No hay datos en ese periodo.</p>'}
</body></html>"""
    salida.write_text(pagina, encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dias", type=int, default=30, help="cuántos días mirar (0 = todo)")
    p.add_argument("--carpeta", default=os.path.join(Path.home(), ".claude", "projects"))
    p.add_argument("--salida", default="medidor-tokens.html")
    p.add_argument("--no-abrir", action="store_true")
    a = p.parse_args()
    raiz = Path(a.carpeta)
    if not raiz.exists():
        raise SystemExit(f"No encuentro {raiz}. Pásale la ruta con --carpeta.")
    desde = datetime.now(timezone.utc) - timedelta(days=a.dias) if a.dias else None
    sesiones = leer_sesiones(raiz, desde)
    salida = Path(a.salida).resolve()
    pintar(sesiones, a.dias, salida)
    print(f"{len(sesiones)} sesiones leídas. Medidor en: {salida}")
    if not a.no_abrir:
        webbrowser.open(salida.as_uri())


if __name__ == "__main__":
    main()
