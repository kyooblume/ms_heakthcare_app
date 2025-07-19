// HTMLの要素を取得
const usernameSpan = document.getElementById('username');
const targetWeightSpan = document.getElementById('target-weight');
const targetStepsSpan = document.getElementById('target-steps');
const logoutButton = document.getElementById('logout-button');
const stepsTextDiv = document.getElementById('steps-text');
const token = localStorage.getItem('accessToken');
const weeklyAvgStepsSpan = document.getElementById('weekly-avg-steps');
const monthlyAvgStepsSpan = document.getElementById('monthly-avg-steps');

// --- ページが読み込まれたら、全てのデータを取得しにいく ---
document.addEventListener('DOMContentLoaded', function() {
    if (!token) {
        alert('ログインが必要です。');
        window.location.href = 'index.html';
        return;
    }
    
    // 4つのAPIを並行して呼び出す
    fetchProfile();
    fetchDailyActivity();
    fetchWeeklySleep();
    fetchDailyNutrition(); // ★ 栄養素取得の関数を追加
});


// --- 1. プロフィール情報を取得する関数 ---
async function fetchProfile() {
    // (この関数は変更なし)
    try {
        const response = await fetch('http://127.0.0.1:8000/api/accounts/profile/', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('プロフィール取得失敗');
        const data = await response.json();
        usernameSpan.textContent = data.username;
        targetWeightSpan.textContent = data.target_weight || '未設定';
        targetStepsSpan.textContent = data.target_steps_per_day || '未設定';
    } catch (error) {
        handleAuthError(error);
    }
}

// --- 2. 今日の活動量を取得し、ドーナツグラフを描画する関数 ---
async function fetchDailyActivity() {
    // (この関数は変更なし)
    const today = new Date().toISOString().split('T')[0];
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/reports/activity/daily/${today}/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('活動量取得失敗');
        const data = await response.json();
        
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
        stepsTextDiv.textContent = `${data.steps.actual} 歩`;
    } catch (error) {
        console.error('活動量データの取得エラー:', error);
    }
}

// --- 3. 週間睡眠記録を取得し、棒グラフを描画する関数 ---
async function fetchWeeklySleep() {
    // (この関数は変更なし)
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/reports/sleep/weekly/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('睡眠記録取得失敗');
        const data = await response.json();
        
        const ctx = document.getElementById('sleepChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(data).map(date => new Date(date).toLocaleDateString('ja-JP', { month: 'numeric', day: 'numeric' })),
                datasets: [{
                    label: '睡眠時間 (h)',
                    data: Object.values(data),
                    backgroundColor: '#5bc0de',
                }]
            },
            options: { scales: { y: { beginAtZero: true } }, plugins: { legend: { display: false } } }
        });
    } catch (error) {
        console.error('睡眠データの取得エラー:', error);
    }
}

// --- ★ 4. 今日の栄養素を取得し、棒グラフを描画する関数を追加 ★ ---
async function fetchDailyNutrition() {
    const today = new Date().toISOString().split('T')[0];

    try {
        const response = await fetch(`http://127.0.0.1:8000/api/meals/summary/daily/${today}/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        console.log('📦 レスポンスステータス:', response.status);

        if (!response.ok) {
            const errorText = await response.text();  // HTMLなどが返ってきた場合の表示用
            console.error('❌ サーバーエラーレスポンス:', errorText);
            throw new Error('栄養素取得失敗');
        }

        const rawData = await response.json();
        console.log('✅ 受信データ:', rawData);

        const data = rawData.summary;

        const ctx = document.getElementById('nutritionChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['カロリー(kcal)', 'タンパク質(g)', '脂質(g)', '炭水化物(g)'],
                datasets: [
                    {
                        label: '目標値',
                        data: [data.calories.target, data.protein.target, data.fat.target, data.carbohydrate.target],
                        backgroundColor: '#f0ad4e',
                    },
                    {
                        label: '摂取量',
                        data: [data.calories.actual, data.protein.actual, data.fat.actual, data.carbohydrate.actual],
                        backgroundColor: '#5cb85c',
                    }
                ]
            },
            options: {
                responsive: true,
                scales: { y: { beginAtZero: true } },
                plugins: { legend: { position: 'top' } }
            }
        });
    } catch (error) {
        console.error('❗ 栄養素データの取得エラー:', error);
    }
}

async function fetchDashboardData() {
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/reports/dashboard-summary/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('ダッシュボードデータ取得失敗');
        const data = await response.json();
        
        // --- 歩数グラフとサマリーの描画 ---
        const activity = data.activity;
        stepsTextDiv.textContent = `${activity.today_steps} 歩`;
        weeklyAvgStepsSpan.textContent = activity.weekly_average_steps;
        monthlyAvgStepsSpan.textContent = activity.monthly_average_steps;

        const stepsCtx = document.getElementById('stepsChart').getContext('2d');
        new Chart(stepsCtx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [activity.today_steps, Math.max(0, activity.target_steps - activity.today_steps)],
                    backgroundColor: ['#5cb85c', '#f0f0f0'],
                    borderWidth: 0
                }]
            },
            options: { cutout: '70%', plugins: { legend: { display: false } } }
        });

        // --- 睡眠グラフの描画 ---
        const sleep = data.sleep;
        const sleepCtx = document.getElementById('sleepChart').getContext('2d');
        new Chart(sleepCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(sleep.weekly_summary),
                datasets: [{
                    label: '睡眠時間 (h)',
                    data: Object.values(sleep.weekly_summary),
                    backgroundColor: '#5bc0de',
                }]
            },
            options: { scales: { y: { beginAtZero: true } }, plugins: { legend: { display: false } } }
        });

    } catch (error) {
        console.error('ダッシュボードデータの取得エラー:', error);
        // ここでエラー時の表示処理を行う
    }
}





// --- ログアウト処理 ---
logoutButton.addEventListener('click', () => {
    // (この関数は変更なし)
    localStorage.removeItem('accessToken');
    alert('ログアウトしました。');
    window.location.href = 'index.html';
});

// --- 認証エラー時の共通処理 ---
function handleAuthError(error) {
    // (この関数は変更なし)
    console.error('認証エラーまたは通信エラー:', error);
    localStorage.removeItem('accessToken');
    window.location.href = 'index.html';
}


