// HTMLの要素を取得
const usernameSpan = document.getElementById('username');
const targetWeightSpan = document.getElementById('target-weight');
const targetStepsSpan = document.getElementById('target-steps');
const logoutButton = document.getElementById('logout-button');
const stepsTextDiv = document.getElementById('steps-text'); // 歩数表示用のdivを追加

// --- ページが読み込まれたら、全てのデータを取得しにいく ---
document.addEventListener('DOMContentLoaded', function() {
    // 最初にプロフィールを読み込み、その後で他のデータを読み込む
    fetchProfile();
    fetchDailyActivity();
    fetchWeeklySleep();
});

// --- 認証が必要なAPIを叩くための関数 ---
async function fetchProfile() {
    // 1. ログイン時にブラウザに保存したアクセストークンを取得
    const token = localStorage.getItem('accessToken');

    if (!token) {
        // もしトークンがなければ、未ログイン状態なのでログイン画面に戻す
        alert('ログインが必要です。');
        window.location.href = 'index.html';
        return;
    }

    try {
        // 2. 「Authorization」ヘッダーにトークンを載せて、プロフィールAPIにリクエスト
        const response = await fetch('http://127.0.0.1:8000/api/accounts/profile/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}` 
            }
        });

        if (response.ok) {
            // 3. 成功！返ってきたデータを画面に表示
            const data = await response.json();
            usernameSpan.textContent = data.username;
            targetWeightSpan.textContent = data.target_weight || '未設定';
            targetStepsSpan.textContent = data.target_steps_per_day || '未設定';
        } else {
            // 4. トークンの有効期限が切れている、などのエラーの場合
            console.error('プロフィールの取得に失敗:', await response.json());
            alert('セッションが切れました。再度ログインしてください。');
            localStorage.removeItem('accessToken');
            window.location.href = 'index.html';
        }
    } catch (error) {
        console.error('通信エラー:', error);
        alert('サーバーとの通信に失敗しました。');
    }
}

// --- ★ここから新しい関数を追加 ---

// --- 今日の活動量を取得し、ドーナツグラフを描画する関数 ---
async function fetchDailyActivity() {
    const token = localStorage.getItem('accessToken');
    const today = new Date().toISOString().split('T')[0]; // 今日の日付を YYYY-MM-DD 形式で取得
    
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/reports/activity/daily/${today}/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('活動量取得失敗');
        const data = await response.json();
        
        // ドーナツグラフを描画
        const ctx = document.getElementById('stepsChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['達成済み', '残り'],
                datasets: [{
                    data: [data.steps.actual, Math.max(0, data.steps.target - data.steps.actual)],
                    backgroundColor: ['#5cb85c', '#f0f0f0'],
                    borderWidth: 0
                }]
            },
            options: { cutout: '70%', plugins: { legend: { display: false } } }
        });

        // グラフの中央に歩数を表示
        stepsTextDiv.textContent = `${data.steps.actual} 歩`;

    } catch (error) {
        console.error('活動量データの取得エラー:', error);
    }
}

// --- 週間睡眠記録を取得し、棒グラフを描画する関数 ---
async function fetchWeeklySleep() {
    const token = localStorage.getItem('accessToken');
    
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/reports/sleep/weekly/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('睡眠記録取得失敗');
        const data = await response.json();
        
        // 棒グラフを描画
        const ctx = document.getElementById('sleepChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(data), // 日付の配列
                datasets: [{
                    label: '睡眠時間 (h)',
                    data: Object.values(data), // 睡眠時間の配列
                    backgroundColor: '#5bc0de',
                }]
            },
            options: { scales: { y: { beginAtZero: true } }, plugins: { legend: { display: false } } }
        });
    } catch (error) {
        console.error('睡眠データの取得エラー:', error);
    }
}

// --- ★ここまで追加 ---


// --- ログアウトボタンの処理 ---
logoutButton.addEventListener('click', () => {
    localStorage.removeItem('accessToken');
    alert('ログアウトしました。');
    window.location.href = 'index.html';
});