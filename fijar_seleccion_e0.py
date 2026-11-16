"""fijar_seleccion_e0.py - Congela en tu work-dir la selección de Optuna de E0 hecha por Agustín.

No re-corre Optuna (no tiene semilla fija: daría otros hiperparámetros y rompería la
comparabilidad). Toma su seleccion.json (best_params, best_iteration, n_selected_valid)
y deja E0/optimization con los marcadores que espera 04_modelar_evaluar.py.
04 entrenará E0 con sus 30 semillas en tu máquina usando esos valores.

Uso: python fijar_seleccion_e0.py --work ./work --seleccion seleccion.json
"""
import argparse, json
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--work", type=Path, required=True)
ap.add_argument("--seleccion", type=Path, required=True)
a = ap.parse_args()

sel = json.loads(a.seleccion.read_text(encoding="utf-8"))
for k in ("best_params", "best_iteration", "n_selected_valid"):
    if k not in sel:
        raise SystemExit(f"Al seleccion.json le falta '{k}'")
sel["source_method"] = "E0"
for p in ("num_leaves", "learning_rate", "min_data_in_leaf", "feature_fraction", "bagging_fraction"):
    if p not in sel["best_params"]:
        raise SystemExit(f"Falta el hiperparámetro {p}")

d = a.work / "E0" / "optimization"
d.mkdir(parents=True, exist_ok=True)
(d / "seleccion.json").write_text(json.dumps(sel, indent=2), encoding="utf-8")
(d / "curva_ganancia_valid_e0.csv").write_text("envios,ganancia,ganancia_suavizada\n", encoding="utf-8")  # marcador
(d / "DONE.json").write_text(json.dumps({"status": "heredado_de_Agustin"}), encoding="utf-8")
print("Selección E0 fijada:", json.dumps(sel["best_params"]), "iter", sel["best_iteration"], "N", sel["n_selected_valid"])
