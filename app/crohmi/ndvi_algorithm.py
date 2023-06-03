import io
import numpy as np
import calendar
from matplotlib import pyplot as plt

from django.core.files.images import ImageFile


def ndvi_array_calc(file):
    """Calculate ndvi array"""
    ms_camera_imagery = plt.imread(file.path)
    np.seterr(divide='ignore', invalid='ignore')
    ndvi = (1.236 * ms_camera_imagery[:, :, 2] - 0.188 * ms_camera_imagery[:,
                                                         :, 0]) / (
                       1.236 * ms_camera_imagery[:, :,
                               2] + 0.188 * ms_camera_imagery[:, :, 0])
    return ndvi


def ndvi_image(file, array, month, year):
    """Convert np array to ndvi image"""
    nri_image = io.BytesIO()

    plt.figure(figsize=(4, 6))
    plt.title('NRI Map')
    plt.suptitle(f'{calendar.month_name[month]} {year}')
    plt.imshow(plt.imread(file.path))
    plt.savefig(nri_image, format="png")
    file.save(f'{file.name.split(".")[0]}.png', ImageFile(nri_image))

    plt.figure(figsize=(4, 6))
    plt.title('NDVI Map')
    plt.suptitle(f'{calendar.month_name[month]} {year}')
    plt.imshow(array, cmap=plt.cm.RdYlGn)
    plt.colorbar()
    plt.clim(-0.3, 1)
    figure = io.BytesIO()
    plt.savefig(figure, format="png")
    return figure


def health_image(array, month, year):
    """Convert np array to health image"""
    if month == 1:
        array[np.logical_and(array is not None, array > 0.6)] = 3
        array[np.logical_and(array is not None,
                             np.logical_and(0.5 < array, array < 0.6))] = 2
        array[np.logical_and(array < 0.5, array is not None)] = 1
    elif month == 11:
        array[np.logical_and(array is not None, array > 0.5)] = 3
        array[np.logical_and(array is not None,
                             np.logical_and(0.35 < array, array < 0.5))] = 2
        array[np.logical_and(array is not None, array < 0.35)] = 1
    elif month == 12:
        array[np.logical_and(array is not None, array > 0.58)] = 3
        array[np.logical_and(array is not None,
                             np.logical_and(0.4 < array, array < 0.58))] = 2
        array[np.logical_and(array is not None, array < 0.4)] = 1

    plt.figure(figsize=(4, 6))
    plt.title('Health Map')
    plt.suptitle(f'{calendar.month_name[month]} {year}')
    plt.imshow(array, cmap=plt.cm.Blues)
    plt.colorbar()
    figure = io.BytesIO()
    plt.savefig(figure, format="png")
    return figure
