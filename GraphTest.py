###############################################################################
# Line length <= 99 characters
#
###############################################################################

# import sys
# import os
# import re
# import itertools as ite
# import inspect as ins           # Location in the program, members of a class
import matplotlib as mpl
import matplotlib.pyplot as plt # Follow the convention
import numpy as np              # Library for working with arrayss
import pandas as pd


def main():

    B = [
        ['24/04/01', 514, [129, 55], 822, [149, 62], 1143, [170, 70], 1353, [170, 73], '=', '='],
        ['24/03/31', 515, [139, 57], 822, [137, 60], 1128, [154, 54], 1377, [184, 80], '=', '='],
        ['24/03/30', 500, [126, 56], 864, [153, 63], 1132, [172, 66], 1388, [192, 70], 1388, 'Amlodipine'],
        ['24/03/29', 486, [121, 50], 836, [132, 52], 1137, [132, 52], 1381, [132, 52], '=', '='],
        ['24/03/28', 514, [120, 54], 868, [156, 58], 1142, [156, 58], 1374, [156, 58], '=', '='],
        ['24/03/27', 514, [128, 54], 832, [134, 54], 1147, [191, 81], 1367, [179, 76], 1147, 'Amlodipine']
        ]
    # X All time data
    X = []; Y1 = []; Y2 = []
    x2r = 0
    for x in B:
        X.append([x[1]-x[1]+x2r, x[3]-x[1]+x2r, x[5]-x[1]+x2r, x[7]-x[1]+x2r])
        if type(x[9]) == int:
            x[9] = x[9]-x[1]+x2r
        x2r = x[7]-x[1]+x2r
        x2r += 16
        Y1.append([x[2][0], x[4][0], x[6][0], x[8][0]])
        Y2.append([x[2][1], x[4][1], x[6][1], x[8][1]])

    fig, ax = plt.subplots(figsize=(11.75, 8.25))  # In inches, W x H

    ax.set_title('Vilmos Foltenyi blood pressure chart', fontsize=18)
    _p1 = X[0][0]
    _p2 = X[-1][-1]+1
    _p3 = X[-1][-1]
    ax.set_xticks(np.arange(_p1, _p2, _p3), [B[-1][0], B[0][0]], fontsize=16)  # 
    ax.set_ylabel('Blood Pressure', fontsize=14)
    for x,y1,y2 in zip(X, Y1, Y2):
        ax.plot(x, y1, color='#FF0000', label='Systolic'  if x[0]==X[0][0] else '')
        ax.plot(x, y2, color='#0000FF', label='Diastolic' if x[0]==X[0][0] else '')
        
    leg = ax.legend(fontsize=16, frameon=False)
    breakpoint()
    for i in range(len(B)):
        if type(x := B[i][9]) == int:
            com = B[i][10]  # Comment goes into the graph
            y = Y1[i][X[i].index(x)]
            ax.text(x, y, com, fontsize=14, clip_on=True, horizontalalignment='center')
            ax.plot(x, y, 'o', color='#00F000', markersize=15)
            
    ax.grid(axis='y', color='#800080', linestyle='--', linewidth=0.67)
    breakpoint()
    
    plt.show()

    breakpoint()

#######################################################################
if __name__ == '__main__':
    # breakpoint()  # ???? DEBUG, to set other breakpoints
    main()
else:
    sys.stderr.write(f'\n'+ln()+f' Use as a stand alone program\n\n')
