
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('figure > blockquote[translate]').forEach(bq => {
    const translateText = 'см. перевод';
    const originalText = 'см. оригинал';

    const translated = bq.getAttribute('translate');
    const original = bq.textContent.trim();
    if (!translated) return;

    bq.textContent = translated;

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = originalText;

    const fig = bq.parentElement;
    const cap = fig.querySelector(':scope > figcaption');

    const footer = document.createElement('footer');
    footer.append(btn);
    if (cap) footer.append(cap);
    fig.append(footer);

    let showingTranslated = true;
    btn.addEventListener('click', () => {
      if (showingTranslated) {
        bq.textContent = original;
        btn.textContent = translateText;
      } else {
        bq.textContent = translated;
        btn.textContent = originalText;
      }
      showingTranslated = !showingTranslated;
    });
  });
});
