import numpy as np
import os 
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print("LENDO ARQUIVOS DE TEXTO")

try:
    X_raw = np.loadtxt('X.txt').reshape(-1, 1)
    y = np.loadtxt('y.txt').reshape(-1,1)
except OSError:
    print("Erro: Não encontrei os arquivos X.txt ou y.txt na pasta!")
    exit()

print(f"Dados carregados de X:\n{X_raw}")

linhas = X_raw.shape[0]
coluna_um = np.ones((linhas, 1))

X = np.hstack((coluna_um, X_raw))

#Calcula tudo
Xt = np.transpose(X)
XtX = np.dot(Xt, X)
XtX_inversa = np.linalg.inv(XtX)
Xty = np.dot(Xt, y)
beta = np.dot(XtX_inversa, Xty)

print("\n---RESULTADO ---")
print(beta)


from plotnine import *
import pandas as pd

print("\n--- GERANDO O GRÁFICO ---")

# 1. Extraindo os valores
intercepto_calc = beta[0][0]
inclinacao_calc = beta[1][0]

# 2. Preparando o DataFrame
dados_grafico = {
    "x": X_raw.flatten(),
    "y": y.flatten()
}
df = pd.DataFrame(dados_grafico)

plot = (
    ggplot(df, aes("x", "y"))
    + geom_point(size=3, color="blue")
    + geom_abline(intercept=intercepto_calc, slope=inclinacao_calc, color="red", size=1.5)
    + labs(title="Regressão Linear", x="Variável X", y="Variável Y")
    + theme_light()
)

#3. imagem
print("Salvando imagem...")
plot.save("grafico_regressao.png")

print("Gráfico salvo com sucesso!")


