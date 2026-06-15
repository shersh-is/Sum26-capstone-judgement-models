# Project Data Overview 

## 1. Core Entities

| Entity | File / Object | Contents | Link to Other Entities |
|--------|----------------|----------|------------------------|
| **Case (Task)** | `case_XX_*.json` | Description of the assignment, list of **conceptual blocks** and **criteria** (what must be satisfied). | `case_id` (UUID) is referenced in `solutions_metadata.json` and in solution paths. |
| **Solution** | `solution_variant_*.ipynb` | Jupyter notebook that implements the steps of the case. The notebook itself does **not** contain explicit markers for criteria, but the code/comments indicate which criteria are satisfied or violated. | `solution_id` in `solutions_metadata.json` stores the relative path to the notebook. |
| **Evaluation Metadata** | `solutions_metadata.json` | For every *case ↔ solution* pair stores an array `violated_criteria` (list of `criterion_id` that were **not fulfilled**). | Connects a solution to its case via `case_id` and to the set of criteria defined in the case file. |

Together these three pieces form a **complete training / testing set** for the judgement model:

- **Ground‑truth** – a binary vector (see Section 2) derived from `violated_criteria`.  
- **LLM‑generated feedback** – natural‑language comments that will be produced during experiments.  
- **Benchmark** – a suite of metrics (FPR, FNR, cost, latency, flip‑rate, etc.) computed by comparing model predictions with the ground‑truth vectors.

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
* `conceptual_blocks` – logical decomposition of the assignment.  
* `criteria` – atomic, verifiable requirements. Their IDs become the **axis** of the binary ground‑truth vector.

### 2.2. Evaluation Metadata (`solutions_metadata.json`)

```json
[
  {
    "case_id": "<UUID of the case>",
    "solution_id": "<relative path to .ipynb>",
    "violated_criteria": [
      "<criterion_id_1>",
      "<criterion_id_2>"
      // … optionally empty list for a perfect solution
    ]
  }
  // … more records
]
```

* An empty `violated_criteria` array means the solution satisfies **all** criteria (perfect solution).  
* Presence of a `criterion_id` means that requirement is **not satisfied** (`0` in the ground‑truth vector).

---

## 3. Ground‑Truth Vector Construction

1. Load the case file (`case_XX_*.json`) and collect **all** `criterion_id`s in the order they appear (first block → first criterion, etc.).  
2. Locate the corresponding record in `solutions_metadata.json` (matching `case_id` and `solution_id`).  
3. Build a binary vector `y` of length `N = number_of_criteria`:

```text
y[i] = 0  if criterion_id_i is listed in violated_criteria
y[i] = 1  otherwise
```

The resulting `y` is the **ground‑truth** for that particular solution.

---

## 4. Relationship to the Benchmark

The benchmark is a **set of evaluation scripts** that:

1. **Load** a case and its solution.  
2. **Generate** the ground‑truth vector `y_true` as described above.  
3. **Invoke** the current judgement model (LLM‑based) on the notebook and obtain a predicted binary vector `y_pred`.  
4. **Compare** `y_pred` with `y_true` to compute:

   - **False‑Positive Rate (FPR)** = FP / (FP + TN)  
   - **False‑Negative Rate (FNR)** = FN / (FN + TP)  
   - **Flip‑rate** – proportion of identical prompts that yield different predictions (internal provider variance).  
   - **Cost** – number of tokens / API calls.  
   - **Latency** – time required to generate feedback.  

5. **Aggregate** the metrics at three hierarchy levels: per **criterion**, per **block**, per **case**, and **globally**.  
6. **Export** the results as JSON/Markdown/PDF reports containing raw numbers, weighted averages, percentiles, confidence intervals, and dispersion statistics (internal vs. external variance).

These metrics are exactly the ones listed in the project’s original specification (target FPR/FNR values, cost limits, latency limits, etc.).

---

## 5. Summary of the Data Flow

```text
case_XX_*.json  ──►  full list of criteria (ordered) ──► ground‑truth vector (y_true)
         ▲
         │                                 (via case_id)
solutions_metadata.json ──► list of violated criteria ──► y_true
         │
         ▼
solution_variant_*.ipynb  ──►  LLM judgement model  ──► predicted vector (y_pred)
                                   │
                                   ▼
                     Benchmark scripts → compute FPR, FNR, cost, latency, etc.
```

- The **ground‑truth** vector is derived **only** from the static JSON files.  
- The **benchmark** uses that vector as the reference against which the model’s predictions are evaluated.

--- 

### Кратко о причинах, почему ваш оригинальный файл «сломался»

| Что было в оригинальном файле | Почему это ломало рендеринг |
|------------------------------|-----------------------------|
| Открывающий ``` сразу после таблицы, но закрывающий — после `---` | Парсер закрыл блок кода преждевременно, `---` превратилось в `<hr>` и разорвало документ. |
| Внутри кода использовались ещё три обратные кавычки (```), но они не заключались в отдельный fenced‑блок | Внутренние ``` считались закрывающими, из‑за чего последующий JSON и текст стали обычным (не‑кодовым) текстом. |
| Не было пустой строки перед/после некоторых ``` | Некоторые парсеры (GitHub, GitLab) требуют хотя бы одну пустую строку, иначе заголовки и списки могут «притормозиться» внутри кода. |

Применив рекомендации выше, ваш README будет отображаться корректно на всех популярных платформах (GitHub, GitLab, Bitbucket, VS Code preview и т.д.).