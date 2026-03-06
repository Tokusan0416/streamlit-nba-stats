# Configuration Management

This document explains how configuration is managed in this project following security best practices.

## Configuration Files Overview

| File | Purpose | Git Tracked | Contains | Example |
|------|---------|-------------|----------|---------|
| `.env` | Environment-specific settings | ❌ No | Project IDs, table names | `GCP_PROJECT_ID=my-project` |
| `.env.example` | Template for .env | ✅ Yes | Variable names only | `GCP_PROJECT_ID=your-project-id` |
| `secrets.toml` | Authentication credentials | ❌ No | Private keys, passwords | Service account JSON |
| `config.py` | Application defaults | ✅ Yes | Rate limits, constants | `NBA_API_TIMEOUT=30` |

## Why This Separation?

### Security Best Practices

1. **secrets.toml**: Contains sensitive authentication data
   - ❌ NEVER commit to git
   - ⚠️ High security risk if exposed
   - Used by: Streamlit app for BigQuery authentication

2. **.env**: Contains environment-specific configuration
   - ❌ NEVER commit to git
   - ⚠️ Medium security risk (exposes project structure)
   - Used by: Data pipeline scripts

3. **config.py**: Contains application defaults
   - ✅ Safe to commit to git
   - ℹ️ No sensitive information
   - Used by: All components

## Configuration Priority

Settings are loaded in this order (highest priority first):

1. **Environment Variables** (highest priority)
   ```bash
   export GCP_PROJECT_ID="production-project"
   python script.py
   ```

2. **.env File**
   ```bash
   # .env
   GCP_PROJECT_ID=development-project
   ```

3. **config.py Defaults** (lowest priority)
   ```python
   NBA_API_TIMEOUT: int = 30  # Default if not set elsewhere
   ```

## Setup Instructions

### First Time Setup

1. **Install dependencies**
   ```bash
   pip install -e .
   ```
   This will install `python-dotenv` for .env file support.

2. **Create .env file**
   ```bash
   cp .env.example .env
   ```

3. **Edit .env with your values**
   ```bash
   # .env
   GCP_PROJECT_ID=your-actual-project-id
   PLAYER_SEASON_STATS_TABLE=your-project-id.nba_stats.fact_player_season_stats
   ```

4. **Create secrets.toml** (for Streamlit app only)
   ```bash
   mkdir -p .streamlit
   # Add your service account JSON content
   ```

### Verify Configuration

Check if your configuration is loaded correctly:

```python
from scripts.data_pipeline.config import Config

# Display current configuration
Config.display_config()
```

## Configuration Variables

### Required Variables

Must be set in `.env` file or environment:

```bash
# Google Cloud Project ID
GCP_PROJECT_ID=your-project-id
```

### Optional Variables

Have sensible defaults in `config.py`:

```bash
# BigQuery table (defaults to GCP_PROJECT_ID.nba_stats.fact_player_season_stats)
PLAYER_SEASON_STATS_TABLE=custom-project.custom-dataset.custom-table

# NBA API settings (defaults shown)
NBA_API_RATE_LIMIT_DELAY=2.0  # seconds between API calls
NBA_API_TIMEOUT=30            # API timeout in seconds

# Data range (defaults shown)
HISTORICAL_START_YEAR=1997
CURRENT_YEAR=2025

# BigQuery settings (defaults shown)
BIGQUERY_WRITE_DISPOSITION=WRITE_APPEND
```

## Different Environments

### Development Environment

Create a `.env` file:
```bash
GCP_PROJECT_ID=dev-nba-analytics
PLAYER_SEASON_STATS_TABLE=dev-nba-analytics.nba_stats.fact_player_season_stats
```

### Production Environment

Use environment variables (no .env file):
```bash
export GCP_PROJECT_ID="prod-nba-analytics"
export PLAYER_SEASON_STATS_TABLE="prod-nba-analytics.nba_stats.fact_player_season_stats"
python script.py
```

### Testing Environment

Override in code or use separate .env.test:
```python
import os
os.environ['GCP_PROJECT_ID'] = 'test-project'
os.environ['PLAYER_SEASON_STATS_TABLE'] = 'test-project.test_dataset.test_table'
```

## Security Checklist

- [ ] `.env` is in `.gitignore`
- [ ] `secrets.toml` is in `.gitignore`
- [ ] `.env.example` contains no actual values
- [ ] Service account has minimum required permissions
- [ ] Project IDs are not hardcoded in Python files
- [ ] Secrets are never logged or printed

## Common Issues

### Issue: "GCP_PROJECT_ID is required"

**Cause**: .env file not created or GCP_PROJECT_ID not set

**Solution**:
```bash
# Create .env from template
cp .env.example .env

# Edit .env and set your project ID
nano .env  # or use any text editor
```

### Issue: "python-dotenv not installed"

**Cause**: Dependencies not installed

**Solution**:
```bash
pip install -e .
# or
pip install python-dotenv
```

### Issue: Configuration not loading from .env

**Cause**: .env file in wrong location

**Solution**: Make sure .env is in project root:
```
private-nba-analytics/
├── .env              ← Should be here
├── .env.example
├── scripts/
│   └── data_pipeline/
```

## Migrating from Old Configuration

If you have hardcoded values in `config.py`:

1. **Create .env file**:
   ```bash
   cp .env.example .env
   ```

2. **Move project-specific values to .env**:
   ```bash
   # In .env
   GCP_PROJECT_ID=invertible-vine-477701-j8
   PLAYER_SEASON_STATS_TABLE=invertible-vine-477701-j8.nba_stats.fact_player_season_stats
   ```

3. **Remove hardcoded values from config.py**:
   The new config.py already handles this correctly.

4. **Test configuration**:
   ```bash
   cd scripts/data_pipeline/jobs
   python backfill_player_stats.py --dry-run
   ```

## Best Practices

1. **Never commit sensitive data**
   - Use .env for configuration
   - Use secrets.toml for credentials
   - Both are in .gitignore

2. **Use .env.example as documentation**
   - Keep it updated with all required variables
   - Use placeholder values only

3. **Environment variables for production**
   - Don't use .env files in production
   - Set environment variables in your deployment platform

4. **Document configuration changes**
   - Update .env.example when adding new variables
   - Update this document with descriptions

5. **Validate configuration early**
   - Config.validate() runs on import
   - Fails fast with clear error messages

## Additional Resources

- [python-dotenv documentation](https://github.com/theskumar/python-dotenv)
- [12-Factor App Config](https://12factor.net/config)
- [Google Cloud Security Best Practices](https://cloud.google.com/security/best-practices)

---

# 日本語版 / Japanese Version

# 設定管理

このドキュメントは、セキュリティのベストプラクティスに従ったこのプロジェクトの設定管理方法を説明します。

## 設定ファイル概要

| ファイル | 目的 | Git管理 | 含む内容 | 例 |
|---------|------|--------|---------|-----|
| `.env` | 環境固有の設定 | ❌ No | プロジェクトID、テーブル名 | `GCP_PROJECT_ID=my-project` |
| `.env.example` | .envのテンプレート | ✅ Yes | 変数名のみ | `GCP_PROJECT_ID=your-project-id` |
| `secrets.toml` | 認証情報 | ❌ No | 秘密鍵、パスワード | サービスアカウントJSON |
| `config.py` | アプリケーションのデフォルト | ✅ Yes | レート制限、定数 | `NBA_API_TIMEOUT=30` |

## なぜこの分離が必要か？

### セキュリティベストプラクティス

1. **secrets.toml**: 機密の認証データを含む
   - ❌ 絶対にgitにコミットしない
   - ⚠️ 漏洩時の高いセキュリティリスク
   - 使用者: StreamlitアプリのBigQuery認証

2. **.env**: 環境固有の設定を含む
   - ❌ 絶対にgitにコミットしない
   - ⚠️ 中程度のセキュリティリスク（プロジェクト構造が露呈）
   - 使用者: データパイプラインスクリプト

3. **config.py**: アプリケーションのデフォルトを含む
   - ✅ gitにコミットして安全
   - ℹ️ 機密情報なし
   - 使用者: すべてのコンポーネント

## 設定の優先順位

設定は以下の順序で読み込まれます（優先度の高い順）：

1. **環境変数**（最優先）
   ```bash
   export GCP_PROJECT_ID="production-project"
   python script.py
   ```

2. **.envファイル**
   ```bash
   # .env
   GCP_PROJECT_ID=development-project
   ```

3. **config.pyのデフォルト値**（最も優先度が低い）
   ```python
   NBA_API_TIMEOUT: int = 30  # 他で設定されていない場合のデフォルト
   ```

## セットアップ手順

### 初回セットアップ

1. **依存関係のインストール**
   ```bash
   pip install -e .
   ```
   これで.envファイルサポート用の`python-dotenv`がインストールされます。

2. **.envファイルの作成**
   ```bash
   cp .env.example .env
   ```

3. **.envを実際の値で編集**
   ```bash
   # .env
   GCP_PROJECT_ID=your-actual-project-id
   PLAYER_SEASON_STATS_TABLE=your-project-id.nba_stats.fact_player_season_stats
   ```

4. **secrets.tomlの作成**（Streamlitアプリ用のみ）
   ```bash
   mkdir -p .streamlit
   # サービスアカウントJSONの内容を追加
   ```

### 設定の確認

設定が正しく読み込まれているか確認：

```python
from scripts.data_pipeline.config import Config

# 現在の設定を表示
Config.display_config()
```

## 設定変数

### 必須変数

`.env`ファイルまたは環境変数に設定必須：

```bash
# Google CloudプロジェクトID
GCP_PROJECT_ID=your-project-id
```

### オプション変数

`config.py`に適切なデフォルト値あり：

```bash
# BigQueryテーブル（デフォルト: GCP_PROJECT_ID.nba_stats.fact_player_season_stats）
PLAYER_SEASON_STATS_TABLE=custom-project.custom-dataset.custom-table

# NBA API設定（デフォルト値を表示）
NBA_API_RATE_LIMIT_DELAY=2.0  # API呼び出し間の秒数
NBA_API_TIMEOUT=30            # APIタイムアウト（秒）

# データ範囲（デフォルト値を表示）
HISTORICAL_START_YEAR=1997
CURRENT_YEAR=2025

# BigQuery設定（デフォルト値を表示）
BIGQUERY_WRITE_DISPOSITION=WRITE_APPEND
```

## 異なる環境

### 開発環境

`.env`ファイルを作成：
```bash
GCP_PROJECT_ID=dev-nba-analytics
PLAYER_SEASON_STATS_TABLE=dev-nba-analytics.nba_stats.fact_player_season_stats
```

### 本番環境

環境変数を使用（.envファイルなし）：
```bash
export GCP_PROJECT_ID="prod-nba-analytics"
export PLAYER_SEASON_STATS_TABLE="prod-nba-analytics.nba_stats.fact_player_season_stats"
python script.py
```

### テスト環境

コードで上書きするか、別の.env.testを使用：
```python
import os
os.environ['GCP_PROJECT_ID'] = 'test-project'
os.environ['PLAYER_SEASON_STATS_TABLE'] = 'test-project.test_dataset.test_table'
```

## セキュリティチェックリスト

- [ ] `.env`が`.gitignore`に含まれている
- [ ] `secrets.toml`が`.gitignore`に含まれている
- [ ] `.env.example`に実際の値が含まれていない
- [ ] サービスアカウントに必要最小限の権限のみ
- [ ] プロジェクトIDがPythonファイルにハードコードされていない
- [ ] 秘密情報がログや出力に含まれない

## よくある問題

### 問題: "GCP_PROJECT_ID is required"

**原因**: .envファイルが作成されていないか、GCP_PROJECT_IDが設定されていない

**解決策**:
```bash
# テンプレートから.envを作成
cp .env.example .env

# .envを編集してプロジェクトIDを設定
nano .env  # または任意のテキストエディタ
```

### 問題: "python-dotenv not installed"

**原因**: 依存関係がインストールされていない

**解決策**:
```bash
pip install -e .
# または
pip install python-dotenv
```

### 問題: .envから設定が読み込まれない

**原因**: .envファイルの場所が間違っている

**解決策**: .envがプロジェクトルートにあることを確認：
```
private-nba-analytics/
├── .env              ← ここにあるべき
├── .env.example
├── scripts/
│   └── data_pipeline/
```

## 旧設定からの移行

`config.py`にハードコードされた値がある場合：

1. **.envファイルを作成**:
   ```bash
   cp .env.example .env
   ```

2. **プロジェクト固有の値を.envに移動**:
   ```bash
   # .envに
   GCP_PROJECT_ID=invertible-vine-477701-j8
   PLAYER_SEASON_STATS_TABLE=invertible-vine-477701-j8.nba_stats.fact_player_season_stats
   ```

3. **config.pyからハードコードされた値を削除**:
   新しいconfig.pyは既に正しく処理しています。

4. **設定をテスト**:
   ```bash
   cd scripts/data_pipeline/jobs
   python backfill_player_stats.py --dry-run
   ```

## ベストプラクティス

1. **機密データを絶対にコミットしない**
   - 設定には.envを使用
   - 認証情報にはsecrets.tomlを使用
   - 両方とも.gitignoreに含まれている

2. **.env.exampleをドキュメントとして使用**
   - すべての必須変数で最新の状態を保つ
   - プレースホルダー値のみを使用

3. **本番環境では環境変数を使用**
   - 本番環境で.envファイルを使用しない
   - デプロイプラットフォームで環境変数を設定

4. **設定の変更を文書化**
   - 新しい変数を追加する際は.env.exampleを更新
   - このドキュメントに説明を追加

5. **設定を早期に検証**
   - Config.validate()がインポート時に実行
   - 明確なエラーメッセージで早期に失敗

## 追加リソース

- [python-dotenv ドキュメント](https://github.com/theskumar/python-dotenv)
- [12-Factor App Config](https://12factor.net/config)
- [Google Cloud セキュリティベストプラクティス](https://cloud.google.com/security/best-practices)
