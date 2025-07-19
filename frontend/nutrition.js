// HTMLの要素を取得
const nutritionChartCanvas = document.getElementById('nutritionChart');
const suggestionMessageH3 = document.getElementById('suggestion-message');
const recipeSuggestionsDiv = document.getElementById('recipe-suggestions');
const token = localStorage.getItem('accessToken');

// --- ページが読み込まれたら、データを取得しにいく ---
document.addEventListener('DOMContentLoaded', function() {
    if (!token) {
        alert('ログインが必要です。');
        window.location.href = 'index.html';
        return;
    }
    
    fetchDailyNutrition();
    fetchRecipeSuggestions();
});

// --- 今日の栄養素を取得し、棒グラフを描画する関数 ---
async function fetchDailyNutrition() {
    // (この関数は、以前dashboard.jsにあったものとほぼ同じ)
    const today = new Date().toISOString().split('T')[0];
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/meals/summary/daily/${today}/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('栄養素取得失敗');
        const data = await response.json().then(res => res.summary);
        
        new Chart(nutritionChartCanvas.getContext('2d'), { /* ... グラフ描画コード ... */ });

    } catch (error) {
        console.error('栄養素データの取得エラー:', error);
    }
}

// --- 献立提案を取得し、カードを描画する関数 ---
async function fetchRecipeSuggestions() {
    // (この関数は、以前dashboard.jsにあったものとほぼ同じ)
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/recipes/suggestions/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('献立提案の取得失敗');
        const data = await response.json();
        
        suggestionMessageH3.textContent = data.message;
        
        let html = '';
        // ... (レシピカードを生成するロジック) ...
        recipeSuggestionsDiv.innerHTML = html;

    } catch (error) {
        console.error('献立提案の取得エラー:', error);
    }
}