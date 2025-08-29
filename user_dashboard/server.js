const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Simple in-memory storage (replace with your chosen database)
let users = [];
let analytics = [];

// JWT Secret
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';

// Routes
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// User Registration
app.post('/api/register', async (req, res) => {
    try {
        const { email, password, tiktokUsername, plan } = req.body;
        
        // Check if user exists
        if (users.find(u => u.email === email)) {
            return res.status(400).json({ error: 'User already exists' });
        }
        
        // Hash password
        const hashedPassword = await bcrypt.hash(password, 10);
        
        // Create user
        const user = {
            id: Date.now().toString(),
            email,
            password: hashedPassword,
            tiktokUsername,
            plan: plan || 'trial',
            trialEnds: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000), // 3 days
            createdAt: new Date(),
            accounts: []
        };
        
        users.push(user);
        
        // Create JWT token
        const token = jwt.sign({ userId: user.id }, JWT_SECRET, { expiresIn: '7d' });
        
        res.json({ token, user: { id: user.id, email, plan: user.plan } });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// User Login
app.post('/api/login', async (req, res) => {
    try {
        const { email, password } = req.body;
        
        // Find user
        const user = users.find(u => u.email === email);
        if (!user) {
            return res.status(400).json({ error: 'User not found' });
        }
        
        // Check password
        const validPassword = await bcrypt.compare(password, user.password);
        if (!validPassword) {
            return res.status(400).json({ error: 'Invalid password' });
        }
        
        // Create JWT token
        const token = jwt.sign({ userId: user.id }, JWT_SECRET, { expiresIn: '7d' });
        
        res.json({ token, user: { id: user.id, email, plan: user.plan } });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
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

// Get user dashboard data
app.get('/api/dashboard', authenticateToken, (req, res) => {
    const user = users.find(u => u.id === req.user.userId);
    if (!user) {
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
        user: {
            id: user.id,
            email: user.email,
            tiktokUsername: user.tiktokUsername,
            plan: user.plan,
            trialEnds: user.trialEnds,
            accounts: user.accounts
        },
        analytics: mockAnalytics
    });
});

// Add TikTok account
app.post('/api/accounts', authenticateToken, (req, res) => {
    const { username } = req.body;
    const user = users.find(u => u.id === req.user.userId);
    
    if (!user) {
        return res.status(404).json({ error: 'User not found' });
    }
    
    // Check account limits based on plan
    const accountLimits = {
        trial: 3,
        creator: 3,
        pro: 8,
        agency: 15
    };
    
    if (user.accounts.length >= accountLimits[user.plan]) {
        return res.status(400).json({ error: 'Account limit reached for your plan' });
    }
    
    const account = {
        id: Date.now().toString(),
        username,
        addedAt: new Date(),
        status: 'processing'
    };
    
    user.accounts.push(account);
    res.json({ account });
});

// Get analytics for specific account
app.get('/api/analytics/:accountId', authenticateToken, (req, res) => {
    // Mock detailed analytics (replace with real data from your scraping scripts)
    const analytics = {
        followers: 125000,
        following: 850,
        totalLikes: 2500000,
        totalViews: 15000000,
        engagementRate: 3.2,
        avgViews: 125000,
        avgLikes: 6250,
        avgComments: 850,
        avgShares: 320,
        topHashtags: ['#viral', '#dance', '#trending'],
        bestPostingTimes: ['6PM', '8PM', '10PM'],
        recentVideos: [
            { title: "Viral Dance", views: 500000, likes: 25000, date: '2024-01-15' },
            { title: "Cooking Tutorial", views: 320000, likes: 18000, date: '2024-01-14' },
            { title: "Life Update", views: 280000, likes: 15000, date: '2024-01-13' }
        ]
    };
    
    res.json({ analytics });
});

app.listen(PORT, () => {
    console.log(`Dashboard server running on http://localhost:${PORT}`);
    console.log('Database options:');
    console.log('1. SQLite (easiest, file-based, free)');
    console.log('2. MongoDB Atlas (cloud, free tier, easy)');
    console.log('3. PostgreSQL (local or cloud, more complex)');
});
