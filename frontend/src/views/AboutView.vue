<script setup>
import { ref } from 'vue';
import TopBar from '../components/TopBar.vue';
import NavPane from '../components/NavPane.vue';
import BottomTabs from '../components/BottomTabs.vue';
import Drawer from '../components/Drawer.vue';
import { useMedia } from '../composables/useMedia.js';

const { isPhone, isWide } = useMedia();
const drawer = ref(false);
const REPO = 'https://github.com/czczc/arxiv-neutrino';
</script>

<template>
  <div class="shell">
    <TopBar title="About" :is-phone="isPhone" :menu="!isWide" @menu="drawer = true" />
    <div class="panes">
      <NavPane v-if="isWide" />
      <div class="content">
        <h1>Neutrino Daily</h1>
        <p>A daily digest of new <b>experimental neutrino physics</b> papers on arXiv, filtered, summarised and tagged automatically, and served as a triage inbox. The focus is experiments, detectors and data analysis.</p>

        <h2>What is collected</h2>
        <p>Every morning (07:00 US Eastern) the pipeline reads the previous day's arXiv listings in four categories:</p>
        <ul>
          <li><span class="mono">hep-ex</span> High Energy Physics, Experiment</li>
          <li><span class="mono">nucl-ex</span> Nuclear Experiment</li>
          <li><span class="mono">physics.ins-det</span> Instrumentation and Detectors</li>
          <li><span class="mono">physics.data-an</span> Data Analysis, Statistics and Probability</li>
        </ul>

        <h2>How papers are filtered</h2>
        <ol>
          <li><b>Keyword pass.</b> Title and abstract are matched against neutrino terms (neutrino, oscillation, mass ordering, sterile, Majorana, double beta, and experiment names such as DUNE, JUNO, IceCube, T2K, NOvA, KamLAND). A match is kept as <i>certain</i>. Papers that only mention generic detector words (scintillator, PMT, SiPM, dark matter) are held as <i>ambiguous</i>. Everything else is dropped.</li>
          <li><b>InspireHEP lookup.</b> Survivors are enriched with the collaboration name and document type. Conference proceedings are dropped, as are papers from collider collaborations with no neutrino programme.</li>
          <li><b>AI review.</b> An LLM writes a two-to-three sentence summary of each remaining paper for a physicist reader and assigns tags from a fixed taxonomy (oscillations, cross-section, reactor, liquid-argon, machine-learning, theory, ...). For ambiguous papers it also decides whether the work is genuinely applicable to neutrino experiments and discards it otherwise. Summaries are machine-generated; check the abstract or paper before relying on a detail.</li>
        </ol>

        <h2>Reading</h2>
        <p>There is no login. Stars, read marks and deletions live in this browser's local storage and can be exported and imported as JSON from the left pane. Deleted papers are hidden from every list except the Deleted folder.</p>
        <p>Keyboard: <b>j</b>/<b>k</b> move, <b>s</b> star, <b>e</b> mark read, <b>d</b> delete, <b>o</b> open on arXiv, <b>/</b> search.</p>

        <h2>Source</h2>
        <p>Code, filter rules and the summarising prompt: <a :href="REPO" target="_blank" rel="noopener">{{ REPO.replace('https://', '') }}</a></p>
      </div>
    </div>
    <BottomTabs v-if="isPhone" />
    <Drawer :open="drawer" @close="drawer = false"><NavPane :show-folders="isPhone" @navigate="drawer = false" /></Drawer>
  </div>
</template>

<style scoped>
.shell { height: 100%; display: flex; flex-direction: column; }
.panes { flex: 1; min-height: 0; display: flex; }
.content { flex: 1; overflow-y: auto; padding: 18px 28px 40px; max-width: 720px; font-size: 13.5px; line-height: 1.55; color: var(--body); }
h1 { font-size: 20px; font-weight: 700; color: var(--ink); margin: 6px 0 4px; }
h2 { font-size: 15px; font-weight: 700; color: var(--ink); margin: 22px 0 6px; padding-bottom: 5px; border-bottom: 2px solid var(--ink); }
p, li { margin: 0 0 8px; }
ul, ol { padding-left: 22px; margin: 0; }
li .mono { color: var(--text-2); margin-right: 6px; }
b { color: var(--ink); font-weight: 600; }
@media (max-width: 699px) {
  .content { padding: 12px 16px 24px; font-size: 15px; }
}
</style>
