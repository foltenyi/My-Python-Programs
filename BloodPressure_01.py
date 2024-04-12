###############################################################################
# Line length <= 99 characters
#
###############################################################################

import sys
import os
import re
import itertools as ite
import inspect as ins           # Location in the program, members of a class
import matplotlib as mpl
import matplotlib.pyplot as plt # Follow the convention
import numpy as np              # Library for working with arrayss
import pandas as pd


def ln() -> str:
    fi = ins.getframeinfo(ins.currentframe().f_back)
    return f'{fi.lineno:3d}'
def fl() -> str:
    fi = ins.getframeinfo(ins.currentframe().f_back)
    return f'{fi.function} {fi.lineno:3d}'  # fi.filename if needed


##################1####### G L O B A L S #####################
B = []
strt = end = [0,0,0] # [yy,mm,dd] integers
Invocation = sys.argv[0].split(os.sep)[-1]
FileName = ""

##################### F U N C T I O N S #####################


def Usage():
    sys.stderr.write(f'\nUsage:\n{Invocation} <file> <start> <end>')
    sys.stderr.write(
"""
<file> contains the lines below, <start or end> and <end or start>
    in the form 'yy/mm/dd'.
This program will print a graph with date and time with the blood pressure,
Systolic and Diastolic. The input contains weight and heart rate, which will
be ignored. The missing data will be interpolated for the graphical display.
The syntax of the line:
    yy/mm/dd day weight <hh:mm sys/dis/hart>*4 [hh:mm <text>]
The missing data is marked with '=' short string.
If a line doesn't correspond to this, it is ignored.
""")

# def Usage(): ends


def SetupBloodpressure(): # Into B
# The missing data represented by None or NaN ????
    global B, FileName, strt, end
    
    with open(FileName) as f: # will close the file
        while (l := f.readline()): # E.g. a good line can be
        # 24/03/30 Sa 170.7 08:20 126/56/51 14:24 153/63/51 ==== ======
        #     23:08 192/70/52 [23:08 Amlodipine] last two is optional
            x = l.strip().split()
            if not (len(x) in (11, 13)):
                continue # Get the next line
            y = x[0].split('/')
            if len(y) != 3:
                continue # Get the next line
            for z in y:
                if not z.isdecimal():
                    break # From the z loop
            # else: # Executes if there was no break
            if not z.isdecimal():
                continue # There was error, get next line
                    
            d = list(map(int, x[0].split('/')))
            if strt <= d <= end:
                if len(x) == 11:
                    x.append('='); x.append('=') # Make lines equal length
                # Delete the 2nd, day, and 3rd, weight columns
                x[1:3] = []
                B.append(x)

    # B is ready, fill out the missing data.
    # First step convert 'hh:mm' -> 60*hh + mm at index 1,3,5,7,9 if possible,
    # if not, put None to that item, candidate for interpolation
    for l in B:
        for i in (1, 3, 5, 7, 9):
            if len(t := l[i].split(':')) != 2:
                continue
            if not (t[0].isdecimal() and t[1].isdecimal()):
                continue
            l[i] = 60 * int(t[0]) + int(t[1]) # It goes back into B

    # Get the missing values by interpolation. I'm sure there are better methods
    # but this, numpy.interp(), was the first I read.
    for i in (1, 3, 5, 7):
        x = []; y = []; xnew = [] # NOT x = y = xnew = []
        for j in range(len(B)):
            xnew += [j]
            if type(v := B[j][i]) == int:
                x += [j]; y += [v]
        ynew = np.interp(xnew, x, y)

        for j in range(len(B)):
            B[j][i] = int(ynew[j]) # Most of the time it is the same value

    # Times are filled now process the blood pressure, e.g.
    # '165/61/50' -> (165,61), 50, heart beat, is ignored; otherwise leave it
    for l in B:
        for i in (2, 4, 6, 8): # Column with, e.g. '165/61/50' or something else
            if len(t := l[i].split('/')) != 3:
                continue
            if not (t[0].isdecimal() and t[1].isdecimal()):
                continue
            l[i] = [int(t[0]), int(t[1])] # It goes back into B

    # And the final step before graphing fill out the missing sys and diastolic data
    for l in B:
        x = []; s = []; d = []; xnew = []
        for i in (2, 4, 6, 8): # Column with, e.g. [165,61] or something else
            xnew += [l[i-1]] # Time in minutes
            if type(l[i]) == list:
                x += [l[i-1]]
                s += [l[i][0]]
                d += [l[i][1]] # Diastolic
        snew = np.interp(xnew, x, s)
        dnew = np.interp(xnew, x, d)

        j = 0
        for i in (2, 4, 6, 8): # Column with, e.g. [165,61] or something else
            l[i] = [int(snew[j]), int(dnew[j])]
            j += 1

    pass # ???? Set break point here
                         

# <bloodpressure file> <start or end date> <end or start date>
def getParameters() -> bool:
    global FileName, strt, end

    if len(sys.argv) != 4:
        sys.stderr.write(ln() + f'Argument error\n')
        Usage()
        return False

    FileName = sys.argv[1] # First parameter, file name
    FileName = FileName.replace('/',os.sep) # All occurances
    if not os.path.exists(FileName):
        sys.stderr.write(ln() + f" {FileName=} doesn't exist\n")
        Usage()
        return False
    
    try:
        file = open(FileName) # As line oriented text file
                              # Use file.readline()
    except OSError as e:
        sys.stderr.write(ln() + f' OSError {fn=}\n')
        # ???? What is e ????
        sys.stderr.write(f'    {e=}\n')
        return False
    except:
        # https://docs.python.org/3/library/sys.html
        sys.stderr.write(ln() + f' ???? Error: {fn=}\n')
        # (type, value, traceback)
        e = sys.exc_info()
        sys.stderr.write(ln() + f'type     : "{e[0]}"\n')
        sys.stderr.write(f'    value    : "{e[1]}"\n')
        sys.stderr.write(f'    traceback: "{e[2]}"\n')
        Usage()
        return False

    else:  # If in the try there was no execption
        file.close() # Don't leave open if something wrong

    # Get the date interval <yy/mm/dd>{2}
    strt = (sys.argv[2]).split('/')
    if len(strt) != 3:
        sys.stderr.write(ln() + f'The 2nd argument is not yy/mm/dd\n')
        Usage()
        return False
    # strt = [int(x) for x in strt] # Which is better
    strt = list(map(int, strt))

    end = (sys.argv[3]).split('/')
    if len(end) != 3:
        sys.stderr.write(ln() + f'The 2nd argument is not yy/mm/dd\n')
        Usage()
        return False
    # end = [int(x) for x in end]
    end = list(map(int, end)) # Which is better
    if end < strt:
        strt, end = end, strt

    return True

# def getParameters() --> bool: END


#######################################################################

def main():

    if not getParameters(): # <bloodpressure file> <start or end date>
        # <end or start date> date format: yy/mm/dd
        return # Complain was already printed

    SetupBloodpressure()  # B is set up probably no missing data

    # FillMissingDataByInterpolation() # Using the global structure


#######################################################################
if __name__ == '__main__':
    breakpoint()  # ???? DEBUG, to set other breakpoints
    main()
    print('\n'+ln()+' Thanks for using this program, any suggestion is welcomed.\n\n')
else:
    sys.stderr.write(f'\n'+ln()+f' Use as a stand alone program\n\n')
