<script>
  import { createEventDispatcher } from 'svelte';
  import { t, lang } from '$lib/stores/i18n.js';
  import Modal from './Modal.svelte';
  import TasteBadge from './TasteBadge.svelte';
  import { pairingItems } from '$lib/wine-reference.js';
  import { onMount } from 'svelte';
  import { regions, loadRegions, matchRegion } from '$lib/regions.js';

  onMount(loadRegions);
  $: regionMatch = matchRegion(wine, $regions);
  let mapOpen = false;

  export let wine;
  export let editable = false;
  export let customFields = [];

  const dispatch = createEventDispatcher();

  $: typeLabel = {
    red: $t('type_red'), white: $t('type_white'), rosé: $t('type_rose'),
    sparkling: $t('type_sparkling'), dessert: $t('type_dessert'), other: $t('type_other')
  };
  $: bodyMap = { 'Light-bodied': $t('body_light'), 'Medium-bodied': $t('body_medium'), 'Full-bodied': $t('body_full') };
  $: acidMap = { 'Low': $t('acidity_low'), 'Medium': $t('acidity_medium'), 'High': $t('acidity_high') };

  function stars(r) {
    if (!r) return '';
    return '★'.repeat(r) + '☆'.repeat(5 - r);
  }

  let showLightbox = false;

  function openLightbox() { showLightbox = true; }
</script>

{#if showLightbox}
  <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
  <div class="lightbox" on:click={() => showLightbox = false}>
    <img src={wine.image_url} alt={wine.name} class="lightbox-img" />
  </div>
{/if}

<Modal variant="center" maxWidth="780px" labelledby="wine-detail-title" on:close={() => dispatch('close')}>
  <div class="panel">

    <!-- Image -->
    <div class="image-side">
      {#if wine.image_url}
        <button type="button" class="wine-img-btn" on:click={openLightbox}>
          <img src={wine.image_url} alt={wine.name} class="wine-img zoomable" />
        </button>
      {:else}
        <div class="img-placeholder">
          <svg viewBox="0 0 64 100" fill="none">
            <path d="M24 4h16v20c0 8-4 14-4 22v44H28V46c0-8-4-14-4-22V4z" fill="currentColor" opacity=".15"/>
            <path d="M26 4h12v18c0 9-5 15-5 24v44H31V46c0-9-5-15-5-24V4z" fill="currentColor" opacity=".3"/>
            <rect x="22" y="2" width="20" height="6" rx="2" fill="currentColor" opacity=".4"/>
          </svg>
        </div>
      {/if}
      <span class="type-badge type-{wine.type}">{typeLabel[wine.type] || wine.type}</span>
      {#if wine.by_glass}
        <span class="glass-badge">{$t('kiosk_by_glass')}</span>
      {/if}
    </div>

    <!-- Details -->
    <div class="detail-side">
      <div class="detail-header-btns">
        {#if editable}
          <button class="edit-btn fav-btn" class:fav-on={wine.favorite} aria-pressed={!!wine.favorite}
            on:click={() => dispatch('favorite', wine)}
            title={wine.favorite ? $t('fav_remove') : $t('fav_add')} aria-label={wine.favorite ? $t('fav_remove') : $t('fav_add')}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill={wine.favorite ? 'currentColor' : 'none'} stroke="currentColor" stroke-width="2" stroke-linejoin="round">
              <path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/>
            </svg>
          </button>
          <button class="edit-btn" on:click={() => dispatch('edit', wine)} title={$t('action_edit')} aria-label={$t('action_edit')}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
          </button>
        {/if}
        <button class="close-btn" on:click={() => dispatch('close')} aria-label={$t('action_close')}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <div class="detail-scroll">
        <h2 class="wine-name" id="wine-detail-title">{wine.name}</h2>

        {#if wine.producer}
          <p class="producer">{wine.producer}</p>
        {/if}

        {#if wine.rating}
          <div class="stars">{stars(wine.rating)}</div>
        {/if}

        <div class="chips">
          {#if wine.vintage}
            <span class="chip chip-year">{wine.vintage}</span>
          {/if}
          {#if wine.region}
            <span class="chip">{wine.region}</span>
          {/if}
          {#if wine.country}
            <span class="chip">{wine.country}</span>
          {/if}
          {#if wine.grape}
            <span class="chip">{wine.grape}</span>
          {/if}
        </div>

        {#if wine.body || wine.acidity || wine.alcohol}
          <div class="props">
            {#if wine.body}
              <div class="prop-item">
                <span class="prop-label">{$t('detail_body')}</span>
                <span class="prop-val">{bodyMap[wine.body] || wine.body}</span>
              </div>
            {/if}
            {#if wine.acidity}
              <div class="prop-item">
                <span class="prop-label">{$t('detail_acidity')}</span>
                <span class="prop-val">{acidMap[wine.acidity] || wine.acidity}</span>
              </div>
            {/if}
            {#if wine.alcohol}
              <div class="prop-item">
                <span class="prop-label">{$t('detail_alcohol')}</span>
                <span class="prop-val">{wine.alcohol}%</span>
              </div>
            {/if}
          </div>
        {/if}

        {#if wine.description}
          <p class="description">{wine.description}</p>
        {/if}

        {#if wine.keep_until_years || wine.serving_temp || wine.purchase_date || wine.tasting}
          <div class="elabel">
            {#if wine.keep_until_years && wine.vintage}<p class="elabel-line">{$t('detail_keep_until')}: {wine.vintage + wine.keep_until_years}</p>{/if}
            {#if wine.serving_temp}<p class="elabel-line">{$t('detail_serving_temp')}: {wine.serving_temp} °C</p>{/if}
            {#if wine.purchase_date}<p class="elabel-line">{$t('detail_purchase_date')}: {wine.purchase_date}</p>{/if}
            {#if wine.tasting}<p class="elabel-line" style="white-space: pre-line">{wine.tasting}</p>{/if}
          </div>
        {/if}

        {#if wine.ingredients || wine.energy_kcal_100ml || wine.bottled_by || wine.elabel_url}
          <div class="elabel">
            <span class="prop-label">{$t('detail_elabel')}</span>
            {#if wine.ingredients}
              <p class="elabel-line">{$t('detail_ingredients')}: {wine.ingredients}{#if wine.sulphites} · {$t('detail_sulphites')}{/if}</p>
            {/if}
            {#if wine.energy_kcal_100ml || wine.sugar_g_100ml || wine.carbs_g_100ml}
              <p class="elabel-line">{$t('detail_nutrition')}:
                {#if wine.energy_kcal_100ml}{wine.energy_kcal_100ml} kcal{/if}{#if wine.carbs_g_100ml} · {wine.carbs_g_100ml} g {$t('elabel_f_carbs_g_100ml').split(' ')[0].toLowerCase()}{/if}{#if wine.sugar_g_100ml} · {wine.sugar_g_100ml} g {$t('elabel_f_sugar_g_100ml').split(' ')[0].toLowerCase()}{/if}
              </p>
            {/if}
            {#if wine.bottled_by}<p class="elabel-line">{$t('detail_bottled_by')}: {wine.bottled_by}</p>{/if}
            {#if wine.elabel_url}<a class="elabel-line" href={wine.elabel_url} target="_blank" rel="noopener noreferrer">{$t('detail_elabel_open')}</a>{/if}
          </div>
        {/if}

        {#if wine.profile_fruit || wine.profile_personality || wine.sweetness}
          <div class="profile">
            <TasteBadge fruit={wine.profile_fruit} personality={wine.profile_personality} size={88} />
            {#if wine.sweetness}
              <span class="chip">{$t(`sweetness_${wine.sweetness}`)}</span>
            {/if}
          </div>
        {/if}

        {#if wine.pairings}
          <div class="pairings">
            <span class="prop-label">{$t('detail_pairings')}</span>
            <div class="pair-chips">
              {#each pairingItems(wine.pairings, $lang) as p}
                <span class="pair-chip" title={p.known ? p.title : p.label}><span aria-hidden="true">{p.icon}</span> {p.label}</span>
              {/each}
            </div>
          </div>
        {/if}

        {#if regionMatch}
          <div class="region">
            <span class="prop-label">{$t('detail_region')}: {regionMatch.region.name}{#if regionMatch.appellation} · {regionMatch.appellation}{/if}</span>
            {#if regionMatch.region.image_url}
              <button type="button" class="region-map" on:click={() => mapOpen = true} title={$t('detail_region_enlarge')}>
                <img src={regionMatch.region.image_url} alt={regionMatch.region.name} loading="lazy" />
              </button>
            {/if}
            {#if regionMatch.region.intro}<p class="region-intro">{regionMatch.region.intro}</p>{/if}
          </div>
        {/if}

        {#if wine.url}
          <a class="wine-link" href={wine.url} target="_blank" rel="noopener noreferrer">🔗 {$t('detail_link')}</a>
        {/if}

        {#if wine.notes}
          <div class="notes">
            <span class="prop-label">{$t('detail_notes')}</span>
            <p>{wine.notes}</p>
          </div>
        {/if}

        {#if customFields.length > 0 && wine.custom_values}
          {@const visibleFields = customFields.filter(cf => wine.custom_values[cf.key])}
          {#if visibleFields.length > 0}
            <div class="custom-fields">
              <span class="prop-label">{$t('custom_fields_section')}</span>
              <div class="custom-grid">
                {#each visibleFields as cf (cf.key)}
                  <div class="custom-item">
                    <span class="custom-label">{$lang === 'de' ? cf.label_de : (cf.label_en || cf.label_de)}</span>
                    <span class="custom-val">{wine.custom_values[cf.key]}</span>
                  </div>
                {/each}
              </div>
            </div>
          {/if}
        {/if}

        <div class="footer-row">
          {#if wine.price}
            <span class="price">{wine.price.toFixed(2)} € <span class="price-label">{$t('detail_per_bottle')}</span></span>
          {/if}
          {#if wine.by_glass && wine.price_per_glass}
            <span class="price glass-price">
              {wine.price_per_glass.toFixed(2)} € <span class="price-label">{$t('detail_per_glass')}</span>
            </span>
          {/if}
        </div>
      </div>
    </div>

  </div>
</Modal>

{#if mapOpen && regionMatch?.region.image_url}
  <button type="button" class="map-overlay" on:click={() => mapOpen = false} aria-label={$t('detail_region_close')}>
    <img src={regionMatch.region.image_url} alt={regionMatch.region.name} />
  </button>
{/if}

<style>
  .panel {
    display: flex;
    width: 100%;
    /* fill the modal panel but never outgrow it, so .detail-scroll can scroll */
    flex: 1 1 auto;
    min-height: 0;
    max-height: 100%;
  }

  /* ── Image side ── */
  .image-side {
    width: 42%;
    flex-shrink: 0;
    background: var(--surface-2);
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .wine-img-btn {
    width: 100%;
    height: 100%;
    border: none;
    background: none;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .wine-img-btn:focus-visible {
    outline: 2.5px solid var(--primary);
    outline-offset: -2px;
  }
  .wine-img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    padding: 24px;
  }
  .zoomable { cursor: zoom-in; }

  .lightbox {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.92);
    z-index: 500;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: zoom-out;
    animation: lbIn 0.18s ease;
  }
  @keyframes lbIn {
    from { opacity: 0; }
    to   { opacity: 1; }
  }
  .lightbox-img {
    max-width: 92vw;
    max-height: 92vh;
    object-fit: contain;
    border-radius: 8px;
    box-shadow: 0 8px 48px rgba(0,0,0,0.6);
  }

  .img-placeholder {
    color: var(--primary);
    width: 100px;
    height: 100px;
    opacity: 0.25;
  }

  .type-badge {
    position: absolute;
    bottom: 16px;
    left: 16px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    color: white;
    letter-spacing: 0.3px;
  }
  .type-red      { background: var(--red); }
  .type-white    { background: var(--white-wine); }
  .type-rosé     { background: var(--rose); }
  .type-sparkling{ background: var(--sparkling); }
  .type-dessert  { background: var(--dessert); }
  .type-other    { background: var(--other); }

  .glass-badge {
    position: absolute;
    bottom: 16px;
    right: 16px;
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    color: white;
    background: rgba(20, 20, 20, 0.65);
    backdrop-filter: blur(4px);
  }

  /* ── Detail side ── */
  .detail-side {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
    min-height: 0;
    position: relative;
    overflow: hidden;
  }

  .detail-header-btns {
    position: absolute;
    top: 14px;
    right: 14px;
    display: flex;
    gap: 6px;
    z-index: 1;
  }
  .close-btn, .edit-btn {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    border: none;
    background: var(--surface-2);
    color: var(--text-muted);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.15s, color 0.15s;
  }
  .close-btn:hover { background: var(--border); color: var(--text); }
  .edit-btn:hover { background: var(--primary); color: white; }
  .fav-btn.fav-on { color: var(--primary); }
  .fav-btn.fav-on:hover { color: white; }

  .detail-scroll {
    padding: 28px 28px 24px;
    overflow-y: auto;
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  .wine-name {
    font-size: 22px;
    font-weight: 800;
    color: var(--text);
    line-height: 1.25;
    padding-right: 36px;
  }

  .producer {
    font-size: 14px;
    color: var(--text-muted);
    margin-top: -8px;
  }

  .stars {
    font-size: 20px;
    color: var(--accent);
    letter-spacing: 2px;
  }

  .chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .chip {
    font-size: 12px;
    background: var(--surface-2);
    color: var(--text-muted);
    padding: 3px 10px;
    border-radius: 12px;
    border: 1px solid var(--border);
  }
  .chip-year {
    background: rgba(123, 29, 63, 0.08);
    color: var(--primary);
    border-color: rgba(123, 29, 63, 0.2);
    font-weight: 600;
  }

  .props {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
  }
  .prop-item {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .prop-label {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .prop-val {
    font-size: 14px;
    font-weight: 600;
    color: var(--text);
  }

  .description {
    font-size: 14px;
    color: var(--text-muted);
    line-height: 1.6;
    border-left: 3px solid var(--border);
    padding-left: 12px;
  }

  .region { margin-top: 12px; }
  .region-map { display: block; width: 100%; padding: 0; margin-top: 6px; border: 1px solid var(--border); border-radius: 10px; overflow: hidden; background: none; cursor: zoom-in; }
  .region-map img { display: block; width: 100%; height: auto; }
  .region-intro { margin: 8px 0 0; font-size: 13px; line-height: 1.5; color: var(--text-muted); }
  .map-overlay { position: fixed; inset: 0; z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 16px; background: rgba(0, 0, 0, 0.8); cursor: zoom-out; border: none; width: 100%; }
  .map-overlay img { max-width: 100%; max-height: 100%; border-radius: 8px; }
  .profile { display: flex; align-items: center; gap: 12px; margin: 10px 0; }
  .pair-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
  .pair-chip { padding: 3px 10px; border: 1px solid var(--border); border-radius: 999px; font-size: 12px; background: var(--surface-2); }
  .wine-link { display: inline-block; margin-top: 8px; color: var(--primary); font-size: 13px; text-decoration: none; }
  .wine-link:hover { text-decoration: underline; }
  .pairings, .notes {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .pairings p, .notes p {
    font-size: 13px;
    color: var(--text-muted);
    line-height: 1.5;
  }

  .custom-fields { display: flex; flex-direction: column; gap: 8px; }
  .custom-grid { display: flex; flex-direction: column; gap: 6px; }
  .custom-item { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }
  .custom-label { font-size: 13px; color: var(--text-muted); }
  .custom-val { font-size: 13px; font-weight: 600; color: var(--text); text-align: right; }

  .footer-row {
    display: flex;
    align-items: center;
    gap: 16px;
    padding-top: 8px;
    border-top: 1px solid var(--border);
    margin-top: auto;
  }
  .price {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 20px;
    font-weight: 700;
    color: var(--primary);
  }
  .price-label {
    font-size: 12px;
    font-weight: 500;
    opacity: 0.7;
  }
  .glass-price {
    font-size: 18px;
  }
  .qty {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 13px;
    color: var(--text-muted);
  }

  /* Mobile: stack vertically */
  @media (max-width: 600px) {
    .panel {
      flex-direction: column;
      max-height: 95vh;
    }
    .image-side {
      width: 100%;
      height: 240px;
    }
    .detail-scroll {
      padding: 20px;
    }
  }
  .elabel { margin: 10px 0; }
  .elabel-line { margin: 3px 0; font-size: 13px; color: var(--text-muted); display: block; }
</style>
