import os

# Diretórios principais
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENTRADA_DIR = os.path.join(BASE_DIR, 'dados_entrada')
SAIDA_DIR = os.path.join(BASE_DIR, 'saida')

# Mapeamento estendido de colunas que podem vir de diversos órgãos
MAPA_COLUNAS = {
    'latitude': ['latitude', 'lat', 'y', 'coord_y', 'lat_y', 'latitude_y', 'lat_dec'],
    'longitude': ['longitude', 'long', 'lon', 'lng', 'x', 'coord_x', 'long_x', 'longitude_x', 'lon_dec'],
    'nome': ['nome', 'name', 'titulo', 'local', 'ponto', 'identificacao', 'estabelecimento', 'descricao_curta'],
    'descricao': ['descricao', 'desc', 'observacao', 'obs', 'detalhes', 'texto', 'informacao']
}
