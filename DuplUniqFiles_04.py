# Longest line 90 chars

import os      # os.getcwd()
import sys     # Command line arguments
import datetime as dt
import hashlib

# breakpoint() # New style, doesn't work with pipe

# GLOBALS

Invocation = sys.argv[0].split(os.sep)[-1]
LogFreq = 120
LogFrequency = None # The default value is 2 minutes, it can be
    # overwritten by a numeric value, 0 means no logging of the progress

# If the distance between the end of the file name and the write time
# is bigger than this value, set the distance to it
MaxGoodGap = 40
# The position where the last write time will go
posWT = 0 # +2 is the real position

# F<key> - key is the common length of the file in string format
class cvF: # class value of F
  # No class variable
  def __init__(self,fn): # Full name
    self.f = fn # Just remember the first file
    self.h = {} # Empty dictionary: key is hash value, value is a list from f with the
                # same SHA256 value

# Create empty dictionary
F = {} # F.count is the number how many different lengths the files
       # have in the first directory. File length is the key,
       # the value is the cvF class showing above
files = [] # Empty list for the piped in files as it were the first directory
dirs  = [] # Empty list for the arguments
unique = False # By default report the duplicate files

###########################  FUNCTIONS  START  ###########################

LastReported = dt.datetime.now()
def ReportProgress(file): # Full name ------------------------------
  global LastReported, LogFrequency
  if LogFrequency.seconds == 0: # No report
    return
  d = dt.datetime.now()
  delt = d - LastReported
  if delt >= LogFrequency:
    sys.stderr.write(d.strftime("**** %H:%M:%S.%f ")+file+'\n')
    # Reset for the next reporting
    LastReported = d
# ReportProgress


# Double loop, the outher loop is the F dictionary, the value of it is also a dictionary
# the key is the common hash of the files store in the value of this second dictionary
# as a list. If the list is longer than 1 the files are duplicates
def ReportDuplicateFiles(): #-------------------------------------
  global MaxGoodGap, posWT
  ll = [] # List of sorted lists, will be sorted, too
  for k in F:
    for h in F[k].h:
      if len(F[k].h[h]) > 1: # Duplicate files are here, report them
        ll.append(sorted(F[k].h[h], key=str.lower))

  ll = sorted(ll, key=lambda l: str.lower(l[0]))

  for l in ll:
    for f in l:
  # The write below aborted with the next message (Traceback was, too)
  # UnicodeEncodeError: 'charmap' codec can't encode characters in position 27-32:
  #                                                  character maps to <undefined>
  # Is this fix correct ????
      ln = len(f)
      if posWT - ln < 0: posWT = ln # Set it just after the name
      if posWT - ln > MaxGoodGap: posWT = ln + MaxGoodGap
      # a = f.split(os.sep)
      # b = os.sep.join(a[:-1]) # Only the directory part
      # sys.stderr.write(b+'\n')
      x = bytes(f, 'utf-8', 'ignore')
      y = x.decode(errors='ignore')
      try:
        st = os.stat(f)
        sys.stdout.write(y + ' '*(2+posWT-ln) +
          dt.datetime.fromtimestamp(st.st_mtime).strftime('%Y-%m-%d %H:%M:%S') +
          '  ' + f'{st.st_size:,d}\n')
      except FileNotFoundError as e:
        sys.stdout.write(y+' '*(2+posWT-ln)+f'???? os.stat({f=} FAILED\n')
        sys.stderr.write(f'FileNotFoundError {f=}\n')
        # ???? What is e ????
        sys.stderr.write(f'{e=}\n')
      except:
        # https://docs.python.org/3/library/sys.html
        sys.stdout.write(y+' '*(2+posWT-ln)+f'???? os.stat({f=} FAILED\n')
        sys.stderr.write(f'???? Error: {f=}\n')
        # (type, value, traceback)
        e = sys.exc_info()
        sys.stderr.write(f'type     : "{e[0]}"\n')
        sys.stderr.write(f'value    : "{e[1]}"\n')
        sys.stderr.write(f'traceback: "{e[2]}"\n')

    sys.stdout.write('\n') # Empty line to separate


# Similar to the duplicate files, plus those entries in F, for which hash never
# was calculated. No empty line separator
def ReportUniqueFiles(): #-----------------------------------
  for k in F:
    if F[k].f: # A unique file name was stored here, F[k].h must be empty, None
      sys.stdout.write(F[k].f+'\n')
      continue

    for h in F[k].h:
      if len(F[k].h[h]) == 1: # Unique file is here
        sys.stdout.write(F[k].h[h][0]+'\n')


# Try different BLKS
def get_sha256(fn): # Full file name -------------------------
  h = hashlib.sha256()
  BLKS = 128*1024
  # h.block_size = BLKS It is not writeable

# Doesn't work if generates exeption
#  with open(fn, 'rb') as file:
#    while True:
#      # Reading is buffered, so we can read smaller chunks.
#      chunk = file.read(BLKS)
#      if not chunk:
#        break
#      h.update(chunk)

  try:
    file = open(fn, 'rb')
    while True:
      # Reading is buffered, so we can read smaller chunks.
      chunk = file.read(BLKS)
      if not chunk:
        break
      h.update(chunk)
  except OSError as e:
    sys.stderr.write(f'OSError {fn=}\n')
    # ???? What is e ????
    sys.stderr.write(f'{e=}\n')
    return None
  except:
    # https://docs.python.org/3/library/sys.html
    sys.stderr.write(f'???? Error: {fn=}\n')
    # (type, value, traceback)
    e = sys.exc_info()
    sys.stderr.write(f'type     : "{e[0]}"\n')
    sys.stderr.write(f'value    : "{e[1]}"\n')
    sys.stderr.write(f'traceback: "{e[2]}"\n')

  else: # If in the try there was no execption
    file.close()

  return h.hexdigest()
# get_sha256


def SetThisFile(fn): # Full file name --------------------------
  ReportProgress(fn)
  st = os.stat(fn)
  k = st.st_size # File length is the key

  if k in F: # If not, just remember it
    if F[k].f: # There was a file with the same length before
      hash = get_sha256(F[k].f)
      if hash == None:
        return # Check error messages
      F[k].h.update({hash:[F[k].f]}) # The first memberof the F[k].h directory
      F[k].f = None # Has been processed

    # Generate hash of the file, this file length was seen before
    hash = get_sha256(fn)
    if hash == None:
      return # Check error messages
    # Was this hash seen before, e.i. this file was seen before?
    if hash in F[k].h: # It is a dictionary, key is hash, value is a list
                       # of the identical files
      F[k].h[hash].append(fn)
    else:
      F[k].h.update({hash:[fn]}) # First with this hash
  else: # Was NOT in F
    F.update({k:cvF(fn)}) # New length, if appears again calculate SHA256
# SetThisFile


def SetTheseFiles(dir): # In this directory, full name ------------
  currdir = os.getcwd()
  os.chdir(dir)

  a = os.listdir() # The current one
  for f in a:
    fn = dir+os.sep+f   # Full name
    if os.path.isdir(f):
      SetTheseFiles(fn) # Recursive call
    else:
      SetThisFile(fn)

  os.chdir(currdir) # Restore the original directory
# SetTheseFiles

def Usage(): #-----------------------------------

  h = """
LogFrequency - how offten write the current location of the processing of the
    files to the stderr in seconds; default is 120, e.i. 2 minutes, max 30 minutes
    0 - no log
[-unique] - by default the duplicate files are reported, if present, the unique files

"""
  sys.stderr.write(
    f'\nUsage:\n{Invocation} [<LogFrequency>] (<dir>)[1,] [-unique]\n')
  sys.stderr.write(
    f'<fully qualified file names> | {Invocation} [<LogFrequency>] (<dir>)* [-unique]')
  sys.stderr.write(h)

###########################  FUNCTIONS  E N D  ###########################

def main():
  global LogFreq, LogFrequency, unique
  # Process the piped in fully qualified file names
  # How to debug it ???? for f in sys.stdin:
  #                        files.append(f.strip())

  # ????
  # print(currentframe().f_lineno, end=' ')
  # for x in files: print(x)

  # Check the parameters, skip the first one
  i = 0
  for x in sys.argv:
    i += 1
    if i == 1:
      continue    # Invocation name
    if x.isnumeric():
      LogFreq = int(x)
      continue;
    if x.lower() == '-unique':
      unique = True
      continue

    if x[-1] == os.sep: # If the last character 'os.sep', delete it
      x = x[:-1]
    if os.path.isdir(x):
      dirs.append(x)
    else:
      # ERROR
      sys.stderr.write(f"\nWrong Parameter: '{x}'")
      Usage()
      sys.exit(1)

  if not 0 <= LogFreq <= 1800:
    sys.stderr.write("\nLogFrequency must be 0 <= LogFrequency <= 1800")
    Usage()
    sys.exit(1)

  LogFrequency = dt.timedelta(0,LogFreq) # The default value is 2 minutes, it can
    # be overwritten by a numeric value, 0 means no logging of the progress

  if len(files) == 0 and len(dirs) < 1:
    sys.stderr.write("\nAt least one directory or piped in files must be given")
    Usage()
    sys.exit(1)

  Location = os.getcwd() # Everything is fine, START processing =================

  print(dt.datetime.now().strftime("\nSTART %Y-%m-%d %H:%M:%S.%f\n")) # Goes to stdout
  sys.stderr.write(dt.datetime.now().strftime("\nSTART %Y-%m-%d %H:%M:%S.%f\n"))
  sys.stderr.write(f'{sys.version=}\n')

  # $F will be populated
  # First take care the piped in files, if any
  for f in files:
    SetThisFile(f)

  for dir in dirs:
    SetTheseFiles(dir)

  if unique:
    ReportUniqueFiles()
    sys.stdout.write('\n') # Empty line
  else:
    ReportDuplicateFiles()

  print(dt.datetime.now().strftime("ENDED %Y-%m-%d %H:%M:%S.%f\n"))
  sys.stderr.write(dt.datetime.now().strftime("ENDED %Y-%m-%d %H:%M:%S.%f\n"))

  # Restore the original directory
  os.chdir(Location)

if __name__ == '__main__':
  main()
