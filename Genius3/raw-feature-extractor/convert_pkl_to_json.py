# coding=utf-8
import pickle as pk
import re
import json
import os


def convert():
    # for workflow in range(0, 20):
        workflow = 0
        cfg_dir = "D:\\hkn\\infected\\datasets\\virusshare_infected{}_cfg".format(workflow)
        output_dir = "D:\\hkn\\infected\\datasets\\virusshare_infected{}_json".format(workflow)
        dot_path = "D:\\hkn\\infected\\datasets\\virusshare_infected{}_dot".format(workflow)

        for cfg in os.listdir(cfg_dir):
            name = cfg[:-4]  # 纯文件名，不带后缀
            cfg_file = open(os.path.join(cfg_dir, name + '.ida'), 'r')
            data = pk.load(cfg_file)
            cfg_file.close()

            # 打开dot文件获取fcg
            raw_function_edges = []
            with open(os.path.join(dot_path, name + '.dot'), 'r') as dot:
                for line in dot:
                    if '->' in line:
                        raw_function_edges.append(re.findall(r'\b\d+\b', line))

            # 为当前pe文件创建json对象
            json_obj = {
                'hash': data.binary_name[11:],
                'function_number': data.raw_graph_list.__len__(),
                'function_edges': [[d[0] for d in raw_function_edges], [d[1] for d in raw_function_edges]],
                'acfg_list': [],
                'function_names': []
            }
            # 读取pkl文件，一个acfg由一个函数分解而来
            for acfg in data.raw_graph_list:
                # 这里2是因为Genius框架提取特征时将后代数量放在2
                offspring = [d.get('v')[2] for d in acfg.g.node.values()]
                # 将后代数量的特征放入bb_features中
                for i, f in enumerate(acfg.bb_features):
                    f.append(offspring[i])

                acfg_item = {
                    'block_number': acfg.g.__len__(),
                    'block_edges': [[d[0] for d in acfg.g.edges], [d[1] for d in acfg.g.edges]],
                    'block_features': acfg.bb_features
                }

                json_obj['acfg_list'].append(acfg_item)
                json_obj['function_names'].append(acfg.funcname)

            # 将结果写入json本地文件
            result = json.dumps(json_obj)
            with open(os.path.join(output_dir, name + '.jsonl'), 'w') as out:
                out.write(result)


if __name__ == '__main__':
    convert()
