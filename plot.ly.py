import plotly.plotly as py
import pandas as pd

#This reads the output csv file. 
df = pd.read_csv('poverty_agencies.csv')


for col in df.columns:
    df[col] = df[col].astype(str)

scl = [[0.0, 'rgb(242,240,247)'], [0.2, 'rgb(218,218,235)'], [0.4, 'rgb(188,189,220)'], \
       [0.6, 'rgb(158,154,200)'], [0.8, 'rgb(117,107,177)'], [1.0, 'rgb(84,39,143)']]
# scl ==> color scale in appropriate proportion.   

df['text'] = 'State: ' + df['state_name'] + '<br>' + \
             'Number of Agencies: ' + df['number_of_agencies'] + '<br>' + \
             'Poverty Rate: ' + df['poverty_rate'] + '<br>' + \
             'State FIPS Code: ' + df['fips_code']

# df['text'] defines what data should be displayed on the map. 

data = [dict(
    type='choropleth',
    colorscale=scl, 
    autocolorscale=False,
    locations=df['state_abbr'],   # This sets the coordinates via location IDs or names, depending on the locationmode. 
    z=df['poverty_rate'].astype(float), # This code turns the poverty rate into float number and sets the poverty rate as the color scale values for the map.
    locationmode='USA-states', #The choropleth map shows the United States. 
    text=df['text'], #What the display text should show, when hovered over each state. This was taken from the previous code block. 
    marker=dict( # marker input designs the boundaries between the states on the map. 
        line=dict(
            color='rgb(255,255,255)',
            width=2
        )),


    colorbar=dict(
        title="Poverty Rate in %") #This sets the title of the color bar, which depicts the color scale for each state. 
)]

layout = dict(
    title='Poverty Rate and the Presence of Human Trafficking Participating Agencies by State<br>(Hover for breakdown)', #This sets the title of the choropleth map.
    geo=dict(
        scope='usa',
        projection=dict(type='albers usa'),
        showlakes=True,
        lakecolor='rgb(255, 255, 255)'),
) #Geo input sets the layout and the design of the map. 

fig = dict(data=data, layout=layout)
py.iplot(fig, filename='d3-cloropleth-map')