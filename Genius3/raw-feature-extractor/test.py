import re
import os
import subprocess
import time


def func():
    path = "D:\\hkn\\infected\\datasets\\virusshare_infected0_dot\\VirusShare_ccbfc20470b099a188bda55aa8421427.dot"
    result = []
    with open(path, 'r') as f:
        for line in f:
            if '->' in line:
                result.append(re.findall(r'\b\d+\b', line))
    print(result)


def func1():
    for f in os.listdir("D:\\hkn\\infected\\datasets\\virusshare_infected0_dot"):
        print(f[:-4])


def gen_dir():
    parent_dir = "D:\\hkn\\infected\\datasets"
    for workflow in range(0, 35):
        # infected = "virusshare_infected{}".format(workflow)
        # cfg = "virusshare_infected{}_cfg".format(workflow)
        # dot = "virusshare_infected{}_dot".format(workflow)
        # jsonl = "virusshare_infected{}_json".format(workflow)
        iout = "virusshare_infected{}_iout".format(workflow)

        # os.mkdir(os.path.join(parent_dir, infected))
        # os.mkdir(os.path.join(parent_dir, cfg))
        # os.mkdir(os.path.join(parent_dir, dot))
        # os.mkdir(os.path.join(parent_dir, jsonl))
        os.rmdir(os.path.join(parent_dir, iout))
        # os.rmdir(os.path.join(parent_dir, ida))


def change_max_item_lines():
    f = open("F:\\kkk\\IDA_6.6\\cfg\\ida.cfg", 'rb')
    s = f.read()
    f.close()
    index = s.find(b'MAX_ITEM_LINES          = 5000')
    news = s.replace(b'MAX_ITEM_LINES          = 5000', b'MAX_ITEM_LINES          = 50000')
    # print(news[index:index+50])
    f = open("F:\\kkk\\IDA_6.6\\cfg\\ida.cfg", 'wb')
    f.write(news)
    f.close()


def clock():
    TIMEOUT = 10
    start = time.time()
    flag_kill = True
    while time.time() - start <= TIMEOUT:
        if not p.is_alive():
            flag_kill = False
            break
        else:
            time.sleep(1)  # Just to avoid hogging the CPU

    if flag_kill:
        subprocess.call('taskkill /im idaq64.exe /f')


if __name__ == '__main__':
    # gen_dir()
    # change_max_item_lines()
    subprocess.call('taskkill /im idaq64.exe /f')

