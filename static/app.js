const form = document.querySelector('#food-form');
const list = document.querySelector('#food-list');
const count = document.querySelector('#food-count');
const message = document.querySelector('#form-message');

const numberFields = new Set(['servings_per_container', 'calories', 'energy_kj', 'total_fat_g', 'saturated_fat_g', 'carbohydrates_g', 'sugars_g', 'fiber_g', 'protein_g', 'sodium_mg', 'salt_g']);

function formatNumber(value) {
  return value === null || value === '' || value === undefined ? '—' : Number(value).toLocaleString(undefined, { maximumFractionDigits: 1 });
}

function renderFoods(foods) {
  count.textContent = foods.length;
  if (!foods.length) {
    list.innerHTML = '<p class="empty-state">Your saved labels will appear here.</p>';
    return;
  }
  list.innerHTML = foods.map((food) => `
    <article class="food-card">
      <h3>${escapeHtml(food.name)}</h3>
      <div class="food-meta">${escapeHtml(food.brand || 'Unbranded')} · ${escapeHtml(food.serving_size)}</div>
      <div class="food-values">
        <span>${formatNumber(food.calories)} kcal</span>
        <span>${formatNumber(food.protein_g)} g protein</span>
        <span>${formatNumber(food.carbohydrates_g)} g carbs</span>
        <span>${formatNumber(food.total_fat_g)} g fat</span>
      </div>
    </article>
  `).join('');
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#039;', '"': '&quot;' })[character]);
}

async function loadFoods() {
  message.textContent = 'Loading saved foods...';
  console.log('Fetching /api/foods');
  const response = await fetch('/api/foods');
  const data = await response.json();
  console.log('GET /api/foods response:', data);
  renderFoods(data.foods);
  message.textContent = data.foods.length ? `Loaded ${data.foods.length} food entries.` : 'No foods saved yet.';
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  message.textContent = 'Saving...';
  const payload = Object.fromEntries(new FormData(form).entries());
  for (const field of numberFields) {
    if (payload[field] === '') payload[field] = null;
    else if (payload[field] !== undefined) payload[field] = Number(payload[field]);
  }
  console.log('Submitting food payload:', payload);
  try {
    const response = await fetch('/api/foods', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    const data = await response.json();
    console.log('POST /api/foods result:', { status: response.status, data });
    if (!response.ok) throw new Error(data.error || 'Could not save food');
    form.reset();
    message.textContent = 'Saved to your library.';
    await loadFoods();
  } catch (error) {
    console.error('Save failed:', error);
    message.textContent = error.message;
  }
});

loadFoods().catch((error) => {
  console.error('Initial load failed:', error);
  message.textContent = 'The API is not available yet.';
});
