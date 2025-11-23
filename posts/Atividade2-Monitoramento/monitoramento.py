import requests
import folium
import os
from dotenv import load_dotenv

# --- Configuração ---
load_dotenv()
TOKEN = os.getenv('SPTRANS_TOKEN')
CODIGO_LINHA = 1198  # Linha 695Y (Metrô Vl. Mariana / Term. Parelheiros)

print(f"Iniciando monitoramento da Linha 695Y (Cod: {CODIGO_LINHA})...")

# 1. Autenticação
s = requests.Session()
auth = s.post(f"http://api.olhovivo.sptrans.com.br/v2.1/Login/Autenticar?token={TOKEN}")

if auth.text != "true":
    print("Erro de Autenticação. Verifique seu arquivo .env")
    exit()

# 2. Coleta de Dados
url_paradas = f"http://api.olhovivo.sptrans.com.br/v2.1/Parada/BuscarParadasPorLinha?codigoLinha={CODIGO_LINHA}"
url_onibus = f"http://api.olhovivo.sptrans.com.br/v2.1/Posicao/Linha?codigoLinha={CODIGO_LINHA}"

paradas = s.get(url_paradas).json()
posicoes = s.get(url_onibus).json()
lista_onibus = posicoes.get('vs', [])

# 3. Geração do Mapa
if paradas:
    # Centraliza o mapa
    m = folium.Map(location=[paradas[0]['py'], paradas[0]['px']], zoom_start=13)

    # Paradas (Azul)
    for p in paradas:
        folium.Marker(
            location=[p['py'], p['px']],
            popup=f"Parada: {p['np']}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

    # Ônibus (Vermelho)
    if lista_onibus:
        for o in lista_onibus:
            folium.Marker(
                location=[o['py'], o['px']],
                popup=f"Prefixo: {o['p']}",
                icon=folium.Icon(color='red', icon='bus', prefix='fa')
            ).add_to(m)
        print(f"Sucesso! {len(lista_onibus)} onibus no mapa.")
    else:
        print("Aviso: Nenhum onibus rodando agora.")

    # Salva o arquivo HTML
    nome_arquivo = "mapa_linha_695Y.html"
    m.save(nome_arquivo)
    print(f"Arquivo '{nome_arquivo}' gerado com sucesso!")
else:
    print("Erro: Nao foi possivel carregar as paradas.")
    