import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
pd.set_option('display.max_columns', 20)
pd.set_option('display.max_rows', 200)

dati_referendum = "data/referendum-20200920_riduzione_parlamentari.txt"   # inserire qui il path ai dati, poi è tutto automatizzato

df_originale = pd.read_csv(dati_referendum, sep=';', header=0, encoding = "ISO-8859-1")

# Nuove colonne facilmente ricavabili dalle colonne presenti
df_originale['ELETTORI_FEMMINE'] = df_originale['ELETTORI'] - df_originale['ELETTORI_MASCHI']
df_originale['VOTANTI_FEMMINE'] = df_originale['VOTANTI'] - df_originale['VOTANTI_MASCHI']
df_originale['AFFLUENZA'] = np.round(df_originale['VOTANTI'] / df_originale['ELETTORI'], 2)
df_originale['AFFLUENZA_MASCHI'] = np.round(df_originale['VOTANTI_MASCHI'] / df_originale['ELETTORI_MASCHI'], 2)
df_originale['AFFLUENZA_FEMMINE'] = np.round(df_originale['VOTANTI_FEMMINE'] / df_originale['ELETTORI_FEMMINE'], 2)
df_originale['SCHEDE_NULLE'] = df_originale['VOTANTI'] - (df_originale['NUMVOTISI'] + df_originale['NUMVOTINO'] + df_originale['SCHEDE_BIANCHE'])
df_originale['PERC_SI'] = np.round(df_originale['NUMVOTISI'] / df_originale['VOTANTI'], 2)
df_originale['PERC_NO'] = np.round(df_originale['NUMVOTINO'] / df_originale['VOTANTI'], 2)

# Raggruppiamo le regioni in 3 gruppi: NORD, CENTRO, SUD
regioni_macro = {'NORD' : ["VALLE D'AOSTA", "PIEMONTE", "LIGURIA", "LOMBARDIA", "TRENTINO-ALTO ADIGE", "VENETO", "FRIULI-VENEZIA GIULIA", "EMILIA-ROMAGNA"], 'CENTRO' : ["TOSCANA", "LAZIO", "MARCHE", "UMBRIA"], 'SUD' : ["CAMPANIA", "ABRUZZO", "MOLISE", "CALABRIA", "BASILICATA", "PUGLIA", "SICILIA", "SARDEGNA"]}
regioni_macro_mappa = {}
for k, v in regioni_macro.items():
    for v2 in v:
        regioni_macro_mappa[v2] = k
df_originale['REGIONE_MACRO'] = df_originale['REGIONE'].apply(lambda x : regioni_macro_mappa[x])

#print(df_originale.info())
#print(df_originale.head(3))

# Dati affluenza
affluenza = np.round((df_originale['VOTANTI'].sum() / df_originale['ELETTORI'].sum()) * 100, 2)
print(f"\nAffluenza: {affluenza}%")
if affluenza > 50:
    print(f"Quorum raggiunto!\n")
else:
    print(f"Quorum non raggiunto.\n")
affluenza_uomini = np.round((df_originale['VOTANTI_MASCHI'].sum() / df_originale['ELETTORI_MASCHI'].sum()) * 100, 2)
affluenza_donne = np.round((df_originale['VOTANTI_FEMMINE'].sum() / df_originale['ELETTORI_FEMMINE'].sum()) * 100, 2)
print(f"Affluenza uomini: {affluenza_uomini}%, votanti uomini: {df_originale['VOTANTI_MASCHI'].sum()} su {df_originale['ELETTORI_MASCHI'].sum()} elettori.")
print(f"Affluenza donne: {affluenza_donne}%, votanti donne: {df_originale['VOTANTI_FEMMINE'].sum()} su {df_originale['ELETTORI_FEMMINE'].sum()} elettrici.")

# Affluenza e percentuali di Sì/No visualizzati per: 1) raggrupamento di regioni, 2) regione, 3) provincia 
def affluenza_sino_raggruppati(criterio : str, grafico : bool) -> None:
    """
    Funzione che raggruppa i dati secondo il criterio desiderato, calcola affluenza e percentuali di Sì/No e, se richiesto, crea un grafico a barre per visualizzare più chiaramente i risultati.
    Parametri:
    criterio -> uno tra: 'REGIONE_MACRO', 'REGIONE', 'PROVINCIA'
    grafico -> True se si desidera anche il grafico, False altrimenti
    """

    if criterio not in ['REGIONE_MACRO', 'REGIONE', 'PROVINCIA']:
        raise NameError("Raggruppamento non valido! Scegli tra: 'REGIONE_MACRO', 'REGIONE', 'PROVINCIA'")
    if grafico not in [True, False]:
        raise NameError('Il secondo argomento deve essere True se si desidera anche produrre il grafico, False altrimenti')
    
    df_raggruppato = df_originale.groupby(criterio).agg(SI=('NUMVOTISI', 'sum'), NO=('NUMVOTINO', 'sum'), VOTI=('VOTANTI', 'sum'), ELETTORI=('ELETTORI', 'sum'))
    df_raggruppato['AFFLUENZA'] = np.round(df_raggruppato['VOTI'] / df_raggruppato['ELETTORI'], 2)
    df_raggruppato['PERC_SI'] = np.round(df_raggruppato['SI'] / df_raggruppato['VOTI'], 2)
    df_raggruppato['PERC_NO'] = np.round(df_raggruppato['NO'] / df_raggruppato['VOTI'], 2)
    print(f"\nRiassunto per {criterio} ordinato per percentuale di sì decrescente:\n{df_raggruppato.sort_values('PERC_SI', ascending=False)}")

    if grafico == True:
        fig, ax = plt.subplots(2, 1, sharex=True)
        ax[0].bar(x=df_raggruppato.index, height=df_raggruppato['PERC_SI'], label='PERC_SI', color='lightblue')
        ax[0].bar(x=df_raggruppato.index, height=df_raggruppato['PERC_NO'], bottom=df_raggruppato['PERC_SI'], label='PERC_NO', color='coral')
        for r, v in zip(df_raggruppato.index, df_raggruppato['PERC_SI']):
            ax[0].annotate(v, xy=(r, v/2))
        for r, v, v2 in zip(df_raggruppato.index, df_raggruppato['PERC_NO'], df_raggruppato['PERC_SI']):
            ax[0].annotate(v, xy=(r, v2+(v/2)))
        ax[0].legend()
        ax[0].set_title(f'Riassunto per {criterio}', fontsize=12)
        ax[1].bar(x=df_raggruppato.index, height=df_raggruppato['AFFLUENZA'], color='palegreen')
        for r, v in zip(df_raggruppato.index, df_raggruppato['AFFLUENZA']):
            ax[1].annotate(v, xy=(r, v))
        ax[1].set_ylim(bottom=0.0, top=1.0)
        ax[1].set_ylabel('Affluenza', fontsize=10)
        ax[1].set_xlabel(f'{criterio}', fontsize=10)
        ax[1].set_xticklabels(df_raggruppato.index, rotation=90, fontsize=8)
        plt.subplots_adjust(bottom=0.25)
        plt.show()

affluenza_sino_raggruppati("REGIONE_MACRO", True)
affluenza_sino_raggruppati("REGIONE", True)
affluenza_sino_raggruppati("PROVINCIA", False)