"""Erweitert den Arbeitszufriedenheits-Datensatz um Variablen fuer Sitzung 2.

Die bestehenden Spalten bleiben unveraendert, damit alle Ergebnisse der
Probepruefung zu Teil 1 weiterhin exakt stimmen. Die neuen Variablen werden
aus den Residuen des bestehenden Modells konstruiert, damit sie echte
partielle Effekte haben.
"""
import numpy as np
import pandas as pd
from scipy import stats

rng = np.random.default_rng(4711)
df = pd.read_csv("arbeitszufriedenheit.csv")
n = len(df)
y = df.zufriedenheit.to_numpy()
x1 = df.handlungsspielraum.to_numpy()
x2 = df.unterstuetzung.to_numpy()
x3 = df.ueberstunden.to_numpy()


def ols(Xm, yv):
    b, *_ = np.linalg.lstsq(Xm, yv, rcond=None)
    r = yv - Xm @ b
    k = Xm.shape[1]
    s2 = r @ r / (len(yv) - k)
    XtXi = np.linalg.inv(Xm.T @ Xm)
    se = np.sqrt(np.diag(s2 * XtXi))
    r2 = 1 - (r @ r) / ((yv - yv.mean()) ** 2).sum()
    return b, se, r2, r, XtXi, s2


Xfull = np.column_stack([np.ones(n), x1, x2, x3])
_, _, _, resid, _, _ = ols(Xfull, y)

# --- 1) homeoffice: Dummy, korreliert mit den Residuen ------------------
lin = 0.48 * (resid / resid.std()) + rng.normal(0, 1.0, n) - 0.08
homeoffice = (lin > 0).astype(int)

# --- 2) abteilung: vier Kategorien mit unterschiedlichen Niveaus --------
groesse = {"Produktion": 150, "Kundendienst": 120, "Verwaltung": 90, "Vertrieb": 60}
shift = {"Produktion": -0.30, "Kundendienst": 0.00, "Verwaltung": 0.45, "Vertrieb": 0.18}
score = {k: resid * (1 if True else 1) for k in groesse}
# Zuweisung: fuer jede Person einen Score je Abteilung, hoechster gewinnt,
# mit Quoten ueber eine einfache Greedy-Zuteilung nach Rang
noise = rng.normal(0, 0.9, n)
cand = sorted(groesse, key=lambda k: -shift[k])
abteilung = np.array([""] * n, dtype=object)
frei = dict(groesse)
rank_basis = resid + noise
order = np.argsort(-rank_basis)  # hohe Residuen zuerst
# Wahrscheinlichkeitsgewichte: Personen mit hohem Residuum eher in Abteilungen
# mit positivem shift
for idx in order:
    w = np.array([np.exp(3.2 * shift[k] * (1 if rank_basis[idx] > 0 else -1)) * frei[k]
                  for k in cand], dtype=float)
    w = np.where(np.array([frei[k] for k in cand]) > 0, w, 0)
    w = w / w.sum()
    pick = cand[rng.choice(len(cand), p=w)]
    abteilung[idx] = pick
    frei[pick] -= 1

# --- 3) zustimmungstendenz: Suppressor ----------------------------------
z = 0.95 * (x1 - x1.mean()) + rng.normal(0, 0.80, n)
yc = y - y.mean()
z = z - (np.dot(z, yc) / np.dot(yc, yc)) * yc          # Korrelation mit y auf 0
z = 4.3 + z / z.std() * 0.85                            # Skala 1-7
zustimmung = np.clip(np.round(z * 4) / 4, 1, 7)         # Mittelwertskala aus 4 Items

df["homeoffice"] = homeoffice
df["abteilung"] = abteilung
df["zustimmungstendenz"] = np.round(zustimmung, 2)

# =======================================================================
#  Auswertungen
# =======================================================================
def sf3(v):
    import math
    if v == 0:
        return "0.00"
    d = 3 - int(math.floor(math.log10(abs(v)))) - 1
    return f"{round(v, d):.{max(d,0)}f}"


def report(label, cols, data=None, catref=None):
    d = data if data is not None else df
    yy = d.zufriedenheit.to_numpy()
    mats, names = [np.ones(len(d))], ["(Interzept)"]
    for c in cols:
        if not pd.api.types.is_numeric_dtype(d[c]):
            cats = [k for k in sorted(d[c].unique()) if k != catref]
            for k in cats:
                mats.append((d[c] == k).astype(float).to_numpy())
                names.append(f"{k} – {catref}")
        else:
            mats.append(d[c].to_numpy(float))
            names.append(c)
    Xm = np.column_stack(mats)
    b, se, r2, r, _, _ = ols(Xm, yy)
    k = Xm.shape[1]
    nn = len(d)
    adj = 1 - (1 - r2) * (nn - 1) / (nn - k)
    F = (r2 / (k - 1)) / ((1 - r2) / (nn - k))
    tc = stats.t.ppf(.975, nn - k)
    print(f"\n### {label}   R={sf3(np.sqrt(r2))} R2={sf3(r2)} adj={sf3(adj)} "
          f"F({k-1},{nn-k})={sf3(F)} p={stats.f.sf(F,k-1,nn-k):.3g}")
    sdy = yy.std(ddof=1)
    for i, nm in enumerate(names):
        t = b[i] / se[i]
        p = 2 * stats.t.sf(abs(t), nn - k)
        beta = ""
        if i > 0 and Xm[:, i].std() > 0:
            beta = f" beta={sf3(b[i]*Xm[:,i].std(ddof=1)/sdy)}"
        print(f"   {nm:26s} b={sf3(b[i]):>9} SE={sf3(se[i]):>8} "
              f"CI=[{sf3(b[i]-tc*se[i]):>9},{sf3(b[i]+tc*se[i]):>9}] "
              f"t={sf3(t):>7} p={p:.3g}{beta}")
    return r2, k, nn


print("Haeufigkeiten abteilung:\n", df.abteilung.value_counts().to_string())
print("\nhomeoffice:", df.homeoffice.value_counts().to_dict())
print("Mittelwerte zufriedenheit nach homeoffice:\n",
      df.groupby("homeoffice").zufriedenheit.agg(["mean", "std", "count"]).round(3).to_string())
print("\nMittelwerte zufriedenheit nach abteilung:\n",
      df.groupby("abteilung").zufriedenheit.agg(["mean", "std", "count"]).round(3).to_string())
print("\nKorrelationen:\n",
      df[["zufriedenheit", "handlungsspielraum", "unterstuetzung", "ueberstunden",
          "homeoffice", "zustimmungstendenz"]].corr().round(3).to_string())

report("A) nur homeoffice", ["homeoffice"])
report("B) voll + homeoffice", ["handlungsspielraum", "unterstuetzung", "ueberstunden", "homeoffice"])
report("C) nur abteilung (Ref Produktion)", ["abteilung"], catref="Produktion")

# Hierarchisch: Block 1 = 3 Praediktoren, Block 2 = + abteilung
r2_1, k1, _ = report("D) Block 1", ["handlungsspielraum", "unterstuetzung", "ueberstunden"])
r2_2, k2, _ = report("E) Block 2 (+abteilung, Ref Produktion)",
                     ["handlungsspielraum", "unterstuetzung", "ueberstunden", "abteilung"],
                     catref="Produktion")
dR2 = r2_2 - r2_1
df1, df2 = k2 - k1, n - k2
Fch = (dR2 / df1) / ((1 - r2_2) / df2)
print(f"\n>>> Modellvergleich: dR2={sf3(dR2)}  F({df1},{df2})={sf3(Fch)}  "
      f"p={stats.f.sf(Fch, df1, df2):.4g}")

# Suppression
report("F) nur handlungsspielraum", ["handlungsspielraum"])
report("G) handlungsspielraum + zustimmungstendenz", ["handlungsspielraum", "zustimmungstendenz"])
print("r(zustimmung, zufriedenheit) =",
      sf3(np.corrcoef(df.zustimmungstendenz, df.zufriedenheit)[0, 1]),
      "| r(zustimmung, handlungsspielraum) =",
      sf3(np.corrcoef(df.zustimmungstendenz, df.handlungsspielraum)[0, 1]))

# Cook's Distance im einfachen Modell und im vollen Modell
for label, cols in [("y ~ handlungsspielraum", ["handlungsspielraum"]),
                    ("volles Modell", ["handlungsspielraum", "unterstuetzung", "ueberstunden"])]:
    Xm = np.column_stack([np.ones(n)] + [df[c].to_numpy(float) for c in cols])
    b, se, r2, r, XtXi, s2 = ols(Xm, y)
    h = np.einsum("ij,jk,ik->i", Xm, XtXi, Xm)
    k = Xm.shape[1]
    cook = r ** 2 / (k * s2) * h / (1 - h) ** 2
    print(f"Cook's D {label}: max={cook.max():.4f} (Fall {df.id[cook.argmax()]}), "
          f"Anzahl > 1: {(cook>1).sum()}, max Hebelwert={h.max():.4f}")

df.to_csv("arbeitszufriedenheit.csv", index=False)
print("\nGespeichert. Spalten:", list(df.columns))
print(df.head(5).to_string(index=False))
