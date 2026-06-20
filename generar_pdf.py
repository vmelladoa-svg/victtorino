# -*- coding: utf-8 -*-
import markdown, subprocess, os
from pathlib import Path

md_path = Path('informe_gerente_comercial_2026-05-13.md')
html_path = Path('informe_gerente_comercial_2026-05-13.html')
pdf_path  = Path('informe_gerente_comercial_2026-05-13.pdf')

md_text = md_path.read_text(encoding='utf-8')
body = markdown.markdown(md_text, extensions=['tables', 'nl2br'])

html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Informe Gerente Comercial - Victtorino 2026-05-13</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 11px;
    color: #1a1a2e;
    background: #fff;
    padding: 32px 40px;
    max-width: 960px;
    margin: auto;
  }}
  h1 {{
    font-size: 20px;
    color: #fff;
    background: #1a1a2e;
    padding: 18px 24px;
    border-radius: 6px;
    margin-bottom: 6px;
  }}
  h2 {{
    font-size: 13px;
    color: #fff;
    background: #e63946;
    padding: 8px 14px;
    border-radius: 4px;
    margin: 22px 0 10px 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}
  h3 {{
    font-size: 12px;
    color: #1a1a2e;
    border-left: 3px solid #e63946;
    padding-left: 8px;
    margin: 14px 0 6px 0;
  }}
  p {{
    margin: 5px 0;
    line-height: 1.55;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 8px 0 12px 0;
    font-size: 10.5px;
  }}
  th {{
    background: #1a1a2e;
    color: #fff;
    padding: 7px 10px;
    text-align: left;
    font-weight: 600;
  }}
  td {{
    padding: 6px 10px;
    border-bottom: 1px solid #e8e8f0;
  }}
  tr:nth-child(even) td {{ background: #f5f5fb; }}
  tr:hover td {{ background: #eeeef8; }}
  code {{
    background: #f0f0f8;
    padding: 1px 5px;
    border-radius: 3px;
    font-family: 'Consolas', monospace;
    font-size: 10px;
  }}
  blockquote {{
    border-left: 3px solid #e63946;
    padding: 6px 12px;
    background: #fff5f5;
    margin: 8px 0;
    font-style: italic;
    color: #444;
  }}
  ul, ol {{
    padding-left: 18px;
    margin: 4px 0;
  }}
  li {{ margin: 2px 0; line-height: 1.5; }}
  hr {{
    border: none;
    border-top: 1px solid #ddd;
    margin: 18px 0;
  }}
  .footer {{
    margin-top: 30px;
    font-size: 9px;
    color: #888;
    text-align: center;
    border-top: 1px solid #eee;
    padding-top: 10px;
  }}
  @media print {{
    body {{ padding: 0; }}
    h2 {{ break-before: auto; }}
    table {{ page-break-inside: avoid; }}
  }}
</style>
</head>
<body>
{body}
<div class="footer">Victtorino — Informe Gerente Comercial ML | 13 de mayo de 2026</div>
</body>
</html>"""

html_path.write_text(html, encoding='utf-8')
print(f'HTML generado: {html_path.resolve()}')

# Intentar convertir con Edge headless
edge_paths = [
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
]
chrome_paths = [
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
]

browser = None
for p in edge_paths + chrome_paths:
    if os.path.exists(p):
        browser = p
        break

if browser:
    abs_html = str(html_path.resolve())
    abs_pdf  = str(pdf_path.resolve())
    cmd = [
        browser,
        '--headless=new',
        '--disable-gpu',
        '--no-sandbox',
        f'--print-to-pdf={abs_pdf}',
        '--print-to-pdf-no-header',
        f'file:///{abs_html}'
    ]
    result = subprocess.run(cmd, capture_output=True, timeout=30)
    if pdf_path.exists() and pdf_path.stat().st_size > 10000:
        print(f'PDF generado: {pdf_path.resolve()}')
    else:
        print(f'Edge/Chrome fallo (rc={result.returncode}). Stderr: {result.stderr[:200]}')
        print(f'Usa el HTML para imprimir a PDF desde el navegador: {abs_html}')
else:
    print('No se encontro Edge ni Chrome instalado.')
    print(f'Abre el HTML en el navegador y usa Ctrl+P para guardar como PDF:')
    print(f'  {html_path.resolve()}')
