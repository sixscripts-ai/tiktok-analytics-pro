# TikTok Analytics Pro - User Dashboard

Simple user dashboard with authentication and analytics display.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment:**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start the server:**
   ```bash
   npm start
   ```

4. **Access dashboard:**
   - Open: `http://localhost:3001`
   - Register a new account
   - Login and explore the dashboard

## 🗄️ Database Options

### Option 1: SQLite (Recommended - Easiest & Free)
- **Setup:** No setup required
- **Cost:** Free
- **Storage:** Local file
- **Best for:** Development, small scale

### Option 2: MongoDB Atlas (Cloud - Easy)
- **Setup:** Create free account at mongodb.com
- **Cost:** Free tier available
- **Storage:** Cloud
- **Best for:** Production, scalability

### Option 3: PostgreSQL (Advanced)
- **Setup:** Install PostgreSQL locally or use cloud service
- **Cost:** Free locally, paid cloud options
- **Storage:** Local or cloud
- **Best for:** Complex queries, enterprise

## 📁 Current Features

- ✅ User registration & login
- ✅ JWT authentication
- ✅ Dashboard with mock analytics
- ✅ Account management
- ✅ Responsive design
- ✅ Session persistence

## 🔧 Next Steps

1. **Choose your database** (see options above)
2. **Connect your scraping scripts** to replace mock data
3. **Add subscription management**
4. **Implement real-time analytics**

## 🎯 Integration Points

- **Landing Page:** `http://localhost:3000` (payment processing)
- **Dashboard:** `http://localhost:3001` (user interface)
- **Scraping Scripts:** Ready to integrate from `../tiktok_scraping_scripts/`

## 💡 Database Choice Recommendation

**For a one-person operation, I recommend SQLite:**
- Zero setup required
- Data stored in a single file
- Perfect for MVP and early customers
- Easy to migrate to cloud later

**Choose your database and I'll help you integrate it!**
