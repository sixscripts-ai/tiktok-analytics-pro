# TikTok Analytics Pro - Stripe Connect Dashboard

Complete SaaS platform with Stripe Connect integration for creators to receive payments.

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
   - Open: `http://localhost:3002`
   - Register a new account
   - Connect your Stripe account
   - Start receiving payments!

## 🎯 Stripe Connect Features

### ✅ What's Built:
- **User Authentication** - Register/login with JWT
- **Stripe Customer Creation** - Automatic customer setup
- **Connect Account Creation** - Creators can connect Stripe accounts
- **Onboarding Flow** - Seamless Stripe onboarding
- **Subscription Management** - Upgrade plans with Stripe
- **Payment Processing** - Handle payments and payouts
- **Webhook Handling** - Real-time event processing

### 🔗 Connect Account Flow:
1. User registers/logs in
2. Clicks "Connect Stripe Account"
3. Fills out business info
4. Redirected to Stripe onboarding
5. Completes verification
6. Account becomes active for payments

### 💳 Subscription Flow:
1. User selects plan
2. Enters payment info
3. Creates subscription
4. Handles recurring billing
5. Manages plan upgrades/downgrades

## 🗄️ Database

**SQLite** - Simple file-based database:
- No setup required
- Data stored in `database.sqlite`
- Perfect for MVP and testing
- Easy to migrate to cloud later

## 🔧 Stripe Setup Required

### 1. Create Price Products in Stripe Dashboard:
```bash
# You'll need to create these price IDs in your Stripe dashboard:
- price_creator_monthly ($97/month)
- price_pro_monthly ($197/month)  
- price_agency_monthly ($397/month)
```

### 2. Enable Connect in Stripe Dashboard:
- Go to Stripe Dashboard → Connect
- Enable Connect for your account
- Configure your platform settings

### 3. Set up Webhooks:
```bash
# Run this to forward webhooks to your server:
stripe listen --forward-to localhost:3002/webhook
```

## 🎯 Integration Points

- **Landing Page:** `http://localhost:3000` (payment processing)
- **User Dashboard:** `http://localhost:3001` (basic auth)
- **Connect Dashboard:** `http://localhost:3002` (Stripe Connect)
- **Scraping Scripts:** Ready to integrate from `../tiktok_scraping_scripts/`

## 💡 Why Stripe Connect?

**Perfect for your TikTok Analytics SaaS:**

1. **Creator Payments** - Creators can receive payments from brand deals
2. **Platform Fees** - You take a percentage of transactions
3. **Compliance** - Handles tax forms and regulations
4. **Scalability** - Grows with your business
5. **Trust** - Creators trust Stripe for payments

## 🚀 Next Steps

1. **Test Connect Flow** - Create accounts and test onboarding
2. **Create Price Products** - Set up your subscription prices in Stripe
3. **Connect Scraping Scripts** - Replace mock data with real analytics
4. **Add Payment Splitting** - Implement platform fees
5. **Deploy to Production** - Move to cloud hosting

## 💰 Revenue Model

With Stripe Connect, you can:
- **Subscription Revenue** - Monthly SaaS fees
- **Transaction Fees** - Percentage of creator payments
- **Platform Fees** - Take a cut of brand deals
- **Premium Features** - Upsell advanced analytics

**Ready to test the Connect features!**
