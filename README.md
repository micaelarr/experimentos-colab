# Experimento de missings: variantes de forward fill (Micaela)

Extiende el **Exp 1 · Imputación** de Agustín ([experimentos-colaborativos](https://github.com/AgustinBerna/experimentos-colaborativos)). Usa su pipeline sin modificarlo: mismas exclusiones (`tmobile_app`, `cmobile_app_trx`), ceros 100% de un mes → NaN, lags/deltas 1 y 2, 30 semillas comunes, hiperparámetros congelados de E0 (280 árboles, N = 4323) y test 201910. No se re-optimiza nada.

## Hipótesis
En Exp 1 el mejor método fue el forward fill por cliente (E4). Probé tres variantes:

| ID | Método | Hipótesis |
|---|---|---|
| E9 | Forward fill + indicadores `isnull_*` + `n_nulos` | El indicador conserva la señal de "faltaba el dato" |
| E10 | Forward fill + mediana de train para lo que queda sin dato (clientes sin historia) | Rellenar esos NaN mejora el orden |
| E12 | Forward fill limitado a 2 meses | Arrastrar valores viejos mete ruido |

## Resultados (media de 30 semillas, test 201910)

**Entrenamiento 201903–201908** (variante actual del equipo)

| Método | AUC | Ganancia | vs E0 | p Holm gan. vs E0 | vs E4 |
|---|---|---|---|---|---|
| **E10** | **0,93745** | **292,5 M** | **+2,4 M** | 0,050 | +1,1 M (16/30), p = 0,51; AUC p < 0,001 |
| E4 | 0,93686 | 291,3 M | +1,3 M | 0,29 | — |
| E9 | 0,93684 | 291,2 M | +1,1 M | 0,29 | −0,2 M (14/30) |
| E12 | 0,93694 | 290,5 M | +0,4 M | 0,62 | −0,8 M (13/30) |
| E0 | 0,93672 | 290,1 M | — | — | — |

**Entrenamiento 201903–201906** (corrida original)

| Método | AUC | Ganancia | vs E0 |
|---|---|---|---|
| **E10** | **0,93557** | **287,0 M** | **+6,6 M** |
| E9 | 0,93510 | 286,1 M | +5,8 M |
| E4 | 0,93486 | 285,8 M | +5,5 M |
| E12 | 0,93514 | 284,2 M | +3,8 M |
| E0 | 0,93525 | 280,4 M | — |

## Conclusiones
1. **E10 (forward fill + mediana) es el mejor en las dos ventanas** y el único que mejora el AUC de forma significativa contra E0 y contra E4.
2. Su ventaja en ganancia sobre E4 (+1,1 M) **no es concluyente** en ninguna ventana.
3. Indicadores de missing (E9) y forward fill acotado (E12) **no aportan**.
4. Con más meses de entrenamiento, E0 sube unos 10 M y **el beneficio de imputar se achica**.

## Limitaciones
Un solo mes de test (las semillas no son meses independientes). Hiperparámetros optimizados sobre E0. El límite de 2 meses (E12) y la mediana (E10) se fijaron a priori, sin barrido.

## Archivos
- `03_imputar_extra.py`: prepara E7–E12 (yo corrí E9, E10, E12). Se copia a la carpeta del pipeline de Agustín.
- `run_extra_marzo_agosto.sh`: corrida 201903–08 (desde `experimentos-colaborativos/exp_01_imputacion`).
- `run_extra.sh` + `fijar_seleccion_e0.py`: corrida original 201903–06 (repo `exp-colaborativos`).
- `resumen.py`: tablas de resumen y test contra E4: `python resumen.py <work_dir>`.
- `resultados_marzo_agosto/` y `resultados_marzo_junio/`: CSV por semilla y del ensamble.

## Cómo reproducir
```bash
git clone https://github.com/AgustinBerna/experimentos-colaborativos
cd experimentos-colaborativos/exp_01_imputacion
cp /ruta/03_imputar_extra.py /ruta/run_extra_marzo_agosto.sh .
bash run_extra_marzo_agosto.sh /ruta/competencia_02_crudo.csv.gz
```
Unas 1,5–2 h en una VM de 12 vCPU. No se incluyen datos.
