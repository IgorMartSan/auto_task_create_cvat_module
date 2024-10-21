import os
from dotenv import load_dotenv

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()


class Environment:
    def __init__(self):
        # Atributos da configuração carregados do ambiente
        self.CONTAINER_NAME: str = os.getenv("CONTAINER_NAME")

        self.REDIS_PORT: str = os.getenv("REDIS_PORT")
        self.REDIS_HOST: str = os.getenv("REDIS_HOST")
        self.REDIS_DB: str = os.getenv("REDIS_DB")
        self.REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD")

        self.REDIS_STREAM_KEY_CONS: str = os.getenv("REDIS_STREAM_KEY_CONS")
        self.REDIS_STREAM_KEY_CONS2: str = os.getenv("REDIS_STREAM_KEY_CONS2")

        
        









        # Convertendo variáveis de ambiente para tipos apropriados
        # self.RESIZE_PERCENT: int = int(os.getenv("RESIZE_PERCENT"))

        # self.TILE_HEIGHT: int = int(os.getenv("TILE_HEIGHT"))
        # self.IMG_WIDTH: int = int(os.getenv("IMG_WIDTH"))
        # self.CONCAT_HEIGHT: int = int(os.getenv("CONCAT_HEIGHT"))
        
        # self.IMAGE_NUMBER_ROTATE_DEGREES_90: int = int(
        #     os.getenv("IMAGE_NUMBER_ROTATE_DEGREES_90")
        # )
        # self.MILIMETROS_PER_PIXEL_HEIGHT: float = float(os.getenv("MILIMETROS_PER_PIXEL_HEIGHT"))
        # self.MILIMETROS_PER_PIXEL_WIDTH: float = float(os.getenv("MILIMETROS_PER_PIXEL_WIDTH"))


        # Caminho do modelo
        self.MODEL_PATH: str = os.getenv(
            "MODEL_PATH", "/code/client_ws/inference/models/2024_07_12_best.pt"
        )

    def __str__(self):
        # Obtendo todas as variáveis de instância e seus valores
        instance_vars = {name: value for name, value in self.__dict__.items()}
        # Formatando as variáveis no formato "Nome: Tipo = valor"
        formatted_vars = "\n".join(
            f"{name}: {type(value).__name__} = {value}"
            for name, value in instance_vars.items()
        )
        return formatted_vars


# Exemplo de uso
env = Environment()
print(env)
