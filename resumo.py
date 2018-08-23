#!/Users/renantardelli/miniconda2/bin python

import datetime as dt
import pandas as pd
import numpy as np
import dateutil as du
import json

path = "/Users/renantardelli/Desktop/datasets/tesouro/"

with open(path + 'correspondencia.json', 'r') as rf:
	ref = json.load(rf)

operacoes = pd.read_csv(path + 'operacoes.csv', dtype={'titulo':str}).dropna()

## Calcular a posição com o passar do tempo

operacoes.loc[:, 'nome_titulo'] = operacoes.titulo.map(lambda x: ref[x])

valores_diarios = pd.read_csv(path + 'taxas_dia.csv')

def valor_teorico(pu, taxa, inicio, fim=dt.datetime.today()):
	# Assumindo que é composto diariamente
	inicio = du.parser.parse(inicio)
	fim = du.parser.parse(fim)
	ts = np.cumprod(np.repeat(1+taxa, (fim-inicio).days)) * pu
	return ts

