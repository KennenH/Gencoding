# coding=utf-8
import re
import os
import subprocess
import time
import json
import random
import shutil


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


def create_dir():
    parent_dir = "D:\\hkn\\infected\\datasets"
    for workflow in range(35, 40):
        # 生成raw data文件夹
        # infected = "virusshare_infected{}".format(workflow)
        # cfg = "virusshare_infected{}_cfg".format(workflow)
        # dot = "virusshare_infected{}_dot".format(workflow)
        jsonl = "virusshare_infected{}_json".format(workflow)
        # os.mkdir(os.path.join(parent_dir, infected))
        # os.mkdir(os.path.join(parent_dir, cfg))
        # os.mkdir(os.path.join(parent_dir, dot))
        os.mkdir(os.path.join(parent_dir, jsonl))
        # iout = "virusshare_infected{}_iout".format(workflow)
        # os.rmdir(os.path.join(parent_dir, iout))
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


def delete_error():
    for workflow in range(0, 35):
        convert_log_path = "D:\\hkn\\infected\\datasets\\logging\\convert_process_log{}.log".format(workflow)
        json_dir = "D:\\hkn\\infected\\datasets\\virusshare_infected{}_json".format(workflow)

        with open(convert_log_path, 'r') as log:
            for line in log:
                if 'Error occurred' in line:
                    name = line[line.find(',') + 2: line.find('.')] + '.jsonl'
                    # print(os.path.join(json_dir, name))
                    if os.path.exists(os.path.join(json_dir, name)):
                        os.remove(os.path.join(json_dir, name))


def check_json():
    for workflow in range(5, 16):
        json_dir = 'D:\\hkn\\infected\\datasets\\virusshare_infected{}_json'.format(workflow)
        for json_file in os.listdir(json_dir):
            f = open(os.path.join(json_dir, json_file), 'r')
            try:
                data = json.load(f)
            except UnicodeDecodeError:
                continue
            finally:
                f.close()
            for acfg in data['acfg_list']:
                if acfg['block_number'] != len(acfg['block_features']):
                    print("{} {}\n".format(workflow, json_file))


# 临时函数，删除所有jsonl文件
def delete_jsonl():
    for workflow in range(0, 35):
        json_dir = 'D:\\hkn\\infected\\datasets\\virusshare_infected{}_json'.format(workflow)
        for f in os.listdir(json_dir):
            os.remove(os.path.join(json_dir, f))


# 临时函数，重命名pt文件使之与代码相符
def rename():
    tag_set = ['train', 'test', 'valid']
    for tag in tag_set:
        data_dir = 'D:/hkn/infected/datasets/proprecessed_pt/{}_malware/'.format(tag)
        for index, f in enumerate(os.listdir(data_dir)):
            os.rename(os.path.join(data_dir, f), os.path.join(data_dir, 'm' + f))
    for tag in tag_set:
        data_dir = 'D:/hkn/infected/datasets/proprecessed_pt/{}_malware/'.format(tag)
        for index, f in enumerate(os.listdir(data_dir)):
            os.rename(os.path.join(data_dir, f), os.path.join(data_dir, 'malware_{}.pt'.format(index)))


def split_samples():
    path = 'D:\\hkn\\infected\\datasets\\proprecessed_pt\\all'
    out = 'D:\\hkn\\infected\\datasets\\proprecessed_pt'
    os_list = os.listdir(path)
    random.shuffle(os_list)
    # 8/1/1 分数据
    train_len = int(len(os_list) * 0.8)
    test_len = int(train_len / 8)
    for index, f in enumerate(os_list):
        if index < train_len:
            shutil.copy(os.path.join(path, f), os.path.join(out, 'train_malware'))
        elif train_len <= index < train_len + test_len:
            shutil.copy(os.path.join(path, f), os.path.join(out, 'test_malware'))
        else:
            shutil.copy(os.path.join(path, f), os.path.join(out, 'valid_malware'))


def half_divide():
    src = 'D:\\hkn\\infected\\datasets\\proprecessed_pt'

    test = 'D:\\hkn\\infected\\datasets\\proprecessed_pt\\test_malware'
    valid = 'D:\\hkn\\infected\\datasets\\proprecessed_pt\\valid_malware'

    flag = True
    for f in os.listdir(src):
        if 'pt' not in f:
            continue
        if flag:
            shutil.copy(os.path.join(src, f), test)
        else:
            shutil.copy(os.path.join(src, f), valid)
        flag = not flag


def copy_train_data():
    all = 'D:\\hkn\\infected\\datasets\\proprecessed_pt\\all'
    dest = 'D:\\hkn\\infected\\datasets\\proprecessed_pt\\train_malware'
    train = set(os.listdir(all)) - set(os.listdir('D:\\hkn\\infected\\datasets\\proprecessed_pt\\test_malware')) - set(os.listdir('D:\\hkn\\infected\\datasets\\proprecessed_pt\\valid_malware'))
    for f in train:
        shutil.copy(os.path.join(all, f), dest)


def clear_dot():
    for workflow in range(0, 35):
        path = 'D:\\hkn\\infected\\datasets\\virusshare_infected{}_dot\\'.format(workflow)
        for name in os.listdir(path):
            full = os.path.join(path, name)
            f = open(full, 'r')
            data = f.read()
            f.close()
            if 'start' not in data and 'sub_' not in data:
                # print("delete")
                os.remove(full)


def read_test():
    dot_file_path = "D:\\hkn\\infected\\datasets\\virusshare_infected23_dot\\VirusShare_9ba64176b2ca61212ff56a5b4eb546ff.dot"
    with open(dot_file_path, 'r') as dot:
        for line in dot:
            if '->' in line:
                print(re.findall(r'\b\d+\b', line))
            elif 'label' in line:
                print(line[line.find('= "') + 3:line.find('",')])


if __name__ == '__main__':
    # create_dir()
    # change_max_item_lines()
    # subprocess.call('taskkill /im idaq64.exe /f')
    # delete_error()
    # test()
    # delete_jsonl()
    # check_json()
    split_samples()
    rename()
    # half_divide()
    # copy_train_data()
    # clear_dot()
    # read_test()