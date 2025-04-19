import pandas as pd
import numpy as np
import re

def limpar_dados(df):
    # Renomeia as colunas para padronizar
    df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

    # Remove colunas totalmente vazias
    df.dropna(how='all', axis=1, inplace=True)

    # Remove linhas totalmente vazias
    df.dropna(how='all', axis=0, inplace=True)

    # Remove espaços extras em todas as células de texto
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Substitui strings vazias por NaN
    df.replace('', np.nan, inplace=True)

    # Converte colunas de datas
    colunas_data = [col for col in df.columns if 'data' in col]
    for col in colunas_data:
        df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)

    # Corrige nomes de colunas específicas se necessário
    renomear_colunas = {
        'nome_completo': 'nome',
        'email_aluno': 'email',
        'telefone_contato': 'telefone'
    }
    df.rename(columns=renomear_colunas, inplace=True)

    # Remove caracteres não numéricos de colunas como telefone ou CPF
    if 'telefone' in df.columns:
        df['telefone'] = df['telefone'].astype(str).apply(lambda x: re.sub(r'\D', '', x))

    if 'cpf' in df.columns:
        df['cpf'] = df['cpf'].astype(str).apply(lambda x: re.sub(r'\D', '', x))

    # Remove duplicatas
    df.drop_duplicates(inplace=True)

    return df
