from __future__ import annotations

import html
import json
from typing import Optional

import webview


SPLASH_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: #0D1B2A;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    font-family: 'Inter', system-ui, sans-serif;
    color: #fff;
    user-select: none;
  }

  .logo-wrap {
    width: 88px;
    height: 88px;
    border-radius: 24px;
    background: linear-gradient(135deg, #1A56DB, #0EA5E9);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 22px;
    box-shadow: 0 8px 32px rgba(26,86,219,0.45);
  }

  .logo-wrap svg {
    width: 48px;
    height: 48px;
    fill: none;
    stroke: #fff;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
  }

  h1 {
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin-bottom: 6px;
  }

  .subtitle {
    font-size: 13px;
    color: rgba(255,255,255,0.55);
    font-weight: 500;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 48px;
  }

  .bar-track {
    width: 240px;
    height: 5px;
    background: rgba(255,255,255,0.12);
    border-radius: 999px;
    overflow: hidden;
    margin-bottom: 14px;
  }

  .bar-fill {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, #1A56DB, #0EA5E9);
    border-radius: 999px;
    transition: width 0.3s ease;
  }

  .status-text {
    font-size: 12px;
    color: rgba(255,255,255,0.45);
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    min-height: 18px;
  }
</style>
</head>
<body>
  <div class="logo-wrap">
    <!-- icono: scan-face estilo Lucide -->
    <svg viewBox="0 0 24 24">
      <path d="M3 7V5a2 2 0 0 1 2-2h2"/>
      <path d="M17 3h2a2 2 0 0 1 2 2v2"/>
      <path d="M21 17v2a2 2 0 0 1-2 2h-2"/>
      <path d="M7 21H5a2 2 0 0 1-2-2v-2"/>
      <circle cx="12" cy="10" r="3"/>
      <path d="M7 16.8A6 6 0 0 1 12 14a6 6 0 0 1 5 2.8"/>
    </svg>
  </div>

  <h1>IdentifyMe</h1>
  <p class="subtitle">Sistema biometrico escolar</p>

  <div class="bar-track">
    <div class="bar-fill" id="bar"></div>
  </div>
  <p class="status-text" id="status">Iniciando...</p>

  <script>
    const bar    = document.getElementById('bar');
    const status = document.getElementById('status');

    window.updateProgress = (pct, msg) => {
      if (typeof pct === 'number') {
        bar.style.width = pct + '%';
      }
      if (msg) {
        status.textContent = msg;
      }
    };

    window.updateProgress(5, 'Iniciando...');
  </script>
</body>
</html>"""


def error_html(title: str, detail: str, hint: str = "") -> str:
    hint_block = f'<p class="hint">{html.escape(hint)}</p>' if hint else ""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #0D1B2A;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    font-family: 'Inter', system-ui, sans-serif;
    color: #fff;
    padding: 32px;
    text-align: center;
  }}
  .icon {{
    width: 72px; height: 72px;
    border-radius: 50%;
    background: rgba(185,28,28,0.18);
    border: 2px solid rgba(185,28,28,0.5);
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 24px;
  }}
  .icon svg {{
    width: 36px; height: 36px;
    stroke: #FCA5A5; stroke-width: 2;
    stroke-linecap: round; stroke-linejoin: round; fill: none;
  }}
  h2 {{
    font-size: 20px; font-weight: 800;
    color: #FCA5A5; margin-bottom: 10px;
  }}
  .detail {{
    font-size: 13px; color: rgba(255,255,255,0.55);
    line-height: 1.6; margin-bottom: 16px;
    max-width: 320px;
  }}
  .hint {{
    font-size: 12px;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px;
    padding: 10px 16px;
    color: rgba(255,255,255,0.45);
    line-height: 1.6;
    max-width: 320px;
  }}
</style>
</head>
<body>
  <div class="icon">
    <svg viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="10"/>
      <line x1="12" y1="8" x2="12" y2="12"/>
      <line x1="12" y1="16" x2="12.01" y2="16"/>
    </svg>
  </div>
  <h2>{html.escape(title)}</h2>
  <p class="detail">{detail}</p>
  {hint_block}
</body>
</html>"""


def update_splash(splash: webview.Window, pct: int, message: str) -> None:
    try:
        splash.evaluate_js(
            "window.updateProgress(%s, %s);" % (pct, json.dumps(message))
        )
    except Exception:
        return


def format_error_details(lines: list[str]) -> str:
    return "<br>".join(html.escape(line) for line in lines)
