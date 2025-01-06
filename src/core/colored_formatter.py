import logging

from colorama import Fore, Style, init

# Inicializa o colorama
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """
    Formatter personalizado que adiciona cores e emojis aos logs.
    """
    
    # Mapeamento de níveis para cores e emojis
    FORMATS = {
        logging.DEBUG: (Fore.CYAN, "🔍"),
        logging.INFO: (Fore.GREEN, "ℹ️"),
        logging.WARNING: (Fore.YELLOW, "⚠️"),
        logging.ERROR: (Fore.RED, "❌"),
        logging.CRITICAL: (Fore.RED + Style.BRIGHT, "🚨")
    }

    def format(self, record):
        # Obtém a cor e emoji para o nível atual
        color, emoji = self.FORMATS.get(record.levelno, (Fore.WHITE, ""))
        
        # Salva o levelname original
        original_levelname = record.levelname
        # Modifica o levelname para incluir cor e emoji
        record.levelname = f"{color}{emoji} {original_levelname}{Style.RESET_ALL}"
        
        # Formata a mensagem
        result = super().format(record)
        
        # Restaura o levelname original
        record.levelname = original_levelname
        
        return result