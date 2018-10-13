#!/Users/renantardelli/miniconda2/bin python

import urllib2
from bs4 import BeautifulSoup
import pandas as pd
import dateutil as du
import datetime as dt

print '-----'
print 'Atualizando dados diarios\n'

url = 'http://www.tesouro.fazenda.gov.br/tesouro-direto-precos-e-taxas-dos-titulos'
page = urllib2.urlopen(url)
soup = BeautifulSoup(page, 'html.parser')

tabelas = soup.find_all('table')
soup_taxas_dia = tabelas[3].prettify()

df_taxas_dia = pd.read_html(soup_taxas_dia, header=0, skiprows=1)[0].dropna(how='any')

df_taxas_dia.columns = ['titulo', 'vencimento', 'taxas_dia', 'preco_unitario']

def monetary_to_float(strng):
	return float(strng.replace("R$", "").replace(".", "").replace(",", "."))

def fix_interest(float):
	return float/100

df_taxas_dia.loc[:, 'preco_unitario'] = df_taxas_dia.preco_unitario.map(monetary_to_float)
# df_taxas_dia.loc[:, 'valor_minimo'] = df_taxas_dia.valor_minimo.map(monetary_to_float) 
df_taxas_dia.loc[:, 'taxas_dia'] = df_taxas_dia.taxas_dia.map(fix_interest) 
df_taxas_dia.loc[:, 'vencimento'] = df_taxas_dia.vencimento.map(du.parser.parse)
df_taxas_dia.loc[:, 'date'] = dt.datetime.today().replace(hour=0, minute= 0, second=0, microsecond=0)


print "Data base: " 


path = "/Users/renantardelli/Desktop/datasets/tesouro/"

df_taxas_dia.to_csv(path + '/taxas_dia.csv', index=False)

#p_p_id_precosetaxas_WAR_tesourodiretoportlet_ > div > div > div > b