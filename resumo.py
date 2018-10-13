#!/Users/renantardelli/miniconda2/bin python
# -*- coding: utf-8 -*-

import datetime as dt
import pandas as pd
import numpy as np
import dateutil as du
import json

path = "/Users/renantardelli/Desktop/datasets/tesouro/"

### Web

valores_diarios = pd.read_csv(path + 'taxas_dia.csv', parse_dates = ['date', 'vencimento'], decimal = ',')

def ajusta_nome_titulo(strng):
    opcoes = {'Tesouro IPCA+': 'IPCA',
              'Tesouro IPCA+ com Juros Semestrais': 'IPCAJS',
              'Tesouro Prefixado': 'PRE',
              'Tesouro Prefixado com Juros Semestrais': 'PREJS',
              'Tesouro Selic': 'SELIC',
              'Tesouro IGPM+ com Juros Semestrais': 'IGPMJS'}
    return opcoes[strng]

# Criando colunas para usar nos cáculos
valores_diarios.loc[:, 'titulo'] = valores_diarios.titulo.map(lambda x: ajusta_nome_titulo(x[:-5]))
valores_diarios.loc[:, 'ano'] = valores_diarios.vencimento.map(lambda x: str(x.year))
valores_diarios.loc[:, 'data_base'] = valores_diarios.date.map(lambda x: x.strftime("%d/%m/%Y"))
# Corrigindo para numerico
valores_diarios.loc[:, 'preco_unitario'] = pd.to_numeric(valores_diarios.preco_unitario)
valores_diarios.loc[:, 'taxas_dia'] = pd.to_numeric(valores_diarios.taxas_dia)

### Hist

historico = pd.read_csv(path + 'taxas.csv', sep=";", decimal=',')

historico.columns = ['tipo_titulo','data_vencimento','data_base','taxa_compra_manha', 'taxa_venda_manha', 'pu_compra_manha', 'pu_venda_manha', 'pu_base_manha']

historico.loc[:, 'date'] = historico['data_vencimento'].map(lambda x: dt.datetime.strptime(x, "%d/%m/%Y"))
historico.loc[:, 'ano'] = historico.date.map(lambda x: str(x.year))
historico.loc[:, 'base'] = historico['data_base'].map(du.parser.parse)
historico.loc[:, 'titulo'] = historico['tipo_titulo'].map(ajusta_nome_titulo)
historico.sort_values('base', inplace=True)


### Funcoes mat financeira

def anualiza_taxa(i, dias):
    return (1+i)**(250./dias) - 1

### Funcoes

def nome_para_dict(titulo):
    titulo,ano = titulo.split("_")
    return {'ano':ano, 'titulo':titulo}

def vlookup(df=historico, titulo=None, **kwargs):
    try :
        kwargs.update(nome_para_dict(titulo))
    except : 
        pass

    if kwargs['data_base'] == 'max': kwargs['data_base'] = max(df['data_base'])

    param = pd.DataFrame(kwargs, index=[0])

    return df.merge(param)

def simulacao_venda(titulo, data_base, data_venda='max'):
    compra = vlookup(data_base=data_base, titulo=titulo)
    venda = vlookup(df=valores_diarios, data_base=data_venda, titulo=titulo)

    dias = (venda.date - compra.base).dt.days # no historico BASE é a data do dia

    dif_pu = venda.preco_unitario - compra.pu_base_manha
    dif_taxa = venda.taxas_dia - compra.taxa_venda_manha

    juros = (venda.preco_unitario / compra.pu_base_manha) - 1
    juros_anualizados = anualiza_taxa(juros, dias)

    return np.hstack([dias, dif_pu, dif_taxa, juros, juros_anualizados])

def valor_teorico(pu, taxa, data_base, data_venda='max'):
    # Assumindo que é composto diariamente
    inicio = du.parser.parse(inicio)
    fim = du.parser.parse(fim)
    ts = np.cumprod(np.repeat(1+taxa, (fim-inicio).days)) * pu
    return ts

def mostra_resultados(titulo, data_base):
    venda = simulacao_venda(titulo=titulo, data_base=data_base)
    print titulo
    print "Número de dias: %s" %(venda[0])
    print "Ganho em valores absolutos: %.2f" %(venda[1])
    print "Juros no período: %.2f " %(venda[3]*100)
    print "Juros anualizados: %.2f " %(venda[4]*100)
    print "-------------------------------------"

#### TESTES

# tit = "PRE_2023"
# dat = '27/07/2017'

# compra = vlookup(data_base=dat, titulo=tit)
# venda = vlookup(df=valores_diarios, data_base=dat, titulo=tit)

# simulacao_venda(tit, dat)

###

with open('input.json', 'r') as rf:
    posicao = json.load(rf)

for tit in range(len(posicao)):
    mostra_resultados(posicao[tit]['titulo'], posicao[tit]['data'])
