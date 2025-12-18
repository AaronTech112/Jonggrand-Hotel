document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('shadow-lg');
        } else {
            navbar.classList.remove('shadow-lg');
        }
    });

    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const animatedEls = document.querySelectorAll('[data-animate]');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const el = entry.target;
            if (entry.isIntersecting) {
                const delay = el.getAttribute('data-delay');
                if (delay) el.style.transitionDelay = `${parseInt(delay, 10) / 1000}s`;
                el.classList.add('in-view');
                if (el.getAttribute('data-once') === 'true') observer.unobserve(el);
            } else {
                if (!prefersReduced) el.classList.remove('in-view');
            }
        });
    }, { threshold: 0.15 });

    animatedEls.forEach(el => {
        if (!prefersReduced) {
            observer.observe(el);
        } else {
            el.classList.add('in-view');
        }
    });
});
