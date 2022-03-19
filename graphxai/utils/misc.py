import torch
from torch import Tensor
from torch.nn import PairwiseDistance as pdist


def make_node_ref(nodes: torch.Tensor):
    '''
    Makes a node reference to unite node indicies across explanations. 
        Returns a dictionary keyed on node indices in tensor provided.
    Args:
        nodes (torch.tensor): Tensor of nodes to reference.
    
    :rtype: :obj:`Dict`
    '''
    node_reference = {nodes[i].item():i for i in range(nodes.shape[0])}
    return node_reference

def node_mask_from_edge_mask(node_subset: torch.Tensor, edge_index: torch.Tensor, edge_mask: torch.Tensor = None):
    '''
    Gets node mask from an edge_mask:

    Args:
        node_subset
        edge_mask (torch.Tensor): Boolean mask over all edges in edge_index. Shape: (edge_index.shape[1],).
    '''
    if edge_mask is not None:
        mask_eidx = edge_index[:,edge_mask]
    else:
        mask_eidx = edge_index

    unique_nodes = torch.unique(mask_eidx)

    node_mask = torch.tensor([node_subset[i] in unique_nodes for i in range(node_subset.shape[0])])
    
    return node_mask.float()

def edge_mask_from_node_mask(node_mask: torch.Tensor, edge_index: torch.Tensor):
    '''
    Convert edge_mask to node_mask

    Args:
        node_mask (torch.Tensor): Boolean mask over all nodes included in edge_index. Indices must 
            match to those in edge index. This is straightforward for graph-level prediction, but 
            converting over subgraphs must be done carefully to match indices in both edge_index and
            the node_mask.
    '''

    node_numbers = node_mask.nonzero(as_tuple=True)[0]

    iter_mask = torch.zeros((edge_index.shape[1],))

    # See if edges have both ends in the node mask
    for i in range(edge_index.shape[1]):
        iter_mask[i] = (edge_index[0,i] in node_numbers) and (edge_index[1,i] in node_numbers) 
    
    return iter_mask


def top_k_mask(to_mask: torch.Tensor, top_k: int):
    '''
    Perform a top-k mask on to_mask tensor.

    ..note:: Deals with identical values in the same way as
        torch.sort.

    Args:
        to_mask (torch.Tensor): Tensor to mask.
        top_k (int): How many features in Tensor to select.

    :rtype: :obj:`torch.Tensor`
    Returns:
        torch.Tensor: Masked version of to_mask
    '''
    inds = torch.argsort(to_mask)[-int(top_k):]
    mask = torch.zeros_like(to_mask)
    mask[inds] = 1
    return mask.long()

def threshold_mask(to_mask: torch.Tensor, threshold: float):
    '''
    Perform a threshold mask on to_mask tensor.

    Args:
        to_mask (torch.Tensor): Tensor to mask.
        threshold (float): Select all values greater than this threshold.

    :rtype: :obj:`torch.Tensor`
    Returns:
        torch.Tensor: Masked version of to_mask.
    '''
    return (to_mask > threshold).long()


def distance(emb_1: torch.tensor, emb_2: torch.tensor, p=2) -> float:
    '''
    Calculates the distance between embeddings generated by a GNN model
    Args:
        emb_1 (torch.tensor): embeddings for the clean graph
        emb_2 (torch.tensor): embeddings for the perturbed graph
    '''
    if p == 0:
        return torch.dist(emb_1, emb_2, p=0).item()
    elif p == 1:
        return torch.dist(emb_1, emb_2, p=1).item()
    elif p == 2:
        return torch.dist(emb_1, emb_2, p=2).item()
    else:
        print('Invalid choice! Exiting..')

def match_edge_presence(edge_index, node_idx):
    '''
    Returns edge mask with the spots containing node_idx highlighted
    '''

    emask = torch.zeros(edge_index.shape[1]).bool()

    if isinstance(node_idx, torch.Tensor):
        if node_idx.shape[0] > 1:
            for ni in node_idx:
                emask = emask | ((edge_index[0,:] == ni) | (edge_index[1,:] == ni))
        else:
            emask = ((edge_index[0,:] == node_idx) | (edge_index[1,:] == node_idx))
    else:
        emask = ((edge_index[0,:] == node_idx) | (edge_index[1,:] == node_idx))

    return emask

# def make_edge_ref():
#     pass