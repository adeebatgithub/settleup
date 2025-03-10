import argparse
import sys

import models

NOC = "\033[0m"
GREEN = "\033[32m"
RED = "\033[31m"


def log(mode, text):
    colors = {"danger": RED, "success": GREEN}
    print(f"{colors.get(mode, NOC)} {text}{NOC}")


def error_exit(message):
    log("danger", message)
    sys.exit(1)


parser = argparse.ArgumentParser(description="SettleUp - A simple debt tracking CLI")

parser.add_argument("--add", choices=["user"], help="Add a user to the database")
parser.add_argument("-n", "--name", type=str, help="User's name")
parser.add_argument("-p", "--phone", type=str, help="User's phone")
parser.add_argument("-e", "--email", type=str, help="User's email")

parser.add_argument("--pay", choices=["me", "you"], help="Register a payment")
parser.add_argument("-u", "--user", type=str, help="User's name")
parser.add_argument("-a", "--amount", type=int, help="Payment amount")
parser.add_argument("-r", "--remark", type=str, help="Payment remark")

parser.add_argument("--show", action="store_true", help="Show user debt/payment history")

args = parser.parse_args()

if args.add == "user":
    if not args.name:
        error_exit("Error: -n (name) is required when adding a user.")
    if models.User.select().where(models.User.name == args.name).exists():
        error_exit("Error: User already exists.")
    try:
        user = models.User.create(name=args.name, phone=args.phone, email=args.email)
        models.Debt.create(user=user, amount=0)
        log("success", f"User created: {args.name} {args.phone or ''} {args.email or ''}")
    except Exception as e:
        error_exit(f"Error adding user: {str(e)}")

if args.pay:
    if not args.user or args.amount is None:
        error_exit("Error: -u (user) and -a (amount) are required for payments.")
    try:
        user = models.User.get_or_none(models.User.name == args.user)
        if not user:
            error_exit("Error: User not found.")
        debt = models.Debt.get(models.Debt.user == user)
        mode = "success"
        amount = args.amount
        if args.pay == "you":
            amount = -amount
            mode = "danger"
        debt.amount += amount
        debt.save()
        payment = models.Payment.create(user=user, amount=amount, remark=args.remark, total=debt.amount)
        log(
            mode,
            f"{user.name:<10}{abs(amount):<10}{abs(debt.amount):<10}{args.remark or '':<15}"
        )
    except Exception as e:
        error_exit(f"Error processing payment: {str(e)}")

if args.show:
    try:
        if not args.user:
            debts = models.Debt.select()
            for debt in debts:
                mode = "success" if debt.amount >= 0 else "danger"
                log(mode, f"{debt.user.name:<10}{abs(debt.amount):<10}")
        else:
            user = models.User.get_or_none(models.User.name == args.user)
            if not user:
                error_exit("Error: User not found.")
            debt = models.Debt.get(models.Debt.user == user)
            payments = models.Payment.select().where(models.Payment.user == user)
            print("History:")
            for payment in payments:
                text = f"[{payment.date}] {user.name:<8}{abs(payment.amount):<8}{abs(payment.total):<8}{payment.remark or '':<15}"
                log("danger" if payment.amount < 0 else "success", text)
            log("success" if debt.amount >= 0 else "danger", f"\n {user.name:<10}{debt.amount:<10}")
    except Exception as e:
        error_exit(f"Error retrieving user data: {str(e)}")
