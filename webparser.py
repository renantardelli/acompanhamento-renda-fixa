import urllib2
from bs4 import BeautifulSoup
import pandas as pd
import dateutil as du

print '-----'
print 'Atualizando dados diarios\n'

url = 'http://www.tesouro.fazenda.gov.br/tesouro-direto-precos-e-taxas-dos-titulos'
page = urllib2.urlopen(url)
soup = BeautifulSoup(page, 'html.parser')

tabelas = soup.find_all('table')
soup_taxas_dia = tabelas[1].prettify()

df_taxas_dia = pd.read_html(soup_taxas_dia, header=0, skiprows=1)[0].dropna(how='any')
df_taxas_dia.columns = ['titulo', 'vencimento', 'taxas_dia', 'valor_minimo', 'preco_unitario']

def monetary_to_float(strng):
	return float(strng.replace("R$", "").replace(".", "").replace(",", "."))

def fix_interest(float):
	return float/100

df_taxas_dia.loc[:, 'preco_unitario'] = df_taxas_dia.preco_unitario.map(monetary_to_float)
df_taxas_dia.loc[:, 'valor_minimo'] = df_taxas_dia.valor_minimo.map(monetary_to_float) 
df_taxas_dia.loc[:, 'taxas_dia'] = df_taxas_dia.taxas_dia.map(fix_interest) 
df_taxas_dia.loc[:, 'vencimento'] = df_taxas_dia.vencimento.map(du.parser.parse)

print "Data base: "

df_taxas_dia.to_csv('/Users/renantardelli/Desktop/datasets/taxas_dia.csv', index=False)