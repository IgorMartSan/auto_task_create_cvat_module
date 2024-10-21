import mysql.connector
import random
from PIL import Image
import os
import atexit
import traceback

class MariaDBConnection:
    def __init__(self, host, username, password, database, port):
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.port = port
        self.connection = None
        #atexit.register(self.disconnect)


    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.username,
                password=self.password,
                database=self.database,
                port=int(self.port)
            )
            if self.connection.is_connected():
                print("Conectado ao banco de dados")
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {str(e)}")
            #traceback.print_exc()
            raise
            

    def disconnect(self):
        if self.connection is not None and self.connection.is_connected():
            self.connection.close()
            print("Desconectado do banco de dados")

            

    def insert_operation(self, genk_coil_id, global_operation_id, num_pictures):
        try:
            cursor = self.connection.cursor()
            insert_query = ("INSERT INTO operation "
                            "(genkCoilId, globalOperationId, numPictures) "
                            "VALUES (%s, %s, %s)")
            data = (genk_coil_id, global_operation_id, num_pictures)
            cursor.execute(insert_query, data)
            self.connection.commit()
            last_inserted_id = cursor.lastrowid 
            cursor.close()
            print("Inserção de operação bem-sucedida")
            return last_inserted_id  # Retorne o ID criado
        except Exception as e:
            print(f"Erro ao inserir operação no banco de dados: {str(e)}")
            traceback.print_exc()
            raise


        

    def insert_picture(self, 
                       operation_id:any, 
                       product_position_left:any, product_position_right:any,
                   product_position_start:any, product_position_end:any, picture_scale_x:any, picture_scale_y:any,uri:any, cutoff:any,
                   type=1,  label_uri=None, saved=1, original_brightness_min=0,
                   original_brightness_max=255, system_id=1, compression_quality=95):
        try:
            cursor = self.connection.cursor()
            insert_query = ("INSERT INTO picture "
                            "(operationId, productPositionLeft, productPositionRight, "
                            "productPositionStart, productPositionEnd, pictureScaleX, pictureScaleY, "
                            "type, uri, labelUri, saved, originalBrightnessMin, originalBrightnessMax, "
                            "systemId, compressionQuality, cutoff) "
                            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
            
            data = (operation_id,  product_position_left, product_position_right,
                    product_position_start, product_position_end, picture_scale_x, picture_scale_y,
                    type, uri, label_uri, saved, original_brightness_min, original_brightness_max,
                    system_id, compression_quality, cutoff)
            
            cursor.execute(insert_query, data)
            self.connection.commit()
            last_inserted_id = cursor.lastrowid  # Obtenha o ID da última inserção
            cursor.close()
            print(f"Inserção de imagem bem-sucedida. ID inserido: {last_inserted_id}")
            return last_inserted_id  # Retorne o ID criado
        except Exception as e:
            print(f"Erro ao inserir imagem no banco de dados: {str(e)}")
            traceback.print_exc()
            raise