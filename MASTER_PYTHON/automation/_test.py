import numpy

from _localization import filter_prediction_array

a = numpy.array([0, 1, 2, 4, 0, 0,]), numpy.array([0, 1, 2, 3, 4, 5,])

print(filter_prediction_array(a, 1, 0))
