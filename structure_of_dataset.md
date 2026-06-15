# Project Data Overview 

## 1. Core Entities

| Entity | File / Object | What it Contains | How it Links to the Others |
|--------|----------------|------------------|---------------------------|
| **Case (Task)** | `case_XX_*.json` | Human‑readable description of the assignment, a list of **conceptual blocks**, and within each block a list of **criteria** that must be satisfied. | The `case_id` (UUID) appears in `solutions_metadata.json` and is part of the path to the notebook. |
| **Solution** | `solution_variant_*.ipynb` | A Jupyter notebook that implements the steps of the case. No explicit markers for criteria are present; the code/comments implicitly satisfy or violate them. | `solution_id` in `solutions_metadata.json` stores the relative path to the notebook. |
| **Evaluation Metadata** | `solutions_metadata.json` | For every *case ↔ solution* pair a JSON object that contains: <br>• `case_id` – links to the case file. <br>• `solution_id` – path to the notebook. <br>• `violated_criteria` – **list of criterion IDs that were NOT fulfilled**. | Connects a notebook to its case and to the ground‑truth information (which criteria failed). |

Together these three entities constitute a **complete training / testing set** for the judgement model:

- **Ground‑truth** – a binary vector (see Section 3) derived from `violated_criteria`.  
- **LLM‑generated feedback** – natural‑language comments that will be produced during experiments.  
- **Benchmark** – a suite of metrics (FPR, FNR, cost, latency, flip‑rate, etc.) that compare model predictions with the ground‑truth vectors.

---

## 2. JSON Schemas

### 2.1. Case File (`case_XX_*.json`)

```json
{
  "case_profile": {
    "metadata": {
      "case_id": "<UUID>",
      "title": "<string>",
      "description": "<string>",
      "dataset": "<URL>"
    },

    "conceptual_blocks": [
      {
        "block_id": "<UUID>",
        "name": "<string>",
        "description": "<string>",
        "criteria": [
          {
            "criterion_id": "<UUID>",
            "criterion_description": "<string>"
          }
          // … more criteria
        ]
      }
      // … more blocks
    ]
  }
}
```

* `metadata` – static information for UI / documentation.  
* `conceptual_blocks` – logical decomposition of the assignment (e.g., “Data exploration”, “Pre‑processing”, “Model training”).  
* `criteria` – atomic, verifiable requirements. Their UUIDs become the **positions** of the binary ground‑truth vector.

### 2.2. Evaluation Metadata (`solutions_metadata.json`)

```json
[
  {
    "case_id": "<UUID of the case>",
    "solution_id": "<relative path to .ipynb>",
    "violated_criteria": [
      "<criterion_id_1>",
      "<criterion_id_2>"
      // … may be an empty list for a perfect solution
    ]
  }
  // … more records
]
```

* An **empty** `violated_criteria` array means the solution satisfies **all** criteria – i.e. it is a *perfect* solution.  
* Any UUID present in the array marks the corresponding criterion as **failed** (`0` in the ground‑truth vector).

---

## 3. Ground‑Truth Vector Construction

1. **Load the case file** (`case_XX_*.json`) and extract **all** `criterion_id`s **in the order they appear** (block order → criterion order).  
2. **Find the matching record** in `solutions_metadata.json` (by `case_id` + `solution_id`).  
3. **Build the binary vector** `y` of length `N = number_of_criteria`:

```text
y[i] = 0  if criterion_id_i is listed in violated_criteria
y[i] = 1  otherwise
```

The resulting `y` is the **ground‑truth** for that particular solution and will be used by the benchmark.

---

## 4. What the benchmark script computes

* **False‑Positive Rate (FPR)** = FP / (FP + TN)  
* **False‑Negative Rate (FNR)** = FN / (FN + TP)  
* **Flip‑rate** – proportion of identical prompts that yield different predictions (internal provider variance).  
* **Cost** – number of tokens / API calls translated into monetary cost.  
* **Latency** – wall‑clock time needed to obtain the LLM feedback.

Metrics are **aggregated** on three hierarchy levels:

1. **Per‑criterion** (individual UUID)  
2. **Per‑block** (group of criteria)  
3. **Per‑case** (all criteria belonging to a single assignment)  

and finally **globally** across the whole dataset. The aggregated results are exported as JSON, Markdown, and PDF reports.

---

## 5. What “Solutions” and Their Metadata Actually Represent

| Aspect | Description |
|--------|-------------|
| **Solution (notebook)** | A runnable Jupyter notebook that may: <br>• Load the raw data.<br>• Perform exploratory analysis.<br>• Pre‑process features.<br>• Train one or more models.<br>• Evaluate on a hold‑out set.<br>All these steps are **implicitly** mapped to the criteria defined in the case file. |
| **Metadata (`violated_criteria`)** | The **only authoritative source** telling which criteria the notebook *fails*. It is **not** a list of satisfied criteria; it is a list of *failed* ones. Consequently, the ground‑truth binary vector is derived by marking `0` for every ID in this list and `1` for everything else. |
| **Why an empty list means “perfect”** | Because the definition of `violated_criteria` is *“criteria that were **not** fulfilled.”* If the list contains nothing, there are no unfulfilled criteria, i.e., **all** criteria are fulfilled → the ground‑truth vector consists exclusively of `1`s. This interpretation follows directly from the specification and is illustrated by the three “ideal” solutions in the provided `solutions_metadata.json`. |

---

## 6. Data‑Flow Diagram (textual)

```text
case_XX_*.json
   │   (extract ordered list of criterion_id)
   ▼
ground‑truth builder ──► y_true (binary vector)
   ▲                                 │
   │                                 ▼
solutions_metadata.json                ──► y_true (by comparing with violated_criteria)
   │
   ▼
solution_variant_*.ipynb
   │
   ▼
LLM judgement model (evaluate_notebook)
   │
   ▼
y_pred (binary vector) ──► benchmark calculations
   │
   ▼
Aggregated metrics (FPR, FNR, cost, latency, …) → reports
```
