"""
Cliente para el backend uniCloud (aliyun) de la app alila (alila.sspro-vip.com / alila.apk).
Replica el protocolo firmado del gateway api.bspapp.com extraido del bundle JS de la app.
Solo lectura: auth anonimo + clientDB query.
"""
import requests, json, hashlib, hmac, time, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)

SPACE = "mp-7f614c1e-c60e-48fb-8322-9f64d828d541"
SECRET = "26qGrVgydiZJpr4OYgdhSQ=="
URL = "https://api.bspapp.com/client"
H = {"Content-Type": "application/json", "user-agent": "Mozilla/5.0"}

_token = None

def sign(body):
    # sort keys, k=v&... saltando valores falsy, luego HMAC-MD5 hex
    s = ""
    for k in sorted(body.keys()):
        v = body[k]
        if v:
            s += "&" + k + "=" + str(v)
    s = s[1:]
    return hmac.new(SECRET.encode(), s.encode(), hashlib.md5).hexdigest()

def call(method, params, with_token=True):
    # ponytail: api.bspapp.com es lenta/intermitente; reintenta con backoff.
    # Recalcula timestamp+firma en cada intento (la API valida la firma del body).
    last = None
    for intento in range(4):
        body = {"method": method, "params": params, "spaceId": SPACE, "timestamp": int(time.time() * 1000)}
        if with_token and _token:
            body["token"] = _token
        headers = dict(H)
        if with_token and _token:
            headers["x-basement-token"] = _token
        headers["x-serverless-sign"] = sign(body)
        try:
            r = requests.post(URL, headers=headers, data=json.dumps(body, ensure_ascii=False).encode("utf-8"), timeout=60)
            return r.json()
        except requests.exceptions.RequestException as e:
            last = e
            time.sleep(2 * (intento + 1))
    raise last

def auth():
    global _token
    res = call("serverless.auth.user.anonymousAuthorize", "{}", with_token=False)
    tok = (res.get("data") or res).get("accessToken") if isinstance(res, dict) else None
    # estructura puede venir como {success, data:{accessToken}} o {result:{accessToken}}
    if not tok:
        for path in [("data", "accessToken"), ("result", "accessToken")]:
            d = res
            for p in path:
                d = d.get(p) if isinstance(d, dict) else None
            if d:
                tok = d; break
    _token = tok
    return res

def client_db(stages):
    """stages: lista de {'$method':..,'$param':[..]} -> ejecuta query clientDB."""
    command = {"$db": stages}
    fn_args = {"command": command}
    params = json.dumps({"functionTarget": "DCloud-clientDB", "functionArgs": fn_args}, ensure_ascii=False)
    return call("serverless.function.runtime.invoke", params)

def coll_get(name, where=None, skip=0, limit=100, field=None, orderby=None):
    st = [{"$method": "collection", "$param": [name]}]
    if where is not None:
        st.append({"$method": "where", "$param": [where]})
    if field:
        st.append({"$method": "field", "$param": [field]})
    if orderby:
        st.append({"$method": "orderBy", "$param": orderby})
    st.append({"$method": "skip", "$param": [skip]})
    st.append({"$method": "limit", "$param": [limit]})
    st.append({"$method": "get", "$param": []})
    return client_db(st)

if __name__ == "__main__":
    auth()
    print("token:", _token)
    print("\n=== hjxq (productos en venta) primera pagina ===")
    res = coll_get("hjxq", where={"zt": "上线销售"}, limit=3)
    print(json.dumps(res, ensure_ascii=False)[:1500])
    print("\n=== sin filtro (cualquier producto) ===")
    res2 = coll_get("hjxq", limit=2)
    print(json.dumps(res2, ensure_ascii=False)[:1500])
