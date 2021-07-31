from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture
from wanikani_notifier.wanikani import AvailableAssignments

from wanikani_notifier.cli import process_all, processor, generator, cli
from wanikani_notifier.cli import notify, available_assignments_now, all_available_assignments


###################
#     Fixtures    #
###################


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


@pytest.fixture
def mocked_notifier_creator(mocker: MockerFixture):
    return mocker.patch("wanikani_notifier.notifiers.notifier.factory.create")


@pytest.fixture
def mocked_get_available_assignments(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("wanikani_notifier.cli.get_available_assignments")


###################
# Processor tests #
###################


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


###################
#    CLI tests    #
###################


def test_cli_no_commands_no_options():
    runner = CliRunner()
    result = runner.invoke(cli, "")

    assert "Usage" in result.stdout


def test_cli_no_commands_with_wanikani_token(mocked_wk_client):
    runner = CliRunner()
    result = runner.invoke(cli, "--wanikani __TOKEN__")

    assert result.exit_code == 2


def test_cli_available_assignments_now_without_options(mocked_wk_client):
    runner = CliRunner()
    result = runner.invoke(cli, "--wanikani __TOKEN__ available_assignments_now")

    assert result.exit_code == 0


def test_cli_available_assignments_now_with_options(mocked_wk_client):
    runner = CliRunner()
    result = runner.invoke(cli, "--wanikani __TOKEN__ available_assignments_now --since 1")

    assert result.exit_code == 0


def test_cli_available_assigments(mocked_wk_client):
    runner = CliRunner()
    result = runner.invoke(cli, "--wanikani __TOKEN__ all_available_assignments")

    assert result.exit_code == 0


def test_cli_notify_no_notifiers(mocked_notifier_creator):
    runner = CliRunner()
    result = runner.invoke(cli, "--wanikani __TOKEN__ notify")

    assert result.exit_code == 0
    mocked_notifier_creator.assert_not_called()


def test_cli_notify_all_notifiers(mocked_notifier_creator):
    runner = CliRunner()
    result = runner.invoke(cli,
                           """
                           --wanikani __TOKEN__
                           notify --pushsafer __TOKEN__ --pushover __APP_TOKEN__ __USER_TOKEN__ --console
                           """
                           )

    assert result.exit_code == 0
    assert mocked_notifier_creator.call_count == 3


###################
#  Command tests  #
###################


def test_available_assignments_now(mocked_get_available_assignments):
    mocked_get_available_assignments.return_value = AvailableAssignments(1, 2)
    message = available_assignments_now(None, 0)

    assert message == "2 lessons and 1 reviews are now available!"


def test_no_available_assignements_now(mocked_get_available_assignments):
    mocked_get_available_assignments.return_value = AvailableAssignments(0, 0)
    message = available_assignments_now(None, 0)

    assert message is None


def test_available_assigments(mocked_get_available_assignments):
    mocked_get_available_assignments.return_value = AvailableAssignments(2, 1)
    message = all_available_assignments(None)

    assert message == "In total, there are 1 lessons and 2 reviews to do."


def test_no_available_assignments(mocked_get_available_assignments):
    mocked_get_available_assignments.return_value = AvailableAssignments(0, 0)
    message = all_available_assignments(None)

    assert message is None


def test_notify_no_notifiers_no_messages(mocked_notifier_creator):
    notify("", [])

    assert mocked_notifier_creator.call_count == 0
    assert mocked_notifier_creator.return_value.notify.call_count == 0


def test_notify_no_notifiers_some_messages(mocked_notifier_creator):
    notify("some message", [])

    assert mocked_notifier_creator.call_count == 0
    assert mocked_notifier_creator.return_value.notify.call_count == 0


def test_notify_all_notifiers_no_messages(mocked_notifier_creator):
    notify("", [mocked_notifier_creator(), mocked_notifier_creator(), mocked_notifier_creator()])

    assert mocked_notifier_creator.call_count == 3
    assert mocked_notifier_creator.return_value.notify.call_count == 0


def test_notify_all_notifiers_some_messages(mocked_notifier_creator):
    notifiers = [mocked_notifier_creator(), mocked_notifier_creator(), mocked_notifier_creator()]

    notify("some message", notifiers)

    assert mocked_notifier_creator.call_count == 3
    assert mocked_notifier_creator.return_value.notify.call_count == 3
