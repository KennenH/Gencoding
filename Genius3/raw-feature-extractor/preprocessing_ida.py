# -*- coding: UTF-8 -*-
import sys

from func import *
from raw_graphs import *
from idc import *
import os
import argparse
import raw_graphs

def print_obj(obj):
    "打印对象的所有属性"
    print(obj.__dict__)

def parse_command():
	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument("--path", type=str, help="The directory where to store the generated .ida file")
	args = parser.parse_args()
	return args

if __name__ == '__main__':
	#E:\BaiduNetdiskDownload\IDA_Pro_v6.8\IDA_Pro_v6.8\idaq.exe -c -S"raw-feature-extractor/preprocessing_ida.py --path C:\Program1\pycharmproject\Genius3\acfgs" hpcenter
	#print str(sys.argv) #['raw-feature-extractor/preprocessing_ida.py']
	#print str(idc.ARGV) #['raw-feature-extractor/preprocessing_ida.py', '--path', 'C:\\Program1\\pycharmproject\\Genius3\\acfgs']
	#print idc.ARGV[2]
	#print type(idc.ARGV[2])

	# E:\BaiduNetdiskDownload\IDA_Pro_v6.8\IDA_Pro_v6.8\idaq.exe  -c -A -S"raw-feature-extractor/preprocessing_ida.py --path C:\Program1\pycharmproject\Genius4\acfgs" hpcenter
	#测试生成原始特征的时间。
	start_t = time.clock()

	args = parse_command()
	#path = args.path
	path = idc.ARGV[2]
	analysis_flags = idc.GetShortPrm(idc.INF_START_AF)
	analysis_flags &= ~idc.AF_IMMOFF
	# turn off "automatically make offset" heuristic
	idc.SetShortPrm(idc.INF_START_AF, analysis_flags)
	idaapi.autoWait()
	cfgs = get_func_cfgs_c(FirstSeg())

	end_t = time.clock()
	print (end_t - start_t) #1.5934438s hpcenter 83.4 KB    #35.6745299s SCGDW698 5.5mb  #14.1480888s  762kb   SCMQTTIot     这个时间包括ida分析二进制文件的时间和脚本生成对应原始特征的时间
	# 应该是随着函数和基本块的数量增加而线性增加的，先不写了。可能ida分析二进制文件的占比比较高

	binary_name = idc.GetInputFile() + '.ida'
	print path
	print binary_name
	fullpath = os.path.join(path, binary_name)
	pickle.dump(cfgs, open(fullpath,'w'))
	#print binary_name



	#加上这句，脚本执行完就退出IDA
	#idc.Exit(0)