let menuItems = [
    {% for item in menu_items %}
    { 
        id: "{{ item.id }}",
        name: "{{ item.name|escapejs }}",
        price: "{{ item.price }}",
        desc: "{{ item.description|escapejs }}",
        category: "{{ item.item_type }}",
        image: "{% if item.image %}{{ item.image.url }}{% else %}null{% endif %}"
    }{% if not forloop.last %},{% endif %}
    {% endfor %}
];

let currentImageData = null;
let editingIndex = null;

/* ================= TOAST ================= */
const TOAST_META = {
    success: { title: 'Done' },
    error: { title: 'Error' },
    warning: { title: 'Heads up' },
    info: { title: 'Tip' }
};

function showToast(message, type='info', title=null, duration=3000) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast t-${type}`;
    toast.innerHTML = `<strong>${title || TOAST_META[type].title}</strong><br>${message}`;
    container.appendChild(toast);
    setTimeout(()=> toast.remove(), duration);
}

/* ================= CONFIRM ================= */
function showConfirm({title, message, onConfirm}) {
    const overlay = document.getElementById('confirm-overlay');
    overlay.classList.add('visible');

    document.getElementById('confirm-title').textContent = title;
    document.getElementById('confirm-message').textContent = message;

    document.getElementById('confirm-ok').onclick = () => {
        overlay.classList.remove('visible');
        onConfirm && onConfirm();
    };

    document.getElementById('confirm-cancel').onclick = () => {
        overlay.classList.remove('visible');
    };
}

/* ================= IMAGE ================= */
function handleItemImage(input) {
    const file = input.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = e => {
        currentImageData = e.target.result;

        const preview = document.getElementById('item-img-preview');
        preview.src = currentImageData;
        preview.style.display = 'block';

        document.getElementById('img-drop-placeholder').style.display = 'none';
        document.getElementById('img-drop').classList.add('has-image');

        syncPreview();
    };
    reader.readAsDataURL(file);
}

/* ================= EDIT ================= */
function editItem(index) {
    const item = menuItems[index];

    document.getElementById('item-name').value = item.name;
    document.getElementById('item-price').value = item.price;
    document.getElementById('item-desc').value = item.desc;
    document.getElementById('item-category').value = item.category;

    currentImageData = item.image;

    if (item.image) {
        const preview = document.getElementById('item-img-preview');
        preview.src = item.image;
        preview.style.display = 'block';
    }

    editingIndex = index;

    showToast("Editing dish...", "info");
}

/* ================= PREVIEW ================= */
function syncPreview() {
    const name = document.getElementById('item-name').value || 'Dish name';
    const price = document.getElementById('item-price').value;
    const desc = document.getElementById('item-desc').value || '';

    let card = document.getElementById('live-preview-card');

    if (!card) {
        card = document.createElement('div');
        card.id = 'live-preview-card';
        card.className = 'phone-item';
        document.getElementById('phone-items').prepend(card);
    }

    card.innerHTML = `
        ${currentImageData ? `<img src="${currentImageData}" class="phone-item-img">` : ''}
        <div>${name}</div>
        <div>${desc}</div>
        <div>₦${price || '—'}</div>
    `;
}

/* ================= ADD / UPDATE ================= */
function addItem() {
    const name = document.getElementById('item-name').value.trim();
    const price = document.getElementById('item-price').value.trim();
    const desc = document.getElementById('item-desc').value.trim();
    const category = document.getElementById('item-category').value;

    if (!name || !price) {
        showToast("Fill required fields", "error");
        return;
    }

    let oldImage = editingIndex !== null ? menuItems[editingIndex].image : null;

    const item = {
        name,
        price,
        desc,
        category,
        image: currentImageData || oldImage
    };

    if (editingIndex !== null) {
        menuItems[editingIndex] = item;
        showToast("Dish updated", "success");
    } else {
        menuItems.push(item);
        showToast("Dish added", "success");
    }

    renderAll();
    resetForm();
}

/* ================= RENDER ================= */
function renderAll() {
    const grid = document.getElementById('items-grid');
    const phone = document.getElementById('phone-items');

    grid.innerHTML = '';
    phone.innerHTML = '';

    menuItems.forEach((item, i) => {
        const card = document.createElement('div');
        card.className = 'dish-card';

        card.innerHTML = `
            ${item.image ? `<img src="${item.image}" class="dish-card-img">` : ''}
            <div>${item.name}</div>
            <div>₦${item.price}</div>
            <button onclick="editItem(${i})">Edit</button>
            <button onclick="confirmRemoveItem(${i})">Delete</button>
        `;

        grid.appendChild(card);

        const phoneCard = document.createElement('div');
        phoneCard.innerHTML = `
            ${item.image ? `<img src="${item.image}">` : ''}
            <div>${item.name}</div>
        `;
        phone.appendChild(phoneCard);
    });
}

/* ================= DELETE ================= */
function confirmRemoveItem(index) {
    showConfirm({
        title: "Delete dish?",
        message: "This cannot be undone",
        onConfirm: () => {
            menuItems.splice(index, 1);
            renderAll();
            showToast("Dish removed", "warning");
        }
    });
}

/* ================= RESET ================= */
function resetForm() {
    document.getElementById('item-name').value = '';
    document.getElementById('item-price').value = '';
    document.getElementById('item-desc').value = '';

    currentImageData = null;
    editingIndex = null;

    document.getElementById('item-img-preview').style.display = 'none';
}

/* ================= SUBMIT ================= */
function submitMenu() {
    if (!menuItems.length) {
        showToast("Menu is empty", "warning");
        return;
    }

    document.getElementById('menu-data-input').value = JSON.stringify(menuItems);
    document.getElementById('menu-form').submit();
}

/* ================= INIT ================= */
window.onload = function() {
    renderAll();
};