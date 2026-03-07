# OpenAI GPT‑5.4 lands in ChatGPT, and Codex pushes it into real multi-file builds

## What changed
OpenAI has released GPT‑5.4, and the model is now available inside ChatGPT. In the same demo flow, GPT‑5.4 is also shown running through OpenAI Codex as a coding-agent workflow rather than a single chat reply. The demonstrated task is not a toy script: Codex creates a new local project folder, generates and edits multiple files, and iterates through feature passes on a browser-based build.

The showcased project is an interactive 3D Earth digital twin that zooms from orbital scale down to city streets. The workflow adds cloud and atmosphere layers, then implements day/night and city-light toggles as additional feature passes. During generation, the demo explicitly selects “extra high” reasoning effort, signaling a deliberate push toward harder, architecture-heavy output instead of quick one-shot code snippets.

## Why it matters
This is a concrete shift from chat-centric “here’s one block of code” behavior toward project execution across files, assets, and iterative revisions. For developers, that matters most when a prototype needs structure, not just syntax, especially for web apps that combine rendering, UI controls, and performance constraints in one pipeline.

Creators and technical founders also benefit because multi-pass scaffolding can reduce setup friction on ambitious prototypes, including graphics-heavy concepts that usually break down when handled as a single prompt. But the key caveat is methodological: the excerpt references specs, performance, and benchmarks without publishing numbers or test design, so claims of superiority remain unverified until independently reproduced.

## What to do next
Run a controlled A/B test in your own stack. Use the same complex multi-file prompt in GPT‑5.4 via ChatGPT and via Codex, then track first-pass completeness, iteration count to acceptable quality, browser performance under load, and maintainability of generated project structure. Compare those results against your current baseline model and workflow before changing team defaults.

If you ship client work, treat this as a validation sprint, not a hype switch. Confirm where GPT‑5.4 materially saves cycles on complex builds, document where it stalls, and only then standardize. Source: [YouTube demo excerpt](https://www.youtube.com/watch?v=YRyjkmmW5Ek).