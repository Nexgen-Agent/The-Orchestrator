/**
 * Main Application Logic for FOG Dashboard
 */
class FogDashboard {
    constructor() {
        this.currentView = 'overview';
        this.tasks = {};
        this.agents = {};
        this.approvals = [];

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

            this.approvals = await API.getPendingApprovals();

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

        grid.innerHTML = Object.entries(this.agents).map(([name, config]) => `
            <div class="glass-card p-6 space-y-4">
                <div class="flex justify-between items-start">
                    <div class="w-12 h-12 rounded-2xl bg-blue-500/10 flex items-center justify-center">
                        <i class="fas fa-robot text-blue-400 text-xl"></i>
                    </div>
                    <div class="px-2 py-1 bg-teal-500/20 rounded-md border border-teal-500/30">
                        <span class="text-[10px] text-teal-400 font-bold uppercase">Online</span>
                    </div>
                </div>
                <div>
                    <h3 class="font-bold">${name}</h3>
                    <p class="text-xs text-white/40 font-mono truncate">${config.endpoint}</p>
                </div>
                <div class="flex space-x-2">
                    <button class="flex-grow py-2 bg-white/5 hover:bg-white/10 rounded-xl text-xs transition-colors">Configure</button>
                    <button onclick="app.toggleAgent('${name}')" class="px-4 py-2 bg-red-500/20 hover:bg-red-500/40 rounded-xl text-xs text-red-400 transition-colors">Disable</button>
                </div>
            </div>
        `).join('');
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
        await API.pauseOrchestration();
        alert("Orchestration Paused");
    }

    async triggerBuild() {
        const path = prompt("Enter project path for build:");
        if (path) {
            await API.runBuild(path);
            alert("Build Triggered");
        }
    }

    async checkResilience() {
        await API.runResilienceCheck();
        alert("Resilience Check Initiated");
    }
}

// Global App Instance
const app = new FogDashboard();
window.app = app;
