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

## 4. How the Metadata Is Consumed by the Benchmark

### 4.1. Typical command‑line entry point

```bash
python run_benchmark.py \
    --cases_dir        ./cases \
    --metadata_path    ./solutions_metadata.json \
    --model_cfg        ./config/model_map.json
```

### 4.2. Internal workflow (simplified pseudocode)

```python
import json, pathlib

# ----------------------------------------------------------------------
# 1. Load all cases (dictionary: case_id → parsed JSON)
# ----------------------------------------------------------------------
cases = {}
for fp in pathlib.Path("./cases").glob("case_*.json"):
    data = json.load(open(fp))
    cid  = data["case_profile"]["metadata"]["case_id"]
    cases[cid] = data

# ----------------------------------------------------------------------
# 2. Load solution‑metadata
# ----------------------------------------------------------------------
solution_meta = json.load(open("./solutions_metadata.json"))

# ----------------------------------------------------------------------
# 3. Iterate over every (case, solution) pair
# ----------------------------------------------------------------------
benchmark_records = []
for entry in solution_meta:
    case_id   = entry["case_id"]
    sol_path  = entry["solution_id"]
    violated  = set(entry["violated_criteria"])

    # 3.1. Ordered list of all criteria for this case
    ordered_criteria = []
    for block in cases[case_id]["case_profile"]["conceptual_blocks"]:
        ordered_criteria.extend([c["criterion_id"] for c in block["criteria"]])

    # 3.2. Ground‑truth vector y_true
    y_true = [0 if cid in violated else 1 for cid in ordered_criteria]

    # 3.3. Obtain model prediction (binary vector) for the notebook
    #     The function `evaluate_notebook` is part of the judgement model implementation.
    y_pred, stats = evaluate_notebook(
        notebook_path = pathlib.Path(sol_path),
        criteria_ids  = ordered_criteria
    )
    # `stats` may contain token count, latency, cost, etc.

    # 3.4. Store everything for later aggregation
    benchmark_records.append({
        "case_id":       case_id,
        "solution_id":   sol_path,
        "criteria":      ordered_criteria,
        "y_true":        y_true,
        "y_pred":        y_pred,
        "runtime_ms":    stats["runtime_ms"],
        "token_usage":   stats["token_usage"],
        "cost_usd":      stats["cost_usd"]
    })
```

### 4.3. What the benchmark script finally computes

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

## 5. Full Dataset Construction Pipeline (Programmatic View)

```python
import json, pathlib

# ----------------------------------------------------------------------
# 1. Load cases (dictionary case_id → case JSON)
# ----------------------------------------------------------------------
cases_dir = pathlib.Path("./cases")
cases = {}
for fp in cases_dir.glob("case_*.json"):
    case_json = json.load(fp.open())
    cid = case_json["case_profile"]["metadata"]["case_id"]
    cases[cid] = case_json

# ----------------------------------------------------------------------
# 2. Load solution metadata
# ----------------------------------------------------------------------
with open("./solutions_metadata.json") as f:
    solutions_meta = json.load(f)

# ----------------------------------------------------------------------
# 3. Build the unified dataset list
# ----------------------------------------------------------------------
dataset = []          # each element = one (case, solution) example
for rec in solutions_meta:
    case_id  = rec["case_id"]
    sol_path = rec["solution_id"]
    violated = set(rec["violated_criteria"])

    # 3.1. Ordered list of criteria for this case
    criteria_order = []
    for block in cases[case_id]["case_profile"]["conceptual_blocks"]:
        criteria_order.extend([c["criterion_id"] for c in block["criteria"]])

    # 3.2. Ground‑truth vector
    y_true = [0 if cid in violated else 1 for cid in criteria_order]

    # 3.3. (Optional) sanity check that the notebook exists
    assert pathlib.Path(sol_path).exists(), f"Notebook not found: {sol_path}"

    # 3.4. Append the prepared record
    dataset.append({
        "case_id":       case_id,
        "solution_id":   sol_path,
        "criteria":      criteria_order,   # needed for later evaluation
        "y_true":        y_true
    })
```

The resulting `dataset` list is what the benchmark code consumes (see Section 4). Each entry contains **all information needed** to:

* Load the notebook (`solution_id`).  
* Know the exact order of criteria (`criteria`).  
* Compare model output with the **ground‑truth** (`y_true`).  

---

## 6. What “Solutions” and Their Metadata Actually Represent

| Aspect | Description |
|--------|-------------|
| **Solution (notebook)** | A runnable Jupyter notebook that may: <br>• Load the raw data.<br>• Perform exploratory analysis.<br>• Pre‑process features.<br>• Train one or more models.<br>• Evaluate on a hold‑out set.<br>All these steps are **implicitly** mapped to the criteria defined in the case file. |
| **Metadata (`violated_criteria`)** | The **only authoritative source** telling which criteria the notebook *fails*. It is **not** a list of satisfied criteria; it is a list of *failed* ones. Consequently, the ground‑truth binary vector is derived by marking `0` for every ID in this list and `1` for everything else. |
| **Why an empty list means “perfect”** | Because the definition of `violated_criteria` is *“criteria that were **not** fulfilled.”* If the list contains nothing, there are no unfulfilled criteria, i.e., **all** criteria are fulfilled → the ground‑truth vector consists exclusively of `1`s. This interpretation follows directly from the specification and is illustrated by the three “ideal” solutions in the provided `solutions_metadata.json`. |

---

## 7. Data‑Flow Diagram (textual)

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
