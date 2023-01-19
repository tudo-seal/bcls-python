import os
from abc import ABC
from collections import deque
from collections.abc import Iterator
from dataclasses import field, dataclass
from functools import partial, reduce, cached_property
from itertools import starmap
from multiprocessing import pool
from typing import Any, Callable, Optional, Tuple, TypeAlias

from .enumeration import ComputationStep
from .enumeration import EmptyStep
from .enumeration import Enumeration
from .subtypes import Subtypes
from .types import Arrow
from .types import Intersection
from .types import Sequence
from .types import Type
from .setcover import minimal_covers, minimal_elements

MultiArrow: TypeAlias = Tuple[list[Type], Type]
State: TypeAlias = list['MultiArrow']
CoverMachineInstruction: TypeAlias = Callable[[State], Tuple[State, list['CoverMachineInstruction']]]

class PoolWrapper(pool.Pool):
    """ Only use multiprocessing, when on Posix """

    class DummyPool():
        """
        If not on a posix platform, use a DummyPool, that only exports a starmap.

        Only use the first two arguments (function and iterable) from the call, and ignore
        additional multiprocessing parameters. Then simply call the itertools.starmap function.
        """

        def starmap(self, function, iterable, *_args, **_kwargs):
            return starmap(function, iterable)

    def __enter__(self):
        if os.name == 'posix':
            return super().__enter__()
        return PoolWrapper.DummyPool()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if os.name == 'posix':
            return super().__exit__(exc_type, exc_val, exc_tb)
        return None


@dataclass(frozen=True)
class Rule(ABC):
    target: Type = field(init=True, kw_only=True)
    is_combinator: bool = field(init=True, kw_only=True)


@dataclass(frozen=True)
class Failed(Rule):
    target: Type = field()
    is_combinator: bool = field(default=False, init=False)

    def __str__(self):
        return f"Failed({str(self.target)})"


@dataclass(frozen=True)
class Combinator(Rule):
    target: Type = field()
    is_combinator: bool = field(default=True, init=False)
    combinator: object = field(init=True)

    def __str__(self):
        return f"Combinator({str(self.target)}, {str(self.combinator)})"


@dataclass(frozen=True)
class Apply(Rule):
    target: Type = field()
    is_combinator: bool = field(default=False, init=False)
    function_type: Type = field(init=True)
    argument_type: Type = field(init=True)

    def __str__(self):
        return f"@({str(self.function_type)}, {str(self.argument_type)}) : {self.target}"


@dataclass(frozen=True)
class Tree(object):
    rule: Rule = field(init=True)
    children: Tuple['Tree', ...] = field(init=True, default_factory=lambda: ())

    class Evaluator(ComputationStep):
        def __init__(self, outer: 'Tree', results: list[Any]):
            self.outer: 'Tree' = outer
            self.results = results

        def __iter__(self) -> Iterator[ComputationStep]:
            match self.outer.rule:
                case Combinator(_, c):
                    self.results.append(c)
                case Apply(_, _, _):
                    f_arg : list[Any] = []
                    yield Tree.Evaluator(self.outer.children[0], f_arg)
                    yield Tree.Evaluator(self.outer.children[1], f_arg)
                    self.results.append(partial(f_arg[0])(f_arg[1]))
                case _:
                    raise TypeError(f"Cannot apply rule: {self.outer.rule}")
            yield EmptyStep()

    def evaluate(self) -> Any:
        result: list[Any] = []
        self.Evaluator(self, result).run()
        return result[0]

    def __str__(self):
        match self.rule:
            case Combinator(_, _): return str(self.rule)
            case Apply(_, _, _): return f"{str(self.children[0])}({str(self.children[1])})"
            case _: return f"{str(self.rule)} @ ({', '.join(map(str, self.children))})"


@dataclass(frozen=True)
class InhabitationResult(object):
    targets: list[Type] = field(init=True)
    rules: set[Rule] = field(init=True)

    @cached_property
    def grouped_rules(self) -> dict[Type, set[Rule]]:
        result: dict[Type, set[Rule]] = dict()
        for rule in self.rules:
            group: Optional[set[Rule]] = result.get(rule.target)
            if group:
                group.add(rule)
            else:
                result[rule.target] = {rule}
        return result

    def check_empty(self, target: Type) -> bool:
        for rule in self.grouped_rules.get(target, {Failed(target)}):
            if isinstance(rule, Failed):
                return True
        return False

    @cached_property
    def non_empty(self) -> bool:
        for target in self.targets:
            if self.check_empty(target):
                return False
        return bool(self.targets)

    def __bool__(self) -> bool:
        return self.non_empty

    @cached_property
    def infinite(self) -> bool:
        if not self:
            return False

        reachable: dict[Type, set[Type]] = {}
        for (target, rules) in self.grouped_rules.items():
            entry: set[Type] = set()
            for rule in rules:
                match rule:
                    case Apply(target, lhs, rhs):
                        next_reached: set[Type] = {lhs, rhs}
                        entry.update(next_reached)
                    case _:
                        pass
            reachable[target] = entry

        changed: bool = True
        to_check: set[Type] = set(self.targets)
        while changed:
            changed = False
            next_to_check = set()
            for target in to_check:
                can_reach = reachable[target]
                if target in can_reach:
                    return True
                newly_reached = set().union(*(reachable[reached] for reached in can_reach))
                for new_target in newly_reached:
                    if target == new_target:
                        return True
                    elif new_target not in to_check:
                        changed = True
                        next_to_check.add(new_target)
                        can_reach.add(new_target)
                    elif new_target not in can_reach:
                        changed = True
                        can_reach.add(new_target)
            to_check.update(next_to_check)
        return False

    def size(self) -> int:
        if self.infinite:
            return -1
        maximum = self.raw.unsafe_max_size()
        size = 0
        values = self.raw.all_values()
        for _ in range(0, maximum+1):
            trees = next(values)
            size += len(trees)
        return size

    def __getitem__(self, target: Type) -> Enumeration[Tree]:
        if target in self.enumeration_map:
            return self.enumeration_map[target]
        else:
            return Enumeration.empty()

    @staticmethod
    def combinator_result(r: Combinator) -> Enumeration[Tree]:
        return Enumeration.singleton(Tree(r, ()))

    @staticmethod
    def apply_result(result: dict[Type, Enumeration[Tree]], r: Apply) -> Enumeration[Tree]:
        def mkapp(left_and_right):
            return Tree(r, (left_and_right[0], left_and_right[1]))

        def apf():
            return (result[r.function_type] * result[r.argument_type]) \
                    .map(mkapp).pay()
        applied = Enumeration.lazy(apf)
        return applied

    @cached_property
    def enumeration_map(self) -> dict[Type, Enumeration[Tree]]:
        result: dict[Type, Enumeration[Tree]] = dict()
        for (target, rules) in self.grouped_rules.items():
            _enum: Enumeration[Tree] = Enumeration.empty()
            for rule in rules:
                match rule:
                    case Combinator(_, _) as r:
                        _enum = _enum + InhabitationResult.combinator_result(r)
                    case Apply(_, _, _) as r:
                        _enum = _enum + InhabitationResult.apply_result(result, r)
                    case _:
                        pass
            result[target] = _enum
        return result

    @cached_property
    def raw(self) -> Enumeration[Tree | list[Tree]]:
        if not self:
            return Enumeration.empty()
        if len(self.targets) == 1:
            return self.enumeration_map[self.targets[0]]
        else:
            result: Enumeration[list[Tree]] = Enumeration.singleton([])
            for target in self.targets:
                result = (result * self.enumeration_map[target]).map(lambda x: [*x[0], x[1]])
            return result

    @cached_property
    def evaluated(self) -> Enumeration[Any | list[Any]]:
        if len(self.targets) == 1:
            return self.raw.map(lambda t: t.evaluate())
        else:
            return self.raw.map(lambda l: list(map(lambda t: t.evaluate(), l)))


class FiniteCombinatoryLogic(object):

    def __init__(self, repository: dict[object, Type], subtypes: Subtypes, processes=os.cpu_count()):
        self.processes = processes

        self.repository = repository
        with PoolWrapper(processes) as pool:
            self.splitted_repository: dict[object, list[list[MultiArrow]]] = \
                dict(pool.starmap(FiniteCombinatoryLogic._split_repo,
                     self.repository.items(),
                     chunksize=max(len(self.repository) // processes, 10)))
        self.subtypes = subtypes

    @staticmethod
    def _split_repo(c: object, ty: Type) -> Tuple[object, list[list[MultiArrow]]]:
        return c, FiniteCombinatoryLogic.split_ty(ty)

    @staticmethod
    def split_ty(ty: Type) -> list[list[MultiArrow]]:
        """Splits a type into a list of 0-ary, 1-ary, ..., n-ary multi-arrows."""

        def safe_split(xss: list[list[MultiArrow]]) -> Tuple[list[MultiArrow], list[list[MultiArrow]]]:
            return (xss[0] if xss else []), xss[1:]

        def split_rec(to_split: Type, srcs: list[Type], delta: list[list[MultiArrow]]) -> list[list[MultiArrow]]:
            match to_split:
                case Arrow(src, tgt):
                    xs, xss = safe_split(delta)
                    next_srcs = [src, *srcs]
                    return [[(next_srcs, tgt), *xs], *split_rec(tgt, next_srcs, xss)]
                case Intersection(sigma, tau) if sigma.is_omega:
                    return split_rec(tau, srcs, delta)
                case Intersection(sigma, tau) if tau.is_omega:
                    return split_rec(sigma, srcs, delta)
                case Intersection(sigma, tau):
                    return split_rec(sigma, srcs, split_rec(tau, srcs, delta))
                case _:
                    return delta

        return [] if ty.is_omega else [[([], ty)], *split_rec(ty, [], [])]

    def _dcap(self, sigma: Type, tau: Type) -> Type:
        if self.subtypes.check_subtype(sigma, tau):
            return sigma
        elif self.subtypes.check_subtype(tau, sigma):
            return tau
        else:
            return Intersection(sigma, tau)

    def _omega_rules(self, target: Type) -> set[Rule]:
        return {Apply(target, target, target),
                *map(lambda c: Combinator(target, c), self.splitted_repository.keys())}

    @staticmethod
    def _combinatory_expression_rules(combinator: object, arguments: list[Type], target: Type) -> set[Rule]:
        """Set of rules from combinatory expression `combinator(arguments1, ..., argumentn)`."""
        result: set[Rule] = set()
        arguments: deque[Type] = deque(arguments)
        while arguments:
            argument = arguments.pop()
            result.add(Apply(target, Arrow(argument, target), argument))
            target = Arrow(argument, target)
        result.add(Combinator(target, combinator))
        return result


    def inhabit(self, *targets: Type) -> InhabitationResult:
        # dictionary of type |-> sequence of combinatory expressions
        memo: dict[Type, deque[tuple[object, list[Type]]]] = dict()
        remaining_targets: deque[Type] = deque(targets)
        # intermediate rules (stopgap from prior fcl implementation)
        result: set[Rule] = set()
        while remaining_targets:
            target = remaining_targets.pop()
            if memo.get(target) is None:
                # target type was not seen before
                paths: list[Type] = list(target._organized())
                possibilities: deque[tuple[object, list[Type]]] = deque()
                memo.update({target : possibilities})
                if target.is_omega:
                    result |= self._omega_rules(target)
                else:
                    # try each combinator and arity
                    for combinator, splitted_types in self.splitted_repository.items():
                        for splitted_type in splitted_types:
                            contains = lambda m, t: self.subtypes.check_subtype(m[1], t)
                            # possibilities to cover target using targets of multi-arrows in splitted_type
                            covers = list(map(lambda c: list(map(lambda m: m[0], c)), minimal_covers(splitted_type, paths, contains)))
                            # intersect corresponding arguments of multi-arrows in each cover
                            accumulated_args = list(map(lambda c: reduce(lambda args1, args2: list(map(self._dcap, args1, args2)), c), covers))
                            compare_args = lambda greater, lesser: all(starmap(self.subtypes.check_subtype, zip(lesser, greater)))
                            # remove redundant argument vectors
                            subqueries = minimal_elements(accumulated_args, compare_args)
                            for subquery in subqueries:
                                temp = list(subquery)
                                temp.reverse()
                                possibilities.append((combinator, temp))
                                remaining_targets.extendleft(subquery)

        # convert memo into resulting set of rules
        for target, possibilities in memo.items():
            for combinator, arguments in possibilities:
                result |= self._combinatory_expression_rules(combinator, arguments, target)

        return InhabitationResult(targets=list(targets), rules=FiniteCombinatoryLogic._prune(result))

    @staticmethod
    def _ground_types_of(rules: set[Rule]) -> set[Type]:
        ground: set[Type] = set()
        next_ground: set[Type] = set(rule.target for rule in rules if rule.is_combinator)

        while next_ground:
            ground |= next_ground
            next_ground = set()
            for rule in rules:
                match rule:
                    case Apply(target, function_type, argument_type) if (function_type in ground
                                                                         and argument_type in ground
                                                                         and target not in ground):
                        next_ground.add(target)
                    case _: pass
        return ground

    @staticmethod
    def _prune(rules: set[Rule]) -> set[Rule]:
        ground_types: set[Type] = FiniteCombinatoryLogic._ground_types_of(rules)
        result = set()
        for rule in rules:
            match rule:
                case Apply(target, _, _) if target not in ground_types:
                    result.add(Failed(target))
                case Apply(_, function_type, argument_type) if not (function_type in ground_types
                                                                    and argument_type in ground_types):
                    continue
                case _:
                    result.add(rule)
        return result
