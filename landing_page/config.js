// Server-side configuration (DO NOT expose this in client-side code)
// This file should be used in your backend server, not in the browser

const config = {
    stripe: {
        secretKey: process.env.STRIPE_SECRET_KEY,
        publishableKey: process.env.STRIPE_PUBLISHABLE_KEY
    },
    webhookSecret: process.env.STRIPE_WEBHOOK_SECRET,
    environment: process.env.NODE_ENV || 'development'
};

module.exports = config;
