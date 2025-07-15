# ms_healthcare_app バックエンド

日々の健康活動を記録し、ゲーミフィケーション要素でモチベーションを高める総合ヘルスケアアプリケーションのバックエンドシステムです。

## ✨ 主な機能

* **ユーザー管理:** 認証、プロフィール管理、スマートなオンボーディングフロー
* **健康記録:** 歩数、体重、食事、睡眠などの記録
* **レポート & ランキング:** 歩数や睡眠リズムのランキング機能
* **バーコード連携:** Open Food Factsを利用した、バーコードからの栄養情報取得と食事記録
* **献立提案機能:** ユーザーの栄養摂取状況を分析し、不足している栄養素を補う最適なレシピを提案
* **キャラクターカスタマイズ:** ユーザーの活動に応じたアバターの見た目変化
* **チャットボット:** Gemini APIを利用したAIチャット機能

---

## 🛠️ 技術スタック

* **フレームワーク:** Django
* **API:** Django REST Framework
* **認証:** Simple JWT (JSON Web Token)
* **データベース:** SQLite (開発用)
* **外部API連携:** Google Gemini, Open Food Facts

---

## 🚀 セットアップ手順

1.  **リポジトリのクローン:**
    ```bash
    git clone [https://github.com/kyooblume/ms_heakthcare_app.git](https://github.com/kyooblume/ms_heakthcare_app.git)
    cd ms_healthcare_app_backend
    ```

2.  **Python仮想環境の作成と有効化:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **必要なライブラリのインストール:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **`.env`ファイルの作成とAPIキーの設定:**
    本プロジェクトは、チャット機能でGemini APIを使用します。プロジェクトのルートディレクトリに `.env` ファイルを新規作成し、ご自身のAPIキーを記述してください。
    ```
    GEMINI_API_KEY="ここにあなたのAPIキーを貼り付け"
    ```

5.  **データベースの初期化:**
    ```bash
    python manage.py migrate
    ```

6.  **管理者ユーザーの作成:**
    ```bash
    python manage.py createsuperuser
    ```

7.  **レシピデータの一括インポート（任意）:**
    献立提案機能の初期データを登録するために、特別な管理コマンドを用意しています。
    プロジェクトのルートディレクトリに`recipes.csv`と`ingredients.csv`を配置した後、以下のコマンドを実行してください。
    ```bash
    python manage.py import_recipes
    ```

8.  **開発サーバーの起動:**
    ```bash
    python manage.py runserver
    ```
    ブラウザで `http://127.0.0.1:8000/` にアクセスして動作を確認します。

---

## 📝 設計思想・詳細ドキュメント

より詳しいデータベース設計やAPIのエンドポイント一覧、機能仕様については、`docs/`フォルダ内の各ドキュメントを参照してください。

* [**データベース設計**](./docs/DATABASE_DESIGN.md)
* [**APIエンドポイント一覧**](./docs/API_ENDPOINTS.md)
* [**機能仕様：推奨栄養摂取量の自動計算**](./docs/FEATURE_NUTRITION_CALCULATION.md)
