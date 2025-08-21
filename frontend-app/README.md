
# ログインアプリケーション (frontend-app)

これは、[Expo](https://expo.dev/) と [React Native](https://reactnative.dev/) を使用して作成されたシンプルなログインアプリケーションです。

## 概要

このアプリケーションは、ユーザーがユーザー名とパスワードを入力してログインするための基本的なフロントエンド機能を提供します。入力された情報はバックエンドのAPIに送信され、認証が行われます。

## 主な機能

  * ユーザー名とパスワードの入力フォーム
  * ログインボタンによる認証情報の送信
  * 認証結果（成功・失敗）のアラート表示
  * 通信エラーが発生した場合のアラート表示

## セットアップと実行方法

### 必要なもの

  * [Node.js](https://nodejs.org/)
  * [Expo CLI](https://docs.expo.dev/get-started/installation/)

<!-- end list -->

```bash
npm install -g expo-cli
```

### インストール

1.  このリポジトリをクローンします。
2.  プロジェクトのルートディレクトリで、依存関係をインストールします。

<!-- end list -->

```bash
npm install
```

### アプリケーションの実行

以下のコマンドで、開発サーバーを起動します。

```bash
npm start
```

または `expo start` を使用することもできます。

実行後、表示されるQRコードをExpo Goアプリ（iOSまたはAndroid）でスキャンすることで、お使いのデバイスでアプリケーションを起動できます。

また、以下のコマンドで特定のプラットフォーム向けに直接起動することも可能です。

  * **Android:**
    ```bash
    npm run android
    ```
  * **iOS:**
    ```bash
    npm run ios
    ```
  * **Web:**
    ```bash
    npm run web
    ```

## 設定

このアプリケーションは、バックエンドの認証APIと通信します。APIのエンドポイントは `frontend-app/App.js` ファイル内で設定されています。

  * **現在のAPIエンドポイント:** `http://10.0.2.2:8000/api/token/`

`10.0.2.2` は、Androidエミュレータからローカルマシン（ホスト）の`localhost`を参照するための特別なIPアドレスです。ご自身の開発環境に合わせて、このURLを適宜変更してください。

## 主な使用ライブラリ

このプロジェクトで使用されている主なライブラリは `frontend-app/package.json` を参照してください。

  * `expo`
  * `react`
  * `react-native`
  * `@react-navigation/native`
  * `@react-navigation/stack`
