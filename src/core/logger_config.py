# logger_config.py
import logging

from src.core.colored_formatter import ColoredFormatter


def setup_global_logging(
    level: int = logging.INFO,
    log_file: str = None
) -> logging.Logger:
    """
    Configura o logger global com formatação colorida e opcionalmente salva em arquivo.
    
    Args:
        level: Nível de logging (default: logging.INFO)
        log_file: Caminho opcional para arquivo de log
        
    Returns:
        logging.Logger: Logger global configurado
    """
    # Obtém o logger root
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Remove handlers existentes para evitar duplicação
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Configuração do console handler com cores
    console_handler = logging.StreamHandler()
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Configuração opcional do file handler
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

# Configuração inicial do logger global
logger = setup_global_logging()

# Função helper para obter um logger específico para cada módulo
def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger específico para um módulo, mantendo a configuração global.
    
    Args:
        name: Nome do módulo/logger
        
    Returns:
        logging.Logger: Logger configurado para o módulo
    """
    return logging.getLogger(name)