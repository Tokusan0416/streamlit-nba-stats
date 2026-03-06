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

BigQuery table: `nba_stats.fact_player_season_stats`

Key columns:
- `PLAYER_NAME`: Player name
- `SEASON`: Season ID
- `TEAM_ABBREVIATION`: Team abbreviation
- `GP`: Games played
- `PTS`, `AST`, `REB`: Points, Assists, Rebounds
- `FG_PCT`, `FG3_PCT`, `FT_PCT`: Shooting percentages
- Many other stats

## 🔄 Data Pipeline

The project includes a modular data pipeline for fetching NBA statistics from the NBA API and loading them into BigQuery.

### Pipeline Components

- **extractors/**: Extract data from NBA API endpoints
- **loaders/**: Load data into BigQuery
- **utils/**: Utility functions (season generation, etc.)
- **jobs/**: Executable scripts for data operations

### Configuration

Configure the pipeline via environment variables or edit `scripts/data_pipeline/config.py`:

```bash
# Optional: Override default settings
export GCP_PROJECT_ID="your-project-id"
export HISTORICAL_START_YEAR="1997"
export CURRENT_YEAR="2025"
```

### Usage

#### 1. Backfill Historical Data

Fetch and load all historical player statistics (one-time operation):

```bash
cd scripts/data_pipeline/jobs

# Backfill all seasons (1997-2025)
python backfill_player_stats.py

# Backfill specific year range
python backfill_player_stats.py --start-year 2020 --end-year 2023

# Dry run (fetch but don't load to BigQuery)
python backfill_player_stats.py --dry-run
```

#### 2. Update Current Season

Update the current season's statistics (for scheduled/periodic execution):

```bash
cd scripts/data_pipeline/jobs

# Update current season (auto-detected)
python update_current_season.py

# Update specific season
python update_current_season.py --season 2024-25

# Dry run
python update_current_season.py --dry-run
```

#### 3. Scheduled Updates

For automated updates, set up a cron job or scheduled task:

```bash
# Example cron job (daily at 6 AM)
0 6 * * * cd /path/to/private-nba-analytics/scripts/data_pipeline/jobs && python update_current_season.py
```

### Pipeline Features

- **Rate Limiting**: Automatic rate limiting to respect NBA API limits
- **Error Handling**: Continues processing on individual failures
- **Upsert Support**: Prevents duplicate data for the same season
- **Logging**: Comprehensive logging to both console and file
- **Dry Run Mode**: Test data fetching without modifying BigQuery

## 📁 Project Structure

```
private-nba-analytics/
├── main.py                      # Home page
├── pages/
│   ├── 1_player_search.py      # Player search page
│   └── 2_rankings.py           # Rankings page
├── scripts/
│   └── data_pipeline/          # Data pipeline for fetching NBA stats
│       ├── config.py           # Configuration settings
│       ├── client.py           # BigQuery client management
│       ├── utils/              # Utility functions
│       │   └── season_generator.py
│       ├── extractors/         # Data extraction from APIs
│       │   └── player_stats.py
│       ├── loaders/            # Data loading to BigQuery
│       │   └── bigquery_loader.py
│       └── jobs/               # Executable scripts
│           ├── backfill_player_stats.py     # Backfill historical data
│           └── update_current_season.py     # Update current season
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

---

# 日本語版 / Japanese Version

## 🏀 NBA Stats Analytics

BigQueryに格納されたNBAの個人スタッツを分析・可視化するStreamlitアプリケーション

## 📋 概要

このプロジェクトは、Google BigQueryに保存されたNBAの選手スタッツデータを、インタラクティブなWebインターフェースで可視化・分析するためのアプリケーションです。

## ✨ 主な機能

### 1. 選手検索
- 選手名で検索し、キャリア全体のスタッツを確認
- 過去シーズンのスタッツ推移をグラフで可視化
- 得点、アシスト、リバウンド、シュート成功率などの詳細データ
- キャリア平均と最高記録の表示
- CSVでのデータダウンロード

### 2. スタッツランキング
- シーズン別のスタッツランキング表示
- 複数のスタッツカテゴリーに対応：
  - 得点 (PTS)
  - アシスト (AST)
  - リバウンド (REB)
  - スティール (STL)
  - ブロック (BLK)
  - シュート成功率 (FG%, 3P%, FT%)
  - 3Pシュート成功数、出場時間など
- トップ3選手のハイライト表示
- 最小試合数によるフィルタリング
- トップ10選手の比較グラフ

### 3. ホームページ
- データベース統計情報の表示
- 最新データサンプルの閲覧

## 🛠️ 技術スタック

- **フロントエンド**: Streamlit
- **データベース**: Google BigQuery
- **言語**: Python 3.11+
- **主要ライブラリ**:
  - streamlit: Webアプリケーションフレームワーク
  - google-cloud-bigquery: BigQueryクライアント
  - pandas: データ分析
  - altair: データ可視化

## 📦 インストール

### 前提条件
- Python 3.11以上
- Google Cloud Platformのアカウント
- BigQueryへのアクセス権限

### セットアップ

1. リポジトリをクローン
```bash
git clone <repository-url>
cd private-nba-analytics
```

2. 仮想環境の作成とアクティベート
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate  # Windows
```

3. 依存関係のインストール
```bash
pip install -e .
```

4. BigQuery認証情報の設定

`.streamlit/secrets.toml`ファイルを作成し、以下の形式でGCPサービスアカウントの情報を記載：

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

## 🚀 使い方

1. アプリケーションの起動
```bash
streamlit run main.py
```

2. ブラウザで `http://localhost:8501` にアクセス

3. サイドバーから機能を選択：
   - **選手検索**: 選手を検索してスタッツを確認
   - **ランキング**: シーズン別のランキングを表示

## 📊 データ構造

BigQueryのテーブル: `nba_stats.fact_player_season_stats`

主要なカラム：
- `PLAYER_NAME`: 選手名
- `SEASON`: シーズンID
- `TEAM_ABBREVIATION`: チーム略称
- `GP`: 出場試合数
- `PTS`, `AST`, `REB`: 得点、アシスト、リバウンド
- `FG_PCT`, `FG3_PCT`, `FT_PCT`: シュート成功率
- その他多数のスタッツ

## 🔄 データパイプライン

このプロジェクトには、NBA APIからNBAスタッツを取得してBigQueryにロードするモジュラーなデータパイプラインが含まれています。

### パイプラインコンポーネント

- **extractors/**: NBA APIエンドポイントからデータを抽出
- **loaders/**: BigQueryにデータをロード
- **utils/**: ユーティリティ関数（シーズン生成など）
- **jobs/**: データ操作のための実行可能スクリプト

### 設定

環境変数で設定するか、`scripts/data_pipeline/config.py`を編集：

```bash
# オプション: デフォルト設定を上書き
export GCP_PROJECT_ID="your-project-id"
export HISTORICAL_START_YEAR="1997"
export CURRENT_YEAR="2025"
```

### 使い方

#### 1. 過去データの一括取得

全ての過去の選手スタッツを取得してロード（一度だけの操作）：

```bash
cd scripts/data_pipeline/jobs

# 全シーズンを一括取得（1997-2025）
python backfill_player_stats.py

# 特定の年範囲を一括取得
python backfill_player_stats.py --start-year 2020 --end-year 2023

# ドライラン（取得のみでBigQueryにロードしない）
python backfill_player_stats.py --dry-run
```

#### 2. 今シーズンの更新

今シーズンのスタッツを更新（定期実行/スケジュール実行用）：

```bash
cd scripts/data_pipeline/jobs

# 今シーズンを更新（自動検出）
python update_current_season.py

# 特定のシーズンを更新
python update_current_season.py --season 2024-25

# ドライラン
python update_current_season.py --dry-run
```

#### 3. スケジュール更新

自動更新のために、cronジョブやスケジュールタスクを設定：

```bash
# cronジョブの例（毎日午前6時）
0 6 * * * cd /path/to/private-nba-analytics/scripts/data_pipeline/jobs && python update_current_season.py
```

### パイプライン機能

- **レート制限**: NBA APIの制限を尊重する自動レート制限
- **エラーハンドリング**: 個別の失敗があっても処理を継続
- **Upsertサポート**: 同じシーズンの重複データを防止
- **ログ機能**: コンソールとファイルへの包括的なログ
- **ドライランモード**: BigQueryを変更せずにデータ取得をテスト

## 📁 プロジェクト構造

```
private-nba-analytics/
├── main.py                      # ホームページ
├── pages/
│   ├── 1_player_search.py      # 選手検索ページ
│   └── 2_rankings.py           # ランキングページ
├── scripts/
│   └── data_pipeline/          # NBAスタッツ取得用データパイプライン
│       ├── config.py           # 設定
│       ├── client.py           # BigQueryクライアント管理
│       ├── utils/              # ユーティリティ関数
│       │   └── season_generator.py
│       ├── extractors/         # APIからのデータ抽出
│       │   └── player_stats.py
│       ├── loaders/            # BigQueryへのデータロード
│       │   └── bigquery_loader.py
│       └── jobs/               # 実行可能スクリプト
│           ├── backfill_player_stats.py     # 過去データ一括取得
│           └── update_current_season.py     # 今シーズン更新
├── .streamlit/
│   └── secrets.toml            # BigQuery認証情報（gitignore）
├── pyproject.toml              # プロジェクト設定
├── .gitignore
└── README.md
```

## 🔒 セキュリティ

- BigQueryの認証情報は`.streamlit/secrets.toml`に保存し、Gitにコミットしない
- `.gitignore`に`secrets.toml`が含まれていることを確認

## 📝 ライセンス

このプロジェクトは個人用途です。

## 🤝 貢献

バグ報告や機能リクエストはIssueで受け付けています。
