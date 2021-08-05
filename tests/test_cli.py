from typing import Tuple
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture

from wanikani_notifier.cli import cli
from wanikani_notifier.cli import notify, available_assignments_now, all_available_assignments
from wanikani_notifier.wanikani import AvailableAssignments


###################
#     Fixtures    #
###################


@pytest.fixture
def mocked_wk_client(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("wanikani_notifier.cli.WaniKaniClient")


@pytest.fixture
def mocked_notifier_creator(mocker: MockerFixture):
    return mocker.patch("wanikani_notifier.notifiers.notifier.factory.create")


@pytest.fixture
def mocked_get_available_assignments(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("wanikani_notifier.cli.get_available_assignments")


@pytest.fixture
def mocked_available_assignments_now(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("wanikani_notifier.cli.available_assignments_now")


@pytest.fixture
def mocked_all_available_assignments(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("wanikani_notifier.cli.all_available_assignments")


###################
#    CLI tests    #
###################

class TestCli:
    def test_cli_no_commands_no_options(self):
        runner = CliRunner()
        result = runner.invoke(cli, "")

        assert "Usage" in result.stdout

    def test_cli_no_commands_with_wanikani_token(self, mocked_wk_client):
        runner = CliRunner()
        result = runner.invoke(cli, "--wanikani __TOKEN__")

        assert result.exit_code == 2

    def test_cli_available_assignments_now_without_options(self, mocked_wk_client):
        runner = CliRunner()
        result = runner.invoke(cli, "--wanikani __TOKEN__ available_assignments_now")

        assert result.exit_code == 0

    def test_cli_available_assignments_now_with_options(self, mocked_wk_client):
        runner = CliRunner()
        result = runner.invoke(cli, "--wanikani __TOKEN__ available_assignments_now --since 1")

        assert result.exit_code == 0

    def test_cli_available_assigments(self, mocked_wk_client):
        runner = CliRunner()
        result = runner.invoke(cli, "--wanikani __TOKEN__ all_available_assignments")

        assert result.exit_code == 0

    def test_cli_notify_no_notifiers(self, mocked_notifier_creator):
        runner = CliRunner()
        result = runner.invoke(cli, "--wanikani __TOKEN__ notify")

        assert result.exit_code == 0
        mocked_notifier_creator.assert_not_called()

    def test_cli_notify_all_notifiers(self, mocked_notifier_creator):
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
#  CLI use cases  #
###################
class TestUseCases:
    @staticmethod
    @pytest.fixture(params=[True, False], ids=["stop", "continue"])
    def notify_new_and_all_use_case(request) -> Tuple[str, bool]:
        return (
            """
            --wanikani __TOKEN__ {}
            available_assignments_now
            all_available_assignments
            notify --console
            """.format(("--continue-even-empty" if not request.param else "")),
            request.param
        )

    @pytest.mark.parametrize("now_available,all_available", [
        pytest.param(None, None, id="none"),
        pytest.param("__MESSAGE__", None, id="some_new_none_all"),
        pytest.param(None, "__MESSAGE__", id="none_new_some_all"),
        pytest.param("__MESSAGE__", "__MESSAGE__", id="some_new_some_all"),
    ])
    def test_cli_notify_new_and_all_use_case(self,
                                             mocked_notifier_creator,
                                             mocked_available_assignments_now,
                                             mocked_all_available_assignments,
                                             notify_new_and_all_use_case,
                                             now_available,
                                             all_available
                                             ):
        mocked_available_assignments_now.return_value = now_available
        mocked_all_available_assignments.return_value = all_available
        if not notify_new_and_all_use_case[1]:
            expect_notify = any((now_available, all_available))
        else:
            expect_notify = all((now_available, all_available))

        runner = CliRunner()
        result = runner.invoke(cli, notify_new_and_all_use_case[0])

        assert result.exit_code == 0
        assert mocked_notifier_creator.call_count == 1
        assert mocked_available_assignments_now.call_count == 1
        assert mocked_all_available_assignments.call_count == 1
        assert mocked_notifier_creator.return_value.notify.call_count == (1 if expect_notify else 0)


###################
#  Command tests  #
###################
class TestCommands:
    @pytest.mark.parametrize("assignments,min_assignments,expected_message",
                             [
                                 pytest.param(AvailableAssignments(0, 2),
                                              1,
                                              "2 lessons are now available!",
                                              id="lessons_only"),
                                 pytest.param(AvailableAssignments(3, 0),
                                              1,
                                              "3 reviews are now available!",
                                              id="reviews_only"),
                                 pytest.param(AvailableAssignments(4, 5),
                                              1,
                                              "5 lessons and 4 reviews are now available!",
                                              id="lessons_and_reviews"),
                                 pytest.param(AvailableAssignments(4, 5),
                                              10,
                                              None,
                                              id="lessons_and_reviews_below_min"),
                                 pytest.param(AvailableAssignments(4, 5),
                                              9,
                                              "5 lessons and 4 reviews are now available!",
                                              id="lessons_and_reviews_equal_min"),
                                 pytest.param(AvailableAssignments(0, 0),
                                              1,
                                              None,
                                              id="none")
                             ]
                             )
    def test_available_assignments_now(self, mocked_get_available_assignments,
                                       assignments, min_assignments, expected_message):
        mocked_get_available_assignments.return_value = assignments
        message = available_assignments_now(None, 0, min_assignments)

        assert message == expected_message

    @pytest.mark.parametrize("assignments,expected_message",
                             [
                                 pytest.param(AvailableAssignments(0, 2),
                                              "In total, there are 2 lessons to do.",
                                              id="lessons_only"),
                                 pytest.param(AvailableAssignments(3, 0),
                                              "In total, there are 3 reviews to do.",
                                              id="reviews_only"),
                                 pytest.param(AvailableAssignments(4, 5),
                                              "In total, there are 5 lessons and 4 reviews to do.",
                                              id="lessons_and_reviews"),
                                 pytest.param(AvailableAssignments(0, 0),
                                              None,
                                              id="none")
                             ]
                             )
    def test_all_available_assignments(self, mocked_get_available_assignments, assignments, expected_message):
        mocked_get_available_assignments.return_value = assignments
        message = all_available_assignments(None)

        assert message == expected_message

    def test_notify_no_notifiers_no_messages(self, mocked_notifier_creator):
        notify("", [])

        assert mocked_notifier_creator.call_count == 0
        assert mocked_notifier_creator.return_value.notify.call_count == 0

    def test_notify_no_notifiers_some_messages(self, mocked_notifier_creator):
        notify("some message", [])

        assert mocked_notifier_creator.call_count == 0
        assert mocked_notifier_creator.return_value.notify.call_count == 0

    def test_notify_all_notifiers_no_messages(self, mocked_notifier_creator):
        notify("", [mocked_notifier_creator(), mocked_notifier_creator(), mocked_notifier_creator()])

        assert mocked_notifier_creator.call_count == 3
        assert mocked_notifier_creator.return_value.notify.call_count == 0

    def test_notify_all_notifiers_some_messages(self, mocked_notifier_creator):
        notifiers = [mocked_notifier_creator(), mocked_notifier_creator(), mocked_notifier_creator()]

        notify("some message", notifiers)

        assert mocked_notifier_creator.call_count == 3
        assert mocked_notifier_creator.return_value.notify.call_count == 3
