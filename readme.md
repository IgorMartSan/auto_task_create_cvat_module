# LEIAME (README)

Este projeto é um sistema de processamento de imagens que detecta defeitos usando um modelo YOLO, salva imagens com defeitos localmente e, posteriormente, cria tasks no CVAT para anotação.

## Funcionalidades
- Processa imagens de streams Redis.
- Detecta defeitos com YOLO.
- Cria até 3 tasks diárias no CVAT, cada uma com até 100 imagens.
- Limpa o diretório de imagens após o envio.

## Requisitos
- Python 3.x
- Redis
- CVAT

## Como Executar
1. Configure as variáveis de ambiente (ex: Redis, CVAT).
2. Execute o script principal:
   ```bash
   python main.py
