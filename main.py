import os
import time
from leitor_xlsx import listar_arquivos_entrada, processar_planilha
from mapa_osm import criar_mapa
from config import SAIDA_DIR

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import base64

def html_para_pdf_imagem(caminho_html, nome_base):
    """
    Usa o Selenium para renderizar o HTML gerado e capturar um screenshot e exportar PDF.
    """
    # Prepara o caminho absoluto para o navegador ler (file:///)
    caminho_html_absoluto = f"file:///{os.path.abspath(caminho_html).replace(chr(92), '/')}"
    
    options = Options()
    options.add_argument("--headless")  # Roda silenciosamente
    # Alta resolução para garantir nitidez na plotagem
    options.add_argument("--window-size=2560,1440") 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = None
    try:
        service = ChromeService(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Carregar a página do mapa local
        driver.get(caminho_html_absoluto)
        
        # Aguardar 3 segundos até que os tiles do mapa OpenStreetMap terminem de carregar no navegador
        time.sleep(3)
        
        # 1. Salvar como PNG em Alta Resolução
        caminho_png = os.path.join(SAIDA_DIR, f"{nome_base}.png")
        driver.save_screenshot(caminho_png)
        print(f"  [+] Imagem exportada com sucesso: {caminho_png}")
        
        # 2. Salvar como PDF via Chrome Protocol
        caminho_pdf = os.path.join(SAIDA_DIR, f"{nome_base}.pdf")
        pdf_options = {
            'landscape': True,
            'displayHeaderFooter': False,
            'printBackground': True,
            'preferCSSPageSize': True,
        }
        res = driver.execute_cdp_cmd("Page.printToPDF", pdf_options)
        
        with open(caminho_pdf, 'wb') as f:
            f.write(base64.b64decode(res['data']))
        print(f"  [+] PDF exportado com sucesso: {caminho_pdf}")
        
    except Exception as e:
        print(f"  [-] Erro ao exportar PDF/Imagem via Selenium: {str(e)}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def main():
    print("=== Iniciando sistema de plotagem mapeada ===")
    arquivos = listar_arquivos_entrada()
    
    if not arquivos:
        print("\n[Aviso] Nenhum arquivo .xlsx encontrado na pasta 'dados_entrada/'.")
        print("Adicione suas planilhas lá e rode o programa novamente.")
        return

    for caminho_arquivo in arquivos:
        nome_arquivo = os.path.basename(caminho_arquivo)
        nome_base = os.path.splitext(nome_arquivo)[0]
        
        print(f"\n>> Lendo o arquivo: {nome_arquivo}")
        
        # 1. Processar arquivo
        dados = processar_planilha(caminho_arquivo)
        if not dados:
            print(f"  [-] Nenhuma coordenada válida lida de {nome_arquivo}.")
            continue
            
        print(f"  [*] {len(dados)} marcações encontradas.")
        
        # 2. Criar HTML com o mapa
        caminho_html = criar_mapa(dados, nome_base)
        print(f"  [*] Molde do mapa (HTML) montado.")
        
        # 3. Exportar usando Selenium
        print(f"  [*] Renderizando arquivo de alta resolução... Aguarde...")
        html_para_pdf_imagem(caminho_html, nome_base)
        
    print("\n=== Rotina concluída ===")

if __name__ == '__main__':
    main()
