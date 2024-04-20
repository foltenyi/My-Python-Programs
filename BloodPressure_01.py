###############################################################################
# Line length <= 99 characters
#
###############################################################################

import sys
import os
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


def SetupBloodpressureAndGraph(): # Into B
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

    B.reverse()

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
        if len(x) < 1:
            sys.stderr.write(f'\n'+ln()+f' Column {i} does not have time!\n')
            return

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

    # All data in B are filled. Just a reminder, there are two types of rows:
    #      0        1       2      3      4        5      6        7      8       9     10
    # ['24/03/31', 515, [139,57], 822, [137,60], 1128, [154,54], 1377, [184,80], '=' , '='],
    # ['24/03/30', 500, [126,56], 864, [153,63], 1132, [172,66], 1388, [192,70], 1388,'Amlodipine']
    #
    # Prepare X for daily display and YS for systolic and YD for the diastolic measurements
    X = []; YS = []; YD = []
    x2r = 0  # How much to step to right on x from one to the other
    minD = 100; maxS = 0  # For grid setting
    for x in B:
        X.append([x[1]-x[1]+x2r, x[3]-x[1]+x2r, x[5]-x[1]+x2r, x[7]-x[1]+x2r])
        if type(x[9]) == int:  # There is a time and comment on this day
            x[9] = x[9]-x[1]+x2r  # Modify the time, so it can be found in the transformed time
        x2r = x[7]-x[1]+x2r
        x2r += 16  # Leave a little gap between days
        YS.append([x[2][0], x[4][0], x[6][0], x[8][0]])
        if maxS < max(YS[-1]):
            maxS = max(YS[-1])
        YD.append([x[2][1], x[4][1], x[6][1], x[8][1]])
        if minD > min(YD[-1]):
            minD = min(YD[-1])

    # Ready for display the graph
    fig, ax = plt.subplots(figsize=(11.75, 8.25))  # In inches, W x H

    ax.set_title('Vilmos Foltenyi blood pressure chart', fontsize=18)
    _p1 = X[0][0]  # Generate 2 ticks, to the first and the last times
    _p2 = X[-1][-1]+1
    _p3 = X[-1][-1]
    ax.set_xticks(np.arange(_p1, _p2, _p3), [B[0][0], B[-1][0]], fontsize=16)
    ax.set_ylabel('Blood Pressure', fontsize=14)
    for x, ys, yd in zip(X, YS, YD):
        ax.plot(x, ys, color='#FF0000', label='Systolic'  if x[0]==X[0][0] else '')
        ax.plot(x, yd, color='#0000FF', label='Diastolic' if x[0]==X[0][0] else '')

    leg = ax.legend(fontsize=16, frameon=False)

    for i in range(len(B)):
        if type(x := B[i][9]) == int:
            com = B[i][10]  # Comment goes into the graph
            if X[i].count(x) < 1:
                sys.stderr.write(f'\n'+ln()+f" Timestamp for {com} doesn't occur before!\n")
                return

            y = YS[i][X[i].index(x)]
            ax.text(x, y, com, fontsize=14, clip_on=True, horizontalalignment='center')
            ax.plot(x, y, 'o', color='#00F000', markersize=15)

    ax.grid(axis='y', color='#800080', linestyle='--', linewidth=0.5)
    step = 10
    yticks = np.arange(step*(minD//step), step*(maxS//step+1), step)
    ax.set_yticks(yticks)
    # breakpoint()

    plt.show()

# END def SetupBloodpressureAndGraph(): # Into B


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
        sys.stderr.write(ln() + f'    {e=}\n')
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

    SetupBloodpressureAndGraph()  # B is set up probably no missing data

    # FillMissingDataByInterpolation() # Using the global structure


#######################################################################
if __name__ == '__main__':
    # breakpoint()  # ???? DEBUG, to set other breakpoints
    main()
    print('\n'+ln()+' Thanks for using this program, any suggestion is welcomed.\n\n')
else:
    sys.stderr.write(f'\n'+ln()+f' Use as a stand alone program\n\n')
