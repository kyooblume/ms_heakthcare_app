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
* **役割:** ログイン中のユーザーのプロフィール情報を取得または部分的に更新します。

### オンボーディング状況の確認
* **METHOD:** `GET`
* **ENDPOINT:** `/api/accounts/onboarding-status/`
* **役割:** ユーザーが各アンケートに回答済みかどうかを返します。

## 食事 (`meals`)
### 食事記録の追加（バーコード経由）
* **METHOD:** `POST`
* **ENDPOINT:** `/api/meals/add-from-barcode/`
* **役割:** バーコード番号と食べた量を送信すると、栄養情報を自動計算して食事記録として保存します。

### 食事記録のCRUD
* **METHOD:** `GET`, `POST`, `PATCH`, `DELETE`
* **ENDPOINT:** `/api/meals/records/`
* **役割:** 食事記録（朝食、昼食など）とそれに含まれる品目を手動で管理します。

## アンケート (`surveys`)
### アンケートの一覧取得
* **METHOD:** `GET`
* **ENDPOINT:** `/api/surveys/`
* **役割:** 実施中のアンケートの一覧を取得します。

### アンケートの詳細取得
* **METHOD:** `GET`
* **ENDPOINT:** `/api/surveys/{survey_id}/`
* **役割:** 特定のアンケートのタイトル、説明、質問、選択肢の一覧を取得します。

### 回答の送信
* **METHOD:** `POST`
* **ENDPOINT:** `/api/answers/`
* **役割:** ユーザーからのアンケートの回答を送信します。

## その他
（`products`, `reports`アプリのAPIもここに記載）
