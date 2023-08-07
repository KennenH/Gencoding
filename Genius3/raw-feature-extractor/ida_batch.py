# coding=utf-8
import os
import subprocess
import multiprocessing
from tqdm import tqdm
import time

# 单个pe文件处理超时/s
# 多次处理，一批数据中只有少量文件会超时
# 所有数据处理完成后可以对这些数据再进行一次更长超时时间的处理，若仍然超时则放弃
TIMEOUT = 60


def call_preprocess(cmd_line):
    subprocess.call(cmd_line, shell=True)


def batch_mode():
    for workflow in range(1, 20):
        # workflow = 0
        pe_dir = 'D:\\hkn\\infected\\datasets\\virusshare_infected{}'.format(workflow)
        # for test
        # pe_dir = 'D:\\hkn\\infected\\datasets\\virusshare_test'
        log_path = 'D:\\hkn\\infected\\datasets\\logging\\ida_log{}.log'.format(workflow)
        process_log_path = 'D:\\hkn\\infected\\datasets\\logging\\ida_process_log{}.log'.format(workflow)
        with open(log_path, 'a+') as log, open(process_log_path, 'a+') as process_log:
            logged = log.readline()
            if logged == '':
                log_index = 0
            else:
                log_index = int(logged)

            # pe = "VirusShare_bc161e5e792028e8137aa070fda53f82"
            for index, pe in enumerate(tqdm(sorted(os.listdir(pe_dir)))):
                if index < log_index:
                    continue

                # for test
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
                else:
                    # 正常运行结束
                    log.truncate(0)
                    log.seek(0)
                    log.write(str(index))
                    log.flush()
                    process_log.write("index {}, {} process done.\n".format(index, pe))
    # 一次workflow结束后将所有副产物删除
    delete_output()


def delete_output():
    out_dir = 'F:\\iout'
    os.rmdir(out_dir)
    os.mkdir(out_dir)


# 注意：该py文件必须放在IDA的根目录下，且必须使用cmd命令执行，否则无法链接到python库
if __name__ == '__main__':
    batch_mode()
