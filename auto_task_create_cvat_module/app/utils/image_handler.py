import numpy as np
from utils.metadata_image import MetadataImage
from datetime import datetime

import pickle


class ImageHandler:
        
    @staticmethod
    def convert_image_grey_scale_vector_to_matrix(image_vector: np.ndarray, height: int, width: int, mode: str) -> np.ndarray:
        """
        Convert a grayscale image represented as a vector to a matrix.

        Args:
            image_vector (numpy.ndarray): The input vector representing the image.
            height (int): The height of the original image.
            width (int): The width of the original image.
            mode (str): The mode of the image data. It should be one of the following:
                - '8-bit': for 8-bit grayscale images.
                - '12-bit': for 12-bit grayscale images.
                - '12-bit packed': for 12-bit packed grayscale images.

        Returns:
            numpy.ndarray: The matrix representation of the grayscale image.

        Raises:
            ValueError: If an unknown mode is provided.
        """
        # Get the original shape from the metadata
        original_shape = (height, width)

        if mode == 'Mono8':
            # Cast the data to 8-bit integers
            unpacked_data = image_vector.astype(np.uint8)
        
        elif mode == 'Mono12':
            # Cast the data to 16-bit integers
            unpacked_data = image_vector.astype(np.uint16) 

        elif mode == 'Mono12Packed':
            # Unpack the 12-bit packed data into 16-bit pixel values
            #unpacked_data = ImageHandler.__unpack_12bit(image_vector)
            raise ValueError(" The '12-bit packet method has not yet been implemented ")
            
        else:
            raise ValueError("Unknown mode - The mode should be: 8-bit, 12-bit, 12-bit packed. ")

        # Reshape the data back to its original matrix form
        original_matrix = unpacked_data.reshape(original_shape)
        return original_matrix

    @staticmethod
    def __unpack_12bit(image_vector):
        if image_vector.size % 3 != 0:
            raise ValueError("Invalid packed data size. Must be a multiple of 3.")

        unpacked_size = (image_vector.size // 3) * 2
        result = np.zeros(unpacked_size, dtype=np.uint16)

        # Ensure contiguous array for reliable slicing
        image_vector = np.ascontiguousarray(image_vector, dtype=np.uint16)
        
        # Unpack
        result[0::2] = ((image_vector[1::3] & 0x0F) << 8) | image_vector[0::3]
        result[1::2] = (image_vector[1::3] >> 4) | ((image_vector[2::3] & 0xFF) << 4)
        
        return result
    

    @staticmethod
    def convert_image_grey_scale_matrix_to_vector(image_matrix: np.ndarray, mode: str) -> np.ndarray:

        if mode == 'Mono8':
            # Cast the data to 8-bit integers
            image_vector = image_matrix.reshape(-1)
            
        elif mode == 'Mono12':
            # Cast the data to 16-bit integers
            image_vector = image_matrix.reshape(-1)

        elif mode == 'Mono12Packed':
            raise ValueError(" The '12-bit packet method has not yet been implemented ")
            # Unpack the 12-bit packed data into 16-bit pixel values
            #unpacked_data = ImageHandler.__unpack_12bit(image_matrix)

        return image_vector
    
