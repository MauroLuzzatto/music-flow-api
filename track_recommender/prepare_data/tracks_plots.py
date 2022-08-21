import pandas as pd
import plotly.express as px

df_artists = pd.read_csv("df_artists.csv").sort_values("counts", ascending=False)


fig = px.bar(df_artists, x="artistName", y="counts", height=400)
fig.show()
