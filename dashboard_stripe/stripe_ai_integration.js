const stripe = require('stripe');
const aiService = require('./tiktok_ai/ai_service');
require('dotenv').config();

class StripeAIIntegration {
    constructor() {
        this.stripe = stripe(process.env.STRIPE_SECRET_KEY);
        this.aiService = aiService;
    }

    // ===== STRIPE AGENT SDK INTEGRATION =====

    async createAIEnhancedCustomer(userData, tiktokAnalytics) {
        try {
            // Use AI to analyze customer potential
            const aiAnalysis = await this.aiService.analyzeCreator(userData.tiktokUsername);
            
            // Create enhanced customer with AI insights
            const customer = await this.stripe.customers.create({
                email: userData.email,
                metadata: {
                    tiktok_username: userData.tiktokUsername,
                    ai_revenue_potential: aiAnalysis.revenuePrediction.monthlyEarnings,
                    ai_confidence: aiAnalysis.revenuePrediction.confidence,
                    engagement_rate: tiktokAnalytics.engagementRate,
                    follower_count: tiktokAnalytics.followers,
                    content_type: aiAnalysis.tiktokData.contentType,
                    viral_potential: aiAnalysis.trends.trends.length,
                    ai_recommendations: JSON.stringify(aiAnalysis.analysis.recommendations.slice(0, 3))
                },
                description: `AI-Enhanced Creator: ${userData.tiktokUsername}`,
                source: 'tiktok_analytics_ai'
            });

            return {
                customer,
                aiInsights: aiAnalysis,
                riskScore: this.calculateRiskScore(aiAnalysis),
                creditLimit: this.calculateCreditLimit(aiAnalysis)
            };
        } catch (error) {
            console.error('AI Enhanced Customer Creation Error:', error);
            throw error;
        }
    }

    async createAIOptimizedSubscription(customerId, planType, aiAnalysis) {
        try {
            // Use AI to optimize subscription based on creator potential
            const optimizedPlan = this.optimizePlanForCreator(planType, aiAnalysis);
            
            const subscription = await this.stripe.subscriptions.create({
                customer: customerId,
                items: [{ price: optimizedPlan.priceId }],
                metadata: {
                    ai_optimized: 'true',
                    revenue_potential: aiAnalysis.revenuePrediction.monthlyEarnings,
                    recommended_plan: optimizedPlan.recommendedPlan,
                    growth_potential: aiAnalysis.analytics.growthRate.trend,
                    content_strategy: JSON.stringify(aiAnalysis.contentRecommendations.recommendations.slice(0, 2))
                },
                payment_behavior: 'default_incomplete',
                payment_settings: {
                    save_default_payment_method: 'on_subscription'
                },
                expand: ['latest_invoice.payment_intent']
            });

            return {
                subscription,
                aiOptimization: optimizedPlan,
                paymentIntent: subscription.latest_invoice.payment_intent
            };
        } catch (error) {
            console.error('AI Optimized Subscription Error:', error);
            throw error;
        }
    }

    async createAIPoweredConnectAccount(userData, aiAnalysis) {
        try {
            // Use AI to determine optimal Connect account settings
            const connectSettings = this.optimizeConnectSettings(aiAnalysis);
            
            const account = await this.stripe.accounts.create({
                type: 'express',
                country: connectSettings.country,
                email: userData.email,
                capabilities: {
                    card_payments: { requested: true },
                    transfers: { requested: true }
                },
                business_type: connectSettings.businessType,
                metadata: {
                    ai_analyzed: 'true',
                    revenue_potential: aiAnalysis.revenuePrediction.monthlyEarnings,
                    content_category: aiAnalysis.tiktokData.contentType,
                    engagement_score: aiAnalysis.tiktokData.engagementRate,
                    viral_potential: connectSettings.viralPotential,
                    recommended_payout_schedule: connectSettings.payoutSchedule
                }
            });

            return {
                account,
                aiSettings: connectSettings,
                onboardingUrl: await this.generateOnboardingUrl(account.id, aiAnalysis)
            };
        } catch (error) {
            console.error('AI Powered Connect Account Error:', error);
            throw error;
        }
    }

    // ===== AI-POWERED FINANCIAL FEATURES =====

    async generateAIPaymentIntents(amount, customerId, aiAnalysis) {
        try {
            // Use AI to optimize payment intent settings
            const optimizedSettings = this.optimizePaymentSettings(amount, aiAnalysis);
            
            const paymentIntent = await this.stripe.paymentIntents.create({
                amount: optimizedSettings.amount,
                currency: 'usd',
                customer: customerId,
                metadata: {
                    ai_optimized: 'true',
                    revenue_potential: aiAnalysis.revenuePrediction.monthlyEarnings,
                    risk_score: optimizedSettings.riskScore,
                    payment_strategy: optimizedSettings.strategy
                },
                automatic_payment_methods: {
                    enabled: true
                },
                setup_future_usage: optimizedSettings.futureUsage
            });

            return {
                paymentIntent,
                aiOptimization: optimizedSettings,
                recommendations: this.generatePaymentRecommendations(aiAnalysis)
            };
        } catch (error) {
            console.error('AI Payment Intent Error:', error);
            throw error;
        }
    }

    async createAIBrandDealContract(customerId, brandData, aiAnalysis) {
        try {
            // Use AI to optimize brand deal terms
            const optimizedTerms = this.optimizeBrandDealTerms(brandData, aiAnalysis);
            
            const contract = await this.stripe.paymentIntents.create({
                amount: optimizedTerms.amount,
                currency: 'usd',
                customer: customerId,
                metadata: {
                    contract_type: 'brand_deal',
                    ai_optimized: 'true',
                    creator_potential: aiAnalysis.revenuePrediction.monthlyEarnings,
                    engagement_rate: aiAnalysis.tiktokData.engagementRate,
                    content_alignment: optimizedTerms.contentAlignment,
                    deal_structure: optimizedTerms.dealStructure,
                    performance_metrics: JSON.stringify(optimizedTerms.performanceMetrics)
                },
                description: `AI-Optimized Brand Deal: ${brandData.brandName} x ${aiAnalysis.tiktokData.username}`
            });

            return {
                contract,
                aiTerms: optimizedTerms,
                performanceProjections: this.generatePerformanceProjections(aiAnalysis, brandData)
            };
        } catch (error) {
            console.error('AI Brand Deal Contract Error:', error);
            throw error;
        }
    }

    // ===== AI ANALYTICS & OPTIMIZATION =====

    calculateRiskScore(aiAnalysis) {
        const factors = {
            engagementRate: aiAnalysis.tiktokData.engagementRate,
            followerGrowth: aiAnalysis.analytics.growthRate.followersGrowth,
            contentConsistency: aiAnalysis.tiktokData.videoCount,
            revenuePotential: aiAnalysis.revenuePrediction.monthlyEarnings,
            viralPotential: aiAnalysis.trends.trends.length
        };

        // Calculate risk score (0-100, lower is better)
        let riskScore = 50;
        
        if (factors.engagementRate > 5) riskScore -= 10;
        if (factors.followerGrowth > 10) riskScore -= 10;
        if (factors.contentConsistency > 100) riskScore -= 5;
        if (factors.revenuePotential > 5000) riskScore -= 10;
        if (factors.viralPotential > 3) riskScore -= 5;

        return Math.max(0, Math.min(100, riskScore));
    }

    calculateCreditLimit(aiAnalysis) {
        const baseLimit = 1000;
        const revenueMultiplier = aiAnalysis.revenuePrediction.monthlyEarnings * 0.3;
        const engagementBonus = aiAnalysis.tiktokData.engagementRate * 100;
        const riskAdjustment = (100 - this.calculateRiskScore(aiAnalysis)) * 10;

        return Math.round(baseLimit + revenueMultiplier + engagementBonus + riskAdjustment);
    }

    optimizePlanForCreator(planType, aiAnalysis) {
        const plans = {
            creator: { priceId: 'price_creator', basePrice: 97 },
            pro: { priceId: 'price_pro', basePrice: 197 },
            agency: { priceId: 'price_agency', basePrice: 397 }
        };

        // AI logic to recommend optimal plan
        let recommendedPlan = planType;
        let discount = 0;

        if (aiAnalysis.revenuePrediction.monthlyEarnings > 10000) {
            recommendedPlan = 'agency';
            discount = 20; // 20% discount for high-potential creators
        } else if (aiAnalysis.revenuePrediction.monthlyEarnings > 5000) {
            recommendedPlan = 'pro';
            discount = 15; // 15% discount
        }

        return {
            recommendedPlan,
            priceId: plans[recommendedPlan].priceId,
            originalPrice: plans[recommendedPlan].basePrice,
            discountedPrice: plans[recommendedPlan].basePrice * (1 - discount / 100),
            discount,
            aiReasoning: `Recommended ${recommendedPlan} plan based on ${aiAnalysis.revenuePrediction.monthlyEarnings} monthly revenue potential`
        };
    }

    optimizeConnectSettings(aiAnalysis) {
        return {
            country: 'US', // Default, could be AI-determined
            businessType: aiAnalysis.revenuePrediction.monthlyEarnings > 5000 ? 'company' : 'individual',
            viralPotential: aiAnalysis.trends.trends.length > 2 ? 'high' : 'medium',
            payoutSchedule: aiAnalysis.revenuePrediction.monthlyEarnings > 3000 ? 'weekly' : 'monthly',
            aiRecommendations: {
                businessStructure: aiAnalysis.revenuePrediction.monthlyEarnings > 10000 ? 'LLC' : 'Individual',
                taxStrategy: 'AI-optimized based on revenue potential',
                expenseTracking: 'Automated based on content creation patterns'
            }
        };
    }

    optimizePaymentSettings(amount, aiAnalysis) {
        return {
            amount: amount,
            riskScore: this.calculateRiskScore(aiAnalysis),
            strategy: aiAnalysis.revenuePrediction.confidence === 'high' ? 'aggressive' : 'conservative',
            futureUsage: aiAnalysis.revenuePrediction.monthlyEarnings > 5000 ? 'off_session' : 'on_session',
            aiInsights: {
                paymentMethod: 'AI-recommended based on creator profile',
                frequency: aiAnalysis.revenuePrediction.monthlyEarnings > 3000 ? 'recurring' : 'one-time',
                securityLevel: this.calculateRiskScore(aiAnalysis) < 30 ? 'enhanced' : 'standard'
            }
        };
    }

    optimizeBrandDealTerms(brandData, aiAnalysis) {
        const baseAmount = brandData.baseOffer || 1000;
        const engagementMultiplier = aiAnalysis.tiktokData.engagementRate / 2;
        const followerMultiplier = Math.log10(aiAnalysis.tiktokData.followers) / 5;
        const viralBonus = aiAnalysis.trends.trends.length * 200;

        const optimizedAmount = Math.round(baseAmount * (1 + engagementMultiplier + followerMultiplier) + viralBonus);

        return {
            amount: optimizedAmount * 100, // Convert to cents
            contentAlignment: this.calculateContentAlignment(brandData, aiAnalysis),
            dealStructure: this.recommendDealStructure(aiAnalysis),
            performanceMetrics: this.definePerformanceMetrics(aiAnalysis),
            aiReasoning: `Optimized deal value based on ${aiAnalysis.tiktokData.engagementRate}% engagement and ${aiAnalysis.tiktokData.followers} followers`
        };
    }

    calculateContentAlignment(brandData, aiAnalysis) {
        const contentThemes = aiAnalysis.tiktokData.contentThemes || [];
        const brandKeywords = brandData.keywords || [];
        
        let alignment = 0;
        contentThemes.forEach(theme => {
            if (brandKeywords.some(keyword => theme.toLowerCase().includes(keyword.toLowerCase()))) {
                alignment += 25;
            }
        });

        return Math.min(100, alignment);
    }

    recommendDealStructure(aiAnalysis) {
        if (aiAnalysis.revenuePrediction.monthlyEarnings > 10000) {
            return 'performance-based with guaranteed minimum';
        } else if (aiAnalysis.revenuePrediction.monthlyEarnings > 5000) {
            return 'hybrid: fixed + performance bonus';
        } else {
            return 'fixed rate with milestone bonuses';
        }
    }

    definePerformanceMetrics(aiAnalysis) {
        return {
            engagementTarget: aiAnalysis.tiktokData.engagementRate * 1.2,
            viewTarget: aiAnalysis.tiktokData.avgViews * 1.5,
            conversionTarget: aiAnalysis.revenuePrediction.monthlyEarnings * 0.1,
            aiOptimized: true
        };
    }

    generatePaymentRecommendations(aiAnalysis) {
        return {
            recommendedMethods: ['card', 'bank_transfer'],
            frequency: aiAnalysis.revenuePrediction.monthlyEarnings > 5000 ? 'weekly' : 'monthly',
            securityLevel: this.calculateRiskScore(aiAnalysis) < 30 ? 'enhanced' : 'standard',
            aiInsights: [
                `Based on ${aiAnalysis.revenuePrediction.monthlyEarnings} monthly revenue potential`,
                `Engagement rate of ${aiAnalysis.tiktokData.engagementRate}% indicates strong audience connection`,
                `${aiAnalysis.trends.trends.length} trending topics suggest viral potential`
            ]
        };
    }

    generatePerformanceProjections(aiAnalysis, brandData) {
        return {
            projectedViews: aiAnalysis.tiktokData.avgViews * 1.5,
            projectedEngagement: aiAnalysis.tiktokData.engagementRate * 1.2,
            projectedRevenue: aiAnalysis.revenuePrediction.monthlyEarnings * 0.15,
            confidence: aiAnalysis.revenuePrediction.confidence,
            aiFactors: [
                'Historical performance analysis',
                'Trending content patterns',
                'Audience growth trajectory',
                'Brand alignment score'
            ]
        };
    }

    async generateOnboardingUrl(accountId, aiAnalysis) {
        try {
            const accountLink = await this.stripe.accountLinks.create({
                account: accountId,
                refresh_url: `${process.env.BASE_URL}/dashboard/connect/refresh`,
                return_url: `${process.env.BASE_URL}/dashboard/connect/success`,
                type: 'account_onboarding',
                collect: 'eventually_due'
            });

            return accountLink.url;
        } catch (error) {
            console.error('Onboarding URL Generation Error:', error);
            throw error;
        }
    }

    // ===== AI-POWERED FRAUD DETECTION =====

    async analyzeTransactionRisk(paymentIntent, aiAnalysis) {
        const riskFactors = {
            unusualAmount: this.detectUnusualAmount(paymentIntent.amount, aiAnalysis),
            timingAnomaly: this.detectTimingAnomaly(paymentIntent.created, aiAnalysis),
            patternDeviation: this.detectPatternDeviation(paymentIntent, aiAnalysis),
            aiConfidence: aiAnalysis.revenuePrediction.confidence
        };

        const riskScore = this.calculateTransactionRiskScore(riskFactors);
        
        return {
            riskScore,
            riskFactors,
            recommendation: riskScore > 70 ? 'review' : 'approve',
            aiInsights: this.generateRiskInsights(riskFactors, aiAnalysis)
        };
    }

    detectUnusualAmount(amount, aiAnalysis) {
        const expectedRange = aiAnalysis.revenuePrediction.monthlyEarnings * 100; // Convert to cents
        const deviation = Math.abs(amount - expectedRange) / expectedRange;
        return deviation > 0.5; // More than 50% deviation
    }

    detectTimingAnomaly(timestamp, aiAnalysis) {
        // Implement timing analysis logic
        return false; // Placeholder
    }

    detectPatternDeviation(paymentIntent, aiAnalysis) {
        // Implement pattern analysis logic
        return false; // Placeholder
    }

    calculateTransactionRiskScore(riskFactors) {
        let score = 0;
        if (riskFactors.unusualAmount) score += 30;
        if (riskFactors.timingAnomaly) score += 25;
        if (riskFactors.patternDeviation) score += 25;
        if (riskFactors.aiConfidence === 'low') score += 20;
        
        return Math.min(100, score);
    }

    generateRiskInsights(riskFactors, aiAnalysis) {
        const insights = [];
        
        if (riskFactors.unusualAmount) {
            insights.push('Transaction amount significantly differs from AI revenue projections');
        }
        if (riskFactors.aiConfidence === 'low') {
            insights.push('AI analysis indicates low confidence in creator revenue potential');
        }
        
        return insights;
    }
}

module.exports = StripeAIIntegration;
