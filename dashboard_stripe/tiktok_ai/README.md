# TikTok AI Analytics Service

AI-powered TikTok analytics and insights service with OpenAI integration.

## 🚀 Features

### 🤖 AI-Powered Analytics
- **Creator Analysis** - Deep insights into TikTok creator performance
- **Revenue Predictions** - AI-powered earnings estimates and projections
- **Content Strategy** - Personalized content recommendations
- **Trend Detection** - Identify trending topics and viral potential
- **Growth Predictions** - Forecast follower and engagement growth
- **Audience Insights** - Detailed audience demographics and behavior

### 📊 Data Integration
- **TikTok Scraping** - Integration with your existing scraping scripts
- **Caching System** - Intelligent data caching for performance
- **Mock Data** - Fallback data for testing and development
- **Batch Processing** - Analyze multiple creators simultaneously

### ⏰ Automated Features
- **Daily Analytics Updates** - Automatic daily performance tracking
- **Weekly Trend Analysis** - Scheduled trend detection
- **Health Monitoring** - Service health checks and status reporting

## 🛠️ Installation

### 1. Install Dependencies
```bash
cd dashboard_stripe/tiktok_ai
npm install
```

### 2. Set Up Environment
```bash
cp env.example .env
# Edit .env with your OpenAI API key
```

### 3. Configure OpenAI API
Get your OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys) and add it to your `.env` file:
```
OPENAI_API_KEY=sk-your-openai-api-key-here
```

## 🧪 Testing

### Run AI Service Tests
```bash
npm test
```

### Test Individual Components
```bash
# Test AI analytics
node -e "const ai = require('./ai_analytics_service'); console.log('AI Service loaded successfully')"

# Test data integration
node -e "const data = require('./tiktok_data_integration'); console.log('Data Integration loaded successfully')"

# Test full service
node test_ai.js
```

## 📡 API Integration

### Integration with Your Dashboard

Add this to your `dashboard_stripe/server.js`:

```javascript
const aiService = require('./tiktok_ai/ai_service');

// Initialize AI service
aiService.initialize().then(() => {
    console.log('AI Service initialized');
}).catch(console.error);

// AI Analysis endpoint
app.post('/api/ai/analyze', authenticateToken, async (req, res) => {
    try {
        const { username } = req.body;
        const analysis = await aiService.analyzeCreator(username);
        res.json(analysis);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Quick insights endpoint
app.get('/api/ai/insights/:username', authenticateToken, async (req, res) => {
    try {
        const { username } = req.params;
        const insights = await aiService.getQuickInsights(username);
        res.json(insights);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Revenue analysis endpoint
app.get('/api/ai/revenue/:username', authenticateToken, async (req, res) => {
    try {
        const { username } = req.params;
        const revenue = await aiService.getRevenueAnalysis(username);
        res.json(revenue);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Content strategy endpoint
app.get('/api/ai/strategy/:username', authenticateToken, async (req, res) => {
    try {
        const { username } = req.params;
        const strategy = await aiService.getContentStrategy(username);
        res.json(strategy);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});
```

### Frontend Integration

Add this to your `dashboard_stripe/public/script.js`:

```javascript
// AI Analysis Functions
async function getAIAnalysis(username) {
    try {
        const response = await fetch('/api/ai/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ username })
        });
        
        const data = await response.json();
        displayAIAnalysis(data);
    } catch (error) {
        console.error('AI Analysis failed:', error);
    }
}

async function getQuickInsights(username) {
    try {
        const response = await fetch(`/api/ai/insights/${username}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        displayQuickInsights(data);
    } catch (error) {
        console.error('Quick insights failed:', error);
    }
}

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
            </div>
        </div>
    `;
}
```

## 🎯 Usage Examples

### Basic Creator Analysis
```javascript
const aiService = require('./tiktok_ai/ai_service');

// Initialize the service
await aiService.initialize();

// Analyze a creator
const analysis = await aiService.analyzeCreator('@username');
console.log('Analysis:', analysis);
```

### Quick Insights
```javascript
const insights = await aiService.getQuickInsights('@username');
console.log('Quick Insights:', insights);
```

### Revenue Analysis
```javascript
const revenue = await aiService.getRevenueAnalysis('@username');
console.log('Revenue Analysis:', revenue);
```

### Content Strategy
```javascript
const strategy = await aiService.getContentStrategy('@username');
console.log('Content Strategy:', strategy);
```

### Compare Multiple Creators
```javascript
const comparison = await aiService.compareCreators(['@user1', '@user2', '@user3']);
console.log('Comparison:', comparison);
```

## 📊 Data Structure

### Creator Analysis Response
```json
{
  "username": "@username",
  "tiktokData": {
    "followers": 125000,
    "engagementRate": 3.2,
    "recentVideos": [...],
    "topVideos": [...]
  },
  "analysis": {
    "insights": "Growth analysis and recommendations...",
    "recommendations": ["Action item 1", "Action item 2"],
    "actionItems": ["Specific action 1", "Specific action 2"]
  },
  "revenuePrediction": {
    "monthlyEarnings": 8500,
    "breakdown": {
      "brandDeals": 5000,
      "creatorFund": 2000,
      "merchandise": 1500
    },
    "confidence": "high"
  },
  "contentRecommendations": {
    "recommendations": ["Content idea 1", "Content idea 2"],
    "trendingTopics": ["Topic 1", "Topic 2"],
    "optimalTiming": {
      "bestDay": "friday",
      "bestTime": "7:30 PM"
    }
  },
  "trends": {
    "trends": ["Trend 1", "Trend 2"],
    "opportunities": ["Opportunity 1", "Opportunity 2"],
    "warnings": ["Warning 1", "Warning 2"]
  },
  "analytics": {
    "growthRate": {...},
    "engagementTrend": {...},
    "contentPerformance": {...},
    "audienceInsights": {...},
    "revenuePotential": {...}
  },
  "timestamp": "2024-01-15T10:00:00.000Z"
}
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `NODE_ENV` - Environment (development/production)
- `AI_MODEL` - OpenAI model to use (default: gpt-4)
- `AI_MAX_TOKENS` - Maximum tokens for AI responses
- `AI_TEMPERATURE` - AI response creativity (0-1)
- `CACHE_TTL` - Cache duration in seconds
- `SCRAPING_TIMEOUT` - Scraping timeout in milliseconds

### AI Model Configuration
```javascript
// In ai_analytics_service.js
const response = await this.openai.chat.completions.create({
    model: process.env.AI_MODEL || "gpt-4",
    messages: [...],
    max_tokens: parseInt(process.env.AI_MAX_TOKENS) || 800,
    temperature: parseFloat(process.env.AI_TEMPERATURE) || 0.7
});
```

## 🚀 Deployment

### Production Setup
1. Set `NODE_ENV=production` in your environment
2. Ensure OpenAI API key is properly configured
3. Set up proper logging and monitoring
4. Configure rate limiting for API endpoints
5. Set up health checks and monitoring

### Docker Deployment
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3003
CMD ["node", "ai_service.js"]
```

## 📈 Performance

### Caching Strategy
- TikTok data cached for 24 hours
- AI analysis results cached for 1 hour
- Trending topics updated every 6 hours
- Daily analytics run at 2 AM
- Weekly trends analyzed on Sundays at 3 AM

### Rate Limiting
- 100 requests per 15 minutes per user
- OpenAI API calls limited to prevent quota exhaustion
- Automatic retry with exponential backoff

## 🔍 Monitoring

### Health Check
```javascript
const health = await aiService.healthCheck();
console.log('Service Status:', health.status);
```

### Logging
The service includes comprehensive logging:
- AI service initialization
- Data fetching operations
- Error handling and recovery
- Performance metrics
- API usage statistics

## 💰 Cost Estimation

### OpenAI API Costs
- **GPT-4 Analysis**: ~$0.03 per analysis
- **Daily Usage**: ~$1-5 for 1000 users
- **Monthly Cost**: ~$30-150 for active usage

### Revenue Potential
- **AI Analytics Add-on**: $25/month per user
- **Premium AI Features**: $50/month per user
- **ROI**: 10x+ return on AI costs

## 🛡️ Security

### API Key Security
- OpenAI API key stored in environment variables
- Never exposed in client-side code
- Rotated regularly for security

### Data Privacy
- TikTok data cached locally
- No personal data sent to OpenAI
- GDPR compliant data handling

## 🔄 Updates and Maintenance

### Scheduled Tasks
- Daily analytics updates at 2 AM
- Weekly trend analysis on Sundays at 3 AM
- Cache cleanup every 24 hours
- Health check every 5 minutes

### Version Updates
- Check for OpenAI API updates
- Monitor for new TikTok scraping methods
- Update AI prompts for better insights
- Optimize performance and costs

## 🆘 Troubleshooting

### Common Issues

**OpenAI API Key Error**
```bash
# Check if API key is set
echo $OPENAI_API_KEY

# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

**Scraping Script Not Found**
```bash
# Check if Python scripts exist
ls -la ../../tiktok_scraping_scripts/

# Test Python execution
python3 ../../tiktok_scraping_scripts/1_profile_scraper.py --help
```

**Cache Issues**
```bash
# Clear cache
rm -rf cache/

# Check cache directory
ls -la cache/
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=debug
node test_ai.js
```

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Test individual components
4. Verify environment configuration

**Ready to integrate AI-powered analytics into your TikTok Analytics Pro platform!**
