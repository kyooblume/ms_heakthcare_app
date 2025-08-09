import React, { useState } from 'react';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, Alert } from 'react-native';

export default function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    try {
      // 1. バックエンドのAPIに、POSTリクエストを送信
      const response = await fetch('http://10.0.2.2:8000/api/token/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username,
          password: password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // 2. ログイン成功！
        Alert.alert('成功', 'ログインしました！');
        // ここで、取得したトークンを保存し、次の画面に移動する処理を書きます
        // (例: AsyncStorage.setItem('accessToken', data.access); navigation.navigate('Dashboard');)
      } else {
        // 3. ログイン失敗...
        Alert.alert('エラー', 'ユーザー名またはパスワードが間違っています。');
      }
    } catch (error) {
      // 4. サーバーに接続できないなどのエラー
      console.error(error);
      Alert.alert('通信エラー', 'サーバーに接続できませんでした。');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>ログイン</Text>
      
      <TextInput
        style={styles.input}
        placeholder="ユーザー名"
        value={username}
        onChangeText={setUsername}
        autoCapitalize="none"
      />
      
      <TextInput
        style={styles.input}
        placeholder="パスワード"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />

      <TouchableOpacity style={styles.button} onPress={handleLogin}>
        <Text style={styles.buttonText}>ログイン</Text>
      </TouchableOpacity>
    </View>
  );
}

// CSSの代わりに、StyleSheetで見た目を定義します
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f4f4f9',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 30,
  },
  input: {
    width: '100%',
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15,
    fontSize: 16,
  },
  button: {
    width: '100%',
    backgroundColor: '#5cb85c',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
});