<script>
  import { t } from '$lib/stores/i18n.js';
  import { PROFILE_MIN, PROFILE_MAX } from '$lib/wine-reference.js';

  // "Macaron du goût": round badge with a wine glass in the centre.
  // Top arc = fruit (léger → prononcé), bottom arc = personnalité (léger → puissant).
  export let fruit = null;
  export let personality = null;
  export let size = 96;

  const CX = 50, CY = 50, R = 28;
  const steps = Array.from({ length: PROFILE_MAX - PROFILE_MIN + 1 }, (_, i) => i + PROFILE_MIN);

  // 5 dots over a 140° arc; top arc runs left→right over the top, bottom arc left→right under the bottom.
  function dot(i, top) {
    const a = (top ? 200 + i * 35 : 160 - i * 35) * Math.PI / 180;
    return { x: CX + R * Math.cos(a), y: CY + R * Math.sin(a) };
  }

  $: valid = Number.isInteger(fruit) || Number.isInteger(personality);
  $: label = `${$t('badge_fruit')}: ${fruit ?? '–'}/5, ${$t('badge_personality')}: ${personality ?? '–'}/5`;
</script>

{#if valid}
  <svg class="badge" width={size} height={size} viewBox="0 0 100 100" role="img" aria-label={label}>
    <title>{label}</title>
    <circle cx={CX} cy={CY} r="47" class="ring" />
    {#each steps as s, i}
      {@const p = dot(i, true)}
      <circle cx={p.x} cy={p.y} r="3.8" class="dot" class:on={fruit !== null && s <= fruit} />
    {/each}
    {#each steps as s, i}
      {@const p = dot(i, false)}
      <circle cx={p.x} cy={p.y} r="3.8" class="dot" class:on={personality !== null && s <= personality} />
    {/each}
    <text x="50" y="12" text-anchor="middle" class="lbl">{$t('badge_fruit')}</text>
    <text x="50" y="94" text-anchor="middle" class="lbl">{$t('badge_personality')}</text>
    <!-- wine glass -->
    <g class="glass" fill="none" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M43 37h14c0 9-2.5 15-7 15s-7-6-7-15z" />
      <path d="M50 52v9M44.5 61h11" />
    </g>
  </svg>
{/if}

<style>
  .ring { fill: var(--surface); stroke: var(--border); stroke-width: 1.5; }
  .dot { fill: none; stroke: var(--primary); stroke-width: 1.5; }
  .dot.on { fill: var(--primary); }
  .glass { stroke: var(--primary); }
  .lbl { font-size: 6.5px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; fill: var(--text-muted); }
</style>
