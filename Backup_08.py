# Longest line 90 chars

# Version 07: Added clock timeing:
#     * What was the total time from start to finish.
#     * For how many files sha256 was calculated and what was the total time doing that

# Version 06: Changed ReportProgress(). Call tess frequently, only when directory
#     changed. Report the elapsed time and the directories to be processed.
#     The statistics is from the start.

# Version 05: Added a) subdirectory if it is among the directory parameters, is skipped
#     when going down from a directory is reached.
#     b) The output is sorted.
# =======================================================

import sys   # Command line arguments
import os    # os.getcwd()
import queue
import datetime as dt
import re
import hashlib
from timeit import default_timer as timer # timer() -> float

import inspect
def ln():
  return f'{inspect.currentframe().f_back.f_lineno:3d}'

# ???? breakpoint()

# GLOBALS

Invocation = sys.argv[0].split(os.sep)[-1]
LogFreq = 300 # 5 minutes
LogFrequency = None # The default value is 3 minutes, it can be
  # overwritten by a numeric value, 0 means no logging of the progress

class T: # No instance, for gathering time related info
  cb = 0 # For how many already backed up files hash was calculated
  tb = 0 # For the above files how much time was spent, seconds, float
  cc = 0 # For how many to be checked files hash was calculated
  tc = 0 # For the above files how much time was spent, seconds, float

# If the distance between the end of the file name and the write time
# is bigger than this value, set the distance to it
MaxGoodGap = 38
# The position where the last write time will go
posWT = 0 # +2 is the real position

# There is a class as values of the F dictionary:
# F<key> - key is the common length of the file(s)
class cvF: # class value of F
  # No class variable
  def __init__(self, fn, mtime, size): # Full name
    self.f = {(fn, mtime, size)} # Python set with one tuple
    self.h = {}   # Empty dictionary: key is hash value, value is the full file name

# Create empty dictionaries
F = {} # F.count is the number how many different lengths the files
       # have in the first directory. File length is the key,
       # the value is the cvF class showing above
N = {} # The key is the file names, leaves, lower case, from the first,
       # backup directory, for hint reporting
       # The value is a set of tuples (full file name, mtime, size)
pipedin = [] # Empty list for the piped in files as it were the first directory
             # to be backed up
dirs    = [] # Empty list for the arguments
###########################  FUNCTIONS  START  ###########################

Started = LastReported = dt.datetime.now()
LengthsProcessed = FilesProcessed = 0 # Number of files SHA256 calculated
prev_q = [] # Stop reporting the dirs if it is already reported
def ReportProgress(q): # Directories to be processed
  global LogFrequency, Started, LastReported, LengthsProcessed, FilesProcessed
  global prev_q

  if LogFrequency.seconds == 0: # No report
    return
  d = dt.datetime.now()
  delt = d - LastReported
  if delt >= LogFrequency:
    dur = d - Started
    s = str(dur) ; s = s[:s.index('.')] # ???? How to do it better?
    sys.stderr.write(d.strftime("    %H:%M:%S") + f" ({s})  ")
    mb = round((LengthsProcessed*60)/(dur.seconds*1024*1024))
    sys.stderr.write(f'({mb:,d}MB  ')
    fp = round(FilesProcessed*60/dur.seconds)
    sys.stderr.write(f'{fp:,d}' + ' files) / minute\n')

    _frst = True
    for i, x in enumerate(q.queue[::-1]): # Reverse, last put() is the first
      _s = f'{i+1:2d}' + '. ' + x
      if i == 0:
        _s = _s + '  <-- Next to process'
      # Mark the untouched part
      if _frst and x in prev_q:
        _frst = False
        _s = _s + ' ... from here same as above'
      sys.stderr.write(_s + '\n')

    sys.stderr.write('\n') # Separate the reports
    # Reset for the next reporting
    prev_q = list(q.queue)
    LastReported = d
# ReportProgress

def files(d): # Full directory name ------------------------
  currdir = os.getcwd()
  q = queue.LifoQueue() # Or just Queus for FIFO
  q.put(d) # To avoid recursion, where yield does NOT work

  while not q.empty():
    ReportProgress(q)
    d = q.get() # get() the last put() in directory
    d = d.replace('/', os.sep) # All occurances, happened under Spyder
    os.chdir(d)
    a = os.listdir()
    for fi in a:
      fn = d+os.sep+fi
      if os.path.isdir(fi):
        for x in dirs:
          if fn.lower() == x.lower:
            break
        else:
          q.put(fn) # For the next round
      else:
        st = os.stat(fn)
        yield (fn, st.st_mtime, st.st_size) # Return tuple

  os.chdir(currdir)
# files

def SetupBackedFiles(d): # Full directory name -----------------
  for fn, mtime, size in files(d): # size is the file length as key

    if size in F:
      F[size].f.add((fn, mtime, size)) # Add the tuple to a Python set
    else:
      c = cvF(fn, mtime, size)   # Could be a one line code
      F.update({size: c})

    # Add for hint reporting
    k = fn.split(os.sep)[-1].lower()  # File name is the key to N
    if k in N:   # Was this file name seen before
      N[k].add((fn, mtime, size))
    else:
      N.update({k:{(fn, mtime, size)}})  # The vale is a set of tuples
# SetupBackedFiles


def get_sha256(fn): # Full file name
  start = timer()
  h = hashlib.sha256()
  BLKS = 128*1024
  # h.block_size = BLKS It is not writeable

  # Microsoft Defender does not allow open psneuter, etc.
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
    sys.stderr.write(ln()+f' OSError {fn=}\n')
    # ???? What is e ????
    sys.stderr.write(f'    {e=}\n')
    return (timer()-start, None)
  except:
    # https://docs.python.org/3/library/sys.html
    sys.stderr.write(ln()+f' ???? Error: {fn=}\n')
    # (type, value, traceback)
    e = sys.exc_info()
    sys.stderr.write(f'type     : "{e[0]}"\n')
    sys.stderr.write(f'value    : "{e[1]}"\n')
    sys.stderr.write(f'traceback: "{e[2]}"\n')
    return (timer()-start, None)

  else: # If in the try there was no execption
    file.close()

  return (timer()-start, h.hexdigest())
# get_sha256(fn)


llt = [] # list of lists of tuples. The inner list is already in reportable order,
         # (<file to be backed up> (, Files backed up with the same name, sorted)*)

def CheckThisFileBackedUp(t):
  global LengthsProcessed, FilesProcessed
  global llt

  fn, mtime, k = t # k is size as key, fn full file name
  if k in F: # If not, report this file
    # Generate hash of the file, this file length was seen before
    while True: # Create a scope
      LengthsProcessed += k # Only for
      FilesProcessed   += 1 # progress reporting

      dur, hash = get_sha256(fn)
      T.cc += 1 ; T.tc += dur # Failed or not, update it
      if hash == None:
        return # >>>>>>>>> CHECK ERROR MESSAGES >>>>>>>>>>
      while True: # Until F[k].f is empty
        # If F[k].h (dictionary) contains hash as key, the file is backed up
        if hash in F[k].h:
          return # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> BACKED UP

        # If the F[k].f set is empty, no hope
        if len(F[k].f) == 0:
          break  # >>>>>>>>>>>>>>>>>>>>>>>>>>>> NOT BACKED UP

        # Pick up one element, get its hash, add to F[k].h if it is NOT
        # already there and delete from the set and try again
        _fn, mtime, size = F[k].f.pop()  # Gets and deletes one element, size == k

        LengthsProcessed += size # Only for progress
        FilesProcessed   += 1    # reporting

        _dur, _hash = get_sha256(_fn)
        T.cb += 1 ; T.tb += _dur # Failed or not, update it
        if _hash == None:
          return # >>>>>>>>> CHECK ERROR MESSAGES >>>>>>>>>>

        # Add it to the hash table (dictionary), F[k].h if it is NOT there.
        # If it is there duplicate file, do not report here
        if not _hash in F[k].h:
          # The file name really not needed
          F[k].h.update({_hash: _fn})

        # ... and try again

      break  # From 'Create a scope'

  # If we are here, the file is NOT backed up, report it
  x = [(fn, mtime, k)] # list of tuples, already in the right order, will be added to llt
  # Report ALL already backed files with the same file name as a hint
  _k = fn.split(os.sep)[-1].lower()
  if _k in N:
    # N[_k] is a set of tuples (fn, mtime, size)
    for t in sorted(N[_k], key = lambda t: str.lower(t[0])):
      x.append(t)

  llt.append(x)
# CheckThisFileBackedUp(t)

def CheckTheseFiles(dir): # Full directory name -------------------------
  for t in files(dir):
    fn = t[0]
    # Ignore these files ... see Usage
    f = fn.split(os.sep)[-1].lower()

    for ig in ['desktop\.ini$', "\.un~$", "\.swp$"]:
      if re.search(ig, f, re.I) != None:
        break
    else:
      CheckThisFileBackedUp(t)

# CheckTheseFiles

def Usage(): #-----------------------------------
  h = """
LogFrequency - how offten write statistics and current location of the processing of
    the files to the screen in seconds; default is 300, e.i. 5 minutes, 0 - no log
The first dir is the backup, the files in the second etc.
directories are checked whether they are in the backup directory.
The piped in files are treated as they were in the 2nd directory.
A subdirectory can be given as a separate parameter, if it is reached by traveling
down from an upper directory, it is skipped.
Only the not backuped files are reported. Identical file names, but different files
are reported as hint from the backed up directory.
Zero length files are not skipped.
Files are skipped if:
- dektop.ini
- If its name ends with '.un~'
- If its name ends with '.swp'
Use the DuplUniqFiles script to find duplicate files.
The files to be backed up are sorted.
The filenames are ignored, only the contents are compared.
E.i. if a file is backuped up and renamed, it will be treated as backed up.
If more than one identical files are not backed up, all identical files are reported.

"""
  sys.stderr.write(f'\nUsage:\n{Invocation} [<LogFrequency>] (<dir>)[2,]')
  sys.stderr.write(
      f'\n<fully qualified file names> | {Invocation} [<LogFrequency>] (<dir>)[1,]')
  sys.stderr.write(h)

###########################  FUNCTIONS  E N D  ###########################

def main():
  global LogFreq, LogFrequency, dirs, pipedin
  global llt, MaxGoodGap, posWT

  start = dt.datetime.now()

  # Process the piped in fully qualified file names
  # for f in sys.stdin:
  #   pipedin.append(f.strip())

  # for x in pipedin:
  #  print(ln(), x)

  # Check the parameters, skip the first one, the invocation
  first = True
  for x in sys.argv:
    if first:
      first = False
      continue
    if x.isnumeric():
      LogFreq = int(x)
      continue

    # Spyder puts '/' into the string, change to os.sep
    x = x.replace('/', os.sep) # All occurances
    # If it ends with 'os.sep', delete it
    if x[-1] == os.sep:
      x = x[:-1]       # Delete the last character
    if os.path.isdir(x):
      dirs.append(x)
    else:
      # ERROR
      sys.stderr.write(f"\nWrong Parameter: '{x}'") # Usage starts with new line
      Usage()
      sys.exit(1)

  if len(pipedin) == 0 and len(dirs) < 2 or len(pipedin) > 0 and len(dirs) < 1:
    sys.stderr.write(
      "\nAt least two directories or piped in files and one directory must be given")
    Usage()
    sys.exit(1)

  if not 0 <= LogFreq <= 1800:
    sys.stderr.write("\nLogFrequency must be 0 <= LogFrequency <= 1800")
    Usage()
    sys.exit(1)

  LogFrequency = dt.timedelta(0, LogFreq) # The default value is 3 minutes, it can
      # be overwritten by a numeric value, 0 means no logging of the progress

  print(ln(), start.strftime("START %Y-%m-%d %H:%M:%S"))
  sys.stderr.write(ln() + start.strftime(" START %Y-%m-%d %H:%M:%S\n"))

  Location = os.getcwd()
  print(ln(), os.getcwd())
  sys.stderr.write(ln() + ' ' + os.getcwd() + '\n')
  print(ln(), f'{sys.version=}\n')
  sys.stderr.write(ln() + f' {sys.version=}\n\n')

  SetupBackedFiles(dirs[0]) # Keep ALL directory names for subdirectory checking

  # First take care the piped in files, if any
  for fn in pipedin:
    st = os.stat(fn)
    CheckThisFileBackedUp((fn, st.st_mtime, st.st_size))

  first = True
  for dir in dirs:
    if first:
      first = False
      continue # Skip the backed up directory
    CheckTheseFiles(dir)

  llt = sorted(llt, key = lambda lt: str.lower(lt[0][0]))
  for lt in llt:
    for f, t, s in lt:
      l = len(f) # Full file name
      if posWT - l < 0:          posWT = l # Adjust to end +2 position
      if posWT - l > MaxGoodGap: posWT = l + MaxGoodGap
      # UnicodeEncodeError exeption was generated, try to fix it
      _f = f.encode(errors='ignore')
      sys.stdout.write(_f.decode() + ' '*(2+posWT-l) +
          dt.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S') +
          f'  {s:,d}\n')
    sys.stdout.write('\n') # Empty line to separate

  n = dt.datetime.now()
  print(str(ln()), f"The program run: {str(n-start)[:-4]}\n")
  sys.stderr.write(str(ln()) + f" The program run: {str(n-start)[:-4]}\n\n")

  print(ln(),
    f"Hash was calculated for {T.cb:,d} backed up and {T.cc:,d} to be checked files")
  sys.stderr.write('\n' + ln() +
    f" Hash was calculated for {T.cb:,d} backed up and {T.cc:,d} to be checked files\n")
  db = dt.timedelta(seconds=T.tb) ; dc = dt.timedelta(seconds=T.tc)
  print(ln(),
    f"For the calculation was needed {str(db)[:-4]} and {str(dc)[:-4]} respectively\n")
  sys.stderr.write(ln() +
    f" For the calculation was needed {str(db)[:-4]} and {str(dc)[:-4]} respectively\n\n")

  print(ln(), n.strftime("ENDED %Y-%m-%d %H:%M:%S.%f\n"))
  sys.stderr.write(ln() + n.strftime(" ENDED %Y-%m-%d %H:%M:%S.%f\n\n"))

  # Restore the original directory
  os.chdir(Location)

  print(ln(), os.getcwd())
  sys.stderr.write(ln() + ' ' + os.getcwd() + '\n')

if __name__ == '__main__':
  main()
