<script>
  import { createEventDispatcher, onDestroy } from 'svelte';
  import Modal from './Modal.svelte';
  import { t } from '$lib/stores/i18n.js';
  import { updateWine } from '$lib/api.js';

  export let wine;

  const dispatch = createEventDispatcher();
  const before = { quantity: wine.quantity || 0, last_drunk: wine.last_drunk || '' };
  const CHIPS = ['open_chip_rebuy', 'open_chip_young', 'open_chip_past'];

  let step = 'confirm'; // 'confirm' | 'done' | 'rate'
  let current = wine;
  let busy = false;
  let error = '';
  let rating = wine.rating || 0;
  let note = '';
  let chip = '';
  let timer;

  async function save(values) {
    busy = true; error = '';
    try {
      current = await updateWine(wine.id, values);
      dispatch('updated', current);
      return true;
    } catch {
      error = $t('toast_error_save');
      return false;
    } finally {
      busy = false;
    }
  }

  async function confirm() {
    if (!(await save({ quantity: before.quantity - 1 }))) return;
    step = 'done';
    timer = setTimeout(() => dispatch('close'), 10000);
  }

  async function undo() {
    clearTimeout(timer);
    if (await save({ quantity: before.quantity, last_drunk: before.last_drunk })) dispatch('close');
  }

  function startRate() {
    clearTimeout(timer);
    step = 'rate';
  }

  function pickChip(key) {
    chip = chip === key ? '' : key;
  }

  // One dated line: the chosen tag, then the free note.
  $: tastingLine = (() => {
    const text = [chip && $t(chip), note.trim()].filter(Boolean).join(': ');
    return text ? `${new Date().toISOString().slice(0, 10)}: ${text}` : '';
  })();

  async function saveRating() {
    const values = {};
    if (rating && rating !== wine.rating) values.rating = rating;
    if (tastingLine) values.tasting = current.tasting ? `${current.tasting}\n${tastingLine}` : tastingLine;
    if (!Object.keys(values).length || await save(values)) dispatch('close');
  }

  onDestroy(() => clearTimeout(timer));
</script>

{#if step === 'confirm'}
  <Modal variant="sheet" labelledby="open-title" on:close={() => dispatch('close')}>
    <div class="sheet">
      <div class="title" id="open-title">{$t('open_title')}</div>
      <div class="wine">{wine.name}{#if wine.vintage} <span class="vint">{wine.vintage}</span>{/if}</div>
      <div class="stock">{$t('open_stock').replace('{from}', before.quantity).replace('{to}', before.quantity - 1)}</div>
      {#if error}<p class="err">{error}</p>{/if}
      <div class="actions">
        <button type="button" class="btn ghost" on:click={() => dispatch('close')}>{$t('modal_cancel')}</button>
        <button type="button" class="btn primary" disabled={busy} on:click={confirm}>🍷 {$t('open_confirm')}</button>
      </div>
    </div>
  </Modal>
{:else if step === 'done'}
  <div class="snack" role="status">
    <span class="msg">{before.quantity - 1 > 0 ? $t('open_done').replace('{n}', before.quantity - 1) : $t('open_done_last')}</span>
    {#if error}<span class="err">{error}</span>{/if}
    <button type="button" class="link" disabled={busy} on:click={undo}>{$t('open_undo')}</button>
    <button type="button" class="link strong" on:click={startRate}>{$t('open_rate')}</button>
  </div>
{:else}
  <Modal variant="sheet" labelledby="rate-title" on:close={() => dispatch('close')}>
    <div class="sheet">
      <div class="title" id="rate-title">{$t('open_rate_title')}</div>
      <div class="wine">{wine.name}{#if wine.vintage} <span class="vint">{wine.vintage}</span>{/if}</div>
      <div class="stars" role="group" aria-label={$t('open_rate')}>
        {#each [1, 2, 3, 4, 5] as n}
          <button type="button" class="star" class:on={n <= rating} aria-pressed={n === rating}
            aria-label={`${n}/5`} on:click={() => rating = n === rating ? 0 : n}>★</button>
        {/each}
      </div>
      <div class="chips">
        {#each CHIPS as c}<button type="button" class="chip" class:on={chip === c} aria-pressed={chip === c} on:click={() => pickChip(c)}>{$t(c)}</button>{/each}
      </div>
      <input class="note" type="text" bind:value={note} placeholder={$t('open_note')} />
      {#if tastingLine}<p class="preview">{$t('open_saved_as')} {tastingLine}</p>{/if}
      {#if error}<p class="err">{error}</p>{/if}
      <div class="actions">
        <button type="button" class="btn ghost" on:click={() => dispatch('close')}>{$t('open_skip')}</button>
        <button type="button" class="btn primary" disabled={busy} on:click={saveRating}>{$t('open_save')}</button>
      </div>
    </div>
  </Modal>
{/if}

<style>
  .sheet { padding: 20px 20px 18px; display: flex; flex-direction: column; gap: 10px; }
  .title { font-size: 13px; font-weight: 700; color: var(--primary); text-transform: uppercase; letter-spacing: 0.04em; }
  .wine { font-size: 17px; font-weight: 700; color: var(--text); }
  .vint { color: var(--text-muted); font-weight: 400; }
  .stock { font-size: 14px; color: var(--text-muted); }
  .err { color: #8c2a20; font-size: 13px; margin: 0; }
  .actions { display: flex; gap: 10px; margin-top: 6px; }
  .btn { flex: 1; min-height: 46px; border-radius: 10px; font-size: 15px; font-weight: 600; cursor: pointer; border: 1.5px solid var(--border); }
  .btn.primary { background: var(--primary); border-color: var(--primary); color: #fff; flex: 2; }
  .btn.ghost { background: var(--bg); color: var(--text); }
  .btn:disabled { opacity: 0.6; }

  .stars { display: flex; gap: 4px; }
  .star { background: none; border: none; font-size: 34px; line-height: 1; padding: 2px 4px; color: var(--border); cursor: pointer; }
  .star.on { color: #d4a017; }
  .chips { display: flex; flex-wrap: wrap; gap: 6px; }
  .chip { padding: 6px 12px; border: 1.5px solid var(--border); border-radius: 999px; background: var(--bg); color: var(--text-muted); font-size: 13px; cursor: pointer; }
  .chip.on { background: var(--primary); border-color: var(--primary); color: #fff; font-weight: 600; }
  .preview { margin: 0; font-size: 12px; color: var(--text-muted); }
  .note { width: 100%; box-sizing: border-box; min-height: 42px; padding: 0 12px; border: 1.5px solid var(--border); border-radius: 10px; background: var(--bg); color: var(--text); font-size: 15px; }

  .snack { position: fixed; left: 50%; bottom: calc(16px + env(safe-area-inset-bottom, 0px)); transform: translateX(-50%); z-index: 400;
    width: calc(100% - 24px); max-width: 460px; box-sizing: border-box; display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
    background: var(--text); color: #fff; padding: 12px 16px; border-radius: 12px; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3); font-size: 14px; }
  .snack .msg { flex: 1; min-width: 120px; }
  .link { background: none; border: none; color: #fff; text-decoration: underline; font-size: 14px; padding: 8px 2px; cursor: pointer; }
  .link.strong { font-weight: 700; }
</style>
