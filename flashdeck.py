import argparse
import logging
import json
import pathlib

letters = [
  ("α", "alpha (lowercase)"),
  ("β", "beta (lowercase)"),
  ("γ", "gamma (lowercase)"),
  ("δ", "delta (lowercase)"),
  ("ε", "epsilon (lowercase)"),
  ("ζ", "zeta (lowercase)"),
  ("η", "eta (lowercase)"),
  ("θ", "theta (lowercase)"),
  ("ι", "iota (lowercase)"),
  ("κ", "kappa (lowercase)"),
  ("λ", "lambda (lowercase)"),
  ("μ", "mu (lowercase)"),
  ("ν", "nu (lowercase)"),
  ("ξ", "xi (lowercase)"),
  ("ο", "omicron (lowercase)"),
  ("π", "pi (lowercase)"),
  ("ρ", "rho (lowercase)"),
  ("σ", "sigma (lowercase)"),
  ("τ", "tau (lowercase)"),
  ("υ", "upsilon (lowercase)"),
  ("φ", "phi (lowercase)"),
  ("χ", "chi (lowercase)"),
  ("ψ", "psi (lowercase)"),
  ("ω", "omega (lowercase)"),
  ("Α", "alpha (uppercase)"),
  ("Β", "beta (uppercase)"),
  ("Γ", "gamma (uppercase)"),
  ("Δ", "delta (uppercase)"),
  ("Ε", "epsilon (uppercase)"),
  ("Ζ", "zeta (uppercase)"),
  ("Η", "eta (uppercase)"),
  ("Θ", "theta (uppercase)"),
  ("Ι", "iota (uppercase)"),
  ("Κ", "kappa (uppercase)"),
  ("Λ", "lambda (uppercase)"),
  ("Μ", "mu (uppercase)"),
  ("Ν", "nu (uppercase)"),
  ("Ξ", "xi (uppercase)"),
  ("Ο", "omicron (uppercase)"),
  ("Π", "pi (uppercase)"),
  ("Ρ", "rho (uppercase)"),
  ("Σ", "sigma (uppercase)"),
  ("Τ", "tau (uppercase)"),
  ("Υ", "upsilon (uppercase)"),
  ("Φ", "phi (uppercase)"),
  ("Χ", "chi (uppercase)"),
  ("Ψ", "psi (uppercase)"),
  ("Ω", "omega (uppercase)"),
]

def main():
  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument("infile")
  arg_parser.add_argument("outfile")
  args = arg_parser.parse_args()
  del arg_parser

  input_path = pathlib.Path(args.infile)
  output_path = pathlib.Path(args.outfile)
  del args

  logging.info("Reading %s", input_path)
  with input_path.open("rb") as f:
    data = json.load(f)

  if len(data) != 1:
    raise Exception(f"len(data) should be 1, but got {len(data)}")

  cardlist = []
  nextId = 0
  for (letter, letter_name) in letters:
    nextId += 1
    cardlist.append({
      "id": nextId,
      "deckId": 1,
      "ordinal": nextId,
      "question": letter,
      "questionImage": "",
      "questionVoice": "",
      "answer": letter_name,
      "answerImage": "",
    })

  data[0]["cardList"] = cardlist
  logging.info("Writing %s", output_path)
  with output_path.open("wt", encoding="utf8") as f:
    json.dump(data, f, indent=2)



if __name__ == "__main__":
  main()
