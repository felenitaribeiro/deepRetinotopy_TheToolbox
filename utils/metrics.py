import numpy as np


def smallest_angle(x, y):
    """Least difference between two angles.

    Args:
      x (numpy array): An array of shape (number of vertices,1) containing
        the empirical polar angles
      y (numpy array): An array of shape (number of vertices,1) containing
        the predicted polar angles

    Returns:
      numpy array: the difference between predicted and empirical polar angles
    """
    difference = []
    dif_1 = np.abs(y - x)
    dif_2 = np.abs(y - x + 2 * np.pi)
    dif_3 = np.abs(y - x - 2 * np.pi)
    for i in range(len(x)):
        difference.append(min(dif_1[i], dif_2[i], dif_3[i]))
    return np.array(difference) * 180 / np.pi


def distance_PolarCoord(radius1, radius2, theta1, theta2):
    """Difference of pRF center location in polar coordinates.

    Args:
      radius1 (numpy array): An array of shape (number of vertices,1) containing
        the empirical eccentricity values
      radius2 (numpy array): An array of shape (number of vertices,1) containing
        the predicted eccentricity values
      theta1 (numpy array): An array of shape (number of vertices,1) containing
        the empirical polar angles
      theta2 (numpy array): An array of shape (number of vertices,1) containing
        the predicted polar angles

    Returns:
      numpy array: the difference between predicted and empirical pRF center
        locations
    """
    assert theta1 >= -np.pi and theta1 <= 2 * np.pi
    assert theta2 >= -np.pi and theta2 <= 2 * np.pi
    distance = np.sqrt(
        radius1 ** 2 + radius2 ** 2 - 2 * radius1 * radius2 * np.cos(
            theta2 - theta1))
    return distance

def average_prediction(predictions_array):
    """Average the predictions across models.

    Args:
      predictions_array (numpy array): An array of shape 
      ((len(list_subs), num_of_models, num_of_cortical_nodes)) 
      containing the predictions of each model

    Returns:
      numpy array: the average prediction across models
    """
    predictions_array = predictions_array/180 * np.pi
    average_predictions = np.mean(predictions_array, axis=1)
    average_predictions = average_predictions * 180 / np.pi
    return average_predictions