# NBA Data Pipeline

A modular data pipeline for extracting NBA statistics from the NBA API and loading them into Google BigQuery.

## Architecture

```
data_pipeline/
├── config.py              # Configuration management
├── client.py              # BigQuery client
├── utils/                 # Utility functions
│   └── season_generator.py
├── extractors/            # Data extraction
│   └── player_stats.py    # NBA API player stats extractor
├── loaders/               # Data loading
│   └── bigquery_loader.py # BigQuery loader
└── jobs/                  # Executable scripts
    ├── backfill_player_stats.py     # Historical data backfill
    └── update_current_season.py     # Current season update
```

## Design Principles

### 1. Separation of Concerns
- **Extractors**: Fetch data from external APIs
- **Loaders**: Write data to storage systems
- **Utils**: Shared utility functions
- **Jobs**: Orchestrate extractors and loaders

### 2. Extensibility
The modular design makes it easy to add new data sources:

```python
# Example: Add a new extractor for team stats
from extractors.base import BaseExtractor

class TeamStatsExtractor(BaseExtractor):
    def fetch_season_stats(self, season):
        # Implementation here
        pass
```

### 3. Configuration Management
All settings are centralized in `config.py` and can be overridden via environment variables.

### 4. Error Handling
- Graceful error handling with detailed logging
- Continue-on-error for batch operations
- Retry logic for transient failures

## Usage

### Backfill Historical Data

```bash
cd jobs

# Full backfill (1997-2025)
python backfill_player_stats.py

# Specific years
python backfill_player_stats.py --start-year 2020 --end-year 2023

# Different stats mode
python backfill_player_stats.py --per-mode Totals

# Dry run
python backfill_player_stats.py --dry-run
```

### Update Current Season

```bash
cd jobs

# Update current season
python update_current_season.py

# Update specific season
python update_current_season.py --season 2024-25

# Dry run
python update_current_season.py --dry-run
```

## Configuration

### Environment Variables

```bash
# Google Cloud settings
export GCP_PROJECT_ID="your-project-id"
export PLAYER_SEASON_STATS_TABLE_ID="project.dataset.table"

# NBA API settings
export NBA_API_RATE_LIMIT_DELAY="2.0"  # seconds
export NBA_API_TIMEOUT="30"            # seconds

# Data range
export HISTORICAL_START_YEAR="1997"
export CURRENT_YEAR="2025"

# BigQuery settings
export BIGQUERY_WRITE_DISPOSITION="WRITE_APPEND"
```

### Programmatic Configuration

```python
from config import Config

# Override settings
Config.HISTORICAL_START_YEAR = 2000
Config.NBA_API_RATE_LIMIT_DELAY = 1.5

# Get current season
current_season = Config.get_current_season()  # "2024-25"
```

## Extending the Pipeline

### Adding a New Extractor

1. Create a new extractor class in `extractors/`:

```python
# extractors/team_stats.py
from nba_api.stats.endpoints import leaguedashteamstats

class TeamStatsExtractor:
    def fetch_season_stats(self, season):
        stats = leaguedashteamstats.LeagueDashTeamStats(season=season)
        return stats.get_data_frames()[0]
```

2. Update `extractors/__init__.py`:

```python
from .team_stats import TeamStatsExtractor

__all__ = ["PlayerStatsExtractor", "TeamStatsExtractor"]
```

3. Create a corresponding job script:

```python
# jobs/backfill_team_stats.py
from extractors import TeamStatsExtractor
from loaders import BigQueryLoader

extractor = TeamStatsExtractor()
loader = BigQueryLoader()

# Fetch and load data
df = extractor.fetch_season_stats("2024-25")
loader.load_dataframe(df, "project.dataset.team_stats")
```

### Adding a New Data Source

For non-NBA-API data sources, create a new extractor following the same pattern:

```python
# extractors/external_api.py
import requests

class ExternalAPIExtractor:
    def fetch_data(self):
        response = requests.get("https://api.example.com/data")
        return response.json()
```

## Logging

Logs are written to both console and log files:

- `backfill_player_stats.log`: Historical backfill logs
- `update_current_season.log`: Current season update logs

Log format:
```
2025-03-06 10:30:45 - extractor - INFO - Fetching 2024-25 season stats...
```

## Error Handling

### Transient Errors
The pipeline handles transient API errors gracefully:
- Rate limiting delays
- Network timeouts
- Temporary API unavailability

### Data Validation
Data is validated before loading:
- Non-empty DataFrames
- Required columns present
- Valid data types

### Continue on Error
Batch operations continue even if individual items fail:
```python
extractor.fetch_multiple_seasons(
    seasons=["2022-23", "2023-24", "2024-25"],
    continue_on_error=True  # Don't stop on individual failures
)
```

## Testing

### Dry Run Mode
Test the pipeline without modifying BigQuery:

```bash
python backfill_player_stats.py --dry-run
python update_current_season.py --dry-run
```

### Connection Test
Test BigQuery connectivity:

```python
from client import BigQueryClient

if BigQueryClient.test_connection():
    print("Connection successful!")
```

## Scheduled Execution

### Cron (Linux/macOS)

```bash
# Edit crontab
crontab -e

# Add daily update at 6 AM
0 6 * * * cd /path/to/scripts/data_pipeline/jobs && /path/to/python update_current_season.py >> /path/to/cron.log 2>&1
```

### Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., daily at 6 AM)
4. Set action: Run program
   - Program: `python.exe`
   - Arguments: `update_current_season.py`
   - Start in: `C:\path\to\scripts\data_pipeline\jobs`

### Cloud Scheduler (GCP)

```bash
# Create Cloud Scheduler job
gcloud scheduler jobs create http update-nba-stats \
  --schedule="0 6 * * *" \
  --uri="https://your-cloud-function-url" \
  --http-method=POST \
  --location=us-central1
```

## Monitoring

### Check Logs
```bash
# View recent backfill logs
tail -f backfill_player_stats.log

# View current season update logs
tail -f update_current_season.log

# Search for errors
grep -i error *.log
```

### Verify Data
```sql
-- Check latest season data
SELECT
  SEASON,
  COUNT(*) as player_count,
  MAX(UPDATED_DT) as last_update
FROM `nba_stats.fact_player_season_stats`
GROUP BY SEASON
ORDER BY SEASON DESC
LIMIT 5;
```

## Troubleshooting

### Issue: API Rate Limiting

**Solution**: Increase `NBA_API_RATE_LIMIT_DELAY`:
```bash
export NBA_API_RATE_LIMIT_DELAY="3.0"
```

### Issue: BigQuery Connection Failed

**Solution**: Check GCP credentials:
```bash
# Set GOOGLE_APPLICATION_CREDENTIALS
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

### Issue: Empty Data Returned

**Solution**: Verify the season format and API availability:
```python
from extractors import PlayerStatsExtractor

extractor = PlayerStatsExtractor()
df = extractor.fetch_season_stats("2024-25")
print(f"Rows: {len(df)}")
```

## Best Practices

1. **Always use dry-run first** when testing new configurations
2. **Monitor logs regularly** for errors or warnings
3. **Set up alerts** for pipeline failures
4. **Version control** configuration changes
5. **Document** any customizations or extensions
6. **Test locally** before deploying to production
7. **Use environment variables** for sensitive data

## Future Enhancements

- [ ] Add support for player game logs
- [ ] Add support for team statistics
- [ ] Implement incremental updates (only new games)
- [ ] Add data quality checks and validation
- [ ] Create unit and integration tests
- [ ] Add Airflow/Dagster orchestration
- [ ] Implement data versioning
- [ ] Add metrics and monitoring dashboard

---

# 日本語版 / Japanese Version

# NBAデータパイプライン

NBA APIからNBAスタッツを抽出し、Google BigQueryにロードするモジュラーなデータパイプラインです。

## アーキテクチャ

```
data_pipeline/
├── config.py              # 設定管理
├── client.py              # BigQueryクライアント
├── utils/                 # ユーティリティ関数
│   └── season_generator.py
├── extractors/            # データ抽出
│   └── player_stats.py    # NBA API選手スタッツ抽出器
├── loaders/               # データロード
│   └── bigquery_loader.py # BigQueryローダー
└── jobs/                  # 実行可能スクリプト
    ├── backfill_player_stats.py     # 過去データ一括取得
    └── update_current_season.py     # 今シーズン更新
```

## 設計原則

### 1. 関心の分離
- **Extractors**: 外部APIからデータを取得
- **Loaders**: ストレージシステムにデータを書き込み
- **Utils**: 共有ユーティリティ関数
- **Jobs**: ExtractorとLoaderを組み合わせて実行

### 2. 拡張性
モジュラー設計により、新しいデータソースの追加が容易：

```python
# 例: チームスタッツ用の新しいExtractorを追加
from extractors.base import BaseExtractor

class TeamStatsExtractor(BaseExtractor):
    def fetch_season_stats(self, season):
        # 実装
        pass
```

### 3. 設定管理
すべての設定は`config.py`に集約され、環境変数で上書き可能。

### 4. エラーハンドリング
- 詳細なログ付きの優雅なエラー処理
- バッチ操作でのエラー時継続
- 一時的な失敗のリトライロジック

## 使い方

### 過去データの一括取得

```bash
cd jobs

# 全データ一括取得（1997-2025）
python backfill_player_stats.py

# 特定の年を指定
python backfill_player_stats.py --start-year 2020 --end-year 2023

# 異なるスタッツモード
python backfill_player_stats.py --per-mode Totals

# ドライラン
python backfill_player_stats.py --dry-run
```

### 今シーズンの更新

```bash
cd jobs

# 今シーズンを更新
python update_current_season.py

# 特定のシーズンを更新
python update_current_season.py --season 2024-25

# ドライラン
python update_current_season.py --dry-run
```

## 設定

### 環境変数

```bash
# Google Cloud設定
export GCP_PROJECT_ID="your-project-id"
export PLAYER_SEASON_STATS_TABLE_ID="project.dataset.table"

# NBA API設定
export NBA_API_RATE_LIMIT_DELAY="2.0"  # 秒
export NBA_API_TIMEOUT="30"            # 秒

# データ範囲
export HISTORICAL_START_YEAR="1997"
export CURRENT_YEAR="2025"

# BigQuery設定
export BIGQUERY_WRITE_DISPOSITION="WRITE_APPEND"
```

### プログラムによる設定

```python
from config import Config

# 設定を上書き
Config.HISTORICAL_START_YEAR = 2000
Config.NBA_API_RATE_LIMIT_DELAY = 1.5

# 現在のシーズンを取得
current_season = Config.get_current_season()  # "2024-25"
```

## パイプラインの拡張

### 新しいExtractorの追加

1. `extractors/`に新しいExtractorクラスを作成：

```python
# extractors/team_stats.py
from nba_api.stats.endpoints import leaguedashteamstats

class TeamStatsExtractor:
    def fetch_season_stats(self, season):
        stats = leaguedashteamstats.LeagueDashTeamStats(season=season)
        return stats.get_data_frames()[0]
```

2. `extractors/__init__.py`を更新：

```python
from .team_stats import TeamStatsExtractor

__all__ = ["PlayerStatsExtractor", "TeamStatsExtractor"]
```

3. 対応するジョブスクリプトを作成：

```python
# jobs/backfill_team_stats.py
from extractors import TeamStatsExtractor
from loaders import BigQueryLoader

extractor = TeamStatsExtractor()
loader = BigQueryLoader()

# データを取得してロード
df = extractor.fetch_season_stats("2024-25")
loader.load_dataframe(df, "project.dataset.team_stats")
```

### 新しいデータソースの追加

NBA API以外のデータソースには、同じパターンで新しいExtractorを作成：

```python
# extractors/external_api.py
import requests

class ExternalAPIExtractor:
    def fetch_data(self):
        response = requests.get("https://api.example.com/data")
        return response.json()
```

## ログ

ログはコンソールとログファイルの両方に出力：

- `backfill_player_stats.log`: 過去データ一括取得のログ
- `update_current_season.log`: 今シーズン更新のログ

ログフォーマット：
```
2025-03-06 10:30:45 - extractor - INFO - Fetching 2024-25 season stats...
```

## エラーハンドリング

### 一時的なエラー
パイプラインは一時的なAPIエラーを適切に処理：
- レート制限の遅延
- ネットワークタイムアウト
- 一時的なAPI利用不可

### データ検証
ロード前にデータを検証：
- 空でないDataFrame
- 必須カラムの存在
- 有効なデータ型

### エラー時の継続
バッチ操作は個別のアイテムが失敗しても継続：
```python
extractor.fetch_multiple_seasons(
    seasons=["2022-23", "2023-24", "2024-25"],
    continue_on_error=True  # 個別の失敗で停止しない
)
```

## テスト

### ドライランモード
BigQueryを変更せずにパイプラインをテスト：

```bash
python backfill_player_stats.py --dry-run
python update_current_season.py --dry-run
```

### 接続テスト
BigQuery接続をテスト：

```python
from client import BigQueryClient

if BigQueryClient.test_connection():
    print("接続成功！")
```

## スケジュール実行

### Cron（Linux/macOS）

```bash
# crontabを編集
crontab -e

# 毎日午前6時に更新
0 6 * * * cd /path/to/scripts/data_pipeline/jobs && /path/to/python update_current_season.py >> /path/to/cron.log 2>&1
```

### タスクスケジューラー（Windows）

1. タスクスケジューラーを開く
2. 基本タスクを作成
3. トリガーを設定（例: 毎日午前6時）
4. アクションを設定: プログラムの実行
   - プログラム: `python.exe`
   - 引数: `update_current_season.py`
   - 開始: `C:\path\to\scripts\data_pipeline\jobs`

### Cloud Scheduler（GCP）

```bash
# Cloud Schedulerジョブを作成
gcloud scheduler jobs create http update-nba-stats \
  --schedule="0 6 * * *" \
  --uri="https://your-cloud-function-url" \
  --http-method=POST \
  --location=us-central1
```

## モニタリング

### ログの確認
```bash
# 最近の一括取得ログを表示
tail -f backfill_player_stats.log

# 今シーズン更新ログを表示
tail -f update_current_season.log

# エラーを検索
grep -i error *.log
```

### データの検証
```sql
-- 最新シーズンのデータを確認
SELECT
  SEASON,
  COUNT(*) as player_count,
  MAX(UPDATED_DT) as last_update
FROM `nba_stats.fact_player_season_stats`
GROUP BY SEASON
ORDER BY SEASON DESC
LIMIT 5;
```

## トラブルシューティング

### 問題: APIレート制限

**解決策**: `NBA_API_RATE_LIMIT_DELAY`を増やす：
```bash
export NBA_API_RATE_LIMIT_DELAY="3.0"
```

### 問題: BigQuery接続失敗

**解決策**: GCP認証情報を確認：
```bash
# GOOGLE_APPLICATION_CREDENTIALSを設定
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

### 問題: 空のデータが返される

**解決策**: シーズンフォーマットとAPI可用性を確認：
```python
from extractors import PlayerStatsExtractor

extractor = PlayerStatsExtractor()
df = extractor.fetch_season_stats("2024-25")
print(f"行数: {len(df)}")
```

## ベストプラクティス

1. **新しい設定をテストする際は常にドライランを最初に使用**
2. **エラーや警告のためにログを定期的に監視**
3. **パイプライン失敗のアラートを設定**
4. **設定変更をバージョン管理**
5. **カスタマイズや拡張を文書化**
6. **本番環境にデプロイする前にローカルでテスト**
7. **機密データには環境変数を使用**

## 今後の機能拡張

- [ ] 選手のゲームログのサポートを追加
- [ ] チームスタッツのサポートを追加
- [ ] 増分更新の実装（新しいゲームのみ）
- [ ] データ品質チェックと検証の追加
- [ ] ユニットテストと統合テストの作成
- [ ] Airflow/Dagsterオーケストレーションの追加
- [ ] データバージョニングの実装
- [ ] メトリクスとモニタリングダッシュボードの追加
