let currentChart = null;

document.getElementById('company-select').addEventListener('change', function() {
    const company = this.value;
    if (company) {
        loadCompanyData(company);
    } else {
        document.getElementById('dashboard-content').classList.add('hidden');
    }
});

async function loadCompanyData(company) {
    try {
        const response = await fetch(`/api/company/${company}`);
        const data = await response.json();
        
        if (data.error) {
            alert(data.error);
            return;
        }
        
        displayScores(data);
        displayChart(data);
        displayNews(data);
        
        document.getElementById('dashboard-content').classList.remove('hidden');
    } catch (error) {
        console.error('Error loading company data:', error);
        alert('Failed to load company data');
    }
}

function displayScores(data) {
    const categories = ['Environmental', 'Social', 'Governance'];
    const ids = ['env', 'social', 'gov'];
    
    categories.forEach((category, index) => {
        const id = ids[index];
        const original = data.original_scores[category];
        const adjusted = data.adjusted_scores[category];
        
        if (original) {
            document.getElementById(`${id}-original`).textContent = original.score;
        }
        
        if (adjusted) {
            document.getElementById(`${id}-adjusted`).textContent = adjusted.score;
            const arrow = document.getElementById(`${id}-arrow`);
            
            if (adjusted.score > original.score) {
                arrow.textContent = '↑';
                arrow.className = 'arrow up';
            } else if (adjusted.score < original.score) {
                arrow.textContent = '↓';
                arrow.className = 'arrow down';
            } else {
                arrow.textContent = '→';
                arrow.className = 'arrow';
            }
        } else {
            document.getElementById(`${id}-adjusted`).textContent = '-';
            document.getElementById(`${id}-arrow`).textContent = '';
        }
    });
}

function displayChart(data) {
    const ctx = document.getElementById('breakdown-chart').getContext('2d');
    
    if (currentChart) {
        currentChart.destroy();
    }
    
    const labels = [];
    const originalScores = [];
    const adjustedScores = [];
    
    Object.entries(data.original_scores).forEach(([category, categoryData]) => {
        categoryData.metrics.forEach(metric => {
            labels.push(metric.metric);
            originalScores.push(metric.score);
            adjustedScores.push(metric.adjusted_score || metric.score);
        });
    });
    
    currentChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Self-Reported Score',
                    data: originalScores,
                    backgroundColor: 'rgba(149, 165, 166, 0.7)',
                    borderColor: 'rgba(149, 165, 166, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Adjusted Score',
                    data: adjustedScores,
                    backgroundColor: 'rgba(102, 126, 234, 0.7)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 5
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            const index = context.dataIndex;
                            const original = originalScores[index];
                            const adjusted = adjustedScores[index];
                            const diff = (adjusted - original).toFixed(2);
                            if (diff != 0) {
                                return `Change: ${diff > 0 ? '+' : ''}${diff}`;
                            }
                            return '';
                        }
                    }
                }
            }
        }
    });
}

function displayNews(data) {
    const newsContainer = document.getElementById('news-articles');
    
    if (!data.news_articles || data.news_articles.length === 0) {
        newsContainer.innerHTML = '<p class="placeholder">No news articles analyzed yet</p>';
        return;
    }
    
    newsContainer.innerHTML = data.news_articles.map(article => `
        <div class="news-article">
            <h4>${article.title}</h4>
            <p>${article.summary || 'No summary available'}</p>
            ${article.date ? `<p style="color: #7f8c8d; font-size: 0.9em; margin-top: 5px;">Date: ${article.date}</p>` : ''}
            <div class="impact">
                ${Object.entries(article.impact || {}).map(([metric, score]) => {
                    const isPositive = score > 0;
                    return `<span class="impact-badge ${isPositive ? 'positive' : 'negative'}">
                        ${metric}: ${score > 0 ? '+' : ''}${score.toFixed(1)}
                    </span>`;
                }).join('')}
            </div>
        </div>
    `).join('');
}
