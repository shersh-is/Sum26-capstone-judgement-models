# Construction of Judgement Models from Imperfect Human Expert Feedback
_Research Project from Dmitriy Prokopyev_

> A "perfect model" of an expert judgement is defined for ML tasks (similar to course assignmnets). Task: build an application that converges on an internal model that approximates the "true" expert judgement as closely possible given feedback on solution attempts.

This convergence occurs in cycles using the following steps:
1. Take the current specification of the ML task.
2. Generate a solution of the ML task of varying quality (both well designed and poorly designed solutions are valuable).
3. Generate a plain-text feedback for the solution based on the "perfect model" (will be provided).
4. Generate a diff to the current task specifications (not using the "perfect model") that update the specifications to encourage avoiding the mistakes of the last solution.
5. Run the quality benchmark (will be provided) to evaluate the specification quality metrics using the "perfect model" as a baseline.

The goal of the project is to discover the architecture resulting in maximum metrics adjustment speed, or in other words to minimize the number of iterations required for adjustment to an unknown expert model. There is no fixed goal in metrics, rather the aim is to show the progress across iterations (the judgement model being constructed faster and faster). Interface requirements are minimal, the most important part is benchmark optimization.

## Technological Stack
Backend: Python + FastAPI\
Frontend: Streamlit\
LLM API: AITunnel (the customer provides access and runway budget)\
Benchmark integration: Python or manual (either allowed)\
Databases: Not required, direct file storage along with git versioning is sufficient\
VCS: Git + GitHub

## Expected Result
1. Implementation of the judgement model constructor in a repository
2. Generated benchmark reports history (already automated in benchmark)
3. A short research report visually demonstrating adjustment quality accross iterations (at least 2) through metrics graphs, associated with improvement hypotheses
