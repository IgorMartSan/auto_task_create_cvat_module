import cv2
import math
import base64
import torch
from ultralytics import YOLO

class ModelManagerYolo:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = YOLO(self.model_path)
        
        # Definindo uma lista de cores para as classes, cada cor será associada ao índice da classe correspondente
        self.colors = [
            "#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#33FFA1", "#A133FF", "#FF9633", "#33FF96", "#9633FF", "#FF333F",
            "#33FFDA", "#FFDA33", "#DA33FF", "#33DAFF", "#FFD733", "#33FF73", "#7333FF", "#FF3370", "#70FF33", "#FF7033",
            "#33FF70", "#3370FF", "#FF33DA", "#DAFF33", "#70DAFF", "#DAFF70", "#FF3377", "#7733FF", "#33FF77", "#FF7733"
        ]

    def getAllClassesNameAndIndexToModel(self):
        return self.model.model.names

    def gpuIsAvaliable(self):
        return torch.cuda.is_available()

    def detect_defects_and_return_data(self, img, confidence_threshold=0.1):
        results = self.model(img, stream=True, imgsz=640)
        defects = []

        # Obtém a altura e a largura da imagem original
        image_height, image_width = img.shape[:2]

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                conf = math.ceil((box.conf[0] * 100)) / 100
                cls = int(box.cls[0])

                # Verifica se a classe existe no modelo
                if cls in self.model.model.names:
                    defect_name = self.model.model.names[cls]
                    color_hex = self.colors[cls % len(self.colors)]  # Associa cor fixa com base no índice

                    if conf > confidence_threshold:
                        defects.append({
                            "Name": defect_name,
                            "bounding_box_x_px": x1,
                            "bounding_box_y_px": y1,
                            "bounding_box_width_px": x2 - x1,
                            "bounding_box_height_px": y2 - y1,
                            "color_hex": color_hex,
                            "confidence": conf
                        })

        # Codificar a imagem em base64
        _, buffer = cv2.imencode('.jpg', img)
        img_str_base64 = base64.b64encode(buffer).decode('utf-8')

        # Criar o dicionário no formato especificado
        data = {
            "defects": defects,
            "image_base64": img_str_base64,
            "image_height": image_height,
            "image_width": image_width
        }

        return data

    def detect_defects_using_xywhn(self, img, confidence_threshold=0.1, width = None, height = None):
        if width or height is None:
            results = self.model(img, stream=True)
        else:
            results = self.model(img, stream=True, imgsz=(height, width))

            
             #imgsz=640)
        defects = []
        # Obtém a altura e a largura da imagem original
        image_height, image_width = img.shape[:2]
        print ("##############################################################")
        print (img.shape[:2])

        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Obter as coordenadas normalizadas no formato xywhn
                x_center_n, y_center_n, width_n, height_n = box.xywhn[0]  # Coordenadas normalizadas
        
                # Desnormalizar para o tamanho real da imagem

                width = width_n * image_width
                height = height_n * image_height
                x_center = ((x_center_n * image_width))
                y_center = ((y_center_n * image_height))


                # Confiança e classe do defeito
                conf = math.ceil((box.conf[0] * 100)) / 100
                cls = int(box.cls[0])

                # Verifica se a classe existe no modelo
                if cls in self.model.model.names:
                    defect_name = self.model.model.names[cls]
                    color_hex = self.colors[cls % len(self.colors)]  # Associa cor fixa com base no índice

                    # Verifica se a confiança é maior que o limiar configurado
                    if conf > confidence_threshold:
                        defects.append({
                            "Name": defect_name,
                            "bounding_box_x_px": float(x_center),
                            "bounding_box_y_px": float(y_center),
                            "bounding_box_width_px": float(width),
                            "bounding_box_height_px": float(height),
                            "color_hex": color_hex,
                        })

        # Criar o dicionário no formato especificado
        data = {
            "defects": defects,
        }

        return data
