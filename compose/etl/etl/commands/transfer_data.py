from __future__ import annotations

import sys
import time
from pathlib import Path

import elasticsearch

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from etl.extract import (  # noqa: E402
    FilmWorksExtractor,
    GenresExtractor,
    PersonsExtractor,
)
from etl.load import ElasticsearchLoader  # noqa: E402
from etl.pipelines import (  # noqa: E402
    ETLPipeline,
    FilmsTransformExecutor,
    GenresTransformExecutor,
    PersonsTransformExecutor,
)
from etl.settings import settings  # noqa: E402
from etl.state import JsonFileStorage  # noqa: E402
from etl.transform import (  # noqa: E402
    Document,
    Film,
    Genre,
    Person,
)
from etl.utils import (  # noqa: E402
    setup_logging,
    load_index_file,
)


def main() -> None:
    setup_logging(file_path=BASE_DIR / 'logs' / 'transfer_data.log')
    postgresql_connection_params = settings.postgresql.connection_params
    schema_dir = BASE_DIR / 'schema'

    storage = JsonFileStorage(file_path=BASE_DIR / 'data' / 'state.json')
    state = storage.load()

    with (
        elasticsearch.Elasticsearch(settings.elasticsearch.url) as elasticsearch_client,
    ):
        etl_pipelines: list[ETLPipeline[Document]] = [
            ETLPipeline[Film](
                extractor=FilmWorksExtractor(connection_params=postgresql_connection_params),
                extractor_state=state.extractors.film_works,
                transform_executor=FilmsTransformExecutor(),
                loader=ElasticsearchLoader[Film](
                    client=elasticsearch_client,
                    index_name='films',
                    index_data=load_index_file(schema_dir / 'films.json'),
                ),
            ),

            ETLPipeline[Genre](
                extractor=GenresExtractor(connection_params=postgresql_connection_params),
                extractor_state=state.extractors.genres,
                transform_executor=GenresTransformExecutor(),
                loader=ElasticsearchLoader[Genre](
                    client=elasticsearch_client,
                    index_name='genres',
                    index_data=load_index_file(schema_dir / 'genres.json'),
                ),
            ),

            ETLPipeline[Person](
                extractor=PersonsExtractor(connection_params=postgresql_connection_params),
                extractor_state=state.extractors.persons,
                transform_executor=PersonsTransformExecutor(),
                loader=ElasticsearchLoader[Person](
                    client=elasticsearch_client,
                    index_name='persons',
                    index_data=load_index_file(schema_dir / 'persons.json'),
                ),
            )
        ]

        while True:
            for etl_pipeline in etl_pipelines:
                while True:
                    documents_transform_result = etl_pipeline.transfer_data()

                    if not documents_transform_result.documents:
                        break

                    storage.save(state)

            time.sleep(10)


if __name__ == '__main__':
    main()
