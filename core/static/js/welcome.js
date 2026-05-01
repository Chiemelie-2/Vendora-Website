function toggleMenu() {
    const menu = document.getElementById('side-menu');
    const overlay = document.getElementById('sidebar-overlay');
    
    if (menu.classList.contains('active')) {
        menu.classList.remove('active');
        overlay.style.display = 'none';
        document.body.style.overflow = 'auto'; // Re-enable scrolling
    } else {
        menu.classList.add('active');
        overlay.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Disable background scrolling
    }
}
