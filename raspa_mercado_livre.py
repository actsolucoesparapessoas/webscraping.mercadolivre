import streamlit as st
import sqlite3
from PIL import Image # Lib para carregar imagem no Streamlit

import webbrowser
from io import BytesIO
import requests
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
from urllib.parse import urlencode, urljoin, urlparse

#LINK PARA EDITAR A PLANILHA: https://docs.google.com/spreadsheets/d/1TSEtdHcccHN90IOKtS1tqEAtzlr9UyPQSuhLnJkl9lI/edit?usp=sharing
rD = requests.get('https://docs.google.com/spreadsheets/d/e/2PACX-1vSqgZ-c4X0D9bTLcpVSrcaty0TIYTtPL-tyKfo_UiBdrIrGOXbX8NymoQl37puy1qBoK-km1t1mnSfw/pub?gid=0&single=true&output=csv')
dataD = rD.content
df = pd.read_csv(BytesIO(dataD))
vetQTD = []
vetDESC = []
vetVmedio = []
vetVtotal = []
vetVmin = []
vetVmax = []

def Busca_Mercado_Livre(Descricao1, Descricao2, Descricao3):
  Busca_Mercado_Livre.Descricao1 = Descricao1
  Busca_Mercado_Livre.Descricao2 = Descricao2
  Busca_Mercado_Livre.Descricao3 = Descricao3
  Termo_Busca1 = Descricao1 + '-' + Descricao2 + '-' + Descricao3
  Termo_Busca2 = Descricao1 + '%20' + Descricao2 + '%20' + Descricao3

  url = str(f'https://lista.mercadolivre.com.br/{Termo_Busca1}#D[A:{Termo_Busca2}]')
  response = requests.get(url)
  html = response.text

  # Criando o objeto Beautiful Soup
  soup = BeautifulSoup(html, 'html.parser')

  # Buscando todos os elementos que contêm os produtos
  produtos = soup.find_all('div', class_='ui-search-result__content-wrapper')

  vetDESC = []
  vetPRECO = []
  vetLINK = []
  # Extraindo e imprimindo a descrição e o preço de cada produto
  for produto in produtos:
      # Encontrando a descrição do produto
      descricao_tag = produto.find('h2', class_='ui-search-item__title')
      descricao = descricao_tag.text.strip() if descricao_tag else 'Sem descrição'

      # Encontrando o preço do produto
      preco_tag = produto.find('span', class_='andes-money-amount__fraction')
      preco = preco_tag.text.strip() if preco_tag else 'Sem preço'
      preco = FormatarReal(float(preco))
      # Encontrando o link do produto
      link_tag = produto.find('a', class_='ui-search-link')
      link = link_tag['href'] if link_tag else 'Sem link'

      vetDESC.append(descricao)
      vetPRECO.append(float(preco))
      vetLINK.append(urljoin(link, " "))

  Media = round(np.mean(vetPRECO), 2)
  DesvPad = round(np.std(vetPRECO), 3)
  MIN = round(np.min(vetPRECO), 3)
  MAX = round(np.max(vetPRECO), 3)
  return Media, MIN, MAX, DesvPad, vetDESC, vetPRECO, vetLINK

def FormatarReal(valor = 1.234):
  #valor_real = "R${:,.2f}".format(valor).replace(",", "X").replace(".", ",").replace("X", ".")
  if len(str(valor))<=3:
    val = "{:,.2f}".format(valor).replace(",", "X").replace(".", ".").replace("X", "")
  else:
    val = "{:,.2f}".format(valor).replace(",", "X").replace(".", ",").replace("X", "")

  if ',' in val:
    val = float(val.replace(",", '.'))
    if len(str(val))<=4 and float(val)<10:
      val = round(float(val), 2)*1000
  return val
  
# Função para conectar ao banco de dados
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
    return conn      

#FUNÇÕES DA BASE DE DADOS Pesq.db
# Adiciona um novo registro à tabela
def ADD_registro(QTD, DESCRICAO):
    #InicializarCRUDpesq:
    connection = create_connection('Pesq.db')
    sql = connection.cursor()
    sql.execute('''CREATE TABLE IF NOT EXISTS Pesq (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                QTD INT,
                DESCRICAO TEXT)''')
    sql.execute('''INSERT INTO Pesq (QTD, DESCRICAO) VALUES (?, ?)''',(QTD, DESCRICAO))
    connection.commit()

# Exclui um registro da tabela
def DEL_registro(id):
    connection = create_connection('Pesq.db')
    sql = connection.cursor()
    sql.execute('''DELETE FROM Pesq WHERE id = ?''', (id,))
    connection.commit()

# Exibe todos os registros da tabela
def MOSTRAR_registros():
    connection = create_connection('Pesq.db')
    sql = connection.cursor()
    sql.execute('''SELECT * FROM Pesq''')
    registros = sql.fetchall()
    return registros

def MKD(texto, alinhamento = "esquerda", tamanho_fonte = 28, cor_fonte = "black"):
    if alinhamento.lower()=="justificado":
        alinhamento = "justified" 
    elif alinhamento.lower()=="esquerda":
        alinhamento = "left"
    elif alinhamento.lower()=="direita":
        alinhamento = "right"
    elif alinhamento.lower()=="centro":
        alinhamento = "center"
    elif alinhamento.lower()=="centralizado":
        alinhamento = "center"        
    else:
        alinhamento = "justified"
        
    conteudo = '<p style="font-weight: bolder; color:%s; font-size: %spx;">%s</p>'%(cor_fonte, tamanho_fonte, texto)    
    st.markdown(conteudo, unsafe_allow_html=True)
    mystyle0 = '''<style> p{text-align:%s;}</style>'''%(alinhamento)
    st.markdown(mystyle0, unsafe_allow_html=True) 

def sidebar_MKD(texto, alinhamento = "esquerda", tamanho_fonte = 28, cor_fonte = "black"):
    if alinhamento.lower()=="justificado":
        alinhamento = "justified" 
    elif alinhamento.lower()=="esquerda":
        alinhamento = "left"
    elif alinhamento.lower()=="direita":
        alinhamento = "right"
    elif alinhamento.lower()=="centro":
        alinhamento = "center"
    elif alinhamento.lower()=="centralizado":
        alinhamento = "center"        
    else:
        alinhamento = "justified"
        
    conteudo = '<p style="font-weight: bolder; color:%s; font-size: %spx;">%s</p>'%(cor_fonte, tamanho_fonte, texto)    
    st.sidebar.markdown(conteudo, unsafe_allow_html=True)
    mystyle1 = '''<style> p{text-align:%s;}</style>'''%(alinhamento)
    st.sidebar.markdown(mystyle1, unsafe_allow_html=True)
  
st.set_page_config(
     page_title="Scraping Mercado Livre - By: Massaki",
     page_icon="📃",
     layout="wide",
     initial_sidebar_state="expanded",
     menu_items={
         'Get Help': 'mailto:informacoes.actsp@gmail.com',
         'Report a bug': "mailto:informacoes.actsp@gmail.com",
         'About': "#### Desenvolvedor: Massaki de O. Igarashi"
     }
 )

new=2


image = Image.open('Logo_Web_Scraping1.png')    
st.sidebar.image(image, width=300)
info = 'O web scraping (raspagem na internet), também conhecido como extração de dados da web, é o nome dado ao processo de coleta de dados estruturados da web de maneira automatizada.'
sidebar_MKD(info, alinhamento = "centralizado", tamanho_fonte = 18, cor_fonte = "yellow")
st.sidebar.write('')
sidebar_MKD('Desenvolvido por: Massaki Igarashi', alinhamento = "centralizado", tamanho_fonte = 18, cor_fonte = "white")

#st.title('Web Scraping no Mercado Livre')
#st.subheader('Desenvolvido por: Massaki Igarashi')
MKD('Web Scraping no Mercado Livre', alinhamento = "centralizado", tamanho_fonte = 38, cor_fonte = "yelow")

tab1, tab2 = st.tabs(["Busca", "Lista"])
with tab1:
    # Criação do formulário usando st.form
    with st.form("Formulário"):
        col1, col2 = st.columns(2)
        with col1:
            col1_1, col1_2, col1_3 = st.columns(3)
            with col1_1:
                st.write('')
                QTD = st.text_input("Quantidade")
            with col1_2:
                st.write("")
            with col1_3:
                st.write("")    
            DESCRICAO = st.text_input("Descrição:", help="Digite apenas 3 palavras chaves para consulta. Termos maiores, una_as_palavras com _")
                # Botão de envio do formulário
            st.write('')
            cols1 = st.columns(2)
            with cols1[0]:
                submit_button1 = st.form_submit_button(label="Cadastrar na Lista de Compras", type="primary", use_container_width=True)
            with cols1[1]:   
                submit_button2 = st.form_submit_button(label="Pesquisar a Lista de Compras Cadastrada", type="secondary", use_container_width=True)

        with col2:
            st.write(''' ## **Dicas de uso:** ''')
            st.write(''' ##### **1ºPasso:** Digite a QTD e 3 Palavras chave na Descrição''')          
            Passo2 = '<p style="font-weight: bolder; color:red; font-size: 18px">Cadastrar na Lista de Compras</p>'
            Passo3 = '<p style="font-weight: bolder; color:darkgray; font-size: 16px">Pesquisar a Lista de Compras Cadastrada</p>'            
            
            st.write(''' ##### **2ºPasso:** Clique no botão''') 
            st.markdown(Passo2, unsafe_allow_html=True)
            st.write(''' ##### **3ºPasso:** Clique no botão''')  
            st.markdown(Passo3, unsafe_allow_html=True)
            mystyle2 =   '''<style> p{text-align:justified;}</style>'''
            st.markdown(mystyle2, unsafe_allow_html=True)      

    if submit_button1:
        ADD_registro(QTD, DESCRICAO)
        st.write("Dados enviados:")
        registros = MOSTRAR_registros()
        if registros:
            df = pd.DataFrame(registros, columns=['ID', 'QTD', 'DESCRIÇÃO'])
            st.dataframe(df)

        else:
            st.write('Não há registros no banco de dados.')
        
    if submit_button2:
        registros = MOSTRAR_registros()
        df = pd.DataFrame(registros, columns=['ID', 'QTD', 'DESCRIÇÃO'])
        for i in range(len(df)):
            termo = df['DESCRIÇÃO'][i].split()
            resp = Busca_Mercado_Livre(termo[0], termo[1], termo[2])
            #print(resp)
            DESC = resp[4]
            PRECO = resp[5]
            LINK = resp[6]
            dict1 = {'DESCRIÇÃO': DESC, 'PREÇO': PRECO, 'LINK': LINK}
            df1 = pd.DataFrame(dict1)
            with st.expander("Dados da Pesquisa: " + str(df['DESCRIÇÃO'][i])):
                st.write(df1)
                st.write("\n \n")
            vetDESC.append(termo)
            vetVmedio.append(resp[0])
            vetVmin.append(resp[1])
            vetVmax.append(resp[2])
            vetQTD.append(df['QTD'][i])
            vetVtotal.append(int(df['QTD'][i])*float(resp[0]))
        dict = {'QTD': vetQTD, 'DESCRIÇÃO': vetDESC, 'VALOR_MÉDIO': vetVmedio, 'VALOR_TOTAL': vetVtotal, 'VALOR_MÍNIMO': vetVmin, 'VALOR_MÁXIMO': vetVmax}
        Base_Dados = pd.DataFrame(dict)
        colunasA = st.columns(2)
        ##st.metric("Titulo_Superior", "Valor", "Variação")
        with colunasA[0]:
            st.write(Base_Dados)
        with colunasA[1]:
            #st.metric("Titulo_Superior", "Valor", "Variação")
            st.write(f' Considerando o Valor médio de cada produto o total estimado da sua lista é:')
            with st.container(height=None, border=True):
                MKD("R$" + str(round(sum(vetVtotal), 3)), alinhamento = "centro", tamanho_fonte = 56, cor_fonte = "blue")
            #st.write(f' \n \n Estima-se que, considerando o Valor médio de cada produto, sua lista de compras custe um total de R$ {round(sum(vetVtotal), 3)}')
        
        registros = MOSTRAR_registros()
        cols2 = st.columns(2)
        with cols2[0]:
            image = Image.open('Logo_Web_Scraping1.png')    
            st.image(image, width=350)
        with cols2[1]:
            if registros:
                df = pd.DataFrame(registros, columns=['ID', 'QTD', 'DESCRIÇÃO'])
                st.dataframe(df)
            else:
                st.write('Não há registros no banco de dados.')
                
with tab2:
    registros = MOSTRAR_registros()  
    colunas = st.columns(2)
    with colunas[0]:
        ColunasInternas = st.columns(3)
        with ColunasInternas[0]:
            IDpesq = str(st.number_input("ID a pesquisar?", value=1, step=1))
            if st.button("DELETAR"):
                DEL_registro(IDpesq)
                registros = MOSTRAR_registros()
        with ColunasInternas[1]:
            st.write("")
        with ColunasInternas[2]:
            st.write("")
    with colunas[1]:
        if registros:
            df = pd.DataFrame(registros, columns=['ID', 'QTD', 'DESCRIÇÃO'])
            st.dataframe(df)
        else:
            st.write('Não há registros no banco de dados.')
