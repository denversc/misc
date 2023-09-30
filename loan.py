# Loan Payment Calculator


def main():
  a = 174251.15  # principal
  n = (26 * 10) + 79  # num payment periods
  r = 0.061 / 26  # interest per period

  p = calculate_periodic_payment(a, n, r)
  p = round(p, 2)

  print(f"a=${a}")
  print(f"n={n}")
  print(f"r={r}")
  print(f"p=${p}")

  print_payment_schedule(a, n, r, p)


def calculate_periodic_payment(a: float, n: int, r: float) -> float:
  return a / ((((1 + r) ** n) - 1) / (r * ((1 + r) ** n)))


def print_payment_schedule(a: float, n: int, r: float, p: float, limit: int | None = None) -> float:
  principal_remaining = a
  total_interest_paid = 0
  total_principal_paid = 0

  i = 0
  while True:
    if i >= n:
      break
    if limit is not None and i >= limit:
      break
    i += 1

    payment_towards_interest = round(principal_remaining * r, 2)
    payment_towards_principal = p - payment_towards_interest
    total_interest_paid += payment_towards_interest
    total_principal_paid += payment_towards_principal
    principal_before = principal_remaining
    principal_remaining -= payment_towards_principal

    print(
        f"{i:02} "
        f"${principal_before} "
        f"${p} "
        f"${payment_towards_principal} "
        f"${payment_towards_interest}"
    )

  print()
  print(f"Starting Amount:  ${a}")
  print(f"Ending Amount:    ${round(principal_remaining, 2)}")
  print(f"Principal Repaid: ${round(total_principal_paid, 2)}")
  print(f"Interest Paid:    ${round(total_interest_paid, 2)}")


if __name__ == "__main__":
  main()
