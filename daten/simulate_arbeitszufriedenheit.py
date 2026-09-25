"""Erzeugt fiktive Daten zur Arbeitszufriedenheit (JD-R) fuer die Probepruefung.

Konstruktion: Die Praediktoren werden realistisch erzeugt (Mittelwertskalen mit
Item-Granularitaet, Ueberstunden ganzzahlig). Der Fehlerterm wird gegen die
Praediktoren orthogonalisiert und auf eine Zielstreuung skaliert, damit die
OLS-Schaetzer exakt den Zielkoeffizienten entsprechen.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(20260924)
n = 420

B0, B1, B2, B3 = 3.02, 0.34, 0.08, -0.06
S_E = 0.92

# --- Praediktoren -------------------------------------------------------
# latente, korrelierte Groessen
r12, r13, r23 = 0.40, -0.30, -0.22
C = np.array([[1, r12, r13], [r12, 1, r23], [r13, r23, 1]])
L = np.linalg.cholesky(C)
z = (rng.standard_normal((n, 3)) @ L.T)

# Handlungsspielraum: Mittelwertskala aus 5 Items (Granularitaet 0.2), 1-7
x1 = np.clip(np.round((4.55 + 1.05 * z[:, 0]) * 5) / 5, 1, 7)
# Unterstuetzung: Mittelwertskala aus 4 Items (Granularitaet 0.25), 1-7
x2 = np.clip(np.round((4.80 + 0.95 * z[:, 1]) * 4) / 4, 1, 7)
# Ueberstunden pro Woche: ganzzahlig, 0-20
x3 = np.clip(np.round(5.2 + 3.7 * z[:, 2]), 0, 20)

X = np.column_stack([np.ones(n), x1, x2, x3])

# --- Fehlerterm: exakt orthogonal zu X, Zielstreuung S_E ----------------
e = rng.standard_normal(n)
e = e - X @ np.linalg.lstsq(X, e, rcond=None)[0]
e = e / e.std(ddof=0) * S_E

y = B0 + B1 * x1 + B2 * x2 + B3 * x3 + e
# Zufriedenheit: Mittelwertskala aus 6 Items, 1-7
y = np.clip(np.round(y * 6) / 6, 1, 7)

df = pd.DataFrame({
    "id": np.arange(1, n + 1),
    "handlungsspielraum": np.round(x1, 2),
    "unterstuetzung": np.round(x2, 2),
    "ueberstunden": x3.astype(int),
    "zufriedenheit": np.round(y, 2),
})


# --- Auswertung ----------------------------------------------------------
def ols(Xm, yv):
    b, *_ = np.linalg.lstsq(Xm, yv, rcond=None)
    res = yv - Xm @ b
    nn, kk = Xm.shape
    s2 = res @ res / (nn - kk)
    se = np.sqrt(np.diag(s2 * np.linalg.inv(Xm.T @ Xm)))
    sst = ((yv - yv.mean()) ** 2).sum()
    r2 = 1 - (res @ res) / sst
    adj = 1 - (1 - r2) * (nn - 1) / (nn - kk)
    f = (r2 / (kk - 1)) / ((1 - r2) / (nn - kk))
    dw = np.sum(np.diff(res) ** 2) / (res @ res)
    return b, se, r2, adj, f, res, dw


yv = df.zufriedenheit.to_numpy()
Xs = np.column_stack([np.ones(n), df.handlungsspielraum])
Xm = np.column_stack([np.ones(n), df.handlungsspielraum, df.unterstuetzung, df.ueberstunden])

from scipy import stats

print("=== Ausgabe A: einfache Regression ===")
b, se, r2, adj, f, res, dw = ols(Xs, yv)
for nm, bb, ss in zip(["(Achsenabschnitt)", "handlungsspielraum"], b, se):
    t = bb / ss
    p = 2 * stats.t.sf(abs(t), n - 2)
    print(f"{nm:20s} b={bb:7.3f} SE={ss:6.3f} t={t:7.2f} p={p:.4g}")
print(f"R={np.sqrt(r2):.3f}  R2={r2:.3f}")
print(f"Vorhersage bei x1=5: {b[0] + b[1] * 5:.3f}")

print("\n=== Ausgabe B: multiple Regression ===")
b, se, r2, adj, f, res, dw = ols(Xm, yv)
names = ["(Achsenabschnitt)", "handlungsspielraum", "unterstuetzung", "ueberstunden"]
sds = [None, df.handlungsspielraum.std(ddof=1), df.unterstuetzung.std(ddof=1), df.ueberstunden.std(ddof=1)]
sdy = yv.std(ddof=1)
for i, nm in enumerate(names):
    t = b[i] / se[i]
    p = 2 * stats.t.sf(abs(t), n - 4)
    lo, hi = b[i] - stats.t.ppf(.975, n - 4) * se[i], b[i] + stats.t.ppf(.975, n - 4) * se[i]
    beta = "" if i == 0 else f" beta={b[i] * sds[i] / sdy:6.3f}"
    print(f"{nm:20s} b={b[i]:7.3f} SE={se[i]:6.3f} CI=[{lo:7.3f},{hi:7.3f}] t={t:7.2f} p={p:.4g}{beta}")
print(f"R={np.sqrt(r2):.3f}  R2={r2:.4f}  adjR2={adj:.4f}  F({3},{n-4})={f:.1f}  p={stats.f.sf(f,3,n-4):.3g}")
print(f"Durbin-Watson={dw:.3f}")

# VIF
for j, nm in enumerate(names[1:], start=1):
    others = [c for c in [1, 2, 3] if c != j]
    Xo = np.column_stack([np.ones(n), Xm[:, others]])
    _, _, r2j, *_ = ols(Xo, Xm[:, j])
    print(f"VIF {nm:20s} {1 / (1 - r2j):.3f}   Toleranz {1 - r2j:.3f}")

print("\nDeskriptiv:")
print(df.drop(columns='id').describe().round(2).to_string())
print("\nKorrelationen:")
print(df.drop(columns='id').corr().round(3).to_string())

pred = b[0] + b[1] * 5 + b[2] * 4 + b[3] * 6
print(f"\nVorhersage (HS=5, US=4, UeSt=6): {pred:.4f}")

df.to_csv("/tmp/claude-0/-home-claude/a8381bc4-6971-53e6-883b-6f4285c7938b/scratchpad/arbeitszufriedenheit.csv",
          index=False, sep=";", decimal=".")
print("\nCSV geschrieben, n =", len(df))
