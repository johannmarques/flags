import sidrapy
import pandas as pd
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud, ImageColorGenerator
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt


brasil = sidrapy.get_table(table_code="4709", territorial_level="1", ibge_territorial_code="all", period="2022")
data = sidrapy.get_table(table_code="4709", territorial_level="6", ibge_territorial_code="all", period="2022")

def first_as_collum(df):
    df.columns = df.iloc[0]
    df = df[1:]
    df = df.reset_index(drop=True)
    return df

brasil = first_as_collum(brasil)
brasil = brasil[brasil['Variável'] == 'População residente']

data = first_as_collum(data)
data = data[data['Variável'] == 'População residente']

# Domain table

states_domain = pd.read_csv('https://raw.githubusercontent.com/leogermani/estados-e-municipios-ibge/'
                            'ef495ad10360fd9cd5f5ccfbb7db170a9fb411b0/estados.csv')
data['COD'] = [int(muni[:2]) for muni in data['Município (Código)']]

# Merge - State name
data = data.merge(states_domain, on='COD', how='left')

# Scrap flags
response = requests.get("https://www.infoescola.com/geografia/estados-do-brasil/")
contents = BeautifulSoup(response.content).find('article')
len(contents.find_all('img')[2:]) # There're more entries than states (Brazil has 27)

images = contents.find_all('img')[2:] # All images
sources = [row['src'] for row in images]
# keep only if it contains the word upload
len(list(filter(lambda row: 'bandeira' in row, sources)))

# Finally, all flags!
sources = list(filter(lambda row: 'bandeira' in row, sources))

# Now I need state names
len(contents.find_all('h2')[1:]) # 27 states!

states = contents.find_all('h2')[1:]
states = [state.text[:-5] for state in states]

# Dict containing pairs: states and its respective flags
states_flags = {states[ii] : sources[ii] for ii in range(len(states))}

def generate_state(data, state) : # Function that generates wordcloud for each state
    print('Gerando para {}'.format(state))
    filtered = data[data['NOME'] == state][['Município', 'Valor']] # Current state

    # Lists containing municipalities names and population
    muni_name = [muni[:-5] for muni in filtered['Município']]
    valor = [int(muni) for muni in filtered['Valor']]
    # Into dict
    dicio = dict(zip(muni_name, valor))

    # Mask based on current state flag
    mask = np.array(Image.open(requests.get(states_flags[state], stream=True).raw))
    wc = WordCloud(background_color="white",
                   mask = mask, random_state = 3)
    wc.generate_from_frequencies(dicio)

    # Colors
    image_colors = ImageColorGenerator(mask)
    plt.figure(figsize=[7,7])
    plt.imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
    plt.axis("off")
    wc.to_file('figures/'+state+'.png')
    #plt.show()

for state in states :
    generate_state(data, state)

# Now for Brazil:
data_dict = dict(zip([muni[:-5] for muni in data['Município']],
                     [int(muni) for muni in data['Valor']]))

mask = np.array(Image.open(
    requests.get('https://www.gov.br/planalto/pt-br/conheca-a-presidencia/acervo/simbolos-nacionais/bandeira/'
                 'bandeiranacionalbrasil_.jpg', stream=True).raw))
    wc = WordCloud(background_color="white",
                   mask = mask, random_state = 3)
    wc.generate_from_frequencies(data_dict)

    image_colors = ImageColorGenerator(mask)
    plt.figure(figsize=[7,7])
    plt.imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
    plt.axis("off")
    wc.to_file('figures/brasil.png')