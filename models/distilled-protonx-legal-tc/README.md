---
license_file: LICENSE.md
library_name: protonx-text-correction
tags:
- text-to-text
language:
- vi
---

<div align="center">

<p align="center">
    <img src="https://storage.googleapis.com/mle-courses-prod/users/61b6fa1ba83a7e37c8309756/private-files/678dadd0-603b-11ef-b0a7-998b84b38d43-ProtonX_logo_horizontally__1_.png" width="260"/>
</p>

<h1 align="center">
Distilled High-Accuracy Vietnamese Legal Document Correction
</h1>

[![GitHub](https://img.shields.io/badge/ProtonX-GitHub-black?logo=github)](https://github.com/protonx-engineering/protonx-text-correction)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Model-black?logo=huggingface)](https://huggingface.co/protonx-models/protonx-tc)
[![Website](https://img.shields.io/badge/protonx.co-Website-blue)](https://protonx.co)

</div>

---

## **Introduction**

### **Distilled ProtonX Legal Text Correction (v1.3-NC)**

This model is a distilled version of the [ProtonX Legal Text Correction](https://huggingface.co/protonx-models/protonx-legal-tc)

A **specialized Vietnamese correction model** engineered for **high-accuracy OCR post-processing**, especially **to fix noisy PaddleOCR outputs** in enterprise and legal workflows.

#### **Best Use Case (Primary Focus)**: **Fixing PaddleOCR text errors** 

<img src="https://protonx.co/assets/img/paddle-ocr-protonx.png">

The model is optimized to clean up real-world OCR mistakes such as:

* missing or incorrect diacritics
* broken word segmentation
* misrecognized legal terms
* punctuation artifacts
* formatting inconsistencies

Built on a Seq2Seq Transformer architecture, the model is trained on 70,000 correction pairs, including 20,000 pairs manually annotated by expert Vietnamese annotators, covering:

* official legal documents
* OCR outputs from scanned PDFs
* colloquial → standardized legal text

Strict constraints ensure:

* **Correction ≠ rewriting**
* meaning of legal text must never change
* no hallucination / no added legal terms
* confidence-based correction
* no paraphrasing

---

## **LICENSE**

This model is released under the ProtonX Text Correction Model License (v1.3-NC).

See [LICENSE.md](./LICENSE.md) for full terms, conditions, and usage restrictions.

## **Highlights**


1. **ROUGE-L: 96.30**
- Achieved on the ProtonX Legal Correction Validation Dataset. The evaluation dataset will be released in an upcoming public release.
- The model is half the size of the teacher model.


---

## **Quick Usage with Transformers**

```python
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_path = "protonx-models/distilled-protonx-legal-tc"

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

examples = [
    "can cu bo luat lao dong 2019 va cac van ban huong dan thuc hien.",
]

for text in examples:
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=160
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            num_beams=10,
            max_new_tokens=160,
            length_penalty=1.0,
            early_stopping=True,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    result = tokenizer.decode(outputs[0], skip_special_tokens=True)

    print(f"Input:  {text}")
    print(f"Output: {result}")
    print("-" * 30)
```

---

## **Benchmark**

### **ProtonX Legal Text Correction Validation Dataset**

| Metric        | Score     |
| ------------- | --------- |
| **ROUGE-L**   | **96.30** |

---


## **Training Details**

* Model: Seq2Seq Transformer
* Legal-domain augmentation
* Beam search decoding
* Max sequence length: 256 tokens total (128 tokens for input and 128 tokens for output).
* High-precision diacritic + punctuation restoration

### Domain Coverage:

* Government decrees
* Resolutions
* Contract clauses
* Administrative procedures
* OCR-normalized scanned documents

---

## **Example Outputs**


**Input:**

```
2.Báo vé an ninh mang là phòng ngìaphát hiēn,ngǎn chǎn xù ly hành vi
```

**Output:**

```
2. Bảo vệ an ninh mạng là phòng ngừa phát hiện, ngăn chặn xử lý hành vi
```

---

## **Use Cases**

* Legal OCR text normalization
* Standardizing government documents
* Contract proofreading
* Preprocessing for legal RAG systems
* Administrative workflow automation
* Compliance document processing

---

## **Limitations**

* Does not paraphrase or rewrite legal clauses
* Cannot restore missing semantic content
* Primarily optimized for Vietnamese
* Not designed for informal social media slang

---

## **Future Work**

* Achieving even higher ROUGE-L performance on legal-domain datasets
* Extending maximum sequence length from 128 to 1024 tokens for long-clause legal documents
---

## **Acknowledgments**

Thanks to:

* [vit5-base](https://huggingface.co/VietAI/vit5-base)
