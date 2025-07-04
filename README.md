# ms_healthcare_app バックエンド概要

日々の健康活動を記録し、ゲーミフィケーション要素でモチベーションを高める総合ヘルスケアアプリケーションのバックエンドシステムです。

# ms_healthcare_app バックエンド

日々の健康活動を記録し、ゲーミフィケーション要素でモチベーションを高める総合ヘルスケアアプリケーションのバックエンドシステムです。

## ✨ 主な機能

* **ユーザー管理:** 認証、プロフィール管理、スマートなオンボーディングフロー
* **健康記録:** 歩数、体重、食事、睡眠などの記録
* **レポート & ランキング:** 歩数や睡眠リズムのランキング機能
* **バーコード連携:** Open Food Factsを利用した、バーコードからの栄養情報取得と食事記録
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
    cd ms_heakthcare_app_backend
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

7.  **開発サーバーの起動:**
    ```bash
    python manage.py runserver
    ```
    ブラウザで `http://127.0.0.1:8000/` にアクセスして動作を確認します。

---

## 📝 設計思想メモ

### 推奨栄養摂取量の自動計算

ユーザーのプロフィール情報（年齢、性別、体重、身長、活動レベル）を基に、個別化された1日の推奨摂取カロリーおよびPFC（タンパク質・脂質・炭水化物）バランスを自動計算します。

1.  **基礎代謝量 (BMR) の計算:**
    * **ハリス・ベネディクト方程式（改良版）**を用いて算出します。

2.  **1日の総消費カロリー (TDEE) の計算:**
    * BMRに、ユーザーの活動レベルに応じた係数（1.2〜1.9）を乗じて推定します。

3.  **PFCバランスの設定:**
    * 決定した目標カロリーを、タンパク質(20%)・脂質(25%)・炭水化物(55%)の比率で分配し、目標グラム数を算出します。

---

## 技術スタック

* **フレームワーク:** Django 5.2.1
* **API:** Django REST Framework
* **認証:** Simple JWT (JSON Web Token)
* **データベース:** SQLite (開発用)


---

## セットアップ手順

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

7.  **開発サーバーの起動:**
    ```bash
    python manage.py runserver
    ```

---

## 詳細ドキュメント

より詳しいデータベース設計やAPIのエンドポイント一覧については、以下のドキュメントを参照してください。

* [**データベース設計**](./docs/DATABASE_DESIGN.md)
* [**APIエンドポイント一覧**](./docs/API_ENDPOINTS.md)
















