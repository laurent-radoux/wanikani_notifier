from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from wanikani_notifier.cli import process_all, processor, generator


@pytest.fixture
def mocked_wk_client(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("wanikani_notifier.cli.WaniKaniClient")


@pytest.fixture
def mocked_processor_counter(mocker: MockerFixture):
    return mocker.Mock()


@pytest.fixture
def mocked_consumer(mocked_processor_counter):
    @processor
    def message_consumer(_, message_stream):
        mocked_processor_counter()
        yield

    return message_consumer()


@pytest.fixture
def mocked_processor(mocked_processor_counter):
    @processor
    def message_processor(_, message_stream):
        mocked_processor_counter()
        yield from message_stream

    return message_processor()


@pytest.fixture
def mocked_generator(mocked_processor_counter):
    @generator
    def message_generator(*unused):
        mocked_processor_counter()
        yield "new message"

    return message_generator()


@pytest.mark.parametrize("stop_if_empty", [pytest.param(True, id="stop"), pytest.param(False, id="continue")])
def test_process_all_no_processors(mocked_wk_client, mocked_processor_counter, stop_if_empty):
    process_all([], "__TOKEN__", stop_if_empty)

    mocked_wk_client.assert_called_once()
    mocked_processor_counter.assert_not_called()


@pytest.mark.parametrize("stop_if_empty", [pytest.param(True, id="stop"), pytest.param(False, id="continue")])
def test_process_all_with_processors_no_generators(mocked_wk_client,
                                                   mocked_processor_counter,
                                                   mocked_consumer,
                                                   stop_if_empty
                                                   ):
    processors = [mocked_consumer, mocked_consumer, mocked_consumer]
    process_all(processors, "__TOKEN__", stop_if_empty)

    mocked_wk_client.assert_called_once()
    mocked_processor_counter.assert_called_once()


@pytest.mark.parametrize("stop_if_empty", [pytest.param(True, id="stop"), pytest.param(False, id="continue")])
def test_process_all_no_processors_with_generators(mocked_wk_client,
                                                   mocked_processor_counter,
                                                   mocked_generator,
                                                   stop_if_empty
                                                   ):
    processors = [mocked_generator, mocked_generator, mocked_generator]
    process_all(processors, "__TOKEN__", stop_if_empty)

    mocked_wk_client.assert_called_once()
    assert mocked_processor_counter.call_count == len(processors)
