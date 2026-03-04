import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

st.title("NBA Data Test")

# Create API client
credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
client = bigquery.Client(credentials=credentials)

df = client.query("SELECT * FROM `nba_stats.player_season_stats` LIMIT 10").to_dataframe()

# Print results
st.dataframe(df)

# st.title("NBA Player Stats Analysis")

# client = bigquery.Client()

# # 選手名でフィルタリング
# player_name = st.selectbox("選手を選択", ["Stephen Curry", "LeBron James", "Kevin Durant"])

# query = f"""
#     SELECT SEASON_ID, PTS, AST, REB 
#     FROM `your-project.nba_stats.player_season_stats`
#     WHERE PLAYER_NAME = '{player_name}'
#     ORDER BY SEASON_ID
# """

# df = client.query(query).to_dataframe()

# # 可視化
# st.line_chart(df.set_index('SEASON_ID')[['PTS', 'AST', 'REB']])
# st.dataframe(df)