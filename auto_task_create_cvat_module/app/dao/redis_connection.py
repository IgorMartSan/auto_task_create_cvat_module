import redis
import atexit
import pickle
from prometheus_client import Summary, Counter
from functools import wraps

class RedisConnection:
    _instance_counter = 0
    
    def __init__(self, host, port, db, password = None):
        """
        Initializes the connection to the Redis server.
        
        Inicializa a conexão com o servidor Redis.
        """
        RedisConnection._instance_counter += 1
        self.__instance_id = RedisConnection._instance_counter
        self.__host = host
        self.__port = port
        self.__db = db
        self.__password = password
        
        if self.__password == None:
            self.redis_client = redis.Redis(
                host=self.__host,
                port=self.__port,
                db=self.__db
            )
        else:
                self.redis_client = redis.Redis(
                host=self.__host,
                port=self.__port,
                db=self.__db,
                password=self.__password
            )
        self._initialize_metrics()

    def _initialize_metrics(self):
        """
        Initializes the Prometheus metrics and applies decorators to the methods.
        
        Inicializa as métricas do Prometheus e aplica decoradores aos métodos.
        """
        self.STREAM_WRITE_TIME = Summary(f'redis_queue_write_time_seconds_{self.__instance_id}', 'Time spent writing to the queue redis')
        self.STREAM_READ_TIME = Summary(f'redis_queue_read_time_seconds_{self.__instance_id}', 'Time spent reading from the queue')
        self.PUSH_COUNTER = Counter(f'redis_queue_write_total_{self.__instance_id}', 'Total number of Redis write operations performed')
        self.READ_COUNTER = Counter(f'redis_queue_read_total_{self.__instance_id}', 'Total number of Redis read operations performed')

        self._decorate_methods()

    def _decorate_methods(self):
        """
        Applies decorators to methods to record metrics.
        
        Aplica decoradores aos métodos para registrar métricas.
        """
        self.add_to_stream = self._time_decorator(self.add_to_stream, self.STREAM_WRITE_TIME)
        self.get_from_stream = self._time_decorator(self.get_from_stream, self.STREAM_READ_TIME)

    def _time_decorator(self, func, metric):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with metric.time():
                return func(*args, **kwargs)
        return wrapper

    def get_connection(self):
        """
        Returns the Redis client for operations.
        
        Retorna o cliente Redis para operações.
        """
        return self.redis_client

    def __destroy_connection(self):
        """
        Ends the connection to the Redis server.
        
        Finaliza a conexão com o servidor Redis.
        """
        print("Connection terminated")
        self.redis_client.close()

    def add_to_stream(self, data: dict, stream_key: str, max_len: int = 50):
        """
        Adds data to a stream in Redis.
        
        Adiciona dados a um stream no Redis.

        Args:
            stream_key (str): Name of the stream where the data will be added.
            data (dict): Data to be added as a dictionary, should be serialized with the pickle library.
            max_len (int, optional): Maximum length of the stream. Default is 50.

        Returns:
            str: The ID of the added entry.

        Args:
            stream_key (str): Nome do stream onde os dados serão adicionados.
            data (dict): Dados a serem adicionados como um dicionário, deve ser serializado com a biblioteca pickle.
            max_len (int, optional): Comprimento máximo do stream. O padrão é 50.

        Returns:
            str: O ID da entrada adicionada.
        """
        serialized_data = pickle.dumps(data)
        entry_id = self.redis_client.xadd(
            stream_key,
            {"data_serialized": serialized_data},
            maxlen=max_len,
            approximate=True
        )

        # Increment the counter for each write operation
        # Incrementa o contador para cada operação de escrita
        self.PUSH_COUNTER.inc()
        return entry_id

    def get_from_stream(self, stream_key: str, last_id: str = "0") -> dict:
        """
        Reads a single entry from the stream in Redis and returns the deserialized data.

        Lê uma única entrada do stream no Redis e retorna os dados desserializados.

        Args:
            stream_key (str): Name of the stream.
            last_id (str): ID of the last read entry. Default is "0".

        Returns:
            dict: Deserialized data and the last read ID, or None if the stream is empty.

        Args:
            stream_key (str): Nome do stream.
            last_id (str): ID da última entrada lida. O padrão é "0".

        Returns:
            dict: Dados desserializados e o último ID lido, ou None se o stream estiver vazio.
        """
        # Reads a single message from the stream in Redis
        # Lê uma única mensagem do stream no Redis
        stream_messages = self.redis_client.xread(
            {stream_key: last_id}, count=1, block=0)

        if stream_messages:
            stream_name, message_list = stream_messages[0]
            message = message_list[0]

            # Gets the current message ID
            # Obtém o ID da mensagem atual
            currentID = message[0]

            # Extracts the serialized data from the message
            # Extrai os dados serializados da mensagem
            data_serialized = message[1][b'data_serialized']

            # Deserializes the data using the pickle library
            # Desserializa os dados usando a biblioteca pickle
            deserialized_data = pickle.loads(data_serialized)

            # Updates the last read ID
            # Atualiza o último ID lido
            last_id = currentID
            
            # Increment the counter for each read operation
            # Incrementa o contador para cada operação de leitura
            self.READ_COUNTER.inc()
            return deserialized_data, last_id

        # Returns None if there are no messages
        # Retorna None se não houver mensagens
        return None

    def get_stream_length(self, stream_name):
        """
        Returns the length of the stream.
        
        Retorna o comprimento do stream.

        Args:
            stream_name (str): Name of the stream.
            stream_name (str): Nome do stream.

        Returns:
            int: Length of the stream.
            int: Comprimento do stream.
        """
        stream_length = self.redis_client.xlen(stream_name)
        return stream_length

    def insert_dict_to_redis(self, key, data):
        """
        Inserts a dictionary into Redis.

        Insere um dicionário no Redis.

        Args:
            key (str): Key for the dictionary.
            data (dict): Dictionary to be inserted.
            
        Args:
            key (str): Chave para o dicionário.
            data (dict): Dicionário a ser inserido.
        """
        serialized_data = pickle.dumps(data)
        self.redis_client.set(key, serialized_data)

    def get_dict_from_redis(self, key):
        """
        Retrieves a dictionary from Redis.

        Recupera um dicionário do Redis.

        Args:
            key (str): Key for the dictionary.

        Args:
            key (str): Chave para o dicionário.

        Returns:
            dict: Dictionary retrieved from Redis.
            dict: Dicionário recuperado do Redis.
        """
        serialized_data = self.redis_client.get(key)
        if serialized_data:
            deserialized_data = pickle.loads(serialized_data)
            return deserialized_data
        else:
            return None
