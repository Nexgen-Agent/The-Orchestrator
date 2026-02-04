/**
 * API communication layer for FOG Dashboard
 */
const API = {
    baseUrl: '',

    async get(endpoint) {
        const response = await fetch(`${this.baseUrl}${endpoint}`);
        if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
        return response.json();
    },

    async post(endpoint, data = {}) {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
        return response.json();
    },

    // Core System
    getSystemState() { return this.get('/system-state'); },

    // Human Control Agent
    getPendingApprovals() { return this.get('/human-control/approvals/pending'); },
    approveRequest(id) { return this.post(`/human-control/approvals/${id}/approve`); },
    rejectRequest(id) { return this.post(`/human-control/approvals/${id}/reject`); },
    pauseOrchestration() { return this.post('/human-control/pause'); },
    resumeOrchestration() { return this.post('/human-control/resume'); },
    emergencyStop() { return this.post('/human-control/emergency-stop'); },

    // Agent Management
    getAgentToggles() { return this.get('/human-control/agent-toggles'); },
    toggleAgent(name, enabled) { return this.post(`/human-control/toggle-agent?agent_name=${name}&enabled=${enabled}`); },

    // Tasks
    submitTask(task) { return this.post('/submit-task', task); },
    getTaskStatus(id) { return this.get(`/task-status/${id}`); },

    // Builder & Debugger
    runBuild(projectPath) { return this.post('/builder/build', { project_path: projectPath }); },
    runDebug(projectPath) { return this.post('/debugger/run', { project_path: projectPath }); },

    // Resilience
    runResilienceCheck() { return this.post('/resilience/analyze-and-fix'); }
};
