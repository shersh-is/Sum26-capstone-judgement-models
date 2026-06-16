# Project Data Overview

## 1. JSON Structure of a Case (dataset)

Each case is stored in a file named `case_XX_*.json`.  
The top‑level key is **`case_profile`** and it contains two sections:

| Section            | Fields (as in the provided files)                                                                                                                                               | Description                                            |
|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------|
| `metadata`         | `case_id`, `title`, `description`, `dataset`                                                                                                                                      | Static information about the case. `case_id` is a UUID that uniquely identifies the case. |
| `conceptual_blocks`| An array of blocks. Each block has:<br>• `block_id` (UUID)<br>• `name` (string)<br>• `description` (string)<br>• `criteria` (array)                                                   | Logical subdivision of the assignment.                |
| `criteria` (inside each block) | Each criterion has:<br>• `criterion_id` (UUID)<br>• `criterion_description` (string)                                                                                                   | Atomic, binary requirement. The list of all `criterion_id`s from all blocks defines the length and order of the binary ground‑truth vector for this case. |

**Example excerpt (from `case_01_customer_churn.json`):**

~~~json
{
  "case_profile": {
    "metadata": {
      "case_id": "019c3857-81ef-769b-9e19-e99fb5632d6c",
      "title": "...",
      "description": "...",
      "dataset": "..."
    },
    "conceptual_blocks": [
      {
        "block_id": "019c3858-3024-77e6-816a-4b2c1838e422",
        "name": "Первичный обзор данных",
        "description": "...",
        "criteria": [
          {
            "criterion_id": "019c3858-7664-7899-8675-66bf8917de9c",
            "criterion_description": "Явно загружен датасет Telco Customer Churn из файла в pandas DataFrame."
          }
          // … more criteria
        ]
      }
      // … more blocks
    ]
  }
}
~~~

---

## 2. Solution Metadata (`solutions_metadata.json`)

`solutions_metadata.json` is a JSON array. Each element links a solution notebook to a case and enumerates the criteria that were **not fulfilled**.

| Field            | Meaning (as defined in the file)                                                                                              |
|------------------|-------------------------------------------------------------------------------------------------------------------------------|
| `case_id`        | UUID of the case (matches the `case_id` in the case JSON).                                                                   |
| `solution_id`    | Relative path to the notebook file (`solution_variant_*.ipynb`).                                                             |
| `violated_criteria` | List of `criterion_id` values that **failed** for this solution. If the array is empty, no criteria failed.                 |

**Example element (ideal solution):**

~~~json
{
  "case_id": "019c3857-81ef-769b-9e19-e99fb5632d6c",
  "solution_id": "tests/semantic_eval/testcases/new_cases/case1/solution_variant_ideal.ipynb",
  "violated_criteria": []
}
~~~

The list in `violated_criteria` is the **only source** that tells which criteria are considered failed for the associated notebook.

---

## 3. Benchmark

## Input data
- **Evaluation model** – JSON file containing the full set of criteria.  
- **LLM‑mentor API call** – generates textual feedback and a binary vector for a given solution.  
- **Correct annotation** – binary vector (ground‑truth) derived from the evaluation model for each solution.

## Result (JSON + Markdown/PDF report)
- **Execution log** – records of all runs.  
- **Metrics (grouped by hierarchy level)**  
  - FPR (false positive rate)  
  - FNR (false negative rate)  
  - Generation cost (e.g., token usage)  
  - Generation latency (time)  
  - Flip‑rate (impact of provider non‑determinism)  

### Statistics for each metric (grouped by hierarchy level)
- Global aggregate (per grouping level)  
- Weighted mean  
- Weighted 90 % percentile  
- Weighted standard deviation  
- 95 % Confidence Interval for the mean  
- 95 % Confidence Interval for the 90 % percentile  
- 95 % Confidence Interval for the standard deviation  
- Internal dispersion (provider variability)  
- External dispersion (content variability)  
- 95 % prediction interval for the metric
---

## 4. How the Dataset Is Constructed

1. **Load all case files** (`case_XX_*.json`).  
   - For each case, extract the ordered list of all `criterion_id`s from all `conceptual_blocks`.  
   - This ordered list determines the vector length for that case.

2. **Read `solutions_metadata.json`.** For each record:  
   - Use `case_id` to locate the corresponding case file.  
   - Use `solution_id` to locate the notebook (`solution_variant_*.ipynb`).  
   - Use `violated_criteria` to create the ground‑truth binary vector (`0` for listed IDs, `1` otherwise).

3. **Create a dataset entry** containing:  
   - `case_id`  
   - Path to the notebook (`solution_id`)  
   - Ordered list of criteria (`criterion_id`s)  
   - Ground‑truth binary vector (`y_true`)

Each entry therefore represents **one solution** together with its **metadata** (`violated_criteria`) and the **reference vector** used by the benchmark.

---

## 5. What the Solutions and Their Metadata Represent

| Component                     | Representation                                                                                                                      |
|-------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| **Solution (notebook)**       | A Jupyter notebook (`solution_variant_*.ipynb`) that implements the assignment for the given case. The notebook file is identified by `solution_id`. |
| **Metadata (`violated_criteria`)** | The list of criterion IDs that the notebook failed to satisfy. It is the sole authoritative source indicating which binary elements should be `0` in the ground‑truth vector. |
| **Ground‑truth binary vector**| Derived from `violated_criteria`: `0` for each failed criterion, `1` for all others. This vector is used by the benchmark as the target against which model predictions are evaluated. |

Thus, the dataset consists of pairs **(notebook, metadata)** linked to a case, and the metadata directly drives the construction of the ground‑truth vector that the benchmark consumes.