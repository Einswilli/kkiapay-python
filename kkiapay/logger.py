"""
KKiapay - Logging Module
This module provides a logging setup for the Kkiapay payment system.
"""
import logging
import os
import sys
from typing import Any, Dict, Optional
from logging.handlers import RotatingFileHandler

from kkiapay.types import LoggingConfig


####  SETUP LOGGER FUNCTION
def setup_logger(
    config: LoggingConfig,
    name: str = "KKiapay",
) -> logging.Logger:
    """
    Configures and returns a logger.

    Args:
        config: Logging configuration model
        name: Logger name (default is 'KKiapay')

    Returns:
        logging.Logger: Configured logger
    """

    logger = logging.getLogger(name)

    if not config.enabled:
        logger.disabled = True
        return logger

    # Set logging level
    logger.setLevel(config.level.value if hasattr(config.level, "value") else config.level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Determine log format
    if config.format == "json":
        try:
            import json_log_formatter
            formatter = json_log_formatter.JSONFormatter()
        except ImportError:
            raise ImportError("json_log_formatter must be installed to use JSON log format.")
    else:
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
        )

    # Add file handler with optional rotation
    if config.file:
        if config.rotate:
            file_handler = RotatingFileHandler(
                filename = config.file,
                maxBytes = config.max_size * 1024 * 1024,  # Convert MB to bytes
                backupCount = config.backups
            )
        else:
            file_handler = logging.FileHandler(config.file)

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Add console handler if requested
    if config.console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

#### SANITIZE LOGS FUNCTION
def sanitize_logs(
    data: Dict[str, Any], 
    sensitive_fields: Optional[list] = None
) -> Dict[str, Any]:
    """
    Sanitizes log data by masking sensitive information.

    Args:
        data: Data to sanitize
        sensitive_fields: List of sensitive fields to mask

    Returns:
        Dict[str, Any]: Sanitized data
    """

    # Default sensitive fields if not provided
    if sensitive_fields is None:
        sensitive_fields = [
            "password", "api_key", "secret", "token", "private_key",
            "api_secret", "client_secret", "card_number", "cvv", "signature"
        ]
    
    sanitized = {}
    
    for key, value in data.items():
        # Mask sensitive fields
        if key.lower() in [f.lower() for f in sensitive_fields]:
            # If the value is a string, mask it partially
            if isinstance(value, str) and value:
                visible_chars = min(4, len(value) // 4)
                sanitized[key] = value[:visible_chars] + "*" * (len(value) - visible_chars)
            else:
                sanitized[key] = "***"

        # Recursively sanitize nested dictionaries or lists
        elif isinstance(value, dict):
            sanitized[key] = sanitize_logs(value, sensitive_fields)

        elif isinstance(value, list) and value and isinstance(value[0], dict):
            sanitized[key] = [
                sanitize_logs(item, sensitive_fields) 
                if isinstance(item, dict) 
                else item 
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized


####
##      
#####
class KKiaPayLogger:
    """
    Specialized logger for payment operations.
    Logs payment events with the appropriate information.
    """
    
    def __init__(
        self, 
        config: LoggingConfig, 
        logger_name: str = "Kkiapay.payment"
    ):
        """
        Initializes the payment logger.

        Args:
            config: An instance of LoggingConfig
            logger_name: Name of the logger
        """
        # Setup the logger using the configuration
        self.logger = setup_logger(config=config, name=logger_name)
    
    def payment_initiated(
        self, 
        transaction_id: str,
        amount: float, 
        currency: str, 
        reference: str, 
        **kwargs
    ):
        """Logs the initiation of a payment."""
        self.logger.info(
            (
                "Payment initialized | "
                f"ID: {transaction_id} | "
                f"Amount: {amount} {currency} | "
                f"Ref: {reference}"
            ),
            extra = sanitize_logs(kwargs)
        )
    
    def payment_success(
        self, 
        amount: float, 
        currency: str, 
        reference: str, 
        transaction_id: str, 
        **kwargs
    ):
        """Logs a successful payment."""
        self.logger.info(
            (
                f"Payment successful | "
                f"ID: {transaction_id} | "
                f"Amount: {amount} {currency} | "
                f"Ref: {reference}"
            ),
            extra = sanitize_logs(kwargs)
        )
    
    def payment_failed(
        self, provider: str, 
        reference: str, 
        reason: str, 
        **kwargs
    ):
        """Logs a failed payment."""
        self.logger.error(
            (
                f"Paiement échoué | "
                f"ID: {provider} | "
                f"Ref: {reference} | "
                f"Reason: {reason}"
            ),
            extra = sanitize_logs(kwargs)
        )
    
    def refund_initiated(
        self, 
        transaction_id: str, 
        amount: Optional[float] = None, 
        **kwargs
    ):
        """Logs the initiation of a refund."""
        amount_str = f"Amount: {amount}" if amount else "total amount"
        # Log the refund initiation with sanitized logs
        self.logger.info(
            (
                f"Refund initialized | "
                f"ID: {transaction_id} | {amount_str}"
            ),
            extra = sanitize_logs(kwargs)
        )
    
    def refund_success(
        self, 
        transaction_id: str, 
        amount: Optional[float] = None, 
        **kwargs
    ):
        """Logs a successful refund."""
        amount_str = f"Amount: {amount}" if amount else "Total amount"
        self.logger.info(
            (
                f"Refund Success | "
                f"ID: {transaction_id} | {amount_str}"
            ),
            extra = sanitize_logs(kwargs)
        )
    
    def refund_failed(
        self, 
        transaction_id: str, 
        reason: str, 
        **kwargs
    ):
        """Logs a failed refund."""
        self.logger.error(
            (
                f"Refund failed | "
                f"ID: {transaction_id} | "
                f"Reason: {reason}"
            ),
            extra = sanitize_logs(kwargs)
        )
    
    def webhook_received(
        self, 
        event_type: str, 
        transaction_id: Optional[str] = None, 
        **kwargs
    ):
        """Logs the receipt of a webhook."""
        tx_info = f"| ID: {transaction_id}" if transaction_id else ""
        self.logger.info(
            (
                f"Webhook received | "
                f"Event: {event_type} {tx_info}"
            ),
            extra = sanitize_logs(kwargs)
        )
    
    def api_request(
        self, 
        method: str, 
        endpoint: str, 
        **kwargs
    ):
        """Logs an API request."""
        self.logger.debug(
            (
                f"API Request | "
                f"Method: {method.upper()} | "
                f"Endpoint: {endpoint}"
            ),
            extra = sanitize_logs(kwargs)
        )
    
    def api_response(
        self, 
        status_code: int, 
        endpoint: str, 
        **kwargs
    ):
        """Logs an API response."""
        log_level = logging.DEBUG if 200 <= status_code < 300 else logging.ERROR
        self.logger.log(
            log_level,
            (
                f"API Response | "
                f"Status Code: {status_code} | "
                f"Endpoint: {endpoint}" 
            ),
            extra = sanitize_logs(kwargs)
        )
