# Longest line 90 chars

import sys    # Command line arguments
import os      # os.getcwd()
import argparse # Instead of getopt

# breakpoint()

# GLOBALS

Invocation = sys.argv[0].split(os.sep)[-1]

# From the parameters, these are the default values
numb  = 0 # Number of swimmers, must be given
meth  = 1 # Currently 1 and 2 are supported, 1 is the default
lanes = 8 # How many lanes are in the pool, default is 8
seed  = 0 # If 0, print the whole table. If 0<seed<=numb, print the
          # heat and lane for that swimmer
circ  = 0 # See Usage, default is 0, NO Circle Seeded

ll = [] # list of lists ll[j][i]=swm means:
        # swm swimmwer is in j+1 heat in lane i+1
cw = 0  # Column width, len(str(numb))

###########################  FUNCTIONS  START  ###########################

def fill_ll_M1():
  global ll, numb

  # Fill out the first (will be the last) template list
  L = [x for x in range(lanes)] # Get the right size
  for i in range(len(L)):
    x = len(L)-1-2*i
    L[i] = x if x>0 else 1-x

  while True:
    for i in range(len(L)):
      if L[i] > numb: L[i] = 0
    if max(L) == 0:
      break
    ll.append(list(L)) # list makes a new copy
    if min(L) == 0:
      break
    for i in range(len(L)):
      L[i] += len(L)

  if 0 < circ <= len(ll):
    # Rearrange the first circ lines, see Usage
    _sw = 1
    for i in range(len(L)):
      _i = round(len(L)/2-1-i/2 if i%2 == 0 else len(L)/2-1+(i+1)/2)
      for j in range(circ):
        ll[j][_i] = _sw ; _sw += 1

    for i in range(len(L)):
      for j in range(circ):
        if ll[j][i] > numb: ll[j][i] = 0

  # Flip ll to get the real order
  ll = ll[::-1]

# fill_ll_M1

def fill_ll_M2(): #---------------------------------------------
  global ll, numb

  # Fill out ll
  L = [x for x in range(lanes)] # Get the right size
  for i in range(len(L)):
    x = len(L)-1-2*i
    L[i] = x if x>0 else 1-x

  while True:
    for i in range(len(L)):
      if L[i] > numb: L[i] = 0
    if max(L) == 0:
      break
    ll.append(list(L)) # list makes a new copy
    if min(L) == 0:
      break
    for i in range(len(L)):
      L[i] += len(L)

  # No Circle Seeded for Method 2
# fill_ll_M2

def PrintResult(): #---------------------------------------------
  global ll, seed, cw

  if seed > 0: # Asked only for one swimmer's heat and lane
    for j in range(len(ll)):
      for i in range(len(ll[0])):
        if ll[j][i] == seed:
          print(f'\nFor swimmer {seed} Heat {j+1}  Lane {i+1}\n')
          break
      else:
        continue
      break

  else: # Print the whole table, for all swimmers
    print('\nHEAT'+' '*round((len(ll[0])/2)*(cw+1)-2)+'LANE')
    s = ''
    for i in range(len(ll[0])):
      s += f' {i+1:{cw}d}'
    print('   ' + s)
    for j in range(len(ll)):
      s = f'{j+1:2d}.'
      for i in range(len(ll[0])):
        s += f' {ll[j][i]:{cw}d}' if ll[j][i] > 0 else ' '+' '*cw
      print(s)

# PrintResult()

def Usage(): #--------------------------------------------------------
  h = """
numb  - number of registered swimmers, must be given
meth  - method 1 or 2, default is 1, see explanation below.
        If it is not enough, new method can be added.
lanes - how many are in the pool, default is 8
seed  - if zero or missing print the whole Heat / Lane for all, default is 0,
        otherwise it prints the Heat and Lane for that swimmer
circ  - how many is Circle Seeded, default is zero, if used it is usually 3,
        not used for method 2, for method 1, e.g. in a 6 lane pool
                                LANE
                          1  2  3  4  5  6
    Heat fastest - 2     15  9  3  6 12 18    seeded
    Heat fastest - 1     14  8  2  5 11 17
    Heat fastest         13  7  1  4 10 16

Lane assignment always this way, L lanes in the pool, e.g. 8
Fastest in the heat go to lane L/2
          LANE
 1  2  3  4  5  6  7  8
 7  5  3  1  2  4  6  8   seeded
Method 1, default
  Swimmers groupped, one group has Lanes numbers, slowest, usually
  not whole group swims first.
Method 2
  Swimmers groupped, one group has Lanes numbers, fastest group
  swims first; the last group can be uncomplete

"""
  sys.stderr.write(
    f'\nUsage:\n{Invocation} numb [-meth=1] [-lanes=8] [-seed=0] [-circ=0]')
  sys.stderr.write(h)
# Usage

###########################  FUNCTIONS  E N D  ###########################

def main():
  global numb, meth, lanes, seed, circ, cw # Column width

  Location = os.getcwd()

  # Check the parameters
  parser = argparse.ArgumentParser(usage='', add_help=False) # Parses sys.argv
  # store is the default action
  parser.add_argument( 'numb' , type=int, help=argparse.SUPPRESS)
  parser.add_argument(
    '-meth' , type=int, default=1, required=False, help=argparse.SUPPRESS)
  parser.add_argument(
    '-lanes', type=int, default=8, required=False, help=argparse.SUPPRESS)
  parser.add_argument(
    '-seed' , type=int, default=0, required=False, help=argparse.SUPPRESS)
  parser.add_argument(
    '-circ' , type=int, default=0, required=False, help=argparse.SUPPRESS)

  try:
    args = parser.parse_args() # sys.argv if no argument is given here
  except:
    sys.stderr.write('\nWrong parameter')
    Usage()
    sys.exit(2)

  numb = args.numb
  meth = args.meth
  lanes= args.lanes
  seed = args.seed
  circ = args.circ
  
  if numb <= 0:
    sys.stderr.write(f'\nSPlease give the number of swimmers')
    Usage()
    sys.exit(1)

  if not 0 <= seed <= numb:
    sys.stderr.write(
      f'\nSeed must be between (including) 0 and number of swimmers, {numb}')
    Usage()
    sys.exit(1)
    
  if meth == 1:
    fill_ll_M1()
  elif meth == 2:
    fill_ll_M2()
  else: # ERROR
    sys.stderr.write(f'\nUnsupported method {meth}, see:')
    Usage()
    sys.exit(1)

  cw = len(str(numb)) # Set column width + 1 space

  PrintResult()

  # Restore the original directory
  os.chdir(Location)

if __name__ == '__main__':
  main()
