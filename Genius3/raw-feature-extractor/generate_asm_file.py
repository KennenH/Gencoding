# coding=utf-8
from func import *
from idc import *


def generate_asm_file():
    binary_name = idc.GetInputFile()

    # workflow = idc.ARGV[1]

    analysis_flags = idc.GetShortPrm(idc.INF_START_AF)
    analysis_flags &= ~idc.AF_IMMOFF
    idc.SetShortPrm(idc.INF_START_AF, analysis_flags)
    idaapi.autoWait()

    # 生成pe文件的asm文件
    idc.GenerateFile(idc.OFILE_ASM, binary_name + ".asm", 0, idc.BADADDR, 0)

    # 由于命令行模式也必须打开ida pro，因此每次结束自动关闭ida
    idc.Exit(0)


if __name__ == '__main__':
    generate_asm_file()
