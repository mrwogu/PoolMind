// PoolMind Frontend Application
class PoolMindApp {
    constructor() {
        this.isConnected = false;
        this.refreshInterval = 1000;
        this.retryDelay = 5000;
        this.lastUpdateTime = 0;
        this.refreshTimer = null;
        this.fpsCounter = 0;
        this.fpsLastTime = Date.now();

        this.initializeApp();
    }

    initializeApp() {
        this.setupThemeToggle();
        this.setupEventListeners();
        this.startDataRefresh();
        this.setupFullscreen();

        console.log('🎱 PoolMind app initialized');
    }

    // Theme Management
    setupThemeToggle() {
        const themeToggle = document.getElementById('theme-toggle');
        const darkIcon = document.getElementById('theme-toggle-dark-icon');
        const lightIcon = document.getElementById('theme-toggle-light-icon');

        // Check for saved theme preference or default to 'dark'
        const currentTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.classList.toggle('dark', currentTheme === 'dark');

        this.updateThemeIcons(currentTheme === 'dark');

        themeToggle.addEventListener('click', () => {
            const isDark = document.documentElement.classList.contains('dark');
            document.documentElement.classList.toggle('dark');

            const newTheme = isDark ? 'light' : 'dark';
            localStorage.setItem('theme', newTheme);
            this.updateThemeIcons(!isDark);

            // Add smooth transition effect
            document.body.style.transition = 'background-color 0.3s ease';
            setTimeout(() => {
                document.body.style.transition = '';
            }, 300);
        });
    }

    updateThemeIcons(isDark) {
        const darkIcon = document.getElementById('theme-toggle-dark-icon');
        const lightIcon = document.getElementById('theme-toggle-light-icon');

        if (isDark) {
            darkIcon.classList.remove('hidden');
            lightIcon.classList.add('hidden');
        } else {
            darkIcon.classList.add('hidden');
            lightIcon.classList.remove('hidden');
        }
    }

    // Event Listeners
    setupEventListeners() {
        // Stream error handling
        const streamImg = document.getElementById('live-stream');
        streamImg.addEventListener('error', () => this.handleStreamError());
        streamImg.addEventListener('load', () => this.handleStreamLoad());

        // Visibility change handling
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseRefresh();
            } else {
                this.resumeRefresh();
            }
        });

        // Window focus/blur
        window.addEventListener('focus', () => this.resumeRefresh());
        window.addEventListener('blur', () => this.pauseRefresh());
    }

    // Fullscreen functionality
    setupFullscreen() {
        const fullscreenBtn = document.getElementById('fullscreen-btn');
        const streamContainer = document.querySelector('.video-container');

        fullscreenBtn.addEventListener('click', () => {
            if (!document.fullscreenElement) {
                streamContainer.requestFullscreen().catch(err => {
                    console.error('Fullscreen error:', err);
                });
            } else {
                document.exitFullscreen();
            }
        });

        document.addEventListener('fullscreenchange', () => {
            const isFullscreen = !!document.fullscreenElement;
            fullscreenBtn.textContent = isFullscreen ? '🪟 Exit Fullscreen' : '📺 Fullscreen';
        });
    }

    // Data Management
    async startDataRefresh() {
        await this.refreshData();
        this.scheduleNextRefresh();
    }

    async refreshData() {
        try {
            const [stateResponse, eventsResponse] = await Promise.all([
                fetch('/state'),
                fetch('/events')
            ]);

            if (!stateResponse.ok || !eventsResponse.ok) {
                throw new Error('API request failed');
            }

            const state = await stateResponse.json();
            const events = await eventsResponse.json();

            this.updateUI(state, events);
            this.setConnectionStatus(true);
            this.lastUpdateTime = Date.now();

        } catch (error) {
            console.error('Data refresh failed:', error);
            this.setConnectionStatus(false);
        }
    }

    scheduleNextRefresh() {
        this.refreshTimer = setTimeout(() => {
            this.refreshData().then(() => this.scheduleNextRefresh());
        }, this.refreshInterval);
    }

    pauseRefresh() {
        if (this.refreshTimer) {
            clearTimeout(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    resumeRefresh() {
        if (!this.refreshTimer) {
            this.scheduleNextRefresh();
        }
    }

    // UI Updates
    updateUI(state, events) {
        this.updateGameStatus(state);
        this.updateBallCounts(state);
        this.updateEvents(events);
        this.updateAnalytics(state);
        this.updateFPS();
    }

    updateGameStatus(state) {
        const container = document.getElementById('game-status');
        const statusItems = [
            { label: 'Total Tracked', value: state.total_tracked || 0, icon: '🎯' },
            { label: 'Active Balls', value: state.active_balls || 0, icon: '⚫' },
            { label: 'Total Potted', value: state.potted || 0, icon: '🕳️' },
            { label: 'Game State', value: this.formatGameState(state.game_state), icon: '🎮' }
        ];

        container.innerHTML = statusItems.map(item => `
            <div class="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                <div class="flex items-center space-x-2">
                    <span class="text-lg">${item.icon}</span>
                    <span class="text-sm text-gray-300">${item.label}</span>
                </div>
                <span class="font-semibold text-white">${item.value}</span>
            </div>
        `).join('');
    }

    updateBallCounts(state) {
        // Active balls with progress
        const activeBalls = state.active_balls || 0;
        const maxBalls = 16; // Standard pool set
        const progressPercent = (activeBalls / maxBalls) * 100;

        document.getElementById('active-balls-count').textContent = activeBalls;
        document.getElementById('active-balls-progress').style.width = `${progressPercent}%`;

        // Individual ball types
        document.getElementById('cue-ball-count').textContent = state.active_cue || 0;
        document.getElementById('solid-balls-count').textContent = state.active_solid || 0;
        document.getElementById('stripe-balls-count').textContent = state.active_stripe || 0;

        // Status indicators
        document.getElementById('cue-ball-status').textContent =
            (state.active_cue > 0) ? 'On table' : 'Potted/Missing';
        document.getElementById('solid-balls-potted').textContent =
            `Potted: ${state.solid_potted || 0}`;
        document.getElementById('stripe-balls-potted').textContent =
            `Potted: ${state.stripe_potted || 0}`;
    }

    updateEvents(events) {
        const container = document.getElementById('events-container');

        if (!events || events.length === 0) {
            container.innerHTML = `
                <div class="text-center text-gray-400 py-8">
                    <div class="text-2xl mb-2">🔍</div>
                    <p>No events yet</p>
                </div>
            `;
            return;
        }

        const recentEvents = events.slice(-10).reverse();

        container.innerHTML = recentEvents.map(event => {
            const time = new Date(event.ts * 1000).toLocaleTimeString();
            const { icon, color, description } = this.getEventDisplay(event);

            return `
                <div class="flex items-center space-x-3 p-3 bg-white/5 rounded-lg animate-slide-in">
                    <div class="text-lg">${icon}</div>
                    <div class="flex-1 min-w-0">
                        <div class="flex items-center justify-between">
                            <span class="text-sm font-medium ${color}">${event.type}</span>
                            <span class="text-xs text-gray-400">${time}</span>
                        </div>
                        <p class="text-xs text-gray-300 truncate">${description}</p>
                    </div>
                </div>
            `;
        }).join('');
    }

    updateAnalytics(state) {
        const container = document.getElementById('analytics-container');

        const totalBalls = 16;
        const activeBalls = state.active_balls || 0;
        const pottedBalls = state.potted || 0;
        const trackingAccuracy = totalBalls > 0 ? ((activeBalls + pottedBalls) / totalBalls * 100).toFixed(1) : 0;

        const analytics = [
            {
                label: 'Tracking Accuracy',
                value: `${trackingAccuracy}%`,
                progress: trackingAccuracy,
                color: trackingAccuracy > 80 ? 'bg-green-500' : trackingAccuracy > 60 ? 'bg-yellow-500' : 'bg-red-500'
            },
            {
                label: 'Ball Recognition',
                value: `${activeBalls + pottedBalls}/${totalBalls}`,
                progress: ((activeBalls + pottedBalls) / totalBalls) * 100,
                color: 'bg-blue-500'
            },
            {
                label: 'Session Uptime',
                value: this.getUptime(),
                progress: 100,
                color: 'bg-purple-500'
            }
        ];

        container.innerHTML = analytics.map(item => `
            <div class="space-y-2">
                <div class="flex justify-between items-center">
                    <span class="text-sm text-gray-300">${item.label}</span>
                    <span class="text-sm font-semibold text-white">${item.value}</span>
                </div>
                <div class="w-full bg-gray-700 rounded-full h-2">
                    <div class="${item.color} h-2 rounded-full transition-all duration-500"
                         style="width: ${item.progress}%"></div>
                </div>
            </div>
        `).join('');
    }

    // Helper Methods
    formatGameState(state) {
        const stateMap = {
            'break': 'Break Shot',
            'open_table': 'Open Table',
            'solid_player': 'Solids Turn',
            'stripe_player': 'Stripes Turn',
            'eight_ball': '8-Ball Shot',
            'game_over': 'Game Over',
            'waiting': 'Waiting...'
        };
        return stateMap[state] || 'Unknown';
    }

    getEventDisplay(event) {
        const eventTypes = {
            'pot': { icon: '🎯', color: 'text-green-400', description: event.info || 'Ball potted' },
            'scratch': { icon: '❌', color: 'text-red-400', description: event.info || 'Scratch occurred' },
            'foul': { icon: '⚠️', color: 'text-yellow-400', description: event.info || 'Foul committed' },
            'break': { icon: '💥', color: 'text-blue-400', description: event.info || 'Break shot' },
            'eight_ball_win': { icon: '🏆', color: 'text-gold-400', description: event.info || 'Game won!' },
            'default': { icon: '📋', color: 'text-gray-400', description: event.info || 'Game event' }
        };

        return eventTypes[event.type] || eventTypes.default;
    }

    getUptime() {
        if (!this.lastUpdateTime) return '0s';

        const uptime = Date.now() - this.lastUpdateTime;
        const seconds = Math.floor(uptime / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);

        if (hours > 0) return `${hours}h ${minutes % 60}m`;
        if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
        return `${seconds}s`;
    }

    updateFPS() {
        const now = Date.now();
        this.fpsCounter++;

        if (now - this.fpsLastTime >= 1000) {
            const fps = Math.round(this.fpsCounter * 1000 / (now - this.fpsLastTime));
            document.getElementById('fps-counter').textContent = fps;

            this.fpsCounter = 0;
            this.fpsLastTime = now;
        }
    }

    // Connection Status
    setConnectionStatus(connected) {
        this.isConnected = connected;
        const indicator = document.getElementById('status-indicator');
        const statusText = document.getElementById('status-text');
        const streamStatus = document.getElementById('stream-status');

        if (connected) {
            indicator.className = 'w-3 h-3 rounded-full status-dot-online animate-pulse-slow';
            statusText.textContent = 'Connected';
            statusText.className = 'text-sm font-medium text-green-400';
            streamStatus.textContent = 'MJPEG • Live';
        } else {
            indicator.className = 'w-3 h-3 rounded-full status-dot-offline animate-pulse-slow';
            statusText.textContent = 'Disconnected';
            statusText.className = 'text-sm font-medium text-red-400';
            streamStatus.textContent = 'Stream Offline';
        }
    }

    // Stream Error Handling
    handleStreamError() {
        console.warn('Stream error occurred');
        this.setConnectionStatus(false);

        // Try to reload the stream after a delay
        setTimeout(() => {
            const streamImg = document.getElementById('live-stream');
            const currentSrc = streamImg.src;
            streamImg.src = '';
            streamImg.src = currentSrc + '?t=' + Date.now();
        }, 2000);
    }

    handleStreamLoad() {
        if (!this.isConnected) {
            this.setConnectionStatus(true);
        }
    }
}

// Global Functions
async function resetGame() {
    try {
        const response = await fetch('/game/reset', { method: 'POST' });
        if (response.ok) {
            // Show success notification
            showNotification('Game reset successfully', 'success');
        } else {
            throw new Error('Reset failed');
        }
    } catch (error) {
        console.error('Failed to reset game:', error);
        showNotification('Failed to reset game', 'error');
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `
        fixed top-4 right-4 z-50 px-4 py-3 rounded-lg text-white font-medium
        transform transition-all duration-300 translate-x-full opacity-0
        ${type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500'}
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
        notification.classList.remove('translate-x-full', 'opacity-0');
    }, 100);

    // Animate out and remove
    setTimeout(() => {
        notification.classList.add('translate-x-full', 'opacity-0');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.poolMindApp = new PoolMindApp();
});
