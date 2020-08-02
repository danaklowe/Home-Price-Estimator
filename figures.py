# Builds the figures to be used by dash in app.py

import pandas as pd
import plotly.graph_objects as go

# Loads raw csv data on home sales into a pandas dataframe
df = pd.read_csv('data/kc_house_data.csv', parse_dates=['date'])

# Figure 1 - Histogram of home sale volume
fig1 = go.Figure(data=[go.Histogram(x=df['date'], xbins=dict(start='2014-05-02', end='2015-05-14', size='D1'))])
fig1.update_layout(
                   title='Daily Home Sales Volume',
                   plot_bgcolor='rgb(230, 230, 230)',
                   showlegend=False,
                   xaxis_title='Date',
                   yaxis_title='Daily Sales Volume'
                   )

# Figure 2 - Scatter plot of living area vs. sale price
fig2 = go.Figure(data=go.Scatter(x=df['sqft_living'], y=df['price'], mode='markers',
                                 marker=dict(size=16, color='forestgreen', line_width=1)))
fig2.update_layout(title='Home Living Area size (excluding basement) vs. Sale Price',
                   plot_bgcolor='rgb(230, 230, 230)',
                   showlegend=False,
                   xaxis=dict(range=[0, 10000]),
                   yaxis=dict(range=[0, 6000000]),
                   xaxis_title='Living area (in sqft)',
                   yaxis_title='Sale Price (in USD)',
                   )

# drops extraneous column(s) from the original dataframe
df_corr = df.drop(['id'], axis=1)


fig3 = go.Figure(data=go.Heatmap(z=df_corr.corr(),
                                 x=df.columns[2:],
                                 y=df.columns[2:],
                                 colorscale='magma'
                                 ))
fig3.update_layout(title='Relation between Home Features',
                   yaxis=dict(tickmode='linear'))
fig3.update_yaxes(autorange='reversed',
                  automargin=True)


df_t = df.head(50)

fig4 = go.Figure(data=[go.Table(
    header=dict(values=df_t.columns,
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[df_t.id, df_t.date, df_t.price, df_t.bedrooms, df_t.bathrooms, df_t.sqft_living, df_t.sqft_lot,
                       df_t.floors, df_t.waterfront, df_t.view, df_t.condition, df_t.grade, df_t.sqft_above,
                       df_t.sqft_basement, df_t.yr_built, df_t.yr_renovated, df_t.zipcode, df_t.lat, df_t.long,
                       df_t.sqft_living15, df_t.sqft_lot15],
               fill_color='lavender',
               align='left')
)])

fig4.update_layout(title='Raw Dataset of Home Sales in King County (first 50 sales)',
                   xaxis=dict(rangeslider=dict(visible=True),
                              type="linear"))
