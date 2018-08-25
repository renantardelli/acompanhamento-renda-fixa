#!/Users/renantardelli/miniconda2/bin python

import datetime as dt
import pandas as pd
import numpy as np
import dateutil as du
import json

path = "/Users/renantardelli/Desktop/datasets/tesouro/"

### Web

valores_diarios = pd.read_csv(path + 'taxas_dia.csv', parse_dates = ['date', 'vencimento'])

hoje = dt.datetime.strftime(dt.datetime.today(), "%d/%m/%Y")

def ajusta_nome_titulo(strng):
	opcoes = {'Tesouro IPCA+': 'IPCA',
	 		  'Tesouro IPCA+ com Juros Semestrais': 'IPCAJS',
	 		  'Tesouro Prefixado': 'PRE',
	 		  'Tesouro Prefixado com Juros Semestrais': 'PREJS',
	 		  'Tesouro Selic': 'SELIC',
	 		  'Tesouro IGPM+ com Juros Semestrais': 'IGPMJS'}
	return opcoes[strng]

valores_diarios.loc[:, 'titulo'] = valores_diarios.titulo.map(lambda x: ajusta_nome_titulo(x[:-5]))
valores_diarios.loc[:, 'ano'] = valores_diarios.vencimento.map(lambda x: str(x.year))

### Hist

historico = pd.read_csv(path + 'taxas.csv', sep=";")

historico.loc[:, 'date'] = historico['Data Vencimento'].map(lambda x: dt.datetime.strptime(x, "%d/%m/%Y"))
historico.loc[:, 'ano'] = historico.date.map(lambda x: str(x.year))
historico.loc[:, 'base'] = historico['Data Base'].map(du.parser.parse)
historico.loc[:, 'titulo'] = historico['Tipo Titulo'].map(ajusta_nome_titulo)
historico.sort_values('base', inplace=True)



### Funções mat financeira

def anualiza_taxa(i, dias):
	return (1+i)**(250./dias) - 1

### Cálculos


def dados_hist(titulo, date=None):
	# date = du.parser.parse(date)
	titulo,ano = titulo.split("_")
	df = historico[(historico.titulo == titulo) & (historico['Data Base'] == date) & (historico.ano == ano)]
	return dict(df)

def dados_dia(titulo):
	# date = du.parser.parse(date)
	titulo,ano = titulo.split("_")
	df = valores_diarios[(valores_diarios.titulo == titulo) & (valores_diarios.ano == ano)]
	return dict(df)


dat = "31/12/2015"
tit = 'IPCAJS_2050'
a = dados_hist(tit, dat)
b= dados_dia(tit)

def ganho(titulo, data_compra):
	compra = dados_hist(titulo, date=data_compra)
	venda = dados_dia(titulo)

	dias = (compra['date'].iloc[0] - venda['date'].iloc[0]).days
	dif_pu = venda['preco_unitario'].iloc[0] - float(compra['PU Base Manha'].iloc[0].replace(",", "."))
	juros = (venda['preco_unitario'].iloc[0] / float(compra['PU Base Manha'].iloc[0].replace(",", "."))) - 1
	juros_anualizados = anualiza_taxa(juros, dias)
	return dif_pu, dias, juros, juros_anualizados

print ganho(tit, dat)

def valor_teorico(pu, taxa, inicio, fim=dt.datetime.today()):
	# Assumindo que é composto diariamente
	inicio = du.parser.parse(inicio)
	fim = du.parser.parse(fim)
	ts = np.cumprod(np.repeat(1+taxa, (fim-inicio).days)) * pu
 	return ts





