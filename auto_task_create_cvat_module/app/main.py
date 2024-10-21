import os
import time
import traceback
import cv2
import numpy as np
from datetime import datetime
from config.logger import get_logger
from dao.redis_connection import RedisConnection
from utils.image_handler import ImageHandler
from inference.model_manager import ModelManagerYolo
from config.environment import Environment
from prometheus_client import start_http_server
from utils.metrics_prometheus import register_execution_time_gauge
from utils.cvat_requests import CVATClient  # Assumindo que você tenha um cliente CVAT configurado

start_http_server(8123)

####################### ENV #######################
env = Environment()
time.sleep(1)

####################### LOG #######################
logger = get_logger()
####################### CONSTANTS #######################



IMAGE_SAVE_DIR = "/home/igor/projects/CVAT/saved_images"
NUM_IMG_PER_TASK = 100
CHECK_INTERVAL = 60 * 60 * 24  # 24 horas (em segundos) para inciar outro clico
TASKS_PER_DAY = 2  # Número máximo de tasks que podem ser criadas por dia MAX_IMAGE * TASK_PER_DAY

cvat_url = "http://10.247.141.99:8080"
username = "igor.santos@aperam.com"
password = "qwer1234Q."
project_id = 18
min_defects_to_save_image = 1
conf_model = 0.1

####################### UTILITIES #######################

def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def clear_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            logger.error(f'Failed to delete {file_path}. Reason: {e}')

def save_image(image_matrix, image_count, path):
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    image_name = f"{timestamp}_{image_count}.png"
    image_path = os.path.join(path, image_name)
    cv2.imwrite(image_path, image_matrix)
    logger.info(f"Image saved: {image_path}")
    return image_path

def get_image_count_in_directory(directory):
    return len([name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))])

def get_path_imagens(diretorio_raiz):
    imagens = []
    for root, dirs, files in os.walk(diretorio_raiz):
        for file in files:
            if file.endswith(('.jpg', '.png')):
                imagens.append(os.path.join(root, file))
    return imagens

####################### MAIN #######################

def main():
    MODEL_PATH1 = "/home/igor/projects/CVAT/auto_task_create_cvat_module/app/inference/models/main.pt"
    MODEL_PATH2 = "/code/app/inference/models/main.pt"
    try:
        model_manager = ModelManagerYolo(model_path=MODEL_PATH2)
    except:
        model_manager = ModelManagerYolo(model_path=MODEL_PATH1)

    print(f"A GPU está ativada? \n {model_manager.gpuIsAvaliable()}")
    time.sleep(2)
    
    print(f"Lista das classes do modelo carregado (índice, nome): \n {model_manager.getAllClassesNameAndIndexToModel()}")

    redis_con = RedisConnection(
        host=env.REDIS_HOST,
        port=env.REDIS_PORT,
        db=env.REDIS_DB
    )

    client = CVATClient(cvat_url=cvat_url, username=username, password=password)

    image_count = 0
    current_id_stream_1 = "0"
    current_id_stream_2 = "0"
    image_paths = []

    create_directory_if_not_exists(IMAGE_SAVE_DIR)
    toggle = True

    tasks_created_today = 0  # Contador de tasks criadas hoje
    current_day = datetime.now().day  # Inicializa com o dia atual

    while True:
        start_time = time.perf_counter()

        ################### GET DATA FROM CAM SERVICE ################### 
        
        if toggle:
            # Processa o primeiro stream
            metadata, current_id_stream_1 = redis_con.get_from_stream(
                stream_key=env.REDIS_STREAM_KEY_CONS, 
                last_id=current_id_stream_1)
        else:
            # Processa o segundo stream
            metadata, current_id_stream_2 = redis_con.get_from_stream(
                stream_key=env.REDIS_STREAM_KEY_CONS2, 
                last_id=current_id_stream_2)
        
        toggle = not toggle
        
        ################### PROCESS IMAGE ################### 
        matrix_image = ImageHandler.convert_image_grey_scale_vector_to_matrix(
            image_vector=metadata["camera"]["image"],
            height=metadata["camera"]["height"],
            width=metadata["camera"]["width"],
            mode=metadata["camera"]["pixelformat"])
        
        complete_matrix_image_bgr = cv2.cvtColor(matrix_image, cv2.COLOR_GRAY2BGR)

        image_height, image_width = complete_matrix_image_bgr.shape[:2]
        defects = model_manager.detect_defects_using_xywhn(img=complete_matrix_image_bgr,confidence_threshold=conf_model)

        
        metadata["defects"] = defects["defects"]

        if len(metadata["defects"]) >= min_defects_to_save_image:
            ################### SAVE IMAGE ###################
            image_count += 1
            save_image(image_matrix=matrix_image, image_count=image_count, path=IMAGE_SAVE_DIR)
        
            
        # Verificar se chegou no limite de 100 imagens e se podemos criar mais tasks hoje
        if get_image_count_in_directory(directory=IMAGE_SAVE_DIR) >= NUM_IMG_PER_TASK and tasks_created_today < TASKS_PER_DAY:
            print(f"Criando task {tasks_created_today + 1}/{TASKS_PER_DAY} de hoje...")
            paths_imagens: list = get_path_imagens(diretorio_raiz=IMAGE_SAVE_DIR)
            data_hora_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            task_name = f"New task date {data_hora_atual}"

            if client.criar_task_com_imagens(image_paths=paths_imagens, project_id=project_id, task_name=task_name):
                # Se o envio foi bem-sucedido, limpar o diretório
                clear_directory(IMAGE_SAVE_DIR)
                image_paths.clear()  # Limpa a lista de caminhos de imagens
                image_count = 0  # Reseta o contador de imagens
                tasks_created_today += 1  # Incrementa o número de tasks criadas no dia
            else:
                print("Erro ao enviar imagens para o CVAT. Tentando novamente após 24 horas.")

        # Verifica se atingiu o limite diário de tasks criadas
        if tasks_created_today >= TASKS_PER_DAY:
            print(f"Limite de tasks atingido. Aguardando {CHECK_INTERVAL} s")
            time.sleep(CHECK_INTERVAL)  # Espera até o próximo dia (24 horas)
            tasks_created_today = 0

        register_execution_time_gauge(time.perf_counter() - start_time)


if __name__ == "__main__":
    try:
        main() 
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.exception(f"Traceback details:\n {error_trace}")
        traceback.print_exc()
