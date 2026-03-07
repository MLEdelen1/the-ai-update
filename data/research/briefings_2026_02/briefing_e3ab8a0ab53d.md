# Qwen3.5-27B & 2B Uncensored Aggressive Release (GGUF)

## What changed
<!-- SC_OFF --><div class="md"><p>Following up on the 9B - here's the promised 27B and 2B. </p> <p>27B is the main event. 27B dense, 64 layers, hybrid DeltaNet + softmax, 262K context, multimodal, <strong>all functional</strong>. 0/465 refusals. <strong>Lossless uncensoring.</strong> Due to popular demand, I've added IQ quants this time since a few people asked for them on the 9B post. Depending on the reception, I might add for 35B-A3B as well.</p> <p>Link: <a href="https://huggingface.co/HauhauCS/Qwen3.5-27B-Uncensored-HauhauCS-Aggressive">https://huggingface.co/HauhauCS/Qwen3.5-27B-Uncensored-HauhauCS-Aggressive</a></p> <p>Quants: IQ2_M (8.8 GB), IQ3_M (12 GB), Q3_K_M (13 GB), IQ4_XS (14 GB), Q4_K_M (16 GB), Q5_K_M (19 GB), Q6_K (21 GB), Q8_0 (27 GB), BF16 (51 GB)</p> <p>For clarity sake, the IQ quants use importance matrix calibration.</p> <p>2B is more of a proof of concept. It's a 2B model so <strong>don't expect miracles but abliteration didn't degrade it</strong>, so whatever q

Source: [Qwen3.5-27B & 2B Uncensored Aggressive Release (GGUF)](https://www.reddit.com/r/LocalLLaMA/comments/1rlwbrf/qwen3527b_2b_uncensored_aggressive_release_gguf/)

## Why it matters
This affects near-term AI workflows, model/tool selection, and practical implementation decisions. It should be validated in a real use case before broad rollout.

## What to do next
Read the primary source, run a small pilot in one workflow, track quality and speed impact, and only scale if measurable gains hold.