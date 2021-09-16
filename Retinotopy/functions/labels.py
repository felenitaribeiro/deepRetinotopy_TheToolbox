import numpy as np


def labels(input, labels):
    """Function for the selection of triangular faces from the region of
    interest.

    Args:
        input (.mat file): .mat file with the triangular faces composing the
            surface template
        labels (numpy array): vertices index from the region of interest

    Returns:
        numpy array: triangular faces from the region of interest (number of
            faces, 3)
    """

    # Append to faces_indexes from those faces containing nodes from the
    # visual cortex
    faces_indexes = np.array([])
    for j in range(len(labels)):
        faces_indexes = np.concatenate(
            (faces_indexes, np.where(input == labels[j])[0]), axis=0)

    # Select indexed faces (faces_indexes)
    faces = []
    for i in range(len(faces_indexes)):
        faces.append(input[int(faces_indexes[i])])

    # Change the nodes numbers (indexes) from the visual system to range
    # from 0:len(index_mask)
    faces = np.array(faces)
    for i in range(len(labels)):
        index = np.array(labels)
        index.sort
        faces[np.where(faces == index[i])] = i

    # Select only faces composed of vertices that are within the ROI
    final_faces = []
    for i in range(len(faces)):
        if np.sum(faces <= len(labels) - 1, axis=1)[i] == 3:
            final_faces.append(faces[i])

    return np.reshape(final_faces, (len(final_faces), 3))
