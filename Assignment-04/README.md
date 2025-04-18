---
base_model: unsloth/llama-3.2-1b-bnb-4bit
library_name: transformers
model_name: llama-3.2-1B-sutdqa
tags:
- generated_from_trainer
- unsloth
- trl
- sft
licence: license
---

# Model Card for llama-3.2-1B-sutdqa

This model is a fine-tuned version of [unsloth/llama-3.2-1b-bnb-4bit](https://huggingface.co/unsloth/llama-3.2-1b-bnb-4bit).
It has been trained using [TRL](https://github.com/huggingface/trl).

## Quick start

```python
from transformers import pipeline

question = "If you had a time machine, but could only go to the past or the future once and never return, which would you choose and why?"
generator = pipeline("text-generation", model="adi0308/llama-3.2-1B-sutdqa", device="cuda")
output = generator([{"role": "user", "content": question}], max_new_tokens=128, return_full_text=False)[0]
print(output["generated_text"])
```

## Training procedure

[<img src="https://raw.githubusercontent.com/wandb/assets/main/wandb-github-badge-28.svg" alt="Visualize in Weights & Biases" width="150" height="24"/>](https://wandb.ai/adityakuma0308/huggingface/runs/5hqsck4z) 


This model was trained with SFT.

### Framework versions

- TRL: 0.14.0
- Transformers: 4.51.1
- Pytorch: 2.6.0+cu118
- Datasets: 3.5.0
- Tokenizers: 0.21.1

## Citations



Cite TRL as:
    
```bibtex
@misc{vonwerra2022trl,
	title        = {{TRL: Transformer Reinforcement Learning}},
	author       = {Leandro von Werra and Younes Belkada and Lewis Tunstall and Edward Beeching and Tristan Thrush and Nathan Lambert and Shengyi Huang and Kashif Rasul and Quentin Gallouédec},
	year         = 2020,
	journal      = {GitHub repository},
	publisher    = {GitHub},
	howpublished = {\url{https://github.com/huggingface/trl}}
}
```