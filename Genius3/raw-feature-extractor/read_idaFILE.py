# -*- coding: UTF-8 -*-
import sys
import sys
from matplotlib import pyplot as plt
sys.path.insert(0, '/usr/local/lib/python2.7/dist-packages/')
sys.path.insert(1, 'C:/Python27/Lib/site-packages')
import networkx as nx
def print_obj(obj):
    "打印对象的所有属性"
    print(obj.__dict__)

import pickle

#sub_10F20 308  反编译代码有字符串，但是这个特征提取里没有字符串 constant，可能是间接引用的，不识别。看了下所有函数的特征，几乎都没有字符串常量，可能都是写在别的地方然后引用的。
#sub_166C4 393
if __name__ == '__main__':


    testpath = "C:\Program1\pycharmproject\Genius3/acfgs/hpcenter.ida"
    fr = open(testpath, 'r')
    data1 = pickle.load(fr) #一个二进制文件的acfgs
    #print(type(data1))
    #print_obj(data1)
    #print data1.raw_graph_list[393]
    #print_obj(data1.raw_graph_list[393])
    #nx.draw(data1.raw_graph_list[393].g,with_labels=True)
    #plt.show()

    print "一个二进制文件的所有函数的原始特征，list。"
    print_obj(data1) #acfg list
    print "\n"

    print "一个函数的原始特征，由old_g（discovRe方法的ACFG），g（Genius方法的ACFG），fun_feature（表示函数级别的特征的向量）三部分构成"
    print_obj(data1.raw_graph_list[393]) #一个函数的acfg
    print "\n"
    feature=data1.raw_graph_list[393].fun_features
    print "函数级别特征： # 1 function calls # 2 logic instructions # 3 TransferIns # 4 LocalVariables # 5 BB basicblocks# 6 Edges # 7 IncommingCalls# 8 Intrs# 9 between # 10 strings # 11 consts"
    print feature
    print "\n"


    # G=data1.raw_graph_list[393].old_g
    # print G.node[0] # G.node[i]是dict
    # for key, value in G.node[0].items():
    #     print('{key}:{value}'.format(key=key, value=value))

    # 一个基本块的特征 #1'consts' 数字常量 #2'strings'字符串常量 #3'offs' offspring 字节点数量？ #4'numAs' 算数指令如INC  #5'numCalls' 调用指令 #6'numIns' 指令数量 #7'numLIs' LogicInstructions 如AND #8'numTIs' 转移指令数量
    G=data1.raw_graph_list[393].g
    print "# 一个基本块的特征 #1'consts' 数字常量 #2'strings'字符串常量 #3'offs' offspring 字节点数量？ #4'numAs' 算数指令如INC  #5'numCalls' 调用指令 #6'numIns' 指令数量 #7'numLIs' LogicInstructions 如AND #8'numTIs' 转移指令数量"
    print G.node[0]
    print "\n"
    # for key, value in G.node[0].items():
    #     print('{key}:{value}'.format(key=key, value=value))



    #oldg就是读取IDA的CFG，所以数量、方向等都一样；g根据old_g生成，也一样
    #old g
    G = data1.raw_graph_list[393].old_g
    nx.draw(G,with_labels=True)
    #plt.title('old_g')
    plt.show()


    # g
    G = data1.raw_graph_list[393].g
    nx.draw(G,with_labels=True)
    #plt.title('Genius_g')
    plt.show()

    # draw graph with labels
    pos = nx.spring_layout(G)
    nx.draw(G, pos)
    node_labels = nx.get_node_attributes(G, 'v')  #networkx的node，由属性。g的属性为'v'，意为原始特征的vector。old_g的属性见cfg_constructor.py
    nx.draw_networkx_labels(G, pos, labels=node_labels)
    #plt.title('Genius_g with raw feature vector')
    plt.show()


# 1 function calls（本函数的函数调用指令（call jal jalr）数量）。。注意arm中没有这些指令

# 2 logic instructions ，本函数的逻辑运算指令数量。如and、or的数量

# 3 TransferIns 转移指令（如jmp arm中为mov）数量

# 4 LocalVariables 局部变量数量

# 5 BB basicblocks数量

# 6 Edges icfg edges数量。icfg是另一篇论文dicovRe中的特征，这里暂时不管

# 7 IncommingCalls，调用本函数的指令数量

# 8 Intrs 指令数量

# 9 between 结构特征中的betweeness。

# 10 strings 字符串

# 11 consts  数字常量