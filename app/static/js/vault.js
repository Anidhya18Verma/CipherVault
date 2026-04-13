// ── vault.js ─ Dashboard note management ─────────────────────────────────────
 
let allNotes = [];
let showingFavorites = false;
 
async function apiRequest(url, options = {}) {
    const token = localStorage.getItem('cv_token');
    if (!token) { window.location.href = '/login'; return; }
    const res = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token,
            ...(options.headers || {})
        }
    });
    if (res.status === 401) { logout(); return; }
    return res;
}
 
async function loadNotes() {
    document.getElementById('notes-loading').classList.remove('hidden');
    document.getElementById('notes-grid').innerHTML = '';
    document.getElementById('notes-empty').classList.add('hidden');
 
    try {
        const url = showingFavorites ? '/api/notes?favorites=true' : '/api/notes';
        const res = await apiRequest(url);
        if (!res) return;
        const data = await res.json();
        allNotes = data.notes || [];
        renderNotes(allNotes);
    } catch (err) {
        console.error(err);
    } finally {
        document.getElementById('notes-loading').classList.add('hidden');
    }
}
 
function renderNotes(notes) {
    const grid = document.getElementById('notes-grid');
    const empty = document.getElementById('notes-empty');
 
    // Update counts
    const favCount = allNotes.filter(n => n.is_favorite).length;
    document.getElementById('all-count').textContent = allNotes.length;
    document.getElementById('fav-count').textContent = favCount;
 
    if (notes.length === 0) {
        empty.classList.remove('hidden');
        grid.innerHTML = '';
        return;
    }
 
    empty.classList.add('hidden');
    grid.innerHTML = notes.map(note => `
        <div class="note-card" id="note-${note.id}">
            <div class="note-card-header">
                <h3 class="note-card-title" onclick="viewNote(${note.id})">${escapeHtml(note.title)}</h3>
                <div class="note-card-actions">
                    <button class="note-action-btn fav-btn ${note.is_favorite ? 'active' : ''}"
                        onclick="toggleFavorite(${note.id})" title="${note.is_favorite ? 'Remove favorite' : 'Add favorite'}">
                        ${note.is_favorite ? '⭐' : '☆'}
                    </button>
                    <button class="note-action-btn delete-btn" onclick="deleteNote(${note.id})" title="Delete note">🗑</button>
                </div>
            </div>
            <p class="note-card-preview" id="preview-${note.id}" onclick="viewNote(${note.id})">${escapeHtml(note.content.substring(0, 120))}${note.content.length > 120 ? '...' : ''}</p>
            <p id="encrypted-${note.id}" style="display:none;font-size:11px;color:#00ff88;word-break:break-all;margin-top:6px;font-family:monospace;">${note.encrypted_content || ''}</p>
            <div class="note-card-footer">
                <span class="note-card-date">${formatDate(note.created_at)}</span>
                <span class="note-encrypted-badge">🔒 encrypted</span>
                <button onclick="toggleEncrypted(${note.id})" id="enc-btn-${note.id}" style="font-size:11px;background:none;border:1px solid #00ff88;color:#00ff88;padding:2px 8px;border-radius:4px;cursor:pointer;margin-left:6px;">Show Encrypted</button>
            </div>
        </div>
    `).join('');
}
 
function toggleEncrypted(noteId) {
    const preview = document.getElementById('preview-' + noteId);
    const encrypted = document.getElementById('encrypted-' + noteId);
    const btn = document.getElementById('enc-btn-' + noteId);
    const isHidden = encrypted.style.display === 'none';
    encrypted.style.display = isHidden ? 'block' : 'none';
    preview.style.display = isHidden ? 'none' : 'block';
    btn.textContent = isHidden ? 'Show Decrypted' : 'Show Encrypted';
}
 
function viewNote(noteId) {
    const note = allNotes.find(n => n.id === noteId);
    if (!note) return;
    document.getElementById('view-note-title').textContent = note.title;
    document.getElementById('view-note-content').textContent = note.content;
    document.getElementById('view-note-date').textContent = formatDate(note.created_at);
    document.getElementById('view-note-fav').textContent = note.is_favorite ? '⭐ Favorite' : '';
    document.getElementById('view-modal-overlay').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}
 
function closeViewModal() {
    document.getElementById('view-modal-overlay').classList.add('hidden');
    document.body.style.overflow = '';
}
 
function closeViewModalOutside(e) {
    if (e.target.id === 'view-modal-overlay') closeViewModal();
}
 
async function handleCreateNote(e) {
    e.preventDefault();
    const btn = document.getElementById('save-note-btn');
    const btnText = document.getElementById('save-note-text');
    const errorDiv = document.getElementById('modal-error');
    errorDiv.classList.add('hidden');
 
    const title = document.getElementById('note-title').value.trim();
    const content = document.getElementById('note-content').value.trim();
    const isFavorite = document.getElementById('note-favorite').checked;
 
    if (!title || !content) return;
 
    btn.disabled = true;
    btnText.textContent = '🔒 Encrypting...';
 
    try {
        const res = await apiRequest('/api/notes', {
            method: 'POST',
            body: JSON.stringify({ title, content, is_favorite: isFavorite })
        });
        if (!res) return;
        const data = await res.json();
 
        if (res.ok) {
            closeModal();
            document.getElementById('note-form').reset();
            await loadNotes();
        } else {
            errorDiv.textContent = '✕ ' + (data.error || 'Failed to save note');
            errorDiv.classList.remove('hidden');
        }
    } catch (err) {
        errorDiv.textContent = '✕ Network error';
        errorDiv.classList.remove('hidden');
    } finally {
        btn.disabled = false;
        btnText.textContent = '🔒 Encrypt & Save';
    }
}
 
async function deleteNote(noteId) {
    if (!confirm('Delete this note permanently?')) return;
    const res = await apiRequest('/api/notes/' + noteId, { method: 'DELETE' });
    if (res && res.ok) {
        document.getElementById('note-' + noteId)?.remove();
        allNotes = allNotes.filter(n => n.id !== noteId);
        renderNotes(showingFavorites ? allNotes.filter(n => n.is_favorite) : allNotes);
    }
}
 
async function toggleFavorite(noteId) {
    const res = await apiRequest('/api/notes/' + noteId + '/favorite', { method: 'PATCH' });
    if (res && res.ok) {
        const data = await res.json();
        const note = allNotes.find(n => n.id === noteId);
        if (note) note.is_favorite = data.is_favorite;
        renderNotes(showingFavorites ? allNotes.filter(n => n.is_favorite) : allNotes);
    }
}
 
function showAll() {
    showingFavorites = false;
    document.getElementById('vault-title').textContent = 'All Notes';
    document.getElementById('vault-subtitle').textContent = 'Your encrypted private notes';
    document.querySelectorAll('.sidebar-btn').forEach((b, i) => b.classList.toggle('active', i === 0));
    renderNotes(allNotes);
}
 
function showFavorites() {
    showingFavorites = true;
    document.getElementById('vault-title').textContent = 'Favorites';
    document.getElementById('vault-subtitle').textContent = 'Your starred notes';
    document.querySelectorAll('.sidebar-btn').forEach((b, i) => b.classList.toggle('active', i === 1));
    renderNotes(allNotes.filter(n => n.is_favorite));
}
 
function openModal() {
    document.getElementById('modal-overlay').classList.remove('hidden');
    document.getElementById('modal-error').classList.add('hidden');
    document.body.style.overflow = 'hidden';
    setTimeout(() => document.getElementById('note-title').focus(), 100);
}
 
function closeModal() {
    document.getElementById('modal-overlay').classList.add('hidden');
    document.body.style.overflow = '';
}
 
function closeModalOutside(e) {
    if (e.target.id === 'modal-overlay') closeModal();
}
 
function escapeHtml(str) {
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
 
function formatDate(iso) {
    return new Date(iso).toLocaleDateString('en-US', { year:'numeric', month:'short', day:'numeric' });
}
 
// Init on load
document.addEventListener('DOMContentLoaded', async () => {
    // Set user info in sidebar
    const user = JSON.parse(localStorage.getItem('cv_user') || '{}');
    if (user.username) {
        document.getElementById('user-name').textContent = user.username;
        document.getElementById('user-avatar').textContent = user.username[0].toUpperCase();
    }
    await loadNotes();
});