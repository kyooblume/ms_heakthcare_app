# 主要APIエンドポイント一覧

このドキュメントは、本バックエンドシステムが提供する主要なAPIのエンドポイント、役割、および使用方法をまとめたものです。

## 認証

### トークンの取得（ログイン）
* **METHOD:** `POST`
* **ENDPOINT:** `/api/token/`
* **役割:** ユーザー名とパスワードを送信し、認証トークン（Access & Refresh）を取得します。

## アカウント (`accounts`)

### プロフィールの取得・更新
* **METHOD:** `GET`, `PATCH`
* **ENDPOINT:** `/api/accounts/profile/`
* **役割:** ログイン中のユーザーのプロフィール情報（目標、身体情報、BigFiveスコアなど）を取得または部分的に更新します。

### オンボーディング状況の確認
* **METHOD:** `GET`
* **ENDPOINT:** `/api/accounts/onboarding-status/`
* **役割:** ユーザーが各アンケート（BigFive, 睡眠など）に回答済みかどうかを返し、フロントエンドが表示すべき画面を判断するのに役立ちます。

## 健康記録 (`health_records`)

### 健康記録のCRUD
* **METHOD:** `GET`, `POST`, `PATCH`, `DELETE`
* **ENDPOINT:** `/api/health/records/`
* **役割:** 歩数や体重といった日々の健康記録を作成、一覧取得、更新、削除します。

## 食事 (`meals`)

### 食事記録の追加（バーコード経由）
* **METHOD:** `POST`
* **ENDPOINT:** `/api/meals/add-from-barcode/`
* **役割:** バーコード番号と食べた量を送信すると、栄養情報を自動計算して食事記録として保存します。

### 食事記録のCRUD
* **METHOD:** `GET`, `POST`, `PATCH`, `DELETE`
* **ENDPOINT:** `/api/meals/records/`
* **役割:** 食事記録（朝食、昼食など）とそれに含まれる品目を手動で管理します。

## 商品情報 (`products`)

### バーコード検索
* **METHOD:** `GET`
* **ENDPOINT:** `/api/products/lookup/<barcode>/`
* **役割:** 商品のバーコード番号を元に、Open Food Facts APIを利用して商品名や栄養情報を取得します。結果はキャッシュされます。

## レポート (`reports`)

### 歩数ランキング
* **METHOD:** `GET`
* **ENDPOINT:** `/api/reports/steps-ranking/<YYYY-MM-DD>/`
* **役割:** 指定された日付の歩数ランキングと、自分の順位や全体の統計情報を取得します。

### 睡眠リズムランキング
* **METHOD:** `GET`
* **ENDPOINT:** `/api/reports/sleep-rhythm-ranking/`
* **役割:** 社会的ジェットラグ（体内時計のズレ）が少ない順のランキングを取得します。