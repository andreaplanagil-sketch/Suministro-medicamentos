import json, time, requests
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://cima.aemps.es/cima/rest/psuministro"
OUT = Path("data.json")

def ms_to_iso(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).date().isoformat() if ms else None

def fetch_all():
    resultados, pagina = [], 1
    while True:
        r = requests.get(BASE, params={"pagina": pagina}, timeout=30)
        r.raise_for_status()
        d = r.json()
        resultados += d["resultados"]
        if not d["resultados"] or len(resultados) >= d["totalFilas"]:
            break
        pagina += 1
        time.sleep(0.5)
    return resultados

def main():
    nuevos = fetch_all()
    for x in nuevos:
        x["fini"] = ms_to_iso(x.get("fini"))
        x["ffin"] = ms_to_iso(x.get("ffin"))

    previos = set()
    if OUT.exists():
        previos = {x["cn"] for x in json.loads(OUT.read_text())["resultados"]}
    actuales = {x["cn"] for x in nuevos}

    OUT.write_text(json.dumps({
        "actualizado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total": len(nuevos),
        "nuevos_cn": sorted(actuales - previos),
        "resueltos_cn": sorted(previos - actuales),
        "resultados": nuevos,
    }, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
