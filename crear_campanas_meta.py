# -*- coding: utf-8 -*-
"""
Crear campanas Meta Ads — Victtorino
Cuenta: act_2087839325471724
Campana 1: Ventas Productos Top (OUTCOME_SALES)
Campana 3: Crecimiento Instagram (OUTCOME_ENGAGEMENT)
Campana 2: Remarketing — pendiente (activar con 7+ dias de pixel)
"""
import json, requests, sys, time

TOKEN = "EAAYlThMWakQBRdYv4ifF30c9hUCawmde3hpn375uU6znZCLwR9DZAXxDHf1rsJCTwYs2HlKm1kEYbnQhV4akdzoSV9gdhlWtqp2hFCK45LlwariYMcfUarkS5kp4Quy1V0IfM13pHspJ6gyld9YOFB7ODJTwDGAZA605DIPx2L66BgfZCb7l6xEpBMUMM9nbNnjUP1vSZCOAyZCQ86stB6bWTfmArXLifT2Crgfog8NR3eIXNOZB2287PbXkwgDyG4DsKCE6j23oKprqSrF7mLX8O0YAd0iZBGovMAZDZD"
ACCOUNT  = "act_2087839325471724"
PIXEL_ID = "1361965342502798"
BASE     = "https://graph.facebook.com/v21.0"

# Intereses encontrados via Targeting Search API
INTERESES = {
    "diseno_interiores":  {"id": "6002920953955",  "name": "Diseno de interiores"},
    "remodelaciones":     {"id": "6003234413249",  "name": "Remodelaciones"},
    "home_improvement":   {"id": "6003314631218",  "name": "Home Improvement"},
    "cocina":             {"id": "6002897751962",  "name": "Cocina (hogar)"},
    "ducha":              {"id": "6003714025153",  "name": "Ducha (hogar)"},
    "modern_bathroom":    {"id": "6014625994060",  "name": "Modern Bathroom"},
}

results = {}

def api_post(path, payload):
    payload["access_token"] = TOKEN
    r = requests.post(f"{BASE}/{path}", json=payload)
    return r.json()

def api_get(path, params=None):
    p = params or {}
    p["access_token"] = TOKEN
    r = requests.get(f"{BASE}/{path}", params=p)
    return r.json()

def check(resp, label):
    if "error" in resp:
        e = resp["error"]
        print(f"  ERROR [{label}]: {e.get('message')} | subcode={e.get('error_subcode')} | user_msg={e.get('error_user_msg','')}")
        return False
    return True

# ── Verificar token ──────────────────────────────────────────────────────────
print("Verificando token...")
me = api_get("me")
if "error" in me:
    print(f"TOKEN INVALIDO: {me['error']['message']}")
    sys.exit(1)
print(f"  OK — {me.get('name')} ({me.get('id')})\n")

# ── Buscar Instagram Business Account vinculado ──────────────────────────────
print("Buscando Instagram Business Account...")
ig_resp = api_get(f"{ACCOUNT}", {"fields": "instagram_accounts"})
ig_account_id = None
if ig_resp.get("instagram_accounts", {}).get("data"):
    ig_account_id = ig_resp["instagram_accounts"]["data"][0]["id"]
    print(f"  Instagram Account ID: {ig_account_id}")
else:
    print("  No se encontro Instagram Account vinculado — Campana 3 sin promoted_object")

print()

# ════════════════════════════════════════════════════════════════════════════
# CAMPANA 1: VENTAS PRODUCTOS TOP
# ════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("CREANDO CAMPANA 1 — Ventas Productos Top")
print("=" * 60)

# Reutilizar campana ya creada
c1_id = "120249077890650066"
results["campana1_id"] = c1_id
print(f"  Campana 1 (existente): {c1_id}")
time.sleep(0.5)

# ── Ad Set 1A: Lavaplatos ────────────────────────────────────────────────────
print("\nCreando Ad Set 1A — Lavaplatos...")

as1a = api_post(f"{ACCOUNT}/adsets", {
    "name": "1A - Lavaplatos",
    "campaign_id": c1_id,
    "daily_budget": 2500,
    "billing_event": "IMPRESSIONS",
    "optimization_goal": "OFFSITE_CONVERSIONS",
    "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
    "promoted_object": {
        "pixel_id": PIXEL_ID,
        "custom_event_type": "PURCHASE"
    },
    "targeting": {
        "geo_locations": {"countries": ["CL"]},
        "age_min": 28,
        "age_max": 55,
        "targeting_automation": {"advantage_audience": 0},
        "flexible_spec": [{
            "interests": [
                INTERESES["diseno_interiores"],
                INTERESES["remodelaciones"],
                INTERESES["home_improvement"],
                INTERESES["cocina"]
            ]
        }]
    },
    "publisher_platforms": ["facebook", "instagram"],
    "facebook_positions": ["feed"],
    "instagram_positions": ["stream", "story"],
    "status": "PAUSED"
})

if check(as1a, "Ad Set 1A"):
    as1a_id = as1a["id"]
    results["adset_1a_id"] = as1a_id
    print(f"  Ad Set 1A creado: {as1a_id}")
time.sleep(0.5)

# ── Ad Set 1B: Shower & Receptáculos ────────────────────────────────────────
print("\nCreando Ad Set 1B — Shower & Receptaculos...")

as1b = api_post(f"{ACCOUNT}/adsets", {
    "name": "1B - Shower & Receptaculos",
    "campaign_id": c1_id,
    "daily_budget": 2000,
    "billing_event": "IMPRESSIONS",
    "optimization_goal": "OFFSITE_CONVERSIONS",
    "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
    "promoted_object": {
        "pixel_id": PIXEL_ID,
        "custom_event_type": "PURCHASE"
    },
    "targeting": {
        "geo_locations": {"countries": ["CL"]},
        "age_min": 25,
        "age_max": 55,
        "targeting_automation": {"advantage_audience": 0},
        "flexible_spec": [{
            "interests": [
                INTERESES["diseno_interiores"],
                INTERESES["remodelaciones"],
                INTERESES["ducha"],
                INTERESES["modern_bathroom"]
            ]
        }]
    },
    "publisher_platforms": ["facebook", "instagram"],
    "facebook_positions": ["feed"],
    "instagram_positions": ["stream", "reels"],
    "status": "PAUSED"
})

if check(as1b, "Ad Set 1B"):
    as1b_id = as1b["id"]
    results["adset_1b_id"] = as1b_id
    print(f"  Ad Set 1B creado: {as1b_id}")
time.sleep(0.5)

# ════════════════════════════════════════════════════════════════════════════
# CAMPANA 3: CRECIMIENTO INSTAGRAM
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("CREANDO CAMPANA 3 — Crecimiento Instagram")
print("=" * 60)

c3_payload = {
    "name": "C3 - Crecimiento Instagram",
    "objective": "OUTCOME_ENGAGEMENT",
    "status": "PAUSED",
    "special_ad_categories": [],
    "is_adset_budget_sharing_enabled": False
}

# Reutilizar campana ya creada
c3_id = "120249077890870066"
results["campana3_id"] = c3_id
print(f"  Campana 3 (existente): {c3_id}")

time.sleep(0.5)

if c3_id:
    targeting_ig = {
        "geo_locations": {"countries": ["CL"]},
        "age_min": 25,
        "age_max": 50,
        "flexible_spec": [{
            "interests": [
                INTERESES["diseno_interiores"],
                INTERESES["remodelaciones"],
                INTERESES["cocina"],
                INTERESES["home_improvement"]
            ]
        }]
    }

    # ── Ad Set 3A: Contenido producto ────────────────────────────────────────
    print("\nCreando Ad Set 3A — Contenido de producto...")

    targeting_ig["targeting_automation"] = {"advantage_audience": 0}
    as3a_payload = {
        "name": "3A - Contenido de producto",
        "campaign_id": c3_id,
        "daily_budget": 1000,
        "billing_event": "IMPRESSIONS",
        "optimization_goal": "POST_ENGAGEMENT",
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "targeting": targeting_ig,
        "publisher_platforms": ["instagram"],
        "instagram_positions": ["stream", "story"],
        "status": "PAUSED"
    }
    if ig_account_id:
        as3a_payload["promoted_object"] = {"instagram_profile_id": ig_account_id}

    as3a = api_post(f"{ACCOUNT}/adsets", as3a_payload)
    if check(as3a, "Ad Set 3A"):
        as3a_id = as3a["id"]
        results["adset_3a_id"] = as3a_id
        print(f"  Ad Set 3A creado: {as3a_id}")
    time.sleep(0.5)

    # ── Ad Set 3B: Video instalación ──────────────────────────────────────────
    print("\nCreando Ad Set 3B — Video instalacion...")

    as3b_payload = {
        "name": "3B - Video instalacion",
        "campaign_id": c3_id,
        "daily_budget": 1000,
        "billing_event": "IMPRESSIONS",
        "optimization_goal": "POST_ENGAGEMENT",
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "targeting": targeting_ig,
        "publisher_platforms": ["instagram"],
        "instagram_positions": ["stream", "reels"],
        "status": "PAUSED"
    }
    if ig_account_id:
        as3b_payload["promoted_object"] = {"instagram_profile_id": ig_account_id}

    as3b = api_post(f"{ACCOUNT}/adsets", as3b_payload)
    if check(as3b, "Ad Set 3B"):
        as3b_id = as3b["id"]
        results["adset_3b_id"] = as3b_id
        print(f"  Ad Set 3B creado: {as3b_id}")

# ════════════════════════════════════════════════════════════════════════════
# RESUMEN
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("RESUMEN — IDs CREADOS")
print("=" * 60)
for k, v in results.items():
    print(f"  {k}: {v}")

print("""
NOTAS:
  - Todas las campanas y ad sets estan en estado PAUSED
  - Faltan los ANUNCIOS (creatividades) — agregar en Ads Manager
  - Campana 2 (Remarketing): activar despues de 7+ dias con pixel
  - Ad Set 1C (Advantage+): activar con 50+ conversiones
  - Para activar: Meta Ads Manager -> revisar cada campana -> activar
""")

# Guardar IDs
with open("meta_campanas_ids.json", "w") as f:
    json.dump(results, f, indent=2)
print("IDs guardados en meta_campanas_ids.json")
