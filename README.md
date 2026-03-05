# 🏀 NBA Stats Analytics

A Streamlit application for analyzing and visualizing NBA player statistics stored in BigQuery

## 📋 Overview

This project is an application for visualizing and analyzing NBA player statistics data stored in Google BigQuery through an interactive web interface.

## ✨ Key Features

### 1. Player Search
- Search by player name and view career-wide statistics
- Visualize stats trends from past seasons with charts
- Detailed data including points, assists, rebounds, shooting percentages, etc.
- Display career averages and best performances
- Download data as CSV

### 2. Stats Rankings
- Display season-by-season stats rankings
- Support for multiple stats categories:
  - Points (PTS)
  - Assists (AST)
  - Rebounds (REB)
  - Steals (STL)
  - Blocks (BLK)
  - Shooting Percentages (FG%, 3P%, FT%)
  - 3-Pointers Made, Minutes Played, etc.
- Highlight top 3 players
- Filter by minimum games played
- Top 10 player comparison charts

### 3. Home Page
- Display database statistics
- View latest data samples

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Database**: Google BigQuery
- **Language**: Python 3.11+
- **Key Libraries**:
  - streamlit: Web application framework
  - google-cloud-bigquery: BigQuery client
  - pandas: Data analysis
  - altair: Data visualization

## 📦 Installation

### Prerequisites
- Python 3.11 or higher
- Google Cloud Platform account
- BigQuery access permissions

### Setup

1. Clone the repository
```bash
git clone <repository-url>
cd private-nba-analytics
```

2. Create and activate virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -e .
```

4. Configure BigQuery credentials

Create a `.streamlit/secrets.toml` file with your GCP service account information:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

## 🚀 Usage

1. Launch the application
```bash
streamlit run main.py
```

2. Access `http://localhost:8501` in your browser

3. Select features from the sidebar:
   - **Player Search**: Search for players and view their stats
   - **Rankings**: Display season-by-season rankings

## 📊 Data Structure

BigQuery table: `nba_stats.player_season_stats`

Key columns:
- `PLAYER_NAME`: Player name
- `SEASON_ID`: Season ID
- `TEAM_ABBREVIATION`: Team abbreviation
- `GP`: Games played
- `PTS`, `AST`, `REB`: Points, Assists, Rebounds
- `FG_PCT`, `FG3_PCT`, `FT_PCT`: Shooting percentages
- Many other stats

## 📁 Project Structure

```
private-nba-analytics/
├── main.py                      # Home page
├── pages/
│   ├── 1_player_search.py      # Player search page
│   └── 2_rankings.py           # Rankings page
├── .streamlit/
│   └── secrets.toml            # BigQuery credentials (gitignored)
├── pyproject.toml              # Project configuration
├── .gitignore
└── README.md
```

## 🔒 Security

- Store BigQuery credentials in `.streamlit/secrets.toml` and do not commit to Git
- Ensure `secrets.toml` is included in `.gitignore`

## 📝 License

This project is for personal use.

## 🤝 Contributing

Bug reports and feature requests are accepted via Issues.
