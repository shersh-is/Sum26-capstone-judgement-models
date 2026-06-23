# Binary-Vector Conversion

The feedback generator gives us a binary vector built on the current version of the evaluation model. Each criterion of that model gets a 0/1 value. The benchmark, though, can only score a vector if it has the same shape as the ideal model of the same task. The current model usually has a different number and structure of criteria than the ideal one, so before we can measure anything we have to move the vector from one criteria space into the other.

So the converter does two things:
1. Build a mapping between the current model's criteria(A) and the ideal model's criteria(B). This is the hard part.
2. Project the 0/1 values through that mapping into a vector over B. This part is basically the rule set already written in our spec.

Step 1: label matching, which is about finding correspondences between elements of two different schemas. Rahm and Bernstein's survey is the standard map of this space and splits matchers into element-level vs structure-level and language-based vs constraint-based, which gives us a useful vocabulary for everything below (Rahm & Bernstein, 2001).

Step 2: Once we have the A->B mapping, our spec already defines the projection, and it is deterministic:
- a B that has exactly one A=1 mapped to it -> B = 1;
- a B that has several A=1 mapped to it -> B = 1, and we flag it as a structural non-optimality (the current model split one ideal criterion into many);
- an A with no mapping to any B -> count it as a separate false positive (the current model invented a criterion that does not exist in the ideal one);
- a B with no A=1 mapped to it -> B = 0.
Nothing here needs machine learning. The intelligence all sits in step 1, in how good the mapping is. So the methods below are really methods for building the mapping, ordered from cheap-and-simple to smart-and-expensive.

## Method 1: String

Compare each criterion text to each other one with plain string measures: token overlap, edit distance, or TF-IDF cosine. Whatever clears a threshold becomes a candidate match. In Rahm and Bernstein's taxonomy this is an element-level, language-based matcher (Rahm & Bernstein, 2001), and the LLM study below uses exactly this kind of string-similarity matcher as its baseline (Parciak et al., 2024).
It is fast, fully transparent, costs nothing, and gives us a baseline number to beat. The catch is that our criteria are full natural-language sentences. String similarity will miss those. It works as a sanity check, but it is not good enough on its own.

## Method 2: Embedding-based semantic matching

Encode every criterion (current and ideal) into a sentence embedding, then match by cosine similarity, taking the best match above a threshold or the top-k candidates. Sentence-BERT is the standard tool here: it was built specifically so that semantically similar sentences land close together and can be compared with cosine similarity, which is exactly our situation (Reimers & Gurevych, 2019). In practice this is the sentence-transformers library plus a similarity threshold we tune on our own cases.
It handles paraphrase and synonyms, which is where Method 1 falls apart, and it is still cheap and deterministic (no API calls per match once the model is loaded). The weak spot is that a single similarity score does not really understand logical relationships. It cannot, on its own, tell us "this one ideal criterion was split into three current ones," which is one of the cases our projection rules care about.

## Method 3: LLM-based matching/conversion

Give an LLM both lists of criteria (with their descriptions) and ask it to produce the mapping, or even output the converted vector directly. This is the route our spec points at LLM conversion, and there is now solid experimental work on it. Parciak et al. test off-the-shelf LLMs for schema matching using only names and descriptions, compare different "task scopes" (how much context you put in the prompt), and also look at how much human verification the results need (Parciak et al., 2024). Matchmaker pushes this further into a self-improving LLM program that works zero-shot, without any labelled training pairs, which matters because we do not have a big set of pre-labelled A->B mappings (Seedat & van der Schaar, 2024).
LLM can read the full sentence, reason about meaning, and naturally express many-to-one and "no match" relationships, which are exactly the cases our rules need flagged. The trade-offs are the usual ones: cost per call, latency, and non-determinism (the same flip-rate concern the benchmark already measures). So the LLM should not run unsupervised, which is what the last two methods address.

## Method 4: Hybrid embedding retrieval + LLM rerank

Do not ask the LLM to compare every A against every B. Instead run a two-phase pipeline: phase one uses cheap embeddings to retrieve a short list of candidate matches, phase two uses the LLM only to rerank or confirm that short list. This is exactly the design of Magneto, which combines small (embedding) models for retrieval with a large model for reranking to stay both accurate and cost-effective (Liu et al., 2024).
It keeps the number of LLM calls (and therefore cost and latency) low, while still getting LLM-level judgement on the cases that actually matter. For a loop that runs over 75+ solutions repeatedly, that keeps the experiment affordable.

## Method 5: Human oversight

The spec does not say - LLM conversion, it says: "LLM conversion with human oversight," and that is a deliberate, well-supported choice. The practical pattern is to let the automated matcher handle the clear cases and route only the uncertain ones to a person: low-confidence matches, many-to-one cases, and criteria with no match at all. Work on human-in-the-loop schema matching shows the value of combining a human matcher with an algorithmic one and calibrating or filtering the human decisions rather than trusting either alone (Shraga & Gal, 2021).
It keeps the converter honest exactly where it is weakest (structural mismatches between model versions) without forcing a human to check every single vector. It also gives us a natural place to record the structural non-optimality and extra-criterion false positive flags from the rules.

## References

1. Rahm, E., & Bernstein, P. A. (2001). A survey of approaches to automatic schema matching. The VLDB Journal, 10(4), 334-350. https://doi.org/10.1007/s007780100057
2. Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. EMNLP-IJCNLP 2019. https://aclanthology.org/D19-1410/ 
3. Parciak, M., Vandevoort, B., Neven, F., Peeters, L. M., & Vansummeren, S. (2024). Schema Matching with Large Language Models: an Experimental Study. https://arxiv.org/abs/2407.11852
4. Seedat, N., & van der Schaar, M. (2024). Matchmaker: Self-Improving Large Language Model Programs for Schema Matching. https://arxiv.org/abs/2410.24105
5. Liu, Y., Pena, E., Santos, A., Wu, E., & Freire, J. (2024). Magneto: Combining Small and Large Language Models for Schema Matching. https://arxiv.org/abs/2412.08194
6. Shraga, R., & Gal, A. (2021). PoWareMatch: a Quality-aware Deep Learning Approach to Improve Human Schema Matching. ACM Journal of Data and Information https://arxiv.org/abs/2109.07321Quality. https://arxiv.org/abs/2109.07321