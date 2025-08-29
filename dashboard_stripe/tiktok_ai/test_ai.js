const aiService = require('./ai_service');
require('dotenv').config();

async function testAIService() {
    console.log('🧪 Testing TikTok AI Service...\n');
    
    try {
        // Initialize the service
        console.log('1. Initializing AI Service...');
        await aiService.initialize();
        console.log('✅ AI Service initialized successfully\n');
        
        // Test health check
        console.log('2. Testing health check...');
        const health = await aiService.healthCheck();
        console.log('Health Status:', health.status);
        console.log('✅ Health check completed\n');
        
        // Test quick insights
        console.log('3. Testing quick insights...');
        const insights = await aiService.getQuickInsights('testuser');
        console.log('Quick Insights:', {
            username: insights.username,
            followers: insights.followers,
            engagementRate: insights.engagementRate,
            insights: insights.insights.substring(0, 100) + '...',
            recommendations: insights.topRecommendations
        });
        console.log('✅ Quick insights test completed\n');
        
        // Test revenue analysis
        console.log('4. Testing revenue analysis...');
        const revenue = await aiService.getRevenueAnalysis('testuser');
        console.log('Revenue Analysis:', {
            username: revenue.username,
            currentMetrics: revenue.currentMetrics,
            revenuePrediction: revenue.revenuePrediction,
            revenuePotential: revenue.revenuePotential
        });
        console.log('✅ Revenue analysis test completed\n');
        
        // Test content strategy
        console.log('5. Testing content strategy...');
        const strategy = await aiService.getContentStrategy('testuser');
        console.log('Content Strategy:', {
            username: strategy.username,
            recommendations: strategy.contentRecommendations,
            trends: strategy.trends,
            performanceInsights: strategy.performanceInsights
        });
        console.log('✅ Content strategy test completed\n');
        
        // Test trending topics
        console.log('6. Testing trending topics...');
        const trends = await aiService.getTrendingTopics();
        console.log('Trending Topics:', trends.trendingTopics);
        console.log('✅ Trending topics test completed\n');
        
        // Test audience insights
        console.log('7. Testing audience insights...');
        const audience = await aiService.getAudienceInsights('testuser');
        console.log('Audience Insights:', {
            username: audience.username,
            demographics: audience.demographics,
            interests: audience.interests.slice(0, 5),
            activeHours: audience.activeHours
        });
        console.log('✅ Audience insights test completed\n');
        
        // Test growth predictions
        console.log('8. Testing growth predictions...');
        const predictions = await aiService.getGrowthPredictions('testuser');
        console.log('Growth Predictions:', {
            username: predictions.username,
            currentMetrics: predictions.currentMetrics,
            predictions: predictions.predictions['6months'],
            confidence: predictions.confidence
        });
        console.log('✅ Growth predictions test completed\n');
        
        console.log('🎉 All tests completed successfully!');
        console.log('\n📊 Test Summary:');
        console.log('- ✅ AI Service initialization');
        console.log('- ✅ Health check');
        console.log('- ✅ Quick insights generation');
        console.log('- ✅ Revenue analysis');
        console.log('- ✅ Content strategy generation');
        console.log('- ✅ Trending topics detection');
        console.log('- ✅ Audience insights analysis');
        console.log('- ✅ Growth predictions');
        
    } catch (error) {
        console.error('❌ Test failed:', error);
        process.exit(1);
    }
}

// Run the test if this file is executed directly
if (require.main === module) {
    testAIService();
}

module.exports = { testAIService };
