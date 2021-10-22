import torch
import numpy as np


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
        neighbor_nodes = torch.cat((neighbor_nodes, torch.tensor([int(node)])))
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


def node_neighbourhood_reverse(data, node, neighborhood_size):
    if neighborhood_size == 1:
        neighbor_nodes = data.edge_index[1][
            data.edge_index[0] == torch.tensor([int(node)])]
        neighbor_nodes = torch.cat((neighbor_nodes, torch.tensor([int(node)])))
        neighbors = {'level_1': neighbor_nodes}

        # constant
        kernel = neighbors['level_1']
        ROIminusPatch = [item for item in np.arange(0, 3267) if
                         item not in kernel]
        data.x[ROIminusPatch] = torch.ones(
            data.x[ROIminusPatch].shape) * torch.tensor(
            [0.027303819, 1.4386905])

    else:
        neighbor_nodes = data.edge_index[1][
            data.edge_index[0] == torch.tensor([int(node)])]
        neighbor_nodes = torch.cat((neighbor_nodes, torch.tensor([int(node)])))
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

        # # constant
        kernel = neighbors['level_' + str(neighborhood_size)]
        ROIminusPatch = [item for item in np.arange(0, 3267) if
                         item not in kernel]
        data.x[ROIminusPatch] = torch.ones(
            data.x[ROIminusPatch].shape) * torch.tensor(
            [0.027303819, 1.4386905])
    return data, neighbors


def node_neighbourhood_curv(data, node, neighborhood_size):
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
        neighbor_nodes = torch.cat((neighbor_nodes, torch.tensor([int(node)])))
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
        curvature = torch.ones(data.x[neighbors[
            'level_' + str(neighborhood_size)]].T[0].shape) * torch.tensor(
            [0.027303819])
        myelin = data.x[neighbors[
            'level_' + str(neighborhood_size)]].T[1]
        patch = torch.cat((torch.reshape(curvature, (1, -1)),
                           torch.reshape(myelin, (1, -1))), 0).T
        data.x[neighbors['level_' + str(neighborhood_size)]] = patch
    return data, neighbors

def node_neighbourhood_myelin(data, node, neighborhood_size):
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
        neighbor_nodes = torch.cat((neighbor_nodes, torch.tensor([int(node)])))
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
        curvature = data.x[neighbors[
            'level_' + str(neighborhood_size)]].T[0]
        myelin = torch.ones(data.x[neighbors[
            'level_' + str(neighborhood_size)]].T[1].shape) * torch.tensor(
            [1.4386905])
        patch = torch.cat((torch.reshape(curvature, (1, -1)),
                           torch.reshape(myelin, (1, -1))), 0).T
        data.x[neighbors['level_' + str(neighborhood_size)]] = patch
    return data, neighbors