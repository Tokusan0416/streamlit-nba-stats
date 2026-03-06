import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

st.set_page_config(
    page_title="NBA Stats Analytics",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏀 NBA Stats Analytics")

st.markdown("""
## Welcome!

This application allows you to analyze and visualize NBA player statistics stored in BigQuery.

### Features

- **🔍 Player Search**: Search by player name and view detailed stats from past seasons
- **🏆 Rankings**: Display season-by-season and category-based stats rankings

### How to Use

Select the desired feature from the left sidebar.

1. **Player Search**: Search for players and view their career stats trends
2. **Rankings**: Select a season and stats category to compare top players

---
""")

# Initialize BigQuery client
@st.cache_resource
def get_bigquery_client():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    return bigquery.Client(credentials=credentials)

# Display database statistics
st.subheader("📊 Database Statistics")

try:
    client = get_bigquery_client()

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.spinner(''):
            total_players = client.query(
                "SELECT COUNT(DISTINCT PLAYER_NAME) as count FROM `nba_stats.fact_player_season_stats`"
            ).to_dataframe()
            st.metric("Total Players", f"{total_players['count'].iloc[0]:,}")

    with col2:
        with st.spinner(''):
            total_seasons = client.query(
                "SELECT COUNT(DISTINCT SEASON) as count FROM `nba_stats.fact_player_season_stats`"
            ).to_dataframe()
            st.metric("Total Seasons", f"{total_seasons['count'].iloc[0]:,}")

    with col3:
        with st.spinner(''):
            total_records = client.query(
                "SELECT COUNT(*) as count FROM `nba_stats.fact_player_season_stats`"
            ).to_dataframe()
            st.metric("Total Records", f"{total_records['count'].iloc[0]:,}")

    # Latest data sample
    st.subheader("📋 Latest Data Sample")

    sample_query = """
        SELECT
            PLAYER_NAME,
            SEASON,
            TEAM_ABBREVIATION,
            GP,
            PTS,
            AST,
            REB
        FROM `nba_stats.fact_player_season_stats`
        ORDER BY SEASON DESC
        LIMIT 10
    """

    sample_df = client.query(sample_query).to_dataframe()
    sample_df.columns = ['Player', 'Season', 'Team', 'Games', 'Points', 'Assists', 'Rebounds']

    st.dataframe(
        sample_df,
        use_container_width=True,
        hide_index=True
    )

except Exception as e:
    st.error(f"Database connection error: {str(e)}")
    st.info("Please check your BigQuery connection settings.")

st.markdown("""
---
### Data Source

- BigQuery Dataset: `nba_stats.fact_player_season_stats`
- Data is updated regularly
""")