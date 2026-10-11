<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import Modal from './Modal.svelte';
  import { t } from '$lib/stores/i18n.js';
  import { regions, loadRegions, matchRegion } from '$lib/regions.js';

  export let wines = [];

  const dispatch = createEventDispatcher();

  onMount(loadRegions);

  const norm = s => (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();

  // wines per region key, and which appellations of that region hold at least one wine
  $: byRegion = (() => {
    const out = {};
    for (const w of wines) {
      const m = matchRegion(w, $regions);
      if (!m) continue;
      const e = (out[m.region.key] ||= { wines: [], apps: new Set() });
      e.wines.push(w);
      if (m.appellation) e.apps.add(m.appellation);
    }
    return out;
  })();

  $: matched = Object.values(byRegion).reduce((n, e) => n + e.wines.length, 0);

  let open = null;      // region key whose wines are expanded
  let enlarged = null;  // region shown full-size

  const bottles = list => list.reduce((n, w) => n + (w.quantity || 0), 0);
</script>

<Modal variant="center" maxWidth="900px" labelledby="regions-title" on:close={() => dispatch('close')}>
  <div class="panel">
    <header class="panel-header">
      <div class="panel-title" id="regions-title">{$t('regions_title')}</div>
      <button class="close-btn" on:click={() => dispatch('close')} aria-label={$t('modal_cancel')}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </header>

    <div class="body">
      {#each $regions as r (r.key)}
        {@const e = byRegion[r.key]}
        <section class="region" class:empty={!e}>
          <div class="head">
            <h3>{r.name}</h3>
            {#if e}
              <button type="button" class="count" on:click={() => open = open === r.key ? null : r.key} aria-expanded={open === r.key}>
                {e.wines.length} · {bottles(e.wines)} {$t('regions_bottles')}
              </button>
            {:else}
              <span class="none">{$t('regions_none')}</span>
            {/if}
          </div>

          {#if r.image_url}
            <button type="button" class="map" on:click={() => enlarged = r} title={$t('detail_region_enlarge')}>
              <img src={r.image_url} alt={r.name} loading="lazy" />
            </button>
          {/if}
          {#if r.intro}<p class="intro">{r.intro}</p>{/if}

          {#if r.appellations.length}
            <div class="apps">
              {#each r.appellations as a}
                <span class="app" class:has={e && e.apps.has(a)}>{a}</span>
              {/each}
            </div>
          {/if}

          {#if e && open === r.key}
            <ul class="wines">
              {#each e.wines as w (w.id)}
                <li>
                  <button type="button" on:click={() => dispatch('selectWine', w)}>
                    <span class="wname">{w.name}{#if w.vintage} <span class="vint">{w.vintage}</span>{/if}</span>
                    <span class="q">{w.quantity}×</span>
                  </button>
                </li>
              {/each}
            </ul>
          {/if}
        </section>
      {/each}
      {#if $regions.length === 0}
        <p class="note">{$t('regions_loading')}</p>
      {/if}
    </div>

    <footer class="foot">{matched}/{wines.length} {$t('regions_matched')}</footer>
  </div>
</Modal>

{#if enlarged}
  <button type="button" class="overlay" on:click={() => enlarged = null} aria-label={$t('detail_region_close')}>
    <img src={enlarged.image_url} alt={enlarged.name} />
  </button>
{/if}

<style>
  .panel { display: flex; flex-direction: column; width: 100%; height: 100%; max-height: 85vh; }
  .panel-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid var(--border); flex-shrink: 0; }
  .panel-title { font-size: 16px; font-weight: 700; color: var(--primary); }
  .close-btn { background: none; border: none; color: var(--text-muted); display: flex; padding: 4px; border-radius: 6px; cursor: pointer; }
  .close-btn:hover { color: var(--text); }

  .body { flex: 1; overflow-y: auto; padding: 16px 20px; display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 16px; align-content: start; }
  .region { border: 1px solid var(--border); border-radius: 12px; padding: 14px; background: var(--surface); display: flex; flex-direction: column; gap: 10px; }
  .region.empty { opacity: 0.8; }
  .head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
  h3 { margin: 0; font-size: 15px; color: var(--text); }
  .count { background: var(--primary); color: #fff; border: none; border-radius: 999px; padding: 3px 10px; font-size: 12px; font-weight: 600; cursor: pointer; }
  .none { font-size: 12px; color: var(--text-muted); }

  .map { display: block; width: 100%; padding: 0; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; background: none; cursor: zoom-in; }
  .map img { display: block; width: 100%; height: auto; }
  .intro { margin: 0; font-size: 13px; line-height: 1.5; color: var(--text-muted); }

  .apps { display: flex; flex-wrap: wrap; gap: 5px; }
  .app { padding: 2px 8px; border-radius: 999px; background: var(--surface-2); color: var(--text-muted); font-size: 11px; }
  .app.has { background: var(--primary); color: #fff; font-weight: 600; }

  .wines { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--border); }
  .wines li + li { border-top: 1px solid var(--border); }
  .wines button { width: 100%; display: flex; justify-content: space-between; gap: 10px; padding: 7px 4px; background: none; border: none; color: var(--text); font-size: 13px; cursor: pointer; text-align: left; }
  .wines button:hover { background: var(--surface-2); }
  .vint { color: var(--text-muted); }
  .q { color: var(--primary); font-weight: 700; }

  .note { grid-column: 1 / -1; text-align: center; color: var(--text-muted); font-size: 14px; }
  .foot { padding: 10px 20px; border-top: 1px solid var(--border); font-size: 12px; color: var(--text-muted); flex-shrink: 0; }

  .overlay { position: fixed; inset: 0; z-index: 1100; display: flex; align-items: center; justify-content: center; padding: 16px; background: rgba(0, 0, 0, 0.8); border: none; width: 100%; cursor: zoom-out; }
  .overlay img { max-width: 100%; max-height: 100%; border-radius: 8px; }
</style>
