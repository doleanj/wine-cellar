<script>
  import { createEventDispatcher } from 'svelte';
  import Modal from './Modal.svelte';
  import { t, lang } from '$lib/stores/i18n.js';
  import { pairingItems } from '$lib/wine-reference.js';
  import { isFilled } from '$lib/elabel.js';

  // Compare what a scanned label / product page found with what the form holds now.
  export let title = '';
  export let rows = [];        // [{ key, value }]
  export let current = {};     // the form's current values
  export let notes = [];       // short info lines (existing wine, language of the text, ...)

  const dispatch = createEventDispatcher();

  const norm = v => (v === null || v === undefined || v === false ? '' : String(v).trim());

  // changed or new values first and ticked; identical ones last, unticked
  let items = rows
    .map(r => {
      const cur = current[r.key];
      const same = isFilled(cur) && norm(cur) === norm(r.value);
      return { ...r, cur, same, empty: !isFilled(cur), on: !same };
    })
    .sort((a, b) => Number(a.same) - Number(b.same));

  $: count = items.filter(i => i.on).length;

  function fmt(key, v, tr, language) {
    if (!isFilled(v) && v !== false) return '';
    if (typeof v === 'boolean') return v ? '✓' : '—';
    if (key === 'type') return tr(`type_${v === 'rosé' ? 'rose' : v}`);
    if (key === 'sweetness') return tr(`sweetness_${v}`);
    if (key === 'pairings') return pairingItems(v, language).map(p => `${p.icon} ${p.label}`).join(', ');
    return String(v);
  }

  const pick = fn => { items = items.map(i => ({ ...i, on: fn(i) })); };
</script>

<Modal variant="center" maxWidth="760px" zIndex={320} labelledby="fill-title" on:close={() => dispatch('close')}>
  <div class="panel">
    <header class="head">
      <div class="title" id="fill-title">{title}</div>
      <button class="x" type="button" on:click={() => dispatch('close')} aria-label={$t('preview_cancel')}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </header>

    {#each notes as n}<p class="note">{n}</p>{/each}

    <div class="quick">
      <span>{$t('preview_select')}:</span>
      <button type="button" on:click={() => pick(() => true)}>{$t('preview_all')}</button>
      <button type="button" on:click={() => pick(() => false)}>{$t('preview_none')}</button>
      <button type="button" on:click={() => pick(i => i.empty)}>{$t('preview_only_empty')}</button>
    </div>

    <div class="table" role="group" aria-label={title}>
      <div class="row hdr"><span></span><span>{$t('preview_field')}</span><span>{$t('preview_current')}</span><span>{$t('preview_new')}</span></div>
      {#each items as i (i.key)}
        <label class="row" class:same={i.same} class:on={i.on}>
          <input type="checkbox" bind:checked={i.on} />
          <span class="field">{$t('elabel_f_' + i.key)}{#if i.same} <em>({$t('preview_same')})</em>{/if}</span>
          <span class="cur"><b class="lbl">{$t('preview_current')}</b>
            {#if i.key === 'image_url' && i.cur}<img src={i.cur} alt="" />{:else}{fmt(i.key, i.cur, $t, $lang) || '—'}{/if}</span>
          <span class="new"><b class="lbl">{$t('preview_new')}</b>
            {#if i.key === 'image_url'}<img src={i.value} alt="" />{:else}{fmt(i.key, i.value, $t, $lang)}{/if}</span>
        </label>
      {/each}
    </div>

    <footer class="foot">
      <button type="button" class="btn secondary" on:click={() => dispatch('close')}>{$t('preview_cancel')}</button>
      <button type="button" class="btn primary" disabled={count === 0}
              on:click={() => dispatch('apply', items.filter(i => i.on))}>{$t('preview_apply')} ({count})</button>
    </footer>
  </div>
</Modal>

<style>
  .panel { display: flex; flex-direction: column; width: 100%; max-height: 88vh; min-height: 0; }
  .head { display: flex; align-items: center; justify-content: space-between; padding: 14px 18px; border-bottom: 1px solid var(--border); }
  .title { font-size: 16px; font-weight: 700; color: var(--primary); }
  .x { background: none; border: none; color: var(--text-muted); cursor: pointer; display: flex; padding: 4px; }
  .note { margin: 8px 18px 0; font-size: 12px; color: var(--text-muted); }
  .quick { display: flex; gap: 8px; align-items: center; padding: 10px 18px 6px; font-size: 12px; color: var(--text-muted); flex-wrap: wrap; }
  .quick button { background: none; border: 1px solid var(--border); border-radius: 999px; padding: 3px 10px; font-size: 12px; color: var(--text); cursor: pointer; }
  .quick button:hover { border-color: var(--primary); color: var(--primary); }

  .table { overflow-y: auto; padding: 0 18px 8px; min-height: 0; flex: 1 1 auto; }
  .row { display: grid; grid-template-columns: 26px 130px 1fr 1fr; gap: 10px; align-items: start; padding: 9px 6px; border-bottom: 1px solid var(--border); font-size: 13px; cursor: pointer; }
  .row.hdr { position: sticky; top: 0; background: var(--surface); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .04em; color: var(--text-muted); cursor: default; z-index: 1; }
  .row.on { background: color-mix(in srgb, var(--primary) 6%, transparent); }
  .row.same { opacity: .55; }
  .field { font-weight: 600; }
  .field em { font-weight: 400; font-style: normal; color: var(--text-muted); font-size: 11px; }
  .cur { color: var(--text-muted); }
  .new { color: var(--text); font-weight: 600; }
  .cur, .new { white-space: pre-wrap; word-break: break-word; max-height: 7.5em; overflow-y: auto; }
  .row img { max-width: 64px; max-height: 64px; border-radius: 6px; object-fit: cover; display: block; }
  .lbl { display: none; }

  .foot { display: flex; justify-content: flex-end; gap: 10px; padding: 12px 18px; border-top: 1px solid var(--border); background: var(--surface); }
  .btn { border-radius: 8px; padding: 9px 18px; font-size: 14px; font-weight: 600; cursor: pointer; border: 1px solid var(--border); }
  .btn.secondary { background: var(--surface); color: var(--text); }
  .btn.primary { background: var(--primary); border-color: var(--primary); color: #fff; }
  .btn.primary:disabled { opacity: .5; cursor: not-allowed; }

  @media (max-width: 640px) {
    .row { grid-template-columns: 26px 1fr; row-gap: 2px; }
    .row.hdr { display: none; }
    .field { grid-column: 2; }
    .cur, .new { grid-column: 2; }
    .lbl { display: inline-block; min-width: 64px; font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; }
    .foot .btn { flex: 1; }
  }
</style>
