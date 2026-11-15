// Small interactivity: filter project cards and smooth-scroll
document.addEventListener('DOMContentLoaded', function () {
  // Project filter
  const filter = document.getElementById('project-filter');
  if (filter) {
    filter.addEventListener('input', function () {
      const q = this.value.trim().toLowerCase();
      document.querySelectorAll('.project-card').forEach(function (card) {
        const tech = (card.dataset.tech || '').toLowerCase();
        card.style.display = (q === '' || tech.includes(q)) ? '' : 'none';
      });
    });
  }

  // Smooth scroll for internal links
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({behavior: 'smooth', block: 'start'});
      }
    });
  });
});
