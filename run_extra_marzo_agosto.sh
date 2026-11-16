#!/usr/bin/env bash
# Mis métodos (E9, E10, E12) con la variante NUEVA de Agustín: entrenamiento final 201903–201908, test 201910.
# Mismos 280 árboles, N=4323 y 30 semillas (seleccion.json ya viene en su carpeta exp_01_imputacion).
# Ejecutar desde experimentos-colaborativos/exp_01_imputacion, con 03_imputar_extra.py copiado ahí.
#
# Uso: bash run_extra_marzo_agosto.sh /ruta/competencia_02_crudo.csv.gz [work] ["E9 E10 E12"]
set -euo pipefail

DATA="${1:?ruta al CSV del curso}"
WORK="${2:-$HOME/work_missings_marzo_agosto}"      # carpeta NUEVA, no mezclar con la corrida anterior
METHODS="${3:-E9 E10 E12}"
PY="${PY:-$HOME/exp-colaborativos/.venv/bin/python}" # mismo entorno de la corrida anterior
NJOBS="${NJOBS:-12}"

grep -q '201908' config.json && grep -q '"best_iteration": 280' seleccion.json \
  || { echo "Correr desde exp_01_imputacion (config marzo–agosto + seleccion.json)"; exit 1; }

$PY 01_auditar.py          --work "$WORK" --data "$DATA"
$PY 02_particionar.py      --work "$WORK"
$PY 03_imputar_baseline.py --work "$WORK"     # E0
$PY 03_imputar_temporal.py --work "$WORK"     # E4 (referencia)
for m in $METHODS; do
  $PY 03_imputar_extra.py --work "$WORK" --method "$m"   # medianas/indicadores se ajustan con marzo–agosto
done
$PY 04_modelar_evaluar.py  --work "$WORK" --methods E0 E4 $METHODS --n_jobs "$NJOBS"
echo "Listo: $WORK/resultados/"
