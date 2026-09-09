import katex from 'katex';
import 'katex/dist/katex.min.css';

const esc = (s) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

// Titles and abstracts from arXiv carry TeX in $...$ / \(...\) / $$...$$.
// Escape the prose, render only the math segments, return HTML for v-html.
const SPLIT = /(\$\$[\s\S]+?\$\$|\\\[[\s\S]+?\\\]|\$[^$\n]+?\$|\\\([\s\S]+?\\\))/g;

export function renderMath(text) {
  if (!text) return '';
  return text.split(SPLIT).map((seg, i) => {
    if (i % 2 === 0) return esc(seg);
    let display = false, tex = seg;
    if (seg.startsWith('$$')) { display = true; tex = seg.slice(2, -2); }
    else if (seg.startsWith('\\[')) { display = true; tex = seg.slice(2, -2); }
    else if (seg.startsWith('\\(')) tex = seg.slice(2, -2);
    else tex = seg.slice(1, -1);
    try {
      return katex.renderToString(tex, { displayMode: display, throwOnError: false });
    } catch {
      return esc(seg);
    }
  }).join('');
}
