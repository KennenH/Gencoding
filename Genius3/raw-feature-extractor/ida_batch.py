# coding=utf-8
import re
import os
import subprocess
import multiprocessing
from tqdm import tqdm
import time

# 单个pe文件处理超时/s
# 多次处理，一批数据中只有少量文件会超时
# 所有数据处理完成后可以对这些数据再进行一次更长超时时间的处理，若仍然超时则放弃
TIMEOUT = 60

# 每个家族最大处理数量
MAX_FAMILY_PROCESS_NUM = 200


def call_preprocess(cmd_line):
    subprocess.call(cmd_line, shell=True)


# 良性软件分析模式，ida的命令中将workflow改为-1
def benign_batch_mode(overhaul):
    # 总失败数据数量
    total_failed = 0

    log_path = 'D:\\hkn\\infected\\datasets\\logging\\ida_log_benign.log'
    process_log_path = 'D:\\hkn\\infected\\datasets\\logging\\ida_process_log_benign.log'
    benign_pe_dir = 'D:\\hkn\\infected\\datasets\\benign\\new'

    if overhaul:
        if os.path.exists(log_path):
            os.remove(log_path)
        if os.path.exists(process_log_path):
            os.remove(process_log_path)

    with open(log_path, 'a+') as log, open(process_log_path, 'a+') as process_log:
        logged = log.readline()
        if logged == '':
            log_index = 0
        else:
            log_index = int(logged)

        for index, pe in enumerate(tqdm(sorted(os.listdir(benign_pe_dir)))):
            if index < log_index:
                continue

            cmd_line = r'idaq64 -c -A -S"D:\hkn\project_folder\Gencoding3\Genius3\raw-feature-extractor\preprocessing_ida.py -1" -oF:\iout {}'.format(
                os.path.join(benign_pe_dir, pe))

            p = multiprocessing.Process(target=call_preprocess, args=[cmd_line])
            p.start()
            flag_kill = True
            start = time.time()
            while time.time() - start <= TIMEOUT:
                if not p.is_alive():
                    flag_kill = False
                    break
                else:
                    time.sleep(1)

            if flag_kill:
                subprocess.call('taskkill /im idaq64.exe /f')
                process_log.write(
                    "index {}, {} stuck, process terminated.\n".format(index, pe))

                total_failed += 1
            else:
                # 正常运行结束
                log.truncate(0)
                log.seek(0)
                log.write(str(index))
                log.flush()
                process_log.write("index {}, {} process done.\n".format(index, pe))
    # 所有副产物删除
    delete_output()

    print('总失败数{}'.format(total_failed))


def mal_batch_mode(start, end):
    # 只选其中这些类的pe进行分析，其他的就直接跳过
    families_need_to_analyze = {'wacatac': 0, 'glupteba': 0, 'ulpm': 0, 'fugrafa': 0, 'tiggre': 0,
                                'redcap': 0, 'generickdz': 0, 'berbew': 0, 'agenttesla': 0, 'lazy': 0}
    # 记录ida处理报错的数据来自哪些家族
    failed_family = {'wacatac': 0, 'glupteba': 0, 'ulpm': 0, 'fugrafa': 0, 'tiggre': 0,
                     'redcap': 0, 'generickdz': 0, 'berbew': 0, 'agenttesla': 0, 'lazy': 0}
    # 总失败数据数量
    total_failed = 0

    for workflow in range(start, end):
        # pe_dir = 'D:\\hkn\\infected\\datasets\\virusshare_test'
        pe_dir = 'D:\\hkn\\infected\\datasets\\virusshare_infected{}'.format(workflow)
        family_path = 'D:\\hkn\\infected\\datasets\\virusshare_family\\virusshare_family{}.txt'.format(workflow)
        log_path = 'D:\\hkn\\infected\\datasets\\logging\\ida_log{}.log'.format(workflow)
        process_log_path = 'D:\\hkn\\infected\\datasets\\logging\\ida_process_log{}.log'.format(workflow)
        with open(log_path, 'a+') as log, open(process_log_path, 'a+') as process_log, open(family_path,
                                                                                            'r') as family_file:
            logged = log.readline()
            if logged == '':
                log_index = 0
            else:
                log_index = int(logged)

            families = family_file.read()
            for index, pe in enumerate(tqdm(sorted(os.listdir(pe_dir)))):
                if index < log_index:
                    continue

                # 匹配文件md5，取出family文件中该md5的家族
                regex = re.compile(pe[11:] + r'[\t][\S]*')
                search_result = regex.findall(families)
                if len(search_result) == 0:
                    continue

                pe_family = search_result[0].split()[1]
                if pe_family not in families_need_to_analyze:
                    continue

                # FOR TEST ONLY
                # cmd_line = r'idaq64 -c -A -S"D:\hkn\project_folder\Gencoding3\Genius3\raw-feature-extractor\preprocessing_ida.py {}" -oF:\iout {}'.format(
                #     workflow, os.path.join(pe_dir, pe))
                cmd_line = r'idaq64 -c -A -S"D:\hkn\project_folder\Gencoding3\Genius3\raw-feature-extractor\preprocessing_ida.py {}" -oF:\iout {}'.format(
                    workflow, os.path.join(pe_dir, pe))

                p = multiprocessing.Process(target=call_preprocess, args=[cmd_line])
                p.start()
                flag_kill = True
                start = time.time()
                while time.time() - start <= TIMEOUT:
                    if not p.is_alive():
                        flag_kill = False
                        break
                    else:
                        time.sleep(1)

                if flag_kill:
                    subprocess.call('taskkill /im idaq64.exe /f')
                    process_log.write(
                        "index {}, {} in workflow {} stuck, process terminated.\n".format(index, pe, workflow))

                    failed_family[pe_family] += 1
                    total_failed += 1
                else:
                    # 正常运行结束
                    log.truncate(0)
                    log.seek(0)
                    log.write(str(index))
                    log.flush()
                    process_log.write("index {}, {} process done.\n".format(index, pe))

                    families_need_to_analyze[pe_family] += 1
        # 一次workflow结束后将所有副产物删除
        delete_output()

    print(families_need_to_analyze)
    print('\n')
    print(failed_family, '总失败数{}'.format(total_failed))


def delete_output():
    out_dir = 'F:\\iout'
    for f in os.listdir(out_dir):
        if os.path.exists(os.path.join(out_dir, f)):
            os.remove(os.path.join(out_dir, f))


# 注意：该py文件必须放在IDA的根目录下，且必须使用cmd命令执行，否则无法链接到python库
# F:\\kkk\\IDA_6.6
if __name__ == '__main__':
    benign_batch_mode(True)
    # mal_batch_mode(35, 69)
