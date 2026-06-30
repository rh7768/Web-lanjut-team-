/* ── BookAI — app.js ─────────────────────────────────────────── */

// ── CSRF helper ────────────────────────────────────────────────
function getCsrf() {
  return document.cookie.split(';')
    .map(c => c.trim()).find(c => c.startsWith('csrftoken='))
    ?.split('=')[1] || '';
}

// ── Fetch wrapper ───────────────────────────────────────────────
async function apiFetch(url, opts = {}) {

  try {

    const res = await fetch(url, {

      credentials: 'same-origin',

      headers: {
        'X-CSRFToken': getCsrf(),
        'Content-Type': 'application/json',
        ...opts.headers
      },

      ...opts,
    });

    if (!res.ok) return null;

    return await res.json();

  } catch {

    return null;
  }
}

// ── Modal state ─────────────────────────────────────────────────
let _currentBook = null;
let _bookDetailRequestId = 0;

function setBookMeta(book, isLoading = false) {
  const el = id => document.getElementById(id);
  const fallbackText = isLoading ? 'Memuat...' : 'Tidak tersedia';

  el('modalAuthor').textContent = hasUsableValue(book.author) ? book.author : fallbackText;
  el('modalYear').textContent = hasUsableValue(book.year) ? book.year : fallbackText;
  el('modalLanguage').textContent = formatLanguage(book.language) || fallbackText;
}

function setBookCover(book) {
  const img = document.getElementById('modalCoverImg');
  const fallback = document.getElementById('modalCoverFallback');

  if (book.cover_url) {
    img.src = book.cover_url;
    img.alt = book.title || 'Cover Buku';
    img.style.display = 'block';
    fallback.style.display = 'none';
  } else {
    img.removeAttribute('src');
    img.style.display = 'none';
    fallback.style.display = 'flex';
  }
}

async function hydrateBookDetail(book, requestId) {
  const params = new URLSearchParams();

  if (book.key) params.set('key', book.key);
  if (book.title) params.set('title', book.title);
  if (!params.toString()) return;

  const detail = await apiFetch(`/api/book-detail/?${params.toString()}`);

  if (_currentBook !== book || requestId !== _bookDetailRequestId) return;

  if (!detail) {
    setBookMeta(book);
    return;
  }

  if (detail.year) book.year = detail.year;
  if (detail.language) book.language = detail.language;
  if (detail.cover_url && !book.cover_url) book.cover_url = detail.cover_url;
  if (
    detail.author &&
    (!book.author || book.author === 'Unknown' || book.author === 'AI Summary')
  ) {
    book.author = detail.author;
  }
  if (
    detail.description &&
    (!book.description || book.description === 'Book from OpenLibrary API')
  ) {
    book.description = detail.description;
  }

  setBookMeta(book);
  setBookCover(book);
  document.getElementById('modalDescription').textContent =
    book.description || 'Tidak ada deskripsi tersedia.';
}

function openBookModal(book) {
  _currentBook = book;
  _bookDetailRequestId += 1;

  const needsDetail =
    !hasUsableValue(book.year) ||
    !hasUsableValue(book.language) ||
    !hasUsableValue(book.author) ||
    book.author === 'Unknown' ||
    book.author === 'AI Summary';

  document.getElementById('modalTitle').textContent = book.title || '';
  document.getElementById('modalDescription').textContent =
    book.description || 'Tidak ada deskripsi tersedia.';

  setBookMeta(book, needsDetail);
  setBookCover(book);
  updateFavBtn(book.is_favorite);

  document.getElementById('bookModal').hidden = false;
  document.body.style.overflow = 'hidden';

  if (needsDetail) {
    hydrateBookDetail(book, _bookDetailRequestId);
  }
}

function closeBookModal() {
  _bookDetailRequestId += 1;
  document.getElementById('bookModal').hidden = true;
  document.body.style.overflow = '';
}

function openLoginModal() {
  document.getElementById('loginRequiredModal').hidden = false;
  document.body.style.overflow = 'hidden';
}

function closeLoginModal() {
  document.getElementById('loginRequiredModal').hidden = true;
  document.body.style.overflow = '';
}

// Close modals on overlay click
document.addEventListener('click', e => {
  if (e.target.id === 'bookModal') closeBookModal();
  if (e.target.id === 'loginRequiredModal') closeLoginModal();
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { closeBookModal(); closeLoginModal(); }
});

// ── Favourite toggle ────────────────────────────────────────────
function updateFavBtn(isFav) {
  const btn = document.getElementById('modalFavBtn');
  const text = document.getElementById('modalFavText');
  if (!btn) return;
  btn.classList.toggle('active', isFav);
  text.textContent = isFav ? 'Hapus dari Favorit' : 'Tambah ke Favorit';
}

async function toggleFavoriteFromModal() {
  if (!_currentBook) return;

  // Check if logged in — backend returns 401 if not
  const data = await apiFetch('/api/favorite/toggle/', {
    method: 'POST',
    body: JSON.stringify(_currentBook),
  });

  if (!data) {
    // 401 → show login modal
    closeBookModal();
    openLoginModal();
    return;
  }

  const isFav = data.status === 'added';
  _currentBook.is_favorite = isFav;
  updateFavBtn(isFav);

  // Sync card in grid if present
  document.querySelectorAll(`[data-book-key="${_currentBook.key}"]`).forEach(card => {
    card.dataset.isFavorite = isFav ? '1' : '0';
  });
}

// ── Render books ────────────────────────────────────────────────
function renderBooks(container, books, showRank = false) {
  container.innerHTML = '';
  books.forEach((book, i) => {
    const card = document.createElement('div');
    card.className = 'book-card';
    card.dataset.bookKey = book.key;
    card.dataset.isFavorite = book.is_favorite ? '1' : '0';
    card.onclick = () => openBookModal(book);

    const coverHtml = book.cover_url
      ? `<img src="${book.cover_url}" alt="${esc(book.title)}" loading="lazy" />`
      : `<div class="cover-fallback">
           <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
             <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
             <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
           </svg>
         </div>`;

    const rankBadge = showRank
      ? `<span class="rank-badge">${i + 1}</span>` : '';

    card.innerHTML = `
      <div class="book-cover">
        ${rankBadge}
        ${coverHtml}
        <div class="book-cover-overlay">
          <span class="book-title-overlay">${esc(book.title)}</span>
          <span class="book-author-overlay">${esc(book.author)}</span>
        </div>
      </div>
      <div class="book-info">
        <p class="book-title">${esc(book.title)}</p>
        <p class="book-author">${esc(book.author)}</p>
      </div>`;

    container.appendChild(card);
  });
}

// ── Utils ───────────────────────────────────────────────────────
function esc(str) {
  return String(str || '').replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}

function formatLanguage(language) {
  if (Array.isArray(language)) {
    language = language.find(Boolean) || '';
  }

  if (!language) return '';

  const value = String(language).trim();
  const languageNames = {
    eng: 'English',
    en: 'English',
    ind: 'Indonesian',
    id: 'Indonesian',
    may: 'Malay',
    msa: 'Malay',
    fre: 'French',
    fra: 'French',
    ger: 'German',
    deu: 'German',
    spa: 'Spanish',
    ita: 'Italian',
    por: 'Portuguese',
    dut: 'Dutch',
    nld: 'Dutch',
    jpn: 'Japanese',
    kor: 'Korean',
    chi: 'Chinese',
    zho: 'Chinese',
    ara: 'Arabic',
    rus: 'Russian',
  };

  return languageNames[value.toLowerCase()] || capitalise(value);
}

function hasUsableValue(value) {
  if (value === null || value === undefined) return false;
  const text = String(value).trim();
  return text !== '' && text !== '-' && text.toLowerCase() !== 'none';
}

function capitalise(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

// ── OTP Auto Next ─────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {

  const otpInputs = document.querySelectorAll('.otp-input');

  if (!otpInputs.length) return;

  otpInputs.forEach((input, index) => {

    input.addEventListener('input', function () {

      this.value = this.value.replace(/[^0-9]/g, '');

      if (this.value.length === 1 && index < otpInputs.length - 1) {
        otpInputs[index + 1].focus();
      }

    });

    input.addEventListener('keydown', function (e) {

      if (e.key === 'Backspace' &&
          this.value === '' &&
          index > 0) {

        otpInputs[index - 1].focus();
      }

    });

  });

});
