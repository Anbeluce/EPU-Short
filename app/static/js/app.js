let quill; // Global quill instance
let adminQuill; // Admin quill instance
let fpLinkExpire, fpNoteExpire, fpShortenExpire;

window.switchTab = function(tabName) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    
    const btn = document.querySelector(`.tab-btn[onclick="switchTab('${tabName}')"]`) || document.querySelector(`.tab-btn[data-target="tab-${tabName}"]`);
    if (btn) btn.classList.add('active');
    
    const content = document.getElementById('tab-' + tabName);
    if (content) content.classList.add('active');
};

window.openLinkModal = function(btnOrId = null, url = '', code = '', expires = '') {
    let id = btnOrId;
    if (typeof btnOrId === 'object' && btnOrId !== null) {
        id = btnOrId.dataset.id;
        url = btnOrId.dataset.url;
        code = btnOrId.dataset.code;
        expires = btnOrId.dataset.expires || '';
    }
    const modal = document.getElementById('linkModal');
    const form = document.getElementById('linkForm');
    const title = document.getElementById('linkModalTitle');
    
    document.getElementById('link_url').value = url;
    document.getElementById('link_code').value = code;
    if (fpLinkExpire) {
        if (expires) fpLinkExpire.setDate(expires);
        else fpLinkExpire.clear();
    }
    
    if (id) {
        title.innerText = 'Sửa Link';
        form.action = `/memaybeo/edit/link/${id}`;
    } else {
        title.innerText = 'Tạo Link';
        form.action = '/memaybeo/create/link';
    }
    
    modal.style.display = 'block';
};

window.openNoteModal = function(btnOrId = null, titleStr = '', code = '', expires = '') {
    let id = btnOrId;
    if (typeof btnOrId === 'object' && btnOrId !== null) {
        id = btnOrId.dataset.id;
        titleStr = btnOrId.dataset.title;
        code = btnOrId.dataset.code;
        expires = btnOrId.dataset.expires || '';
    }
    const modal = document.getElementById('noteModal');
    const form = document.getElementById('noteForm');
    const titleEl = document.getElementById('noteModalTitle');
    
    document.getElementById('note_title').value = titleStr;
    document.getElementById('note_code').value = code;
    document.getElementById('note_pass').value = '';
    if (fpNoteExpire) {
        if (expires) fpNoteExpire.setDate(expires);
        else fpNoteExpire.clear();
    }
    
    if (adminQuill) {
        if (id) {
            const contentEl = document.getElementById('note-content-' + id);
            adminQuill.root.innerHTML = contentEl ? contentEl.value : '';
        } else {
            adminQuill.root.innerHTML = '';
        }
    }
    
    if (id) {
        titleEl.innerText = 'Sửa Note';
        form.action = `/memaybeo/edit/note/${id}`;
    } else {
        titleEl.innerText = 'Tạo Note';
        form.action = '/memaybeo/create/note';
    }
    
    modal.style.display = 'block';
};

window.closeModal = function(modalId) {
    document.getElementById(modalId).style.display = 'none';
};

window.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
});

document.addEventListener('DOMContentLoaded', () => {

    // Form Submissions
    const shortenForm = document.getElementById('shorten-form');
    if (shortenForm) {
        shortenForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await submitForm(shortenForm, '/api/shorten', 'shorten-btn');
        });
    }

    const noteForm = document.getElementById('note-form');
    if (noteForm) {
        noteForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await submitForm(noteForm, '/api/note', 'note-btn');
        });
    }

    const fpConfig = {
        enableTime: true,
        dateFormat: "Y-m-d H:i",
        minDate: "today",
        time_24hr: true,
        disableMobile: true
    };
    
    const shortenExpireEl = document.getElementById('link-expire');
    if (shortenExpireEl) fpShortenExpire = flatpickr(shortenExpireEl, fpConfig);
    
    const adminLinkExpireEl = document.getElementById('link_expire');
    if (adminLinkExpireEl) fpLinkExpire = flatpickr(adminLinkExpireEl, fpConfig);
    
    const adminNoteExpireEl = document.getElementById('note_expire');
    if (adminNoteExpireEl) fpNoteExpire = flatpickr(adminNoteExpireEl, fpConfig);

    const frontNoteExpireEl = document.getElementById('front-note-expire');
    if (frontNoteExpireEl) flatpickr(frontNoteExpireEl, fpConfig);

    if (document.getElementById('editor')) {
        quill = new Quill('#editor', {
            theme: 'snow',
            placeholder: 'Nhập nội dung ghi chú...',
            modules: {
                toolbar: [
                    [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
                    ['bold', 'italic', 'underline', 'strike'],
                    ['blockquote', 'code-block'],
                    [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                    [{ 'align': [] }],
                    ['link', 'image'],
                    ['clean']
                ]
            }
        });
    }

    if (document.getElementById('note_editor')) {
        adminQuill = new Quill('#note_editor', {
            theme: 'snow',
            placeholder: 'Nhập nội dung ghi chú...',
            modules: {
                toolbar: [
                    [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
                    ['bold', 'italic', 'underline', 'strike'],
                    ['blockquote', 'code-block'],
                    [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                    [{ 'align': [] }],
                    ['link', 'image'],
                    ['clean']
                ]
            }
        });
    }

    // Custom Alias Preview has been replaced with a robust prefix layout
    // No JS needed for the prefix input

    // Admin Search
    const searchInput = document.getElementById('table-search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const searchText = e.target.value.toLowerCase();
            const activeTableId = document.querySelector('.tab-content.active .admin-table').id;
            filterTable(activeTableId, searchText);
        });
    }
});

function switchTab(tabName) {
    // Manual tab switch if needed
}

async function submitForm(form, endpoint, btnId) {
    const btn = document.getElementById(btnId);
    setLoading(btn, true);

    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // Clean up empty optional fields
    if (!data.custom_code) delete data.custom_code;
    if (!data.password) delete data.password;
    if (!data.expires_at) delete data.expires_at;
    if (!data.title) delete data.title;

    // If this is the note form, get HTML from Quill
    if (endpoint === '/api/note' && quill) {
        const htmlContent = quill.root.innerHTML;
        if (quill.getText().trim().length === 0) {
            showToast('Nội dung không được để trống', 'error');
            setLoading(btn, false);
            return;
        }
        data.content = htmlContent;
    }

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (response.ok) {
            showResult(result, endpoint.includes('note') ? 'note' : 'link');
            // Reset form
            form.reset();
            if (endpoint === '/api/note' && quill) {
                quill.setText('');
            }
            showToast('Tạo thành công!', 'success');
        } else {
            showToast(result.detail || 'Đã xảy ra lỗi!', 'error');
        }
    } catch (error) {
        showToast('Lỗi kết nối máy chủ!', 'error');
        console.error(error);
    } finally {
        setLoading(btn, false);
    }
}

function showResult(data, type) {
    const resultCard = document.getElementById('result-card');
    const urlInput = document.getElementById('result-url-input');
    const badgesContainer = document.querySelector('.result-badges');
    
    const baseUrl = window.location.origin;
    const code = data.short_code;
    const url = type === 'link' ? (data.short_url || `${baseUrl}/${code}`) : (data.note_url || `${baseUrl}/n/${code}`);
    
    urlInput.value = url;
    
    badgesContainer.innerHTML = '';
    if (data.has_password) {
        badgesContainer.innerHTML += '<span class="badge badge-purple">🔒 Protected</span>';
    }
    if (data.expires_at) {
        badgesContainer.innerHTML += '<span class="badge badge-yellow">⏰ Has Expiry</span>';
    }

    resultCard.style.display = 'block';
}

async function copyToClipboard(inputId = 'result-url-input') {
    let text;
    if (inputId === 'result-url-input') {
         text = document.getElementById(inputId).value;
    } else {
        // copy raw text
        text = inputId;
    }
    
    try {
        await navigator.clipboard.writeText(text);
        showToast('Đã copy link!', 'success');
    } catch (err) {
        showToast('Lỗi khi copy!', 'error');
    }
}

function copyNoteContent() {
    const content = document.querySelector('.note-content').innerText;
    copyToClipboard(content);
}

function showToast(message, type = 'success') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span>${type === 'success' ? '✅' : '❌'}</span>
        <div>${message}</div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease reverse forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Make togglePassword and toggleDropdown global
window.togglePassword = function(inputId) {
    const input = document.getElementById(inputId);
    const btn = input.nextElementSibling;
    const icon = btn.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        if (icon) {
            icon.classList.remove('ph-eye');
            icon.classList.add('ph-eye-slash');
        }
    } else {
        input.type = 'password';
        if (icon) {
            icon.classList.remove('ph-eye-slash');
            icon.classList.add('ph-eye');
        }
    }
};

window.toggleDropdown = function(dropdownId) {
    const dropdown = document.getElementById(dropdownId);
    // Close other dropdowns
    document.querySelectorAll('.dropdown-menu').forEach(d => {
        if (d.id !== dropdownId) d.classList.remove('active');
    });
    dropdown.classList.toggle('active');
};

// Close dropdowns when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.dropdown-container')) {
        document.querySelectorAll('.dropdown-menu').forEach(d => {
            d.classList.remove('active');
        });
    }
});

function setLoading(button, isLoading) {
    if (!button) return;
    const textSpan = button.querySelector('.btn-text');
    const loadingSpan = button.querySelector('.btn-loading');
    
    if (isLoading) {
        button.disabled = true;
        if(textSpan) textSpan.style.display = 'none';
        if(loadingSpan) loadingSpan.style.display = 'inline';
    } else {
        button.disabled = false;
        if(textSpan) textSpan.style.display = 'inline';
        if(loadingSpan) loadingSpan.style.display = 'none';
    }
}

// Admin functions
function confirmDelete(type, id) {
    return confirm('Bạn có chắc chắn muốn xóa mục này?');
}

function filterTable(tableId, searchText) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchText) ? '' : 'none';
    });
}
