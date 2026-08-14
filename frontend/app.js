/**
 * ProjectForge AI — Client-Side Application Logic (Blueprint Theme)
 *
 * Handles Session/User Authentication, WebSockets, Stage Stepper,
 * SVG Telemetry Mapping, Terminal Logging, and Markdown/Mermaid parsing.
 */

// ─── State Variables ────────────────────────────────────────────────────────
let ws = null;
let sessionId = null;
let username = null;
let isConnected = false;
let isStreaming = false;
let currentStreamDiv = null;
let streamBuffer = "";
let activeWorkingAgent = null;

// ─── DOM Elements ───────────────────────────────────────────────────────────
// Screens
const authScreen = document.getElementById("authScreen");
const dashboardScreen = document.getElementById("dashboardScreen");

// Forms & Auth
const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");
const showRegister = document.getElementById("showRegister");
const showLogin = document.getElementById("showLogin");
const loginStatus = document.getElementById("loginStatus");
const regStatus = document.getElementById("regStatus");
const loginUser = document.getElementById("loginUser");
const loginPass = document.getElementById("loginPass");
const regUser = document.getElementById("regUser");
const regPass = document.getElementById("regPass");
const headerUser = document.getElementById("headerUser");
const logoutBtn = document.getElementById("logoutBtn");

// Core Dashboard
const messagesContainer = document.getElementById("messagesContainer");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const sessionBadge = document.getElementById("sessionBadge");
const newSessionBtn = document.getElementById("newSessionBtn");
const refreshReportsBtn = document.getElementById("refreshReportsBtn");

// Stepper & Progress Card
const pipelineStepper = document.getElementById("pipelineStepper");
const progressVal = document.getElementById("progressVal");
const progressBar = document.getElementById("progressBar");
const stageState = document.getElementById("stageState");

// Parameters Widgets
const tempSlider = document.getElementById("tempSlider");
const tempVal = document.getElementById("tempVal");
const riskToggle = document.getElementById("riskToggle");
const learningToggle = document.getElementById("learningToggle");

// Reports Modal & List
const reportsListBody = document.getElementById("reportsListBody");
const reportsModal = document.getElementById("reportsModal");
const closeReportsModal = document.getElementById("closeReportsModal");
const closeReportsModalBtn = document.getElementById("closeReportsModalBtn");
const reportsModalBody = document.getElementById("reportsModalBody");
const viewingReportName = document.getElementById("viewingReportName");
const downloadReportLink = document.getElementById("downloadReportLink");

// ─── Page Initialization ─────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    checkAuthentication();
    setupAuthEventListeners();
    setupDashboardEventListeners();
    initMermaid();
});

function initMermaid() {
    mermaid.initialize({
        startOnLoad: false,
        theme: "dark",
        themeVariables: {
            primaryColor: "#00f0ff",
            primaryTextColor: "#cce3e8",
            primaryBorderColor: "#4c8b99",
            lineColor: "#4c8b99",
            secondaryColor: "#0a1c24",
            tertiaryColor: "#050f14",
        },
    });
}

// ─── Authentication state check ──────────────────────────────────────────────
function checkAuthentication() {
    username = localStorage.getItem("pf_username");
    if (username) {
        // Authenticated - Transition to Dashboard
        headerUser.textContent = username.toUpperCase();
        authScreen.classList.add("hidden");
        dashboardScreen.classList.remove("hidden");
        initSession();
    } else {
        // Not Authenticated - Show Login Gateway
        authScreen.classList.remove("hidden");
        dashboardScreen.classList.add("hidden");
    }
}

// ─── Auth Form Events ────────────────────────────────────────────────────────
function setupAuthEventListeners() {
    showRegister.addEventListener("click", (e) => {
        e.preventDefault();
        loginForm.classList.remove("active");
        registerForm.classList.add("active");
        regStatus.textContent = "PENDING INITIALIZATION...";
        regStatus.className = "auth-status";
    });

    showLogin.addEventListener("click", (e) => {
        e.preventDefault();
        registerForm.classList.remove("active");
        loginForm.classList.add("active");
        loginStatus.textContent = "READY FOR CREDENTIALS...";
        loginStatus.className = "auth-status";
    });

    // Login Submission
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const user = loginUser.value.trim();
        const pass = loginPass.value.trim();
        
        loginStatus.textContent = "DECRYPTING IDENTITY CHANNEL...";
        loginStatus.className = "auth-status";

        try {
            const res = await fetch("/api/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username: user, password: pass })
            });
            const data = await res.json();
            
            if (res.ok) {
                loginStatus.textContent = "ACCESS GRANTED. SYNCING...";
                loginStatus.className = "auth-status success";
                localStorage.setItem("pf_username", data.username);
                setTimeout(() => {
                    loginUser.value = "";
                    loginPass.value = "";
                    checkAuthentication();
                }, 1000);
            } else {
                loginStatus.textContent = `DECRYPTION ERROR: ${data.error || "ACCESS DENIED"}`;
                loginStatus.className = "auth-status error";
            }
        } catch (err) {
            loginStatus.textContent = "CONNECTION TIMEOUT. GATEWAY DOWN.";
            loginStatus.className = "auth-status error";
        }
    });

    // Registration Submission
    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const user = regUser.value.trim();
        const pass = regPass.value.trim();

        regStatus.textContent = "INITIALIZING OPERATOR PROTOCOL...";
        regStatus.className = "auth-status";

        try {
            const res = await fetch("/api/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username: user, password: pass })
            });
            const data = await res.json();

            if (res.ok) {
                regStatus.textContent = "OPERATOR REGISTERED. GATEWAY ENABLED.";
                regStatus.className = "auth-status success";
                setTimeout(() => {
                    regUser.value = "";
                    regPass.value = "";
                    // Auto switch to login
                    registerForm.classList.remove("active");
                    loginForm.classList.add("active");
                    loginUser.value = user;
                    loginStatus.textContent = "OPERATOR CONSOLE READY. PLEASE ENTER PASSKEY.";
                    loginStatus.className = "auth-status success";
                }, 1500);
            } else {
                regStatus.textContent = `INITIALIZATION FAILED: ${data.error}`;
                regStatus.className = "auth-status error";
            }
        } catch (err) {
            regStatus.textContent = "CONNECTION TIMEOUT. REGISTRATION OFFLINE.";
            regStatus.className = "auth-status error";
        }
    });

    // Disconnect Action
    logoutBtn.addEventListener("click", () => {
        if (ws) ws.close();
        localStorage.removeItem("pf_username");
        checkAuthentication();
    });
}

// ─── Dashboard Orchestration Events ──────────────────────────────────────────
function setupDashboardEventListeners() {
    // Send message triggers
    sendBtn.addEventListener("click", sendMessage);
    messageInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Handle parameter slider change
    tempSlider.addEventListener("input", () => {
        tempVal.textContent = tempSlider.value;
    });

    // Initialize new project session
    newSessionBtn.addEventListener("click", async () => {
        messagesContainer.innerHTML = "";
        resetTelemetryUI();
        await initSession();

        // Re-inject blueprint system ready message
        const readyHtml = `
            <div class="message agent-message welcome-msg">
                <div class="msg-header">
                    <span class="sender-tag">[SYSTEM_ORCHESTRATOR]</span>
                    <span class="time-tag">SEC_01 // RESET</span>
                </div>
                <div class="msg-body">
                    <h3>NEW SESSION INITIALIZED.</h3>
                    <p>Describe your next project idea, learning preferences, and framework constraints to kick off a new roadmap analysis.</p>
                </div>
            </div>
        `;
        messagesContainer.innerHTML = readyHtml;
    });

    // Manual re-scan of files
    refreshReportsBtn.addEventListener("click", loadReports);

    // Auto-expand prompt textarea
    messageInput.addEventListener("input", () => {
        messageInput.style.height = "auto";
        messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + "px";
    });

    // Modal Close Triggers
    const closeAllModals = () => {
        reportsModal.classList.remove("visible");
    };
    closeReportsModal.addEventListener("click", closeAllModals);
    closeReportsModalBtn.addEventListener("click", closeAllModals);
    reportsModal.addEventListener("click", (e) => {
        if (e.target === reportsModal) closeAllModals();
    });
}

// ─── Session Setup ───────────────────────────────────────────────────────────
async function initSession() {
    sessionBadge.textContent = "connecting...";
    sessionBadge.className = "session-id muted-text";

    try {
        const res = await fetch("/api/session", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: username })
        });
        const data = await res.json();
        sessionId = data.session_id;
        sessionBadge.textContent = `SYS_ID: ${sessionId.slice(0, 8).toUpperCase()}`;
        sessionBadge.className = "session-id text-glow";
        
        connectWebSocket();
        updateStageProgress("discovery");
        loadReports();
    } catch (err) {
        sessionBadge.textContent = "SYS_ID: ERROR INITIALIZING";
        sessionBadge.className = "session-id error-text";
        console.error("Failed to initialize session:", err);
    }
}

// ─── WebSockets Communication ────────────────────────────────────────────────
function connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws/${sessionId}?user_id=${username}`;
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        isConnected = true;
        sessionBadge.textContent = `SYS_ID: ${sessionId.slice(0, 8).toUpperCase()} // ONLINE`;
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleAgentSocketMessage(data);
    };

    ws.onclose = () => {
        isConnected = false;
        sessionBadge.textContent = `SYS_ID: ${sessionId.slice(0, 8).toUpperCase()} // DISCONNECTED`;
        resetTelemetryUI();
        
        // Reconnect loop
        setTimeout(() => {
            if (!isConnected && username) {
                connectWebSocket();
            }
        }, 3000);
    };

    ws.onerror = (err) => {
        console.error("WebSocket socket error:", err);
    };
}

// ─── Socket Message Routing ──────────────────────────────────────────────────
function handleAgentSocketMessage(data) {
    switch (data.type) {
        case "agent_status":
            // Highlight active agent node in the connection diagram
            updateAgentTelemetryNode(data.agent, "working");
            addTypingIndicator(data.label || data.agent);
            break;

        case "chunk":
            removeTypingIndicator();
            // Once streaming starts, transition nodes
            if (activeWorkingAgent) {
                updateAgentTelemetryNode(activeWorkingAgent, "active");
            }
            if (!isStreaming) {
                isStreaming = true;
                streamBuffer = "";
                currentStreamDiv = createAgentMessageContainer(data.agent);
            }
            streamBuffer += data.text;
            renderMarkdown(currentStreamDiv, streamBuffer);
            scrollToBottom();
            break;

        case "done":
            isStreaming = false;
            if (currentStreamDiv && data.full_text) {
                renderMarkdown(currentStreamDiv, data.full_text);
                renderMermaidDiagrams(currentStreamDiv);
            }
            
            // Clean up telemetry states
            if (activeWorkingAgent) {
                updateAgentTelemetryNode(activeWorkingAgent, "active");
            }
            resetNodeWorkingStates();
            removeTypingIndicator();

            // Unlock prompt input
            sendBtn.disabled = false;
            messageInput.disabled = false;
            messageInput.focus();

            currentStreamDiv = null;
            streamBuffer = "";
            scrollToBottom();

            // Update Progress bar & Stage list
            if (data.current_stage) {
                updateStageProgress(data.current_stage);
            }
            loadReports();
            break;

        case "error":
            isStreaming = false;
            resetNodeWorkingStates();
            removeTypingIndicator();
            
            addSystemErrorMessage(`CRITICAL CONSOLE EXCEPTION: ${data.message}`);
            sendBtn.disabled = false;
            messageInput.disabled = false;
            currentStreamDiv = null;
            streamBuffer = "";
            break;
    }
}

// ─── SVG Telemetry Map Control ───────────────────────────────────────────────
function updateAgentTelemetryNode(agentName, state) {
    // Map backend agent strings to SVG node element IDs
    const agentMap = {
        "projectforge_orchestrator": "node-orchestrator",
        "discovery_agent": "node-discovery",
        "tech_design_agent": "node-tech",
        "risk_analysis_agent": "node-risk",
        "learning_path_agent": "node-learn",
        "report_generator_agent": "node-report"
    };

    const nodeId = agentMap[agentName];
    if (!nodeId) return;

    if (state === "working") {
        activeWorkingAgent = agentName;
        // Make previous nodes inactive working, set current node to working pulsing
        document.querySelectorAll(".agent-node").forEach(node => {
            node.classList.remove("working");
        });
        document.querySelectorAll(".conn-line").forEach(line => {
            line.classList.remove("working");
        });

        const nodeEl = document.getElementById(nodeId);
        if (nodeEl) {
            nodeEl.classList.add("active", "working");
        }

        // Pulse the line between orchestrator and node
        const lineId = `line-${nodeId.split("-")[1]}`;
        const lineEl = document.getElementById(lineId);
        if (lineEl) {
            lineEl.classList.add("working");
        }
    } else if (state === "active") {
        const nodeEl = document.getElementById(nodeId);
        if (nodeEl) {
            nodeEl.classList.add("active");
            nodeEl.classList.remove("working");
        }
        const lineId = `line-${nodeId.split("-")[1]}`;
        const lineEl = document.getElementById(lineId);
        if (lineEl) {
            lineEl.classList.remove("working");
        }
    }
}

function resetNodeWorkingStates() {
    document.querySelectorAll(".agent-node").forEach(node => {
        node.classList.remove("working");
    });
    document.querySelectorAll(".conn-line").forEach(line => {
        line.classList.remove("working");
    });
    activeWorkingAgent = null;
}

function resetTelemetryUI() {
    document.querySelectorAll(".agent-node").forEach(node => {
        node.classList.remove("active", "working");
    });
    document.querySelectorAll(".conn-line").forEach(line => {
        line.classList.remove("working");
    });
    
    // Default orchestrator active
    const orchestratorNode = document.getElementById("node-orchestrator");
    if (orchestratorNode) orchestratorNode.classList.add("active");
    
    activeWorkingAgent = null;
}

// ─── Input Transmit ──────────────────────────────────────────────────────────
function sendMessage() {
    const text = messageInput.value.trim();
    if (!text || !isConnected || isStreaming) return;

    // Render client message
    createUserMessageContainer(text);

    // Send payload
    ws.send(JSON.stringify({ text }));

    // Lock inputs & show thinking state
    messageInput.value = "";
    messageInput.style.height = "auto";
    sendBtn.disabled = true;
    messageInput.disabled = true;
    
    // Highlight Orchestrator node during transmission
    updateAgentTelemetryNode("projectforge_orchestrator", "working");
    addTypingIndicator("INITIALIZING SHELL PARSING...");
    scrollToBottom();
}

// ─── Message Render Blocks ───────────────────────────────────────────────────
function createUserMessageContainer(text) {
    const div = document.createElement("div");
    div.className = "message user-message";
    div.innerHTML = `
        <div class="msg-header">
            <span class="sender-tag">[OPERATOR_TRANSMISSION]</span>
            <span class="time-tag">SEC_02 // UPLOADED</span>
        </div>
        <div class="msg-body">${escapeHtml(text)}</div>
    `;
    messagesContainer.appendChild(div);
    return div;
}

function createAgentMessageContainer(agentName) {
    const div = document.createElement("div");
    div.className = "message agent-message";

    const displayNames = {
        projectforge_orchestrator: "[SYSTEM_ORCHESTRATOR]",
        discovery_agent: "[DISCOVERY_AGENT]",
        tech_design_agent: "[TECH_DESIGN_AGENT]",
        risk_analysis_agent: "[RISK_ANALYSIS_AGENT]",
        report_generator_agent: "[REPORT_GENERATOR]"
    };

    const senderTag = displayNames[agentName] || `[${agentName.toUpperCase()}]`;

    div.innerHTML = `
        <div class="msg-header">
            <span class="sender-tag">${senderTag}</span>
            <span class="time-tag">SEC_03 // COMPUTING</span>
        </div>
        <div class="msg-body"></div>
    `;
    messagesContainer.appendChild(div);
    return div.querySelector(".msg-body");
}

function addSystemErrorMessage(text) {
    const div = document.createElement("div");
    div.className = "message agent-message";
    div.innerHTML = `
        <div class="msg-header">
            <span class="sender-tag error-text">[CONSOLE_EXCEPTION]</span>
            <span class="time-tag">SEC_04 // TIMEOUT</span>
        </div>
        <div class="msg-body error-text" style="border: 1px dashed rgba(255, 74, 74, 0.4); padding: 10px; background: rgba(255, 74, 74, 0.05);">
            ${text}
        </div>
    `;
    messagesContainer.appendChild(div);
    scrollToBottom();
}

function addTypingIndicator(agentLabel) {
    const existing = document.getElementById("typingIndicator");
    if (existing) {
        document.getElementById("typingLabel").textContent = agentLabel;
        return;
    }

    const div = document.createElement("div");
    div.id = "typingIndicator";
    div.className = "message agent-message";
    div.innerHTML = `
        <div class="msg-header">
            <span class="sender-tag">[TRANSMISSION_POLLING]</span>
            <span class="time-tag">SEC_00 // BUFFERING</span>
        </div>
        <div class="msg-body">
            <div class="typing-indicator">
                <span class="typing-label" id="typingLabel">${escapeHtml(agentLabel)}</span>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    messagesContainer.appendChild(div);
    scrollToBottom();
}

function removeTypingIndicator() {
    const indicator = document.getElementById("typingIndicator");
    if (indicator) indicator.remove();
}

// ─── Stage & Progress Controls ───────────────────────────────────────────────
function updateStageProgress(currentStage) {
    if (!currentStage) return;

    const stages = ["discovery", "tech_design", "risk_analysis", "report_generation"];
    const stageIdx = stages.indexOf(currentStage);

    // Progress Bar calculations
    const percentages = {
        "discovery": 25,
        "tech_design": 50,
        "risk_analysis": 75,
        "report_generation": 100
    };
    const percentage = percentages[currentStage] || 0;
    progressVal.textContent = `${percentage}%`;
    progressBar.style.width = `${percentage}%`;

    const stateLabels = {
        "discovery": "DISCOVERY STAGE IN-PROGRESS",
        "tech_design": "TECH ARCHITECTURE FORMULATION",
        "risk_analysis": "RELIABILITY & RISK MITIGATION",
        "report_generation": "ROADMAP SCHEMATIC COMPLETE"
    };
    stageState.textContent = stateLabels[currentStage] || "ORCHESTRATING";

    // Stepper updates
    stages.forEach((stage, idx) => {
        const stepEl = document.querySelector(`.step[data-stage="${stage}"]`);
        if (!stepEl) return;

        const chip = stepEl.querySelector(".status-chip");
        
        stepEl.className = "step";
        if (idx < stageIdx) {
            stepEl.classList.add("completed");
            if (chip) chip.textContent = "[COMPLETE]";
        } else if (idx === stageIdx) {
            stepEl.classList.add("active");
            if (chip) chip.textContent = "[ACTIVE]";
        } else {
            if (chip) chip.textContent = "[PENDING]";
        }
    });

    // SVG node highlighting updates
    for (let i = 0; i <= stageIdx; i++) {
        // Highlight active connections in SVG maps
        const stageNodeName = stages[i] === "report_generation" ? "report_generator_agent" : 
                             stages[i] === "risk_analysis" ? "risk_analysis_agent" : 
                             stages[i] === "tech_design" ? "tech_design_agent" : "discovery_agent";
        updateAgentTelemetryNode(stageNodeName, "active");
    }
}

// ─── Markdown Parsing ────────────────────────────────────────────────────────
function renderMarkdown(element, text) {
    if (!element) return;

    marked.setOptions({
        highlight: function (code, lang) {
            if (lang && hljs.getLanguage(lang)) {
                return hljs.highlight(code, { language: lang }).value;
            }
            return hljs.highlightAuto(code).value;
        },
        breaks: true,
        gfm: true,
    });

    element.innerHTML = marked.parse(text);
}

function renderMermaidDiagrams(container) {
    if (!container) return;

    const codeBlocks = container.querySelectorAll("pre code.language-mermaid");
    codeBlocks.forEach((block) => {
        const pre = block.parentElement;
        const mermaidDiv = document.createElement("div");
        mermaidDiv.className = "mermaid";
        mermaidDiv.textContent = block.textContent;

        pre.replaceWith(mermaidDiv);

        try {
            mermaid.run({ nodes: [mermaidDiv] });
        } catch (err) {
            console.warn("Mermaid rendering exception caught:", err);
        }
    });
}

// ─── Reports list explorer loader ────────────────────────────────────────────
async function loadReports() {
    reportsListBody.innerHTML = '<div class="list-empty">LOADING SCHEMATICS...</div>';

    try {
        const res = await fetch("/api/reports");
        const data = await res.json();

        if (!data.reports || data.reports.length === 0) {
            reportsListBody.innerHTML = '<div class="list-empty">NO SCHEMATICS FOUND. RUN PIPELINE.</div>';
            return;
        }

        let html = "";
        for (const report of data.reports) {
            html += `
                <div class="report-item" data-filename="${report.filename}">
                    <span class="report-name">📄 ${report.filename}</span>
                    <button class="btn btn-secondary btn-sm report-download-btn" data-filename="${report.filename}">VIEW</button>
                </div>
            `;
        }
        reportsListBody.innerHTML = html;

        // Add event listeners to buttons
        reportsListBody.querySelectorAll(".report-item").forEach(item => {
            item.addEventListener("click", (e) => {
                const filename = item.getAttribute("data-filename");
                openReportViewerModal(filename);
            });
        });
    } catch (err) {
        reportsListBody.innerHTML = '<div class="list-empty error-text">RE-SCAN SCHEMATICS FAILED.</div>';
    }
}

// ─── Modal schematic report viewer ──────────────────────────────────────────
async function openReportViewerModal(filename) {
    reportsModal.classList.add("visible");
    reportsModalBody.innerHTML = '<p class="text-glow">DECRYPTING SCHEMATIC DOCUMENT CHARACTERS...</p>';
    viewingReportName.textContent = filename.toUpperCase();
    downloadReportLink.href = `/api/reports/${filename}`;

    try {
        const res = await fetch(`/api/reports/${filename}`);
        if (!res.ok) throw new Error("Document unreadable");
        
        const markdown = await res.text();
        renderMarkdown(reportsModalBody, markdown);
        renderMermaidDiagrams(reportsModalBody);
    } catch (err) {
        reportsModalBody.innerHTML = '<p class="error-text">EXCEPTION CAUGHT: FAILED TO PARSE ARCHIVE SCHEMATIC DATA.</p>';
    }
}

// ─── Helper utilities ────────────────────────────────────────────────────────
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function scrollToBottom() {
    requestAnimationFrame(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    });
}
