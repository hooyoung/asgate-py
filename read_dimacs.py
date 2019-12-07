#!/usr/bin/env python

import os
import json

FN = os.path.expanduser("~/Downloads/incremental/experiment/essentials/inputs/fla-barthel-200-2.cnf")

# These aren't really used
maxvar = 0
nclauses = 0

clauses = []
current_clause = []
with open(FN) as f:
  for line in f:
    if line.startswith("c"):
      continue
    if line.startswith("p cnf "):
      maxvar,nclauses = map(int, line.split()[2:])
      continue
    current_clause.extend(map(int, line.split()))
    if current_clause and current_clause[-1] == 0:
      clauses.append(current_clause[:-1])
      current_clause = []

assert not current_clause
print(json.dumps(clauses, indent=2))
