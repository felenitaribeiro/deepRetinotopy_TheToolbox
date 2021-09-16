import torch



def node_neighbourhood(data, node, neighborhood_size):
    if neighborhood_size == 1:
        neighbor_nodes = data.edge_index[1][
            data.edge_index[0] == torch.tensor([int(node)])]
        neighbor_nodes = torch.cat((neighbor_nodes, torch.tensor([int(node)])))
        neighbors = {'level_1': neighbor_nodes}

        # # zero out
        # data.x[neighbors['level_1']] = torch.zeros(
        #     data.x[neighbors['level_1']].shape)

        # constant
        data.x[neighbors['level_1']] = torch.ones(
            data.x[neighbors['level_1']].shape) * torch.tensor(
            [0.027303819, 1.4386905])

    else:
        neighbor_nodes = data.edge_index[1][
            data.edge_index[0] == torch.tensor([int(node)])]
        neighbor_nodes = torch.cat((neighbor_nodes,  torch.tensor([int(node)])))
        neighbors = {'level_' + str(1): neighbor_nodes}

        for l in range(neighborhood_size - 1):
            all_neighbors = torch.tensor([], dtype=torch.long)
            for n in range(len(neighbors[
                                   'level_' + str(l + 1)])):
                all_neighbors = torch.cat(
                    (all_neighbors, data.edge_index[1][
                        data.edge_index[0] == neighbors[
                            'level_' + str(l + 1)][n]]))

            neighbors['level_' + str(l + 2)] = torch.unique(torch.cat(
                (neighbors['level_' + str(l + 1)], all_neighbors)))

        # # zero out
        # data.x[neighbors['level_' + str(neighborhood_size)]] = torch.zeros(
        #     data.x[neighbors['level_' + str(neighborhood_size)]].shape)

        # # constant
        data.x[neighbors['level_' + str(neighborhood_size)]] = torch.ones(
            data.x[neighbors[
                'level_' + str(neighborhood_size)]].shape) * torch.tensor(
            [0.027303819, 1.4386905])
    return data, neighbors

