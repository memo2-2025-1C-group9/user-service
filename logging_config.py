import logging

# Configuracion de un logger global para poder usarlo tanto desde el controller
# como desde los archivos de tests
def setup_logger(service: str) -> logging.Logger:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(service)

    return logger
