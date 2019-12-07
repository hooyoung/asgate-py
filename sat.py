from typing import List, Union, Set, Optional, Tuple
import random

def verify(clauses, assignment):
  anti = set(-lit for lit in assignment)
  if assignment & anti:
    return False
  for clause in clauses:
    good = False
    for lit in clause:
      if lit in assignment:
        good = True
        break
    if not good:
      return False
  return True

def partial_apply(clauses: List[frozenset], lits: Union[frozenset, set]) -> Optional[Tuple[List[frozenset], frozenset]]:
  """Returns (new clauses, deduced units), or None if found not satisfiable after partial assignment"""
  contra_lits = {-lit for lit in lits}
  if lits & contra_lits:
    return None
  units: Set[int] = set()
  out = []
  for clause in clauses:
    if clause & lits:
      continue
    clause = clause - contra_lits
    if not clause:
      return None
    if len(clause) == 1:
      units |= clause
    else:
      out.append(clause)
  if units:
    if units & contra_lits:
      return None
    res = partial_apply(out, units)
    if res is None:
      return None
    out, newunits = res
    return out, newunits | units
  return out, frozenset(units)

problem_size = len

ALLOWABLE_SIZE = 17

def permute_problem(clauses: List[frozenset]) -> Tuple[List[frozenset], List[int]]:
  """First retval is transformed clauses.
  
  Second retval is [lit(1), lit(2), ...] where lit(i) is the literal corresponding to i(=TRUE) in the original problem."""
  used = list({abs(lit) for clause in clauses for lit in clause})
  random.shuffle(used)
  mapping = [random.choice([v,-v]) for v in used]
  rev = {}
  for i,liti in enumerate(mapping):
    rev[liti] = i + 1
    rev[-liti] = -i - 1
  transformed = [frozenset({rev[lit] for lit in clause}) for clause in clauses]
  return transformed, mapping

def sign(n):
  return 1 if n > 0 else -1

def transform(assignment: frozenset, mapping: List[int]) -> frozenset:
  return frozenset(mapping[abs(lit) - 1] * sign(lit) for lit in assignment)

def random_restrict_unknown(clauses: List[frozenset]) -> Optional[Tuple[List[frozenset], List[int], List[int]]]:
  """Return (new clauses, mapping, applied literals) or None."""
  used_set = {abs(lit) for clause in clauses for lit in clause}
  restriction = []
  while problem_size(clauses) > ALLOWABLE_SIZE:
    v = random.choice(list(used_set))
    used_set.remove(v)
    lit = random.choice([v,-v])
    res = partial_apply(clauses, {lit})
    if res is not None:
      clauses, units = res
      restriction.append(lit)
      restriction.extend(units)
    else:
      res = partial_apply(clauses, {-lit})
      if res is None:
        return None  # TODO: is it worth implementing backtracking?
      clauses, units = res
      restriction.append(-lit)
      restriction.extend(units)
  transformed, mapping = permute_problem(clauses)
  return (transformed, mapping, restriction)

def random_restrict_known(clauses: List[frozenset], assignment: frozenset) -> Tuple[List[frozenset], List[int], List[int]]:
  """Return (new clauses, mapping, applied literals)."""
  assignment_set = set(assignment)
  restriction = []
  while problem_size(clauses) > ALLOWABLE_SIZE:
    lit = random.choice(list(assignment_set))
    assignment_set.remove(lit)
    res = partial_apply(clauses, {lit})
    assert res is not None, "Conflicting assignment"
    clauses, units = res
    restriction.append(lit)
    restriction.extend(units)
  transformed, mapping = permute_problem(clauses)
  return (transformed, mapping, restriction)

def testcase():
  """If we take an orig problem -> transformed,mapping,restriction via random_restrict_unknown,
  and let solution be a solution for transformed, restriction|transform(solution,mapping) should be a solution for the orig problem."""
  # TODO: find a more interesting test case
  orig_clauses = [frozenset({1,2,3}), frozenset({-3,4,5}), frozenset({-4,-5})]
  print(orig_clauses)
  assignment = frozenset({-4,5,3})
  new_clauses, mapping, restriction = random_restrict_unknown(orig_clauses)
  # TODO

  """Transforming new_clauses through the mapping should hopefully resemble the orig problem..."""
  mapped_new_clauses = [transform(clause,mapping) for clause in new_clauses]
  print(mapped_new_clauses,restriction, "vs.", orig_clauses)

if __name__ == '__main__':
  testcase()
