import streamlit as st
import pandas as pd
import numpy  as np
import io
from datetime import datetime, timedelta
from PIL import Image
from functools import partial
import os
#from unidecode import unidecode
import subprocess
import sys

os.system(f"{sys.executable} -m pip install unidecode")

# Configurações da página
st.set_page_config(
    page_title="Título da Página",
    page_icon=":bar_chart:",  # Ícone da aba do navegador
    layout="wide",  # Layout para ocupar toda a largura da tela
    initial_sidebar_state="expanded",  # Estado inicial da barra lateral
)
# Dicionario associacoes
dic_meta = {'ARJF-ASSOCIACAO RECONSTRUIR DO JARDIM FONTALIS': 30000,
  'ASSOCIACAO ALCANDO VELAS': 30000,
  'ASSOCIACAO AMIGOS DA TIA EDNA': 30000,
  'ASSOCIACAO BENEFICENTE ARCA SOCIAL': 30000,
  'ASSOCIACAO BENEFICENTE RAUL DAS TINTAS': 10000,
  'ASSOCIACAO BENEFICENTE VIVENDA DA CRIANCA': 30000,
  'ASSOCIACAO BRASILEIRA MISSOES E ESPERANCA - ASBRAME': 30000,
  'ASSOCIACAO CRIANCAS DA BRASILANDIA PARA O MUNDO': 30000,
  'ASSOCIACAO DE ASSISTENCIA A MULHER AO ADOLESCENTE E A CRIANCA ESPERANCA': 30000,
  'ASSOCIACAO DE MORADORES DO ALTO DA VILA BRASILANDIA': 10000,
  'ASSOCIACAO DE MULHERES BOULEVAR DA PAZ': 10000,
  'ASSOCIACAO DOS IDOSOS DA ZONA SUL ROSA DE SARON': 10000,
  'ASSOCIACAO EDUCACAO,CULTURA,ARTE E CIDADANIA': 30000,
  'ASSOCIACAO ESPERANCA E DESTINO': 30000,
  'ASSOCIACAO INFANCIA E FAMILIA': 30000,
  'ASSOCIACAO INSTITUTO KARAN': 10000,
  'ASSOCIACAO IRMAOS DE VILA': 30000,
  'ASSOCIACAO MAO NO ARADO': 30000,
  'ASSOCIACAO PROJETO PONTO E VIRGULA': 30000,
  'ASSOCIACAO REDE ACESSILIBILIDADE': 50000,
  'ASSOCIACAO SEMPRE JUNTOS': 10000,
  'CHIC E SER SOLIDARIO': 30000,
  'FAVELA DOS SONHOS': 30000,
  'INSTITUTO BATISTA PR. SIMON HORBACZYK': 30000,
  'INSTITUTO CRISTIANE CAMARGO DOE VIDA': 30000,
  'INSTITUTO DESPORTIVO EDUCACIONAL DRIBLE CERTO': 10000,
  'INSTITUTO ECLESIA MOVEMENT': 50000,
  'INSTITUTO FELIZ CIDADE': 30000,
  'INSTITUTO INOVACAO SUSTENTAVEL': 10000,
  'INSTITUTO JOSEFINA BAKHITA': 30000,
  'INSTITUTO RECOMECAR': 10000,
  'INSTITUTO RESGATANDO VIDAS PARA VIDA': 50000,
  'INSTITUTO RESILIENCIA AZUL': 30000,
  'INSTITUTO RUGBY PARA TODOS': 10000,
  'INSTITUTO SONHAR ALTO': 30000,
  'INSTITUTO SUBLIM': 30000,
  'NUCLEO DE APOIO AO PEQUENO CIDADAO': 10000,
  'ONG CLUBE ESCOLA FORMARE': 10000,
  'ONG LIFE TRANSFORMERS': 10000,
  'ORGANIZACAO DA SOCIEDADE CIVIL IZAIAS LUZIA DA SILVA': 10000,
  'ORGANIZACAO DA SOCIEDADE CIVIL JUNTOS AO LAR DE SAO FRANCISCO DE ASSIS EM SAO PAULO': 10000,
  'ORGANIZACAO NAO GOVERNAMENTAL PILARES': 30000,
  'PROJETO NOS SOMOS A PONTE': 10000,
  'PROJETO SOCIAL NOVA CHANCE': 30000,
  'PROJETO VIELA': 50000,
  'UNIDADE PROPRIA POA': 50000,
  'VEM COMIGO GERANDO FRUTOS': 30000,
  'VOZES DAS PERIFERIAS': 30000}

# Funções
def estoque_inicial_ideal(indece_ajuste,df_mara ):
    
   
    #Criando df
    df_estoque_inicial_ideal = pd.DataFrame()
    # Retirando as ongs a desconsiderar do df_mara e agrupando o df resultante por ong, contando os Id_mara
    df_estoque_inicial_ideal = df_mara.groupby(['ong']).agg({ #df_mara[~df_mara['ong'].isin(ong_desconsiderar)].groupby(['ong']).agg({
       'id_mara' : 'count'
    }).reset_index()
    
    # renomeando a contagem do id_mara para 'Começando'
    df_estoque_inicial_ideal['Começando'] = df_estoque_inicial_ideal['id_mara']
    
    # Assumindo que todos os valores das colunas: 'Progredindo',,'Fortalecendo' e 'Compartilhando' são zeros
    df_estoque_inicial_ideal['Progredindo'] = 0
    df_estoque_inicial_ideal['Fortalecendo'] = 0
    df_estoque_inicial_ideal['Compartilhando'] = 0
    
    # Multiplicando a quantidade de marasmcomeçando por ong pelo indice de ajuste
    df_estoque_inicial_ideal['Começando'] = round(df_estoque_inicial_ideal['Começando'] * indece_ajuste)
    
    return df_estoque_inicial_ideal

def ranking_faturamento(df_estoque_inicial_ideal,df_produto, associacoes,dicionario_ranking_faturamento):
    
    # Criar df
    setor_linha = pd.DataFrame()
    # Remover os valores duplicados do df_produto referente as colunas setor e linha
    setor_linha = df_produto[['setor', 'linha']].drop_duplicates().reset_index(drop=True)
    # Remover acentos e caractéres especiais
    setor_linha['setor'] = setor_linha['setor'].apply(unidecode)
    setor_linha['linha'] = setor_linha['linha'].apply(unidecode)
    
    df_aux = pd.DataFrame(index = df_estoque_inicial_ideal['ong'], columns = setor_linha['linha'].unique(), data = 0)

    for ong in df_aux.index:
        for coluna in df_aux.columns:
            try:
                df_aux.loc[ong,coluna] = associacoes[ong] * dicionario_ranking_faturamento[coluna]
            except:
                df_aux.loc[ong,coluna] = 1 * dicionario_ranking_faturamento[coluna]
    return  df_aux

def estoque_alvo_cat(df_aux,df_estoque_inicial_ideal):
    # df_aux = df_ranking_faturamento
    
    df_aux_v1 = df_aux.copy()
    df_estoque_inicial_ideal_1 = df_estoque_inicial_ideal.copy()
    df_estoque_inicial_ideal_1.reset_index(inplace = True)
    df_estoque_inicial_ideal_1.set_index('ong',inplace= True)
    for ong in df_aux_v1.index:

        a = df_estoque_inicial_ideal_1.loc[ong]['Começando']
        b = df_estoque_inicial_ideal_1.loc[ong]['Progredindo']
        c = df_estoque_inicial_ideal_1.loc[ong]['Fortalecendo']
        d = df_estoque_inicial_ideal_1.loc[ong]['Compartilhando']

        soma  = a+b+c+d
        for coluna in df_aux_v1.columns:
            df_aux_v1.loc[ong,coluna] = soma * df_aux_v1.loc[ong,coluna]

    df_estoque_inicial_ideal_1.reset_index(inplace = True)
    df_estoque_alvo_ong_cat = df_aux_v1.copy()
    
    return df_estoque_alvo_ong_cat

def estoque_alvo_ong_cat_porcentagem(df_estoque_alvo_ong_cat):
    df_estoque_alvo_ong_cat_porcentagem = df_estoque_alvo_ong_cat.copy()
    for i in df_estoque_alvo_ong_cat_porcentagem.columns:
        df_estoque_alvo_ong_cat_porcentagem[i] =  df_estoque_alvo_ong_cat_porcentagem[i]/np.sum( df_estoque_alvo_ong_cat_porcentagem[i])
    df_estoque_alvo_ong_cat_porcentagem.fillna(0, inplace = True)
    
    return df_estoque_alvo_ong_cat_porcentagem

def preco_medio_linha_ong(df_aux,dicionario_ranking_faturamento):
    # def_aux =  df_ranking_faturamento
    df_aux_preco_medio = df_aux.copy()
    for ong in df_aux.index:
        for coluna in df_aux_preco_medio.columns:
            try:
                df_aux_preco_medio.loc[ong,coluna] = df_aux_preco_medio.loc[ong,coluna] * dicionario_ranking_faturamento[coluna]
            except:
                print('ERRO')
                df_aux_preco_medio.loc[ong,coluna] = 'ERRO'
    return df_aux_preco_medio

def data_ultimo_abastecimento(data):
    #data = '2024-06-05' (formato ano, mes, dia)
    data = (pd.to_datetime(data) + timedelta(days=1)).strftime('%Y-%m-%d')
    return data

def obter_segunda_feira_mais_recente():
    # Obter a data atual
    hoje = datetime.now()
    
    # Calcular a diferença de dias até a última segunda-feira
    dias_ate_segunda = (hoje.weekday() - 0) % 7
    
    # Subtrair a diferença de dias da data atual para obter a última segunda-feira
    ultima_segunda_feira = hoje - timedelta(days=dias_ate_segunda)
    
    # Retornar a data no formato "ano-mês-dia"
    return ultima_segunda_feira.strftime('%Y-%m-%d')

def estimativa_estoque_inicial(df_teste_abastecimento_inicial,df_venda_mara,df_produto ):
    
    
    data_ultimo_abastecimento_var = data_ultimo_abastecimento (str(df_teste_abastecimento_inicial['Data_Abastecimento'][0]))
    data_segunda_recente = obter_segunda_feira_mais_recente()
    
    nome_coluna = 'vendas_entre_'+data_ultimo_abastecimento_var+' e ' +str(data_segunda_recente)
    

    df_venda_v1 = pd.DataFrame()

    # cacrescentar nas vendas_maras colunas: setor, linha, descricao vindas da tabela produtos
    df_venda_v1 = pd.merge(df_venda_mara,df_produto[['cod_produto','setor','linha','descricao']], on = ['cod_produto'], how = 'left')


    #remover as datas de venda inferior ou igual a 8 de julho de 2024
    df_venda_v1 = df_venda_v1[( df_venda_v1['data_venda'] >= data_ultimo_abastecimento_var) & ( df_venda_v1['data_venda'] <= data_segunda_recente)].reset_index(drop =True)
    #Retirar acento
    df_venda_v1['ong'] = df_venda_v1['ong'].apply(unidecode)
    df_venda_v1['linha'] = df_venda_v1['linha'].apply(unidecode)

    # agrupar o df esultante por ['ong','linha'] e somar a coluna quantidade
    df_venda_v2 = pd.DataFrame()
    df_venda_v2 = df_venda_v1.groupby(['ong','linha']).agg({
            'quantidade':'sum'
        })
    df_venda_v2.columns = [nome_coluna]
    df_venda_v2.reset_index(inplace=True)
        

    #Acrescentanto hipotéticamente quantidade abastecidada até a data limite
    df_estoque_apos_abastecimento_v1 = pd.DataFrame()
    df_estoque_apos_abastecimento_v1 = df_teste_abastecimento_inicial.drop(columns={'Data_Abastecimento'}).reset_index().melt(id_vars=['ong'], var_name='linha', value_name='qtd_abastecida_ate_'+ str(data_ultimo_abastecimento_var)).set_index(['ong', 'linha'])
    df_estoque_apos_abastecimento_v1 = df_estoque_apos_abastecimento_v1.reset_index()
    df_estoque_apos_abastecimento_v1['ong'] = df_estoque_apos_abastecimento_v1['ong'].apply(unidecode)
    df_estoque_apos_abastecimento_v1['linha'] = df_estoque_apos_abastecimento_v1['linha'].apply(unidecode)

    df_estimativa_estoque = pd.DataFrame()
    df_estimativa_estoque = pd.merge(df_venda_v2, df_estoque_apos_abastecimento_v1,on =['ong','linha'], how = 'outer')


    df_estimativa_estoque.fillna(0,inplace=True)

    df_estimativa_estoque['estimativa_estoque_ong_em_'+str(data_segunda_recente)] = np.where((df_estimativa_estoque['qtd_abastecida_ate_'+ str(data_ultimo_abastecimento_var)] -df_estimativa_estoque[nome_coluna]) < 0,
                                                                          0,
                                                                          df_estimativa_estoque['qtd_abastecida_ate_'+ str(data_ultimo_abastecimento_var)] - df_estimativa_estoque[nome_coluna])


    df_ong_estoque_inicial = pd.DataFrame()
    df_ong_estoque_inicial = df_estimativa_estoque.groupby(['ong', 'linha']).agg({
            'estimativa_estoque_ong_em_'+ str(data_segunda_recente):'sum'
        })#.reset_index()
    return df_ong_estoque_inicial, df_estimativa_estoque

def estimativa_estoque_inicial_sku(df_abastecimento_inicial_ong_sku,df_venda_mara,df_produto ):
    dic_abastecimento_inicial = df_abastecimento_inicial_ong_sku.set_index('cod_produto')['descricao'].to_dict()
    dic_produto = df_produto.set_index('cod_produto')['descricao'].to_dict()
    
    #separando o intervalo de datas para filtrar as vendas, data do último abastecimeno +1 até a segunda feira mais recente
    data_ultimo_abastecimento_var = data_ultimo_abastecimento (str(df_abastecimento_inicial_ong_sku['Data_Abastecimento'][0]))
    data_segunda_recente = obter_segunda_feira_mais_recente()
    
    nome_coluna = 'vendas_entre_'+data_ultimo_abastecimento_var+' e ' +str(data_segunda_recente)
    nome_coluna_abastecimento = f"Abastecimento_em_{data_ultimo_abastecimento_var}"
    
    #Acrescentando linha no abstecimento inicial por ong e sku
    df_abastecimento_inicial_ong_sku['ong'] = df_abastecimento_inicial_ong_sku['ong'].apply(unidecode)
    df_abastecimento_inicial_ong_sku = pd.merge(df_abastecimento_inicial_ong_sku,df_produto[['cod_produto','linha']], on =['cod_produto'], how = 'left')
    
    abastecimento_inicial_ong_agg = df_abastecimento_inicial_ong_sku.groupby(['ong','cod_produto']).agg({
    'quantidade':'sum'
    })
    abastecimento_inicial_ong_agg.columns = [nome_coluna_abastecimento]
    
    
    df_venda_v1 = pd.DataFrame()

    # cacrescentar nas vendas_maras colunas: setor, linha, descricao vindas da tabela produtos
    df_venda_v1 = pd.merge(df_venda_mara,df_produto[['cod_produto','setor','linha','descricao']], on = ['cod_produto'], how = 'left')


    #remover as datas de venda inferior ou igual a 8 de julho de 2024
    df_venda_v1 = df_venda_v1[( df_venda_v1['data_venda'] >= data_ultimo_abastecimento_var) & ( df_venda_v1['data_venda'] <= data_segunda_recente)].reset_index(drop =True)
    #Retirar acento
    df_venda_v1['ong'] = df_venda_v1['ong'].apply(unidecode)
    df_venda_v1['linha'] = df_venda_v1['linha'].apply(unidecode)
    
    df_venda_mara_v2_agg = df_venda_v1.groupby(['ong','cod_produto']).agg({
    'quantidade':'sum'
    })
    df_venda_mara_v2_agg.columns = [nome_coluna]
    
    
    df_new = pd.DataFrame()
    df_new = pd.merge(abastecimento_inicial_ong_agg, df_venda_mara_v2_agg, on =['ong', 'cod_produto'] , how ='outer')
    df_new.fillna(0, inplace = True)
    df_new[f'estimativa_estoque_ong_em_{str(data_segunda_recente)}'] = np.where((df_new[nome_coluna_abastecimento] -df_new[nome_coluna]) < 0,
                                                                      0,
                                                                      df_new[nome_coluna_abastecimento] -df_new[nome_coluna])
    
    df_new.reset_index(inplace=True)
    df_new = pd.merge(df_new,df_produto[['cod_produto','linha']], on =['cod_produto'], how='left')
    df_new_2 = df_new.groupby(['ong', 'linha']).agg({
       f'estimativa_estoque_ong_em_{str(data_segunda_recente)}':'sum'
    })
    df_new = df_new[['ong', 'cod_produto',f'estimativa_estoque_ong_em_{str(data_segunda_recente)}']]
    df_new.columns = ['ong', 'cod_produto','estoque_inicial']
    
    df_new['descricao'] = df_new['cod_produto'].map(dic_abastecimento_inicial)
    
    df_new['descricao'] = np.where(df_new['descricao'].isna(),
                                df_new['cod_produto'].map(dic_produto),
                                  df_new['descricao'])
    
    
    return  df_new_2, df_new

def estoque_minimo_ong(porcentagem_estoque_alvo, df_estoque_alvo_ong_cat):
    #porcentagem_estoque_alvo = 0.5
    df_estouqe_minimo_ong = pd.DataFrame()
    df_estouqe_minimo_ong = df_estoque_alvo_ong_cat.copy()
    df_estouqe_minimo_ong = df_estouqe_minimo_ong * porcentagem_estoque_alvo
    
    return df_estouqe_minimo_ong

def saldo_abastecer(df_estouqe_minimo_ong,df_ong_estoque_inicial,porcentagem_estoque_alvo):
    dic = {}
    for ong in df_estouqe_minimo_ong.index:
        dic[ong] = []
        for coluna in df_estouqe_minimo_ong.columns:
            try:
                if (df_estouqe_minimo_ong.loc[ong,coluna]/porcentagem_estoque_alvo) - df_ong_estoque_inicial.loc[ong,coluna][0] < 0:
                    dic[ong].append(0)
                else:
                    dic[ong].append((df_estouqe_minimo_ong.loc[ong,coluna]/porcentagem_estoque_alvo) - df_ong_estoque_inicial.loc[ong,coluna][0])


            except:

                    dic[ong].append((df_estouqe_minimo_ong.loc[ong,coluna]/porcentagem_estoque_alvo))

    df_saldo_abastecer = pd.DataFrame(dic)
    df_saldo_abastecer = df_saldo_abastecer.set_index(df_estouqe_minimo_ong.columns).T
    
    return df_saldo_abastecer

# entrar manualmente porcentagem_disp_mara
def estoque_cd_agrupado(porcentagem_disp_mara, df_estoque, df_produto):
    # entrar maualmente
    
    df_estoque_cd = pd.DataFrame()
    df_estoque_cd = pd.merge(df_estoque,df_produto[['cod_produto','setor','linha']], on =['cod_produto'], how = 'left' )
    df_estoque_cd_agrupado = pd.DataFrame()

    df_estoque_cd_agrupado = df_estoque_cd[df_estoque_cd['id_loja'] == 3].groupby(['linha']).agg({
       'quantidade': 'sum'
    })
    df_estoque_cd_agrupado = df_estoque_cd_agrupado * porcentagem_disp_mara
    
    
    return df_estoque_cd_agrupado

def estoque_cd_disponivel(df_estoque_alvo_ong_cat,df_estoque_alvo_ong_cat_porcentagem,df_estoque_cd_agrupado):
    estoque_cd_disp = df_estoque_alvo_ong_cat.copy()
    for coluna in df_estoque_alvo_ong_cat.columns:
        try:
           estoque_cd_disp[coluna] = df_estoque_alvo_ong_cat_porcentagem[coluna] * df_estoque_cd_agrupado.loc[coluna][0]
        except:
            estoque_cd_disp[coluna] = df_estoque_alvo_ong_cat_porcentagem[coluna]
            
    return estoque_cd_disp

def abastecimento(estoque_cd_disp,df_saldo_abastecer,df_estouqe_minimo_ong): ####AVALIAR
    df_abastecimento = estoque_cd_disp.copy()
    for index, row in estoque_cd_disp.iterrows():
        for coluna in  estoque_cd_disp.columns:
            if df_saldo_abastecer.loc[index][coluna] == 0:
                df_abastecimento.loc[index][coluna] = 0
            else:
                if min(df_saldo_abastecer.loc[index][coluna], estoque_cd_disp.loc[index][coluna]) == 0:
                    df_abastecimento.loc[index][coluna] = min(estoque_cd_disp.loc[index][coluna], df_estouqe_minimo_ong.loc[index][coluna])
                else:
                    df_abastecimento.loc[index][coluna] = min(df_saldo_abastecer.loc[index][coluna], estoque_cd_disp.loc[index][coluna])

    return df_abastecimento

def estoque_apos_abastecimento(df_abastecimento,df_ong_estoque_inicial):

    df_estoque_apos_abastecimento = df_abastecimento.copy()
    for ong in df_abastecimento.index:
        for coluna in df_abastecimento.columns:
            try:
                estoque_inicio = df_ong_estoque_inicial.loc[ong, coluna][0]
            except:
                estoque_inicio = 0

            df_estoque_apos_abastecimento.loc[ong][coluna] = df_estoque_apos_abastecimento.loc[ong][coluna] + estoque_inicio
    
    return df_estoque_apos_abastecimento

def estoque_apos_abastecimento_sku(estoque_inicial, dic_abastecimento_ong_sku):
    data_atual = datetime.now().strftime("%Y-%m-%d")
    
    lst = []
    for ong,df in dic_abastecimento_ong_sku.items():
        df['ong'] = ong
        lst.append(df)
        
    df = pd.concat(lst)
    df.reset_index(inplace=True)
    
    df_estoque_final = pd.merge(df,estoque_inicial, on =['cod_produto','ong'], how ='outer' )
    df_estoque_final.fillna(0,inplace=True)
    
    df_estoque_final['descricao'] = np.where(df_estoque_final['descricao'] == 0,
                                            df_estoque_final['descrição'] ,
                                            df_estoque_final['descricao'])
    #df_estoque_final['descricao'] = df_estoque_final['cod_produto'].map(dic_descricao)
    df_estoque_final['Data_Abastecimento'] = data_atual
    
    df_estoque_final.rename(columns = {'quantidade': 'abastecimento'}, inplace = True)
    
    df_estoque_final['quantidade'] = df_estoque_final['estoque_inicial'] + df_estoque_final['abastecimento']
    return df_estoque_final[['ong','cod_produto','descricao','quantidade','Data_Abastecimento']]

def porcentagem_sku_cd(df_estoque,df_produto):
    
    df_teste = pd.DataFrame()
    df_teste = df_estoque[df_estoque['id_loja'] == 3].groupby(['cod_produto']).agg({
      'quantidade' : 'sum'
    }).sort_values(by = 'quantidade', ascending = False).reset_index()

    df_teste = pd.merge(df_teste,df_produto[['cod_produto','linha']], on = ['cod_produto'], how = 'left')

    df_teste_total = pd.DataFrame()
    df_teste_total = df_teste.groupby('linha').agg({
     'quantidade' : 'sum'
    })
    df_teste_total.columns = ['Total']
    df_teste_total.reset_index(inplace=True)

    df_teste = pd.merge(df_teste,df_teste_total,on =['linha'], how = 'left')
    df_teste['Porcentagem'] = df_teste['quantidade']/df_teste['Total']

    df_teste = df_teste[['cod_produto','linha','Porcentagem']].set_index(['cod_produto'])
    
    return df_teste

def abasteciemnto_ong_sku(df_abastecimento,df_teste,df_produto ):

    dic_descricao = df_produto.set_index('cod_produto')['descricao'].to_dict()
    
    dicionario = {}
    dicionario_1 = {}
    for ong in df_abastecimento.index: #['ARJF-ASSOCIACAO RECONSTRUIR DO JARDIM FONTALIS']:
        df_abastecimento_ong_sku =  pd.DataFrame(index = df_teste.reset_index()['cod_produto'], columns = df_estoque_alvo_ong_cat.columns, data = 0)

        dicionario[ong] = df_abastecimento_ong_sku

        for index in df_abastecimento_ong_sku.index:
            for coluna in df_abastecimento_ong_sku.columns:
                try:
                    if df_teste.loc[index]['linha'] == coluna:
                        df_abastecimento_ong_sku.loc[index, coluna] = df_abastecimento.loc[ong,coluna] * df_teste.loc[index]['Porcentagem']
                    else:
                        df_abastecimento_ong_sku.loc[index, coluna] = df_abastecimento_ong_sku.loc[index, coluna] 
                except:
                    df_abastecimento_ong_sku.loc[index, coluna] =  df_abastecimento_ong_sku.loc[index, coluna] * 1
        dicionario[ong] = df_abastecimento_ong_sku
        df = pd.DataFrame()
        df = df_abastecimento_ong_sku.sum(axis=1).apply(lambda x: round(x)).to_frame()
        df.columns = ['quantidade']
        df['descrição'] = df.index.map(dic_descricao)
        dicionario_1[ong] = df.sort_values(by='quantidade', ascending = False)
    return dicionario_1 

def formatar_como_porcentagem(valor):
    if isinstance(valor, (int, float)):  # Certifique-se de que o valor é numérico
        return f'{valor:.2%}'
    return valor

def porcentagem_para_decimal(porcentagem_str):
    # Remove o símbolo '%' da string
    valor_str = porcentagem_str.replace('%', '')
    # Converte a string para float
    valor_float = float(valor_str)
    # Converte para valor decimal
    valor_decimal = valor_float / 100
    return valor_decimal

def exibir_imagem(caminho, largura):

    """
    Exibe uma imagem no Streamlit com o caminho especificado e opções de ajuste de tamanho.

    Parâmetros:
    - caminho (str): Caminho para o arquivo da imagem.
    - largura (int, opcional): Largura da imagem em pixels. Se None, usa a largura original.
    - altura (int, opcional): Altura da imagem em pixels. Se None, ajusta a altura proporcionalmente.
    - legenda (str, opcional): Legenda para a imagem.
    """
    try:
        imagem = Image.open(caminho)
        st.image(imagem,  width=largura)
    except FileNotFoundError:
        st.error(f"Arquivo não encontrado: {caminho}")

def nivel_abastecimento(df_estoque_apos_abastecimento,df_estoque_minimo_ong,porcentagem_estoque_alvo):

    df_porcentagem_estoque_disponibilizado = pd.DataFrame()
    df_porcentagem_estoque_disponibilizado = df_estoque_apos_abastecimento/(df_estoque_minimo_ong/porcentagem_estoque_alvo)
    df_porcentagem_estoque_disponibilizado.fillna('Meta Atingida', inplace = True)
    df_porcentagem_estoque_disponibilizado.replace([np.inf, -np.inf], 'Meta Atingida', inplace=True)
    df_porcentagem_estoque_disponibilizado = df_porcentagem_estoque_disponibilizado.applymap(lambda x: formatar_como_porcentagem(x))
    return df_porcentagem_estoque_disponibilizado

def ajuste(df_estoque_inicial_ideal):
    df_estoque_inicial_1 = df_estoque_inicial_ideal.copy()

    df_estoque_inicial_1 = df_estoque_inicial_1[['Começando','Progredindo','Fortalecendo','Compartilhando']]
    df_estoque_inicial_ideal['soma'] =  df_estoque_inicial_1.sum(axis=1)
        
    return df_estoque_inicial_ideal

def ranking(dicionario_ranking_faturamento, df_ajuste):
    data = [list(dicionario_ranking_faturamento.values())] * len(df_ajuste['ong'])
    # Criar o DataFrame
    df_ranking = pd.DataFrame(data, index=df_ajuste['ong'], columns=dicionario_ranking_faturamento.keys())

    df_ranking = df_ranking.mul(list(df_ajuste['soma']), axis=0)

    return df_ranking 

def preco_medio(df_estoque,df_produto):
    df_estoque_loja_3 = pd.DataFrame()
    df_estoque_loja_3 = df_estoque[df_estoque["id_loja"] == 3].groupby(["cod_produto"]).agg({
        'quantidade': 'sum'
    }).reset_index()
    df_estoque_loja_3 = pd.merge(df_estoque_loja_3, df_produto[['cod_produto','preco_vendas','linha']])
    df_estoque_loja_3['valor_estoque'] = df_estoque_loja_3['preco_vendas'] * df_estoque_loja_3['quantidade']

    df_estoque_loja_3 = df_estoque_loja_3.groupby(['linha']).agg({
       'preco_vendas': 'sum',
        'quantidade': 'sum',
        'valor_estoque':'sum'
    })
    df_estoque_loja_3['preco_medio'] = df_estoque_loja_3['valor_estoque']/df_estoque_loja_3['quantidade']

    df_estoque_loja_3.fillna(0,inplace = True)
    return df_estoque_loja_3 

def ranking_1 (df_ranking,df_preco_medio):
    df_ranking_1 = df_ranking.copy()
    for coluna in df_ranking_1.columns:
        
        try: 
            preco_medio = df_preco_medio.loc[coluna]['preco_medio']
        except: 
            preco_medio = 0
        
        df_ranking_1.loc[:,coluna] = df_ranking_1.loc[:,coluna] * preco_medio
    df_ranking_1['soma'] = df_ranking_1.sum(axis=1)
    return df_ranking_1

def dic_indice_meta(dicionario_meta_ong, df_ranking_1):
    df_meta = pd.DataFrame(list(dicionario_meta_ong.values()), index=dicionario_meta_ong.keys(), columns=['meta'])
    df_ranking_1 = df_ranking_1.join(df_meta, how='left')
            
    df_ranking_1['associacao'] = df_ranking_1['meta']/df_ranking_1['soma']

    dicionario = df_ranking_1['associacao'].to_dict()    
    return dicionario


# Caminho para a imagem
caminho = "C:/Users/pedro.arroyo.cruz/Desktop/Mara/streamlit_estoque_mara/Logo-AsMara-nova-cor_low-1024x937-optimized.webp"

# Layout com colunas
colTitulo, colImagem = st.columns([2, 1])  # Ajuste os pesos conforme necessário

with colTitulo:
    # Adicionando título
    st.title("Abastecimento Estoque MARAS")
    

with colImagem:
    # Exibindo a imagem
    exibir_imagem(caminho, largura=200)

#Adicioando título
#st.title('Abastecimento Estoque MARAS')

# Criar abas
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Upload bases", "Definição de parâmetros", "Abastecimento por ONG e SKU", 'Nível de abastecimento', 'Estoque negativo'])

with tab1:

    if 'bases' not in st.session_state:
        st.header('Upload')

        # Adicionar widget de upload de arquivos
        uploaded_files = st.file_uploader(
            label="",
            type=None,
            accept_multiple_files=True,  # Alterado para aceitar múltiplos arquivos
            key=None,
            help=None,
            on_change=None,
            args=None,
            kwargs=None,
            disabled=False,
            label_visibility="collapsed"
        )

        # Verificar se algum arquivo foi carregado
        if uploaded_files:
            # Inicializar dicionário para armazenar DataFrames
            dfs = {}

            for uploaded_file in uploaded_files:
                # Verificar se o arquivo está sendo carregado corretamente
                if uploaded_file is not None:
                    #st.write("Arquivo carregado:", uploaded_file.name)

                    # Ler o arquivo Excel em um DataFrame
                    df = pd.read_excel(uploaded_file)
                    
                    # Armazenar o DataFrame no dicionário com o nome do arquivo como chave
                    dfs[uploaded_file.name] = df
                    #st.write("Arquivo carregado:", uploaded_file.name)

            st.success('Bases Carregadas!', icon="✅")
            # Lendo os DFs ###################################################
            df_estoque = dfs['estoques.xlsx']
            # Substituindo valores negativos por 0
            #df_estoque['quantidade'] = np.where(df_estoque['quantidade'] < 0, 0,df_estoque['quantidade'] )

            df_loja = dfs["lojas.xlsx"]

            df_mara = dfs["maras.xlsx"]
            df_mara['ong'] = df_mara['ong'].apply(unidecode)

            df_produto = dfs["produtos.xlsx"]
            df_produto['linha'] = df_produto['linha'].apply(unidecode)

            #df_venda_loja = dfs["vendas_lojas.xlsx"]
            # Substituindo valores negativos por 0
            #df_venda_loja['quantidade'] = np.where(df_venda_loja['quantidade'] < 0, 0,df_venda_loja['quantidade'] )

            #df_venda_mara = dfs["vendas_maras.xlsx"]
            #ARRUMAR ESSA PARTE FUTURAMENTE !!!!!!
            df_venda_mara = dfs["vendas_maras.xlsx"]
            # Substituindo valores negativos por 0
            df_venda_mara['quantidade'] = np.where(df_venda_mara['quantidade'] < 0, 0,df_venda_mara['quantidade'] )

            df_inicio_vendas = pd.DataFrame()
            df_inicio_vendas = df_venda_mara.groupby(['id_mara']).agg({
                'data_venda' :'min'
            }).reset_index()
            df_inicio_vendas.rename(columns = {'data_venda':'inicio_vendas'},inplace = True)

            df_venda_mara = pd.merge(df_venda_mara, df_inicio_vendas, on = ['id_mara'], how = 'left')
            df_venda_mara = pd.merge(df_venda_mara, df_mara[['id_mara', 'ong']],  on = ['id_mara'], how = 'left')
            
            

            #df_teste_abastecimento_inicial = dfs['df_teste_abastecimento_inicial.xlsx']
            #ARRUMAR ESSA PARTE FUTURAMENTE !!!!!!
            df_teste_abastecimento_inicial = dfs['df_abastecimento_inicial_ong_sku.xlsx']
            # Criar df
            setor_linha = pd.DataFrame()
            # Remover os valores duplicados do df_produto referente as colunas setor e linha
            setor_linha = df_produto[['setor', 'linha']].drop_duplicates().reset_index(drop=True)
            # Remover acentos e caractéres especiais
            setor_linha['setor'] = setor_linha['setor'].apply(unidecode)
            setor_linha['linha'] = setor_linha['linha'].apply(unidecode)
            ###################################################
            st.session_state.bases = {
                'df_estoque': df_estoque,
                'df_loja': df_loja,
                'df_mara': df_mara,
                'df_produto': df_produto,
                #'df_venda_loja': df_venda_loja,
                'df_venda_mara': df_venda_mara,
                'df_teste_abastecimento_inicial': df_teste_abastecimento_inicial,
                'setor_linha': setor_linha
            }
            
# Verificar se os DataFrames estão armazenados no session_state
if 'bases' in st.session_state:
    df_estoque = st.session_state.bases.get('df_estoque')
    df_loja = st.session_state.bases.get('df_loja')
    df_mara = st.session_state.bases.get('df_mara')
    df_produto = st.session_state.bases.get('df_produto')
    #df_venda_loja = st.session_state.bases.get('df_venda_loja')
    df_venda_mara = st.session_state.bases.get('df_venda_mara')
    df_teste_abastecimento_inicial = st.session_state.bases.get('df_teste_abastecimento_inicial')
    setor_linha = st.session_state.bases.get('setor_linha')


    categorias_valores = {
    "CASA - CAMEBA": 0,
    "CASA - DECORACAO": 0,
    "CASA - ELETRO LAVANDERIA": 0,
    "CASA - UTENSILIOS COZINHA": 10,
    "MODA - ACESSORIOS": 1,
    "MODA - CALCADOS": 11,
    "MODA - FEMININO": 76,
    "MODA - INFANTIL": 6,
    "MODA - MASCULINO": 6,
    "GERAL" : 10
    }    
    with tab2:

        col1, col2,col3,col4,col5 = st.columns(5) 
        with col1:
            st.header('Porcentagens')


            
            indice_ajuste =  st.number_input("Porcentagem de Ongs ativas para abastecimento", min_value=0.0, max_value=1.0, step=0.01, format="%.2f", value= 0.4)
            
            porcentagem_estoque_alvo = st.number_input("Porcentagem do Estoque Alvo", min_value=0.0, max_value=1.0, step=0.01, format="%.2f", value= 1.0)
            porcentagem_disp_mara =  st.number_input("Porcentagem do estoque disponível para Mara no CD", min_value=0.0, max_value=1.0, step=0.01, format="%.2f", value= 0.7)
            #porcentagem_estoque_alvo = st.slider("Porcentagem do Estoque Alvo", min_value=0.0, max_value=1.0, step=0.01, format="%.2f")
            #porcentagem_disp_mara = st.slider("Porcentagem Disponível Mara no CD", min_value=0.0, max_value=1.0, step=0.01, format="%.2f") 
        with col2:
                    
            st.header('Ranking de Faturamento')
            dicionario_ranking_faturamento = {}
            for valor in setor_linha['linha'].sort_values().unique():
                try:
                    valor_pad = categorias_valores[valor]
                except:
                    valor_pad = 0
                dicionario_ranking_faturamento[valor] = st.number_input(f'Insira o valor para: {valor}', value=valor_pad)
        with col3:
            st.header('Remover Ongs')
            excluir_ong =  df_mara['ong'].sort_values().unique()
            ong_desconsiderar = ['CD','CIELO','CLIQX','GERAL','GOOGLE','UNIDADE PROPRIA POA']
            selecionados = st.multiselect("Selecione as ONGs que serão removidas:", excluir_ong, default=ong_desconsiderar)
            df_mara = df_mara[~df_mara['ong'].isin(selecionados)].reset_index(drop=True)

        with col4:
            st.header('Meta Financeira por Ong')
            dicionario_meta_ong = {}
            for ong in df_mara['ong'].sort_values().unique():
                try:
                    valor = dic_meta[ong]
                except:
                    valor = 0
                dicionario_meta_ong[ong] = st.number_input(f'Insira a meta financeira para: {ong}', value=valor)    
        
        with col5:
            st.header('Confirmar Informações')
            dados_corretos = st.checkbox("Os dados estão corretos?", value=False)

                #st.header("Coluna 1")
    if dados_corretos:
        with tab3:
            
            if 'bases_aba3' not in st.session_state:
                # indice ajuste preencher manual
                #indece_ajuste = 0.4
                df_estoque_inicial_ideal = estoque_inicial_ideal(indice_ajuste,df_mara )

                ##########################
                df_ajuste = ajuste(df_estoque_inicial_ideal)
                df_ranking = ranking(dicionario_ranking_faturamento, df_ajuste)
                df_preco_medio = preco_medio(df_estoque,df_produto)
                df_ranking_1 = ranking_1(df_ranking,df_preco_medio)
                associacoes = dic_indice_meta(dicionario_meta_ong, df_ranking_1)
                ##########################

                # associacoes e dicionario_ranking_faturamento preencher manual, df_ranking_faturamento = df_aux
                df_ranking_faturamento = ranking_faturamento(df_estoque_inicial_ideal,df_produto, associacoes,dicionario_ranking_faturamento)

                df_estoque_alvo_ong_cat = estoque_alvo_cat(df_ranking_faturamento,df_estoque_inicial_ideal)

                df_estoque_alvo_ong_cat_porcentagem = estoque_alvo_ong_cat_porcentagem(df_estoque_alvo_ong_cat)

                # dicionario_ranking_faturamento preencher manual
                df_preco_medio_linha_ong = preco_medio_linha_ong(df_ranking_faturamento, dicionario_ranking_faturamento)

                # df_teste_abastecimento_inicial inicialmente vem de uma base externa, posteriormente é susbituido pelo df_apos_abstecimento

                #df_estimativa_estoque_inicial_full = estimativa_estoque_inicial_sku(df_abastecimento_inicial_ong_sku,df_venda_mara_v2,df_produto)[0]
                df_estimativa_estoque_inicial_agg = estimativa_estoque_inicial_sku(df_teste_abastecimento_inicial,df_venda_mara,df_produto)[0]
                df_estimativa_estoque_inicial = estimativa_estoque_inicial_sku(df_teste_abastecimento_inicial,df_venda_mara,df_produto)[1]
                # definir manualmente porcentagem_estoque_alvo
                #porcentagem_estoque_alvo = 0.5
                df_estoque_minimo_ong = estoque_minimo_ong(porcentagem_estoque_alvo, df_estoque_alvo_ong_cat)
                

                #porcentagem_estoque_alvo entrar manualmente
                #df_saldo_abastecer = saldo_abastecer(df_estoque_minimo_ong,df_estimativa_estoque_inicial,porcentagem_estoque_alvo)
                df_saldo_abastecer = saldo_abastecer(df_estoque_minimo_ong,df_estimativa_estoque_inicial_agg,porcentagem_estoque_alvo)
                # porcentagem_disp_mara entrar manualmente
                #porcentagem_disp_mara = 0.7
                df_estoque_cd_agrupado = estoque_cd_agrupado(porcentagem_disp_mara, df_estoque, df_produto)

                df_estoque_cd_disponivel = estoque_cd_disponivel(df_estoque_alvo_ong_cat,df_estoque_alvo_ong_cat_porcentagem,df_estoque_cd_agrupado)

                df_abastecimento = abastecimento(df_estoque_cd_disponivel,df_saldo_abastecer,df_estoque_minimo_ong)

                df_porcentagem_sku_cd = porcentagem_sku_cd(df_estoque,df_produto)

                #df_estoque_apos_abastecimento = estoque_apos_abastecimento(df_abastecimento,df_estimativa_estoque_inicial)
                df_estoque_apos_abastecimento = estoque_apos_abastecimento(df_abastecimento,df_estimativa_estoque_inicial_agg)

                dic_abastecimento_ong_sku = abasteciemnto_ong_sku(df_abastecimento,df_porcentagem_sku_cd ,df_produto)

                df_apos_abastecimento_sku = estoque_apos_abastecimento_sku(df_estimativa_estoque_inicial, dic_abastecimento_ong_sku)

                #df_nivel_abastecimento = nivel_abastecimento(df_estoque_apos_abastecimento,df_estoque_minimo_ong,porcentagem_estoque_alvo)
                df_nivel_abastecimento = nivel_abastecimento(df_estoque_apos_abastecimento,df_estoque_minimo_ong,porcentagem_estoque_alvo)
                #EXPORTAR df_apos_abastecimento_sku
                
                # Construir o nome do arquivo com data e hora
                output_file = f"C:/Users/pedro.arroyo.cruz/Desktop/Mara/Output_Abastecimento/Abastecimento({datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}).xlsx"
                # Criar um buffer de memória
                buffer = io.BytesIO()


                # EXPORTANDO O DF PARA A PASTA DOWNLOADS
                user_home = os.path.expanduser('~')
                downloads_path = os.path.join(user_home, 'Downloads')

                # Salvando o arquivo Excel
                df_apos_abastecimento_sku.to_excel(os.path.join(downloads_path, 'df_abastecimento_inicial_ong_sku.xlsx'), index=False)
                # Criar o arquivo Excel no buffer
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    for sheet_name, df_abastecimento_ong_sku_exp in dic_abastecimento_ong_sku.items():
                        sheet_name = sheet_name[:30]  # Limitar o nome da aba a 30 caracteres
                        df_abastecimento_ong_sku_exp.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Colocar o cursor de volta no início do buffer
                buffer.seek(0)
                
                st.session_state.bases_aba3 = {
                        'dic_abastecimento_ong_sku': dic_abastecimento_ong_sku,
                        'df_estoque_apos_abastecimento': df_estoque_apos_abastecimento,
                        'df_abastecimento_ong_sku_exp': df_abastecimento_ong_sku_exp,
                        'df_nivel_abastecimento':df_nivel_abastecimento,
                        'excel_buffer': buffer,
                        'associacoes' : associacoes
                    }
                buffer = st.session_state.bases_aba3.get('excel_buffer')

                option = st.selectbox(
                "Selecione a ONG",
                list(dic_abastecimento_ong_sku.keys()),
                index=None,
                placeholder="Selecione uma ong...",
                )

                st.write("Você selecionou:", option)
                if option != None:
                    #dic_abastecimento_ong_sku[option]
                    # Exibir o DataFrame com ajuste de largura e altura
                    #st.write('aqui')
                    st.dataframe(dic_abastecimento_ong_sku[option], width=800, height=600)
                # Criar um botão de download
                st.download_button(
                    label="Baixar Relatório com 100% Ongs",
                    data=buffer,
                    file_name=f"Abastecimento_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            else:
                #st.write('ENTROU AQUI')
                df_estoque_apos_abastecimento = st.session_state.bases_aba3.get('df_estoque_apos_abastecimento')
                dic_abastecimento_ong_sku = st.session_state.bases_aba3.get('dic_abastecimento_ong_sku')
                buffer = st.session_state.bases_aba3.get('excel_buffer')

                df_nivel_abastecimento = st.session_state.bases_aba3.get('df_nivel_abastecimento')

                option = st.selectbox(
                "Selecione a ONG",
                list(dic_abastecimento_ong_sku.keys()),
                index=None,
                placeholder="Selecione uma ong...",
                )

                st.write("Você selecionou:", option)
                if option != None:
                    dic_abastecimento_ong_sku[option]
                

                # Criar um botão de download
                st.download_button(
                    label="Baixar Relatório com 100% Ongs",
                    data=buffer,
                    file_name=f"Abastecimento_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        with tab4:
            
            col1, col2,col3 = st.columns(3) 

            def colorir_celula(valor,valor_verde,valor_vermelho ):
                if valor == 'Meta Atingida':
                    color = '#ccffcc' #verde claro
                else:
                    if porcentagem_para_decimal(valor) >= valor_verde:
                        color = '#ccffcc'
                    elif porcentagem_para_decimal(valor) < valor_vermelho:
                        color = '#ffcccc' #vermelho claro
                    else: 
                        color = '#ffffcc'#amarelo claro

                return f'background-color: {color}'
            lista_ong = list(dic_abastecimento_ong_sku.keys())
            lista_ong.insert(0,"TODAS AS ONGs")
            option_1 = st.selectbox(
                "Selecione a ONG",
                lista_ong,
                index=None,
                placeholder="Selecione uma ong...",
                 key="opcao_1"
                )
            with col1:
                #st.header('VERDE')
                st.markdown("<h1 style='color: green;'>VERDE</h1>", unsafe_allow_html=True)
                valor_verde = st.number_input(f'Pintar de verde valores (>=):', value=1.0, key="input1")
            with col3:
                st.markdown("<h1 style='color: red;'>VERMELHO</h1>", unsafe_allow_html=True)
                valor_vermelho = st.number_input(f'Pintar de vermelho valores (<):', value=0.3, key="input3")
            with col2:
                 st.markdown("<h1 style='color: yellow;'>AMARELO</h1>", unsafe_allow_html=True)
                 #valor_amarelo = st.number_input(f'Pintar de verde valores maiores que (>=):', value=1.0, key="input2")
                 st.write(f'Pintar de amarelo valores (>=) {valor_vermelho} e (<=) {valor_verde}')


            colorir_parcial = partial(colorir_celula, valor_verde= float(valor_verde) ,valor_vermelho = float(valor_vermelho))
            st.write("Você selecionou:", option_1)
            if option_1 != None:
                if option_1 == "TODAS AS ONGs":
                    df_nivel_abastecimento_cor = df_nivel_abastecimento.style.applymap(colorir_parcial)
                    df_nivel_abastecimento_cor
                else: 
                    df_nivel_abastecimento = df_nivel_abastecimento.loc[[option_1]]
                
                    df_nivel_abastecimento_cor = df_nivel_abastecimento.style.applymap(colorir_parcial)
                    df_nivel_abastecimento_cor
        with tab5:
            df_estoque_neg = st.session_state.bases.get('df_estoque')

            # Filtragem e exibição do DataFrame
            df_filtrado = df_estoque_neg[df_estoque_neg['quantidade'] < 0][['cod_produto', 'quantidade']].set_index('cod_produto')
            df_filtrado = df_estoque[df_estoque['quantidade'] <0].groupby(['cod_produto','id_loja']).agg({'quantidade': 'sum'})
            # Exibir o DataFrame com ajuste de largura e altura
            st.dataframe(df_filtrado, width=800, height=600)
                # Criar um buffer de memória
            buffer_1 = io.BytesIO()
            
            # Salvar o DataFrame no buffer como um arquivo Excel
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_filtrado.to_excel(writer, sheet_name='Estoque Negativo', index=True)
            
            # Mover o cursor do buffer para o início
            buffer_1.seek(0)
            
            # Adicionar o botão de download
            st.download_button(
                label="Baixar SKUs com estoque negativo",
                data=buffer,
                file_name='estoque_negativo.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                key="download_button_1"
            )


            
