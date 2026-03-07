# I thought a 7M model shouldn't be able to do this

## What changed
<table> <tr><td> <a href="https://www.reddit.com/r/LocalLLaMA/comments/1rlqnyt/i_thought_a_7m_model_shouldnt_be_able_to_do_this/"> <img alt="I thought a 7M model shouldn't be able to do this" src="https://preview.redd.it/11k3k5j3z9ng1.png?width=640&amp;crop=smart&amp;auto=webp&amp;s=f70614b21bbb9fbdb03f37c4c10f521ddbcdc4c9" title="I thought a 7M model shouldn't be able to do this" /> </a> </td><td> <!-- SC_OFF --><div class="md"><p>Bias detection and sycophancy resistance don't show up until 18-34M parameters in normal training. <strong>I got both at 7M</strong> by injecting contrastive behavioral pairs into 0.05% of pretraining tokens. No architecture changes, no auxiliary loss, zero inference cost.</p> <p>Bias: 0.000 → 0.433 (vanilla needs 18M to hit 0.133) Sycophancy: 0.000 → 0.513 (vanilla 34M only gets 0.300) Factual cost: -0.029 at 5% injection rate</p> <p>I also tried a geometric regularizer targeting the same subspaces. Zero effect at both 7M and 12M. The model has enough capac

Source: [I thought a 7M model shouldn't be able to do this](https://www.reddit.com/r/LocalLLaMA/comments/1rlqnyt/i_thought_a_7m_model_shouldnt_be_able_to_do_this/)

## Why it matters
This affects near-term AI workflows, model/tool selection, and practical implementation decisions. It should be validated in a real use case before broad rollout.

## What to do next
Read the primary source, run a small pilot in one workflow, track quality and speed impact, and only scale if measurable gains hold.