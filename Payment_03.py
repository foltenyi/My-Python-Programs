# Longest line 90 chars
#
# Version 03: Set column width according to the numbers. Is anything in f formatting
#     like in C, e.g. "%-*.*s ",i,i,<string> ? Yes, the f-string has!
#
# Version 02: Make m.Month, m.PaymentPrincChange, m.Interest, m.Loan to work
#
# Version 01: Make m.Years, m.Total, m.DurationPrincChange to work

import sys, os
import copy
from enum import IntEnum, Enum, auto

import inspect
def ln():
  return f'{inspect.currentframe().f_back.f_lineno:3d}'

# breakpoint()

# GLOBALS
class m(IntEnum): # For the menu
  # What to print
  Menu               = auto()
  Years              = auto() # The default, yearly changes
  Months             = auto()
  Totals             = auto()

  # What to calculate
  PaymentPrincChange = auto() # Loan,     Interest, Duration => Payment
  DurationPrincChange= auto() # Loan,     Interest, Payment  => Duration
  Interest           = auto() # Loan,     Duration, Payment  => Interest
  Loan               = auto() # Interest, Duration, Payment  => Loan

  Exit               = auto()

class t(IntEnum): # Indices of the tuple, which calculated for each month
  IntrPaid = 0
  PrReduced= auto()
  PrLeft   = auto()

ToPrint = m.Years # The default value
ToDo    = None # The

 # Input data
LOAN = None
INTR = None
YEAR = MONTH = None # Duration
PAYMENT = None

P = [] # List of tuples for each month, no year break (IntrPaid, PrLeft, PrReduced)

def Menu(): #============================================
  menu = [ '',
  f'{m.Menu:2d} - print this menu',
  f'{m.Years:2d} - print totals + years (default)',
  f'{m.Months:2d} - print totals + years + months',
  f'{m.Totals:2d} - print totals',  # Total interest always printed
  "              GIVEN              |             YOU ASK FOR",
  f'{m.PaymentPrincChange:2d} - '
    'loan,    interest, duration | payment,  principal change, interest paid',
  f'{m.DurationPrincChange:2d} - '
    'loan,    interest, payment  | duration, principal change, interest paid',
  f'{m.Interest:2d} - '
    'loan,    duration, payment  | interest',
  f'{m.Loan:2d} - '
    'interest,duration, payment  | loan',
  '',
  f'{m.Exit:2d} - exit'
  ]

  for x in menu:
    sys.stderr.write(x + '\n')
  sys.stderr.write('\n')
# Menu()

def FillPayment(loan, intr, payment): # ???? Add validation if needed =============
  global P
  P = []
  PrLeft = loan

  while PrLeft > 0:
    x = PrLeft
    IntrPaid = PrLeft * (intr / 12)
    PrLeft  += IntrPaid - payment
    PrReduced = x - PrLeft
    P.append((IntrPaid, PrReduced, PrLeft)) # Keep order according t IntEnum above
# FillPayment(...)

def prntMonths(Loan): # Loan used only for calculating column with) ====================
  global P

  # Make a page for print, max. 12 months
  T = [['   Month    '],
       ['  IntrPaid  '],
       ['PrincReduced'],
       [' PrincLeft  ']]

  w = len(f'{Loan:,.2f}')

  for m in range(len(P)): # Gather one year information
    if m % 12 == 0:  # Executed every year
      p = copy.deepcopy(T)   # To make a real copy
      # list(T), T.copy(), [*T], copy.copy(T) do not work

    p[0].append(m+1) # Put this year information into p(age)
    p[1].append(P[m][t.IntrPaid])
    p[2].append(P[m][t.PrReduced])
    p[3].append(max(P[m][t.PrLeft], 0.0))

    if m % 12 != 11 and m + 1 != len(P): # Was it the last m?
       continue # Filling up p
    # Print p ???? Adjust to the numbers, later
    for i in range(len(p)):
      for j in range(len(p[0])): # All have the same length
        if j == 0: # The header
          print(p[i][j], sep='', end='')
        elif i == 0: # The month
          print(f'{int(p[i][j]):>{w-2}}   ',sep='', end='')
        else:
          print(f'{p[i][j]:>{w+1},.2f}',sep='', end='')
      print()
    print()
# prntMonths()

def prntYears(Loan): # Loan used only for calculating column with) =====================
  global P

  # Make a page for print, max. 10 years
  T = [['    Year    '], # The years will be appended to it
       ['  IntrPaid  '],
       ['PrincReduced'],
       [' PrincLeft  ']]

  w = len(f'{Loan:,.2f}')

  r = 1 + int((len(P)-1) / 12)
  for y in range(r): # 0 ... +1 when printing
    if y % 10 == 0:  # Executed every 10 years
      p = copy.deepcopy(T)   # To make a real copy
      # list(T), T.copy(), [*T], copy.copy(T) do not work

    intr = prre = prlf = 0.0
    for m in range(12*y, min(12*(y+1), len(P))): # Gather one year information
      intr += P[m][t.IntrPaid]
      prre += P[m][t.PrReduced]
      prlf  = max(P[m][t.PrLeft], 0.0) # ! NO +

    p[0].append(y+1) # Put this year information into p(age)
    p[1].append(intr)
    p[2].append(prre)
    p[3].append(prlf)

    if y % 10 != 9 and y+1 != r:
       continue # Filling up p
    # Print p ???? Adjust to the numbers, later
    for i in range(len(p)):
      for j in range(len(p[0])): # All have the same length
        if j == 0: # The header
          print(p[i][j], sep='', end='')
        elif i == 0: # The year
          print(f'{int(p[i][j]):>{w-2}}   ',sep='', end='')
        else:
          print(f'{p[i][j]:>{w+1},.2f}',sep='', end='')
      print()
    print()
# prntYears()

def prnt(Loan, intr, Payment): #==============================
  global P, ToPrint
  # First print the totals
  TotIntrPaid = P[0][t.IntrPaid]
  for i in range(1, len(P)):
    TotIntrPaid += P[i][t.IntrPaid]

  LastPayment = Payment + P[-1][t.PrLeft]
  year = int(len(P) / 12) ; month = len(P) % 12
  print(f'\n{Loan=:,.2f} ', f'Interest={intr*100:.3f}% ',
        f'{Payment=:,.2f}', f'(Last one={LastPayment:,.2f})',
        f' {year=}' if year>0 else '',
        f'{month=}' if month>0 else '', f' {TotIntrPaid=:,.2f}\n')

  if ToPrint == m.Totals:
    return

  if ToPrint == m.Years:
    prntYears(Loan) # Loan used only for calculating column with
  else:
    prntMonths(Loan)
# prnt(...)

def GetPayment(loan, intr, dur): # -> payment ===============
  l = 0.0 ; h = loan

  while (payment := (l+h)/2.0) != l and payment != h:
    a = loan
    for _ in range(dur): # Duration in montchs
      a += (a * intr) / 12.0 # One month interest to add
      a -= payment

    if a > 0.0:
      l = payment
    elif a < 0.0:
      h = payment
    else:
      l = h = payment # And the while should break

  return payment
# GetPayment(...)

def GetInterest(loan, payment, dur): # -> intr ===============
  l = 0.0 ; h = 1.0 # 100%

  while (intr := (l+h)/2.0) != l and intr != h:
    a = loan
    for _ in range(dur): # Duration in montchs
      a += (a * intr) / 12.0 # One month interest to add
      a -= payment

    if a > 0.0:
      h = intr
    elif a < 0.0:
      l = intr
    else:
      l = h = intr # And the while should break

  return intr
# GetInterest(...)

def GetLoan(intr, payment, dur): # -> intr ===============
  l = 0.0 ; h = 2 * payment * dur # Some big number

  while (loan := (l+h)/2.0) != l and loan != h:
    a = loan
    for _ in range(dur): # Duration in months
      a += (a * intr) / 12.0 # One month interest to add
      a -= payment

    if a > 0.0:
      h = loan
    elif a < 0.0:
      l = loan
    else:
      l = h = loan # And the while should break

  return loan
# GetLoan(...)

def main(): #==============================================
  global ToPrint, ToDo
  global LOAN, INTR, YEAR, MONTH, PAYMENT

  Menu()
  while ToDo != m.Exit:
    ToDo = int(input(f'Enter  your  choice [1 - {m.Exit}]: '))

    if ToDo == m.Menu:
      Menu()
      continue

    if m.Menu < ToDo <= m.Totals:
      ToPrint = ToDo
      continue
    elif not (m.PaymentPrincChange <= ToDo <= m.Exit):
      sys.stderr.write('Please give a valid choice!\n')
      continue

    if ToDo == m.Exit:
      break

    if ToDo in {m.PaymentPrincChange, m.DurationPrincChange, m.Interest}:
      LOAN = float(input('Enter Loan: ').replace(',',''))

    if ToDo in {m.PaymentPrincChange, m.DurationPrincChange, m.Loan}:
      INTR = float(input('Enter Interest (%): ')) / 100.0

    if ToDo in {m.PaymentPrincChange, m.Interest, m.Loan}: # Duration
      YEAR  = int(input('Enter Years: '))
      MONTH = int(input('Enter Months: '))

    if ToDo in {m.DurationPrincChange, m.Interest, m.Loan}:
      PAYMENT = float(input('Enter Payment: ').replace(',',''))

    # Now do what was asked for ----------------------------

    if ToDo == m.PaymentPrincChange:
      payment = GetPayment(LOAN, INTR, 12*YEAR + MONTH)
      FillPayment(LOAN, INTR, payment)
      print("\nCHECK  PAYMENT !")
      prnt(LOAN, INTR, payment)

    if ToDo == m.DurationPrincChange:
      FillPayment(LOAN, INTR, PAYMENT) # Input data (???? Add validation if needed)
      prnt(LOAN, INTR, PAYMENT) # Duration is len(P)

    if ToDo == m.Interest:
      intr = GetInterest(LOAN, PAYMENT, 12*YEAR + MONTH)
      FillPayment(LOAN, intr, PAYMENT)
      print("\nCHECK  INTEREST !")
      prnt(LOAN, intr, PAYMENT)

    if ToDo == m.Loan:
      loan = GetLoan(INTR, PAYMENT, 12*YEAR + MONTH)
      FillPayment(loan, INTR, PAYMENT)
      print("\nCHECK  LOAN !")
      prnt(loan, INTR, PAYMENT)

# main()

if __name__ == '__main__':
  main()
  sys.stderr.write("\nIs any question this script can't answer, please let me know.\n")
  sys.stderr.write('foltenyi@hotmail.com\n\n')
