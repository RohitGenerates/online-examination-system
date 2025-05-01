document.addEventListener('DOMContentLoaded', () => {
    const cursorOuter = document.querySelector('.cursor-outer');
    const cursorInner = document.querySelector('.cursor-inner');
    let isHovering = false;

    // Main cursor movement
    document.addEventListener('mousemove', (e) => {
        requestAnimationFrame(() => {
            cursorOuter.style.left = e.clientX + 'px';
            cursorOuter.style.top = e.clientY + 'px';

            if (!isHovering) {
                cursorInner.style.left = e.clientX + 'px';
                cursorInner.style.top = e.clientY + 'px';
            }
        });
    });

    // Add hover effects for interactive elements
    const interactiveElements = document.querySelectorAll('a, button, .user-type, input');

    interactiveElements.forEach(el => {
        el.addEventListener('mouseenter', () => {
            isHovering = true;
            cursorOuter.style.transform = 'translate(-50%, -50%) scale(1.5)';
            cursorOuter.style.backgroundColor = 'rgba(249, 177, 122, 0.1)';
            cursorInner.style.transform = 'translate(-50%, -50%) scale(0.5)';
        });

        el.addEventListener('mouseleave', () => {
            isHovering = false;
            cursorOuter.style.transform = 'translate(-50%, -50%) scale(1)';
            cursorOuter.style.backgroundColor = 'transparent';
            cursorInner.style.transform = 'translate(-50%, -50%) scale(1)';
        });
    });

    // Click effect
    document.addEventListener('mousedown', () => {
        cursorOuter.style.transform = 'translate(-50%, -50%) scale(0.9)';
        cursorInner.style.transform = 'translate(-50%, -50%) scale(0.9)';
    });

    document.addEventListener('mouseup', () => {
        cursorOuter.style.transform = 'translate(-50%, -50%) scale(1)';
        cursorInner.style.transform = 'translate(-50%, -50%) scale(1)';
    });

    // Hide cursor when leaving window
    document.addEventListener('mouseleave', () => {
        cursorOuter.style.display = 'none';
        cursorInner.style.display = 'none';
    });

    document.addEventListener('mouseenter', () => {
        cursorOuter.style.display = 'block';
        cursorInner.style.display = 'block';
    });
});