<script>
  // Add several wines at once from product links (an order, a cart, a list of tips).
  // Each page is read with "fill from link"; a bottle already known (same EAN or link) gets the
  // bottles added instead of a duplicate, and a wished bottle bought this way leaves the wishlist.
  import { createEventDispatcher } from 'svelte';
  import Modal from './Modal.svelte';
  import { fillFromUrl, uploadFromUrl, createWine, updateWine } from '$lib/api.js';
  import { t } from '$lib/stores/i18n.js';

  export let wines = [];            // the main page list (stock + wishlist)
  export let mode = 'cellar';       // 'cellar' | 'wishlist'

  const dispatch = createEventDispatcher();

  let text = '';
  let rows = [];                    // { url, status: 'loading'|'ok'|'error', fields, existing, include, qty, target }
  let reading = false;
  let saving = false;
  let doneCount = 0;

  $: links = [...new Set((text.match(/https:\/\/[^\s"'<>]+/g) || []).map(u => u.replace(/[),.;]+$/, '')))];
  $: ready = rows.filter(r => r.status === 'ok' && r.include);

  async function readPages() {
    reading = true;
    rows = links.map(url => ({ url, status: 'loading', include: true, qty: mode === 'cellar' ? 1 : 0, target: null }));
    for (let i = 0; i < rows.length; i++) {
      try {
        const res = await fillFromUrl(rows[i].url);
        const f = res.fields || {};
        const known = res.existing_wine_id ? wines.find(w => w.id === res.existing_wine_id) || { id: res.existing_wine_id } : null;
        rows[i] = { ...rows[i], status: 'ok', fields: f, existing: known, target: f.price ?? null,
                    include: !(mode === 'wishlist' && known?.wishlist) };
      } catch {
        rows[i] = { ...rows[i], status: 'error', include: false };
      }
      rows = rows;
    }
    reading = false;
  }

  function note(r) {
    if (!r.existing) return $t('links_new');
    if (mode === 'wishlist') return r.existing.wishlist ? $t('links_already_wished') : $t('links_known_add_wish');
    return r.existing.wishlist ? $t('links_wish_bought') : $t('links_known_add_stock').replace('{n}', r.existing.quantity ?? 0);
  }

  async function addAll() {
    saving = true; doneCount = 0;
    const today = new Date().toISOString().slice(0, 10);
    const failed = [];
    for (const r of ready) {
      const qty = Math.max(0, parseInt(r.qty) || 0);
      const target = r.target === '' || r.target == null ? null : parseFloat(r.target);
      try {
        if (r.existing) {
          if (mode === 'wishlist') {
            await updateWine(r.existing.id, { wishlist: true, target_price: target });
          } else {
            await updateWine(r.existing.id, { quantity: (r.existing.quantity || 0) + qty, wishlist: false, purchase_date: today });
          }
        } else {
          const f = { ...r.fields };
          for (const k of Object.keys(f)) if (f[k] === null || f[k] === '') delete f[k];
          if (f.image_url) {
            try { f.image_url = (await uploadFromUrl(f.image_url)).url; } catch { delete f.image_url; }
          }
          await createWine(mode === 'wishlist'
            ? { ...f, url: f.url || r.url, quantity: 0, wishlist: true, target_price: target }
            : { ...f, url: f.url || r.url, quantity: qty || 1, purchase_date: today });
        }
        doneCount += 1;
      } catch {
        failed.push(r.url);
      }
    }
    saving = false;
    dispatch('done', { added: doneCount, failed: failed.length });
  }
</script>

<Modal variant="center" maxWidth="720px" zIndex={320} labelledby="links-title" on:close={() => !saving && dispatch('close')}>
  <div class="panel">
    <header class="head">
      <div class="title" id="links-title">{mode === 'wishlist' ? $t('links_title_wishlist') : $t('links_title_cellar')}</div>
      <button class="x" type="button" on:click={() => dispatch('close')} aria-label={$t('links_close')} disabled={saving}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </header>

    <div class="body">
      <div class="modes" role="group" aria-label={$t('links_mode')}>
        <button type="button" class:on={mode === 'cellar'} on:click={() => { mode = 'cellar'; rows = []; }} disabled={reading || saving}>{$t('links_mode_cellar')}</button>
        <button type="button" class:on={mode === 'wishlist'} on:click={() => { mode = 'wishlist'; rows = []; }} disabled={reading || saving}>{$t('links_mode_wishlist')}</button>
      </div>

      {#if rows.length === 0}
        <p class="intro">{$t('links_intro')}</p>
        <textarea rows="7" bind:value={text} placeholder="https://www.e.leclerc/fp/…"></textarea>
        <p class="count">{$t('links_found').replace('{n}', links.length)}</p>
      {:else}
        <ul class="rows">
          {#each rows as r (r.url)}
            <li class="row" class:muted={!r.include}>
              <input type="checkbox" bind:checked={r.include} disabled={r.status !== 'ok' || saving} aria-label={$t('links_include')} />
              {#if r.status === 'ok' && r.fields.image_url}
                <img src={r.fields.image_url} alt="" loading="lazy" />
              {:else}
                <span class="ph"></span>
              {/if}
              <div class="info">
                {#if r.status === 'loading'}
                  <div class="name">{$t('links_reading')}</div><div class="sub">{r.url}</div>
                {:else if r.status === 'error'}
                  <div class="name err">{$t('links_error')}</div><div class="sub">{r.url}</div>
                {:else}
                  <div class="name">{r.fields.name}{r.fields.vintage ? ` ${r.fields.vintage}` : ''}</div>
                  <div class="sub">{[r.fields.region, r.fields.price != null ? `${r.fields.price.toFixed(2)} €` : ''].filter(Boolean).join(' · ')}</div>
                  <div class="note" class:known={r.existing}>{note(r)}</div>
                {/if}
              </div>
              {#if r.status === 'ok'}
                {#if mode === 'cellar'}
                  <label class="num">{$t('links_qty')}<input type="number" min="1" bind:value={r.qty} disabled={saving} /></label>
                {:else}
                  <label class="num">{$t('links_target')}<input type="number" min="0" step="0.01" bind:value={r.target} disabled={saving} /></label>
                {/if}
              {/if}
            </li>
          {/each}
        </ul>
      {/if}
    </div>

    <footer class="foot">
      {#if rows.length === 0}
        <button type="button" class="btn" on:click={readPages} disabled={!links.length}>{$t('links_read').replace('{n}', links.length)}</button>
      {:else}
        <button type="button" class="btn ghost" on:click={() => rows = []} disabled={reading || saving}>{$t('links_back')}</button>
        <button type="button" class="btn" on:click={addAll} disabled={reading || saving || !ready.length}>
          {saving ? `${doneCount}/${ready.length}…` : (mode === 'wishlist' ? $t('links_add_wishlist') : $t('links_add_cellar')).replace('{n}', ready.length)}
        </button>
      {/if}
    </footer>
  </div>
</Modal>

<style>
  .panel { display: flex; flex-direction: column; width: 100%; max-height: 85vh; min-height: 0; }
  .head { display: flex; align-items: center; justify-content: space-between; padding: 14px 18px; border-bottom: 1px solid var(--border); }
  .title { font-size: 16px; font-weight: 700; color: var(--primary); }
  .x { background: none; border: none; color: var(--text-muted); cursor: pointer; display: flex; padding: 4px; }
  .body { overflow-y: auto; padding: 12px 18px; flex: 1 1 auto; min-height: 0; }
  .modes { display: inline-flex; border: 1px solid var(--border); border-radius: 999px; overflow: hidden; margin-bottom: 10px; }
  .modes button { background: none; border: none; padding: 6px 14px; font-size: 13px; cursor: pointer; color: var(--text-muted); }
  .modes button.on { background: var(--primary); color: #fff; }
  .intro, .count { font-size: 13px; color: var(--text-muted); margin: 4px 0 8px; }
  textarea { width: 100%; box-sizing: border-box; font: inherit; font-size: 13px; padding: 8px 10px; border: 1px solid var(--border); border-radius: 8px; background: var(--surface-2); color: var(--text); }
  .rows { list-style: none; margin: 0; padding: 0; }
  .row { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid var(--border); }
  .row:last-child { border-bottom: none; }
  .row.muted { opacity: 0.5; }
  .row img, .ph { width: 36px; height: 52px; object-fit: contain; border-radius: 4px; background: var(--surface-2); flex: none; }
  .info { flex: 1; min-width: 0; }
  .name { font-size: 14px; font-weight: 600; }
  .name.err { color: #b91c1c; }
  .sub { font-size: 12px; color: var(--text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .note { font-size: 12px; color: var(--text-muted); }
  .note.known { color: var(--primary); font-weight: 600; }
  .num { display: flex; flex-direction: column; font-size: 11px; color: var(--text-muted); gap: 2px; }
  .num input { width: 72px; padding: 5px 6px; border: 1px solid var(--border); border-radius: 6px; background: var(--surface-2); color: var(--text); font: inherit; font-size: 13px; }
  .foot { display: flex; justify-content: flex-end; gap: 8px; padding: 12px 18px; border-top: 1px solid var(--border); }
  .btn { background: var(--primary); color: #fff; border: none; border-radius: 8px; padding: 9px 18px; font-size: 14px; font-weight: 600; cursor: pointer; }
  .btn:disabled { opacity: 0.5; cursor: default; }
  .btn.ghost { background: none; color: var(--text); border: 1px solid var(--border); }
</style>
