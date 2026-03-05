import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd

st.set_page_config(page_title="Player Search", page_icon="🏀", layout="wide")

st.title("🏀 NBA Player Stats Search")

# Initialize BigQuery client
@st.cache_resource
def get_bigquery_client():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    return bigquery.Client(credentials=credentials)

client = get_bigquery_client()

# Get list of all players with optional filters
@st.cache_data(ttl=3600)
def get_all_players(team=None, season=None):
    conditions = []
    params = []

    if team and team != "All Teams":
        conditions.append("TEAM_ABBREVIATION = @team")
        params.append(bigquery.ScalarQueryParameter("team", "STRING", team))

    if season and season != "All Seasons":
        conditions.append("SEASON_ID = @season")
        params.append(bigquery.ScalarQueryParameter("season", "STRING", season))

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    query = f"""
        SELECT DISTINCT PLAYER_NAME
        FROM `nba_stats.player_season_stats`
        WHERE {where_clause}
        ORDER BY PLAYER_NAME
    """

    job_config = bigquery.QueryJobConfig(query_parameters=params)
    df = client.query(query, job_config=job_config).to_dataframe()
    return df['PLAYER_NAME'].tolist()

# Get list of all teams
@st.cache_data(ttl=3600)
def get_all_teams():
    query = """
        SELECT DISTINCT TEAM_ABBREVIATION
        FROM `nba_stats.player_season_stats`
        WHERE TEAM_ABBREVIATION IS NOT NULL
        ORDER BY TEAM_ABBREVIATION
    """
    df = client.query(query).to_dataframe()
    return ['All Teams'] + df['TEAM_ABBREVIATION'].tolist()

# Get list of all seasons
@st.cache_data(ttl=3600)
def get_all_seasons():
    query = """
        SELECT DISTINCT SEASON_ID
        FROM `nba_stats.player_season_stats`
        ORDER BY SEASON_ID DESC
    """
    df = client.query(query).to_dataframe()
    return ['All Seasons'] + df['SEASON_ID'].tolist()

# Get player statistics
@st.cache_data(ttl=600)
def get_player_stats(player_name):
    query = f"""
        SELECT
            SEASON_ID,
            TEAM_ABBREVIATION,
            AGE,
            GP,
            MIN,
            PTS,
            REB,
            AST,
            STL,
            BLK,
            FG_PCT,
            FG3_PCT,
            FT_PCT,
            FGM,
            FGA,
            FG3M,
            FG3A,
            FTM,
            FTA,
            OREB,
            DREB,
            TOV,
            PF
        FROM `nba_stats.player_season_stats`
        WHERE PLAYER_NAME = @player_name
        ORDER BY SEASON_ID
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("player_name", "STRING", player_name)
        ]
    )
    df = client.query(query, job_config=job_config).to_dataframe()
    return df

# Get filtered team/season statistics
@st.cache_data(ttl=600)
def get_filtered_stats(team=None, season=None):
    conditions = []
    params = []

    if team and team != "All Teams":
        conditions.append("TEAM_ABBREVIATION = @team")
        params.append(bigquery.ScalarQueryParameter("team", "STRING", team))

    if season and season != "All Seasons":
        conditions.append("SEASON_ID = @season")
        params.append(bigquery.ScalarQueryParameter("season", "STRING", season))

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    query = f"""
        SELECT
            PLAYER_NAME,
            SEASON_ID,
            TEAM_ABBREVIATION,
            AGE,
            GP,
            MIN,
            PTS,
            REB,
            AST,
            STL,
            BLK,
            FG_PCT,
            FG3_PCT,
            FT_PCT,
            FGM,
            FGA,
            FG3M,
            FG3A,
            FTM,
            FTA,
            OREB,
            DREB,
            TOV,
            PF
        FROM `nba_stats.player_season_stats`
        WHERE {where_clause}
        ORDER BY PTS DESC
    """

    job_config = bigquery.QueryJobConfig(query_parameters=params)
    df = client.query(query, job_config=job_config).to_dataframe()
    return df

try:
    # Get team and season lists
    with st.spinner('Loading filters...'):
        teams = get_all_teams()
        seasons = get_all_seasons()

    # Filter section at the top
    st.subheader("🔍 Search Filters")

    col1, col2 = st.columns(2)

    with col1:
        # Team filter
        selected_team = st.selectbox(
            "Filter by Team",
            options=teams,
            help="Filter players by team"
        )

    with col2:
        # Season filter
        selected_season = st.selectbox(
            "Filter by Season",
            options=seasons,
            help="Filter players by season"
        )

    # Get filtered player list
    with st.spinner('Loading player list...'):
        players = get_all_players(
            team=selected_team if selected_team != "All Teams" else None,
            season=selected_season if selected_season != "All Seasons" else None
        )

    if not players:
        st.warning("No players found matching the selected filters.")
        st.stop()

    st.info(f"Found {len(players)} players matching filters")

    # Show filtered stats if team or season is selected (not "All")
    show_filtered_view = (selected_team != "All Teams" or selected_season != "All Seasons")

    if show_filtered_view:
        # Get filtered stats
        with st.spinner('Loading filtered data...'):
            filtered_df = get_filtered_stats(
                team=selected_team if selected_team != "All Teams" else None,
                season=selected_season if selected_season != "All Seasons" else None
            )

        if not filtered_df.empty:
            # Display filter summary
            filter_desc = []
            if selected_team != "All Teams":
                filter_desc.append(f"Team: {selected_team}")
            if selected_season != "All Seasons":
                filter_desc.append(f"Season: {selected_season}")

            st.subheader(f"📊 Stats for {' | '.join(filter_desc)}")

            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Players", len(filtered_df))
            with col2:
                st.metric("Avg Points", f"{filtered_df['PTS'].mean():.1f}")
            with col3:
                st.metric("Avg Assists", f"{filtered_df['AST'].mean():.1f}")
            with col4:
                st.metric("Avg Rebounds", f"{filtered_df['REB'].mean():.1f}")

            # Top performers
            tab1, tab2 = st.tabs(["📊 Top Performers", "📈 Stats Distribution"])

            with tab1:
                col_a, col_b = st.columns(2)

                with col_a:
                    st.subheader("🏆 Top 10 Scorers")
                    top_scorers = filtered_df.nlargest(10, 'PTS')[['PLAYER_NAME', 'PTS', 'AST', 'REB', 'GP']].copy()
                    top_scorers.columns = ['Player', 'Points', 'Assists', 'Rebounds', 'Games']
                    st.dataframe(top_scorers, use_container_width=True, hide_index=True)

                with col_b:
                    st.subheader("🎯 Top 10 Assist Leaders")
                    top_assists = filtered_df.nlargest(10, 'AST')[['PLAYER_NAME', 'AST', 'PTS', 'REB', 'GP']].copy()
                    top_assists.columns = ['Player', 'Assists', 'Points', 'Rebounds', 'Games']
                    st.dataframe(top_assists, use_container_width=True, hide_index=True)

            with tab2:
                # Top 15 scorers bar chart
                st.subheader("Top 15 Scorers Comparison")
                top15 = filtered_df.nlargest(15, 'PTS')[['PLAYER_NAME', 'PTS']].copy()
                top15 = top15.set_index('PLAYER_NAME')
                st.bar_chart(top15, use_container_width=True, height=400)

            # Display full data table
            st.subheader("📋 All Players Data")
            display_cols = ['PLAYER_NAME', 'SEASON_ID', 'TEAM_ABBREVIATION', 'GP', 'MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'FG_PCT', 'FG3_PCT', 'FT_PCT']
            display_df = filtered_df[display_cols].copy()
            display_df.columns = ['Player', 'Season', 'Team', 'Games', 'Min', 'Points', 'Rebounds', 'Assists', 'Steals', 'Blocks', 'FG%', '3P%', 'FT%']

            st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)

            # CSV Download
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Full Data as CSV",
                data=csv,
                file_name=f"{'_'.join(filter_desc).replace(': ', '_').replace(' | ', '_')}_stats.csv",
                mime="text/csv",
            )

    # Player selection (optional)
    st.subheader("🔎 View Individual Player Details")
    selected_player = st.selectbox(
        "Select a player (optional - for detailed view)",
        options=players,
        index=None,
        placeholder="Type or select a player name..."
    )

    if selected_player:
        st.subheader(f"📊 {selected_player}'s Stats")

        # Get stats
        with st.spinner('Loading data...'):
            stats_df = get_player_stats(selected_player)

        if not stats_df.empty:
            # Apply season/team filters if selected
            if selected_season != "All Seasons":
                stats_df = stats_df[stats_df['SEASON_ID'] == selected_season]

            if selected_team != "All Teams":
                stats_df = stats_df[stats_df['TEAM_ABBREVIATION'] == selected_team]

            if stats_df.empty:
                st.warning(f"No data found for {selected_player} with the selected filters.")
                st.stop()

            # Summary information
            col1, col2, col3, col4 = st.columns(4)

            latest_season = stats_df.iloc[0]
            with col1:
                st.metric("Seasons", len(stats_df))
            with col2:
                st.metric("Latest Season", latest_season['SEASON_ID'])
            with col3:
                st.metric("Avg Points", f"{stats_df['PTS'].mean():.1f}")
            with col4:
                st.metric("Avg Assists", f"{stats_df['AST'].mean():.1f}")

            # Tabs for different views
            tab1, tab2, tab3 = st.tabs(["📈 Charts", "📋 Detailed Data", "🎯 Key Stats"])

            with tab1:
                st.subheader("Key Stats Trends by Season")

                # Points, Assists, Rebounds
                chart_data = stats_df[['SEASON_ID', 'PTS', 'AST', 'REB']].copy()
                chart_data = chart_data.set_index('SEASON_ID')

                st.line_chart(
                    chart_data,
                    use_container_width=True,
                    height=400
                )

                # Shooting Percentages
                st.subheader("Shooting Percentage Trends")
                shooting_data = stats_df[['SEASON_ID', 'FG_PCT', 'FG3_PCT', 'FT_PCT']].copy()
                shooting_data = shooting_data.set_index('SEASON_ID')
                shooting_data.columns = ['FG%', '3P%', 'FT%']

                st.line_chart(
                    shooting_data,
                    use_container_width=True,
                    height=300
                )

            with tab2:
                st.subheader("All Stats Data")
                st.dataframe(
                    stats_df,
                    use_container_width=True,
                    hide_index=True
                )

                # CSV Download
                csv = stats_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name=f"{selected_player}_stats.csv",
                    mime="text/csv",
                )

            with tab3:
                st.subheader("Key Stats Overview")

                # Career Averages
                st.write("**Career Averages**")
                career_avg = pd.DataFrame({
                    'Stat': ['Points', 'Assists', 'Rebounds', 'Steals', 'Blocks'],
                    'Average': [
                        f"{stats_df['PTS'].mean():.1f}",
                        f"{stats_df['AST'].mean():.1f}",
                        f"{stats_df['REB'].mean():.1f}",
                        f"{stats_df['STL'].mean():.1f}",
                        f"{stats_df['BLK'].mean():.1f}"
                    ]
                })
                st.table(career_avg)

                st.write("**Best Performances**")
                best_stats = pd.DataFrame({
                    'Stat': ['Highest Points', 'Highest Assists', 'Highest Rebounds'],
                    'Record': [
                        f"{stats_df['PTS'].max():.1f}",
                        f"{stats_df['AST'].max():.1f}",
                        f"{stats_df['REB'].max():.1f}"
                    ],
                    'Season': [
                        stats_df.loc[stats_df['PTS'].idxmax(), 'SEASON_ID'],
                        stats_df.loc[stats_df['AST'].idxmax(), 'SEASON_ID'],
                        stats_df.loc[stats_df['REB'].idxmax(), 'SEASON_ID']
                    ]
                })
                st.table(best_stats)
        else:
            st.warning("No data found.")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please check your BigQuery connection settings.")
