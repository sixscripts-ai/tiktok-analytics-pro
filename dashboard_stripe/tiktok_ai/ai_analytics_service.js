const OpenAI = require('openai');
const { spawn } = require('child_process');
const path = require('path');
require('dotenv').config();

class TikTokAIAnalytics {
    constructor() {
        this.openai = new OpenAI({
            apiKey: process.env.OPENAI_API_KEY
        });
    }

    async analyzeCreatorData(tiktokData) {
        try {
            const prompt = this.buildAnalysisPrompt(tiktokData);
            
            const response = await this.openai.chat.completions.create({
                model: "gpt-4",
                messages: [
                    {
                        role: "system",
                        content: "You are an expert TikTok analytics consultant. Provide actionable, specific insights and recommendations based on creator data. Be concise but comprehensive."
                    },
                    {
                        role: "user",
                        content: prompt
                    }
                ],
                max_tokens: 800,
                temperature: 0.7
            });

            return this.parseAIResponse(response.choices[0].message.content);
        } catch (error) {
            console.error('AI Analysis Error:', error);
            return {
                insights: "Unable to analyze data at this time.",
                recommendations: [],
                error: error.message
            };
        }
    }

    async predictRevenue(creatorData) {
        try {
            const prompt = this.buildRevenuePrompt(creatorData);

            const aiResponsePromise = this.openai.chat.completions.create({
                model: "gpt-4",
                messages: [
                    {
                        role: "system",
                        content: "You are a TikTok monetization expert. Provide realistic revenue estimates based on creator metrics. Include breakdowns by revenue stream."
                    },
                    {
                        role: "user",
                        content: prompt
                    }
                ],
                max_tokens: 600,
                temperature: 0.5
            });

            const [aiResponse, mlEstimate] = await Promise.all([
                aiResponsePromise,
                this.mlPredictRevenue(creatorData).catch(() => null)
            ]);

            const parsed = this.parseRevenueResponse(aiResponse.choices[0].message.content);
            if (mlEstimate !== null) parsed.mlEstimate = mlEstimate;
            return parsed;
        } catch (error) {
            console.error('Revenue Prediction Error:', error);
            return {
                monthlyEarnings: 0,
                breakdown: {},
                confidence: "low",
                error: error.message
            };
        }
    }

    mlPredictRevenue(creatorData) {
        return new Promise((resolve, reject) => {
            const py = spawn('python', [path.join(__dirname, '../ml/revenue_model.py')]);
            let stdout = '';
            let stderr = '';
            py.stdout.on('data', d => stdout += d.toString());
            py.stderr.on('data', d => stderr += d.toString());
            py.on('close', code => {
                if (code !== 0) return reject(new Error(stderr));
                try {
                    const res = JSON.parse(stdout);
                    resolve(res.prediction);
                } catch (e) {
                    reject(e);
                }
            });
            py.stdin.write(JSON.stringify(creatorData));
            py.stdin.end();
        });
    }

    async generateContentRecommendations(creatorData) {
        try {
            const prompt = this.buildContentPrompt(creatorData);
            
            const response = await this.openai.chat.completions.create({
                model: "gpt-4",
                messages: [
                    {
                        role: "system",
                        content: "You are a TikTok content strategy expert. Provide specific, actionable content recommendations based on creator performance data."
                    },
                    {
                        role: "user",
                        content: prompt
                    }
                ],
                max_tokens: 700,
                temperature: 0.8
            });

            return this.parseContentResponse(response.choices[0].message.content);
        } catch (error) {
            console.error('Content Recommendations Error:', error);
            return {
                recommendations: [],
                trendingTopics: [],
                optimalTiming: {},
                error: error.message
            };
        }
    }

    async detectTrends(videoData) {
        try {
            const prompt = this.buildTrendsPrompt(videoData);
            
            const response = await this.openai.chat.completions.create({
                model: "gpt-4",
                messages: [
                    {
                        role: "system",
                        content: "You are a TikTok trend analyst. Identify patterns, trends, and opportunities in video performance data."
                    },
                    {
                        role: "user",
                        content: prompt
                    }
                ],
                max_tokens: 500,
                temperature: 0.6
            });

            return this.parseTrendsResponse(response.choices[0].message.content);
        } catch (error) {
            console.error('Trend Detection Error:', error);
            return {
                trends: [],
                opportunities: [],
                warnings: [],
                error: error.message
            };
        }
    }

    // Helper methods for building prompts
    buildAnalysisPrompt(tiktokData) {
        return `
        Analyze this TikTok creator's data and provide insights:

        CREATOR DATA:
        - Username: ${tiktokData.username || 'N/A'}
        - Followers: ${tiktokData.followers || 'N/A'}
        - Following: ${tiktokData.following || 'N/A'}
        - Total Likes: ${tiktokData.totalLikes || 'N/A'}
        - Video Count: ${tiktokData.videoCount || 'N/A'}
        - Engagement Rate: ${tiktokData.engagementRate || 'N/A'}%
        - Bio: ${tiktokData.bio || 'N/A'}
        - Optimal Posting Windows: ${JSON.stringify(tiktokData.postingWindows?.slice(0,3) || [])}
        - Hashtag Performance: ${JSON.stringify(tiktokData.hashtagLift?.slice(0,5) || [])}
        - Top Sound: ${tiktokData.topSound || 'N/A'}

        RECENT VIDEOS:
        ${JSON.stringify(tiktokData.recentVideos || [], null, 2)}

        Please provide:
        1. Growth Analysis (3-4 bullet points)
        2. Content Performance Insights (3-4 bullet points)
        3. Engagement Optimization Tips (3-4 bullet points)
        4. Immediate Action Items (2-3 specific recommendations)
        `;
    }

    buildRevenuePrompt(creatorData) {
        return `
        Predict monthly earnings for this TikTok creator:

        METRICS:
        - Followers: ${creatorData.followers || 0}
        - Engagement Rate: ${creatorData.engagementRate || 0}%
        - Average Views: ${creatorData.avgViews || 0}
        - Content Type: ${creatorData.contentType || 'General'}
        - Account Age: ${creatorData.accountAge || 'Unknown'}

        Provide:
        1. Monthly earnings estimate (total)
        2. Breakdown by revenue stream:
           - Brand deals
           - Creator Fund
           - Merchandise
           - Live streaming
           - Affiliate marketing
        3. Confidence level (high/medium/low)
        4. Growth potential for next 6 months
        `;
    }

    buildContentPrompt(creatorData) {
        return `
        Generate content recommendations for this creator:

        CURRENT PERFORMANCE:
        - Top performing content: ${JSON.stringify(creatorData.topVideos || [])}
        - Audience demographics: ${creatorData.demographics || 'Unknown'}
        - Content themes: ${creatorData.contentThemes || 'General'}

        Provide:
        1. 5 specific content ideas
        2. Trending hashtags to use
        3. Optimal posting times
        4. Content format recommendations
        5. Collaboration opportunities
        `;
    }

    buildTrendsPrompt(videoData) {
        return `
        Analyze trends in this video data:

        VIDEO PERFORMANCE:
        ${JSON.stringify(videoData, null, 2)}

        Identify:
        1. Performance patterns
        2. Trending content types
        3. Optimal video length
        4. Best performing hashtags
        5. Audience engagement patterns
        `;
    }

    // Helper methods for parsing AI responses
    parseAIResponse(response) {
        try {
            const sections = response.split('\n\n');
            return {
                insights: sections[0] || response,
                recommendations: this.extractRecommendations(response),
                actionItems: this.extractActionItems(response),
                rawResponse: response
            };
        } catch (error) {
            return {
                insights: response,
                recommendations: [],
                actionItems: [],
                rawResponse: response
            };
        }
    }

    parseRevenueResponse(response) {
        try {
            const lines = response.split('\n');
            const monthlyEarnings = this.extractNumber(response, 'monthly|earnings|revenue');
            
            return {
                monthlyEarnings: monthlyEarnings || 0,
                breakdown: this.extractRevenueBreakdown(response),
                confidence: this.extractConfidence(response),
                growthPotential: this.extractGrowthPotential(response),
                rawResponse: response
            };
        } catch (error) {
            return {
                monthlyEarnings: 0,
                breakdown: {},
                confidence: "low",
                growthPotential: "unknown",
                rawResponse: response
            };
        }
    }

    parseContentResponse(response) {
        try {
            return {
                recommendations: this.extractContentIdeas(response),
                trendingTopics: this.extractTrendingTopics(response),
                optimalTiming: this.extractOptimalTiming(response),
                hashtags: this.extractHashtags(response),
                rawResponse: response
            };
        } catch (error) {
            return {
                recommendations: [],
                trendingTopics: [],
                optimalTiming: {},
                hashtags: [],
                rawResponse: response
            };
        }
    }

    parseTrendsResponse(response) {
        try {
            return {
                trends: this.extractTrends(response),
                opportunities: this.extractOpportunities(response),
                warnings: this.extractWarnings(response),
                patterns: this.extractPatterns(response),
                rawResponse: response
            };
        } catch (error) {
            return {
                trends: [],
                opportunities: [],
                warnings: [],
                patterns: [],
                rawResponse: response
            };
        }
    }

    // Utility methods for extracting specific data
    extractNumber(text, pattern) {
        const regex = new RegExp(`(${pattern}).*?(\\d+(?:,\\d+)*(?:\\.\\d+)?)`, 'i');
        const match = text.match(regex);
        return match ? parseFloat(match[2].replace(/,/g, '')) : 0;
    }

    extractRecommendations(text) {
        const recommendations = [];
        const lines = text.split('\n');
        
        lines.forEach(line => {
            if (line.includes('•') || line.includes('-') || line.includes('*')) {
                const clean = line.replace(/^[•\-\*]\s*/, '').trim();
                if (clean) recommendations.push(clean);
            }
        });
        
        return recommendations;
    }

    extractActionItems(text) {
        const actionItems = [];
        const lines = text.split('\n');
        
        lines.forEach(line => {
            if (line.toLowerCase().includes('action') || 
                line.toLowerCase().includes('do') || 
                line.toLowerCase().includes('try')) {
                const clean = line.replace(/^[•\-\*]\s*/, '').trim();
                if (clean) actionItems.push(clean);
            }
        });
        
        return actionItems;
    }

    extractRevenueBreakdown(text) {
        const breakdown = {};
        const lines = text.split('\n');
        
        lines.forEach(line => {
            if (line.includes('$') || line.includes('brand') || line.includes('fund')) {
                const amount = this.extractNumber(line, '\\$\\d+');
                if (amount > 0) {
                    if (line.includes('brand')) breakdown.brandDeals = amount;
                    else if (line.includes('fund')) breakdown.creatorFund = amount;
                    else if (line.includes('merch')) breakdown.merchandise = amount;
                    else if (line.includes('live')) breakdown.liveStreaming = amount;
                    else if (line.includes('affiliate')) breakdown.affiliate = amount;
                }
            }
        });
        
        return breakdown;
    }

    extractConfidence(text) {
        if (text.toLowerCase().includes('high confidence')) return 'high';
        if (text.toLowerCase().includes('medium confidence')) return 'medium';
        if (text.toLowerCase().includes('low confidence')) return 'low';
        return 'medium';
    }

    extractGrowthPotential(text) {
        if (text.toLowerCase().includes('high growth') || text.toLowerCase().includes('strong growth')) return 'high';
        if (text.toLowerCase().includes('moderate growth')) return 'medium';
        if (text.toLowerCase().includes('slow growth')) return 'low';
        return 'medium';
    }

    extractContentIdeas(text) {
        const ideas = [];
        const lines = text.split('\n');
        
        lines.forEach(line => {
            if (line.includes('idea') || line.includes('content') || line.includes('video')) {
                const clean = line.replace(/^[•\-\*]\s*/, '').trim();
                if (clean && clean.length > 10) ideas.push(clean);
            }
        });
        
        return ideas.slice(0, 5); // Return top 5 ideas
    }

    extractTrendingTopics(text) {
        const topics = [];
        const lines = text.split('\n');
        
        lines.forEach(line => {
            if (line.includes('trend') || line.includes('viral') || line.includes('popular')) {
                const clean = line.replace(/^[•\-\*]\s*/, '').trim();
                if (clean) topics.push(clean);
            }
        });
        
        return topics;
    }

    extractOptimalTiming(text) {
        const timing = {};
        const lines = text.split('\n');
        
        lines.forEach(line => {
            if (line.includes('time') || line.includes('schedule') || line.includes('post')) {
                if (line.includes('day')) {
                    const day = line.match(/(monday|tuesday|wednesday|thursday|friday|saturday|sunday)/i);
                    if (day) timing.bestDay = day[1];
                }
                if (line.includes('hour') || line.includes('pm') || line.includes('am')) {
                    const time = line.match(/(\d{1,2}(?::\d{2})?\s*(?:am|pm))/i);
                    if (time) timing.bestTime = time[1];
                }
            }
        });
        
        return timing;
    }

    extractHashtags(text) {
        const hashtags = [];
        const matches = text.match(/#\w+/g);
        if (matches) {
            hashtags.push(...matches);
        }
        return hashtags.slice(0, 10); // Return top 10 hashtags
    }

    extractTrends(text) {
        const trends = [];
        const lines = text.split('\n');
        
        lines.forEach(line => {
            if (line.includes('trend') || line.includes('pattern') || line.includes('increase')) {
                const clean = line.replace(/^[•\-\*]\s*/, '').trim();
                if (clean) trends.push(clean);
            }
        });
        
        return trends;
    }

    extractOpportunities(text) {
        const opportunities = [];
        const lines = text.split('\n');
        
        lines.forEach(line => {
            if (line.includes('opportunity') || line.includes('potential') || line.includes('growth')) {
                const clean = line.replace(/^[•\-\*]\s*/, '').trim();
                if (clean) opportunities.push(clean);
            }
        });
        
        return opportunities;
    }

    extractWarnings(text) {
        const warnings = [];
        const lines = text.split('\n');
        
        lines.forEach(line => {
            if (line.includes('warning') || line.includes('risk') || line.includes('avoid')) {
                const clean = line.replace(/^[•\-\*]\s*/, '').trim();
                if (clean) warnings.push(clean);
            }
        });
        
        return warnings;
    }

    extractPatterns(text) {
        const patterns = [];
        const lines = text.split('\n');
        
        lines.forEach(line => {
            if (line.includes('pattern') || line.includes('consistent') || line.includes('regular')) {
                const clean = line.replace(/^[•\-\*]\s*/, '').trim();
                if (clean) patterns.push(clean);
            }
        });
        
        return patterns;
    }
}

module.exports = TikTokAIAnalytics;
