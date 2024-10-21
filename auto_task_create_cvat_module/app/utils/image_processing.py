import cv2

def apply_simple_thresholding(image, th_value=18):
    "Apply simple thresholding to a given image"
    # Apply thresholding
    _, thresh = cv2.threshold(image, th_value, 255, cv2.THRESH_BINARY)
    return thresh


def apply_morphological_closing(image, kernel_size, iterations):
    """Apply morphological closing to an image."""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, kernel_size)
    return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=iterations)


def apply_morphological_opening(image, kernel_size, iterations):
    """Apply morphological closing to an image."""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, kernel_size)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=iterations)
