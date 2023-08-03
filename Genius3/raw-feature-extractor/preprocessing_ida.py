# -*- coding: UTF-8 -*-
import pickle
from func import *
from raw_graphs import *
from idc import *
import idautils
import os
import sys


def preprocess():
    # E:\BaiduNetdiskDownload\IDA_Pro_v6.8\IDA_Pro_v6.8\idaq.exe -c -S"raw-feature-extractor/preprocessing_ida.py --path C:\Program1\pycharmproject\Genius3\acfgs" hpcenter
    # print str(sys.argv) #['raw-feature-extractor/preprocessing_ida.py']
    # print str(idc.ARGV) #['raw-feature-extractor/preprocessing_ida.py', '--path', 'C:\\Program1\\pycharmproject\\Genius3\\acfgs']
    # print idc.ARGV[2]
    # print type(idc.ARGV[2])

    binary_name = idc.GetInputFile()

    workflow = idc.ARGV[1]
    # workflow = 0
    cfg_path = "D:\\hkn\\infected\\datasets\\virusshare_infected{}_cfg".format(workflow)
    gdl_path = "D:\\hkn\\infected\\datasets\\virusshare_infected{}_dot\\{}.dot".format(workflow, binary_name)

    analysis_flags = idc.GetShortPrm(idc.INF_START_AF)
    analysis_flags &= ~idc.AF_IMMOFF
    idc.SetShortPrm(idc.INF_START_AF, analysis_flags)
    idaapi.autoWait()

    # 生成pe文件的cfg列表
    cfgs = get_func_cfgs_c(FirstSeg())
    # 生成pe文件的fcg
    # idc.GenCallGdl(gdl_path, 'Call Gdl', idc.CHART_GEN_GDL) 这个生成gdl文件，网上几乎找不到gdl这个格式
    idc.GenCallGdl(gdl_path, 'Call Gdl', idaapi.CHART_GEN_DOT)

    full_path = os.path.join(cfg_path, binary_name + '.ida')
    pickle.dump(cfgs, open(full_path, 'w'))

    # 由于命令行模式也必须打开ida pro，因此每次结束自动关闭ida
    idc.Exit(0)


# 通用命令行格式  idaq64 -c -A -S"preprocessing_ida.py arg1 arg2" VirusShare_bca58b12923073
# 此处使用 idaq64 -c -A -S"preprocessing_ida.py workflow" -oF:\iout pe_path，完整命令行如下
# F:\kkk\IDA_6.6\idaq64 -c -A -S"D:\hkn\project_folder\Gencoding3\Genius3\raw-feature-extractor\preprocessing_ida.py 0" -oF:\iout D:\hkn\infected\datasets\virusshare_infected0\VirusShare_bc161e5e792028e8137aa070fda53f82
if __name__ == '__main__':
    preprocess()
