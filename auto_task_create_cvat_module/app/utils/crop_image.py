#Crop and Measure
import cv2
from cv2.typing import MatLike
import numpy as np

def find_borders_optimized(binary: np.ndarray, white_pixels_limit: float, 
                           start_height_percent: float = 0, end_height_percent: float = 1):
    """
    Optimized function to identify the left and right borders of an area in a binary image based on
    the density of white pixels using numpy vectorized operations.
    
    Parameters:
        binary (np.ndarray): The binary image to process.
        white_pixels_limit (float): The threshold proportion of white pixels in a column.
        start_height_percent (float): The starting vertical percentile of the image to consider (0-1).
        end_height_percent (float): The ending vertical percentile of the image to consider (0-1).
    
    Returns:
        tuple: A tuple containing:
               - List of white pixel proportions per column,
               - Index of the first border column,
               - Index of the last border column,
               - Approximate center column index between the first and last borders.
    """
    height, width = binary.shape
    ignore = 140  # columns ignored from each side of the image

    # Calculate the start and end indices in terms of rows
    start_row = int(height * start_height_percent)
    end_row = int(height * end_height_percent)

    # Calculate white pixel proportions using vectorized operations
    white_pixels_proportions = np.mean(binary[start_row:end_row, ignore:width-ignore] == 255, axis=0)

    # Determine columns that exceed the white pixel limit
    valid_columns = white_pixels_proportions > white_pixels_limit

    # Use convolution to find regions with the required minimum number of consecutive columns
    min_consecutive = 5
    filter_kernel = np.ones(min_consecutive, dtype=int)
    valid_consecutive_columns = np.convolve(valid_columns, filter_kernel, mode='same') >= min_consecutive

    # Find indices of the valid regions
    valid_indices = np.where(valid_consecutive_columns)[0] + ignore  # adjusting for 'ignore'

    if valid_indices.size > 0:
        first_index = valid_indices[0]
        last_index = valid_indices[-1]
        # Calculate the center column index
        coil_center = (first_index + last_index) // 2
    else:
        # Default to the center of the range if no valid borders are found
        first_index, last_index = ignore, width - ignore - 1
        coil_center = (first_index + last_index) // 2

    return white_pixels_proportions, first_index, last_index, coil_center

def find_borders(binary: MatLike, white_pixels_limit: float, start_height_percent:float = 0, end_height_percent: float = 1):
    # Obter largura e altura da imagem
    height, width = binary.shape


    # Igora colunas do inicio e fim
    ignore = 140

    white_pixels_per_column = []

    # Iterar sobre cada coluna da imagem para verificar os pixels brancos (Igora 200 de cada lado)
    relative_height = height * (end_height_percent - start_height_percent)
    for col in range(ignore, width - ignore):
        white_pixels = np.count_nonzero(binary[round(height*start_height_percent):round(height*end_height_percent), col] == 255) / relative_height
        white_pixels_per_column.append(white_pixels)

    # Encontrar o primeiro e o último índice
    first_ind = 0
    last_ind = width - 1

    count = 0
    for i, value in enumerate(white_pixels_per_column):
        if value > white_pixels_limit:
            count = count + 1
            if count == 1:
                first_ind = i + ignore
            if count >= 5:
                break
        else:
            count = 0
            first_ind = 0

    count = 0
    for i in range(len(white_pixels_per_column) - 1, -1, -1):
        if white_pixels_per_column[i] > white_pixels_limit:
            count = count + 1
            if count == 1:
                last_ind = i + ignore
            if count >= 5:
                break
        else:
            count = 0
            last_ind = width - 1

    coil_center = round(first_ind + (last_ind - first_ind) / 2)

    return white_pixels_per_column, first_ind, last_ind, coil_center


def crop_and_measure(image: MatLike, mm_per_px: float = 1, border_size_px: int = 100, white_pixel_percentage_limit: float = 0.08, threshold1: int = 13, threshold2: int = 35, last_coil_center: int = -1, last_coil_width_mm: float = -1, compressionRatio = 1):

#   Config
  max_coil_width = 1600
  min_coil_width = 940
  
  real_width = image.shape[1]
  real_height = image.shape[0]
  # Redimensionar a imagem para ganho de performace
  width = int(real_width * compressionRatio)
  height = int(real_height * compressionRatio)
  resized_image = cv2.resize(image, (width, height))
  
  # Filtro de desfoque
  blur = cv2.GaussianBlur(resized_image, (1,99), 0)
  # Detecção de bordas
  canny = cv2.Canny(blur, threshold1=threshold1, threshold2=threshold2)
  # Encontrar contornos na imagem canny
  canny_edges, _ = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

  # Cria uma imagem com os contornos
  edges_image = np.zeros((height, width, 3), dtype=np.uint8)
  edges_image = cv2.cvtColor(edges_image, cv2.COLOR_BGR2GRAY)
  cv2.drawContours(edges_image, canny_edges, -1, (255, 255, 255), 3)

  # Realiza a detecção das bordas e ofsets
  _, _, _, start_coil_center  = find_borders_optimized(edges_image, white_pixel_percentage_limit * 3, 0, 0.1)
  _, first_ind, last_ind, coil_center  = find_borders_optimized(edges_image, white_pixel_percentage_limit, 0, 1)
  _, _, _, end_coil_center  = find_borders_optimized(edges_image, white_pixel_percentage_limit * 3, 0.9, 1)

  # Realiza a detecção da medida
  _, first_ind_measure, last_ind_measure, _  = find_borders_optimized(edges_image, white_pixel_percentage_limit * 3, 0.45, 0.55)

  # Redimensionar o index para compensar o resize do inicio
  start_coil_center =  int(start_coil_center / compressionRatio)
  coil_center =  int(coil_center / compressionRatio)
  end_coil_center =  int(end_coil_center / compressionRatio)
  first_ind = int(first_ind / compressionRatio)
  last_ind =  int(last_ind / compressionRatio)
  
  # Informações da bobina
#   coil_width_px = last_ind - first_ind
  coil_width_px = last_ind_measure - first_ind_measure
  coil_width_mm = coil_width_px * mm_per_px

  # Compara coil_width anterior com o atual, caso seja maior que 10% houve um erro
  # Não há problemas quando troca de bobina pois o valor de last_coil_width_mm se torna zero quando troca de bobina
  if (last_coil_width_mm > 0):
    if (abs(last_coil_width_mm - coil_width_mm) / last_coil_width_mm > 10/100):
      coil_width_mm = last_coil_width_mm
      coil_center = last_coil_center

      first_ind = round(coil_center - ((coil_width_mm / 2) / mm_per_px))
      last_ind = round(coil_center + ((coil_width_mm / 2) / mm_per_px))

  start_offset = (start_coil_center - coil_center)
  end_offset = (end_coil_center - coil_center)

  # Ajustar o corte para manter a altura original e adicionar bordas na largura
  crop_start = first_ind - border_size_px
  crop_end = last_ind + border_size_px

  # Corta a imagem
  cropped_image = image[0:real_height, crop_start:crop_end]

  #Verifica as dimensões limites
  if (coil_width_mm > max_coil_width or coil_width_mm < min_coil_width):
    # Tenta a medida alternativa
    alt_coil_width_px = last_ind - first_ind
    alt_coil_width_mm = alt_coil_width_px * mm_per_px
    if (alt_coil_width_mm > max_coil_width or alt_coil_width_mm < min_coil_width):
      coil_width_mm = 0
      start_offset = 0
      end_offset = 0
      cropped_image = image
    else:
       coil_width_mm = alt_coil_width_mm
    
  start_offset_mm = start_offset * mm_per_px
  end_offset_mm = end_offset * mm_per_px

  return cropped_image, coil_width_mm, start_offset, end_offset, coil_center, edges_image

def draw_col(image: MatLike, col: int, start:int, end:int, color, thickness=1):
  # Definir as coordenadas iniciais e finais da linha
  start_point = (col, start)
  end_point = (col, end)
  image_with_line = cv2.line(image, start_point, end_point, color, thickness=thickness)

  return image_with_line

def draw_line(image: MatLike, lin: int, start:int, end:int, color, thickness=1):
  # Definir as coordenadas iniciais e finais da linha
  start_point = (start, lin)
  end_point = (end, lin)
  image_with_line = cv2.line(image, start_point, end_point, color, thickness=thickness)

  return image_with_line



# if __name__ == "__main__":
#   import time

#   image = cv2.imread('teste2.jpg')

#   start_time = time.perf_counter()
#   # Com validação da medida da imagem anterior (Só poderá ser usado quando garantir que a solda estará no final da bobina)
#   # crop_image, coil_width_mm, offset_start, offset_end, coil_center  = crop_and_measure(resized_image, 0.45, 150, last_coil_center=830, last_coil_width_mm=456.3)
  
#   # Sem validação da medida da imagem anterior (Usar por enquanto)
#   crop_image, coil_width_mm, offset_start, offset_end, coil_center  = crop_and_measure(image, 0.45, 30)
#   end_time = time.perf_counter()

#   # Redimensionar a imagem para 20% do tamanho original
#   width = int(crop_image.shape[1] * 0.2)
#   height = int(crop_image.shape[0] * 0.2)
#   crop_image = cv2.resize(crop_image, (width, height))

#   print(f"Tempo: {end_time - start_time}")

#   print(f"Tamanho da bobina em mm: {coil_width_mm}")
#   print(f"coil_center: {coil_center} px")
#   print(f"offset_start: {offset_start} px")
#   print(f"offset_end: {offset_end} px")

#   # Mostrar a imagem cortada
#   cv2.imshow('Imagem cropada teste', crop_image)
#   cv2.waitKey(0)
#   cv2.destroyAllWindows()

