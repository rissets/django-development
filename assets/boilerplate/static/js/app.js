(() => {
  const root = document.querySelector('[data-app-shell]');
  const toggle = document.getElementById('theme-toggle');
  let stored;
  try { stored = localStorage.getItem('theme'); } catch { /* Storage can be unavailable. */ }
  root.dataset.theme = stored || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  toggle.hidden = false;
  const label = () => {
    const next = root.dataset.theme === 'dark' ? 'terang' : 'gelap';
    toggle.textContent = `Tema ${next}`;
    toggle.setAttribute('aria-label', `Gunakan tema ${next}`);
  };
  label();
  toggle.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('theme', root.dataset.theme); } catch { /* Optional preference. */ }
    label();
  });
  document.querySelectorAll('[data-pending-form]').forEach(form => {
    form.addEventListener('submit', () => {
      const button = form.querySelector('button[type="submit"]');
      button.dataset.label = button.textContent;
      button.textContent = 'Memproses…';
      button.disabled = true;
      form.setAttribute('aria-busy', 'true');
    });
  });
  window.addEventListener('pageshow', () => {
    document.querySelectorAll('button[data-label]').forEach(button => {
      button.textContent = button.dataset.label;
      button.disabled = false;
      button.form.removeAttribute('aria-busy');
    });
  });
})();
