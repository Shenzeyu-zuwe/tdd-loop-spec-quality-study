# ClassEval_8 — BankAccount

## Class description
```
"""
    This is a class as a bank account system, which supports deposit money, withdraw money, view balance, and transfer money.
    """
```

## Required imports (prepend to solution.py)
```python

```

## Skeleton (to implement)
```python
class BankAccount:
    """
    This is a class as a bank account system, which supports deposit money, withdraw money, view balance, and transfer money.
    """

    def __init__(self, balance=0):
        """
        Initializes a bank account object with an attribute balance, default value is 0.
        """
        self.balance = balance

    def deposit(self, amount):
        """
        Deposits a certain amount into the account, increasing the account balance, return the current account balance.
        If amount is negative, raise a ValueError("Invalid amount").
        :param amount: int
        """

    def withdraw(self, amount):
        """
        Withdraws a certain amount from the account, decreasing the account balance, return the current account balance.
        If amount is negative, raise a ValueError("Invalid amount").
        If the withdrawal amount is greater than the account balance, raise a ValueError("Insufficient balance.").
        :param amount: int
        """

    def view_balance(self):
        """
        Return the account balance.
        """

    def transfer(self, other_account, amount):
        """
        Transfers a certain amount from the current account to another account.
        :param other_account: BankAccount
        :param amount: int
        >>> account1 = BankAccount()
        >>> account2 = BankAccount()
        >>> account1.deposit(1000)
        >>> account1.transfer(account2, 300)
        account1.balance = 700 account2.balance = 300
        """
```

## Target file
`solution.py` — write the completed class here. Do **not** modify
any other file in the project root.

## Verification discipline
Every test intent in feature_list.json is a **RUNTIME CHECK**. The
Tester must write a temp Python script, execute it via the Bash
tool, and compare actual stdout to expected. Code review alone is
never sufficient.