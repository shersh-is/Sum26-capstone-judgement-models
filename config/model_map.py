from pydantic import BaseModel
from typing import Iterator, Iterable, List
import json


MODEL_MAP_PATH = "config/model_map.json"


class Model(BaseModel):
    name: str
    projected_fitness_score: float
    projected_performance_score: float
    projected_cost_score: float
    no_reasoning_support: bool
    structured_generation_support: bool
    logprobs_support: bool
    reasoning_support: bool
    structured_generation_with_reasoning_support: bool
    logprobs_with_reasoning_support: bool


with open(MODEL_MAP_PATH) as file:
    mapping = json.load(file)
models = [Model.model_validate(item) for item in mapping]


class ModelQuery:
    """LINQ-style query builder for Model instances."""
    def __init__(self, items: Iterable[Model] = None):
        self._items = items if items is not None else models
    
    def _chain(self, new_items: Iterable[Model]) -> 'ModelQuery':
        """Create a new query with transformed items."""
        return ModelQuery(new_items)
    
    def sorted_by_performance(self) -> 'ModelQuery':
        """Sort by projected performance score."""
        return self._chain(sorted(self._items, key=lambda m: m.projected_performance_score, reverse=True))
    
    def sorted_by_cost(self) -> 'ModelQuery':
        """Sort by projected cost score."""
        return self._chain(sorted(self._items, key=lambda m: m.projected_cost_score, reverse=False))
    
    def sorted_by_fitness(self) -> 'ModelQuery':
        """Sort by projected fitness score."""
        return self._chain(sorted(self._items, key=lambda m: m.projected_fitness_score, reverse=True))
    
    def filtered_by_full_no_reasoning_support(self) -> 'ModelQuery':
        """Select models with support for completion, logprobs, and structured generation without reasoning."""
        return self._chain(filter(
            lambda m: m.no_reasoning_support 
                      and m.structured_generation_support
                      and m.logprobs_support,
            self._items
        ))
    
    def filtered_by_full_reasoning_support(self) -> 'ModelQuery':
        """Select models with simulteneous reasoning, logprobs, and structured generation support."""
        return self._chain(filter(
            lambda m: m.reasoning_support 
                      and m.structured_generation_with_reasoning_support
                      and m.logprobs_with_reasoning_support,
            self._items
        ))
    
    def top(self, n: int = 1) -> 'ModelQuery':
        """Take first n items."""
        return self._chain(self._items[:n])
    
    def names(self) -> Iterator[str]:
        """Return iterator of model names."""
        return map(lambda m: m.name, self._items)
    
    def to_list(self) -> List[Model]:
        """Convert to list of Models."""
        return list(self._items)
    
    def __iter__(self) -> Iterator[Model]:
        """Allow iteration over the query results."""
        return iter(self._items)
