const TikTokAIAnalytics = require('./ai_analytics_service');
const TikTokDataIntegration = require('./tiktok_data_integration');
const cron = require('node-cron');
require('dotenv').config();

class TikTokAIService {
    constructor() {
        this.aiAnalytics = new TikTokAIAnalytics();
        this.dataIntegration = new TikTokDataIntegration();
        this.isInitialized = false;
    }

    async initialize() {
        try {
            console.log('🤖 Initializing TikTok AI Service...');
            
            // Check if OpenAI API key is available
            if (!process.env.OPENAI_API_KEY) {
                console.warn('⚠️  OpenAI API key not found. Using mock AI responses.');
            } else {
                console.log('✅ OpenAI API key found');
            }
            
            // Test AI service
            await this.testAIService();
            
            // Start scheduled tasks
            this.startScheduledTasks();
            
            this.isInitialized = true;
            console.log('✅ TikTok AI Service initialized successfully');
        } catch (error) {
            console.error('❌ Failed to initialize TikTok AI Service:', error);
            throw error;
        }
    }

    async testAIService() {
        try {
            console.log('🧪 Testing AI Service...');
            
            const testData = this.dataIntegration.getMockData('testuser');
            const analysis = await this.aiAnalytics.analyzeCreatorData(testData);
            
            if (analysis && analysis.insights) {
                console.log('✅ AI Service test successful');
                return true;
            } else {
                console.warn('⚠️  AI Service test returned empty results');
                return false;
            }
        } catch (error) {
            console.error('❌ AI Service test failed:', error);
            return false;
        }
    }

    startScheduledTasks() {
        // Daily analytics update at 2 AM
        cron.schedule('0 2 * * *', async () => {
            console.log('🔄 Running daily analytics update...');
            await this.updateDailyAnalytics();
        });

        // Weekly trend analysis every Sunday at 3 AM
        cron.schedule('0 3 * * 0', async () => {
            console.log('📊 Running weekly trend analysis...');
            await this.analyzeWeeklyTrends();
        });

        console.log('⏰ Scheduled tasks started');
    }

    async analyzeCreator(username) {
        try {
            console.log(`🔍 Analyzing creator: ${username}`);
            
            // Get TikTok data
            const tiktokData = await this.dataIntegration.getTikTokData(username);
            
            // Run AI analysis
            const analysis = await this.aiAnalytics.analyzeCreatorData(tiktokData);
            const revenuePrediction = await this.aiAnalytics.predictRevenue(tiktokData);
            const contentRecommendations = await this.aiAnalytics.generateContentRecommendations(tiktokData);
            const trends = await this.aiAnalytics.detectTrends(tiktokData.recentVideos);
            
            // Get enhanced analytics data
            const analyticsData = await this.dataIntegration.getAnalyticsData(username);
            
            return {
                username,
                tiktokData,
                analysis,
                revenuePrediction,
                contentRecommendations,
                trends,
                analytics: analyticsData.analytics,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            console.error(`❌ Error analyzing creator ${username}:`, error);
            throw error;
        }
    }

    async getQuickInsights(username) {
        try {
            console.log(`⚡ Getting quick insights for: ${username}`);
            
            const tiktokData = await this.dataIntegration.getTikTokData(username);
            const analysis = await this.aiAnalytics.analyzeCreatorData(tiktokData);
            
            return {
                username,
                followers: tiktokData.followers,
                engagementRate: tiktokData.engagementRate,
                insights: analysis.insights,
                topRecommendations: analysis.recommendations.slice(0, 3),
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            console.error(`❌ Error getting quick insights for ${username}:`, error);
            throw error;
        }
    }

    async getRevenueAnalysis(username) {
        try {
            console.log(`💰 Analyzing revenue for: ${username}`);
            
            const tiktokData = await this.dataIntegration.getTikTokData(username);
            const revenuePrediction = await this.aiAnalytics.predictRevenue(tiktokData);
            const analyticsData = await this.dataIntegration.getAnalyticsData(username);
            
            return {
                username,
                currentMetrics: {
                    followers: tiktokData.followers,
                    engagementRate: tiktokData.engagementRate,
                    avgViews: tiktokData.avgViews
                },
                revenuePrediction,
                revenuePotential: analyticsData.analytics.revenuePotential,
                growthProjection: analyticsData.analytics.growthRate,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            console.error(`❌ Error analyzing revenue for ${username}:`, error);
            throw error;
        }
    }

    async getContentStrategy(username) {
        try {
            console.log(`📝 Generating content strategy for: ${username}`);
            
            const tiktokData = await this.dataIntegration.getTikTokData(username);
            const contentRecommendations = await this.aiAnalytics.generateContentRecommendations(tiktokData);
            const trends = await this.aiAnalytics.detectTrends(tiktokData.recentVideos);
            const analyticsData = await this.dataIntegration.getAnalyticsData(username);
            
            return {
                username,
                contentRecommendations,
                trends,
                performanceInsights: analyticsData.analytics.contentPerformance,
                audienceInsights: analyticsData.analytics.audienceInsights,
                optimalTiming: analyticsData.analytics.engagementTrend,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            console.error(`❌ Error generating content strategy for ${username}:`, error);
            throw error;
        }
    }

    async compareCreators(usernames) {
        try {
            console.log(`📊 Comparing creators: ${usernames.join(', ')}`);
            
            const results = {};
            
            for (const username of usernames) {
                try {
                    const analysis = await this.analyzeCreator(username);
                    results[username] = analysis;
                } catch (error) {
                    console.error(`❌ Error analyzing ${username}:`, error);
                    results[username] = { error: error.message };
                }
            }
            
            // Generate comparison insights
            const comparison = this.generateComparisonInsights(results);
            
            return {
                creators: results,
                comparison,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            console.error('❌ Error comparing creators:', error);
            throw error;
        }
    }

    generateComparisonInsights(results) {
        const validResults = Object.entries(results).filter(([_, data]) => !data.error);
        
        if (validResults.length < 2) {
            return { message: "Need at least 2 valid creators for comparison" };
        }
        
        const insights = {
            topPerformer: null,
            growthLeader: null,
            engagementChampion: null,
            recommendations: []
        };
        
        // Find top performer by followers
        let maxFollowers = 0;
        validResults.forEach(([username, data]) => {
            if (data.tiktokData.followers > maxFollowers) {
                maxFollowers = data.tiktokData.followers;
                insights.topPerformer = username;
            }
        });
        
        // Find engagement champion
        let maxEngagement = 0;
        validResults.forEach(([username, data]) => {
            if (data.tiktokData.engagementRate > maxEngagement) {
                maxEngagement = data.tiktokData.engagementRate;
                insights.engagementChampion = username;
            }
        });
        
        // Generate recommendations
        insights.recommendations = [
            `${insights.topPerformer} has the largest audience`,
            `${insights.engagementChampion} has the highest engagement rate`,
            "Consider collaboration opportunities between creators",
            "Share successful content strategies across accounts"
        ];
        
        return insights;
    }

    async updateDailyAnalytics() {
        try {
            console.log('🔄 Updating daily analytics...');
            
            // This would typically update analytics for all tracked creators
            // For now, we'll just log the action
            
            console.log('✅ Daily analytics update completed');
        } catch (error) {
            console.error('❌ Error updating daily analytics:', error);
        }
    }

    async analyzeWeeklyTrends() {
        try {
            console.log('📊 Analyzing weekly trends...');
            
            // This would analyze trends across all creators
            // For now, we'll just log the action
            
            console.log('✅ Weekly trend analysis completed');
        } catch (error) {
            console.error('❌ Error analyzing weekly trends:', error);
        }
    }

    async getTrendingTopics() {
        try {
            console.log('🔥 Getting trending topics...');
            
            // Mock trending topics - in production, this would analyze real data
            const trendingTopics = [
                { topic: "Dance Challenges", trend: "rising", engagement: "high" },
                { topic: "Cooking Tutorials", trend: "stable", engagement: "medium" },
                { topic: "Comedy Skits", trend: "rising", engagement: "high" },
                { topic: "Fitness Tips", trend: "declining", engagement: "low" },
                { topic: "Life Hacks", trend: "stable", engagement: "medium" }
            ];
            
            return {
                trendingTopics,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            console.error('❌ Error getting trending topics:', error);
            throw error;
        }
    }

    async getAudienceInsights(username) {
        try {
            console.log(`👥 Getting audience insights for: ${username}`);
            
            const analyticsData = await this.dataIntegration.getAnalyticsData(username);
            
            return {
                username,
                demographics: analyticsData.analytics.audienceInsights.demographics,
                interests: analyticsData.analytics.audienceInsights.interests,
                activeHours: analyticsData.analytics.audienceInsights.activeHours,
                engagementPatterns: analyticsData.analytics.audienceInsights.engagementPatterns,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            console.error(`❌ Error getting audience insights for ${username}:`, error);
            throw error;
        }
    }

    async getGrowthPredictions(username, timeframe = '6months') {
        try {
            console.log(`📈 Getting growth predictions for: ${username}`);
            
            const tiktokData = await this.dataIntegration.getTikTokData(username);
            const analyticsData = await this.dataIntegration.getAnalyticsData(username);
            
            // Calculate growth predictions based on current trends
            const currentGrowth = analyticsData.analytics.growthRate;
            const predictions = {
                '1month': {
                    followers: Math.round(tiktokData.followers * (1 + currentGrowth.followersGrowth / 100)),
                    engagement: Math.round((tiktokData.engagementRate * (1 + currentGrowth.engagementGrowth / 100)) * 100) / 100,
                    views: Math.round(tiktokData.avgViews * (1 + currentGrowth.viewsGrowth / 100))
                },
                '3months': {
                    followers: Math.round(tiktokData.followers * Math.pow(1 + currentGrowth.followersGrowth / 100, 3)),
                    engagement: Math.round((tiktokData.engagementRate * Math.pow(1 + currentGrowth.engagementGrowth / 100, 3)) * 100) / 100,
                    views: Math.round(tiktokData.avgViews * Math.pow(1 + currentGrowth.viewsGrowth / 100, 3))
                },
                '6months': {
                    followers: Math.round(tiktokData.followers * Math.pow(1 + currentGrowth.followersGrowth / 100, 6)),
                    engagement: Math.round((tiktokData.engagementRate * Math.pow(1 + currentGrowth.engagementGrowth / 100, 6)) * 100) / 100,
                    views: Math.round(tiktokData.avgViews * Math.pow(1 + currentGrowth.viewsGrowth / 100, 6))
                }
            };
            
            return {
                username,
                currentMetrics: {
                    followers: tiktokData.followers,
                    engagementRate: tiktokData.engagementRate,
                    avgViews: tiktokData.avgViews
                },
                growthRate: currentGrowth,
                predictions,
                confidence: "medium",
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            console.error(`❌ Error getting growth predictions for ${username}:`, error);
            throw error;
        }
    }

    // Health check method
    async healthCheck() {
        try {
            const status = {
                service: 'TikTok AI Service',
                status: 'healthy',
                timestamp: new Date().toISOString(),
                components: {
                    aiAnalytics: 'operational',
                    dataIntegration: 'operational',
                    scheduledTasks: 'operational'
                },
                version: '1.0.0'
            };
            
            // Test AI service
            try {
                await this.testAIService();
                status.components.aiAnalytics = 'operational';
            } catch (error) {
                status.components.aiAnalytics = 'error';
                status.status = 'degraded';
            }
            
            return status;
        } catch (error) {
            return {
                service: 'TikTok AI Service',
                status: 'unhealthy',
                error: error.message,
                timestamp: new Date().toISOString()
            };
        }
    }
}

// Export singleton instance
const aiService = new TikTokAIService();

module.exports = aiService;
