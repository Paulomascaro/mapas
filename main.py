import os
import sys
import time
import json
from leitor_xlsx import processar_planilha
from mapa_osm import criar_mapa
from config import SAIDA_DIR

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import base64

def html_para_pdf_imagem(caminho_html, nome_base):
    caminho_html_absoluto = f"file:///{os.path.abspath(caminho_html).replace(chr(92), '/')}"
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=2560,1440") 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Suprimir logs do selenium na saida padrao
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = None
    caminho_png = os.path.join(SAIDA_DIR, f"{nome_base}.png")
    caminho_pdf = os.path.join(SAIDA_DIR, f"{nome_base}.pdf")
    
    try:
        service = ChromeService(executable_path=ChromeDriverManager().install())
        
        # Desabilita output do service
        import subprocess
        service.creation_flags = subprocess.CREATE_NO_WINDOW
        
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get(caminho_html_absoluto)
        time.sleep(3)
        
        driver.save_screenshot(caminho_png)
        
        pdf_options = {
            'landscape': True,
            'displayHeaderFooter': False,
            'printBackground': True,
            'preferCSSPageSize': True,
        }
        res = driver.execute_cdp_cmd("Page.printToPDF", pdf_options)
        
        with open(caminho_pdf, 'wb') as f:
            f.write(base64.b64decode(res['data']))
            
        return caminho_pdf, caminho_png
    except Exception as e:
        raise Exception(f"Erro Selenium: {str(e)}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "Nenhum arquivo fornecido."}))
        return

    caminho_arquivo = sys.argv[1]
    
    if not os.path.exists(caminho_arquivo):
        print(json.dumps({"status": "error", "message": "Arquivo não encontrado."}))
        return

    nome_arquivo = os.path.basename(caminho_arquivo)
    nome_base = os.path.splitext(nome_arquivo)[0]

    try:
        dados = processar_planilha(caminho_arquivo)
        if not dados:
            print(json.dumps({"status": "error", "message": f"Nenhuma coordenada lida de {nome_arquivo}."}))
            return

        caminho_html = criar_mapa(dados, nome_base)
        
        caminho_pdf, caminho_png = html_para_pdf_imagem(caminho_html, nome_base)
        
        print(json.dumps({
            "status": "success",
            "nome_base": nome_base,
            "html": caminho_html,
            "pdf": caminho_pdf,
            "png": caminho_png
        }))
        
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == '__main__':
    # Forçar stdout para utf-8
    sys.stdout.reconfigure(encoding='utf-8')
    main()
