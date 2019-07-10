import numpy as np
import itertools
import sys

class factor:
    def __init__(self,variables,num, table):
        self.variables = variables
        self.num =num
        self.table = table
    
    def print(self):
        string = ""
        for i in self.variables:
            string+=i
            string+="  "
        string+="Prob"
        print(string)
        for i in self.table:
            string = ''
            for j in range(len(i)):
                if j !=len(i)-1:
                    string = string+str(int(i[j]))+'   '
                else:
                    string = string+str(i[j])
            print(string)

def restrict(factor, variable, value):
    print("Restricted to "+str(variable)+" = "+str(value))
    print("\n")
    factor.print()
    print("\n")
    print("Result:")
    shape = factor.table.shape
    col = None
    for i in range(factor.num):
        if factor.variables[i] == variable:
            col = i
            break
    factor.num-=1
    del factor.variables[col]
    delete = []
    for i in range(shape[0]):
        if factor.table[i][col] !=value:
            delete.append(i)
    while delete != []:
        factor.table = np.delete(factor.table,delete.pop(),0)
    factor.table = np.delete(factor.table,col,1)
    factor.print()
    print("--------------")
    return factor

def multiply(factor1,factor2):
    print("Multiplying:")
    factor1.print()
    factor2.print()
    print("\n")
    print("Result:")
    intersact = list(set(factor1.variables) & set(factor2.variables))
    intersact.sort()
    union = list(set(factor1.variables) | set(factor2.variables))
    union.sort()
    length = len(union)
    table = list(itertools.product([1, 0], repeat=length))
    table = np.array(table)
    table = np.c_[table,np.zeros(2**length)]
    f1Pos = []
    f2Pos = []
    for i in range(length):
        if union[i] in factor1.variables:
            f1Pos.append(i)
        if union[i] in factor2.variables:
            f2Pos.append(i)
    for i in range(2**length):
        f1value = None
        f2value = None
        length1 = len(factor1.table)
        for j in range(length1):
            found = True
            for k in range(factor1.num):
                if factor1.table[j][k] != table[i][f1Pos[k]]:
                    found = False
                    break
            if found:
                f1value = factor1.table[j][-1]
                break
        
        length2 = len(factor2.table)
        for j in range(length2):
            found = True
            for k in range(factor2.num):
                if factor2.table[j][k] != table[i][f2Pos[k]]:
                    found = False
                    break
            if found:
                f2value = factor2.table[j][-1]
                break
        table[i][-1] = f1value * f2value
    ans = factor(union,len(union),table)
    ans.print()
    print("--------------")
    return ans



def sumout(factor,variable):
    print("Sumout "+variable+" from:")
    factor.print()
    print("\n")
    print("Result:")
    shape = factor.table.shape
    col = None
    for i in range(factor.num):
        if factor.variables[i] == variable:
            col = i
            break
    factor.num-=1
    del factor.variables[col]
    factor.table = factor.table[factor.table[:,col].argsort(kind='mergesort')]
    for i in range(int(shape[0]/2)):
        factor.table[i][-1]+=factor.table[i+int(shape[0]/2)][-1]
    factor.table = np.delete(factor.table,col,1)
    for i in range(int(shape[0]/2)):
        factor.table = np.delete(factor.table,int(shape[0]/2),0)
    factor.print()
    print("--------------")
    return factor

def normalize(factor):
    print("Normalize:")
    factor.print()
    print("\n")
    print("Result:")
    shape = factor.table.shape
    total = 0
    for i in range(shape[0]):
        total+=factor.table[i][-1]
    for i in range(shape[0]):
        factor.table[i][-1] = factor.table[i][-1]/total
    factor.print()
    print("--------------")
    return factor

def inference(factor_list, query_variables, ordered_hidden_var_list, evidence_vars):
    #restrict factors
    for key, value in evidence_vars.items():
        i = 0
        while i < len(factor_list):
            if key in factor_list[i].variables:
                factor_list.append(restrict(factor_list[i], key, value))
                del factor_list[i]
                i-=1
            i+=1
    #eliminate hidden
    for i in ordered_hidden_var_list:
        factors = []
        j = 0
        while j < len(factor_list):
            if i in factor_list[j].variables:
                factors.append(factor_list[j])
                del factor_list[j]
                j-=1
            j+=1
        while len(factors) >= 2:
            factors.append(multiply(factors[0],factors[1]))
            factors.pop(0)
            factors.pop(0)
        if len(factors) != 0:
            factor_list.append(sumout(factors[0],i))
        
    #multiply all remaining
    while len(factor_list) >= 2:
        factor_list.append(multiply(factor_list[0],factor_list[1]))
        factor_list.pop(0)
        factor_list.pop(0)
    for i in ordered_hidden_var_list:
        if i in factor_list[0].variables:
            factor_list.append(sumout(factor_list[0],i))
            factor_list.pop(0)
    #normalize
    return normalize(factor_list[0])
        


        



AB = factor(["AB","AS"],2,np.array([(1,1,0.6), (1,0,0.1), (0,1,0.4), (0,0,0.9)]))
AH = factor(["AH","AS","M","NH"],4, np.array([(1,1,1,1,0.99),(1,1,1,0,0.9),(1,1,0,1,0.75),(1,1,0,0,0.5),\
    (1,0,1,1,0.65),(1,0,1,0,0.4),(1,0,0,1,0.2),(1,0,0,0,0),\
        (0,1,1,1,0.01),(0,1,1,0,0.1),(0,1,0,1,0.25),(0,1,0,0,0.5),\
            (0,0,1,1,0.35),(0,0,1,0,0.6),(0,0,0,1,0.8),(0,0,0,0,1)]))
AS = factor(["AS"],1,np.array([(1,0.05),(0,0.95)]))
M = factor(["M"],1,np.array([(1,1/28),(0,27/28)]))
NA = factor(["NA"],1,np.array([(1,0.3),(0,0.7)]))
NH = factor(["M","NA","NH"],3,np.array([(1,1,1,0.8),(1,1,0,0.2),(1,0,1,0.4),(1,0,0,0.6),\
    (0,1,1,0.5),(0,1,0,0.5),(0,0,1,0),(0,0,0,1)]))
# ans = restrict(AB,'AS',1)
# print(ans.table)
# ans = sumout(AH,"AH")
# print(ans.table)
# ans = normalize(AB)
# print(ans.table)
# multiply(AH,NH)
# inference([AB,M],0,0,{'AB':1})
# AB.print()

if len(sys.argv) == 2:
    if(sys.argv[1]) == '0':
        print("yes")
        inference([AB,AH,AS,M,NA,NH], ['AH'], ['AB','AS','M','NA','NH'], {})
    elif(sys.argv[1] == '1'):
        inference([AB,AH,AS,M,NA,NH], ['AH','AS','M'], ['AB','NA','NH'], {'AH':1,'M':1})
    elif(sys.argv[1] == '2'):
        inference([AB,AH,AS,M,NA,NH], ['AB','AH','AS','M'], ['NA','NH'], {'AB':1,'AH':1,'M':1})
    else:
        inference([AB,AH,AS,M,NA,NH], ['AB','AH','AS','M','NA'], ['NH'], {'AB':1,'AH':1,'M':1,'NA':1})

# E = factor(['E'],1,np.array([(1,0.0003),(0,0.9997)]))
# B = factor(['B'],1,np.array([(1,0.0001),(0,0.9999)]))
# A = factor(['A','B','E'],3,np.array([(1,1,1,0.96),(1,1,0,0.95),(1,0,1,0.2),(1,0,0,0.01),(0,1,1,0.04),(0,1,0,0.05),(0,0,1,0.8),(0,0,0,0.99)]))
# W = factor(['A','W'],2,np.array([(1,1,0.8),(1,0,0.2),(0,1,0.4),(0,0,0.6)]))
# G = factor(['A','G'],2,np.array([(1,1,0.4),(1,0,0.6),(0,1,0.04),(0,0,0.96)]))

# inference([E,B,A,W,G], ['W'], ['A','B','E','G'], {})
# inference([E,B,A,W,G], ['G','W'], ['A','B','E'], {'W':0})
# inference([E,B,A,W,G], ['G','W'], ['A','B','E'], {'W':0})
# inference([E,B,A,W,G], ['A','G','W'], ['B','E'], {'G':0,'W':0})
# inference([E,B,A,W,G], ['A','G'], ['B','E','W'], {'G':1})
# inference([E,B,A,W,G], ['B'], ['A','E','G','W'], {})
# inference([E,B,A,W,G], ['A','B','E'], ['G','W'], {'A':0,'B':0})
    
