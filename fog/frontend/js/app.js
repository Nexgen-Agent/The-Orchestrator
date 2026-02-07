/**
 * Main Application Logic for FOG Dashboard
 */
class FogDashboard {
    constructor() {
        this.currentView = 'overview';
        this.tasks = {};
        this.agents = {};
        this.approvals = [];
        this.isPaused = false;
        this.systemHealth = null;

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startPolling();
        this.render();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const view = e.currentTarget.getAttribute('data-view');
                this.switchView(view);
            });
        });

        // Overlay buttons
        document.getElementById('approve-btn')?.addEventListener('click', () => this.handleApproval('approve'));
        document.getElementById('reject-btn')?.addEventListener('click', () => this.handleApproval('reject'));
    }

    async startPolling() {
        // Poll system state every 3 seconds
        setInterval(() => this.updateData(), 3000);
        this.updateData();
    }

    async updateData() {
        try {
            const state = await API.getSystemState();
            this.tasks = state.tasks || {};
            this.agents = state.agents || {};
            this.isPaused = state.controls?.is_paused || false;

            this.approvals = await API.getPendingApprovals();
            this.systemHealth = await API.getSystemHealth();
            this.agentToggles = await API.getAgentToggles();

            this.render();
            this.checkApprovals();
        } catch (err) {
            console.error("Data update failed", err);
        }
    }

    switchView(view) {
        this.currentView = view;
        document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
        const activeView = document.getElementById(`${view}-view`);
        if (activeView) activeView.classList.remove('hidden');

        document.querySelectorAll('.nav-item').forEach(n => {
            if (n.getAttribute('data-view') === view) n.classList.add('active');
            else n.classList.remove('active');
        });
    }

    render() {
        this.renderActiveTasks();
        this.renderAgents();
        this.renderFullTaskList();
        this.renderSystemHealth();
    }

    renderActiveTasks() {
        const list = document.getElementById('active-tasks-list');
        if (!list) return;

        const activeTasks = Object.values(this.tasks).filter(t => t.status === 'running' || t.status === 'pending');

        if (activeTasks.length === 0) {
            list.innerHTML = `<p class="text-white/20 italic text-sm text-center py-4">No active tasks</p>`;
            return;
        }

        list.innerHTML = activeTasks.slice(0, 5).map(task => `
            <div class="task-item flex items-center justify-between p-3 bg-white/5 rounded-xl border border-white/5">
                <div class="flex items-center space-x-3">
                    <div class="w-8 h-8 rounded-lg bg-teal-500/10 flex items-center justify-center">
                        <i class="fas fa-terminal text-[10px] text-teal-400"></i>
                    </div>
                    <div>
                        <p class="text-xs font-bold truncate max-w-[120px]">${task.system_name}</p>
                        <p class="text-[10px] text-white/40 uppercase tracking-tighter">${task.task_type}</p>
                    </div>
                </div>
                <div class="text-right">
                    <span class="text-[10px] font-bold uppercase status-${task.status}">${task.status}</span>
                </div>
            </div>
        `).join('');
    }

    renderAgents() {
        const grid = document.getElementById('agents-grid');
        if (!grid) return;

        grid.innerHTML = Object.entries(this.agents).map(([name, config]) => {
            const isEnabled = this.agentToggles && this.agentToggles[name] !== false;
            return `
                <div class="glass-card p-6 space-y-4">
                    <div class="flex justify-between items-start">
                        <div class="w-12 h-12 rounded-2xl bg-blue-500/10 flex items-center justify-center">
                            <i class="fas fa-robot text-blue-400 text-xl"></i>
                        </div>
                        <div class="px-2 py-1 ${isEnabled ? 'bg-teal-500/20 border-teal-500/30' : 'bg-red-500/20 border-red-500/30'} rounded-md border">
                            <span class="text-[10px] ${isEnabled ? 'text-teal-400' : 'text-red-400'} font-bold uppercase">${isEnabled ? 'Online' : 'Disabled'}</span>
                        </div>
                    </div>
                    <div>
                        <h3 class="font-bold">${name}</h3>
                        <p class="text-xs text-white/40 font-mono truncate">${config.endpoint}</p>
                    </div>
                    <div class="flex space-x-2">
                        <button class="flex-grow py-2 bg-white/5 hover:bg-white/10 rounded-xl text-xs transition-colors">Configure</button>
                        <button onclick="app.toggleAgent('${name}', ${isEnabled})" class="px-4 py-2 ${isEnabled ? 'bg-red-500/20 hover:bg-red-500/40 text-red-400' : 'bg-teal-500/20 hover:bg-teal-500/40 text-teal-400'} rounded-xl text-xs transition-colors">
                            ${isEnabled ? 'Disable' : 'Enable'}
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }

    renderSystemHealth() {
        if (!this.systemHealth) return;

        // Update load text
        const workerLoadEl = document.getElementById('worker-load');
        const memoryLoadEl = document.getElementById('memory-load');

        const workerUsage = Math.round(this.systemHealth.overall_task_metrics.success_rate * 100); // Mocking load from success rate for demo
        const memoryUsage = 45; // Placeholder or calculate from something

        if (workerLoadEl) workerLoadEl.innerText = `${workerUsage}%`;
        if (memoryLoadEl) memoryLoadEl.innerText = `${memoryUsage}%`;

        // Update bars
        const workerBar = document.getElementById('worker-bar');
        const memoryBar = document.getElementById('memory-bar');

        if (workerBar) workerBar.style.width = `${workerUsage}%`;
        if (memoryBar) memoryBar.style.width = `${memoryUsage}%`;

        // Update status indicator
        const statusIndicator = document.getElementById('system-status-indicator');
        if (statusIndicator) {
            const statusText = statusIndicator.querySelector('span');
            const statusDot = statusIndicator.querySelector('div');

            if (statusText) statusText.innerText = this.systemHealth.system_status;

            // Adjust colors based on status
            if (this.systemHealth.system_status === 'Nominal') {
                statusIndicator.className = 'flex items-center space-x-2 px-3 py-1 bg-teal-500/20 rounded-full border border-teal-500/30';
                if (statusDot) statusDot.className = 'w-2 h-2 bg-teal-400 rounded-full animate-pulse shadow-[0_0_8px_#4fd1c5]';
            } else if (this.systemHealth.system_status === 'Degraded') {
                statusIndicator.className = 'flex items-center space-x-2 px-3 py-1 bg-yellow-500/20 rounded-full border border-yellow-500/30';
                if (statusDot) statusDot.className = 'w-2 h-2 bg-yellow-400 rounded-full animate-pulse shadow-[0_0_8px_#ecc94b]';
            } else {
                statusIndicator.className = 'flex items-center space-x-2 px-3 py-1 bg-red-500/20 rounded-full border border-red-500/30';
                if (statusDot) statusDot.className = 'w-2 h-2 bg-red-400 rounded-full animate-pulse shadow-[0_0_8px_#f56565]';
            }
        }

        // Update pause button
        const pauseBtn = document.getElementById('pause-btn');
        if (pauseBtn) {
            if (this.isPaused) {
                pauseBtn.innerHTML = '<i class="fas fa-play mr-2 text-teal-400"></i> Resume System';
            } else {
                pauseBtn.innerHTML = '<i class="fas fa-pause mr-2 text-teal-400"></i> Pause System';
            }
        }
    }

    renderFullTaskList() {
        const list = document.getElementById('full-task-list');
        if (!list) return;

        list.innerHTML = Object.values(this.tasks).sort((a,b) => new Date(b.timestamp) - new Date(a.timestamp)).map(task => `
             <div class="task-item flex items-center justify-between p-4 bg-white/5 rounded-2xl border border-white/5">
                <div class="flex items-center space-x-4">
                    <div class="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center">
                        <i class="fas fa-cog text-white/20"></i>
                    </div>
                    <div>
                        <p class="text-sm font-bold">${task.system_name} <span class="text-white/20 font-normal ml-2">ID: ${task.task_id.slice(0,8)}</span></p>
                        <p class="text-xs text-white/40">${new Date(task.timestamp).toLocaleString()}</p>
                    </div>
                </div>
                <div>
                    <span class="px-3 py-1 rounded-full bg-white/5 text-[10px] font-bold uppercase status-${task.status}">${task.status}</span>
                </div>
            </div>
        `).join('');
    }

    checkApprovals() {
        const overlay = document.getElementById('approval-overlay');
        const details = document.getElementById('approval-details');

        if (this.approvals.length > 0 && overlay && details) {
            const current = this.approvals[0];
            this.currentApprovalId = current.request_id;

            details.innerHTML = `
                <div class="flex justify-between"><span class="text-white/40">Task ID:</span> <span>${current.task_id}</span></div>
                <div class="flex justify-between"><span class="text-white/40">Requester:</span> <span>${current.requester}</span></div>
                <div class="flex justify-between"><span class="text-white/40">Type:</span> <span>${current.details.task_type}</span></div>
                <div class="mt-4 pt-4 border-t border-white/5 text-[10px] text-teal-400">
                    High-risk action requires human verification.
                </div>
            `;

            overlay.classList.remove('hidden');
        } else if (overlay) {
            overlay.classList.add('hidden');
        }
    }

    async toggleAgent(name, currentEnabled) {
        try {
            await API.toggleAgent(name, !currentEnabled);
            this.updateData();
        } catch (err) {
            alert(`Failed to toggle agent: ${err.message}`);
        }
    }

    async handleApproval(action) {
        if (!this.currentApprovalId) return;

        try {
            if (action === 'approve') await API.approveRequest(this.currentApprovalId);
            else await API.rejectRequest(this.currentApprovalId);

            this.currentApprovalId = null;
            this.updateData();
        } catch (err) {
            alert(`Action failed: ${err.message}`);
        }
    }

    // Command methods
    async pauseOrchestration() {
        try {
            if (this.isPaused) {
                await API.resumeOrchestration();
                alert("Orchestration Resumed");
            } else {
                await API.pauseOrchestration();
                alert("Orchestration Paused");
            }
            this.updateData();
        } catch (err) {
            alert(`Failed to toggle orchestration: ${err.message}`);
        }
    }

    async triggerBuild() {
        const input = document.getElementById('builder-path');
        const path = input ? input.value : prompt("Enter project path for build:");
        if (path) {
            try {
                await API.runBuild(path);
                alert("Build Triggered");
            } catch (err) {
                alert(`Build failed to start: ${err.message}`);
            }
        }
    }

    async triggerDeployment() {
        const input = document.getElementById('deploy-path');
        const path = input ? input.value : prompt("Enter project path for deployment:");
        if (path) {
            try {
                // Assuming API has runDeployment or similar, or we use submitTask
                await API.post('/deployment/run', { project_path: path });
                alert("Deployment Triggered");
            } catch (err) {
                alert(`Deployment failed to start: ${err.message}`);
            }
        }
    }

    async triggerLearningCycle() {
        try {
            await API.post('/learning/trigger');
            alert("Learning Cycle Initiated");
        } catch (err) {
            alert(`Failed to trigger learning: ${err.message}`);
        }
    }

    async checkResilience() {
        await API.runResilienceCheck();
        alert("Resilience Check Initiated");
    }

    showDispatchModal() {
        document.getElementById('dispatch-modal')?.classList.remove('hidden');
    }

    hideDispatchModal() {
        document.getElementById('dispatch-modal')?.classList.add('hidden');
    }

    async handleDispatch() {
        const type = document.getElementById('dispatch-type').value;
        const desc = document.getElementById('dispatch-desc').value;

        if (!desc) {
            alert("Please enter a description");
            return;
        }

        try {
            await API.submitTask({
                task_type: type,
                description: desc,
                system_name: "Manual Dispatch"
            });
            this.hideDispatchModal();
            this.updateData();
            alert("Task Dispatched successfully");
        } catch (err) {
            alert(`Dispatch failed: ${err.message}`);
        }
    }
}

// Global App Instance
const app = new FogDashboard();
window.app = app;
