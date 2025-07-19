// HTMLの要素を取得
const surveyContentDiv = document.getElementById('survey-content');
const token = localStorage.getItem('accessToken');

// TIPI-Jの質問項目（フロントエンドで管理）
const tipiQuestions = [
    { id: 'q1', text: '自分は、活発で、外向的だと思う', trait: 'extraversion', reverse: false },
    { id: 'q2', text: '自分は、他人に不満をもち、もめごとを起こしやすいと思う', trait: 'agreeableness', reverse: true },
    { id: 'q3', text: '自分は、しっかりしていて、自分を律することができると思う', trait: 'conscientiousness', reverse: false },
    { id: 'q4', text: '自分は、心配性で、うろたえやすいと思う', trait: 'neuroticism', reverse: false },
    { id: 'q5', text: '自分は、新しいことを受け入れ、変わった考えをもっていると思う', trait: 'openness', reverse: false },
    { id: 'q6', text: '自分は、無口で、物静かだと思う', trait: 'extraversion', reverse: true },
    { id: 'q7', text: '自分は、思いやりがあり、優しい人間だと思う', trait: 'agreeableness', reverse: false },
    { id: 'q8', text: '自分は、だらしなく、うっかりしていると思う', trait: 'conscientiousness', reverse: true },
    { id: 'q9', text: '自分は、冷静で、気分が安定していると思う', trait: 'neuroticism', reverse: true },
    { id: 'q10', text: '自分は、発想が平凡で、独創的ではないと思う', trait: 'openness', reverse: true }
];

// --- 1. 最初にユーザーの状態を確認しにいく関数 ---
async function checkOnboardingStatus() {
    if (!token) {
        window.location.href = 'index.html'; // トークンがなければログイン画面へ
        return;
    }

    try {
        const response = await fetch('http://127.0.0.1:8000/api/accounts/onboarding-status/', {
            headers: { 
                'Authorization': `Bearer ${token}`,  // ← Bearer に統一
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                // トークンが無効な場合はログアウト処理
                localStorage.removeItem('accessToken');
                window.location.href = 'index.html';
                return;
            }
            throw new Error('ステータスの取得に失敗');
        }

        const status = await response.json();

        // 2. バックエンドからの指示に従って、表示するコンテンツを決める
        if (status.needs_big5_survey) {
            displayBigFiveSurvey(); // BigFiveアンケートを表示
        } else {
            // 全ての初期設定が終わっていれば、ダッシュボードに移動
            window.location.href = 'dashboard.html';
        }

    } catch (error) {
        console.error(error);
        surveyContentDiv.innerHTML = '<p style="color:red;">エラーが発生しました。再読み込みしてください。</p>';
    }
}


// --- 3. BigFiveアンケートを画面に表示する関数 ---
function displayBigFiveSurvey() {
    let html = '<h2>性格診断アンケート</h2><form id="big5-form">';
    html += '<p>各項目について、自分にどれくらい当てはまるか評価してください。(1: 全く当てはまらない ~ 7: 非常に強く当てはまる)</p>';
    
    tipiQuestions.forEach(q => {
        html += `<div class="question">
                    <label>${q.text}</label>
                    <select id="${q.id}" required>`;
        for (let i = 1; i <= 7; i++) {
            html += `<option value="${i}">${i}</option>`;
        }
        html += `</select></div>`;
    });

    html += '<button type="submit">回答を送信</button></form>';
    surveyContentDiv.innerHTML = html;

    // フォームが送信されたときのイベントを設定
    document.getElementById('big5-form').addEventListener('submit', handleBigFiveSubmit);
}


// --- 4. BigFiveの回答を処理・送信する関数 ---
async function handleBigFiveSubmit(event) {
    event.preventDefault();

    // 回答を取得
    const answers = {};
    tipiQuestions.forEach(q => {
        answers[q.id] = parseInt(document.getElementById(q.id).value);
    });

    // スコアを計算
    const scores = {
        big5_openness: ((8 - answers.q10) + answers.q5) / 2,
        big5_conscientiousness: ((8 - answers.q8) + answers.q3) / 2,
        big5_extraversion: ((8 - answers.q6) + answers.q1) / 2,
        big5_agreeableness: ((8 - answers.q2) + answers.q7) / 2,
        big5_neuroticism: ((8 - answers.q9) + answers.q4) / 2,
    };
    
    // オンボーディング完了フラグも一緒に送信
    scores.onboarding_complete = true;

    // APIに送信
    try {
        // デバッグ用：送信データを確認
        console.log('送信データ:', scores);
        
        const response = await fetch('http://127.0.0.1:8000/api/accounts/profile/', {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token}`,  // ← Bearer に統一
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(scores)
        });

        if (!response.ok) {
            // エラーレスポンスの詳細を確認
            const errorData = await response.json().catch(() => null);
            console.error('エラーレスポンス:', errorData);
            
            if (response.status === 401) {
                localStorage.removeItem('accessToken');
                window.location.href = 'index.html';
                return;
            }
            throw new Error(`回答の送信に失敗しました。ステータス: ${response.status}`);
        }

        alert('ありがとうございます！初期設定が完了しました。');
        window.location.href = 'dashboard.html';

    } catch (error) {
        console.error(error);
        alert('エラーが発生しました。もう一度お試しください。');
    }
}


// --- ページが読み込まれたら、すぐに処理を開始 ---
checkOnboardingStatus();