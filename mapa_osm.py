import folium
import os
from config import SAIDA_DIR

def gerar_html_popup(ponto):
    """Gera um HTML estruturado para o balão do mapa, com os dados da planilha."""
    html = f"<div style='font-family: Arial, sans-serif; min-width: 200px; max-width: 300px;'>"
    html += f"<h4 style='margin-top: 0; color: #2c3e50;'>{ponto.get('nome', '')}</h4>"
    
    descricao = ponto.get('descricao', '')
    if descricao:
        html += f"<p style='color: #34495e; font-size: 14px;'>{descricao}</p>"
        
    detalhes = ponto.get('detalhes', {})
    if detalhes:
        html += "<hr style='border: 0; border-top: 1px solid #bdc3c7;'/>"
        html += "<ul style='list-style-type: none; padding: 0; margin: 0; font-size: 12px;'>"
        for key, value in detalhes.items():
            html += f"<li style='margin-bottom: 4px;'><b>{key.title()}:</b> {value}</li>"
        html += "</ul>"
        
    html += "</div>"
    return html

def criar_mapa(dados, nome_arquivo_base):
    """
    Recebe os dados padronizados e gera um arquivo HTML usando Folium.
    Os marcadores recebem um número sequencial na plotagem.
    """
    if not dados:
        return None

    # Calcular o centro do mapa baseado na média das coordenadas
    media_lat = sum(p['latitude'] for p in dados) / len(dados)
    media_lon = sum(p['longitude'] for p in dados) / len(dados)

    mapa = folium.Map(location=[media_lat, media_lon], zoom_start=12)

    # Estilo customizado do marcador numerado usando HTML/CSS em DivIcon
    for idx, ponto in enumerate(dados, start=1):
        popup_html = gerar_html_popup(ponto)
        iframe = folium.IFrame(popup_html, width=320, height=200)
        popup = folium.Popup(iframe, max_width=320)
        
        # DivIcon pra numerar
        icone_numerado = folium.DivIcon(
            icon_size=(30, 30),
            icon_anchor=(15, 30),
            popup_anchor=(0, -30),
            html=f'''
                <div style="
                    background-color: #e74c3c;
                    color: white;
                    border-radius: 50%;
                    width: 30px;
                    height: 30px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    font-size: 14pt;
                    font-weight: bold;
                    border: 2px solid white;
                    box-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                ">{idx}</div>
            '''
        )

        folium.Marker(
            location=[ponto['latitude'], ponto['longitude']],
            popup=popup,
            icon=icone_numerado,
            tooltip=f"{idx}. {ponto.get('nome', '')}"
        ).add_to(mapa)

    # Garante que o diretório de saída exista
    if not os.path.exists(SAIDA_DIR):
        os.makedirs(SAIDA_DIR)

    caminho_html = os.path.join(SAIDA_DIR, f"{nome_arquivo_base}.html")
    mapa.save(caminho_html)
    return caminho_html
