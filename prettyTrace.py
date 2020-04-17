#!/usr/bin/python3
from sys import argv
from menu import *
import sys
import re

import re


functionRegex = r'^([0-9,a-f]{8}) <(.*)>:\n$'
lineRegex = r'^([0-9,a-f]{8}):\t+([0-9,a-f]*)\s*\t*(.*)\n$'

# Time -Cycles - PC - Instr -Mnemo
traceRegex = r'^\s*(\d+)\s*(\d+)\s*([0-9,a-f]+)\s*([0-9,a-f]+)\s*(.+)\n$'


def makeDisassembly(lines):
    res = {}

    currentFunction = ''
    lastAddress = 0
    for l in lines:
        g = re.match(functionRegex, l)
        if g:
            address = int(g.group(1), 16)
            functionName = g.group(2)
            if currentFunction != '':
                res[currentFunction]['last'] = lastAddress
            currentFunction = functionName
            res[currentFunction] = {}
            res[currentFunction]['first'] = address
            res[currentFunction]['instr'] = []
            lastAddress = address

        g = re.match(lineRegex, l)
        if g:
            instr = {}
            lastAddress = int(g.group(1), 16)
            instr['address'] = lastAddress
            instr['opCode']  = g.group(2)
            instr['asm']     = g.group(3)
            res[currentFunction]['instr'].append(instr)

    res[currentFunction]['last'] = lastAddress
    return res

BOLD =u"\u001b[1m"
NORMAL =u"\u001b[0m"
YELLOW =u"\u001b[33m"
GREEN =u"\u001b[32m"
RED =u"\u001b[31m"

def makeTable(dis):
    res = []
    for f in dis.keys():
        res.append((dis[f]['first'], dis[f]['last'],f))
    res.sort(key=lambda x : x[0])
    return res


def addrIn(address, table):
    for i in table:
        if i[0] <= address <= i[1]:
            return i[2]
def printTrace(tr, dis, ta):
    '''
    tr trace lines
    dis : disassembly object
    ta: table of functions
    '''
    currentFunction = ""
    for l in tr:
        g = re.match(traceRegex,l)
        if g:
            time = g.group(1)
            cycles = g.group(2)
            pc     = g.group(3)
            instr  = g.group(4)
            mnemo = g.group(5)
            f = addrIn(int(pc,16), table)

            if f != currentFunction:
                currentFunction = f
                print(BOLD + YELLOW + "Function {}".format(currentFunction) + NORMAL)
            print("\t({:8})   {}".format(pc, mnemo))
            if("jalr" in mnemo):
                print(BOLD + GREEN + "Return Call" + NORMAL)

def generateMenu(tr, dis, ta,callstack=[""], k = 0):
    '''
    tr trace lines
    dis : disassembly object
    ta: table of functions
    '''
    currentFunction = callstack[-1]
    ret = False
    tab = 0
    children = []
    codeLines = []
    k0 =k
    t0 = 0
    while k < len(tr):
        l = tr[k]
        g = re.match(traceRegex,l)
        if g:
            time = g.group(1)
            cycles = g.group(2)
            pc     = g.group(3)
            instr  = g.group(4)
            mnemo = g.group(5)
            f = addrIn(int(pc,16), table)
            if(k == k0):
                t0 = cycles

            if f != currentFunction:
                if f in callstack:
                    # Return from function call
                    if len(codeLines):
                        children.append(MenuItem("...({})".format(len(codeLines)), codeLines))
                    return k, MenuItem("{} (C: {}) (A: 0x{:x})".format(currentFunction,t0,dis[currentFunction]["first"]), children)
                else:
                    callstack.append(f)
                    if len(codeLines):
                        children.append(MenuItem("...({})".format(len(codeLines)), codeLines))
                    codeLines = []
                    # Function call
                    k,c = generateMenu(tr, dis, ta, callstack, k)

                    children.append(c)
                    callstack.pop(-1)
            else:
                c = []
                c.append(MenuItem("Time   : {}".format(time)))
                c.append(MenuItem("Cycles : {}".format(cycles)))
                c.append(MenuItem("PC     : 0x{}".format(pc)))
                c.append(MenuItem("Instr  : 0x{}".format(instr)))
                mnemo = MenuItem("{}".format(mnemo), c)
                codeLines.append(mnemo)

                k += 1
        else:
            k += 1
    if callstack == [""]:
        return MenuItem("", children)
    else:
        return k, MenuItem("{} (C: {}) (A: 0x{:x})".format(currentFunction,t0,dis[currentFunction]["first"]), children)

def printMenu(tr, dis, ta):
    m = Menu(generateMenu(tr,dis,ta).sub)
    return m

def printTree(tr, dis, ta):
    '''
    tr trace lines
    dis : disassembly object
    ta: table of functions
    '''
    currentFunction = ""
    ret = False
    tab = 0
    callstack = []
    for l in tr:
        g = re.match(traceRegex,l)
        if g:
            time = g.group(1)
            cycles = g.group(2)
            pc     = g.group(3)
            instr  = g.group(4)
            mnemo = g.group(5)
            f = addrIn(int(pc,16), table)

            if f != currentFunction:
                if f in callstack:
                    l = ""
                    while l != f:
                        tab -= 2
                        l = callstack.pop(-1)
                    currentFunction = f
                    callstack.append(f)
                    tab += 2
                else:
                    tab += 2
                    callstack.append(f)
                    currentFunction = f
                    print(" " * tab +  currentFunction + " ({})".format(cycles))



if len(argv) != 3:
    print("Usage:")
    print("{} trace disassembly".format(argv[0]))
    sys.exit(0)

with open(argv[1],'r') as f:
    traceLines = f.readlines()

with open(argv[2],'r') as f:
    disLines = f.readlines()

disassembly = makeDisassembly(disLines)
table = makeTable(disassembly)
#printTrace(traceLines, disassembly, table)
#printTree(traceLines, disassembly, table)
printMenu(traceLines, disassembly, table)
