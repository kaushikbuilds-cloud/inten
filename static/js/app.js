/**
 * StudyPulse - Student Task Manager Client Application
 * Modern Dark Theme Edition
 */

// Application State
const appState = {
    tasks: [],
    statusFilter: 'all',
    subjectFilter: 'all',
    priorityFilter: 'all',
    searchQuery: '',
    sortBy: 'due_date_asc',
    deletingTaskId: null
};

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('taskListContainer')) {
        initDashboard();
    }
    initFlashAutoDismiss();
});

/**
 * Initialize Dashboard
 */
function initDashboard() {
    renderCurrentDate();

    // Search bar with debounce
    const searchInput = document.getElementById('searchInput');
    const clearSearchBtn = document.getElementById('clearSearchBtn');

    if (searchInput) {
        let debounceTimer;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            const val = e.target.value.trim();
            if (clearSearchBtn) clearSearchBtn.style.display = val ? 'flex' : 'none';
            debounceTimer = setTimeout(() => {
                appState.searchQuery = val;
                loadTasks();
            }, 250);
        });
    }

    if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', () => {
            searchInput.value = '';
            clearSearchBtn.style.display = 'none';
            appState.searchQuery = '';
            loadTasks();
            searchInput.focus();
        });
    }

    // Status pill tabs
    const statusTabs = document.querySelectorAll('.pill-tab');
    statusTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            statusTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            appState.statusFilter = tab.getAttribute('data-status');
            loadTasks();
        });
    });

    // Subject dropdown filter
    const subjectFilter = document.getElementById('subjectFilter');
    if (subjectFilter) {
        subjectFilter.addEventListener('change', (e) => {
            appState.subjectFilter = e.target.value;
            loadTasks();
        });
    }

    // Priority dropdown filter
    const priorityFilter = document.getElementById('priorityFilter');
    if (priorityFilter) {
        priorityFilter.addEventListener('change', (e) => {
            appState.priorityFilter = e.target.value;
            loadTasks();
        });
    }

    // Sort dropdown
    const sortBy = document.getElementById('sortBy');
    if (sortBy) {
        sortBy.addEventListener('change', (e) => {
            appState.sortBy = e.target.value;
            loadTasks();
        });
    }

    // Escape key listener for modals
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeTaskModal();
            closeDeleteModal();
        }
    });

    // Initial fetch
    loadStats();
    loadTasks();

    if (window.location.search.includes('modal=new')) {
        setTimeout(() => openTaskModal(), 350);
    }
}

/**
 * Render Header Date Chip
 */
function renderCurrentDate() {
    const el = document.getElementById('dateText');
    if (!el) return;
    const now = new Date();
    const options = { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' };
    el.textContent = now.toLocaleDateString('en-US', options);
}

/**
 * Fetch and Render Analytics Metrics
 */
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        if (!response.ok) return;

        const data = await response.json();

        // Update Stat Counters
        const elTotal = document.getElementById('statTotal');
        const elPending = document.getElementById('statPending');
        const elCompleted = document.getElementById('statCompleted');
        const elOverdue = document.getElementById('statOverdue');
        const elRate = document.getElementById('statRate');
        const elFill = document.getElementById('progressFill');
        const elStatusText = document.getElementById('progressStatusText');

        if (elTotal) elTotal.textContent = data.total;
        if (elPending) elPending.textContent = data.pending;
        if (elCompleted) elCompleted.textContent = data.completed;
        if (elOverdue) elOverdue.textContent = data.overdue;
        if (elRate) elRate.textContent = `${data.completion_rate}%`;
        if (elFill) elFill.style.width = `${data.completion_rate}%`;

        if (elStatusText) {
            if (data.total === 0) {
                elStatusText.textContent = 'No tasks in workspace yet';
            } else if (data.completed === data.total) {
                elStatusText.textContent = `All ${data.total} tasks completed! Fantastic job 🎉`;
            } else {
                elStatusText.textContent = `${data.completed} of ${data.total} tasks completed (${data.pending} remaining)`;
            }
        }

        // Update Tab Badges
        const tabAll = document.getElementById('countAll');
        const tabPending = document.getElementById('countPending');
        const tabCompleted = document.getElementById('countCompleted');
        const tabOverdue = document.getElementById('countOverdue');

        if (tabAll) tabAll.textContent = data.total;
        if (tabPending) tabPending.textContent = data.pending;
        if (tabCompleted) tabCompleted.textContent = data.completed;
        if (tabOverdue) tabOverdue.textContent = data.overdue;

        // Populate Subject Filter from active tasks
        const subjectSelect = document.getElementById('subjectFilter');
        if (subjectSelect) {
            const currentSelection = subjectSelect.value;
            subjectSelect.innerHTML = '<option value="all">All Subjects</option>';
            if (data.subjects && data.subjects.length > 0) {
                data.subjects.forEach(sub => {
                    const opt = document.createElement('option');
                    opt.value = sub;
                    opt.textContent = sub;
                    if (sub === currentSelection) opt.selected = true;
                    subjectSelect.appendChild(opt);
                });
            }
        }
    } catch (err) {
        console.error('Error loading stats:', err);
    }
}

/**
 * Fetch and Render Tasks
 */
async function loadTasks() {
    const container = document.getElementById('taskListContainer');
    const emptyState = document.getElementById('emptyState');
    const countDisplay = document.getElementById('visibleTasksCount');

    if (!container) return;

    const params = new URLSearchParams({
        status: appState.statusFilter,
        subject: appState.subjectFilter,
        priority: appState.priorityFilter,
        search: appState.searchQuery,
        sort: appState.sortBy
    });

    try {
        const response = await fetch(`/api/tasks?${params.toString()}`);
        if (!response.ok) throw new Error('Failed to fetch tasks');

        const data = await response.json();
        appState.tasks = data.tasks || [];

        const len = appState.tasks.length;
        if (countDisplay) {
            countDisplay.textContent = `${len} task${len !== 1 ? 's' : ''}`;
        }

        if (len === 0) {
            container.innerHTML = '';
            emptyState.style.display = 'flex';
            updateEmptyStateDetails();
        } else {
            emptyState.style.display = 'none';
            renderTaskCards(appState.tasks, container);
        }
    } catch (err) {
        console.error('Failed to load tasks:', err);
        showToast('Unable to load tasks right now.', 'danger');
    }
}

/**
 * Render Dynamic Task Items
 */
function renderTaskCards(tasks, container) {
    container.innerHTML = tasks.map(task => {
        const isCompleted = task.status === 'Completed';
        const isOverdue = task.is_overdue;

        const priorityClass = `chip-priority-${task.priority.toLowerCase()}`;

        let dueClass = 'chip-due';
        if (isOverdue) dueClass = 'chip-due-danger';
        else if (task.due_badge_variant === 'warning') dueClass = 'chip-due-warning';
        else if (task.due_badge_variant === 'info') dueClass = 'chip-due-info';

        return `
            <div class="task-card-item ${isCompleted ? 'is-completed' : ''}" id="task-${task.id}">
                <div class="check-toggle-area">
                    <button 
                        class="task-toggle-btn" 
                        onclick="toggleTaskStatus(${task.id})" 
                        title="${isCompleted ? 'Mark as pending' : 'Mark as completed'}"
                        aria-label="Toggle task status"
                    >
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                    </button>
                </div>

                <div class="task-content-area">
                    <div class="task-heading-row">
                        <span class="task-main-title">${escapeHtml(task.title)}</span>
                    </div>

                    ${task.description ? `<p class="task-notes">${escapeHtml(task.description)}</p>` : ''}

                    <div class="task-chips-row">
                        <span class="chip chip-subject">
                            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                            </svg>
                            ${escapeHtml(task.subject || 'General')}
                        </span>

                        <span class="chip ${priorityClass}">
                            ${task.priority} Priority
                        </span>

                        <span class="chip ${dueClass}">
                            ${isOverdue ? '<span class="pulsing-danger-dot"></span>' : ''}
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="10"></circle>
                                <polyline points="12 6 12 12 14 14"></polyline>
                            </svg>
                            ${escapeHtml(task.due_human)} (${task.due_date})
                        </span>
                    </div>
                </div>

                <div class="task-actions-stack">
                    <button 
                        class="action-icon-btn action-icon-edit" 
                        onclick="editTask(${task.id})" 
                        title="Edit task"
                        aria-label="Edit task"
                    >
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                        </svg>
                    </button>
                    <button 
                        class="action-icon-btn action-icon-delete" 
                        onclick="openDeleteModal(${task.id}, '${escapeJsQuote(task.title)}')" 
                        title="Delete task"
                        aria-label="Delete task"
                    >
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="3 6 5 6 21 6"></polyline>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Toggle Task Status
 */
async function toggleTaskStatus(taskId) {
    try {
        const response = await fetch(`/api/tasks/${taskId}/toggle`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) throw new Error('Failed to toggle status');

        const result = await response.json();
        showToast(result.message || 'Status updated', 'success');

        await loadStats();
        await loadTasks();
    } catch (err) {
        console.error('Toggle error:', err);
        showToast('Failed to update task status.', 'danger');
    }
}

/**
 * Task Modal Handlers
 */
function openTaskModal(task = null) {
    const modal = document.getElementById('taskModal');
    const modalTitle = document.getElementById('taskModalTitle');
    const form = document.getElementById('taskForm');
    const saveBtnText = document.getElementById('saveBtnText');
    const statusGroup = document.getElementById('statusFieldGroup');

    if (!modal || !form) return;

    form.reset();

    if (task) {
        // Edit Mode
        modalTitle.textContent = 'Edit Task';
        saveBtnText.textContent = 'Update Task';
        document.getElementById('taskId').value = task.id;
        document.getElementById('taskTitle').value = task.title;
        document.getElementById('taskSubject').value = task.subject || '';
        document.getElementById('taskPriority').value = task.priority || 'Medium';
        document.getElementById('taskDueDate').value = task.due_date;
        document.getElementById('taskDescription').value = task.description || '';
        document.getElementById('taskStatus').value = task.status;
        statusGroup.style.display = 'block';
    } else {
        // Create Mode
        modalTitle.textContent = 'Add New Task';
        saveBtnText.textContent = 'Create Task';
        document.getElementById('taskId').value = '';
        statusGroup.style.display = 'none';

        // Default to tomorrow
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        const yyyy = tomorrow.getFullYear();
        const mm = String(tomorrow.getMonth() + 1).padStart(2, '0');
        const dd = String(tomorrow.getDate()).padStart(2, '0');
        document.getElementById('taskDueDate').value = `${yyyy}-${mm}-${dd}`;
    }

    modal.style.display = 'flex';
    setTimeout(() => document.getElementById('taskTitle').focus(), 100);
}

function closeTaskModal() {
    const modal = document.getElementById('taskModal');
    if (modal) modal.style.display = 'none';
}

function editTask(taskId) {
    const task = appState.tasks.find(t => t.id === taskId);
    if (task) openTaskModal(task);
}

/**
 * Form Submission Handler
 */
async function handleTaskFormSubmit(e) {
    e.preventDefault();
    const taskId = document.getElementById('taskId').value;
    const title = document.getElementById('taskTitle').value.trim();
    const subject = document.getElementById('taskSubject').value.trim() || 'General';
    const priority = document.getElementById('taskPriority').value;
    const due_date = document.getElementById('taskDueDate').value;
    const description = document.getElementById('taskDescription').value.trim();
    const status = document.getElementById('taskStatus').value;

    if (!title) {
        showToast('Please enter a task title', 'danger');
        return;
    }

    const payload = { title, subject, priority, due_date, description, status };
    const isEdit = Boolean(taskId);
    const url = isEdit ? `/api/tasks/${taskId}` : '/api/tasks';
    const method = isEdit ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            showToast(data.error || 'Failed to save task', 'danger');
            return;
        }

        showToast(data.message || (isEdit ? 'Task updated!' : 'Task created!'), 'success');
        closeTaskModal();
        await loadStats();
        await loadTasks();
    } catch (err) {
        console.error('Save task error:', err);
        showToast('Error saving task', 'danger');
    }
}

/**
 * Delete Modal Handlers
 */
function openDeleteModal(taskId, taskTitle) {
    appState.deletingTaskId = taskId;
    const modal = document.getElementById('deleteModal');
    const titleDisplay = document.getElementById('deleteTaskTitle');
    if (titleDisplay) titleDisplay.textContent = `"${taskTitle}"`;
    if (modal) modal.style.display = 'flex';
}

function closeDeleteModal() {
    appState.deletingTaskId = null;
    const modal = document.getElementById('deleteModal');
    if (modal) modal.style.display = 'none';
}

async function confirmTaskDeletion() {
    if (!appState.deletingTaskId) return;

    try {
        const response = await fetch(`/api/tasks/${appState.deletingTaskId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (!response.ok) {
            showToast(data.error || 'Failed to delete task', 'danger');
            return;
        }

        showToast(data.message || 'Task deleted permanently', 'info');
        closeDeleteModal();
        await loadStats();
        await loadTasks();
    } catch (err) {
        console.error('Delete task error:', err);
        showToast('Error deleting task', 'danger');
    }
}

/**
 * Modern Toast Notifications
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast-pill toast-${type}`;

    let icon = 'ℹ️';
    if (type === 'success') icon = '✓';
    if (type === 'danger') icon = '✕';

    toast.innerHTML = `
        <span>${icon}</span>
        <span>${escapeHtml(message)}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3200);
}

/**
 * Auto-dismiss flash messages
 */
function initFlashAutoDismiss() {
    const toasts = document.querySelectorAll('.flash-toast');
    toasts.forEach(toast => {
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 350);
        }, 4000);
    });
}

/**
 * Dynamic Context-Aware Empty State
 */
function updateEmptyStateDetails() {
    const title = document.getElementById('emptyTitle');
    const text = document.getElementById('emptyText');
    if (!title || !text) return;

    if (appState.searchQuery) {
        title.textContent = 'No matching tasks found';
        text.textContent = `No assignments or notes match "${appState.searchQuery}". Try a different keyword or reset filters.`;
    } else if (appState.statusFilter === 'Completed') {
        title.textContent = 'No completed tasks yet';
        text.textContent = 'Check off tasks as you finish them to build momentum!';
    } else if (appState.statusFilter === 'Overdue') {
        title.textContent = 'Zero overdue tasks 🎉';
        text.textContent = 'Excellent! You have no overdue assignments or missed deadlines.';
    } else if (appState.statusFilter === 'Pending') {
        title.textContent = 'All caught up!';
        text.textContent = 'You have zero pending tasks. Take a well-earned break or plan ahead.';
    } else {
        title.textContent = 'Your study workspace is clear';
        text.textContent = 'No tasks scheduled yet. Create your first assignment or exam goal to start tracking progress.';
    }
}

/**
 * Escapers
 */
function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function escapeJsQuote(str) {
    if (!str) return '';
    return String(str).replace(/'/g, "\\'").replace(/"/g, '&quot;');
}
