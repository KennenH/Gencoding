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
	#print str(sys.argv) #['raw-feature-extractor/preprocessing_ida.py']
	#print str(idc.ARGV) #['raw-feature-extractor/preprocessing_ida.py', '--path', 'C:\\Program1\\pycharmproject\\Genius3\\new']
	#print idc.ARGV[2]
	#print type(idc.ARGV[2])
	args = parse_command()
	#path = args.path
	path = idc.ARGV[2]
	analysis_flags = idc.GetShortPrm(idc.INF_START_AF)
	analysis_flags &= ~idc.AF_IMMOFF
	# turn off "automatically make offset" heuristic
	idc.SetShortPrm(idc.INF_START_AF, analysis_flags)
	idaapi.autoWait()
	cfgs = get_func_cfgs_c(FirstSeg())
	binary_name = idc.GetInputFile() + '.ida'
	print path
	print binary_name
	fullpath = os.path.join(path, binary_name)
	pickle.dump(cfgs, open(fullpath,'w'))
	#print binary_name

	testpath="C:\Program1\pycharmproject\Genius3/acfgs/hpcenter.ida"
	fr = open(fullpath,'r')
	data1 = pickle.load(fr)
	print(type(data1)) #<type 'instance'>
	print(data1.raw_graph_list[393].__dict__)
	print(data1.raw_graph_list[393].g)
	print(data1.raw_graph_list[393].g.nodes())
	#print_obj(data1)
	#print cfgs.raw_graph_list[0]
	#idc.Exit(0)