import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd

st.set_page_config(page_title="Stats Rankings", page_icon="🏆", layout="wide")

st.title("🏆 NBA Stats Rankings")

# Initialize BigQuery client
@st.cache_resource
def get_bigquery_client():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    return bigquery.Client(credentials=credentials)

client = get_bigquery_client()

# Get list of seasons
@st.cache_data(ttl=3600)
def get_seasons():
    query = """
        SELECT DISTINCT SEASON_ID
        FROM `nba_stats.player_season_stats`
        ORDER BY SEASON_ID DESC
    """
    df = client.query(query).to_dataframe()
    return df['SEASON_ID'].tolist()

# Get ranking data
@st.cache_data(ttl=600)
def get_rankings(season, stat, min_games=20, limit=50):
    query = f"""
        SELECT
            PLAYER_NAME,
            TEAM_ABBREVIATION,
            GP,
            {stat},
            CASE
                WHEN @stat = 'FG_PCT' OR @stat = 'FG3_PCT' OR @stat = 'FT_PCT' THEN {stat} * 100
                ELSE {stat}
            END as STAT_VALUE
        FROM `nba_stats.player_season_stats`
        WHERE SEASON_ID = @season
            AND GP >= @min_games
            AND {stat} IS NOT NULL
        ORDER BY {stat} DESC
        LIMIT @limit
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("season", "STRING", season),
            bigquery.ScalarQueryParameter("stat", "STRING", stat),
            bigquery.ScalarQueryParameter("min_games", "INT64", min_games),
            bigquery.ScalarQueryParameter("limit", "INT64", limit)
        ]
    )
    df = client.query(query, job_config=job_config).to_dataframe()
    return df

try:
    # Sidebar filter settings
    st.sidebar.header("Filter Settings")

    # Season selection
    seasons = get_seasons()
    selected_season = st.sidebar.selectbox(
        "Season",
        options=seasons,
        index=0
    )

    # Stats category selection
    stat_categories = {
        "Points (PTS)": "PTS",
        "Assists (AST)": "AST",
        "Rebounds (REB)": "REB",
        "Steals (STL)": "STL",
        "Blocks (BLK)": "BLK",
        "FG Percentage (FG%)": "FG_PCT",
        "3P Percentage (3P%)": "FG3_PCT",
        "FT Percentage (FT%)": "FT_PCT",
        "3-Pointers Made (3PM)": "FG3M",
        "Minutes Played (MIN)": "MIN"
    }

    selected_stat_name = st.sidebar.selectbox(
        "Stats Category",
        options=list(stat_categories.keys())
    )
    selected_stat = stat_categories[selected_stat_name]

    # Minimum games
    min_games = st.sidebar.slider(
        "Minimum Games",
        min_value=1,
        max_value=82,
        value=20,
        help="Only show players who played at least this many games"
    )

    # Display limit
    display_limit = st.sidebar.slider(
        "Display Limit",
        min_value=10,
        max_value=100,
        value=50,
        step=10
    )

    # Display rankings
    st.subheader(f"📊 {selected_season} Season - {selected_stat_name} Rankings")
    st.caption(f"Minimum games: {min_games} games")

    with st.spinner('Loading data...'):
        rankings_df = get_rankings(selected_season, selected_stat, min_games, display_limit)

    if not rankings_df.empty:
        # Display rankings
        display_df = rankings_df.copy()
        display_df.insert(0, 'Rank', range(1, len(display_df) + 1))

        # Rename columns to English
        display_df = display_df.rename(columns={
            'PLAYER_NAME': 'Player',
            'TEAM_ABBREVIATION': 'Team',
            'GP': 'Games',
            selected_stat: selected_stat_name.split('(')[0].strip()
        })

        # Format percentage stats
        if selected_stat in ['FG_PCT', 'FG3_PCT', 'FT_PCT']:
            display_df[selected_stat_name.split('(')[0].strip()] = display_df[selected_stat_name.split('(')[0].strip()].apply(lambda x: f"{x:.1%}")

        # Remove STAT_VALUE column (for display)
        if 'STAT_VALUE' in display_df.columns:
            display_df = display_df.drop('STAT_VALUE', axis=1)

        # Highlight top 3
        def highlight_top3(row):
            if row['Rank'] == 1:
                return ['background-color: #FFD700; font-weight: bold'] * len(row)  # Gold
            elif row['Rank'] == 2:
                return ['background-color: #C0C0C0; font-weight: bold'] * len(row)  # Silver
            elif row['Rank'] == 3:
                return ['background-color: #CD7F32; font-weight: bold'] * len(row)  # Bronze
            else:
                return [''] * len(row)

        st.dataframe(
            display_df.style.apply(highlight_top3, axis=1),
            use_container_width=True,
            hide_index=True,
            height=600
        )

    else:
        st.warning("No data found matching the criteria.")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please check your BigQuery connection settings.")
