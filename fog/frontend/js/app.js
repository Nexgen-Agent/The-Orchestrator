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
        this.sessionId = 'session-' + Math.random().toString(36).substr(2, 9);
        this.setupEventListeners();
        this.setupKeyboardHandling();
        this.startPolling();
        this.render();
        this.appendMessage('orchestrator', 'System initialized. I am the FOG Orchestrator. How can I assist you today?');
    }

    setupKeyboardHandling() {
        const visualViewport = window.visualViewport;
        if (!visualViewport) return;

        const handleViewportChange = () => {
            const wrapper = document.querySelector('.fixed-chat-input-wrapper');
            if (!wrapper || this.currentView !== 'agents') return;

            // Calculate the distance from the bottom of the layout viewport to the bottom of the visual viewport
            // This is the most stable way to detect keyboard height + scroll/pan offset
            const layoutHeight = window.innerHeight;
            const visualBottom = visualViewport.height + visualViewport.offsetTop;
            const offset = Math.max(0, layoutHeight - visualBottom);

            // Directly set the bottom property. If offset is small (e.g. browser bar changes), snap to 10px.
            if (offset < 30) {
                wrapper.style.bottom = '10px';
            } else {
                // Cap the offset to 50% of screen height to prevent "middle of screen" jumping
                const cappedOffset = Math.min(offset + 10, layoutHeight * 0.5);
                wrapper.style.bottom = `${cappedOffset}px`;
            }

            // Keep conversation scrolled to bottom when keyboard is up
            const conv = document.getElementById('chat-conversation');
            if (conv && offset > 50) {
                conv.scrollTop = conv.scrollHeight;
            }
        };

        visualViewport.addEventListener('resize', handleViewportChange);
        visualViewport.addEventListener('scroll', handleViewportChange);

        // Also trigger on input focus to ensure immediate correction
        document.addEventListener('focusin', (e) => {
            if (e.target.id === 'chat-input') {
                setTimeout(handleViewportChange, 100);
                setTimeout(handleViewportChange, 300); // Second pass for slower keyboard animations
            }
        });
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
            console.log("Fetching system state...");
            const state = await API.getSystemState();
            console.log("System state received:", state);
            this.tasks = state.tasks || {};
            this.agents = state.agents || {};
            this.isPaused = state.controls?.is_paused || false;

            try {
                this.approvals = await API.getPendingApprovals();
            } catch (e) { console.warn("Failed to fetch approvals", e); }

            try {
                this.systemHealth = await API.getSystemHealth();
            } catch (e) { console.warn("Failed to fetch system health", e); }

            try {
                this.agentToggles = await API.getAgentToggles();
            } catch (e) { console.warn("Failed to fetch agent toggles", e); }

            this.render();
            this.checkApprovals();
        } catch (err) {
            console.error("Critical data update failure:", err);
            this.showError(`Critical system failure: ${err.message}`);
            // Even if critical update fails, we should try to render what we have
            this.render();
        }
    }

    showError(msg) {
        const errEl = document.getElementById('global-error');
        const errMsg = document.getElementById('error-message');
        if (errEl && errMsg) {
            errMsg.innerText = msg;
            errEl.classList.remove('hidden');
            setTimeout(() => errEl.classList.add('hidden'), 5000);
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
        this.renderAgentsLanding();
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
        // Legacy mini list if it exists
        const miniList = document.getElementById('agents-mini-list');
        if (!miniList) return;

        miniList.innerHTML = Object.entries(this.agents).map(([name, config]) => {
            const isEnabled = this.agentToggles && this.agentToggles[name] !== false;
            return `
                <div class="p-3 bg-white/5 rounded-xl border border-white/5 flex items-center justify-between group hover:bg-white/10 transition-colors">
                    <div class="flex items-center space-x-3">
                        <div class="w-8 h-8 rounded-lg ${isEnabled ? 'bg-teal-500/10' : 'bg-red-500/10'} flex items-center justify-center">
                            <i class="fas fa-robot ${isEnabled ? 'text-teal-400' : 'text-red-400'} text-xs"></i>
                        </div>
                        <span class="text-xs font-bold">${name}</span>
                    </div>
                    <div class="flex items-center space-x-2">
                        <div class="w-1.5 h-1.5 rounded-full ${isEnabled ? 'bg-teal-400 animate-pulse' : 'bg-red-400'}"></div>
                        <span class="text-[8px] text-white/20 uppercase font-bold">${isEnabled ? 'Online' : 'Off'}</span>
                    </div>
                </div>
            `;
        }).join('');
    }

    renderAgentsLanding() {
        const grid = document.getElementById('agents-landing-grid');
        if (!grid) return;

        if (Object.keys(this.agents).length === 0) {
            grid.innerHTML = `<div class="col-span-full py-12 text-center text-white/20 italic">No agents registered in the ecosystem</div>`;
            return;
        }

        grid.innerHTML = Object.entries(this.agents).map(([name, config]) => {
            const isEnabled = this.agentToggles && this.agentToggles[name] !== false;
            return `
                <div class="agent-landing-card group" onclick="app.showAgentDetails('${name}')">
                    <div class="flex justify-between items-start">
                        <div class="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center group-hover:bg-teal-500/10 transition-colors">
                            <i class="fas fa-robot ${isEnabled ? 'text-teal-400' : 'text-white/20'} text-xl"></i>
                        </div>
                        <div class="flex items-center space-x-2">
                            <div class="w-1.5 h-1.5 rounded-full ${isEnabled ? 'bg-teal-400 animate-pulse' : 'bg-red-400'}"></div>
                            <span class="text-[8px] text-white/40 uppercase font-bold tracking-widest">${isEnabled ? 'Active' : 'Standby'}</span>
                        </div>
                    </div>
                    <div>
                        <h4 class="text-sm font-bold mt-4">${name}</h4>
                        <p class="text-[10px] text-white/40 uppercase mt-1">Status: ${isEnabled ? 'Nominal' : 'Disabled'}</p>
                    </div>
                </div>
            `;
        }).join('');
    }

    showAgentDetails(name) {
        const agent = this.agents[name];
        if (!agent) return;

        const modal = document.getElementById('agent-details-modal');
        const isEnabled = this.agentToggles && this.agentToggles[name] !== false;

        document.getElementById('modal-agent-name').innerText = name;
        document.getElementById('modal-agent-status-text').innerText = isEnabled ? 'Online' : 'Offline';
        document.getElementById('modal-agent-status-text').className = isEnabled ? 'text-xs font-bold uppercase tracking-widest text-teal-400' : 'text-xs font-bold uppercase tracking-widest text-red-400';
        document.getElementById('modal-agent-status-dot').className = isEnabled ? 'w-2 h-2 rounded-full bg-teal-400 animate-pulse' : 'w-2 h-2 rounded-full bg-red-400';

        // Mock health and progress for UI
        document.getElementById('modal-agent-health').innerText = '100%';
        document.getElementById('modal-agent-health-bar').style.width = '100%';
        document.getElementById('modal-agent-progress').innerText = isEnabled ? 'Stable' : 'Paused';
        document.getElementById('modal-agent-progress-bar').style.width = isEnabled ? '100%' : '20%';

        const toggleBtn = document.getElementById('modal-toggle-btn');
        toggleBtn.innerText = isEnabled ? 'Disable Agent' : 'Enable Agent';
        toggleBtn.onclick = () => {
            this.toggleAgent(name, isEnabled);
            this.hideAgentDetails();
        };

        modal.classList.remove('hidden');
    }

    hideAgentDetails() {
        document.getElementById('agent-details-modal')?.classList.add('hidden');
    }

    renderSystemHealth() {
        if (!this.systemHealth) return;

        // Update load text
        const workerLoadEl = document.getElementById('worker-load');
        const memoryLoadEl = document.getElementById('memory-load');

        const cpuUsage = Math.round(this.systemHealth.resource_usage?.cpu_percent || 0);
        const memoryUsage = Math.round(this.systemHealth.resource_usage?.memory_percent || 0);

        if (workerLoadEl) workerLoadEl.innerText = `${cpuUsage}%`;
        if (memoryLoadEl) memoryLoadEl.innerText = `${memoryUsage}%`;

        // Update bars
        const workerBar = document.getElementById('worker-bar');
        const memoryBar = document.getElementById('memory-bar');

        if (workerBar) workerBar.style.width = `${cpuUsage}%`;
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

        // Emergency View Updates
        const safeModeStatus = document.getElementById('safe-mode-status');
        const lockStatus = document.getElementById('lock-status');
        if (safeModeStatus) {
            const isSafe = this.systemHealth.safe_mode_active || false;
            safeModeStatus.innerText = isSafe ? 'Active' : 'Inactive';
            safeModeStatus.className = isSafe
                ? 'text-xs font-mono px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/20 uppercase'
                : 'text-xs font-mono px-2 py-0.5 rounded bg-green-500/10 text-green-400 border border-green-500/20 uppercase';
        }
        if (lockStatus) {
            lockStatus.innerText = this.isPaused ? 'Locked' : 'Unlocked';
            lockStatus.className = this.isPaused
                ? 'text-xs font-mono px-2 py-0.5 rounded bg-yellow-500/10 text-yellow-400 border border-yellow-500/20 uppercase'
                : 'text-xs font-mono px-2 py-0.5 rounded bg-green-500/10 text-green-400 border border-green-500/20 uppercase';
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
                await API.runDeployment(path);
                alert("Deployment Triggered");
                this.updateData();
            } catch (err) {
                this.showError(`Deployment failed: ${err.message}`);
            }
        }
    }

    async triggerLearningCycle() {
        try {
            await API.runLearningCycle();
            alert("Learning Cycle Initiated");
            this.updateData();
        } catch (err) {
            this.showError(`Learning cycle failed: ${err.message}`);
        }
    }

    async checkResilience() {
        await API.runResilienceCheck();
        alert("Resilience Check Initiated");
    }

    async emergencyStop() {
        if (confirm("Are you sure you want to trigger an EMERGENCY STOP? This will halt all operations.")) {
            try {
                await API.emergencyStop();
                alert("Emergency Stop Triggered");
                this.updateData();
            } catch (err) {
                alert(`Action failed: ${err.message}`);
            }
        }
    }

    async triggerRollback() {
        const id = prompt("Enter Backup ID to rollback to (leave blank for latest):");
        if (confirm(`Trigger rollback to ${id || 'latest'}?`)) {
            try {
                await API.triggerRollback(id);
                alert("Rollback Triggered");
                this.updateData();
            } catch (err) {
                alert(`Rollback failed: ${err.message}`);
            }
        }
    }

    autoResizeInput(textarea) {
        textarea.style.height = '48px';
        const scrollHeight = textarea.scrollHeight;
        if (scrollHeight > 48) {
            textarea.style.height = Math.min(scrollHeight, 240) + 'px';
        }
    }

    handleFileSelect(event) {
        const files = Array.from(event.target.files);
        const container = document.getElementById('file-preview-container');
        if (!container) return;

        container.classList.remove('hidden');

        files.forEach(file => {
            const item = document.createElement('div');
            item.className = 'file-preview-item animate-in fade-in zoom-in duration-200';

            const isImage = file.type.startsWith('image/');
            const icon = isImage ? '<i class="fas fa-image text-teal-400"></i>' : '<i class="fas fa-file-alt text-blue-400"></i>';

            item.innerHTML = `
                ${icon}
                <span class="text-[10px] truncate max-w-[100px]">${file.name}</span>
                <button onclick="this.parentElement.remove(); app.checkFilePreviews()" class="text-white/20 hover:text-red-400">
                    <i class="fas fa-times text-[8px]"></i>
                </button>
            `;
            container.appendChild(item);
        });

        event.target.value = ''; // Reset input
    }

    checkFilePreviews() {
        const container = document.getElementById('file-preview-container');
        if (container && container.children.length === 0) {
            container.classList.add('hidden');
        }
    }

    async sendChatMessage() {
        const input = document.getElementById('chat-input');
        if (!input) return;
        const prompt = input.value.trim();
        if (!prompt) return;

        // Clear input
        input.value = '';
        input.style.height = 'auto';
        this.checkFilePreviews();
        const container = document.getElementById('file-preview-container');
        if (container) container.innerHTML = '';
        if (container) container.classList.add('hidden');

        // Add user message to UI
        this.appendMessage('user', prompt);
        this.showTyping(true);

        try {
            const response = await API.sendChat(prompt, this.sessionId);

            this.showTyping(false);
            this.appendMessage('orchestrator', response.message);

            if (response.status === 'completed') {
                this.logToConsole(`Orchestrator responded directly.`, 'success');
            } else {
                this.logToConsole(`Orchestrator initiated background process. Task ID: ${response.task_id}`, 'success');
                // We still poll for the task result but we don't spam the chat with "Agent Assigned"
                this.pollTaskResult(response.task_id);
            }

        } catch (err) {
            this.showTyping(false);
            this.appendMessage('orchestrator', `Error: ${err.message}`);
            this.logToConsole(`Chat error: ${err.message}`, 'error');
        }
    }

    appendMessage(role, text) {
        const conversation = document.getElementById('chat-conversation');
        if (!conversation) return;

        const isUser = role === 'user';
        const rowDiv = document.createElement('div');
        rowDiv.className = `chat-message-row ${isUser ? 'user' : 'orchestrator'} animate-in fade-in slide-in-from-bottom-2 duration-300`;

        // Simple Markdown-to-HTML (Links and Bold)
        let processedText = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/### (.*?)\n/g, '<h3 class="font-bold text-teal-400 mt-2">$1</h3>')
            .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" class="text-teal-400 underline hover:text-teal-300 transition-colors">$1</a>')
            .replace(/\n/g, '<br>');

        rowDiv.innerHTML = `
            <div class="chat-bubble ${isUser ? 'user' : 'orchestrator'}">
                <div class="text-sm leading-relaxed">${processedText}</div>
                <div class="mt-2 pt-2 border-t ${isUser ? 'border-white/10' : 'border-white/5'} flex items-center justify-between">
                    <p class="text-[8px] ${isUser ? 'text-white/50' : 'text-white/30'} uppercase font-bold tracking-widest">
                        ${isUser ? 'User' : 'FOG Orchestrator'}
                    </p>
                    <p class="text-[8px] ${isUser ? 'text-white/50' : 'text-white/30'} font-medium">
                        ${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    </p>
                </div>
            </div>
        `;

        conversation.appendChild(rowDiv);
        conversation.scrollTop = conversation.scrollHeight;
    }

    showTyping(show) {
        const typing = document.getElementById('chat-typing');
        if (typing) {
            if (show) typing.classList.remove('hidden');
            else typing.classList.add('hidden');
        }
    }

    async pollTaskResult(taskId) {
        let attempts = 0;
        const maxAttempts = 30; // 90 seconds

        const interval = setInterval(async () => {
            attempts++;
            try {
                const task = await API.getTaskStatus(taskId);
                if (task.status === 'completed') {
                    clearInterval(interval);
                    this.showTyping(false);

                    const resultMsg = task.result?.message || "Task completed successfully.";
                    this.appendMessage('orchestrator', resultMsg);
                    this.updateData(); // Refresh global state
                } else if (task.status === 'failed') {
                    clearInterval(interval);
                    this.showTyping(false);
                    this.appendMessage('orchestrator', `Task failed: ${task.result?.error || 'Unknown error'}`);
                }
            } catch (err) {
                console.warn("Polling error", err);
            }

            if (attempts >= maxAttempts) {
                clearInterval(interval);
                this.showTyping(false);
                this.appendMessage('orchestrator', "Task is taking longer than expected. Please check the Task Management tab.", 'System');
            }
        }, 3000);
    }

    async runAgentCommand() {
        // Legacy method replaced by sendChatMessage
        this.sendChatMessage();
    }

    stopAgentCommand() {
        this.logToConsole("Stop command issued (Not fully implemented on backend yet)", "warning");
    }

    logToConsole(msg, type = 'info') {
        const output = document.getElementById('console-output');
        if (!output) return;

        const p = document.createElement('p');
        p.className = type === 'error' ? 'text-red-400' : type === 'success' ? 'text-green-400' : type === 'warning' ? 'text-yellow-400' : 'text-teal-400/80';
        p.innerHTML = `<span class="text-white/20 mr-2">${new Date().toLocaleTimeString()}</span> > ${msg}`;
        output.appendChild(p);
        output.scrollTop = output.scrollHeight;
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
        const path = document.getElementById('dispatch-path').value;

        if (!desc) {
            alert("Please enter a description");
            return;
        }

        if (type === 'MODIFICATION' && !path) {
            alert("Project path is required for modification tasks.");
            return;
        }

        try {
            const payload = { description: desc };
            if (path) payload.project_path = path;

            await API.submitTask({
                task_type: type.toLowerCase(),
                module_name: 'manual',
                payload: payload,
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
