# coding=utf-8
import re
import os
import subprocess
import time
import json
import random
import shutil
from tqdm import tqdm
import csv
import pandas as pd


def create_dir():
    parent_dir = "D:\\hkn\\infected\\datasets"
    for workflow in range(40, 70):
        # 生成raw data文件夹
        infected = "virusshare_infected{}".format(workflow)
        cfg = "virusshare_infected{}_cfg".format(workflow)
        dot = "virusshare_infected{}_dot".format(workflow)
        jsonl = "virusshare_infected{}_json".format(workflow)
        create(parent_dir, infected)
        create(parent_dir, cfg)
        create(parent_dir, dot)
        create(parent_dir, jsonl)
        # iout = "virusshare_infected{}_iout".format(workflow)
        # os.rmdir(os.path.join(parent_dir, iout))
        # os.rmdir(os.path.join(parent_dir, ida))


def create(parent_dir, folder):
    if not os.path.exists(os.path.join(parent_dir, folder)):
        os.mkdir(os.path.join(parent_dir, folder))


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
    print('start checking json')
    for workflow in tqdm(range(0, 69)):
        json_dir = 'D:\\hkn\\infected\\datasets\\virusshare_infected{}_json'.format(workflow)
        for json_file in os.listdir(json_dir):
            f = open(os.path.join(json_dir, json_file), 'r')
            try:
                data = json.load(f)
            except UnicodeDecodeError:
                continue
            finally:
                f.close()

            if len(data['function_edges'][0]) == 0:
                print("{} {} function_edges null\n".format(workflow, json_file))
                # continue
            # for acfg in data['acfg_list']:
            #     if acfg['block_number'] != len(acfg['block_features']):
            #         print("{} {}\n".format(workflow, json_file))


# 临时函数，删除所有jsonl文件
def delete_jsonl():
    for workflow in range(0, 35):
        json_dir = 'D:\\hkn\\infected\\datasets\\virusshare_infected{}_json'.format(workflow)
        for f in os.listdir(json_dir):
            os.remove(os.path.join(json_dir, f))


def delete_all_local():
    data_dirs = ['D:\\hkn\\infected\\datasets\\virusshare_train\\1',
                 'D:\\hkn\\infected\\datasets\\virusshare_train\\2',
                 'D:\\hkn\\infected\\datasets\\virusshare_train\\3',
                 'D:\\hkn\\infected\\datasets\\virusshare_train\\4',
                 'D:\\hkn\\infected\\datasets\\virusshare_train\\5',
                 ]
    for d in data_dirs:
        path = os.listdir(d)
        for f in path:
            os.remove(os.path.join(d, f))


# 重命名pt文件使之与代码相符
def rename(mal_or_be, postfix):
    tag_set = ['train', 'test', 'valid']
    for tag in tag_set:
        data_dir = 'D:/hkn/infected/datasets/proprecessed_pt/{}_{}{}/'.format(tag, mal_or_be, postfix)
        for index, f in enumerate(os.listdir(data_dir)):
            os.rename(os.path.join(data_dir, f), os.path.join(data_dir, 'm' + f))
    for tag in tag_set:
        data_dir = 'D:/hkn/infected/datasets/proprecessed_pt/{}_{}{}/'.format(tag, mal_or_be, postfix)
        for index, f in enumerate(os.listdir(data_dir)):
            os.rename(os.path.join(data_dir, f), os.path.join(data_dir, '{}_{}.pt'.format(mal_or_be, index)))


def split_data_by_label():
    all = 'D:\\hkn\\infected\\datasets\\virusshare_train\\all_pt'
    dest = 'D:\\hkn\\infected\\datasets\\virusshare_train'
    csv_path = 'F:\\kkk\\dataset\\virusshare_AllLabel.csv'
    with open(csv_path, 'r') as label:
        label.readline()
        labels = label.readlines()
        for lines in labels:
            name, cls = lines.strip().split(',')
            fpath = os.path.join(all, name + '.pt')
            if os.path.exists(fpath):
                shutil.move(fpath, os.path.join(dest, cls))
            else:
                print(fpath, 'file not exist.')


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


# 临时工具，有些pe文件没有经过api分类，直接删掉
def del_redundant():
    for workflow in range(0, 68):
        pe_dir = 'D:\\hkn\\infected\\datasets\\virusshare_infected{}'.format(workflow)
        family_file_path = 'D:\\hkn\\infected\\datasets\\virusshare_family\\virusshare_family{}.txt'.format(workflow)

        with open(family_file_path, 'r') as f_file:
            family = f_file.read()
            for name in os.listdir(pe_dir):
                if name[11:] in family:
                    continue
                else:
                    # print(name)
                    os.remove(os.path.join(pe_dir, name))


def delete_pe():
    dot_dir = 'D:\\hkn\\infected\\datasets\\benign_dot'
    cfg_dir = 'D:\\hkn\\infected\\datasets\\benign_cfg'
    dot_list = os.listdir(dot_dir)
    for cfg in os.listdir(cfg_dir):
        name = cfg[:-4] + ".dot"
        if name in dot_list:
            continue
        else:
            print(os.path.join(dot_dir, name))
            # os.remove(os.path.join(dot_dir, cfg))


def delete_error_benign():
    jsonl_dir = 'F:\\kkk\\dataset\\benign\\refind_jsonl'
    dot_dir = 'F:\\kkk\\dataset\\benign\\refind_dot'
    cfg_dir = "F:\\kkk\\dataset\\benign\\refind_cfg"
    asm_dir = "F:\\kkk\\dataset\\benign\\refind_asm"
    pe_dir = "F:\\kkk\\dataset\\benign\\refind"
    alist = os.listdir(pe_dir)
    for f in alist:
        if not os.path.exists(os.path.join(jsonl_dir, f + '.jsonl')):
            os.remove(os.path.join(pe_dir, f))
            if os.path.exists(os.path.join(asm_dir, f + '.asm')):
                os.remove(os.path.join(asm_dir, f + '.asm'))
            if os.path.exists(os.path.join(cfg_dir, f + '.ida')):
                os.remove(os.path.join(cfg_dir, f + '.ida'))
            if os.path.exists(os.path.join(dot_dir, f + '.dot')):
                os.remove(os.path.join(dot_dir, f + '.dot'))


def generate_benign_csv():
    benign_pe_dir = 'F:\\kkk\\dataset\\benign\\refind'
    csv_out = 'F:\\kkk\\dataset\\benign_family.csv'
    fieldnames = ['Id', 'Class']
    with open(csv_out, "wb") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        for f in os.listdir(benign_pe_dir):
            writer.writerow({fieldnames[0]: f, fieldnames[1]: '5'})


def process_csv():
    csv_path = 'F:\\kkk\\dataset\\virusshare_AllLabel.csv'
    files = os.listdir('D:\\hkn\\infected\\datasets\\virusshare_train\\pe')
    print(files.__len__())
    df = df[df['Id'].isin(files)]
    df = df.drop_duplicates('Id')
    df['Id'] = 'VirusShare_' + df['Id']
    df.to_csv(csv_path, index=False)


def generate_virusshare_csv():
    index = {'wacatac': 1, 'ulpm': 2, 'fugrafa': 3, 'redcap': 4}
    fieldnames = ['Id', 'Class']
    pe_dir = 'D:\\hkn\\infected\\datasets\\virusshare_train\\pe'
    family_dir = 'D:\\hkn\\infected\\datasets\\virusshare_family'
    csv_out = 'D:\\hkn\\infected\\datasets\\virusshare_family.csv'
    with open(csv_out, "wb") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        for f in tqdm(os.listdir(family_dir)):
            with open(os.path.join(family_dir, f), 'r') as family:
                lines = family.readlines()
                for line in lines:
                    md5, label = line.strip().split('\t')
                    if label in index:
                        if os.path.exists(os.path.join(pe_dir, 'VirusShare_' + md5)):
                            writer.writerow({fieldnames[0]: 'VirusShare_' + md5, fieldnames[1]: index[label]})


def findlostone():
    pe_dir = 'D:\\hkn\\infected\\datasets\\virusshare_train\\pe'
    asm_dir = 'D:\\hkn\\infected\\datasets\\virusshare_train\\asm'
    for f in os.listdir(pe_dir):
        if not os.path.exists(os.path.join(asm_dir, f + '.asm')):
            print(f)


def find_pe_in_original_set():
    for workflow in range(0, 69):
        data_dir = 'D:\\hkn\\infected\\datasets\\virusshare_infected{}_json'.format(workflow)
        for f in os.listdir(data_dir):
            if f[:-6] == 'VirusShare_0f07b29873cf503a0fb69fa064ce76a3':
                print(workflow)
                return


def select_jsonl():
    csv_paths = 'F:\\kkk\\dataset\\virusshare_family.csv'
    jsonl_dir = 'D:\\hkn\\infected\\datasets\\virusshare_train\\malware_jsonl'

    with open(csv_paths, 'r') as csv_path:
        labels = csv.reader(csv_path, delimiter=',')
        data = list(labels)
        for workflow in range(0, 69):
            data_dir = 'D:\\hkn\\infected\\datasets\\virusshare_infected{}_json'.format(workflow)
            for f in os.listdir(data_dir):
                for line in data:
                    if f[:-6] in line:
                        shutil.copy(os.path.join(data_dir, f), jsonl_dir)
                        break


def generate_csv():
    pe_dir = 'D:\\hkn\\infected\\datasets\\virusshare_train\\5\\pe'
    csv_path = 'D:\\hkn\\infected\\datasets\\virusshare_train\\5\\virusshare_5.csv'
    fieldnames = ['Id', 'Class']
    with open(csv_path, "wb") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        for pe in os.listdir(pe_dir):
            writer.writerow({fieldnames[0]: pe, fieldnames[1]: 5})


def merge_csvs(cs, out):
    for i, c in enumerate(cs):
        if i == 0:
            merged = pd.read_csv(c)
        else:
            merged = pd.merge(pd.read_csv(c), merged, on='Id')
            # merged = pd.concat([merged, pd.read_csv(c)])

    # if 'Class' in merged:
    #     merged['Class'] = merged['Class'] - 1
    merged.to_csv(out, index=False)

if __name__ == '__main__':
    # find_pe_in_original_set()
    # split_data_by_label()
    # select_jsonl()
    # findlostone()
    # generate_csv()
    # generate_virusshare_csv()
    # merge_csvs([
    #     'D:\\hkn\\infected\\datasets\\virusshare_train\\virusshare_1_compliment.csv',
    #     'D:\\hkn\\infected\\datasets\\virusshare_family.csv',
    #     'D:\\hkn\\infected\\datasets\\virusshare_train\\virusshare_5.csv',
    # ],
    #     'D:\\hkn\\infected\\datasets\\virusshare_family.csv'
    # )
    process_csv()
    # generate_benign_csv()
    # create_pixel_intensity()
    # create_dir()
    # change_max_item_lines()
    # subprocess.call('taskkill /im idaq64.exe /f')
    # delete_error_benign()
    # test()
    # delete_jsonl()
    # delete_all_local()
    # check_json()
    # delete_pe()

    # rename('malware', '_backup')

    # 指定 'standard' or 'benign' or 'one_family'
    # standard表示处理所有恶意样本
    # split_samples()
    # one_family表示仅处理一个家族，仅用于测试原模型的二分类
    # split_samples('one_family')
    # benign表示处理良性样本
    # split_samples('benign')

    # half_divide()
    # copy_train_data()
    # clear_dot()
    # read_test()
    # del_redundant()