<script>
  import { t, lang } from '$lib/stores/i18n.js';
  import { PAIRINGS, splitPairings, joinPairings } from '$lib/wine-reference.js';

  // Comma-separated string: known category keys plus optional free-text tokens.
  export let value = '';

  $: tokens = splitPairings(value);
  $: selected = new Set(tokens);
  $: freeText = tokens.filter(tok => !PAIRINGS.some(p => p.key === tok)).join(', ');

  function toggle(key) {
    const next = selected.has(key) ? tokens.filter(tok => tok !== key) : [...tokens, key];
    value = joinPairings(next);
  }

  function onFreeText(e) {
    const keys = tokens.filter(tok => PAIRINGS.some(p => p.key === tok));
    const free = e.target.value.split(',').map(s => s.trim()).filter(Boolean);
    value = joinPairings([...keys, ...free]);
  }
</script>

<div class="picker">
  <div class="chips" role="group" aria-label={$t('modal_field_pairings')}>
    {#each PAIRINGS as p (p.key)}
      <button
        type="button"
        class="chip"
        class:on={selected.has(p.key)}
        aria-pressed={selected.has(p.key)}
        title={p.fr}
        on:click={() => toggle(p.key)}
      >
        <span class="icon" aria-hidden="true">{p.icon}</span>{p[$lang] || p.en}
      </button>
    {/each}
  </div>
  <input
    type="text"
    class="free"
    value={freeText}
    on:change={onFreeText}
    placeholder={$t('pairing_other')}
    aria-label={$t('pairing_other')}
  />
</div>

<style>
  .picker { display: flex; flex-direction: column; gap: 8px; }
  .chips { display: flex; flex-wrap: wrap; gap: 6px; }
  .chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 5px 10px;
    border: 1.5px solid var(--border);
    border-radius: 999px;
    background: var(--bg);
    color: var(--text-muted);
    font-size: 12px;
    cursor: pointer;
    transition: background 0.15s, color 0.15s, border-color 0.15s;
  }
  .chip:hover:not(.on) { background: var(--surface-2); color: var(--text); }
  .chip.on {
    background: var(--primary);
    border-color: var(--primary);
    color: #fff;
    font-weight: 600;
  }
  .icon { font-size: 14px; line-height: 1; }
  .free {
    width: 100%;
    box-sizing: border-box;
    padding: 9px 12px;
    border: 1.5px solid var(--border);
    border-radius: 8px;
    background: var(--bg);
    color: var(--text);
    font-size: 14px;
    font-family: inherit;
  }
  .free:focus { outline: none; border-color: var(--primary); }
</style>
