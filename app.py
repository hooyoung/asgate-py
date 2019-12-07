import base64
import json
import nacl.utils
import nacl.secret
import os
import random
import time
from flask import Flask, jsonify, render_template, request


import sat


key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

box = nacl.secret.SecretBox(key)

with open("example_problem.json") as f:
  EXAMPLE_KNOWN = [frozenset(clause) for clause in json.load(f)]
  EXAMPLE_UNKNOWN = EXAMPLE_KNOWN  # TODO: use a different problem
with open("example_solution.json") as f:
  KNOWN_SOLUTION = frozenset(json.load(f))

app = Flask(__name__)

@app.route("/")
def index():
  return render_template("index.html")

def parse_challenge_id(challenge_id):
  challenge_id_ciphertext = base64.b64decode(challenge_id)
  challenge_id_json = box.decrypt(challenge_id_ciphertext)
  challenge_id_dict = json.loads(challenge_id_json)
  ts = float(challenge_id_dict["ts"])
  if abs(ts - time.time()) > 5*60:  # 5 min
    raise ValueError("Challenge timestamp out of range")
  return challenge_id_dict["problems"]

@app.route("/challenge")
def challenge():
  problems = []
  problems_public = []
  res = sat.random_restrict_unknown(EXAMPLE_UNKNOWN)
  if res is not None:
    public, mapping, partial = res
    problems.append(("UNKNOWN", mapping, partial))
    problems_public.append(public)
  public, mapping, partial = sat.random_restrict_known(EXAMPLE_KNOWN, KNOWN_SOLUTION)
  problems.append(("KNOWN", mapping, partial))
  problems_public.append(public)
  if random.randrange(0,2) == 0:
    problems = problems[::-1]
    problems_public = problems_public[::-1]
  problems_public = [[list(clause) for clause in problem] for problem in problems_public]

  challenge_id_dict = {
    "ts": str(time.time()),
    "problems": problems,
  }
  challenge_id_json = json.dumps(challenge_id_dict)
  challenge_id_ciphertext = box.encrypt(challenge_id_json.encode('utf8'))
  challenge_id = base64.b64encode(challenge_id_ciphertext).decode('ascii')
  script = render_template("solve.js", problems=json.dumps(problems_public))
  return jsonify({
    "challenge_id": challenge_id,
    "eval_me": script,
  })

@app.route("/content", methods=["GET","POST"])
def content():
  problems = parse_challenge_id(request.form["challenge_id"])
  k,assignment = json.loads(request.form["solution"])
  which,mapping,partial = problems[k]
  assignment = set(partial) | sat.transform(frozenset(assignment), mapping)
  example = {"KNOWN": EXAMPLE_KNOWN, "UNKNOWN": EXAMPLE_UNKNOWN}[which]
  if sat.verify(example, assignment):
    return render_template("content.html")
  else:
    raise ValueError

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
