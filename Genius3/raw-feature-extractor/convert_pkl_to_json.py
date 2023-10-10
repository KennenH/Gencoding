# coding=utf-8
import pickle as pk
import re
import json
import os
from tqdm import tqdm


def convert(start, end, overhaul):
    for workflow in range(start, end):
        # workflow = 0
        cfg_dir = "D:\\hkn\\infected\\datasets\\virusshare_infected{}_cfg".format(workflow)
        output_dir = "D:\\hkn\\infected\\datasets\\virusshare_infected{}_json".format(workflow)
        dot_dir = "D:\\hkn\\infected\\datasets\\virusshare_infected{}_dot".format(workflow)

        log_path = "D:\\hkn\\infected\\datasets\\logging\\convert_log{}.log".format(workflow)
        process_log_path = "D:\\hkn\\infected\\datasets\\logging\\convert_process_log{}.log".format(workflow)

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

            for index, cfg in enumerate(tqdm(os.listdir(cfg_dir))):
                if index < log_index:
                    continue

                name = cfg[:-4]  # 纯文件名，不带后缀
                cfg_file = open(os.path.join(cfg_dir, name + '.ida'), 'r')
                try:
                    data = pk.load(cfg_file)
                except EOFError:
                    process_log.write("index {}, {} process failed. EOFError occurred.\n".format(index, cfg))
                    continue
                except ValueError:
                    process_log.write("index {}, {} process failed. ValueError occurred.\n".format(index, cfg))
                    continue
                finally:
                    cfg_file.close()

                dot_file_path = os.path.join(dot_dir, name + '.dot')
                if not os.path.exists(dot_file_path):
                    process_log.write("index {}, {} process failed. dot file not exists.\n".format(index, cfg))
                else:
                    # 打开dot文件获取fcg
                    raw_function_edges = []
                    # 2023.8.12 bug fix: ida生成的fcg(.dot)文件包含了所有函数，data.raw_graph_list仅包含了内部函数
                    functions_list = []
                    with open(dot_file_path, 'r') as dot:
                        for line in dot:
                            if '->' in line:
                                raw_function_edges.append(re.findall(r'\b\d+\b', line))
                            elif 'label' in line:
                                functions_list.append(line[line.find('= "') + 3:line.find('",')])

                    # 没有内部函数被检测到，正常来说不应该，保险起见还是不要这数据了
                    if raw_function_edges.__len__() == 0:
                        continue

                    # 为当前pe文件创建json对象
                    json_obj = {
                        'hash': data.binary_name[11:],
                        # 2023.8.12 bug fix: 这里获取的是内部函数的数量
                        # 'function_number': data.raw_graph_list.__len__(),
                        'function_number': len(functions_list),
                        'function_edges': [[int(d[0]) for d in raw_function_edges],
                                           [int(d[1]) for d in raw_function_edges]],
                        'acfg_list': [],
                        'function_names': functions_list
                    }

                    # 2023.8.12 bug fix: data.raw_graph_list是ida检测到的内部函数，不包括外部函数，因此函数列表和函数数量不能从这里获取
                    # 读取pkl文件，一个acfg由一个函数分解而来
                    for acfg in data.raw_graph_list:
                        # 函数为外部函数，不需要构建cfg
                        if acfg.funcname != 'start' and acfg.funcname != 'start_0' and 'sub_' not in acfg.funcname:
                            continue

                        # 这里2是因为Genius框架提取特征时将后代数量放在2
                        offspring = [d.get('v')[2] for d in acfg.g.node.values()]
                        # 这边可能会出现不知名的原因两个数组长度不一致，按理来说应该是一致的
                        # 以框架为主，将bb_features数组削减为和g.node长度一致
                        diff = acfg.g.__len__() - len(acfg.bb_features)
                        if diff != 0:
                            del acfg.bb_features[diff:]
                        # 将后代数量的特征放入bb_features中

                        for i, offs in enumerate(offspring):
                            acfg.bb_features[i].append(offs)

                        acfg_item = {
                            'block_number': acfg.g.__len__(),
                            'block_edges': [[d[0] for d in acfg.g.edges], [d[1] for d in acfg.g.edges]],
                            'block_features': acfg.bb_features
                        }

                        json_obj['acfg_list'].append(acfg_item)
                        # json_obj['function_names'].append(acfg.funcname)

                    # 将结果写入json本地文件
                    result = json.dumps(json_obj, ensure_ascii=False)

                    with open(os.path.join(output_dir, name + '.jsonl'), 'w') as out:
                        out.write(result)

                    log.truncate(0)
                    log.seek(0)
                    log.write(str(index))
                    log.flush()
                    process_log.write("index {}, {} process done.\n".format(index, cfg))


def convert_benign(overhaul):
    cfg_dir = "D:\\hkn\\infected\\datasets\\benign_cfg\\new"
    output_dir = "D:\\hkn\\infected\\datasets\\benign_json\\new"
    dot_dir = "D:\\hkn\\infected\\datasets\\benign_dot\\new"

    log_path = "D:\\hkn\\infected\\datasets\\logging\\convert_benign_log.log"
    process_log_path = "D:\\hkn\\infected\\datasets\\logging\\convert_benign_process_log{}.log"

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

        for index, cfg in enumerate(tqdm(os.listdir(cfg_dir))):
            if index < log_index:
                continue

            name = cfg[:-4]  # 纯文件名
            cfg_file = open(os.path.join(cfg_dir, name + '.ida'), 'r')
            try:
                data = pk.load(cfg_file)
            except EOFError:
                process_log.write("index {}, {} process failed. EOFError occurred.\n".format(index, cfg))
                continue
            except ValueError:
                process_log.write("index {}, {} process failed. ValueError occurred.\n".format(index, cfg))
                continue
            finally:
                cfg_file.close()

            dot_file_path = os.path.join(dot_dir, name + '.dot')
            if not os.path.exists(dot_file_path):
                process_log.write("index {}, {} process failed. dot file not exists.\n".format(index, cfg))
            else:
                # 打开dot文件获取fcg
                raw_function_edges = []
                # 2023.8.12 bug fix: ida生成的fcg(.dot)文件包含了所有函数，data.raw_graph_list仅包含了内部函数
                functions_list = []
                with open(dot_file_path, 'r') as dot:
                    for line in dot:
                        if '->' in line:
                            raw_function_edges.append(re.findall(r'\b\d+\b', line))
                        elif 'label' in line:
                            functions_list.append(line[line.find('= "') + 3:line.find('",')])

                # 没有内部函数被检测到，正常来说不应该，保险起见还是不要这数据了
                if raw_function_edges.__len__() == 0:
                    continue

                # 为当前pe文件创建json对象
                json_obj = {
                    'hash': data.binary_name[11:],
                    # 2023.8.12 bug fix: 这里获取的是内部函数的数量
                    # 'function_number': data.raw_graph_list.__len__(),
                    'function_number': len(functions_list),
                    'function_edges': [[int(d[0]) for d in raw_function_edges],
                                       [int(d[1]) for d in raw_function_edges]],
                    'acfg_list': [],
                    'function_names': functions_list
                }

                # 2023.8.12 bug fix: data.raw_graph_list是ida检测到的内部函数，不包括外部函数，因此函数列表和函数数量不能从这里获取
                # 读取pkl文件，一个acfg由一个函数分解而来
                for acfg in data.raw_graph_list:
                    # 函数为外部函数，不需要构建cfg
                    if acfg.funcname != 'start' and acfg.funcname != 'start_0' and 'sub_' not in acfg.funcname:
                        continue

                    # 这里2是因为Genius框架提取特征时将后代数量放在2
                    offspring = [d.get('v')[2] for d in acfg.g.node.values()]
                    # 这边可能会出现不知名的原因两个数组长度不一致，按理来说应该是一致的
                    # 以框架为主，将bb_features数组削减为和g.node长度一致
                    diff = acfg.g.__len__() - len(acfg.bb_features)
                    if diff != 0:
                        del acfg.bb_features[diff:]
                    # 将后代数量的特征放入bb_features中

                    for i, offs in enumerate(offspring):
                        acfg.bb_features[i].append(offs)

                    acfg_item = {
                        'block_number': acfg.g.__len__(),
                        'block_edges': [[d[0] for d in acfg.g.edges], [d[1] for d in acfg.g.edges]],
                        'block_features': acfg.bb_features
                    }

                    json_obj['acfg_list'].append(acfg_item)
                    # json_obj['function_names'].append(acfg.funcname)

                # 将结果写入json本地文件
                result = json.dumps(json_obj, ensure_ascii=False)

                with open(os.path.join(output_dir, name + '.jsonl'), 'w') as out:
                    out.write(result)

                log.truncate(0)
                log.seek(0)
                log.write(str(index))
                log.flush()
                process_log.write("index {}, {} process done.\n".format(index, cfg))


if __name__ == '__main__':
    # convert(35, 69)
    convert_benign(True)
