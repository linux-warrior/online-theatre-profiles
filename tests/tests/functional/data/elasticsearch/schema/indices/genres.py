from __future__ import annotations

from ..settings import settings_data

index_data: dict = {
    'settings': settings_data,
    'mappings': {
        'dynamic': 'strict',
        'properties': {
            'id': {
                'type': 'keyword',
            },
            'name': {
                'type': 'keyword',
            },
        },
    },
}
