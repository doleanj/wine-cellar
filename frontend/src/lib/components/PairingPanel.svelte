<script>
  import { createEventDispatcher } from 'svelte';
  import Modal from './Modal.svelte';
  import { t, lang } from '$lib/stores/i18n.js';
  import { PAIRINGS, scoreWine } from '$lib/wine-reference.js';

  export let wines = [];
  export let drinkRules = [];

  const dispatch = createEventDispatcher();

  let selected = [];
  let readyOnly = false;
  let favOnly = false;

  const label = key => { const p = PAIRINGS.find(x => x.key === key); return p ? (p[$lang] || p.en) : key; };
  const icon = key => PAIRINGS.find(x => x.key === key)?.icon || '';

  function toggle(key) {
    selected = selected.includes(key) ? selected.filter(k => k !== key) : [...selected, key];
  }

  $: ranked = selected.length
    ? wines
        .filter(w => (w.quantity || 0) > 0 && (!favOnly || w.favorite))
        .map(w => scoreWine(w, selected, drinkRules))
        .filter(Boolean)
        .filter(r => !readyOnly || r.status === 'ready')
        .sort((a, b) => b.score - a.score || (a.wine.name || '').localeCompare(b.wine.name || ''))
    : [];
  $: best = ranked.filter(r => !r.fallback);
  $: suggested = ranked.filter(r => r.fallback);
  $: hasRules = drinkRules.length > 0;
</script>

<Modal variant="center" maxWidth="760px" labelledby="pairing-title" on:close={() => dispatch('close')}>
  <div class="panel">
    <header class="panel-header">
      <div>
        <div class="panel-title" id="pairing-title">{$t('pairing_title')}</div>
        <div class="sub">{$t('pairing_sub')}</div>
      </div>
      <button class="close-btn" on:click={() => dispatch('close')} aria-label={$t('action_close')}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </header>

    <div class="body">
      <div class="chips" role="group" aria-label={$t('pairing_title')}>
        {#each PAIRINGS as p (p.key)}
          <button type="button" class="chip" class:on={selected.includes(p.key)} aria-pressed={selected.includes(p.key)}
            title={p.fr} on:click={() => toggle(p.key)}>
            <span aria-hidden="true">{p.icon}</span> {p[$lang] || p.en}
          </button>
        {/each}
      </div>

      <div class="filters">
        {#if hasRules}
          <label class="flt"><input type="checkbox" bind:checked={readyOnly} /> {$t('pairing_only_ready')}</label>
        {/if}
        <label class="flt"><input type="checkbox" bind:checked={favOnly} /> {$t('pairing_only_fav')}</label>
        {#if selected.length}
          <button type="button" class="clear" on:click={() => selected = []}>{$t('pairing_clear')}</button>
        {/if}
      </div>

      {#if !selected.length}
        <p class="note">{$t('pairing_pick')}</p>
      {:else if !ranked.length}
        <p class="note">{$t('pairing_empty')}</p>
      {:else}
        {#if best.length}
          <h3>{$t('pairing_best')} <span class="count">{best.length}</span></h3>
          <ul class="results">
            {#each best as r (r.wine.id)}
              <li><button type="button" class="row" on:click={() => dispatch('selectWine', r.wine)}>
                {#if r.wine.image_url}<img src={r.wine.image_url} alt="" loading="lazy" />{:else}<span class="ph"></span>{/if}
                <span class="main">
                  <span class="name">{r.wine.name}{#if r.wine.vintage} <span class="vint">{r.wine.vintage}</span>{/if}</span>
                  <span class="prod">{r.wine.producer}</span>
                  <span class="why">
                    {#each r.matched as k}<span class="tag">{icon(k)} {label(k)}</span>{/each}
                    {#if r.status}<span class="drink drink-{r.status}">{$t('drink_' + r.status)}</span>{/if}
                    {#if r.wine.favorite}<span class="drink">♥</span>{/if}
                  </span>
                </span>
                <span class="qty">{r.wine.quantity}×</span>
              </button></li>
            {/each}
          </ul>
        {/if}
        {#if suggested.length}
          <h3>{$t('pairing_suggested')} <span class="count">{suggested.length}</span></h3>
          <p class="hint">{$t('pairing_suggested_hint')}</p>
          <ul class="results">
            {#each suggested as r (r.wine.id)}
              <li><button type="button" class="row" on:click={() => dispatch('selectWine', r.wine)}>
                {#if r.wine.image_url}<img src={r.wine.image_url} alt="" loading="lazy" />{:else}<span class="ph"></span>{/if}
                <span class="main">
                  <span class="name">{r.wine.name}{#if r.wine.vintage} <span class="vint">{r.wine.vintage}</span>{/if}</span>
                  <span class="prod">{r.wine.producer}</span>
                  <span class="why">
                    <span class="tag soft">{$t('type_' + (r.wine.type === 'rosé' ? 'rose' : r.wine.type))}</span>
                    {#if r.status}<span class="drink drink-{r.status}">{$t('drink_' + r.status)}</span>{/if}
                  </span>
                </span>
                <span class="qty">{r.wine.quantity}×</span>
              </button></li>
            {/each}
          </ul>
        {/if}
      {/if}
    </div>
  </div>
</Modal>

<style>
  .panel { display: flex; flex-direction: column; width: 100%; max-height: 88vh; }
  .panel-header { display: flex; align-items: flex-start; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid var(--border); flex-shrink: 0; }
  .panel-title { font-size: 16px; font-weight: 700; color: var(--primary); }
  .sub { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
  .close-btn { background: none; border: none; color: var(--text-muted); display: flex; padding: 4px; border-radius: 6px; cursor: pointer; }
  .body { flex: 1; overflow-y: auto; padding: 16px 20px 22px; }

  .chips { display: flex; flex-wrap: wrap; gap: 6px; }
  .chip { display: inline-flex; align-items: center; gap: 5px; padding: 5px 10px; border: 1.5px solid var(--border); border-radius: 999px; background: var(--bg); color: var(--text-muted); font-size: 12px; cursor: pointer; }
  .chip:hover:not(.on) { background: var(--surface-2); color: var(--text); }
  .chip.on { background: var(--primary); border-color: var(--primary); color: #fff; font-weight: 600; }

  .filters { display: flex; align-items: center; gap: 16px; margin: 12px 0 4px; font-size: 12px; color: var(--text-muted); }
  .flt { display: inline-flex; align-items: center; gap: 6px; cursor: pointer; }
  .clear { margin-left: auto; background: none; border: none; color: var(--primary); text-decoration: underline; cursor: pointer; font-size: 12px; }

  h3 { margin: 16px 0 6px; font-size: 13px; color: var(--text); }
  .count { background: var(--primary); color: #fff; border-radius: 999px; padding: 1px 7px; font-size: 11px; margin-left: 4px; }
  .note { text-align: center; color: var(--text-muted); font-size: 14px; margin: 28px 0; }
  .hint { margin: 0 0 6px; font-size: 12px; color: var(--text-muted); }

  .results { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--border); }
  .results li + li { border-top: 1px solid var(--border); }
  .row { width: 100%; display: flex; align-items: center; gap: 12px; padding: 8px 4px; background: none; border: none; text-align: left; color: var(--text); cursor: pointer; }
  .row:hover { background: var(--surface-2); }
  .row img, .ph { width: 34px; height: 52px; object-fit: contain; flex-shrink: 0; border-radius: 4px; background: var(--surface-2); }
  .main { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
  .name { font-weight: 600; font-size: 14px; }
  .vint { color: var(--text-muted); font-weight: 400; }
  .prod { font-size: 12px; color: var(--text-muted); }
  .why { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 2px; }
  .tag { font-size: 11px; padding: 1px 8px; border-radius: 999px; background: rgba(123, 29, 63, 0.1); color: var(--primary); }
  .tag.soft { background: var(--surface-2); color: var(--text-muted); }
  .drink { font-size: 11px; padding: 1px 8px; border-radius: 999px; background: var(--surface-2); color: var(--text-muted); }
  .drink-ready { background: #dff3e3; color: #1d6b32; }
  .drink-young { background: #deeaf7; color: #25588c; }
  .drink-late { background: #fbe9cf; color: #8a5a10; }
  .drink-past { background: #f6d9d6; color: #8c2a20; }
  .qty { color: var(--primary); font-weight: 700; font-size: 13px; }
</style>
