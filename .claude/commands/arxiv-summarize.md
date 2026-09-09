Read `pending.json` from the current directory. For each paper, produce a JSON result and write all results to `results.json`.

## Fixed taxonomy tags

Physics topics: `oscillations`, `mass-ordering`, `cross-section`, `sterile-neutrino`, `dark-matter`, `supernova`, `solar`, `atmospheric`, `reactor`, `accelerator`, `cosmic-ray`, `double-beta-decay`

Detector/method: `liquid-argon`, `water-cherenkov`, `scintillator`, `radiochemical`, `emulsion`, `data-analysis`, `machine-learning`, `simulation`

Source type: `theory`, `experiment`, `review`

Only assign tags from this exact list. Do not invent new tags.

## Instructions

1. Read `pending.json`. It has two arrays: `certain` (neutrino relevance already confirmed) and `ambiguous` (borderline — needs your judgement).

2. For each paper in `certain`: output `{"arxiv_id": "...", "keep": true, "summary": "...", "tags": [...]}`. Do not question relevance — just summarise and tag.

3. For each paper in `ambiguous`: decide whether it is genuinely relevant to neutrino physics. A detector or data-analysis paper qualifies only if it is directly applicable to neutrino experiments (e.g. liquid argon TPC, water Cherenkov, scintillator detectors used in neutrino experiments). Output `{"arxiv_id": "...", "keep": true/false, "summary": "...", "tags": [...]}`. If `keep` is false, summary may be an empty string and tags an empty array.

4. The `summary` must be 2–3 sentences written for a physicist reader. Summarise the key result or contribution — not the motivation. Be precise; use domain terminology.

5. The `collaboration` field in `pending.json` comes from InspireHEP. If it is non-empty, do NOT add it as a tag — it is stored separately.

6. Write all results (certain + ambiguous) to `results.json` as a JSON array.

## Example output entry

```json
{
  "arxiv_id": "2501.12345",
  "keep": true,
  "summary": "The authors present a measurement of the electron neutrino appearance probability in the NOvA far detector using an updated flux model. The analysis reduces the systematic uncertainty on the cross-section by 15% compared to the previous result. Best-fit values favor the normal mass ordering at 2.1σ.",
  "tags": ["oscillations", "accelerator", "experiment"]
}
```

Now read `pending.json`, process all papers, and write `results.json`.
