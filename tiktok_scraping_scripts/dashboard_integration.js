#!/usr/bin/env node
/**
 * TikTok Dashboard Integration
 * Provides Node.js interface to the Python scraping system
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

class TikTokDashboardIntegration {
    constructor(pythonScriptDir = __dirname) {
        this.pythonScriptDir = pythonScriptDir;
        this.integrationScript = path.join(pythonScriptDir, 'integration_api.py');
    }

    /**
     * Execute Python script and return JSON result
     */
    async executePythonScript(args) {
        return new Promise((resolve, reject) => {
            const pythonProcess = spawn('python', [this.integrationScript, ...args], {
                cwd: this.pythonScriptDir,
                stdio: ['pipe', 'pipe', 'pipe']
            });

            let stdout = '';
            let stderr = '';

            pythonProcess.stdout.on('data', (data) => {
                stdout += data.toString();
            });

            pythonProcess.stderr.on('data', (data) => {
                stderr += data.toString();
            });

            pythonProcess.on('close', (code) => {
                if (code === 0) {
                    try {
                        const result = JSON.parse(stdout);
                        resolve(result);
                    } catch (error) {
                        reject(new Error(`Failed to parse Python output: ${error.message}`));
                    }
                } else {
                    reject(new Error(`Python script failed with code ${code}: ${stderr}`));
                }
            });

            pythonProcess.on('error', (error) => {
                reject(new Error(`Failed to start Python process: ${error.message}`));
            });
        });
    }

    /**
     * Scrape profile data for a username
     */
    async scrapeProfile(username) {
        return this.executePythonScript(['--username', username, '--type', 'profile']);
    }

    /**
     * Scrape video data for a username
     */
    async scrapeVideos(username, limit = 50) {
        return this.executePythonScript(['--username', username, '--type', 'videos']);
    }

    /**
     * Get earnings analysis for a username
     */
    async getEarningsAnalysis(username) {
        return this.executePythonScript(['--username', username, '--type', 'earnings']);
    }

    /**
     * Get engagement analysis for a username
     */
    async getEngagementAnalysis(username) {
        return this.executePythonScript(['--username', username, '--type', 'engagement']);
    }

    /**
     * Get comprehensive analysis for a username
     */
    async getComprehensiveAnalysis(username) {
        return this.executePythonScript(['--username', username, '--type', 'comprehensive']);
    }

    /**
     * Check if Python integration is available
     */
    async checkAvailability() {
        try {
            const result = await this.executePythonScript(['--username', 'test', '--type', 'profile']);
            return {
                available: true,
                message: 'TikTok scraping integration is ready'
            };
        } catch (error) {
            return {
                available: false,
                message: `Integration not available: ${error.message}`
            };
        }
    }

    /**
     * Get cached data if available
     */
    getCachedData(username, type = 'comprehensive') {
        const dataDir = path.join(this.pythonScriptDir, 'scraped_data');
        const files = {
            profile: path.join(dataDir, `${username}_profile.json`),
            videos: path.join(dataDir, `${username}_videos.json`)
        };

        const cached = {};
        
        if (type === 'profile' || type === 'comprehensive') {
            if (fs.existsSync(files.profile)) {
                try {
                    cached.profile = JSON.parse(fs.readFileSync(files.profile, 'utf8'));
                } catch (error) {
                    console.error('Error reading cached profile:', error);
                }
            }
        }

        if (type === 'videos' || type === 'comprehensive') {
            if (fs.existsSync(files.videos)) {
                try {
                    cached.videos = JSON.parse(fs.readFileSync(files.videos, 'utf8'));
                } catch (error) {
                    console.error('Error reading cached videos:', error);
                }
            }
        }

        return cached;
    }
}

// Export for use in other modules
module.exports = TikTokDashboardIntegration;

// CLI interface for testing
if (require.main === module) {
    const integration = new TikTokDashboardIntegration();
    
    async function main() {
        const args = process.argv.slice(2);
        
        if (args.length === 0) {
            console.log('Usage: node dashboard_integration.js <username> [type]');
            console.log('Types: profile, videos, earnings, engagement, comprehensive');
            process.exit(1);
        }

        const username = args[0];
        const type = args[1] || 'comprehensive';

        try {
            console.log(`Analyzing @${username} (${type})...`);
            
            let result;
            switch (type) {
                case 'profile':
                    result = await integration.scrapeProfile(username);
                    break;
                case 'videos':
                    result = await integration.scrapeVideos(username);
                    break;
                case 'earnings':
                    result = await integration.getEarningsAnalysis(username);
                    break;
                case 'engagement':
                    result = await integration.getEngagementAnalysis(username);
                    break;
                case 'comprehensive':
                default:
                    result = await integration.getComprehensiveAnalysis(username);
                    break;
            }

            console.log(JSON.stringify(result, null, 2));
        } catch (error) {
            console.error('Error:', error.message);
            process.exit(1);
        }
    }

    main();
}
