// Example: How to integrate TikTok AI Service with your dashboard
const aiService = require('./ai_service');

// Example 1: Add AI endpoints to your dashboard server
async function addAIToDashboard(app) {
    // Initialize AI service when dashboard starts
    await aiService.initialize();
    
    // AI Analysis endpoint
    app.post('/api/ai/analyze', async (req, res) => {
        try {
            const { username } = req.body;
            const analysis = await aiService.analyzeCreator(username);
            res.json(analysis);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    });
    
    // Quick insights endpoint
    app.get('/api/ai/insights/:username', async (req, res) => {
        try {
            const { username } = req.params;
            const insights = await aiService.getQuickInsights(username);
            res.json(insights);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    });
    
    // Revenue analysis endpoint
    app.get('/api/ai/revenue/:username', async (req, res) => {
        try {
            const { username } = req.params;
            const revenue = await aiService.getRevenueAnalysis(username);
            res.json(revenue);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    });
    
    // Content strategy endpoint
    app.get('/api/ai/strategy/:username', async (req, res) => {
        try {
            const { username } = req.params;
            const strategy = await aiService.getContentStrategy(username);
            res.json(strategy);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    });
    
    // Trending topics endpoint
    app.get('/api/ai/trends', async (req, res) => {
        try {
            const trends = await aiService.getTrendingTopics();
            res.json(trends);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    });
    
    // Health check endpoint
    app.get('/api/ai/health', async (req, res) => {
        try {
            const health = await aiService.healthCheck();
            res.json(health);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    });
}

// Example 2: Frontend JavaScript functions
const frontendAIFunctions = {
    // Get AI analysis for a creator
    async getAIAnalysis(username) {
        try {
            const response = await fetch('/api/ai/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify({ username })
            });
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('AI Analysis failed:', error);
            throw error;
        }
    },
    
    // Get quick insights
    async getQuickInsights(username) {
        try {
            const response = await fetch(`/api/ai/insights/${username}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Quick insights failed:', error);
            throw error;
        }
    },
    
    // Get revenue analysis
    async getRevenueAnalysis(username) {
        try {
            const response = await fetch(`/api/ai/revenue/${username}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Revenue analysis failed:', error);
            throw error;
        }
    },
    
    // Get content strategy
    async getContentStrategy(username) {
        try {
            const response = await fetch(`/api/ai/strategy/${username}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Content strategy failed:', error);
            throw error;
        }
    },
    
    // Get trending topics
    async getTrendingTopics() {
        try {
            const response = await fetch('/api/ai/trends', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Trending topics failed:', error);
            throw error;
        }
    }
};

// Example 3: Display AI insights in the dashboard
function displayAIAnalysis(data) {
    const aiSection = document.getElementById('ai-insights');
    
    aiSection.innerHTML = `
        <div class="ai-insight-card">
            <h3>🤖 AI Analysis for @${data.username}</h3>
            <div class="insight-content">
                <h4>Growth Insights</h4>
                <p>${data.analysis.insights}</p>
                
                <h4>Top Recommendations</h4>
                <ul>
                    ${data.analysis.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
                
                <h4>Revenue Prediction</h4>
                <p>Monthly Earnings: $${data.revenuePrediction.monthlyEarnings}</p>
                <p>Confidence: ${data.revenuePrediction.confidence}</p>
                
                <h4>Content Strategy</h4>
                <ul>
                    ${data.contentRecommendations.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
                
                <h4>Trending Topics</h4>
                <ul>
                    ${data.trends.trends.map(trend => `<li>${trend}</li>`).join('')}
                </ul>
            </div>
        </div>
    `;
}

// Example 4: Add AI button to dashboard
function addAIAnalysisButton() {
    const dashboardContent = document.querySelector('.dashboard-content');
    
    const aiButton = document.createElement('button');
    aiButton.className = 'btn-primary ai-analysis-btn';
    aiButton.innerHTML = '🤖 Get AI Analysis';
    aiButton.onclick = async () => {
        const username = prompt('Enter TikTok username to analyze:');
        if (username) {
            try {
                const analysis = await frontendAIFunctions.getAIAnalysis(username);
                displayAIAnalysis(analysis);
            } catch (error) {
                alert('AI analysis failed. Please try again.');
            }
        }
    };
    
    dashboardContent.insertBefore(aiButton, dashboardContent.firstChild);
}

// Example 5: Usage in your dashboard
async function integrateAIWithDashboard() {
    console.log('Integrating AI with dashboard...');
    
    // Add AI button when dashboard loads
    addAIAnalysisButton();
    
    // Example: Get trending topics on page load
    try {
        const trends = await frontendAIFunctions.getTrendingTopics();
        console.log('Trending topics:', trends);
        
        // Display trending topics in dashboard
        const trendsSection = document.getElementById('trending-topics');
        if (trendsSection) {
            trendsSection.innerHTML = `
                <h3>🔥 Trending Topics</h3>
                <div class="trends-grid">
                    ${trends.trendingTopics.map(topic => `
                        <div class="trend-card">
                            <h4>${topic.topic}</h4>
                            <p>Trend: ${topic.trend}</p>
                            <p>Engagement: ${topic.engagement}</p>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    } catch (error) {
        console.error('Failed to load trending topics:', error);
    }
}

// Example 6: Real-time AI insights
function setupRealTimeAIInsights() {
    // Update AI insights every 5 minutes
    setInterval(async () => {
        try {
            const currentUser = JSON.parse(localStorage.getItem('currentUser'));
            if (currentUser && currentUser.tiktokUsername) {
                const insights = await frontendAIFunctions.getQuickInsights(currentUser.tiktokUsername);
                
                // Update insights in real-time
                const insightsSection = document.getElementById('real-time-insights');
                if (insightsSection) {
                    insightsSection.innerHTML = `
                        <h4>⚡ Real-time Insights</h4>
                        <p>${insights.insights.substring(0, 200)}...</p>
                        <small>Updated: ${new Date().toLocaleTimeString()}</small>
                    `;
                }
            }
        } catch (error) {
            console.error('Real-time insights update failed:', error);
        }
    }, 5 * 60 * 1000); // 5 minutes
}

// Export functions for use in your dashboard
module.exports = {
    addAIToDashboard,
    frontendAIFunctions,
    displayAIAnalysis,
    addAIAnalysisButton,
    integrateAIWithDashboard,
    setupRealTimeAIInsights
};

// Example usage:
// 1. In your server.js: addAIToDashboard(app)
// 2. In your script.js: integrateAIWithDashboard()
// 3. In your HTML: Add <div id="ai-insights"></div>
