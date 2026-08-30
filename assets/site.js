(() => {
  const navToggle = document.querySelector('.nav-toggle');
  const siteNav = document.querySelector('.site-nav');

  if (navToggle && siteNav) {
    const closeNavigation = () => {
      siteNav.classList.remove('is-open');
      navToggle.setAttribute('aria-expanded', 'false');
      navToggle.setAttribute('aria-label', 'Open navigation');
    };

    navToggle.addEventListener('click', () => {
      const isOpen = siteNav.classList.toggle('is-open');
      navToggle.setAttribute('aria-expanded', String(isOpen));
      navToggle.setAttribute('aria-label', isOpen ? 'Close navigation' : 'Open navigation');
    });

    siteNav.addEventListener('click', (event) => {
      if (event.target.closest('a') && window.matchMedia('(max-width: 980px)').matches) {
        closeNavigation();
      }
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && siteNav.classList.contains('is-open')) {
        closeNavigation();
        navToggle.focus();
      }
    });
  }

  document.querySelectorAll('[data-current-year]').forEach((element) => {
    element.textContent = new Date().getFullYear();
  });

  const revealLinkedPaper = () => {
    if (!window.location.hash) return;

    const target = document.getElementById(window.location.hash.slice(1));
    if (target instanceof HTMLDetailsElement) {
      target.open = true;
    }
  };

  revealLinkedPaper();
  window.addEventListener('hashchange', revealLinkedPaper);

  const analyticsLoader = document.createElement('script');
  analyticsLoader.src = 'assets/analytics.js';
  analyticsLoader.async = true;
  document.head.appendChild(analyticsLoader);
})();
