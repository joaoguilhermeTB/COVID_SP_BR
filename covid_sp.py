#Importando bibliotecas utilizadas
import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar

pd.options.display.max_rows = 999

###Abrindo arquivo atualizado do github 
#url = 'https://raw.githubusercontent.com/seade-R/dados-covid-sp/master/data/dados_covid_sp.csv'

#df = pd.read_csv(url, sep=';')

#print(df)

#df.to_csv('C:\\Users\\JoãoGuilherme\\Desktop\\PYTHON\\COVID_SP\\dados.csv')


###Abrindo arquivo já salvo, não atualizado para salvar um tempo 

df = pd.read_csv('C:\\Users\\JoãoGuilherme\\Desktop\\PYTHON\\COVID_SP\\dados.csv', sep=',')

###Removendo coluna não desejada

df = df.drop('Unnamed: 0', axis=1)

#print(df)

###Transformando a coluna código_ibge em strain para mais tarde fazer o merge com geopandas
df['codigo_ibge'] = df['codigo_ibge'].astype(str)
#print(df)

####Transformando a variável 'datahora' em datetime...

df['datahora'] = df['datahora'].apply(lambda x: dt.datetime.strptime(x,'%Y-%m-%d'))

### Loop para trabalhar com os dados da média dos municípios do estado de SP ao longo do tempo

lista_dias = df['datahora'].unique()
lista_frames = []

semana = 0
dias = 0
count = 0

lista_medias_SP = []
lista_semanas = []

for i in lista_dias:
	#print(i)
	count = count + 1
	df_temp = df.loc[df['datahora'] == i,]
	df_temp = df_temp[['nome_munic','codigo_ibge','pop','casos_novos']]
	df_temp.set_index('nome_munic',inplace=True)

	###Limpando os "municípios" Ignorado

	sh = df_temp.shape
	if sh[0] == 646:
		df_temp.drop('Ignorado', axis=0, inplace = True)

	lista_frames.append(df_temp)
	
	if count == 7:
		semana = semana + 1
		count = 0
		nc = 0
		for frame in lista_frames:
			if nc == 0:
				temp_frame = frame
			else:
				temp_frame['casos_novos' + ' ' + str(nc)] = frame['casos_novos']
			nc = nc + 1

		lista_frames = []		

		media_semanal_pop_SP = ((temp_frame['casos_novos'].sum() 
			+ temp_frame['casos_novos 1'].sum() + temp_frame['casos_novos 2'].sum() 
			+ temp_frame['casos_novos 3'].sum() + temp_frame['casos_novos 4'].sum() 
			+ temp_frame['casos_novos 5'].sum() + temp_frame['casos_novos 6'].sum()) * 100000)/(temp_frame['pop'].sum())

		media_semanal_pop_SP = round(media_semanal_pop_SP,2)
		lista_medias_SP.append(media_semanal_pop_SP)
		lista_semanas.append(semana)
		#print('--------SEMANA--------', semana)
		#print(media_semanal_pop_SP)

		
		
#print(lista_medias_SP)
#print(lista_semanas)		


###Carregando arquivo shapefile na biblioteca geopandas
###Os arquivos shapefiles são fundamentais para a plotagem de mapas uma vez que eles detem
###informações geoespaciais à respeito dos territórios
cidades = gpd.read_file(r'C:\Users\JoãoGuilherme\Desktop\PYTHON\COVID_SP\shapefiles\Brasil\São Paulo_Municipios_2020\SP_Municipios_2020.shp')
cidades = cidades.set_index('CD_MUN')

###Lista para utilizar nas legendas do gráfico
meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul','Ago', 'Set', 'Out', 'Nov','Dez']

lista_nomes_ticks = ['Semana 1:\nFevereiro de\n2020','Semana 10:\nAbril de\n2020','Semana 20:\n Julho de\n2020',
    'Semana 30:\nSetembro de\n2020','Semana 40:\nNovembro de\n2020','Semana 50:\nFevereiro de\n2021',
    'Semana 60:\nAbril de\n2021','Semana 70:\nJunho de\n2021']
		
###Loop para trabalhar os dados da covid pelos municípios de SP ao longo do tempo

lll_dias = []

lista_frames = []
semana = 0
dias = 0
count = 0

for i in lista_dias:
	count = count + 1
	df_temp = df.loc[df['datahora'] == i,]
	df_temp = df_temp[['nome_munic','codigo_ibge','pop','casos_novos']]
	df_temp.set_index('nome_munic', inplace = True)

	###Limpando os "municípios" Ignorado
	sh = df_temp.shape
	if sh[0] == 646:
		df_temp.drop('Ignorado', axis=0, inplace = True)

	lista_frames.append(df_temp)
	lll_dias.append(i)
	#print(i)

	###Pegando a faixa da semana de 7 dias:
	if count == 7:		
		semana = semana + 1
		#print('---------semana{}---------'.format(semana))
		count = 0
		nc = 0 
		###Unindo os frames de cada dia da semana, em um único frame
		for frame in lista_frames:
			if nc == 0:
				temp_frame = frame
			else:
				temp_frame['casos_novos' + ' ' + str(nc)] = frame['casos_novos']
			nc = nc + 1

		###Pegando o primeiro e sétimo dia da semana para utilizar na legenda
		tempo1 = dt.datetime.utcfromtimestamp(lll_dias[0].tolist()/1e9)
		tempo2 = dt.datetime.utcfromtimestamp(lll_dias[6].tolist()/1e9)

		#print(semana)
		#print(lll_dias)

		lll_dias = []
		lista_frames = []

		###Somando os casos da semana por município dividido pela sua população em uma variável(NCS/100h)
		temp_frame['novos_semanal_pop'] = ((temp_frame['casos_novos'] + temp_frame['casos_novos 1'] 
			+ temp_frame['casos_novos 2'] + temp_frame['casos_novos 3'] + temp_frame['casos_novos 4'] 
			+ temp_frame['casos_novos 5'] + temp_frame['casos_novos 6']) * 100000)/(temp_frame['pop'])

		###Setando codigo_ibge de cada municipio como index do dataframe
		temp_frame.reset_index(inplace=True)
		temp_frame = temp_frame.set_index('codigo_ibge')
		#print('SEMANA', semana)
		#print(temp_frame['novos_semanal_pop'].describe())

		###Unindo os dados do covid com os geodados
		geodf = pd.merge(cidades,temp_frame,how='left',left_index=True,right_index=True)
		maximum = temp_frame['novos_semanal_pop'].max()

		###Criando figura matplotlib e subplots
		fig, (ax1,ax2) = plt.subplots(2,1,gridspec_kw={'height_ratios': [7, 1]})
		fig.set_size_inches(13.66,7.8)		
		divider = make_axes_locatable(ax1)
		cax = divider.append_axes("right", size="2%", pad=0.1)

		###Criando mapa com heatmap
		geodf.plot(ax= ax1, column='novos_semanal_pop', cmap='hot_r', vmin=0, vmax=1000,
		    edgecolor= '#000000', linewidth=0.1, legend= True, legend_kwds={'label':'NCS/100h por município'},cax=cax)

		###Criando gráfico de barras...
		ax2.bar(lista_semanas,lista_medias_SP,color='#b80000')


		ll2 = [1]
		for l in range(1,8):
			ll2.append(l*10)

		###Configurando cor de fundo dos gráficos
		ax1.set_facecolor('#bfbfbf')
		ax2.set_facecolor('#bfbfbf')
		###Linha vertical no gráfico de barras
		ax2.axvline(semana,color='black',linewidth=2)
		###Removendo marcações no eixos do mapa
		ax1.set_xticks(ticks=[])
		ax1.set_yticks(ticks=[])
		###Determinando características do gráfico de barras
		ax2.set_xlim(left=0,right=72)
		ax2.set_xticks(ticks= ll2)
		ax2.set_xticklabels(labels=lista_nomes_ticks)
		ax2.set_ylim(bottom=0,top=300)
		ax2.set_yticks(ticks=[0, 150, 300])
		ax2.set_ylabel('Média NCS/100h dos municípios')
		ax2.set_xlabel('Semana/Data')
		ax2.yaxis.set_label_position("right")
		ax2.yaxis.tick_right()
		###Adicionando informações extras à figura
		fig.suptitle('Novos casos semanais de COVID-19 no estado de São Paulo por município',size=18,fontstretch=100,fontstyle='oblique')
		fig.text(0.35,0.9,'Semana {} ({} de {} de {} à {} de {} de {})'.format(semana,tempo1.day,meses[(tempo1.month - 1)],
			tempo1.year,tempo2.day,meses[(tempo2.month - 1)],tempo2.year),size=12)
		fig.text(0.9,0.8,'NCS/100h=\nNovos casos semanais\npor 100 mil habitantes',size=10, backgroundcolor='#bfbfbf',ha='center')
		
		geodf_media = geodf['novos_semanal_pop']
		total = (geodf_media.shape)[0]

		def porcent(float_):
			porct = round((float_ * 100),2)
			return porct

		_200 = (geodf_media[geodf_media <= 200].count())/total
		_400 = ((geodf_media.between(200,400,inclusive='right')).sum())/total
		_600 = ((geodf_media.between(400,600,inclusive='right')).sum())/total
		_800 = ((geodf_media.between(600,800,inclusive='right')).sum())/total
		_1000 = ((geodf_media.between(800,1000,inclusive='right')).sum())/total
		_1001 = (geodf_media[geodf_media >= 1001].count())/total

		fig.text(0.23,0.3,'0 e 200 = {}%'.format(porcent(_200)),backgroundcolor='#ffffb3',ha='right')
		fig.text(0.23,0.335,'201 e 400 = {}%'.format(porcent(_400)),backgroundcolor='#ffb326',ha='right')
		fig.text(0.23,0.37,'401 e 600 = {}%'.format(porcent(_600)),backgroundcolor='#ff5500',ha='right')
		fig.text(0.23,0.405,'601 e 800 = {}%'.format(porcent(_800)),backgroundcolor='#de0000',ha='right')
		fig.text(0.23,0.44,'801 e 1000 = {}%'.format(porcent(_1000)),backgroundcolor='#380000',color='white',ha='right')
		fig.text(0.23,0.475,'> 1000 = {}%'.format(porcent(_1001)),backgroundcolor='#000000',color='white',ha='right')
		fig.text(0.23,0.51,'Percentual de cidades dentro \n do intervalo NCS/100h',backgroundcolor='#bfbfbf',ha='right')

		###Adicionando referência às principais cidades do estado
		
		#São Paulo
		ax1.plot(-46.68,-23.55,'*',c='white',markersize=9,alpha=1,fillstyle='none')
		ax1.plot(-46.68,-23.55,'*',c='black',markersize=13,alpha=1,fillstyle='none',label='São Paulo')

		#Santos
		ax1.plot(-46.335,-23.902,'v',c='white',markersize=4,alpha=1,fillstyle='none')
		ax1.plot(-46.335,-23.902,'v',c='black',markersize=6,alpha=1,fillstyle='none',label='Santos')

		#Ribeirão Preto
		ax1.plot(-47.833,-21.211,'o',c='white',markersize=4,alpha=1,fillstyle='none')
		ax1.plot(-47.833,-21.211,'o',c='black',markersize=6,alpha=1,fillstyle='none',label='Ribeirão Preto')

		#Presidente Prudente
		ax1.plot(-51.328,-21.986,'^',c='white',markersize=4,alpha=1,fillstyle='none')
		ax1.plot(-51.328,-21.986,'^',c='black',markersize=6,alpha=1,fillstyle='none',label='Presidente Prudente')

		#São José do Rio Preto
		ax1.plot(-49.363,-20.811,'s',c='white',markersize=5,alpha=1,fillstyle='none')
		ax1.plot(-49.363,-20.811,'s',c='black',markersize=6,alpha=1,fillstyle='none',label='São José do Rio Preto')

		#São José dos Campos
		ax1.plot(-45.937,-23.118,'p',c='white',markersize=5,alpha=1,fillstyle='none')
		ax1.plot(-45.937,-23.118,'p',c='black',markersize=6,alpha=1,fillstyle='none',label='São José dos Campos')

		#Campinas
		ax1.plot(-47.037,-22.874,'P',c='white',markersize=5,alpha=1,fillstyle='none')
		ax1.plot(-47.037,-22.874,'P',c='black',markersize=6,alpha=1,fillstyle='none',label='Campinas')

		#Bauru
		ax1.plot(-49.143,-22.246,'h',c='white',markersize=4,alpha=1,fillstyle='none')
		ax1.plot(-49.143,-22.246,'h',c='black',markersize=6,alpha=1,fillstyle='none',label='Bauru')

		#Itapetininga
		ax1.plot(-48.134,-23.640,'D',c='white',markersize=4,alpha=1,fillstyle='none')
		ax1.plot(-48.134,-23.640,'D',c='black',markersize=5,alpha=1,fillstyle='none',label='Itapetininga')

		ax1.legend(fontsize=7)

		###Adicionando seta para direção norte no mapa
		x, y, arrow_length = 0.92, 0.235, 0.1
		ax1.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),arrowprops=dict(facecolor='black', width=3, headwidth=10),
		    ha='center', va='center', fontsize=17, xycoords=ax1.transAxes)

		###Adicionando barra de escala do mapa
		bar = AnchoredSizeBar(ax1.transData, 1, '1:250000', 4, pad=0.5, borderpad=0.5,sep=3,size_vertical=0.1,label_top=True)
		ax1.add_artist(bar)

		###Salvando figuras em pasta		
		plt.savefig('C:\\Users\\JoãoGuilherme\\Desktop\\PYTHON\\COVID_SP\\figuras_covid\\{}'.format(semana))
		#plt.savefig('C:\\Users\\JoãoGuilherme\\Desktop\\PYTHON\\COVID_SP\\figuras_covid\\bla')
