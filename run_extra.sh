#!/usr/bin/env bash
# Corre los métodos extra (E7-E12) con la misma config del repo de Agustín, SIN acceder a su bucket.
# Usa el dataset del curso + el seleccion.json de E0 (hiperparámetros, iteración y N de Optuna).
# Ejecutar desde la raíz del repo exp-colaborativos, con 03_imputar_extra.py y fijar_seleccion_e0.py copiados ahí.
#
# Uso: bash run_extra.sh /ruta/competencia_02_crudo.csv.gz /ruta/seleccion.json [work] ["E7 E8 ..."]
set -euo pipefail

DATA="${1:?ruta al CSV/CSV.GZ del curso}"
SEL="${2:?ruta a seleccion.json de E0 (pedírselo a Agustín)}"
WORK="${3:-$HOME/work_missings}"
METHODS="${4:-E9 E10 E12}"
PY=".venv/bin/python"
NJOBS="${NJOBS:-12}"

# 1) Pasos comunes del baseline (idénticos a los de Agustín)
$PY 01_auditar.py     --work "$WORK" --data "$DATA"
$PY 02_particionar.py --work "$WORK"
$PY 03_imputar_baseline.py --work "$WORK"                 # E0: NaN nativos + lags/deltas
$PY 03_imputar_temporal.py --work "$WORK"                 # E4: forward fill (el ganador de Agustín, referencia)

# 2) Congelar hiperparámetros / iteración / N de E0 (no se re-optimiza)
$PY fijar_seleccion_e0.py --work "$WORK" --seleccion "$SEL"

# 3) Métodos propios
for m in $METHODS; do
  $PY 03_imputar_extra.py --work "$WORK" --method "$m"
done

# 4) Entrenar E0 y los nuevos con las 30 semillas, test 201910, Wilcoxon+Holm vs E0
$PY 04_modelar_evaluar.py --work "$WORK" --methods E0 E4 $METHODS --n_jobs "$NJOBS"
echo "Listo: $WORK/resultados/"
