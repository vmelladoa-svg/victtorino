"""
Re-mide la salud de las publicaciones y compara contra el baseline guardado.
Llama a auditoria_ml.py (snapshot fresco) y produce un Excel con la comparacion.

Uso:
  python volver_a_medir.py
"""
import json
import subprocess
import sys
import io
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).parent
BASELINE = ROOT / "baseline_health_2026-05-18.json"

def calc_health_score(item):
    score = 0
    pictures = item.get("pictures") or []
    if len(pictures) >= 6: score += 25
    elif len(pictures) >= 4: score += 15
    elif len(pictures) >= 2: score += 8
    title_len = len(item.get("title") or "")
    if title_len >= 50: score += 20
    elif title_len >= 40: score += 12
    elif title_len >= 30: score += 6
    if item.get("listing_type_id") == "gold_pro": score += 15
    elif item.get("listing_type_id") == "gold_special": score += 10
    if (item.get("available_quantity") or 0) >= 3: score += 10
    elif (item.get("available_quantity") or 0) >= 1: score += 5
    h = item.get("health")
    if isinstance(h, (int, float)):
        score += int(h * 30)
    return min(score, 100)


def score_seo(title, n_attrs, v30):
    score = 0
    if len(title) >= 60: score += 35
    elif len(title) >= 50: score += 25
    elif len(title) >= 40: score += 15
    if n_attrs >= 10: score += 35
    elif n_attrs >= 5: score += 20
    if v30 >= 50: score += 30
    elif v30 >= 10: score += 15
    elif v30 >= 1: score += 5
    return score


def medir_actual():
    """Calcula metricas actuales por cuenta. Asume snapshots ya existen."""
    SNAP = ROOT / "data" / "auditoria"
    out = {}
    for c in ["c1","c2","c3"]:
        path = SNAP / f"snapshot_{c}.json"
        if not path.exists():
            print(f"FALTA snapshot {path} — corre 'python auditoria_ml.py' primero")
            return None
        snap = json.loads(path.read_text(encoding="utf-8"))
        visits = snap["visitas_30d"]
        actives = [i for i in snap["items"] if i.get("status")=="active"]
        healths = [calc_health_score(i) for i in actives]
        ml_h = [i.get("health") for i in actives if isinstance(i.get("health"),(int,float))]
        criticas = sum(1 for i in actives
                       if score_seo(i.get("title") or "",
                                    len(i.get("attributes") or []),
                                    visits.get(i["id"], 0)) < 20)
        # Ventas: GMV y ordenes 180d
        orders = snap.get("orders") or []
        gmv = sum((o.get("total_amount") or 0) for o in orders)
        # Visitas totales 30d
        total_visits = sum(visits.values())
        out[c] = {
            "activas": len(actives),
            "health_calc_avg": round(sum(healths)/len(healths), 1) if healths else 0,
            "health_ml_avg": round(sum(ml_h)/len(ml_h), 2) if ml_h else 0,
            "items_con_health_ml": len(ml_h),
            "criticas_sub_20": criticas,
            "ordenes_180d": len(orders),
            "gmv_180d": int(gmv),
            "visitas_30d_total": total_visits,
        }
    return out


def main():
    print("=" * 70)
    print(f"Re-medicion de salud — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)

    print("\n[1/2] Tomando snapshot fresco de la API ML (puede tardar 1-2 min)...")
    # Llama al extractor
    result = subprocess.run([sys.executable, str(ROOT / "auditoria_ml.py")],
                            cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        print("ERROR en auditoria_ml.py:")
        print(result.stderr[-500:])
        return
    print("    OK")

    print("\n[2/2] Comparando contra baseline...")
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    actual = medir_actual()
    if not actual: return

    LBL = {"c1":"C1 PREMIUMGRIFERIAS1","c2":"C2 VICTTORINOOFICIAL2","c3":"C3 NOVAGRIFERIAS3"}

    print(f"\nBaseline: {baseline['fecha_baseline']}")
    print(f"Hoy:      {datetime.now().strftime('%Y-%m-%d')}\n")

    print(f"{'Cuenta':<25}  {'Health calc':>15}  {'Health ML':>12}  {'Críticas':>10}")
    print(f"{'':<25}  {'antes → hoy':>15}  {'antes → hoy':>12}  {'antes → hoy':>10}")
    print("-" * 75)
    for c in ["c1","c2","c3"]:
        b = baseline["por_cuenta"][c]
        a = actual[c]
        dh = a["health_calc_avg"] - b["health_calc_avg"]
        dm = a["health_ml_avg"] - b["health_ml_avg"]
        dc = a["criticas_sub_20"] - b["criticas_sub_20"]
        signo_h = "+" if dh >= 0 else ""
        signo_m = "+" if dm >= 0 else ""
        signo_c = "+" if dc >= 0 else ""
        print(f"{LBL[c]:<25}  {b['health_calc_avg']:.1f}→{a['health_calc_avg']:.1f} ({signo_h}{dh:.1f})  "
              f"{b['health_ml_avg']:.2f}→{a['health_ml_avg']:.2f} ({signo_m}{dm:.2f})  "
              f"{b['criticas_sub_20']}→{a['criticas_sub_20']} ({signo_c}{dc})")
    print()

    # Total
    b_tot = baseline["total"]
    tot_act = sum(actual[c]["activas"] for c in actual)
    tot_h = sum(actual[c]["health_calc_avg"] * actual[c]["activas"] for c in actual) / tot_act
    tot_crit = sum(actual[c]["criticas_sub_20"] for c in actual)
    print(f"TOTAL: health calc {b_tot['health_calc_avg']:.1f} → {tot_h:.1f}  |  "
          f"criticas {b_tot['criticas_sub_20']} → {tot_crit}")

    # Ventas y visitas (comparacion 180d / 30d)
    print()
    print(f"{'Cuenta':<25}  {'Órdenes 180d':>15}  {'GMV 180d':>17}  {'Visitas 30d':>13}")
    print("-" * 80)
    tot_ord_b = tot_ord_a = 0
    tot_gmv_b = tot_gmv_a = 0
    tot_vis_a = 0
    for c in ["c1","c2","c3"]:
        a = actual[c]
        ord_b = baseline["total"].get(f"ordenes_180d_{c.upper()}", 0)
        gmv_b = 0  # baseline solo guarda total
        d_ord = a["ordenes_180d"] - ord_b
        s_ord = "+" if d_ord >= 0 else ""
        print(f"{LBL[c]:<25}  {ord_b}→{a['ordenes_180d']} ({s_ord}{d_ord})        "
              f"${a['gmv_180d']:>13,}     {a['visitas_30d_total']:>10}")
        tot_ord_a += a["ordenes_180d"]; tot_ord_b += ord_b
        tot_gmv_a += a["gmv_180d"]
        tot_vis_a += a["visitas_30d_total"]
    print("-" * 80)
    gmv_b = baseline["total"].get("gmv_180d_total_clp", 0)
    print(f"{'TOTAL':<25}  {tot_ord_b}→{tot_ord_a} ({tot_ord_a-tot_ord_b:+d})        "
          f"${gmv_b:>11,}→${tot_gmv_a:,}     {tot_vis_a:>10}")

    # Guardar nueva medicion
    fecha = datetime.now().strftime("%Y-%m-%d")
    snap_out = ROOT / f"medicion_health_{fecha}.json"
    snap_out.write_text(json.dumps({
        "fecha": fecha,
        "por_cuenta": actual,
        "total": {
            "activas": tot_act,
            "health_calc_avg": round(tot_h, 1),
            "criticas_sub_20": tot_crit,
        }
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nGuardado en: {snap_out}")


if __name__ == "__main__":
    main()
