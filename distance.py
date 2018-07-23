# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 12:48:42 2018

@author: cx10
"""
from math import sqrt

def Cosine(dataseq,seq):
    """
    Calculate the Cosine distance between two sequences
    """   
    
    a=[0]*14
    b=[0]*14
    for elt in dataseq:
        a[elt]+=1
    for elt in seq:
        b[elt]+=1
    dot=sum(i[0] * i[1] for i in zip(a, b))
    normA=sqrt(sum(i**2 for i in a))
    normB=sqrt(sum(i**2 for i in b))
    return 1-(dot/(normA*normB))
    
def Jaccard(answer,ind):
    a=set(answer)
    b=set(ind)
    inter=len(a&b)
    jaccard=inter/(len(a)+len(b)-inter)
    return 1-jaccard


# @author Michael Homer
# http://mwh.geek.nz/2009/04/26/python-damerau-levenshtein-distance/
# https://genepidgin.readthedocs.io/en/latest/compare.html
def damerauLevenshteinHomerDistance(seq1, seq2):
    """
    Calculate the Damerau-Levenshtein distance between sequences.

    This distance is the number of additions, deletions, substitutions,
    and transpositions needed to transform the first sequence into the
    second. Although generally used with strings, any sequences of
    comparable objects will work.

    Transpositions are exchanges of *consecutive* characters; all other
    operations are self-explanatory.

    This implementation is O(N*M) time and O(M) space, for N and M the
    lengths of the two sequences.
    """

    oneago = None
    thisrow = list(range(1, len(seq2) + 1)) + [0]
    for x in range(len(seq1)):
        # Python lists wrap around for negative indices, so put the
        # leftmost column at the *end* of the list. This matches with
        # the zero-indexed strings and saves extra calculation.
        twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
        for y in range(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
            # This block deals with transpositions
            if (x > 0 and y > 0 and seq1[x] == seq2[y-1]
              and seq1[x-1] == seq2[y] and seq1[x] != seq2[y]):
                thisrow[y] = min(thisrow[y], twoago[y-2] + 1)
    return thisrow[len(seq2) - 1]