<script>
  import { createEventDispatcher } from 'svelte';
  import Modal from './Modal.svelte';
  import { t } from '$lib/stores/i18n.js';

  export let sources = [];

  const dispatch = createEventDispatcher();
</script>

<Modal variant="center" maxWidth="620px" zIndex={320} labelledby="sources-title" on:close={() => dispatch('close')}>
  <div class="panel">
    <header class="head">
      <div class="title" id="sources-title">{$t('info_sources_title')}</div>
      <button class="x" type="button" on:click={() => dispatch('close')} aria-label={$t('preview_cancel')}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </header>
    <div class="body">
      <p class="intro">{$t('info_sources_intro')}</p>

      {#each sources as s (s.key)}
        <section class="src">
          <h3>{s.name}</h3>
          <p class="host">{s.hosts[0]}{s.path_prefix}…</p>
          <p class="fills"><b>{$t('info_sources_fills')}:</b> {s.fields.filter(f => f !== 'url').map(f => $t('elabel_f_' + f)).join(', ')}</p>
        </section>
      {:else}
        <p class="intro">{$t('info_sources_none')}</p>
      {/each}

      <section class="src">
        <h3>{$t('info_sources_qr_title')}</h3>
        <p class="host">*.st4.ch · elabel.scantrust.com</p>
        <p class="fills">{$t('info_sources_qr')}</p>
      </section>

      <p class="more">{$t('info_sources_more')}</p>
    </div>
    <footer class="foot">
      <button type="button" class="btn" on:click={() => dispatch('close')}>{$t('info_sources_close')}</button>
    </footer>
  </div>
</Modal>

<style>
  .panel { display: flex; flex-direction: column; width: 100%; max-height: 85vh; min-height: 0; }
  .head { display: flex; align-items: center; justify-content: space-between; padding: 14px 18px; border-bottom: 1px solid var(--border); }
  .title { font-size: 16px; font-weight: 700; color: var(--primary); }
  .x { background: none; border: none; color: var(--text-muted); cursor: pointer; display: flex; padding: 4px; }
  .body { overflow-y: auto; padding: 12px 18px; flex: 1 1 auto; min-height: 0; }
  .intro, .more { font-size: 13px; color: var(--text-muted); margin: 4px 0 10px; }
  .src { border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px; margin-bottom: 10px; background: var(--surface-2); }
  h3 { margin: 0 0 2px; font-size: 14px; }
  .host { margin: 0 0 6px; font-size: 12px; color: var(--primary); word-break: break-all; }
  .fills { margin: 0; font-size: 12px; color: var(--text-muted); line-height: 1.5; }
  .foot { display: flex; justify-content: flex-end; padding: 12px 18px; border-top: 1px solid var(--border); }
  .btn { background: var(--primary); color: #fff; border: none; border-radius: 8px; padding: 9px 22px; font-size: 14px; font-weight: 600; cursor: pointer; }
</style>
