class HierarchicalGraphNeuralNetwork(nn.Module):
    def __init__(self, external_vocab: Vocab):
        super(HierarchicalGraphNeuralNetwork, self).__init__()
        self.pool = 'global_max_pool'
        # Hierarchical 1: Control Flow Graph (CFG) embedding and pooling
        cfg_filter_list =[200, 200]
        cfg_filter_list.insert(0, 11)
        self.cfg_filter_length = len(cfg_filter_list)
        cfg_graphsage_params = [dict(in_channels=cfg_filter_list[i], out_channels=cfg_filter_list[i + 1], bias=True) for
                                i in range(self.cfg_filter_length - 1)]
        cfg_conv = dict(constructor=torch_geometric.nn.conv.SAGEConv, kwargs=cfg_graphsage_params)
        cfg_constructor = cfg_conv['constructor']
        for i in range(self.cfg_filter_length - 1):
            setattr(self, 'CFG_gnn_{}'.format(i + 1), cfg_constructor(**cfg_conv['kwargs'][i]))
        self.dropout = nn.Dropout(p=0.2)
        # Hierarchical 2: Function Call Graph (FCG) embedding and pooling
        self.external_embedding_layer = nn.Embedding(num_embeddings=external_vocab.max_vocab_size + 2,
                                                     embedding_dim=cfg_filter_list[-1],
                                                     padding_idx=external_vocab.pad_idx)
        fcg_filter_list = [200, 200]
        fcg_filter_list.insert(0, cfg_filter_list[-1])
        self.fcg_filter_length = len(fcg_filter_list)
        fcg_graphsage_params = [dict(in_channels=fcg_filter_list[i], out_channels=fcg_filter_list[i + 1], bias=True) for
                                i in range(self.fcg_filter_length - 1)]
        fcg_conv = dict(constructor=torch_geometric.nn.conv.SAGEConv, kwargs=fcg_graphsage_params)
        fcg_constructor = fcg_conv['constructor']
        for i in range(self.fcg_filter_length - 1):
            setattr(self, 'FCG_gnn_{}'.format(i + 1), fcg_constructor(**fcg_conv['kwargs'][i]))
        # Last Projection Function: gradually project with more linear layers
        self.pj1 = torch.nn.Linear(in_features=fcg_filter_list[-1], out_features=int(fcg_filter_list[-1] / 2))
        self.pj2 = torch.nn.Linear(in_features=int(fcg_filter_list[-1] / 2), out_features=int(fcg_filter_list[-1] / 4))
        self.pj3 = torch.nn.Linear(in_features=int(fcg_filter_list[-1] / 4), out_features=6)
        self.last_activation = nn.Softmax(dim=1)

    def forward(self, real_local_batch: Batch, real_bt_positions: list, bt_external_names: list,
                bt_all_function_edges: list):
        rtn_local_batch = self.forward_cfg_gnn(local_batch=real_local_batch)
        x_cfg_pool = torch_geometric.nn.glob.global_max_pool(x=rtn_local_batch.x, batch=rtn_local_batch.batch)
        fcg_list = []
        fcg_internal_list = []
        for idx_batch in range(len(real_bt_positions) - 1):
            start_pos, end_pos = real_bt_positions[idx_batch: idx_batch + 2]
            idx_x_cfg = x_cfg_pool[start_pos: end_pos]
            fcg_internal_list.append(idx_x_cfg)
            idx_x_external = self.external_embedding_layer(
                torch.tensor([bt_external_names[idx_batch]], dtype=torch.long))
            idx_x_external = idx_x_external.squeeze(dim=0)
            idx_x_total = torch.cat([idx_x_cfg, idx_x_external], dim=0)
            idx_function_edge = torch.tensor(bt_all_function_edges[idx_batch], dtype=torch.long)
            idx_graph_data = Data(x=idx_x_total, edge_index=idx_function_edge)
            idx_graph_data.validate()
            fcg_list.append(idx_graph_data)
        fcg_batch = Batch.from_data_list(fcg_list)
        # Hierarchical 2: Function Call Graph (FCG) embedding and pooling
        rtn_fcg_batch = self.forward_fcg_gnn(function_batch=fcg_batch)  # [batch_size, max_node_size, dim]
        x_fcg_pool = torch_geometric.nn.glob.global_max_pool(x=rtn_fcg_batch.x, batch=rtn_fcg_batch.batch)
        batch_final = x_fcg_pool
        # step last project to the number_of_classes (multiclass)
        bt_final_embed = self.pj3(self.pj2(self.pj1(batch_final)))
        bt_pred = self.last_activation(bt_final_embed)
        return bt_pred

    def forward_cfg_gnn(self, local_batch: Batch):
        in_x, edge_index = local_batch.x, local_batch.edge_index
        for i in range(self.cfg_filter_length - 1):
            out_x = getattr(self, 'CFG_gnn_{}'.format(i + 1))(x=in_x, edge_index=edge_index)
            out_x = torch.nn.functional.relu(out_x, inplace=True)
            out_x = self.dropout(out_x)
            in_x = out_x
        local_batch.x = in_x
        return local_batch

    def forward_fcg_gnn(self, function_batch: Batch):
        in_x, edge_index = function_batch.x, function_batch.edge_index
        for i in range(self.fcg_filter_length - 1):
            out_x = getattr(self, 'FCG_gnn_{}'.format(i + 1))(x=in_x, edge_index=edge_index)
            out_x = torch.nn.functional.relu(out_x, inplace=True)
            out_x = self.dropout(out_x)
            in_x = out_x
        function_batch.x = in_x
        return function_batch