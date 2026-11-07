"""Eğitilmiş scikit-learn karar ağacını ESP32'de çalışacak C koduna (if/else) çevirir.

Karar ağacı seçilmesinin nedeni: ESP32'nin belleği küçüktür; karar ağacı birkaç KB
koda dönüşür, kütüphane gerektirmez ve kararın nedeni kolayca açıklanabilir.
"""
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor


def _dugum(agac, i: int, girinti: int, yaprak) -> str:
    t = agac.tree_
    bosluk = "    " * girinti
    if t.children_left[i] == -1:  # yaprak düğüm
        return f"{bosluk}return {yaprak(t.value[i])};\n"
    return (f"{bosluk}if (x[{t.feature[i]}] <= {t.threshold[i]:.6f}f) {{\n"
            + _dugum(agac, t.children_left[i], girinti + 1, yaprak)
            + f"{bosluk}}} else {{\n"
            + _dugum(agac, t.children_right[i], girinti + 1, yaprak)
            + f"{bosluk}}}\n")


def header_uret(siniflandirici: DecisionTreeClassifier, regresor: DecisionTreeRegressor,
                ozellikler: list[str]) -> str:
    siniflar = siniflandirici.classes_
    sinif_yapragi = lambda v: str(int(siniflar[v[0].argmax()]))
    regresyon_yapragi = lambda v: f"{float(v[0][0]):.1f}f"

    aciklama = "\n".join(f"//   x[{i}] = {ad}" for i, ad in enumerate(ozellikler))
    return (
        "// BU DOSYA OTOMATİK ÜRETİLDİ (ml/src/egit.py). ELLE DEĞİŞTİRMEYİN.\n"
        "#pragma once\n\n"
        f"#define MODEL_OZELLIK_SAYISI {len(ozellikler)}\n"
        "#define MODEL_EGITILMIS 1\n\n"
        f"// Girdi sırası:\n{aciklama}\n\n"
        "// 1 = sulama gerekli, 0 = gerekli değil\n"
        "static inline int model_sulama_gerekli(const float *x) {\n"
        + _dugum(siniflandirici, 0, 1, sinif_yapragi) + "}\n\n"
        "// Verilmesi gereken su miktarı (ml)\n"
        "static inline float model_su_ml(const float *x) {\n"
        + _dugum(regresor, 0, 1, regresyon_yapragi) + "}\n"
    )
