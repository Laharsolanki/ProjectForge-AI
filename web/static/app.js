/**
 * ProjectForge AI — Client-Side Application Logic
 *
 * Handles WebSocket connection, message rendering,
 * Markdown parsing, and UI interactions.
 */

// ─── State ──────────────────────────────────────────────────────────────────
let ws = null;
let sessionId = null;
let isConnected = false;
let isStreaming = false;
let currentStreamDiv = null;
let streamBuffer = "";

// ─── DOM Elements ───────────────────────────────────────────────────────────
const messagesContainer = document.getElementById("messagesContainer");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const sessionBadge = document.getElementById("sessionBadge");
const newSessionBtn = document.getElementById("newSessionBtn");
const reportsBtn = document.getElementById("reportsBtn");
const reportsModal = document.getElementById("reportsModal");
const closeReportsModal = document.getElementById("closeReportsModal");
const reportsModalBody = document.getElementById("reportsModalBody");
const menuToggle = document.getElementById("menuToggle");
const sidebar = document.getElementById("sidebar");

// ─── Initialize ─────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    initSession();
    setupEventListeners();
    initMermaid();
});

function initMermaid() {
    mermaid.initialize({
        startOnLoad: false,
        theme: "dark",
        themeVariables: {
            primaryColor: "#6366f1",
            primaryTextColor: "#f1f5f9",
            primaryBorderColor: "#4f46e5",
            lineColor: "#64748b",
            secondaryColor: "#1a2035",
            tertiaryColor: "#111827",
        },
    });
}

// ─── Session Management ─────────────────────────────────────────────────────
async function initSession() {
    try {
        const res = await fetch("/api/session", { method: "POST" });
        const data = await res.json();
        sessionId = data.session_id;
        sessionBadge.textContent = `Session: ${sessionId.slice(0, 8)}...`;
        connectWebSocket();
        updateStageTracker("discovery");
    } catch (err) {
        sessionBadge.textContent = "Session: failed to create";
        console.error("Failed to create session:", err);
    }
}

function connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    ws = new WebSocket(`${protocol}//${window.location.host}/ws/${sessionId}`);

    ws.onopen = () => {
        isConnected = true;
        sessionBadge.textContent = `Session: ${sessionId.slice(0, 8)}... ● connected`;
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleAgentMessage(data);
    };

    ws.onclose = () => {
        isConnected = false;
        sessionBadge.textContent = `Session: disconnected`;
        // Attempt reconnect after 3 seconds
        setTimeout(() => {
            if (!isConnected && sessionId) {
                connectWebSocket();
            }
        }, 3000);
    };

    ws.onerror = (err) => {
        console.error("WebSocket error:", err);
    };
}

// ─── Message Handling ───────────────────────────────────────────────────────
function handleAgentMessage(data) {
    switch (data.type) {
        case "chunk":
            if (!isStreaming) {
                // Start new agent message
                isStreaming = true;
                streamBuffer = "";
                currentStreamDiv = addAgentMessage("", data.agent);
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
            removeTypingIndicator();
            sendBtn.disabled = false;
            messageInput.disabled = false;
            messageInput.focus();
            currentStreamDiv = null;
            streamBuffer = "";
            scrollToBottom();
            if (data.current_stage) {
                updateStageTracker(data.current_stage);
            }
            break;

        case "error":
            isStreaming = false;
            removeTypingIndicator();
            addSystemMessage(`⚠️ ${data.message}`, "error");
            sendBtn.disabled = false;
            messageInput.disabled = false;
            currentStreamDiv = null;
            streamBuffer = "";
            break;
    }
}

function sendMessage() {
    const text = messageInput.value.trim();
    if (!text || !isConnected || isStreaming) return;

    // Add user message to chat
    addUserMessage(text);

    // Send via WebSocket
    ws.send(JSON.stringify({ text }));

    // Clear input and show typing
    messageInput.value = "";
    messageInput.style.height = "auto";
    sendBtn.disabled = true;
    messageInput.disabled = true;
    addTypingIndicator();
    scrollToBottom();
}

// ─── Message Rendering ─────────────────────────────────────────────────────
function addUserMessage(text) {
    const div = document.createElement("div");
    div.className = "message user-message";
    div.innerHTML = `
        <div class="message-avatar">You</div>
        <div class="message-content">
            <div class="message-header">
                <span class="user-name">You</span>
            </div>
            <div class="message-body">${escapeHtml(text)}</div>
        </div>
    `;
    messagesContainer.appendChild(div);
    return div;
}

function addAgentMessage(content, agentName = "ProjectForge AI") {
    const div = document.createElement("div");
    div.className = "message agent-message";

    // Map agent names to display names
    const displayNames = {
        projectforge_orchestrator: "ProjectForge AI",
        discovery_agent: "🔍 Discovery Agent",
        tech_design_agent: "🏗️ Technical Design Agent",
        risk_analysis_agent: "⚠️ Risk Analysis Agent",
        report_generator_agent: "📋 Report Generator",
    };

    const name = displayNames[agentName] || agentName;

    div.innerHTML = `
        <div class="message-avatar">🏗️</div>
        <div class="message-content">
            <div class="message-header">
                <span class="agent-name">${name}</span>
            </div>
            <div class="message-body"></div>
        </div>
    `;
    messagesContainer.appendChild(div);

    const bodyDiv = div.querySelector(".message-body");
    if (content) {
        renderMarkdown(bodyDiv, content);
    }
    return bodyDiv;
}

function addSystemMessage(text, type = "info") {
    const div = document.createElement("div");
    div.className = "message agent-message";
    div.innerHTML = `
        <div class="message-avatar">⚡</div>
        <div class="message-content">
            <div class="message-body" style="border-color: var(--accent-${type === "error" ? "error" : "warning"});">
                ${text}
            </div>
        </div>
    `;
    messagesContainer.appendChild(div);
}

function addTypingIndicator() {
    const existing = document.getElementById("typingIndicator");
    if (existing) return;

    const div = document.createElement("div");
    div.id = "typingIndicator";
    div.className = "message agent-message";
    div.innerHTML = `
        <div class="message-avatar">🏗️</div>
        <div class="message-content">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    messagesContainer.appendChild(div);
}

function removeTypingIndicator() {
    const indicator = document.getElementById("typingIndicator");
    if (indicator) indicator.remove();
}

// ─── Markdown Rendering ─────────────────────────────────────────────────────
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
    codeBlocks.forEach((block, index) => {
        const pre = block.parentElement;
        const mermaidDiv = document.createElement("div");
        mermaidDiv.className = "mermaid";
        mermaidDiv.textContent = block.textContent;

        pre.replaceWith(mermaidDiv);

        try {
            mermaid.run({ nodes: [mermaidDiv] });
        } catch (err) {
            console.warn("Mermaid rendering failed:", err);
        }
    });
}

// ─── Utilities ──────────────────────────────────────────────────────────────
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

// ─── Event Listeners ────────────────────────────────────────────────────────
function setupEventListeners() {
    // Send button
    sendBtn.addEventListener("click", sendMessage);

    // Enter to send, Shift+Enter for new line
    messageInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Auto-resize textarea
    messageInput.addEventListener("input", () => {
        messageInput.style.height = "auto";
        messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + "px";
    });

    // New session
    newSessionBtn.addEventListener("click", async () => {
        messagesContainer.innerHTML = "";
        await initSession();

        // Re-add welcome message
        const welcomeHtml = `
            <div class="message agent-message welcome-message">
                <div class="message-avatar">🏗️</div>
                <div class="message-content">
                    <div class="message-header">
                        <span class="agent-name">ProjectForge AI</span>
                    </div>
                    <div class="message-body">
                        <h3>New session started! 👋</h3>
                        <p>Tell me about your next project idea.</p>
                    </div>
                </div>
            </div>
        `;
        messagesContainer.innerHTML = welcomeHtml;
    });

    // Reports modal
    reportsBtn.addEventListener("click", openReportsModal);
    closeReportsModal.addEventListener("click", () => {
        reportsModal.classList.remove("visible");
    });
    reportsModal.addEventListener("click", (e) => {
        if (e.target === reportsModal) {
            reportsModal.classList.remove("visible");
        }
    });

    // Mobile menu toggle
    menuToggle.addEventListener("click", () => {
        sidebar.classList.toggle("open");
    });
}

// ─── Reports Modal ──────────────────────────────────────────────────────────
async function openReportsModal() {
    reportsModal.classList.add("visible");
    reportsModalBody.innerHTML = '<p class="loading">Loading reports...</p>';

    try {
        const res = await fetch("/api/reports");
        const data = await res.json();

        if (data.reports.length === 0) {
            reportsModalBody.innerHTML = '<p class="empty-state">No reports generated yet. Complete a project analysis to generate a report.</p>';
            return;
        }

        let html = "";
        for (const report of data.reports) {
            html += `
                <div class="report-item">
                    <span class="report-name">📄 ${report.filename}</span>
                    <a href="/api/reports/${report.filename}" download class="report-download">Download</a>
                </div>
            `;
        }
        reportsModalBody.innerHTML = html;
    } catch (err) {
        reportsModalBody.innerHTML = '<p class="empty-state">Failed to load reports.</p>';
    }
}

// ─── Stage Tracker Helper ──────────────────────────────────────────────────
function updateStageTracker(currentStage) {
    if (!currentStage) return;

    const stages = ["discovery", "tech_design", "report_generation"];
    const currentIdx = stages.indexOf(currentStage);

    stages.forEach((stage, idx) => {
        const stageDiv = document.querySelector(`.stage[data-stage="${stage}"]`);
        if (!stageDiv) return;

        const dot = stageDiv.querySelector(".stage-dot");
        if (!dot) return;

        // Reset classes
        dot.className = "stage-dot";
        stageDiv.classList.remove("active", "completed");

        if (idx < currentIdx) {
            dot.classList.add("completed");
            stageDiv.classList.add("completed");
        } else if (idx === currentIdx) {
            dot.classList.add("active");
            stageDiv.classList.add("active");
        } else {
            dot.classList.add("pending");
        }
    });
}
