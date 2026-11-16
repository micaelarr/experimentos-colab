"""Resumen de una corrida: python resumen.py ~/work_missings_marzo_agosto"""
import sys
import polars as pl
from scipy.stats import wilcoxon

pl.Config.set_tbl_cols(20)
pl.Config.set_tbl_width_chars(200)
pl.Config.set_tbl_hide_dataframe_shape(True)

r = sys.argv[1].rstrip('/') + '/resultados/'
s = pl.read_csv(r + 'metricas_por_semilla_test.csv')
e = pl.read_csv(r + 'resumen_ensamble_test.csv')


def g(m, c):
    return s.filter(pl.col('method') == m).sort('seed')[c].to_numpy()


e0 = g('E0', 'gain_at_n_fijo').mean()

print('\n=== 1) Media de 30 semillas (test 201910) ===')
print(s.group_by('method').agg(
    pl.col('roc_auc').mean().round(5).alias('auc'),
    pl.col('roc_auc').std().round(5).alias('auc_sd'),
    (pl.col('gain_at_n_fijo').mean() / 1e6).round(2).alias('gan_M'),
    (pl.col('gain_at_n_fijo').std() / 1e6).round(2).alias('gan_sd_M'),
    ((pl.col('gain_at_n_fijo').mean() - e0) / 1e6).round(2).alias('dif_vs_E0_M'),
).sort('gan_M', descending=True))

print('\n=== 2) Ensamble (promedio de 30 semillas) y p Holm vs E0 ===')
cols = [c for c in ['method', 'roc_auc', 'gain_at_n_fijo', 'p_holm_auc_vs_E0', 'p_holm_gain_vs_E0'] if c in e.columns]
print(e.select(cols).with_columns((pl.col('gain_at_n_fijo') / 1e6).round(2)).sort('gain_at_n_fijo', descending=True))

metodos = s['method'].unique().sort().to_list()
otros = [m for m in metodos if m not in ('E0', 'E4')]
if 'E4' in metodos and otros:
    print('\n=== 3) Contra E4 (forward fill de Agustin), Wilcoxon pareado + Holm ===')
    filas = []
    for m in otros:
        d = g(m, 'gain_at_n_fijo') - g('E4', 'gain_at_n_fijo')
        filas.append(dict(
            method=m,
            gana_en=int((d > 0).sum()),
            dif_gan_M=round(d.mean() / 1e6, 2),
            p_gan=wilcoxon(g(m, 'gain_at_n_fijo'), g('E4', 'gain_at_n_fijo'), zero_method='zsplit')[1],
            dif_auc=round((g(m, 'roc_auc') - g('E4', 'roc_auc')).mean(), 5),
            p_auc=wilcoxon(g(m, 'roc_auc'), g('E4', 'roc_auc'), zero_method='zsplit')[1],
        ))
    for k in ('p_gan', 'p_auc'):
        prev = 0
        orden = sorted(filas, key=lambda f: f[k])
        for i, f in enumerate(orden):
            prev = min(1, max(prev, f[k] * (len(orden) - i)))
            f[k + '_holm'] = round(prev, 4)
    print(pl.DataFrame(filas).select(['method', 'gana_en', 'dif_gan_M', 'p_gan_holm', 'dif_auc', 'p_auc_holm']))
    print('   (gana_en = semillas de 30 en que supera a E4 en ganancia)')
