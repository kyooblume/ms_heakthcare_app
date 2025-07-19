// HTMLの要素を取得
const loginForm = document.getElementById('login-form');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const errorMessage = document.getElementById('error-message');

// フォームが送信されたときの処理
loginForm.addEventListener('submit', async function(event) {
    // ページの再読み込みを防ぐ
    event.preventDefault();

    // 入力されたユーザー名とパスワードを取得
    const username = usernameInput.value;
    const password = passwordInput.value;

    try {
        // 1. バックエンドのAPIに、POSTリクエストを送信
        const response = await fetch('http://127.0.0.1:8000/api/token/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                password: password,
            }),
        });

        // 2. サーバーからの応答をJSONとして解析
        const data = await response.json();

        if (response.ok) {
            // 3. ログイン成功！
            console.log('ログイン成功:', data);
            
            // 受け取ったアクセストークンをブラウザに保存
            localStorage.setItem('accessToken', data.access);
            
            // ログイン後のダッシュボード画面に移動
            window.location.href = 'onboarding.html'; // (このファイルは後で作ります)

        } else {
            // 4. ログイン失敗...
            console.error('ログイン失敗:', data);
            errorMessage.textContent = 'ユーザー名またはパスワードが間違っています。';
        }
    } catch (error) {
        // 5. サーバーに接続できないなどのエラー
        console.error('通信エラー:', error);
        errorMessage.textContent = 'サーバーに接続できませんでした。';
    }
});