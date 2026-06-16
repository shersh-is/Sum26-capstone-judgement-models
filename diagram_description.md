# Diagram Description

The diagram shows the experiment loop - the loop we use to slowly improve the evaluation model(judgement model). The evaluation model is the set of binary, natural-language criteria that we use to check task solutions.
The point of the whole project is to extract this model from the stream of mentor feedback, instead of asking experts to write it by hand. So the loop takes mentor-style feedback, turns it into criteria, and keeps refining them.
Two things run in parallel inside the loop:
- The text feedback is what the evaluation model is actually rebuilt from. The application reads the natural-language feedback and generates/updates the criteria.
- The binary-vector path (generate a vector → reshape it → run the benchmark) is what measures how good the current model is and how fast it converges. It scores the model; it does not build it.

All the blocks are split into three groups.

## The three groups:

### 1. Provided resources

- Primary task dataset - the original set of 3 cases and 9 solutions(three per case: ideal/with errors/with opposite errors). The criteria themselves live in a JSON criteria model; each solution is checked against that model and carries a violated-criteria annotation - the list of criteria it failed.
- Feedback generator and benchmark(runnable) - one runnable box that does two jobs:
 - the feedback generator takes an evaluation model(JSON) and a solution(`.ipynb`) and returns both a binary vector and unstructured natural-language feedback(it is deliberately not perfect, just like a real expert);
 - the benchmark takes an evaluation model, the LLM-mentor API call, and the correct annotation, and returns a log plus the metrics(FPR, FNR, generation cost, generation speed, flip rate) with their statistics.

### 2. Experiment loop

- Feedback on the current solution - what the feedback generator returns for one specific solution on the current version of the evaluation model: the natural-language review plus a binary vector.
- Converted binary feedback vector - the binary vector after it has been reshaped to match the "ideal" model. The raw vector is built on the current model, which usually has a different number and structure of criteria than the ideal model for the same task. The benchmark can only compare two vectors of the same shape, so we have to convert it first. In practice this is an LLM conversion with human oversight.
- Updated evaluation model - the result of the cycle: the improved set of criteria after the changes are applied. It also closes the loop, because it becomes the "current model" for the next round.

### 3. To be built

- Application/pipeline to manage the experiment - the part that constructs the evaluation model from the stream of natural-language feedback and drives the whole experiment(FastAPI + Streamlit, or a Jupyter-notebook pipeline).
- Converter of evaluation-model vectors - reshapes the binary vector of the *current* model into a vector compatible with the ideal model of the same task, so the benchmark can compare them fairly. It does not turn text into a vector - the vector already exists; it only changes its shape.
- Extended task dataset(75+ solutions) - a bigger base of 75+ solutions, with errors evenly spread across one shared error taxonomy. We need the volume and the even spread so the benchmark can measure convergence properly, not just on a handful of examples.
- Evaluation-model diff generator - produces the next version of the evaluation model, i.e. the change from the current criteria to the updated ones. This is what feeds the "Updated evaluation model" block.

## How the data moves

1. The primary task dataset goes into the feedback generator and benchmark - so it runs on these cases.
2. The box sends its result two ways: to the left into feedback on the current solution, and to the right into the application that manages the experiment.
3. The feedback on the current solution goes into the vector converter.
4. The converter sends a result up to the application and produces the converted binary feedback vector below it.
5. The application and the extended dataset are linked both ways - the application pulls solutions from the dataset and also feeds it.
6. The converted binary vector and the data from the application come together at the diff generator.
7. The diff generator produces the updated evaluation model, which goes back into the next iteration.

## Why we built it this way

The whole point is to make the extraction and improvement of the evaluation model **controllable and repeatable**. Instead of relying on an expert's intuition (which is hard to formalise, goes stale, and conflicts between experts), we lean on the steady stream of mentor feedback and turn it into a stable set of verifiable criteria.

The split into three groups is what makes the diagram useful: the "Provided resources" and "Experiment loop" groups show the parts that already work, and the "To be built" group shows exactly which pieces are still missing before the loop can run end to end on its own.