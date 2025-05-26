"""
KKIA PAY TYPES MODULE
This module defines the types and data structures used in the Kkiapay payment gateway integration.
NOTE:This module is built to be flexible and extensible, allowing for easy addition of new features and configurations.
"""

import json
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from datetime import datetime
from typing import (
    Any, TypedDict, Optional, Dict
)


####
##     LOG LEVELs
#####
class LogLevel(str, Enum):
    """Log Levels"""

    DEBUG = 'debug'
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    CRITICAL = 'critical'


####
##      LOG FORMAT CHOICES
#####
class LogFormat(str, Enum):
    """Log Format choices."""

    PLAIN = 'plain'
    JSON = 'json'


####
##      BASE CONFIGURATION CLASS
#####
class BaseConfigModel(BaseModel):
    """Base class of all configuration models."""

    class Config:
        extra = 'forbid'        # Undefined fields are not allowed
        validate_all = True
        use_enum_values = True


####
##      LOGGING CONFIG MODEL CLASS
#####
class LoggingConfig(BaseConfigModel):
    """Logging Configuration Model"""

    enabled: bool = False
    level: LogLevel = LogLevel.INFO
    file: Optional[str] = None
    console: bool = True
    max_size: int = 10  # MB
    backups: int = 5
    compress: bool = True
    format: LogFormat = LogFormat.PLAIN
    rotate: bool = True


####
##      SUPPORTED COUNTRIES
#####
class Countries(str, Enum):
    """Supported Countries Choices."""

    TOGO = 'TG'
    BENIN = 'BJ'
    GHANA = 'GH'
    BURKINA = 'BF'
    IVORY_COAST = 'CI'


####
##      TRANSACTION CURRENCY CHOICES
#####
class Currency(str, Enum):
    """ Available choices of currency . """
    
    XOF = "XOF"  # CFA Franc BCEAO
    XAF = "XAF"  # CFA Franc BEAC
    EUR = "EUR"  # Euro
    USD = "USD"  # US Dollar
    GBP = "GBP"  # British Pound
    NGN = "NGN"  # Nigerian Naira
    GHS = "GHS"  # Ghanaian Cedi
    KES = "KES"  # Kenyan Shilling


####
##      CREDENTIALS MODEL
#####
class Credential(TypedDict):
    ''' Account Credentials Model. '''
    
    apikey : str                        # CINEPAY ACCOUNT APIKEY
    site_id : str                        # ACCOUNT SITE ID
  
  
####
##      CONFIGS BASE REPRESENTATION CLASS
#####
class Config(BaseConfigModel):
    """ The base class for all configs. """
    
    host : Optional[str] = None,                # HOST
    credentials : Credential                    # AUTH MODEL
    # channels : Optional[str] = Channels.ALL     # AVAILABLE PAYMENT CHANNELS
    # language : Optional[str] = Languages.FR     # LANGUAGE
    currency : Optional[str] = Currency.XOF     # TRANSACTION CURRENCY
    lock_phone_number : bool = False            # IF IT'S SET TO TRUE, CLIENT PHONE NUMBER WILL BE AUTOMATICALLY USED TOO FILL CHECKOUT PAGE.
    sandbox: bool = False                       # IF SET TO TRUE, SANDBOX MODE IS ENABLED
    raise_on_error : bool = False               # IF SET TO TRUE, RAISE IF EXCEPTION OCCURES 
    logging: LoggingConfig = Field(
        default_factory = LoggingConfig         # IF SET TO TRUE, LOGGING IS ENABLED
    )                      


####
##      CUSTOMER INFORMATION
#####
@dataclass
class CustomerInfo:
    """Customer informations."""

    phone_number: str = ""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    zip_code: Optional[str] = None
    state: Optional[str] = None
    id: Optional[str] = None


####
##      TRANSACTION STATUS
#####
class TransactionStatus(str, Enum):
    """Possible statues of a transaction."""

    PENDING = "pending"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    ERROR = "error"
    CANCELLED = "cancelled"
    REFUSED = "refused"
    DECLINED = "declined"
    EXPIRED = "expired"
    REFUNDED = "refunded"
    PROCESSING = "processing"
    INITIATED = "initiated"
    UNKNOWN = "unknown"
    COMPLETED = "completed"


####
##      TRANSACTION TYPES
#####
class TransactionType(str, Enum):
    """Supported Transaction Types."""

    PAYMENT = "payment"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    REFUND = "refund"
    TRANSFER = "transfer"


####
##      TRANSACTION DETAIL
#####
@dataclass
class TransactionDetail:
    """Standardized Transaction detail structure."""

    transaction_id: str
    amount: float
    currency: Currency
    status: TransactionStatus = TransactionStatus.PENDING
    # transaction_type: TransactionType = TransactionType.PAYMENT
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    customer: Optional[CustomerInfo] = None
    reference: Optional[str] = None
    description: Optional[str] = None
    callback_url: Optional[str] = None
    return_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_data: Dict[str, Any] = field(default_factory=dict)