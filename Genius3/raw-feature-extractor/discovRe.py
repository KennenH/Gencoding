# coding=utf-8
#
# Reference Lister
#
# List all functions and all references to them in the current section.
#
# Implemented with the idautils module
#
import networkx as nx
import pdb
from graph_analysis_ida import *
from graph_property import *


# import wingdbstub
# wingdbstub.Ensure()

def get_funcs(ea):
    funcs = {}
    # Get current ea
    # Loop from start to end in the current segment
    for funcea in Functions(SegStart(ea)):
        funcname = GetFunctionName(funcea)
        func = get_func(funcea)
        blocks = FlowChart(func)
        funcs[funcname] = []
        for bl in blocks:
            start = bl.startEA
            end = bl.endEA
            funcs[funcname].append((start, end))
    return funcs


# 似乎是没用的函数
# def get_funcs_for_discoverRe(ea):
#     features = {}
#     for funcea in Functions(SegStart(ea)):
#         funcname = GetFunctionName(funcea)
#         print(funcname)
#         func = get_func(funcea)
#         feature = get_discoverRe_feature(func)
#         features[funcname] = feature
#     return features


# 获取所有bb的11维属性特征
# 调用/传输/算术/逻辑/比较/移动/终止/数据声明/总指令数/字符串或整数常量/后代的数量
def get_bb_features(func):
    bb_features = []
    blocks = [(v.startEA, v.endEA) for v in FlowChart(func)]
    for bl in blocks:
        calls = calCalls(bl)
        transferIns = calTransferIns(bl)
        mathematicsIns = calArithmeticIns(bl)
        logicIns = calLogicInstructions(bl)
        cmpIns = calIns(bl, {'cmp': 1, 'cmps': 1, 'cmpsb': 1, 'cmppd': 1, 'cmpps': 1, 'fcom': 1, 'fcomp': 1, 'fcompp': 1, 'ficom': 1, 'ficomp': 1, 'ptest': 1, 'test': 1})
        movIns = calIns(bl, {'mov': 1, 'movb': 1, 'movw': 1, 'movl': 1, 'movq': 1, 'movabsq': 1, 'push': 1, 'pop': 1, 'lea': 1})
        interruptIns = calIns(bl, {'int1': 1, 'int3': 1, 'into': 1, 'iret': 1, 'iretd': 1, 'iretq': 1})
        declareIns = calIns(bl, {'dw': 1, 'dd': 1, 'db': 1})
        totalIns = calInsts(bl)
        consts = getBBconsts(bl)
        stringOrIntConsts = len(consts[0]) + len(consts[1])
        bb_features.append([calls, transferIns, mathematicsIns, logicIns, cmpIns, movIns,
                            interruptIns, declareIns, totalIns, stringOrIntConsts])
    return bb_features


def get_discoverRe_feature(func, icfg):
    start = func.startEA
    end = func.endEA
    features = []
    FunctionCalls = getFuncCalls(func)
    # 1
    features.append(FunctionCalls)
    LogicInstr = getLogicInsts(func)
    # 2
    features.append(LogicInstr)
    Transfer = getTransferInsts(func)
    # 3
    features.append(Transfer)
    Locals = getLocalVariables(func)
    # 4
    features.append(Locals)
    BB = getBasicBlocks(func)
    # 5
    features.append(BB)
    Edges = len(icfg.edges())
    # 6
    features.append(Edges)
    Incoming = getIncommingCalls(func)
    # 7
    features.append(Incoming)
    # 8
    Instrs = getIntrs(func)
    features.append(Instrs)
    between = retrieveGP(icfg)
    # 9
    features.append(between)

    strings, consts = getfunc_consts(func)
    # 10
    features.append(strings)
    # 11
    features.append(consts)
    return features


def get_func_names(ea):
    funcs = {}
    for funcea in Functions(SegStart(ea)):
        funcname = GetFunctionName(funcea)
        funcs[funcname] = funcea
    return funcs


def get_func_bases(ea):
    funcs = {}
    for funcea in Functions(SegStart(ea)):
        funcname = GetFunctionName(funcea)
        funcs[funcea] = funcname
    return funcs


def get_func_range(ea):
    funcs = {}
    for funcea in Functions(SegStart(ea)):
        funcname = GetFunctionName(funcea)
        func = get_func(funcea)
        funcs[funcname] = (func.startEA, func.endEA)
    return funcs


def get_func_sequences(ea):
    funcs_bodylist = {}
    funcs = get_funcs(ea)
    for funcname in funcs:
        if funcname not in funcs_bodylist:
            funcs_bodylist[funcname] = []
        for start, end in funcs[funcname]:
            inst_addr = start
            while inst_addr <= end:
                opcode = GetMnem(inst_addr)
                funcs_bodylist[funcname].append(opcode)
                inst_addr = NextHead(inst_addr)
    return funcs_bodylist


def get_func_cfgs(ea):
    func_cfglist = {}
    i = 0
    start, end = get_section('LOAD')
    # print start, end
    for funcea in Functions(SegStart(ea)):
        if start <= funcea <= end:
            funcname = GetFunctionName(funcea)
            func = get_func(funcea)
            print(i)
            i += 1
            try:
                icfg = cfg.cfg_construct(func)
                func_cfglist[funcname] = icfg
            except:
                pass

    return func_cfglist


def get_section(t):
    base = SegByName(t)
    start = SegByBase(base)
    end = SegEnd(start)
    return start, end


def get_func_cfg_sequences(func_cfglist):
    func_cfg_seqlist = {}
    for funcname in func_cfglist:
        func_cfg_seqlist[funcname] = {}
        cfg = func_cfglist[funcname][0]
        for start, end in cfg:
            codesq = get_sequences(start, end)
            func_cfg_seqlist[funcname][(start, end)] = codesq

    return func_cfg_seqlist


def get_sequences(start, end):
    seq = []
    inst_addr = start
    while inst_addr <= end:
        opcode = GetMnem(inst_addr)
        seq.append(opcode)
        inst_addr = NextHead(inst_addr)
    return seq


def get_stack_arg(func_addr):
    print(func_addr)
    args = []
    stack = GetFrame(func_addr)
    if not stack:
        return []
    firstM = GetFirstMember(stack)
    lastM = GetLastMember(stack)
    i = firstM
    while i <= lastM:
        mName = GetMemberName(stack, i)
        mSize = GetMemberSize(stack, i)
        if mSize:
            i = i + mSize
        else:
            i = i + 4
        if mName not in args and mName and ' s' not in mName and ' r' not in mName:
            args.append(mName)
    return args

    # pickle.dump(funcs, open('C:/Documents and Settings/Administrator/Desktop/funcs','w'))


def processDataSegs():
    funcdata = {}
    datafunc = {}
    for n in xrange(idaapi.get_segm_qty()):
        seg = idaapi.getnseg(n)
        ea = seg.startEA
        segtype = idc.GetSegmentAttr(ea, idc.SEGATTR_TYPE)
        if segtype in [idc.SEG_DATA, idc.SEG_BSS]:
            start = idc.SegStart(ea)
            end = idc.SegEnd(ea)
            cur = start
            while cur <= end:
                refs = [v for v in DataRefsTo(cur)]
                for fea in refs:
                    name = GetFunctionName(fea)
                    if len(name) == 0:
                        continue
                    if name not in funcdata:
                        funcdata[name] = [cur]
                    else:
                        funcdata[name].append(cur)
                    if cur not in datafunc:
                        datafunc[cur] = [name]
                    else:
                        datafunc[cur].append(name)
                cur = NextHead(cur)
    return funcdata, datafunc


def obtainDataRefs(callgraph):
    datarefs = {}
    funcdata, datafunc = processDataSegs()
    for node in callgraph:
        if node in funcdata:
            datas = funcdata[node]
            for dd in datas:
                refs = datafunc[dd]
                refs = list(set(refs))
                if node in datarefs:
                    print(refs)
                    datarefs[node] += refs
                    datarefs[node] = list(set(datarefs[node]))
                else:
                    datarefs[node] = refs
    return datarefs
