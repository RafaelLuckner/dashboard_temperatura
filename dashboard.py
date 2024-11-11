import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# load dataset
data = pd.read_csv('consumo de energia.csv',sep =';')

# organizando e limpando dataframe 
data = data.T.reset_index(drop=True)
data.columns = data.iloc[0,:].map(lambda x: x.split('/')[0])
data = data[1:]
data = data.map((lambda x: float(x.replace(',','.'))))

def tarifa_normal(df):
    base = 0.594
    tarifa_normal = np.round(np.sum(df*base),2)
    return tarifa_normal

def tarifa_branca(df):
    tar_fora_de_ponta =0.499
    tar_intermediaria = 0.724
    tar_ponta = 1.115

    a = np.sum(df[0:16]*tar_fora_de_ponta)
    b = np.sum(df[17:18]*tar_intermediaria)
    c = np.sum(df[18:20]* tar_ponta)
    d = np.sum(df[20:21]*tar_intermediaria)
    e = np.sum(df[21:23]*tar_fora_de_ponta)
    soma = np.round(np.sum(a+b+c+d+e),2)

    return soma

def tarifa_c_final_semana(df):
    fora_de_ponta =0.499

    fds = [5, 6, 12, 13, 19, 20, 26, 27]
    if int(df.name) in fds:
        tarifa = np.round(np.sum(df* fora_de_ponta ),2)
        return tarifa
    
    else: return tarifa_branca(df)

lista_tarifa_branca = []
lista_tarifa_normal = []
days = []

for day in data.columns:
    aux = data[day]
    custo_tarifa_normal = tarifa_normal(aux)
    custo_tarifa_branca = tarifa_c_final_semana(aux)

    lista_tarifa_branca.append(custo_tarifa_branca)
    lista_tarifa_normal.append(custo_tarifa_normal)
    days.append(int(day))


df_calculo = pd.DataFrame({'Dia': days,
                            'tn': lista_tarifa_normal,
                            'tb': lista_tarifa_branca,
                            'acm_tn': np.cumsum(lista_tarifa_normal),
                            'acm_tb': np.cumsum(lista_tarifa_branca)})
df_calculo.set_index('Dia')

df_soma = pd.DataFrame({'op': ['soma'],
                        'Tarifa Normal': np.sum(lista_tarifa_normal),
                        'Tarifa Branca': np.sum(lista_tarifa_branca)})

df_calculo['pct_economia'] = np.round((((df_calculo['acm_tn']-df_calculo['acm_tb'])/df_calculo['acm_tb'][30]))*100,2)
df_calculo['economia_dia'] = np.round(((df_calculo['acm_tn']/df_calculo['acm_tb'])-1)*100,2)

pct = np.round(((df_soma['Tarifa Normal'][0]/ df_soma['Tarifa Branca'][0])-1)*100,2)
ganho = df_soma['Tarifa Normal'][0] - df_soma['Tarifa Branca'][0]

# Configurações do painel Streamlit
st.set_page_config(page_title="Painel de Análise de Tarifas de Energia", layout="centered")

st.title("Painel de Análise de Tarifas de Energia")
st.markdown("### Comparação entre Tarifa Branca e Tarifa Convencional")

# Exibindo dados principais
st.write("**Custo final com a Tarifa Convencional:** R$ {:.2f}".format(df_calculo['acm_tn'][30]))
st.write("**Custo final com a Tarifa Branca:** R$ {:.2f}".format(df_calculo['acm_tb'][30]))
st.write("**Economia total ao optar pela Tarifa Branca:** R${:.2f}".format(ganho))

st.markdown("---") 

# Gráfico 1: Tarifas Branca e Convencional
st.markdown("#### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Custo acumulado ao longo do mês", unsafe_allow_html=True)
fig, ax = plt.subplots(figsize=(10, 4))

# Barras para Tarifa Branca e Tarifa Convencional
ax.bar(df_calculo['Dia'] - 0.2, df_calculo['acm_tb'], width=0.4, color='green', label='Tarifa Branca')
ax.bar(df_calculo['Dia'] + 0.2, df_calculo['acm_tn'], width=0.4, color='red', label='Tarifa Convencional')

# Título e labels
ax.set_xlabel("Dia")

ax.legend()

# Remover eixos superior e direito
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Exibir economia acima da última barra
economia = df_soma['Tarifa Normal'][0] - df_soma['Tarifa Branca'][0]
ultima_barra = df_calculo['Dia'].iloc[-1]  # Último dia no gráfico
ax.text(ultima_barra-5, max(df_calculo['acm_tb'].max(), df_calculo['acm_tn'].max()) * 1.02, 
        f"Economia de R$ {economia:.2f}", ha='center', va='bottom', fontsize=12, color='black', fontweight='bold')

# Remover a grade
ax.grid(False)
st.pyplot(fig)

st.markdown("---") 
st.write("")


# Gráfico 2: Economia Percentual
st.markdown("#### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Economia Percentual Acumulada", unsafe_allow_html=True)
fig, ax = plt.subplots(figsize=(10, 4))

# Linha com pontos de Economia Percentual Acumulada
ax.plot(df_calculo['Dia'], df_calculo['pct_economia'], color='blue', label='Economia Acumulada (%)')
# Removendo grade e eixos superior e direito
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
# ax.spines['left'].set_visible(False)
ax.grid(False)

# ax.get_yaxis().set_visible(False)

# Adicionando valores em cada ponto de 5 em 5 dias
for x, y in zip(df_calculo['Dia'], df_calculo['pct_economia']):
    if x % 8 == 0:  # Mostra o valor apenas a cada 5 dias
        ax.text(x, y+0.5, f"{y:.2f}%", ha='center', va='bottom', fontsize=10)
        ax.plot(x, y, 'o', color='blue', markersize=5)

# Valor final em destaque
final_x = df_calculo['Dia'].iloc[-1]
final_y = df_calculo['pct_economia'].iloc[-1]
ax.plot(final_x, final_y, 'o', color='black', markersize=7)
ax.text(final_x, final_y+0.2, f"{final_y:.2f}%", ha='center', va='bottom', color='black', fontweight='bold')
# Títulos e legenda
ax.set_xlabel("Dia")
ax.legend()
st.pyplot(fig)

# Conclusões e Recomendações
st.markdown("### Conclusões e Recomendações")
st.write("""
- A Tarifa Branca apresenta uma economia significativa, especialmente em horários de baixo consumo.
- Aos finais de semana a Tarifa Branca traz grande economia.
- Avalie a sazonalidade e horários de pico para maior economia com a Tarifa Branca.
""")
