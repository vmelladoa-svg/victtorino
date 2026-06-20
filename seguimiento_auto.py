"""
Wrapper de automatización: chequea si hoy es una fecha de seguimiento pendiente,
y ejecuta el pipeline completo si corresponde.

Diseño:
  - Lista TARGET_DATES: D+7, D+14, D+28 (2026-05-30, 2026-06-06, 2026-06-20)
  - Estado persistente en data/auditoria/seguimiento_state.json (qué fechas ya se ejecutaron)
  - Si HOY >= cualquier fecha pendiente, ejecuta el pipeline UNA VEZ y la marca como done
  - Log completo en data/auditoria/seguimiento_runs/<fecha>.log
  - Si se pierde el día exacto (PC apagada), el primer login posterior lo dispara

Pipeline ejecutado:
  1. auditoria_ml.py         (~3 min)
  2. fix_visitas_snapshots.py (~1 min)
  3. analisis_auditoria_ml.py (~10 seg)
  4. seguimiento_comparar.py  (~5 seg)
"""
import json
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).parent
STATE_FILE = ROOT / "data" / "auditoria" / "seguimiento_state.json"
LOGS_DIR = ROOT / "data" / "auditoria" / "seguimiento_runs"
PY = sys.executable  # python.exe absoluto (asegura que la tarea encuentra Python)

TARGET_DATES = [
    date(2026, 5, 30),  # D+7
    date(2026, 6, 6),   # D+14
    date(2026, 6, 20),  # D+28
]

PIPELINE = [
    ("auditoria_ml.py",          180),  # timeout 3 min
    ("fix_visitas_snapshots.py", 120),
    ("analisis_auditoria_ml.py",  60),
    ("seguimiento_comparar.py",   60),
]


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"runs_done": [], "last_run_attempt": None}


def save_state(s):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8")


def log_line(log_file, msg):
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line)
    with log_file.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def main():
    today = date.today()
    state = load_state()
    runs_done = set(state.get("runs_done", []))

    # Fechas vencidas (today >= target) que aún no se ejecutaron
    pending = [d for d in TARGET_DATES if today >= d and d.isoformat() not in runs_done]
    state["last_run_attempt"] = today.isoformat()

    if not pending:
        # No hay nada que hacer. Igual loguear el chequeo
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        log_file = LOGS_DIR / f"check_{today.isoformat()}.log"
        log_line(log_file, f"Chequeo automático: hoy={today}, runs_done={sorted(runs_done)}, nada pendiente")
        save_state(state)
        return 0

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"run_{today.isoformat()}.log"
    log_line(log_file, f"=== SEGUIMIENTO AUTOMÁTICO ===")
    log_line(log_file, f"Hoy: {today}")
    log_line(log_file, f"Fechas pendientes a cubrir: {[d.isoformat() for d in pending]}")
    log_line(log_file, f"Python: {PY}")

    failed = False
    for script, timeout in PIPELINE:
        script_path = ROOT / script
        if not script_path.exists():
            log_line(log_file, f"✗ Script no existe: {script_path}")
            failed = True
            break
        log_line(log_file, f"\n>>> Ejecutando: {script} (timeout {timeout}s)")
        try:
            result = subprocess.run(
                [PY, str(script_path)],
                cwd=str(ROOT),
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=timeout,
            )
            # Loguear stdout/stderr
            if result.stdout:
                with log_file.open("a", encoding="utf-8") as f:
                    f.write("--- stdout ---\n")
                    f.write(result.stdout)
                    f.write("\n")
            if result.stderr:
                with log_file.open("a", encoding="utf-8") as f:
                    f.write("--- stderr ---\n")
                    f.write(result.stderr)
                    f.write("\n")
            if result.returncode != 0:
                log_line(log_file, f"✗ Exit code {result.returncode} — abortando pipeline")
                failed = True
                break
            log_line(log_file, f"✓ {script} OK")
        except subprocess.TimeoutExpired:
            log_line(log_file, f"✗ TIMEOUT después de {timeout}s — abortando")
            failed = True
            break
        except Exception as e:
            log_line(log_file, f"✗ Error inesperado: {e}")
            failed = True
            break

    if failed:
        log_line(log_file, "\n=== PIPELINE FALLÓ — no se marcan fechas como done. Se reintentará en próximo login. ===")
        save_state(state)
        # Notif de fallo
        try:
            from notif_mail import enviar_resumen
            log_tail = log_file.read_text(encoding="utf-8")[-3000:]
            html = f"""
<h2 style="color:#c0392b">❌ Seguimiento ML — FALLÓ</h2>
<p><b>Fecha:</b> {today}</p>
<p><b>Fechas pendientes (no cubiertas):</b> {[d.isoformat() for d in pending]}</p>
<p>Se reintentará en el próximo login. Revisar log adjunto.</p>
<h3>Últimas líneas del log</h3>
<pre style="background:#f4f4f4;padding:10px;border-radius:4px;font-size:11px">{log_tail}</pre>
"""
            enviar_resumen(asunto=f"❌ Seguimiento {today} — FALLO", html_body=html,
                          txt_body=log_tail, attachments=[log_file])
        except Exception as e:
            log_line(log_file, f"(notif mail también falló: {e})")
        return 1

    # Marcar fechas como completadas
    runs_done.update(d.isoformat() for d in pending)
    state["runs_done"] = sorted(runs_done)
    state["last_run_success"] = today.isoformat()
    save_state(state)

    proximas = [d.isoformat() for d in TARGET_DATES if d.isoformat() not in runs_done]
    log_line(log_file, f"\n=== ✓ SEGUIMIENTO COMPLETADO ===")
    log_line(log_file, f"Fechas cubiertas: {sorted(runs_done)}")
    log_line(log_file, f"Próximas fechas pendientes: {proximas}")
    log_line(log_file, f"\nArchivos generados nuevos: revisar seguimiento_diff_{today}.xlsx")

    # Notificación email con resumen
    try:
        from notif_mail import enviar_resumen
        diff_xlsx = ROOT / f"seguimiento_diff_{today}.xlsx"
        # Leer resumen del log para incluirlo
        log_full = log_file.read_text(encoding="utf-8") if log_file.exists() else ""
        # Intentar leer la tabla agregada del Excel para HTML
        resumen_html = ""
        try:
            import pandas as pd
            if diff_xlsx.exists():
                df_resumen = pd.read_excel(diff_xlsx, sheet_name="Resumen por cohorte")
                resumen_html = df_resumen.to_html(index=False, border=1, classes="kpi",
                                                  float_format=lambda v: f"{v:,.1f}" if isinstance(v, float) else str(v))
        except Exception as e:
            resumen_html = f"<i>(no se pudo leer Excel: {e})</i>"

        proximas_html = ", ".join(proximas) if proximas else "ninguna (todas cubiertas)"

        html = f"""
<h2 style="color:#16a34a">✓ Seguimiento ML — Completado</h2>
<p><b>Fecha de corrida:</b> {today}</p>
<p><b>Fechas cubiertas hasta ahora:</b> {", ".join(sorted(runs_done))}</p>
<p><b>Próximas fechas pendientes:</b> {proximas_html}</p>

<h3>Resumen pre vs post por cohorte</h3>
{resumen_html}

<h3>Archivos generados</h3>
<ul>
  <li><code>seguimiento_diff_{today}.xlsx</code> — adjunto si está disponible</li>
  <li><code>data/auditoria/snapshot_c1/c2/c3.json</code> — snapshots actualizados</li>
  <li><code>data/auditoria/analisis.pkl</code> — dataframe consolidado</li>
</ul>

<p style="color:#666;font-size:12px;border-top:1px solid #ddd;padding-top:10px;margin-top:20px">
Enviado por seguimiento_auto.py — Auditoría ML automática.
Tarea Windows: VicttorinoSeguimientoML.
</p>
"""
        attachments = []
        if diff_xlsx.exists():
            attachments.append(diff_xlsx)
        attachments.append(log_file)

        sent = enviar_resumen(
            asunto=f"✓ Seguimiento {today} OK ({len(pending)} fecha{'s' if len(pending)>1 else ''} cubierta{'s' if len(pending)>1 else ''})",
            html_body=html,
            txt_body=f"Seguimiento completado {today}. Cubiertas: {sorted(runs_done)}. Próximas: {proximas}. Ver Excel adjunto.",
            attachments=attachments,
        )
        log_line(log_file, f"\nNotif mail: {'✓ enviado' if sent else '(no enviado — falta config mail_config.json o credenciales inválidas)'}")
    except Exception as e:
        log_line(log_file, f"\n(notif mail falló silenciosamente: {e})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
