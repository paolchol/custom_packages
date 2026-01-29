import flopy
import numpy as np
import pandas as pd

# For MODFLOW-USG

# .hds processing

def get_hds2d(hds, nodes_ref, layer, ts, sp):
    """
    Obtain a 2d hds numpy array with the same dimensions as the MODFLOW grid,
    starting from a flopy.utils.binaryfile.HeadUFile.
    Need to provide a correspondence between nodes, row and column (nodes_ref)
    Works on a single layer, timestep and stress period

    hds1d: flopy.utils.binaryfile.HeadUFile
    nodes_ref: pandas.DataFrame
        columns needed:
            - node
            - row
            - column
    layer: int
        Layer to extract
    ts: int
        Time step to extract
    sp: int
        Stress period to extract
    """
    # hds1d = hds1d.get_data(kstpkper = (ts-1, sp-1))[layer-1]
    # hds2d = np.zeros(shape = (nodes_ref.row.max(), nodes_ref.column.max()))
    # for r in range(hds2d.shape[0]):
    #     for c in range(hds2d.shape[1]):
    #         hds2d[r,c] = hds1d[nodes_ref.loc[(nodes_ref.row == r+1) & (nodes_ref.column == c+1)].node.values[0]-1]
    
    # hds1d = hds.get_data(kstpkper = (hds.kstpkper[0][0]-1, hds.kstpkper[0][1]-1))[layer-1]
    hds1d = hds.get_data(kstpkper = (ts-1, sp-1))[layer-1]
    df = pd.DataFrame(hds1d, columns=['val'])
    df['row'] = nodes_ref.sort_values('node').row
    df['column'] = nodes_ref.sort_values('node').column
    hds2d = df.pivot_table(values='val', index='row', columns='column').values

    return hds2d

def get_hds3d(hds, nodes_ref, layer, ts, tslist = None, splist = None):
    """
    Works with a single layer, for a single time step
    """
    hdsusg = hds.get_alldata()
    shape = (hdsusg.shape[0], nodes_ref.row.max(), nodes_ref.column.max())
    hds3d = np.ndarray(shape=shape)

    for t in range(hdsusg.shape[0]):
        hds3d[t,:,:] = get_hds2d(hds, nodes_ref, layer, ts, t+1)
    
    return hds3d

def get_hds4d(hds, nodes_ref, layers, ts):
    hdsusg = hds.get_alldata()
    shape = (hdsusg.shape[0], len(layers), nodes_ref.row.max(), nodes_ref.column.max())
    hds4d = np.ndarray(shape=shape)
    for l in layers:
        hds4d[:,l-1,:,:] = get_hds3d(hds, nodes_ref, l, ts)
    return hds4d

# .cbb processing

def get_cbb2d(cbb, nodes_ref, layer, ts, sp, text):
    """
    
    """

    cbb1d = cbb.get_data(kstpkper=(ts, sp), text = text)
    cbb1d_layer = cbb1d[0][0,0, nodes_ref.node.max()*(layer-1):nodes_ref.node.max()*layer]
    df = pd.DataFrame(cbb1d_layer, columns=['val'])
    df['row'] = nodes_ref.sort_values('node').row
    df['column'] = nodes_ref.sort_values('node').column
    cbb2d = df.pivot_table(values='val', index='row', columns='column').values
    
    return cbb2d

def get_cbb3d(cbb, nodes_ref, text, layer = None, n_layers = None):
    """
    layer: int, optional
        If None, takes all layers. Default is None
    """
    if layer is None and n_layers is None:
        print("Error: specify layer or provide the number of layers (n_layers)")
        return

    kstpkper = cbb.get_kstpkper()
    if layer is not None:
        shape = (len(kstpkper), nodes_ref.row.max(), nodes_ref.column.max())
    else:
        shape = (len(kstpkper), n_layers, nodes_ref.row.max(), nodes_ref.column.max())

    hds3d = np.ndarray(shape = shape)
    
    if layer is not None:
        for t, tssp in enumerate(kstpkper):
            hds3d[t,:,:] = get_cbb2d(cbb, nodes_ref, layer-1, tssp[0], tssp[1], text)
    else:
        for l in range(1, n_layers+1):
            for t, tssp in enumerate(kstpkper):
                hds3d[t,l-1,:,:] = get_cbb2d(cbb, nodes_ref, l, tssp[0], tssp[1], text)
    
    return hds3d

# Difference in volumes in the next two years

def comp_diff_cbb_volumes(cbb0, cbb1, s, e, l = None):
    """
    Computes the differences between two cell budget arrays

    
    """
    if l is None:
        diff = cbb1[s:e, :, :, :]-cbb0[s:e, :, :, :]
    else:
        diff = cbb1[s:e, l, :, :]-cbb0[s:e, l, :, :]
    print('Total difference [m3]:', (diff*30*24*60*60).sum(axis=0).sum())
    return diff