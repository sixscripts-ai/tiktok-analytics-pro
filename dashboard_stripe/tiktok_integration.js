/**
 * TikTok Integration for Dashboard
 * Integrates real TikTok scraping data with the AI dashboard
 */

const path = require('path');
const TikTokDashboardIntegration = require('../tiktok_scraping_scripts/dashboard_integration');

class TikTokIntegration {
    constructor() {
        this.scrapingIntegration = new TikTokDashboardIntegration(path.join(__dirname, '../tiktok_scraping_scripts'));
        this.isAvailable = false;
        this.checkAvailability();
    }

    async checkAvailability() {
        try {
            const status = await this.scrapingIntegration.checkAvailability();
            this.isAvailable = status.available;
            console.log(`TikTok Integration Status: ${status.message}`);
            return status;
        } catch (error) {
            console.error('TikTok Integration not available:', error.message);
            this.isAvailable = false;
            return { available: false, message: error.message };
        }
    }

        /**
     * Get real TikTok data for AI analysis
     */
    async getRealTikTokData(username) {
        if (!this.isAvailable) {
            console.log('TikTok scraping not available, using mock data');
            return this.getMockData(username);
        }

        try {
            console.log(`Scraping real data for @${username}...`);
            const data = await this.scrapingIntegration.getComprehensiveAnalysis(username);

            if (data.error) {
                console.error('Scraping error:', data.error);
                return this.getMockData(username);
            }

            // Validate data structure
            if (!data || typeof data !== 'object') {
                console.error('Invalid data structure returned from scraping');
                return this.getMockData(username);
            }

            const formattedData = this.formatRealData(data);
            
            // Additional validation
            if (!formattedData.profile || !formattedData.profile.followers) {
                console.warn('Profile data incomplete, using mock data');
                return this.getMockData(username);
            }

            return formattedData;
        } catch (error) {
            console.error('Error getting real TikTok data:', error.message);
            console.error('Stack trace:', error.stack);
            return this.getMockData(username);
        }
    }

    /**
     * Format real scraped data for AI analysis
     */
    formatRealData(data) {
        const profile = data.profile || {};
        const videos = data.videos || [];
        const earnings = data.earnings || {};
        const engagement = data.engagement || {};

        // Calculate engagement rate from real data
        let engagementRate = 0;
        if (profile.follower_count && profile.follower_count > 0) {
            const totalLikes = profile.total_likes || 0;
            engagementRate = (totalLikes / profile.follower_count) * 100;
        }

        // Calculate total views from videos
        const totalViews = videos.reduce((sum, video) => sum + (video.views || 0), 0);

        return {
            username: data.username,
            profile: {
                followers: profile.follower_count || profile.followers || 0,
                following: profile.following_count || profile.following || 0,
                totalLikes: profile.total_likes || profile.likes || 0,
                videoCount: profile.video_count || profile.videoCount || videos.length,
                bio: profile.bio || '',
                verified: profile.verified || false,
                displayName: profile.display_name || profile.displayName || data.username
            },
            videos: videos.map(video => ({
                url: video.url,
                views: video.views || 0,
                likes: video.likes || 0,
                comments: video.comments || 0,
                shares: video.shares || 0,
                caption: video.caption || '',
                hashtags: video.hashtags || [],
                createTime: video.create_time
            })),
            analytics: {
                engagementRate: Math.round(engagementRate * 100) / 100,
                totalViews: totalViews,
                avgViewsPerVideo: videos.length > 0 ? Math.round(totalViews / videos.length) : 0,
                totalLikes: profile.total_likes || 0,
                totalComments: videos.reduce((sum, video) => sum + (video.comments || 0), 0),
                totalShares: videos.reduce((sum, video) => sum + (video.shares || 0), 0)
            },
            earnings: {
                brandDeals: earnings.brand_deals || { low: 0, mid: 0, high: 0 },
                creatorFund: earnings.creator_fund || { low: 0, mid: 0, high: 0 },
                affiliate: earnings.affiliate || { low: 0, mid: 0, high: 0 },
                merch: earnings.merch || { low: 0, mid: 0, high: 0 }
            },
            engagement: engagement.overall || {},
            timestamp: data.timestamp,
            isRealData: true
        };
    }

    /**
     * Fallback mock data when scraping is not available
     */
    getMockData(username) {
        return {
            username: username,
            profile: {
                followers: 125000,
                following: 850,
                totalLikes: 2500000,
                videoCount: 150,
                bio: 'Content Creator',
                verified: true,
                displayName: username
            },
            videos: [],
            analytics: {
                engagementRate: 3.2,
                totalViews: 2500000,
                avgViewsPerVideo: 16667,
                totalLikes: 85000,
                totalComments: 12500,
                totalShares: 5000
            },
            earnings: {
                brandDeals: { low: 1500, mid: 3000, high: 5000 },
                creatorFund: { low: 25, mid: 50, high: 100 },
                affiliate: { low: 400, mid: 800, high: 1200 },
                merch: { low: 500, mid: 1000, high: 2000 }
            },
            engagement: {
                videos: 150,
                avg_engagement_rate: 0.032,
                avg_views: 16667,
                share_to_view: 0.002,
                comment_to_view: 0.005
            },
            timestamp: new Date().toISOString(),
            isRealData: false
        };
    }

    /**
     * Get AI analysis with real data
     */
    async getAIAnalysis(username) {
        const data = await this.getRealTikTokData(username);
        
        // Generate AI insights based on real data
        const insights = this.generateAIInsights(data);
        
        return {
            ...data,
            aiInsights: insights
        };
    }

    /**
     * Generate AI insights from real data
     */
    generateAIInsights(data) {
        const profile = data.profile;
        const analytics = data.analytics;
        const earnings = data.earnings;

        const insights = {
            growth: {
                status: profile.followers > 100000 ? 'Established' : profile.followers > 10000 ? 'Growing' : 'Emerging',
                recommendation: profile.followers < 10000 ? 'Focus on content consistency and engagement' : 
                               profile.followers < 100000 ? 'Optimize posting times and hashtag strategy' : 
                               'Explore brand partnerships and monetization'
            },
            engagement: {
                status: analytics.engagementRate > 5 ? 'Excellent' : analytics.engagementRate > 3 ? 'Good' : 'Needs Improvement',
                recommendation: analytics.engagementRate < 3 ? 'Increase interaction with followers and optimize content timing' :
                               analytics.engagementRate < 5 ? 'Experiment with new content formats and trending sounds' :
                               'Maintain high engagement with consistent quality content'
            },
            monetization: {
                monthlyPotential: Math.round(earnings.brandDeals.mid + earnings.creatorFund.mid + earnings.affiliate.mid + earnings.merch.mid),
                primaryRevenue: earnings.brandDeals.mid > earnings.affiliate.mid ? 'Brand Deals' : 'Affiliate Marketing',
                recommendation: earnings.brandDeals.mid < 1000 ? 'Build audience before pursuing brand deals' :
                               'Diversify revenue streams with merchandise and affiliate marketing'
            },
            content: {
                optimalPosting: analytics.engagementRate > 3 ? 'Maintain current schedule' : 'Experiment with different posting times',
                hashtagStrategy: profile.followers > 50000 ? 'Use trending hashtags strategically' : 'Focus on niche hashtags',
                videoLength: analytics.avgViewsPerVideo > 10000 ? 'Current length works well' : 'Try shorter, more engaging content'
            }
        };

        return insights;
    }
}

module.exports = TikTokIntegration;
