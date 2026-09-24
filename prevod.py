# Hodinovy prevod dostupnosti pro Upgates (pocty kusu se neposilaji, jinak by Upgates ukazal "Skladem"). Adresa zdroje je ulozena jako tajna hodnota FEED_URL.
import csv, io, os, urllib.request
SIZES = ["S", "M", "L", "XL", "XXL"]
# Obleceni ma u velkoobchodu bud pismena, nebo cisla. Na webu je vzdy S az XXL.
def jen(kod, mid): return [(kod, None, s, mid) for s in SIZES]
MAPA = (jen("228599NK","228599") + jen("228629","228629") + jen("EK228594","228594") + jen("NKM228593","228593")
      + jen("230111","230111") + jen("SK228598","228598") + jen("228577PG","228577") + jen("EM228581","228581")
      + jen("PJ228566","228566") + jen("SPN228567","228567") + jen("ZL228595","228595") + jen("ZC228619","228619")
      + jen("228625","228625") + jen("228621","228621")
      + jen("179255","179255") + jen("179256","179256")
      + [("228620","IVORY",s,"228620") for s in SIZES] + [("228620","CERVENA",s,"204923") for s in SIZES]
      + [("228620","MODRA",s,"204924") for s in SIZES])
NORM = {"2XL": "XXL", "36": "S", "38": "M", "40": "L", "42": "XL", "44": "XXL"}
def rozbal(txt):
    d = {}
    for part in (txt or "").split(","):
        if ":" in part:
            k, v = part.rsplit(":", 1); k = k.strip().upper(); d[NORM.get(k, k)] = v.strip()
    return d
# kody variant, ktere uz jsou v Upgates: velikost S..XXL = 1..5, u Lili barvy od 49
LILI_START = {"IVORY": 49, "CERVENA": 54, "MODRA": 59}
def kod_varianty(kod, barva, vel):
    i = SIZES.index(vel)
    return f"{kod}-{LILI_START[barva] + i}" if barva else f"{kod}-{i + 1}"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
def nacti():
    csv.field_size_limit(10**9)
    if os.environ.get("FEED_FILE") and os.path.exists(os.environ["FEED_FILE"]):
        raw = open(os.environ["FEED_FILE"], encoding="utf-8", errors="replace").read()
    else:
        req = urllib.request.Request(os.environ["FEED_URL"], headers={"User-Agent": UA, "Accept": "text/csv,*/*"})
        raw = urllib.request.urlopen(req, timeout=180).read().decode("utf-8", "replace")
    feed = {r["id"]: r for r in csv.DictReader(io.StringIO(raw), delimiter=";")}
    if len(feed) < 100: raise SystemExit("Zdroj je podezrele maly, soubor neprepisuji.")
    return feed
if __name__ == "__main__":
    feed = nacti()
    with open("sklad.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["[PRODUCT_CODE]", "[VARIANT_YN]", "[VARIANT_CODE]", "[AVAILABILITY]", "[CAN_ADD_TO_BASKET_YN]"])
        for kod, barva, vel, mid in MAPA:
            r = feed.get(mid)
            ks = rozbal(r["sizes_stock"]).get(vel, "0") if r else "0"
            skladem = ks.isdigit() and int(ks) > 0
            w.writerow([kod, 1, kod_varianty(kod, barva, vel),
                        "Dodání do 10 dnů" if skladem else "Není skladem", 1 if skladem else 0])
    print("hotovo", len(MAPA), "variant")
