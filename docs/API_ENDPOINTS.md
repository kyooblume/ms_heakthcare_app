# 主要APIエンドポイント一覧

このドキュメントは、本バックエンドシステムが提供する主要なAPIのエンドポイントと役割をまとめたものです。

## 認証
### トークンの取得（ログイン）
* **METHOD:** `POST`
* **ENDPOINT:** `/api/token/`
* **役割:** ユーザー名とパスワードを送信し、認証トークンを取得します。

## アカウント (`accounts`)
### プロフィールの取得・更新
* **METHOD:** `GET`, `PATCH`
* **ENDPOINT:** `/api/accounts/profile/`
* **役割:** ログイン中のユーザーのプロフィール情報を取得・更新します。

### オンボーディング状況の確認
* **METHOD:** `GET`
* **ENDPOINT:** `/api/accounts/onboarding-status/`
* **役割:** ユーザーが各アンケートに回答済みかどうかを返します。

## 健康記録 (`health_records`)
### 健康記録のCRUD
* **METHOD:** `GET`, `POST`, `PATCH`, `DELETE`
* **ENDPOINT:** `/api/health/records/`
* **役割:** 歩数や体重といった日々の健康記録を管理します。

## 食事 (`meals`)
### 食事記録の追加（バーコード経由）
* **METHOD:** `POST`
* **ENDPOINT:** `/api/meals/add-from-barcode/`
* **役割:** バーコードと量を送信し、食事記録を自動作成します。

### 食事記録のCRUD
* **METHOD:** `GET`, `POST`, `PATCH`, `DELETE`
* **ENDPOINT:** `/api/meals/records/`
* **役割:** 食事記録（朝食、昼食など）を手動で管理します。

## 商品情報 (`products`)
### バーコード検索
* **METHOD:** `GET`
* **ENDPOINT:** `/api/products/lookup/<barcode>/`
* **役割:** 商品のバーコード番号を元に、Open Food Facts APIを利用して商品名や栄養情報を取得します。

## レポート (`reports`)
### 歩数ランキング
* **METHOD:** `GET`
* **ENDPOINT:** `/api/reports/steps-ranking/<YYYY-MM-DD>/`
* **役割:** 指定された日付の歩数ランキングと、自分の順位や統計情報を取得します。

### 睡眠リズムランキング
* **METHOD:** `GET`
* **ENDPOINT:** `/api/reports/sleep-rhythm-ranking/`
* **役割:** 社会的ジェットラグ(平日と休日の差等)が少ない順のランキングを取得します。

## レシピ・献立提案 (`recipes`)
### 献立提案の取得
* **METHOD:** `GET`
* **ENDPOINT:** `/api/recipes/suggestions/`
* **役割:** ユーザーのその日の栄養摂取状況を分析し、最適なレシピを提案します。

## アンケート (`surveys`)
### アンケートの一覧・詳細取得
* **METHOD:** `GET`
* **ENDPOINT:** `/api/surveys/`
* **役割:** アンケートの一覧および詳細（質問・選択肢リスト）を取得します。

### 回答の送信
* **METHOD:** `POST`
* **ENDPOINT:** `/api/answers/`
* **役割:** ユーザーからのアンケートの回答を送信します。
