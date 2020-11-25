from random import randint
from sys import exit
from math import ceil
import sqlite3


class BankSystem:

    def __init__(self):
        self.conn = sqlite3.connect('card.s3db')
        self.curs = self.conn.cursor()
        self.curs.execute("select number, pin, balance from card")
        self.accounts = {}
        rows = self.curs.fetchall()
        for row in rows:
            self.accounts[row[0]] = {"pin": row[1], "balance": row[2]}

    def louhn(self, card):
        nums = [int(x) for x in card]
        for i in range(len(nums)):
            if (i + 1) % 2 != 0:
                nums[i] *= 2
            if nums[i] > 9:
                nums[i] -= 9
        total = sum(nums)
        check = ceil(total / 10) * 10 - total
        return str(check)

    def create_account(self):
        card_number = "400000"
        for i in range(9):
            card_number += str(randint(0, 9))
        card_number += self.louhn(card_number)
        card_pin = ""
        for i in range(4):
            card_pin += str(randint(0, 9))
        self.accounts[card_number] = {"pin": card_pin, "balance": 0}
        self.curs.execute(f"insert into card (number, pin) values ({card_number}, {card_pin})")
        self.conn.commit()
        print(f"""
Your card has been created
Your card number:
{card_number}
Your card PIN:
{card_pin}
""")

    def main_menu(self):
        while True:
            print("""1. Create an account
2. Log into account
0. Exit""")
            n = int(input())
            if n == 1:
                self.create_account()
            elif n == 2:
                self.log_in()
            else:
                print("\nBye!")
                break

    def client_menu(self, card_number):
        while True:
            print("""1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit""")
            n = int(input())
            print()
            if n == 1:
                print(f"Balance: {self.accounts[card_number]['balance']}")
            elif n == 2:
                self.income(card_number)
            elif n == 3:
                self.transfer(card_number)
            elif n == 4:
                self.close_account(card_number)
                break
            elif n == 5:
                print("\nYou have successfully logged out!\n")
                break
            else:
                print("\nBye!")
                exit(0)
            print()

    def log_in(self):
        c_n = input("Enter your card number:\n")
        c_p = input("Enter your PIN:\n")
        if c_n not in self.accounts or self.accounts[c_n]['pin'] != c_p:
            print("\nWrong card number or PIN!\n")
        else:
            print("\nYou have successfully logged in!\n")
            self.client_menu(c_n)

    def check_louhn(self, card_num):
        check = self.louhn(card_num[:len(card_num) - 1])
        return check == card_num[-1]

    def transfer(self, card_from):
        print("Transfer")
        card_to = input("Enter card number:\n")
        if not self.check_louhn(card_to):
            print("Probably you made mistake in the card number. Please try again!")
        elif card_to not in self.accounts:
            print("Such a card does not exist.")
        elif card_to == card_from:
            print("You can't transfer money to the same account!")
        else:
            amount = int(input("Enter how much money you want to transfer:\n"))
            if self.accounts[card_from]["balance"] < amount:
                print("Not enough money!")
            else:
                self.curs.execute(f"update card set balance=balance-{amount} where number = {card_from}")
                self.curs.execute(f"update card set balance=balance+{amount} where number = {card_to}")
                self.accounts[card_from]["balance"] -= amount
                self.accounts[card_to]["balance"] += amount
                self.conn.commit()
                print("Success")

    def income(self, card_number):
        income = int(input("Enter income:\n"))
        self.curs.execute(f"update card set balance=balance+{income} where number = {card_number}")
        self.accounts[card_number]["balance"] += income
        print("Income was added!")
        self.conn.commit()

    def close_account(self, card_number):
        self.curs.execute(f"delete from card where number={card_number}")
        self.accounts.pop(card_number, None)
        self.conn.commit()


def create_table():
    conn = sqlite3.connect('card.s3db')
    curs = conn.cursor()
    curs.execute("""create table if not exists card(
id INTEGER,
number TEXT,
pin TEXT,
balance INTEGER DEFAULT 0
)""")


create_table()
system = BankSystem()
system.main_menu()
