import argparse
import models

NOC = "\033[0m"
GREEN = "\033[32m"
RED = "\033[31m"

def log(mode, text):
    if mode == "danger":
        print(f"{RED} {text}{NOC}")
    if mode == "success":
        print(f"{GREEN} {text}{NOC}")

parser = argparse.ArgumentParser(description="settleUp")

parser.add_argument("--add", choices=["user"], help="add entries to database (user)")
parser.add_argument("-n", "--name", type=str, help="user's name")
parser.add_argument("-p", "--phone", type=str, help="user's phone")
parser.add_argument("-e", "--email", type=str, help="user's email")

parser.add_argument("--pay", choices=["me", "you"], help="add payment")
parser.add_argument("-u", "--user", type=str, help="user's name")
parser.add_argument("-a", "--amount", type=int, help="payment amount")
parser.add_argument("-r", "--remark", type=str, help="remark")

parser.add_argument("--show", action="store_true", help="show whats on a user")

args = parser.parse_args()

if args.add == "user":
    if not args.name:
        parser.error("-n is required")
    if models.User.select().where(models.User.name==args.name).exists():
        print("user already exists'")
        quit()
    user = models.User(
        name=args.name,
        phone=args.phone,
        email=args.email
    )
    user.save()
    models.Debt.create(user=user, amount=0)
    print(f"User created: {args.name} {args.phone} {args.email}")

if args.pay:
    if not args.user and not args.amount:
        parser.error("-u and -a is required")
    user = models.User.get(models.User.name==args.user)
    debt = models.Debt.get(models.Debt.user==user)
    mode = "success"
    if args.pay == "you":
        args.amount = 0 - args.amount
        mode = "danger"
    payment = models.Payment(
        user=user,
        amount=args.amount,
        remark=args.remark
    )
    debt.amount = debt.amount + args.amount
    debt.save()
    payment.total = debt.amount
    payment.save()
    log(
        mode,
        f"{user.name:<10}{abs(args.amount):<10}{abs(debt.amount):<10}{args.remark if args.remark is not None else '':<15}"
    )

if args.show:
    if not args.user:
        debts = models.Debt.select()
        for debt in debts:
            mode = "success"
            if debt.amount < 0:
                mode = "danger"
            log(
                mode,
                f" {debt.user.name:<10}{abs(debt.amount):<10}"
            )
        quit()

    user = models.User.get(models.User.name==args.user)
    debt = models.Debt.get(models.Debt.user==user)
    payments = models.Payment.get(models.Payment.user==user)
    print("History:\n")
    for payment in payments.select():
        text = f"[{payment.date}] {user.name:<8}{abs(payment.amount):<8}{abs(payment.total):<8}{payment.remark if payment.remark is not None else '':<15}"
        if payment.amount < 0:
            log("danger", text)
        else:
            log("success", text)
    mode = "success"
    if debt.amount < 0:
        mode = "danger"
    log(
        mode,
        f"\n {user.name:<10}{debt.amount:<10}"
    )
