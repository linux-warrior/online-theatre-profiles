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
            'title': {
                'type': 'text',
                'analyzer': 'ru_en',
                'fields': {
                    'raw': {
                        'type': 'keyword',
                    },
                },
            },
            'description': {
                'type': 'text',
                'analyzer': 'ru_en',
            },
            'rating': {
                'type': 'float',
            },
            'genres_names': {
                'type': 'keyword',
            },
            'directors_names': {
                'type': 'text',
                'analyzer': 'ru_en',
            },
            'actors_names': {
                'type': 'text',
                'analyzer': 'ru_en',
            },
            'writers_names': {
                'type': 'text',
                'analyzer': 'ru_en',
            },
            'genres': {
                'type': 'nested',
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
            'directors': {
                'type': 'nested',
                'dynamic': 'strict',
                'properties': {
                    'id': {
                        'type': 'keyword',
                    },
                    'full_name': {
                        'type': 'text',
                        'analyzer': 'ru_en',
                    },
                },
            },
            'actors': {
                'type': 'nested',
                'dynamic': 'strict',
                'properties': {
                    'id': {
                        'type': 'keyword',
                    },
                    'full_name': {
                        'type': 'text',
                        'analyzer': 'ru_en',
                    },
                },
            },
            'writers': {
                'type': 'nested',
                'dynamic': 'strict',
                'properties': {
                    'id': {
                        'type': 'keyword',
                    },
                    'full_name': {
                        'type': 'text',
                        'analyzer': 'ru_en',
                    },
                },
            },
        },
    },
}
