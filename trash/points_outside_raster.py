"""
codice di prova per ottenere i punti più vicini al raster

solo iniziato, serve andare avanti
creata funzione find_nearestrastercell in geodata.py
"""

#Obtain the closest raster value for osservation points which don't fall
#inside the raster
base.bounds
base.nodata
msk = np.reshape(base.read_masks(), (base.read_masks().shape[0]*base.read_masks().shape[1], base.read_masks().shape[2]))
plt.imshow(msk)

file_name = 'data/soggiacenza_base_ISS/soggiacenza.tif'
with rasterio.open(file_name) as src:
     band1 = src.read(1)
     print('Band1 has shape', band1.shape)
     height = band1.shape[0]
     width = band1.shape[1]
     cols, rows = np.meshgrid(np.arange(width), np.arange(height))
     xs, ys = rasterio.transform.xy(src.transform, rows, cols)
     lons= np.array(xs)
     lats = np.array(ys)
     print('lons shape', lons.shape)

#obtain the closest point from the raster to the one in gdf
#obtain the raster value of the non-na closest point
#assign it to the point in the gdf