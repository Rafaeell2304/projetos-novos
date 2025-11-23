import calendar
from datetime import datetime, timedelta
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def cotar(dataDolar):
    """
    Busca a cotação do dólar no Banco Central do Brasil para o mês/ano especificado,
    trata os dias sem cotação e gera um gráfico interativo.
    """
    
    # Validação da entrada (MMYYYY)
    if len(dataDolar) != 6:
        raise ValueError("A data deve estar no formato MMYYYY (ex: '102019')")

    # Cria a primeira e última data do mês
    first_date = datetime.strptime(dataDolar, "%m%Y")
    last_date = first_date.replace(day=calendar.monthrange(first_date.year, first_date.month)[1])
    
    # Formato de data exigido pela API do Banco Central (MM-DD-YYYY)
    datainicio = first_date.strftime("%m-%d-%Y")
    datafim = last_date.strftime("%m-%d-%Y")

    # 1. Consulta a cotação do dólar no período (somente dias úteis)
    url = (
        f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
        f"CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?"
        f"@dataInicial='{datainicio}'&@dataFinalCotacao='{datafim}'&$format=json"
    )
    
    res = requests.get(url).json()
    
    # Se a API não retornar dados
    if 'value' not in res or not res['value']:
        print(f"Aviso: Nenhuma cotação encontrada para {dataDolar}. O período pode ser muito antigo.")
        return None
        
    # 2. Cria um dicionário com data e armazena (Compra e venda)
    result = {}
    for item in res['value']: #Percorre cada cotação
        # A data da API vem no formato completo com hora, convertemos para apenas data
        data_completa = datetime.strptime(item["dataHoraCotacao"], "%Y-%m-%d %H:%M:%S.%f")
        data = data_completa.date()
        compra = item["cotacaoCompra"]
        venda = item["cotacaoVenda"]
        result[data] = (compra, venda)
    
    # 3. Função para obter o último dia útil disponível (Tratamento de Feriados/Fins de Semana)
    def ultimo_dia_util(dia_atual):
        # Retrocede um dia para começar a procurar o dia útil mais próximo
        dia_util = dia_atual - timedelta(days=1)
        # Limite de busca para não cair no mês anterior (se for o dia 1)
        while dia_util >= first_date.date():
            if dia_util in result:
                return result[dia_util] # Retorna a cotação do dia útil
            dia_util -= timedelta(days=1)
        return (None, None) # Se não achar nada (ex: primeiro dia do mês)
    
    # 4. Compila a lista final de dados (incluindo fins de semana/feriados)
    dados_cotacao = []
    data_cotacao = first_date.date()
    while data_cotacao <= last_date.date():
        if data_cotacao in result:
            compra, venda = result[data_cotacao]
        else:
            # Se não é dia útil, usa o valor do último dia útil
            compra, venda = ultimo_dia_util(data_cotacao)
            
        dados_cotacao.append({
            "Data": data_cotacao.strftime("%d/%m/%Y"),
            "Compra": compra,
            "Venda": venda,
        })
        data_cotacao += timedelta(days=1)
        
    # 5. Cria o gráfico Plotly
    df = pd.DataFrame(dados_cotacao)

    fig = px.line(
        df,
        x="Data",
        y=["Compra", "Venda"],
        title=f"Cotação do Dólar (PTAX) - {first_date.strftime('%B de %Y')}",
        labels={"value": "Valor (R$)", "variable": "Tipo de Cotação"},
        color_discrete_map={
            "Compra": "green",
            "Venda": "red"
        }
    )
    fig.update_layout(template="plotly_white")
    
    # Salva o gráfico como arquivo HTML para ser embutido no blog
    nome_arquivo_html = f"cotacao_dolar_{dataDolar}.html"
    fig.write_html(nome_arquivo_html)
    
    print(f"Gráfico salvo em: {nome_arquivo_html}")
    return nome_arquivo_html

# Executa a função com a sua data
cotar('102019')