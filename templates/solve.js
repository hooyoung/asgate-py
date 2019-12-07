(function() {
  var problems = {{ problems }};
  var solved = -1;
  var soln = [];
  ploop:
  for (var p = 0; p < problems.length; p++) {
    var clauses = problems[p];
    var assignment = [];
    var N = 0;
    for (var clause of clauses) {
      for (var lit of clause) {
        if (Math.abs(lit) > N) {
          N = Math.abs(lit);
        }
      }
    }
    for (var i = 1; i <= N; ++i) {
      assignment[i] = false;
    }
    while (true) {
      var contra = false;
      cloop:
      for (var clause of clauses) {
        for (var lit of clause) {
          if (lit > 0 && assignment[lit] || lit < 0 && !assignment[-lit]) {
            continue cloop;
          }
        }
        contra = true;
        break;
      }
      console.log(JSON.stringify(assignment));
      if (!contra) {
        solved = p;
        for (var i = 1; i <= N; ++i) {
          soln.push(assignment[i] ? i : -i);
        }
        break ploop;
      }
      for (var i = 1; i <= N; i++) {
        if (!assignment[i]) {
          assignment[i--] = true;
          while (i) {
            assignment[i--] = false;
          }
          break;
        }
      }
      if (i > N) {
        break;
      }
    }
  }
  return [solved, soln];
})()
