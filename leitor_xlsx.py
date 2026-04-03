import pandas as pd
import os
import math
from config import MAPA_COLUNAS, ENTRADA_DIR

def encontrar_coluna(df, nomes_possiveis):
    """Procura no DataFrame uma coluna que bata com os nomes possíveis (case insensitive)."""
    colunas_df = [str(c).strip().lower() for c in df.columns]
    for nome in nomes_possiveis:
        if nome in colunas_df:
            # Retorna o nome original da coluna no DataFrame
            idx = colunas_df.index(nome)
            return df.columns[idx]
    return None

def processar_planilha(caminho_arquivo):
    """
    Lê o arquivo Excel, encontra as colunas essenciais e agrupa o restante num dicionário.
    """
    try:
        df = pd.read_excel(caminho_arquivo)
    except Exception as e:
        print(f"Erro ao ler {caminho_arquivo}: {e}")
        return None

    if df.empty:
        return None

    # Encontrar as colunas essenciais
    col_lat = encontrar_coluna(df, MAPA_COLUNAS['latitude'])
    col_lon = encontrar_coluna(df, MAPA_COLUNAS['longitude'])
    col_nome = encontrar_coluna(df, MAPA_COLUNAS['nome'])
    col_desc = encontrar_coluna(df, MAPA_COLUNAS['descricao'])

    if not col_lat or not col_lon:
        print(f"[{os.path.basename(caminho_arquivo)}] Colunas de latitude e longitude não encontradas.")
        return None

    # Criar lista de resultados
    dados_padronizados = []
    
    # Rastrear quais colunas não são essenciais, para adicioná-las aos detalhes
    colunas_essenciais = [col_lat, col_lon, col_nome, col_desc]
    colunas_extras = [col for col in df.columns if col not in colunas_essenciais]

    for index, row in df.iterrows():
        lat = row[col_lat]
        lon = row[col_lon]

        # Ignorar linhas sem coordenadas válidas
        if pd.isna(lat) or pd.isna(lon):
            continue
            
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            continue

        nome = str(row[col_nome]) if col_nome and not pd.isna(row[col_nome]) else f"Ponto {index+1}"
        descricao = str(row[col_desc]) if col_desc and not pd.isna(row[col_desc]) else ""

        # Montar os dados extras (que o usuário confirmou que quer exibir)
        detalhes = {}
        for col in colunas_extras:
            val = row[col]
            if not pd.isna(val):
                detalhes[str(col)] = val

        dados_padronizados.append({
            'latitude': lat,
            'longitude': lon,
            'nome': nome,
            'descricao': descricao,
            'detalhes': detalhes
        })

    return dados_padronizados

def listar_arquivos_entrada():
    """Retorna uma lista contendo os caminhos completos de todos os .xlsx na pasta de entrada."""
    if not os.path.exists(ENTRADA_DIR):
        os.makedirs(ENTRADA_DIR)
        
    arquivos = []
    for f in os.listdir(ENTRADA_DIR):
        if f.endswith('.xlsx') and not f.startswith('~'):
            arquivos.append(os.path.join(ENTRADA_DIR, f))
    return arquivos
