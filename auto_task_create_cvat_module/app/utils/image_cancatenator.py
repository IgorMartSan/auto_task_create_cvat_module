import cv2
import numpy as np


class ImageConcatenator:
    """
    Class for concatenating images.

    Attributes:
        id (int): Identifier for the ImageConcatenator instance.
        num_of_images (int): Number of images required for concatenation.
        image (numpy.ndarray): The concatenated image array.
    """

    def __init__(self, width: int, height: int, concat_height: int) -> None:
        """
        Initializes a new ImageConcatenator object with given dimensions.

        Args:
            width (int): Width of the image.
            height (int): Height of the image.
            concat_height (int): Desired height for the concatenated image.
        """
        self._width = width
        self._height = height
        self._final_concat_height = (concat_height // height) * height
        self.num_of_images = self._final_concat_height // self._height
        self.image = np.zeros((self._final_concat_height, self._width), dtype=np.uint8)
        self._idx = 0
        self._image_list = []

    def __str__(self) -> str:
        """Return a string representation of the instance."""
        return (
            f"Concatenated Image: {self._width}x{self._final_concat_height}\n"
            f"Required images: {self.num_of_images}"
        )

    def _reset(self) -> None:
        """
        Resets the image and index for a new set of images.
        """
        self.image = np.zeros((self._final_concat_height, self._width), dtype=np.uint8)
        self._idx = 0

    def pop(self) -> np.ndarray:
        """
        Removes and returns the first image in the image list.

        Returns:
            np.ndarray: The first image in the image list, if available.
        """
        if not self._image_list:
            return None
        image = self._image_list.pop(0)
        return image

    def show(self) -> None:
        """
        Displays the concatenated image in a window.
        """
        # Calculate new dimensions
        new_width = int(self.image.shape[1] * 0.1)
        new_height = int(self.image.shape[0] * 0.1)
        resized_image = cv2.resize(self.image, (new_width, new_height))

        cv2.imshow(f"Concatenated Image: {self._idx}", resized_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def fill(self, image: np.ndarray) -> None:
        """
        Fills the instance's image with the input image.

        Args:
            image (np.ndarray): The image to be concatenated.
        """
        start_idx = self._idx * self._height
        end_idx = (self._idx + 1) * self._height
        self.image[start_idx:end_idx, :] = image.view()
        self._idx += 1

        if self._idx >= self.num_of_images:
            self._image_list.append(self.image)
            self._reset()

    def fill_from_bottom(self, image: np.ndarray) -> None:
        """
        Fills the instance's image with the input image, concatenating from bottom to top.

        Args:
            image (np.ndarray): The image to be concatenated.
        """
        # Calculate the starting and ending indices in reverse order
        end_idx = self.image.shape[0] - (self._idx * self._height)
        start_idx = end_idx - self._height

        # Place the new image into the calculated slice
        self.image[start_idx:end_idx, :] = image.view()
        self._idx += 1

        # Check if the image limit is reached and handle accordingly
        if self._idx >= self.num_of_images:
            self._image_list.append(self.image)
            self._reset()