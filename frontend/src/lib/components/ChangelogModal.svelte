<script>
  import { createEventDispatcher } from 'svelte';
  import Modal from './Modal.svelte';
  import { t } from '$lib/stores/i18n.js';
  import { CHANGELOG, currentEntry } from '$lib/changelog.js';

  const dispatch = createEventDispatcher();
  const STATUS_KEY = { planned: 'changelog_planned', 'in-progress': 'changelog_in_progress' };
</script>

<Modal variant="center" maxWidth="560px" zIndex={320} labelledby="changelog-title" on:close={() => dispatch('close')}>
  <div class="panel">
    <header class="head">
      <div class="title" id="changelog-title">{$t('changelog_title')}</div>
      <a class="gh" href="https://github.com/doleanj/wine-cellar/releases" target="_blank" rel="noopener">{$t('changelog_releases')}</a>
      <button class="x" type="button" on:click={() => dispatch('close')} aria-label={$t('changelog_close')}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </header>
    <div class="body">
      {#each CHANGELOG as e (e.version)}
        <section class="entry">
          <div class="ver">
            <span class="badge">{STATUS_KEY[e.status] ? e.version : 'v' + e.version}</span>
            {#if STATUS_KEY[e.status]}<span class="status status-{e.status}">{$t(STATUS_KEY[e.status])}</span>{/if}
            {#if e === currentEntry}<span class="status status-current">{$t('changelog_current')}</span>{/if}
          </div>
          <ul>
            {#each e.items as item}<li>{item}</li>{/each}
          </ul>
        </section>
      {/each}
    </div>
    <footer class="foot">
      <button type="button" class="btn" on:click={() => dispatch('close')}>{$t('changelog_close')}</button>
    </footer>
  </div>
</Modal>

<style>
  .panel { display: flex; flex-direction: column; width: 100%; max-height: 85vh; min-height: 0; }
  .head { display: flex; align-items: center; gap: 10px; padding: 14px 18px; border-bottom: 1px solid var(--border); }
  .title { font-size: 16px; font-weight: 700; color: var(--primary); }
  .gh { font-size: 12px; padding: 2px 10px; border-radius: 999px; border: 1px solid var(--border); color: var(--text-muted); text-decoration: none; }
  .gh:hover { color: var(--primary); }
  .x { margin-left: auto; background: none; border: none; color: var(--text-muted); cursor: pointer; display: flex; padding: 4px; }
  .body { overflow-y: auto; padding: 4px 18px; flex: 1 1 auto; min-height: 0; }
  .entry { padding: 12px 0; border-bottom: 1px solid var(--border); }
  .entry:last-child { border-bottom: none; }
  .ver { display: flex; align-items: center; gap: 6px; margin-bottom: 8px; }
  .badge { font-size: 12px; font-weight: 600; padding: 2px 10px; border-radius: 999px; background: var(--surface-2); border: 1px solid var(--border); color: var(--primary); }
  .status { font-size: 11px; font-weight: 600; padding: 1px 8px; border-radius: 999px; background: var(--surface-2); color: var(--text-muted); }
  .status-in-progress { background: #fef3c7; color: #b45309; }
  .status-current { background: #dcfce7; color: #15803d; }
  ul { margin: 0; padding-left: 18px; }
  li { font-size: 13.5px; line-height: 1.5; margin: 3px 0; }
  li::marker { color: var(--primary); }
  .foot { display: flex; justify-content: flex-end; padding: 12px 18px; border-top: 1px solid var(--border); }
  .btn { background: var(--primary); color: #fff; border: none; border-radius: 8px; padding: 9px 22px; font-size: 14px; font-weight: 600; cursor: pointer; }
</style>
