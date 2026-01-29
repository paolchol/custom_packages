import flopy
import numpy as np
import pandas as pd

# General

def assign_date_to_sp(nsp, start, freq, add_my = False, base = 0):
    sps = {
    'sp': [i for i in range(base, nsp+base)],
    'sp_start': pd.date_range(start = start, periods = nsp, freq = freq)
    }
    sps = pd.DataFrame(sps)
    if add_my:
        sps['month'] = [d.month for d in sps.month_start]
        sps['year'] = [d.year for d in sps.month_start]
    return sps

# For MODFLOW-USG

## .hds processing

def get_hds2d(hds, nodes_ref, layer, ts, sp):
    """
    Obtain a 2d hds numpy array with the same dimensions as the MODFLOW grid,
    starting from a flopy.utils.binaryfile.HeadUFile.
    Need to provide a correspondence between nodes, row and column (nodes_ref)
    Works on a single layer, timestep and stress period
    Tested with MODFLOW-USG configuration

    hds1d: flopy.utils.binaryfile.HeadUFile
        HeadUFile object
    nodes_ref: pandas.DataFrame
        columns needed:
            - node
            - row
            - column
    layer: int
        Layer to extract. Based 0
    ts: int
        Time step to extract. Based 0
    sp: int
        Stress period to extract. Based 0
    """
    hds1d = hds.get_data(kstpkper = (ts, sp))[layer]
    df = pd.DataFrame(hds1d, columns=['val'])
    df['row'] = nodes_ref.sort_values('node').row
    df['column'] = nodes_ref.sort_values('node').column
    hds2d = df.pivot_table(values='val', index='row', columns='column').values
    return hds2d

def get_hds3d(hds, nodes_ref, layer = None, n_layers = None):
    """
    hds: flopy.HeadUFile
        HeadUFile object. Tested with MODFLOW-USG configuration
    nodes_ref: pandas.DataFrame
        Contains the correspondance between node and row/column
        columns needed:
            - node
            - row
            - column
    layer: int, optional
        Layer to extract. Based 0. If None, takes all layers. Default is None
    n_layers: int, optional
        If layer is None, provide the number of layers contained in the file
    """
    if layer is None and n_layers is None:
        print("Error: specify layer or provide the number of layers (n_layers)")
        return

    kstpkper = hds.get_kstpkper()
    if layer is not None:
        shape = (len(kstpkper), nodes_ref.row.max(), nodes_ref.column.max())
    else:
        shape = (len(kstpkper), n_layers, nodes_ref.row.max(), nodes_ref.column.max())

    hds3d = np.ndarray(shape = shape)
    
    if layer is not None:
        for t, tssp in enumerate(kstpkper):
            hds3d[t,:,:] = get_hds2d(hds, nodes_ref, layer, tssp[0], tssp[1])
    else:
        for l in range(0, n_layers):
            for t, tssp in enumerate(kstpkper):
                hds3d[t,l,:,:] = get_hds2d(hds, nodes_ref, l, tssp[0], tssp[1])
    return hds3d

## .cbb processing

def get_cbb2d(cbb, nodes_ref, layer, ts, sp, text):
    """
    Tested with MODFLOW-USG configuration
    This may not work if nested cells are present

    cbb: flopy.CellBudgetFile
        CellBudgetFile object
    nodes_ref: pandas.DataFrame
        Contains the correspondance between node and row/column
    layer: int
        Layer to extract. Based 0 (e.g. the first layer has to be requested with 0)
    ts: int
        Time step to extract. Based 0
    sp: int
        Stress period to extract. Based 0
    text: str
        Text associated with the flux to extract.
        You can obtain the available labels by calling cbb.headers.text.unique()
    """
    cbb1d = cbb.get_data(kstpkper=(ts, sp), text = text)
    cbb1d_layer = cbb1d[0][0,0, nodes_ref.node.max()*(layer):nodes_ref.node.max()*(layer+1)]
    df = pd.DataFrame(cbb1d_layer, columns=['val'])
    df['row'] = nodes_ref.sort_values('node').row
    df['column'] = nodes_ref.sort_values('node').column
    cbb2d = df.pivot_table(values='val', index='row', columns='column').values
    
    return cbb2d

def get_cbb3d(cbb, nodes_ref, text, layer = None, n_layers = None):
    """
    Tested with MODFLOW-USG configuration
    This may not work if nested cells are present

    cbb: flopy.CellBudgetFile
        CellBudgetFile object. Tested with MODFLOW-USG configuration
    nodes_ref: pandas.DataFrame
        Contains the correspondance between node and row/column
    text: str
        Text associated with the flux to extract.
        You can obtain the available labels by calling cbb.headers.text.unique()
    layer: int, optional
        Layer to extract. Based 0. If None, takes all layers. Default is None
    n_layers: int, optional
        If layer is None, provide the number of layers contained in the file
    """
    if layer is None and n_layers is None:
        print("Error: specify layer or provide the number of layers (n_layers)")
        return

    kstpkper = cbb.get_kstpkper()
    if layer is not None:
        shape = (len(kstpkper), nodes_ref.row.max(), nodes_ref.column.max())
    else:
        shape = (len(kstpkper), n_layers, nodes_ref.row.max(), nodes_ref.column.max())

    cbb3d = np.ndarray(shape = shape)
    
    if layer is not None:
        for t, tssp in enumerate(kstpkper):
            cbb3d[t,:,:] = get_cbb2d(cbb, nodes_ref, layer, tssp[0], tssp[1], text)
    else:
        for l in range(0, n_layers):
            for t, tssp in enumerate(kstpkper):
                cbb3d[t,l,:,:] = get_cbb2d(cbb, nodes_ref, l, tssp[0], tssp[1], text)
    
    return cbb3d

def comp_diff_cbb_volumes(cbb0, cbb1, s, e, l = None, splen = 30):
    """
    Computes the differences between two cell budget arrays
    """
    if l is None:
        diff = cbb1[s:e, :, :, :]-cbb0[s:e, :, :, :]
    else:
        diff = cbb1[s:e, l, :, :]-cbb0[s:e, l, :, :]
    print('Total difference [m3]:', (diff*splen*24*60*60).sum(axis=0).sum())
    return diff