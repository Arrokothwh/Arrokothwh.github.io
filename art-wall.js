(function () {
  const magicButton = document.getElementById('magicButton');
  const magicOverlay = document.getElementById('magicOverlay');
  const magicClose = document.getElementById('magicClose');

  if (!magicButton || !magicOverlay || !magicClose) {
    return;
  }

  const artGroups = window.__ART_GROUPS__ || { horizontal: [], vertical: [] };
  const artImages = Array.isArray(window.__ART_IMAGES__) ? window.__ART_IMAGES__ : [];

  let artPage = 0;
  let lastPatternIndex = -1;

  const ORIENTATION_RATIO = {
    horizontal: 1600 / 1067,
    vertical: 1067 / 1600
  };

  const MAGIC_PATTERNS = [
    [['horizontal', 'horizontal', 'horizontal'], ['vertical', 'horizontal', 'vertical']],
    [['vertical', 'horizontal', 'vertical'], ['horizontal', 'horizontal', 'horizontal']],
    [['horizontal', 'horizontal'], ['vertical', 'horizontal', 'vertical']],
    [['vertical', 'horizontal', 'vertical'], ['horizontal', 'horizontal']]
  ];

  const MOBILE_MAGIC_PATTERNS = [
    [['horizontal', 'horizontal'], ['vertical', 'vertical']],
    [['vertical', 'vertical'], ['horizontal', 'horizontal']],
    [['horizontal', 'horizontal'], ['horizontal', 'horizontal']]
  ];

  function cyclePick(pool, index) {
    if (!pool.length) return null;
    return pool[index % pool.length];
  }

  function pickPattern(patterns) {
    if (patterns.length <= 1) return { pattern: patterns[0], index: 0 };

    let index = Math.floor(Math.random() * patterns.length);
    if (index === lastPatternIndex) {
      index = (index + 1) % patterns.length;
    }
    lastPatternIndex = index;
    return { pattern: patterns[index], index };
  }

  function buildMagicTiles(images) {
    magicOverlay.innerHTML = '';

    const stack = document.createElement('div');
    stack.className = 'magic-stack';

    const hasGroups = (artGroups.horizontal && artGroups.horizontal.length) || (artGroups.vertical && artGroups.vertical.length);
    if (!images.length && !hasGroups) {
      const empty = document.createElement('p');
      empty.className = 'magic-empty';
      empty.textContent = 'No images found in art/manifest.json yet.';
      stack.appendChild(empty);
      magicOverlay.appendChild(stack);
      return;
    }

    const patterns = window.innerWidth < 520 ? MOBILE_MAGIC_PATTERNS : MAGIC_PATTERNS;
    const { pattern, index: patternIndex } = pickPattern(patterns);
    let horizontalIndex = artPage * 7 + patternIndex * 3;
    let verticalIndex = artPage * 5 + patternIndex * 2;
    let fallbackIndex = artPage * 6 + patternIndex;
    let delayIndex = 0;

    pattern.forEach((rowPattern) => {
      const row = document.createElement('div');
      row.className = 'magic-row';

      rowPattern.forEach((orientation) => {
        const pool = artGroups[orientation] || [];
        const src =
          cyclePick(pool, orientation === 'horizontal' ? horizontalIndex++ : verticalIndex++) ||
          cyclePick(images, fallbackIndex++);
        const tile = document.createElement('div');
        const img = document.createElement('img');
        const delay = Math.min(delayIndex * 55, 440);
        delayIndex += 1;

        tile.className = 'magic-tile';
        tile.style.setProperty('--tile-delay', `${delay}ms`);
        tile.style.setProperty('--tile-ratio', String(ORIENTATION_RATIO[orientation] || 1));

        img.src = encodeURI(src);
        img.alt = '';
        img.loading = 'eager';
        img.decoding = 'async';

        tile.appendChild(img);
        row.appendChild(tile);
      });

      stack.appendChild(row);
    });

    magicOverlay.appendChild(stack);
  }

  function openMagicOverlay() {
    buildMagicTiles(artImages);
    artPage += 1;
    magicOverlay.classList.add('is-visible');
    magicOverlay.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    magicOverlay.scrollTop = 0;
  }

  function closeMagicOverlay() {
    magicOverlay.classList.remove('is-visible');
    magicOverlay.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  magicButton.addEventListener('click', openMagicOverlay);
  magicClose.addEventListener('click', closeMagicOverlay);
  magicOverlay.addEventListener('click', closeMagicOverlay);

  window.addEventListener('resize', () => {
    if (magicOverlay.classList.contains('is-visible')) {
      buildMagicTiles(artImages);
    }
  });

  window.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && magicOverlay.classList.contains('is-visible')) {
      closeMagicOverlay();
    }
  });
})();
