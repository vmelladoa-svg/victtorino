"""
Módulo de notificación por email.
Lee credenciales SMTP de mail_config.json (NO committeado, ignorado por .gitignore).
Sin config válido: NO falla, solo loguea warning.

Función principal: enviar_resumen(asunto, html_body, txt_body, attachments=[])
"""
import json
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).parent
CONFIG_FILE = ROOT / "mail_config.json"


def _load_config() -> Optional[dict]:
    if not CONFIG_FILE.exists():
        return None
    try:
        cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        # Validación mínima
        required = ("smtp_host", "smtp_port", "smtp_user", "smtp_password", "from_addr", "to_addrs")
        missing = [k for k in required if not cfg.get(k)]
        if missing:
            print(f"[notif_mail] WARN: faltan claves en mail_config.json: {missing}")
            return None
        if "PEGA_AQUI" in cfg.get("smtp_password", ""):
            print(f"[notif_mail] WARN: el password sigue en placeholder, sin enviar mail")
            return None
        return cfg
    except Exception as e:
        print(f"[notif_mail] WARN: error leyendo config: {e}")
        return None


def enviar_resumen(
    asunto: str,
    html_body: str,
    txt_body: str = "",
    attachments: Optional[List[Path]] = None,
) -> bool:
    """
    Envía mail con resumen. Devuelve True si OK, False si falló o sin config.
    No re-lanza excepciones (no rompe el pipeline llamador).
    """
    cfg = _load_config()
    if not cfg:
        return False

    msg = EmailMessage()
    prefix = cfg.get("subject_prefix", "").strip()
    msg["Subject"] = f"{prefix} {asunto}".strip()
    from_name = cfg.get("from_name", "")
    if from_name:
        msg["From"] = f"{from_name} <{cfg['from_addr']}>"
    else:
        msg["From"] = cfg["from_addr"]
    to_addrs = cfg["to_addrs"] if isinstance(cfg["to_addrs"], list) else [cfg["to_addrs"]]
    msg["To"] = ", ".join(to_addrs)

    if txt_body:
        msg.set_content(txt_body)
        msg.add_alternative(html_body, subtype="html")
    else:
        msg.set_content("Resumen en HTML — abrí en cliente compatible.")
        msg.add_alternative(html_body, subtype="html")

    # Attachments
    for att_path in (attachments or []):
        att_path = Path(att_path)
        if not att_path.exists():
            print(f"[notif_mail] WARN: adjunto no existe: {att_path}")
            continue
        data = att_path.read_bytes()
        # Heurística simple de content-type
        suffix = att_path.suffix.lower()
        maintype, subtype = "application", "octet-stream"
        if suffix == ".xlsx":
            maintype, subtype = "application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif suffix == ".json":
            maintype, subtype = "application", "json"
        elif suffix in (".txt", ".log", ".md"):
            maintype, subtype = "text", "plain"
        elif suffix == ".html":
            maintype, subtype = "text", "html"
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=att_path.name)

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(cfg["smtp_host"], int(cfg["smtp_port"]), timeout=30) as srv:
            srv.starttls(context=ctx)
            srv.login(cfg["smtp_user"], cfg["smtp_password"])
            srv.send_message(msg)
        print(f"[notif_mail] ✓ Mail enviado a {to_addrs}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"[notif_mail] ✗ Falló autenticación SMTP: {e}")
        print(f"  -> Verificá que el password sea un APP PASSWORD de Gmail (16 chars), no tu password normal")
        return False
    except Exception as e:
        print(f"[notif_mail] ✗ Error enviando mail: {e}")
        return False


# CLI test
if __name__ == "__main__":
    import sys
    ok = enviar_resumen(
        asunto="Test desde notif_mail.py",
        html_body="""
<h2>Test de notificación</h2>
<p>Si recibís este mail, el setup SMTP está funcionando correctamente.</p>
<p>Próximos eventos: seguimiento automático en 2026-05-30, 2026-06-06 y 2026-06-20.</p>
<hr>
<small>Enviado desde seguimiento_auto.py</small>
""",
        txt_body="Test de notif_mail.py — si recibiste este mail, el setup SMTP está funcionando.",
    )
    sys.exit(0 if ok else 1)
