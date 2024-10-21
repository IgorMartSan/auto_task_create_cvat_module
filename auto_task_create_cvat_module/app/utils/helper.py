import os
from typing import Tuple
import numpy as np
import cv2

def parse_tuple(env_var: str, default: Tuple[int, int] = (0, 0)) -> Tuple[int, int]:
    """
    Parse a string representing a tuple into an actual tuple of integers.

    Args:
    env_var (str): A string representation of the tuple.
    default (Tuple[int, int], optional): The default tuple to return in case of
    parsing errors. Defaults to (0, 0).

    Returns:
    Tuple[int, int]: The parsed tuple or the default value in case of an error.
    """
    try:
        stripped = env_var.strip("()")
        splitted = stripped.split(",")
        return tuple(map(int, splitted))
    except ValueError:
        return default


def display_img(img):
    "Resize and Display image using cv2.imshow function."

    resized_img = cv2.resize(img, (int(img.shape[1] * 0.30), int(img.shape[0] * 0.30)))

    cv2.imshow("Image", resized_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def overlay_contours_on_original(original_image, processed_image):
    """
    Overlay the contours found in the processed image onto the original image.

    Args:
    original_image (numpy.ndarray): The original image.
    processed_image (numpy.ndarray): The processed image after applying
    thresholding and morphological operations.

    Returns:
    numpy.ndarray: The original image with contours overlaid.
    """
    # Find contours in the processed image
    contours, _ = cv2.findContours(
        processed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    # Draw contours on the original image
    contour_overlay = original_image.copy()

    # Convert image to BGR format
    contour_overlay = cv2.cvtColor(contour_overlay, cv2.COLOR_GRAY2BGR)

    # Draw contours on the original image
    cv2.drawContours(contour_overlay, contours, -1, (0, 255, 0), 2)  # Green contours

    return contour_overlay


def show(image) -> None:
    """
    Displays the concatenated image in a window in real-time.

    Args:
    - image (np.ndarray): The image to be displayed.
    """
    # Resize the image to a smaller size for display purposes
    scale_factor = 0.1  # Adjust this factor as needed
    new_width = int(image.shape[1] * scale_factor)
    new_height = int(image.shape[0] * scale_factor)
    resized_image = cv2.resize(image, (new_width, new_height))

    # Display the image
    cv2.imshow("Concatenated Image", resized_image)

    # Wait for a short period and refresh the image display
    # cv2.waitKey(1) is essential for the window to update in real-time
    if cv2.waitKey(1) & 0xFF == ord("q"):
        # Press 'q' to quit the display window
        cv2.destroyAllWindows()
        return


def draw_measurement_lines(img_bgr: np.ndarray, info: dict, conversion_ratio: float) -> None:
    """
    Draw measurement lines on the image.

    Parameters:
    img_bgr (np.ndarray): The image to draw on.
    info (dict): Dictionary containing endpoints and midpoints of lines,
                 and the measured distance.

    Returns:
    None
    """
    # Constants for colors
    RED = (0, 0, 255)
    GREEN = (0, 255, 0)

    # Extracting points and distance from the info dictionary
    pt1 = info["right_edge_start"]
    pt2 = info["right_edge_end"]
    pt3 = info["left_edge_start"]
    pt4 = info["left_edge_end"]
    pt5 = info["mid_point_right"]
    pt6 = info["mid_point_left"]
    distance = info["distance"]

    # Convert float coordinates to integers
    pt5_int = (int(pt5[0]), int(pt5[1]))
    pt6_int = (int(pt6[0]), int(pt6[1]))

    _draw_line(img_bgr, pt1, pt2, color=RED)
    _draw_line(img_bgr, pt3, pt4, color=RED)
    _draw_line(img_bgr, pt5_int, pt6_int, color=GREEN)

    print(f"Distance: {distance:.0f} pixels")
    print(f"Distance: {distance * conversion_ratio:.0f} mm")

    cv2.putText(
        img_bgr,
        f"{distance * conversion_ratio:.0f} mm",
        (pt6_int[0] + 100, pt6_int[1]),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        GREEN,
        2,
    )

    return img_bgr


def _draw_line(
    img: np.ndarray,
    pt1: Tuple[int, int],
    pt2: Tuple[int, int],
    color: Tuple[int, int, int] = (128, 0, 200),
    thickness: int = 2,
) -> None:
    """
    Draw a line on the image.

    Parameters:
    img (np.ndarray): The image to draw on.
    pt1, pt2 (Tuple[int, int]): The start and end points of the line.
    color (Tuple[int, int, int]): The color of the line.
    thickness (int): The thickness of the line.

    Returns:
    None
    """
    cv2.line(
        img,
        pt1=(int(pt1[0]), int(pt1[1])),
        pt2=(int(pt2[0]), int(pt2[1])),
        color=color,
        thickness=thickness,
        lineType=cv2.LINE_AA,
    )

def crop_image_based_on_measurement(
    img: np.ndarray, 
    measurement: dict, 
    reference_center: int, 
    largest_width: int, 
    max_deviation: int = 30, 
    width_deviation: int = 50,
    safety_margin: int = 100
) -> Tuple[np.ndarray, int, int]:
    """
    Crop an image based on given measurements.

    Parameters:
    - img (np.ndarray): The image to be cropped.
    - measurement (dict): A dictionary containing 'distance' and 'center_point'.
    - reference_center (int): The reference center for cropping.
    - largest_width (int): The largest width considered for cropping.
    - max_deviation (int, optional): Maximum deviation allowed for center adjustment.
    - width_deviation (int, optional): Maximum deviation allowed for width change.

    Returns:
    - Tuple[np.ndarray, int, int]: The cropped image, updated reference center,
      and updated largest width.
    """

    image_width = img.shape[1]
    current_width = measurement['distance'] + safety_margin
    current_center = measurement['center_point'][0]

    print(f"Initial reference_center: {reference_center}, current_center: {current_center}, max_deviation: {max_deviation}")

    # Update reference center if deviation is significant
    if abs(current_center - reference_center) > max_deviation:
        reference_center = (reference_center + current_center) // 2
        print(f"Updated reference_center: {reference_center}")

    print(f"Initial largest_width: {largest_width}, current_width: {current_width}, width_deviation: {width_deviation}")

    # Update the largest width if change is significant
    if abs(current_width - largest_width) > width_deviation:
        largest_width = current_width
        print(f"Updated largest_width: {largest_width}")

    # Calculate cropping points
    crop_start = int(max(0, reference_center - largest_width // 2))
    crop_end = int(min(image_width, reference_center + largest_width // 2))

    print(f"Cropping from {crop_start} to {crop_end}")

    # Crop and return the image
    cropped_img = img[:, crop_start:crop_end]
    return cropped_img, reference_center, largest_width