from typing import Any, Union

import os
from enum import Enum, EnumMeta
from datetime import datetime, timezone

from pynamodb.models import Model, GlobalSecondaryIndex
from pynamodb.indexes import AllProjection
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute, TTLAttribute

from libraries.exchanges.bitflyer import ProductCode, State


class EnumAttribute(UnicodeAttribute):
    def __init__(self, enum: EnumMeta, *args: Any, **kwargs: Any) -> None:
        self.enum = enum
        super().__init__(*args, **kwargs)

    def _serialize(self, value: Union[str, Enum, EnumMeta]) -> str:
        e = getattr(self.enum, value) if isinstance(value, str) else value
        return super().serialize(e.name)

    def serialize(self, value: Union[str, Enum, None]) -> str:
        if not isinstance(value, self.enum):
            raise TypeError(f'value must be an instance of `{self.enum.__name__}`')

        return self._serialize(value)

    def deserialize(self, value: str) -> Enum:
        return getattr(self.enum, value)


class ProductCodeIndex(GlobalSecondaryIndex):
    class Meta:
        projection = AllProjection()

    product_code = EnumAttribute(ProductCode, hash_key=True)
    timestamp = UTCDateTimeAttribute(range_key=True)


class TickerTable(Model):
    class Meta:
        table_name = os.environ.get('DDB_TABLE_NAME', 'Ticker')
        region = os.environ.get('AWS_REGION', 'ap-northeast-1')
        billing_mode = 'PAY_PER_REQUEST'

    tick_id = NumberAttribute(hash_key=True)
    product_code = EnumAttribute(ProductCode)
    state = EnumAttribute(State)
    timestamp = UTCDateTimeAttribute()
    best_bid = NumberAttribute()
    best_ask = NumberAttribute()
    best_bid_size = NumberAttribute()
    best_ask_size = NumberAttribute()
    total_bid_depth = NumberAttribute()
    total_ask_depth = NumberAttribute()
    market_bid_size = NumberAttribute()
    market_ask_size = NumberAttribute()
    ltp = NumberAttribute()
    volume = NumberAttribute()
    volume_by_product = NumberAttribute()

    product_code_index = ProductCodeIndex()
    ttl = TTLAttribute(default=datetime(9999, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc))
