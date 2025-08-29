const express = require('express');
const stripe = require('stripe');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
require('dotenv').config();

// Initialize TikTok AI Service
const aiService = require('./tiktok_ai/ai_service');
const TikTokIntegration = require('./tiktok_integration');

const app = express();
const PORT = process.env.PORT || 3002;

// Initialize Stripe with Connect
const stripeClient = stripe(process.env.STRIPE_SECRET_KEY);

// SQLite database setup
const db = new sqlite3.Database('./database.sqlite');

// Create tables
db.serialize(() => {
    // Users table
    db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        tiktok_username TEXT,
        display_name TEXT,
        bio TEXT,
        plan TEXT DEFAULT 'trial',
        stripe_customer_id TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )`);

    // Connected accounts table
    db.run(`CREATE TABLE IF NOT EXISTS connected_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        stripe_account_id TEXT,
        account_status TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )`);

    // Subscriptions table
    db.run(`CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        stripe_subscription_id TEXT,
        plan_type TEXT,
        status TEXT,
        current_period_end DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )`);
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// JWT Secret
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';

// Initialize AI Service and TikTok Integration
aiService.initialize().then(() => {
    console.log('🤖 TikTok AI Service initialized successfully');
}).catch(error => {
    console.error('❌ Failed to initialize AI Service:', error);
});

// Initialize TikTok Integration
const tiktokIntegration = new TikTokIntegration();

// Initialize Stripe Agent SDK Integration
const StripeAIIntegration = require('./stripe_ai_integration');
const StripeAgentEndpoints = require('./stripe_agent_endpoints');

const stripeAI = new StripeAIIntegration();
const stripeAgentEndpoints = new StripeAgentEndpoints();

// Setup Stripe Agent SDK endpoints
stripeAgentEndpoints.setupEndpoints(app);

// Routes
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        timestamp: new Date().toISOString(),
        message: 'TikTok Analytics Pro Dashboard is running'
    });
});

// Token validation endpoint
app.post('/api/validate-token', (req, res) => {
    const token = req.headers.authorization?.split(' ')[1];
    
    if (!token) {
        return res.json({ valid: false });
    }
    
    jwt.verify(token, JWT_SECRET, (err, decoded) => {
        if (err) {
            return res.json({ valid: false });
        }
        
        // Get user data
        db.get('SELECT id, email, tiktok_username, display_name, plan FROM users WHERE id = ?', [decoded.userId], (err, user) => {
            if (err || !user) {
                return res.json({ valid: false });
            }
            
            res.json({ 
                valid: true, 
                user: {
                    id: user.id,
                    email: user.email,
                    tiktok_username: user.tiktok_username,
                    display_name: user.display_name,
                    plan: user.plan
                }
            });
        });
    });
});

// User Registration with Stripe Customer
app.post('/api/register', async (req, res) => {
    try {
        const { name, email, password } = req.body;
        
        // Check if user exists
        db.get('SELECT * FROM users WHERE email = ?', [email], async (err, user) => {
            if (err) {
                return res.status(500).json({ success: false, message: 'Database error' });
            }
            
            if (user) {
                return res.status(400).json({ success: false, message: 'User already exists' });
            }
            
            // Hash password
            const hashedPassword = await bcrypt.hash(password, 10);
            
            // Create user in database
            db.run(
                'INSERT INTO users (email, password, display_name, plan) VALUES (?, ?, ?, ?)',
                [email, hashedPassword, name, 'trial'],
                function(err) {
                    if (err) {
                        return res.status(500).json({ success: false, message: 'Failed to create user' });
                    }
                    
                    // Create JWT token
                    const token = jwt.sign({ userId: this.lastID }, JWT_SECRET, { expiresIn: '7d' });
                    
                    res.json({ 
                        success: true,
                        token, 
                        user: { 
                            id: this.lastID, 
                            email, 
                            display_name: name,
                            plan: 'trial'
                        } 
                    });
                }
            );
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// User Login
app.post('/api/login', (req, res) => {
    const { email, password } = req.body;
    
    db.get('SELECT * FROM users WHERE email = ?', [email], async (err, user) => {
        if (err) {
            return res.status(500).json({ success: false, message: 'Database error' });
        }
        
        if (!user) {
            return res.status(400).json({ success: false, message: 'User not found' });
        }
        
        // Check password
        const validPassword = await bcrypt.compare(password, user.password);
        if (!validPassword) {
            return res.status(400).json({ success: false, message: 'Invalid password' });
        }
        
        // Create JWT token
        const token = jwt.sign({ userId: user.id }, JWT_SECRET, { expiresIn: '7d' });
        
        res.json({ 
            success: true,
            token, 
            user: { 
                id: user.id, 
                email: user.email, 
                display_name: user.display_name,
                tiktok_username: user.tiktok_username,
                plan: user.plan
            } 
        });
    });
});

// Protected route middleware
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];
    
    if (!token) {
        return res.status(401).json({ error: 'Access token required' });
    }
    
    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) {
            return res.status(403).json({ error: 'Invalid token' });
        }
        req.user = user;
        next();
    });
};

// Create Stripe Connect account (for creators to receive payments)
app.post('/api/connect/account', authenticateToken, async (req, res) => {
    try {
        const { country, email, business_type } = req.body;
        
        // Create Connect account
        const account = await stripeClient.accounts.create({
            type: 'express',
            country: country || 'US',
            email: email,
            business_type: business_type || 'individual',
            capabilities: {
                card_payments: { requested: true },
                transfers: { requested: true }
            }
        });
        
        // Store connected account in database
        db.run(
            'INSERT INTO connected_accounts (user_id, stripe_account_id, account_status) VALUES (?, ?, ?)',
            [req.user.userId, account.id, 'pending'],
            function(err) {
                if (err) {
                    return res.status(500).json({ error: 'Failed to save account' });
                }
                
                res.json({ 
                    accountId: account.id,
                    status: 'pending',
                    message: 'Account created successfully'
                });
            }
        );
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get Connect account link for onboarding
app.post('/api/connect/onboard', authenticateToken, async (req, res) => {
    try {
        const { accountId } = req.body;
        
        // Get user's connected account
        db.get(
            'SELECT stripe_account_id FROM connected_accounts WHERE user_id = ? AND stripe_account_id = ?',
            [req.user.userId, accountId],
            async (err, account) => {
                if (err || !account) {
                    return res.status(404).json({ error: 'Account not found' });
                }
                
                // Create account link for onboarding
                const accountLink = await stripeClient.accountLinks.create({
                    account: accountId,
                    refresh_url: `${req.protocol}://${req.get('host')}/dashboard`,
                    return_url: `${req.protocol}://${req.get('host')}/dashboard`,
                    type: 'account_onboarding'
                });
                
                res.json({ url: accountLink.url });
            }
        );
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Create subscription with Connect
app.post('/api/subscriptions/create', authenticateToken, async (req, res) => {
    try {
        const { priceId, paymentMethodId } = req.body;
        
        // Get user's Stripe customer ID
        db.get(
            'SELECT stripe_customer_id FROM users WHERE id = ?',
            [req.user.userId],
            async (err, user) => {
                if (err || !user) {
                    return res.status(404).json({ error: 'User not found' });
                }
                
                // Attach payment method to customer
                await stripeClient.paymentMethods.attach(paymentMethodId, {
                    customer: user.stripe_customer_id
                });
                
                // Set as default payment method
                await stripeClient.customers.update(user.stripe_customer_id, {
                    invoice_settings: {
                        default_payment_method: paymentMethodId
                    }
                });
                
                // Create subscription
                const subscription = await stripeClient.subscriptions.create({
                    customer: user.stripe_customer_id,
                    items: [{ price: priceId }],
                    payment_behavior: 'default_incomplete',
                    payment_settings: { save_default_payment_method: 'on_subscription' },
                    expand: ['latest_invoice.payment_intent']
                });
                
                // Store subscription in database
                db.run(
                    'INSERT INTO subscriptions (user_id, stripe_subscription_id, plan_type, status) VALUES (?, ?, ?, ?)',
                    [req.user.userId, subscription.id, 'pro', subscription.status],
                    function(err) {
                        if (err) {
                            return res.status(500).json({ error: 'Failed to save subscription' });
                        }
                        
                        res.json({
                            subscriptionId: subscription.id,
                            clientSecret: subscription.latest_invoice.payment_intent.client_secret,
                            status: subscription.status
                        });
                    }
                );
            }
        );
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get user's connected accounts
app.get('/api/connect/accounts', authenticateToken, (req, res) => {
    db.all(
        'SELECT * FROM connected_accounts WHERE user_id = ?',
        [req.user.userId],
        async (err, accounts) => {
            if (err) {
                return res.status(500).json({ error: 'Database error' });
            }
            
            // Get account details from Stripe
            const accountDetails = await Promise.all(
                accounts.map(async (account) => {
                    try {
                        const stripeAccount = await stripeClient.accounts.retrieve(account.stripe_account_id);
                        return {
                            id: account.id,
                            accountId: account.stripe_account_id,
                            status: stripeAccount.charges_enabled ? 'active' : 'pending',
                            businessProfile: stripeAccount.business_profile,
                            requirements: stripeAccount.requirements
                        };
                    } catch (error) {
                        return {
                            id: account.id,
                            accountId: account.stripe_account_id,
                            status: 'error',
                            error: error.message
                        };
                    }
                })
            );
            
            res.json({ accounts: accountDetails });
        }
    );
});

// Get user dashboard data
app.get('/api/dashboard', authenticateToken, (req, res) => {
    db.get(
        'SELECT * FROM users WHERE id = ?',
        [req.user.userId],
        (err, user) => {
            if (err || !user) {
                return res.status(404).json({ error: 'User not found' });
            }
            
            // Mock analytics data (replace with real data from your scraping scripts)
            const mockAnalytics = {
                followers: 125000,
                engagement: 3.2,
                monthlyViews: 2500000,
                estimatedEarnings: 8500,
                topVideos: [
                    { title: "Viral Dance Challenge", views: 500000, likes: 25000 },
                    { title: "Cooking Tutorial", views: 320000, likes: 18000 },
                    { title: "Life Update", views: 280000, likes: 15000 }
                ],
                recentActivity: [
                    { type: "video_upload", title: "New Content", date: new Date() },
                    { type: "follower_gain", count: 1250, date: new Date() },
                    { type: "engagement_peak", rate: 4.1, date: new Date() }
                ]
            };
            
            res.json({
                success: true,
                stats: {
                    followers: 125000,
                    views: 2500000,
                    likes: 85000,
                    earnings: 8500
                },
                analytics: mockAnalytics
            });
        }
    );
});

// ===== AI ANALYTICS ENDPOINTS =====

// AI Analysis endpoint
app.post('/api/ai/analyze', authenticateToken, async (req, res) => {
    try {
        const { username } = req.body;
        console.log(`🤖 AI Analysis requested for: ${username}`);
        
        // Get real TikTok data first
        const tiktokData = await tiktokIntegration.getAIAnalysis(username);
        
        // Combine with AI insights
        const aiAnalysis = await aiService.analyzeCreator(username);
        
        const combinedAnalysis = {
            ...tiktokData,
            aiAnalysis: aiAnalysis,
            dataSource: tiktokData.isRealData ? 'Real TikTok Data' : 'Mock Data (Scraping Unavailable)',
            timestamp: new Date().toISOString()
        };
        
        res.json(combinedAnalysis);
    } catch (error) {
        console.error('AI Analysis error:', error);
        res.status(500).json({ error: error.message });
    }
});

// Quick insights endpoint
app.get('/api/ai/insights/:username', authenticateToken, async (req, res) => {
    try {
        const { username } = req.params;
        console.log(`⚡ Quick insights requested for: ${username}`);
        
        // Get real TikTok data
        const tiktokData = await tiktokIntegration.getRealTikTokData(username);
        const insights = await aiService.getQuickInsights(username);
        
        const combinedInsights = {
            ...insights,
            realData: tiktokData,
            dataSource: tiktokData.isRealData ? 'Real TikTok Data' : 'Mock Data (Scraping Unavailable)'
        };
        
        res.json(combinedInsights);
    } catch (error) {
        console.error('Quick insights error:', error);
        res.status(500).json({ error: error.message });
    }
});

// Revenue analysis endpoint
app.get('/api/ai/revenue/:username', authenticateToken, async (req, res) => {
    try {
        const { username } = req.params;
        console.log(`💰 Revenue analysis requested for: ${username}`);
        
        // Get real TikTok data
        const tiktokData = await tiktokIntegration.getRealTikTokData(username);
        const revenue = await aiService.getRevenueAnalysis(username);
        
        const combinedRevenue = {
            ...revenue,
            realEarnings: tiktokData.earnings,
            dataSource: tiktokData.isRealData ? 'Real TikTok Data' : 'Mock Data (Scraping Unavailable)'
        };
        
        res.json(combinedRevenue);
    } catch (error) {
        console.error('Revenue analysis error:', error);
        res.status(500).json({ error: error.message });
    }
});

// Content strategy endpoint
app.get('/api/ai/strategy/:username', authenticateToken, async (req, res) => {
    try {
        const { username } = req.params;
        console.log(`📝 Content strategy requested for: ${username}`);
        
        const strategy = await aiService.getContentStrategy(username);
        res.json(strategy);
    } catch (error) {
        console.error('Content strategy error:', error);
        res.status(500).json({ error: error.message });
    }
});

// Trending topics endpoint
app.get('/api/ai/trends', authenticateToken, async (req, res) => {
    try {
        console.log('🔥 Trending topics requested');
        
        const trends = await aiService.getTrendingTopics();
        res.json(trends);
    } catch (error) {
        console.error('Trending topics error:', error);
        res.status(500).json({ error: error.message });
    }
});

// AI Health check endpoint
app.get('/api/ai/health', authenticateToken, async (req, res) => {
    try {
        const health = await aiService.healthCheck();
        res.json(health);
    } catch (error) {
        console.error('AI health check error:', error);
        res.status(500).json({ error: error.message });
    }
});

// ===== REAL TIKTOK DATA ENDPOINTS =====

// Get real TikTok data for a username
app.get('/api/tiktok/data/:username', authenticateToken, async (req, res) => {
    try {
        const { username } = req.params;
        console.log(`📊 Real TikTok data requested for: ${username}`);
        
        const data = await tiktokIntegration.getRealTikTokData(username);
        res.json(data);
    } catch (error) {
        console.error('TikTok data error:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get comprehensive TikTok analysis
app.get('/api/tiktok/analysis/:username', authenticateToken, async (req, res) => {
    try {
        const { username } = req.params;
        console.log(`🔍 Comprehensive TikTok analysis requested for: ${username}`);
        
        const analysis = await tiktokIntegration.getAIAnalysis(username);
        res.json(analysis);
    } catch (error) {
        console.error('TikTok analysis error:', error);
        res.status(500).json({ error: error.message });
    }
});

// Check TikTok integration status
app.get('/api/tiktok/status', authenticateToken, async (req, res) => {
    try {
        const status = await tiktokIntegration.checkAvailability();
        res.json(status);
    } catch (error) {
        console.error('TikTok status error:', error);
        res.status(500).json({ error: error.message });
    }
});

// ===== PROFILE MANAGEMENT ENDPOINTS =====

// Update profile
app.put('/api/profile/update', authenticateToken, async (req, res) => {
    try {
        const { tiktokUsername, displayName, bio } = req.body;
        const userId = req.user.userId;
        
        db.run(
            'UPDATE users SET tiktok_username = ?, display_name = ?, bio = ? WHERE id = ?',
            [tiktokUsername, displayName, bio, userId],
            function(err) {
                if (err) {
                    console.error('Profile update error:', err);
                    return res.status(500).json({ error: 'Failed to update profile' });
                }
                
                res.json({ 
                    message: 'Profile updated successfully',
                    user: {
                        tiktokUsername,
                        displayName,
                        bio
                    }
                });
            }
        );
    } catch (error) {
        console.error('Profile update error:', error);
        res.status(500).json({ error: error.message });
    }
});

// Change password
app.put('/api/password/change', authenticateToken, async (req, res) => {
    try {
        const { currentPassword, newPassword } = req.body;
        const userId = req.user.userId;
        
        // Get current user
        db.get('SELECT password FROM users WHERE id = ?', [userId], async (err, user) => {
            if (err || !user) {
                return res.status(404).json({ error: 'User not found' });
            }
            
            // Verify current password
            const isValidPassword = await bcrypt.compare(currentPassword, user.password);
            if (!isValidPassword) {
                return res.status(400).json({ error: 'Current password is incorrect' });
            }
            
            // Hash new password
            const hashedPassword = await bcrypt.hash(newPassword, 10);
            
            // Update password
            db.run(
                'UPDATE users SET password = ? WHERE id = ?',
                [hashedPassword, userId],
                function(err) {
                    if (err) {
                        console.error('Password change error:', err);
                        return res.status(500).json({ error: 'Failed to change password' });
                    }
                    
                    res.json({ message: 'Password changed successfully' });
                }
            );
        });
    } catch (error) {
        console.error('Password change error:', error);
        res.status(500).json({ error: error.message });
    }
});

// Webhook for Stripe events
app.post('/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
    const sig = req.headers['stripe-signature'];
    const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET;

    let event;

    try {
        event = stripeClient.webhooks.constructEvent(req.body, sig, endpointSecret);
    } catch (err) {
        console.error('Webhook signature verification failed:', err.message);
        return res.status(400).send(`Webhook Error: ${err.message}`);
    }

    // Handle the event
    switch (event.type) {
        case 'account.updated':
            const account = event.data.object;
            console.log('Account updated:', account.id);
            // Update account status in database
            break;
        case 'customer.subscription.created':
            const subscription = event.data.object;
            console.log('Subscription created:', subscription.id);
            // Update subscription status in database
            break;
        case 'customer.subscription.updated':
            const updatedSubscription = event.data.object;
            console.log('Subscription updated:', updatedSubscription.id);
            // Update subscription in database
            break;
        default:
            console.log(`Unhandled event type ${event.type}`);
    }

    res.json({ received: true });
});

app.listen(PORT, () => {
    console.log(`🚀 Stripe Connect Dashboard running on http://localhost:${PORT}`);
    console.log('Features available:');
    console.log('- User registration with Stripe customers');
    console.log('- Connect account creation for creators');
    console.log('- Subscription management');
    console.log('- Payment processing with Connect');
    console.log('🤖 AI Analytics features:');
    console.log('  - Creator analysis and insights');
    console.log('  - Revenue predictions');
    console.log('  - Content strategy recommendations');
    console.log('  - Trending topics detection');
    console.log('  - Growth predictions');
});
