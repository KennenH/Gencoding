
import pickle
testpath = "C:\Program1\pycharmproject\Genius3/acfgs/hpcenter.ida"
fr = open(testpath, 'r')
data1 = pickle.load(fr)
print(type(data1))
# # print_obj(data1)
# print cfgs.raw_graph_list[0]