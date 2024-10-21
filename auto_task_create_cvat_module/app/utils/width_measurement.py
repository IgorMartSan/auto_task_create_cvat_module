import os
from typing import Tuple
from typing import List
from typing import Dict
import numpy as np 
import cv2 
from scipy import stats
from multiprocessing import Pool


def calc_width_coil(
    binary_img: np.ndarray, sampling_interval: int, meas_distance: int
) -> Tuple[np.ndarray, List[Tuple[int, float]]]:
    """
    Calculate the width of an object in a binary image over a
    coil and, optionally, draw lines at intervals on the
    original BGR image.

    Parameters:
    binary_img (np.ndarray): The binary image to analyze.
    sampling_interval (int): The interval for sampling
    measurements.
    distance_between_measurements (int): The distance between
    each measurement.
    draw (bool): Whether to draw the measurements on the BGR
    image.

    Returns:
    Tuple[np.ndarray, List[Tuple[int, float]]]: The original BGR image with or
    without drawings, and a list of tuples containing the interval and
    measured distance.
    """

    height, _ = binary_img.shape
    step = sampling_interval + meas_distance

    intervals = np.arange(0, height, step)
    measurements = []

    for _, interval in enumerate(intervals):
        if interval + sampling_interval < height:
            # Measure the distance at the given interval
            info = _measure_distance_at_interval(
                binary_img, interval, interval + sampling_interval
            )
            measurements.append((interval, info))

    measurements = tuple(measurements)
    return measurements


def _worker_function(args: Tuple[np.ndarray, int, int]) -> Tuple[int, float]:
    """
    Process a single interval to measure distance.

    Args:
        args (Tuple[np.ndarray, int, int]): A tuple containing the binary image,
                                            interval start, and sampling interval.

    Returns:
        Tuple[int, float]: The interval and the measured distance information.
    """
    binary_img, interval, sampling_interval = args
    info = _measure_distance_at_interval(
        binary_img, interval, interval + sampling_interval
    )
    return (interval, info)


# Helper functions for checking if the border is straight and calculating simple midpoint
def _is_straight_border(points):
    return all(x == points[0][0] for x, _ in points) if points else False


def _calculate_simple_midpoint(points):
    avg_y = int(sum(y for _, y in points) / len(points))
    return (points[0][0], avg_y)


def _measure_distance_at_interval(
    img: np.ndarray, start: int, end: int
) -> Dict[str, Tuple[int, int]]:
    """
    Measure the distance at a given interval in a binary image.

    Parameters:
    - img (np.ndarray): The binary image.
    - start (int): The start of the interval.
    - end (int): The end of the interval.

    Returns:
    - Dict[str, Tuple[int, int]]: A dictionary containing the coordinates of
      right and left edges, their midpoints, and the calculated distance.
    """

    right_edge_points = _collect_edge_points(img, start, end, direction="right")
    left_edge_points = _collect_edge_points(img, start, end, direction="left")

    mid_point_right = _select_midpoint(right_edge_points)
    mid_point_left = _select_midpoint(left_edge_points)

    distance = mid_point_right[0] - mid_point_left[0]

    right_edge_start = right_edge_points[0] if right_edge_points else (0, 0)
    right_edge_end = right_edge_points[-1] if right_edge_points else (0, 0)
    left_edge_start = left_edge_points[0] if left_edge_points else (0, 0)
    left_edge_end = left_edge_points[-1] if left_edge_points else (0, 0)


    # Calculate the center point
    center_point_x = (mid_point_right[0] + mid_point_left[0]) // 2
    center_point_y = (mid_point_right[1] + mid_point_left[1]) // 2
    center_point = (center_point_x, center_point_y)

    # Return statement including the new center point
    return {
        "right_edge_start": right_edge_start,
        "right_edge_end": right_edge_end,
        "left_edge_start": left_edge_start,
        "left_edge_end": left_edge_end,
        "mid_point_right": mid_point_right,
        "mid_point_left": mid_point_left,
        "distance": distance,
        "center_point": center_point
    }


def _select_midpoint(edge_points: list) -> Tuple[int, int]:
    """
    Select the appropriate midpoint calculation method.

    Parameters:
    - edge_points (list): List of edge points.

    Returns:
    - Tuple[int, int]: The calculated midpoint.
    """
    if _is_straight_border(edge_points):
        return _calculate_simple_midpoint(edge_points)
    else:
        return _calculate_regression_midpoint(edge_points)


def _collect_edge_points(
    img: np.ndarray, start: int, end: int, direction: str
) -> List[Tuple[int, int]]:
    """
    Collect points along an edge within a specified interval.

    Parameters:
    img (np.ndarray): The binary image.
    start (int): The start of the interval.
    end (int): The end of the interval.
    direction (str): The direction to search ('left' or 'right').

    Returns:
    List[Tuple[int, int]]: A list of points along the edge.
    """
    points = []
    for y in range(start, end):
        x = _find_horizontal_distance(img, y, direction)
        if x != -1:
            points.append((x, y))
    return points


def _find_horizontal_distance(img: np.ndarray, y: int, direction: str) -> int:
    """
    Find the horizontal distance of a point in the image.

    Parameters:
    img (np.ndarray): The binary image.
    y (int): The y-coordinate of the point.
    direction (str): The direction to search ('left' or 'right').

    Returns:
    int: The x-coordinate of the point.
    """
    y = int(y)

    # Check if the image is actually grayscale
    if len(img.shape) != 2:
        raise ValueError(f"Image is not grayscale. It has shape: {img.shape}.")

    width = img.shape[1]

    if direction == "right":
        for i in reversed(range(width)):
            if img[y, i] == 255:
                return i
    elif direction == "left":
        for i in range(width):
            if img[y, i] == 255:
                return i

    return -1




def calculate_simple_midpoint(points: List[Tuple[int, int]]) -> Tuple[int, int]:
    """
    Calculate the midpoint's x-coordinate and the average y-coordinate of points.

    Args:
    points (List[Tuple[int, int]]): A list of (x, y) coordinate tuples.

    Returns:
    Tuple[int, int]: A tuple representing the midpoint (x, avg_y).
    """
    avg_y = sum(y for _, y in points) // len(points)
    return (points[0][0], avg_y)


def _calculate_middle_point(
    p1: Tuple[int, int], p2: Tuple[int, int]
) -> Tuple[int, int]:
    """
    Calculate the middle point between two points.

    Parameters:
    p1, p2 (Tuple[int, int]): The points to find the middle of.

    Returns:
    Tuple[int, int]: The middle point.
    """
    return (int((p1[0] + p2[0]) / 2), int((p1[1] + p2[1]) / 2))


def _calculate_regression_midpoint(
    points: List[Tuple[int, int]]
) -> Tuple[float, float]:
    """
    Calculate the midpoint using linear regression on a set of points.

    Parameters:
    points (List[Tuple[int, int]]): The list of points to fit the line.

    Returns:
    Tuple[float, float]: The midpoint calculated from the regression line.
    """
    if len(points) < 2:
        raise ValueError(f"Need at least two points for regression, points: {points}")
    
    x = [p[0] for p in points]
    y = [p[1] for p in points]

    slope, intercept, _, _, _ = stats.linregress(x, y)

    mean_x = np.mean(x)
    mean_y = slope * mean_x + intercept

    return (mean_x, mean_y)