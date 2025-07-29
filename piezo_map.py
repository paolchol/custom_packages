import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
# import pykrige.kriging_tools as kt
# from pykrige.ok import OrdinaryKriging
# from pykrige.uk import UniversalKriging
import rasterio as rio

def extract_and_merge(date, ts, meta, code):
    """
    
    date: str or datetime
        Date when to extract the observed values
    ts: pandas.DataFrame
        Dataframe containing all timeseries at all timesteps.
        The columns must have the same content of the meta[code] column specified
    meta: pandas.DataFrame
        Dataframe containing the code column and columns to be merged to ts
    code: str
        Label of the column on which to merge ts and meta
    
    Returns:
    df: pandas.DataFrame
        Contains the values merged with the meta dataframe based on the code column
    """
    values = ts.loc[date, :].dropna()
    values.name = 'value'
    df = pd.merge(values, meta, how = 'left', left_index = True, right_on = code)
    df.reset_index(drop=True, inplace=True)
    return(df)

class piezo_map():
    """
    Class to obtain an interpolated map starting from a list of values with coordinates
    Modules included:
        - grid_gen
        - generate
        - simple_idw
        - distance_matrix
        - kriging: to be developed
        - plot
        - export
    """
    def __init__(self, df, xmin, ymin, xmax, ymax, nx, ny,
                 rename = False, cols = None):
        """
        df: pandas.DataFrame
            DataFrame containing the values and coordinates
        xmin, ymin, xmax, ymax: int or float
            Coordinates of the boundaries of the interpolation area
        nx, ny: int
            Number of pixels to be created in the interpolation area
        rename: bool, optional
            True if the columns of df needs to be renamed. The necessary columns
            for this class to work need to be labeled as:
                x, y: the x and y coordinates
                z: the value to be interpolated
            df can contain additional columns.
            Default is False
        cols: list of str, optional
            The list of 
        """
        self.df = df.copy()
        self.coord = [(xmin, ymin), (xmax, ymax)]
        self.ncells = [nx, ny]
        self.grid = self.grid_gen()
        self.axes = self.grid_gen(axes = True)
        if rename:
            self.df.columns = cols
    
    def grid_gen(self, axes = False):
        """
        Generates the grid on which to interpolate the values
        """
        # generate two arrays of evenly space data between ends of previous arrays
        xi = np.linspace(self.coord[0][0], self.coord[1][0], self.ncells[0])
        yi = np.linspace(self.coord[0][1], self.coord[1][1], self.ncells[1])
        if axes:
            return(xi, yi)

        # generate grid 
        xi, yi = np.meshgrid(xi, yi)

        # colapse grid into 1D
        xi, yi = xi.flatten(), yi.flatten()
        return(xi, yi)

    def generate(self, how = 'IDW', power = 1,  show = True, ktype = 'ordinary', **krigargs):
        """
        Generates the interpolation and plots the result

        how: str, optional
            IDW or KRIGING. Default is IDW
        power: int, optional
            The power to be applied to the IDW weights. Default is 1
        show: bool, optional
            If True, the result obtained will be displayed. Default is True
        ktype: str, optional
            Type of the kriging to be computed. Can be 'ordinary' or 'universal'.
            Default is 'ordinary'
        krigargs: dict, optional
            Additional variables passed to piezo_map.kriging module
        """
        if how == 'IDW':
            self.simple_idw(power)
            if show:
                self.plot(im = self.idw_result, title = f"IDW - Power {power}")
        elif how == 'KRIGING':
            self.kriging(ktype, **krigargs)
            if show:
                self.plot(im = self.krig_result[0], title = f"Kriging - {ktype}")
        else:
            print("Wrong string inserted. The available options are 'IDW' and 'KRIGING'")
    
    def simple_idw(self, power = 1):
        """
        Simple inverse distance weighted (IDW) interpolation 
        Weights are proportional to the inverse of the distance, so as the distance
        increases, the weights decrease rapidly.
        The rate at which the weights decrease is dependent on the value of power.
        As power increases, the weights for distant points decrease rapidly.

        Code taken from: http://stackoverflow.com/questions/1871536
        """
        dist = self.distance_matrix()

        # In IDW, weights are 1 / distance
        weights = 1.0/(dist+1e-12)**power

        # Make weights sum to one
        weights /= weights.sum(axis=0)

        # Multiply the weights for each interpolated point by all observed Z-values
        res = np.dot(weights.T, self.df.z)
        res = res.reshape((self.ncells[1], self.ncells[0]))
        self.idw_result = res

    def distance_matrix(self):
        """
        Needed to compute simple_idw
        Make a distance matrix between pairwise observations.
        Code taken from: http://stackoverflow.com/questions/1871536
        """
        obs = np.vstack((self.df.x, self.df.y)).T
        interp = np.vstack((self.grid[0], self.grid[1])).T

        d0 = np.subtract.outer(obs[:,0], interp[:,0])
        d1 = np.subtract.outer(obs[:,1], interp[:,1])
        
        # calculate hypotenuse
        return np.hypot(d0, d1)

    def kriging(self, ktype = 'ordinary', variogram = 'linear', **krigargs):
        """
        ktype: str
            'ordinary': will perform a fixed ordinary kriging, with linear variogram, 
                        through pykrige.OrdinaryKriging.
                        For documentation: link-here
            'universal': will perform an universal kriging, with the option to specify
                        all arguments that can be provided to pykrige.UniversalKriging.
                        For documentation: link-here
        **krigargs:
            Additional arguments to be passed to pykrige.UniversalKriging.
            Link to its documentation: link-here
        """
        if ktype == 'ordinary':
            OK = OrdinaryKriging(
                self.df.x,
                self.df.y,
                self.df.z,
                variogram_model = variogram,
                verbose = False,
                enable_plotting = False,
            )
            self.krig_result = OK.execute('grid', self.axes[0], self.axes[1])
        elif ktype == 'universal':
            UK = UniversalKriging(
                self.df.x,
                self.df.y,
                self.df.z,
                # variogram_model = variogram,
                **krigargs)
            self.krig_result = UK.execute('grid', self.axes[0], self.axes[1])
        else:
            print("Wrong string inserted. The available options are 'ordinary' and 'universal'")
    
    def plot(self, im, title = None):
        """
        Plot the result of the interpolation along with
        the points used for it

        im: numpy.ndarray
            The result of simple_idw or kriging
        title: str, optional
            The title of the plot. Default is None
        """
        plt.figure(figsize=(10,7.5))
        plt.imshow(im, extent=(self.coord[0][0], self.coord[1][0], self.coord[1][1], self.coord[0][1]), cmap='rainbow', interpolation='gaussian')
        plt.scatter(self.df.x, self.df.y, c=self.df.z, cmap='rainbow', edgecolors='black')
        plt.gca().invert_yaxis()
        plt.title(title)
        plt.colorbar()
    
    def export(self, file = None, what = 'IDW', epsg = 32632, flip = False):
        """
        Exports a raster file containing the result of the interpolation

        file: str, optional
            The name of the file to be created. If None, the file name will
            be computed as {what}_result.tif. Default is None
        what: str
            Select which results to export: IDW or KRIGING
        epsg: int
            EPSG code of the coordinate reference system
        flip: bool, optional
            True: flip the y axis. Default is False
        """
        if what == 'IDW':
            exp = self.idw_result
        elif what == 'KRIGING':
            exp = self.krig_result[0]
        
        if file is None:
            file = f"{what}_result.tif"
        
        if flip:
            exp = exp.copy()
            exp = np.flipud(exp)
        #upper left pixel
        #pixel size is in meters for the default crs, implement a way to have it in degrees
        xsize = (self.coord[1][0] - self.coord[0][0])/self.ncells[0] #m
        ysize = (self.coord[1][1] - self.coord[0][1])/self.ncells[1] #m
        transform = rio.transform.from_origin(self.coord[0][0], self.coord[1][1], xsize, ysize)
        raster = rio.open(file, 'w', driver='GTiff',
                            height = exp.shape[0], width = exp.shape[1],
                            count=1, dtype=str(exp.dtype),
                            crs = rio.CRS.from_epsg(epsg),
                            transform = transform)
        raster.write(exp, 1)
        raster.close()