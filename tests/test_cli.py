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
    def get_full_use_case_command(stop_if_empty: bool) -> str:
        return """
                --wanikani __TOKEN__ {}
                available_assignments_now
                all_available_assignments
                notify --console
                """.format(("--continue-even-empty" if not stop_if_empty else ""))

    @pytest.mark.parametrize("stop_if_empty", [pytest.param(True, id="stop"), pytest.param(False, id="continue"),
                                               pytest.param(False, id="continue2")])
    def test_cli_notify_new_none_available_then_all_none_available(self,
                                                                   mocked_notifier_creator,
                                                                   mocked_available_assignments_now,
                                                                   mocked_all_available_assignments,
                                                                   stop_if_empty
                                                                   ):
        mocked_available_assignments_now.return_value = None
        mocked_all_available_assignments.return_value = None

        runner = CliRunner()
        result = runner.invoke(cli, self.get_full_use_case_command(stop_if_empty))

        assert result.exit_code == 0
        assert mocked_notifier_creator.call_count == 1
        assert mocked_available_assignments_now.call_count == 1
        assert mocked_all_available_assignments.call_count == 1
        assert mocked_notifier_creator.return_value.notify.call_count == 0

    @pytest.mark.parametrize("stop_if_empty", [pytest.param(True, id="stop"), pytest.param(False, id="continue")])
    def test_cli_notify_new_none_available_then_all_some_available(self,
                                                                   mocked_notifier_creator,
                                                                   mocked_available_assignments_now,
                                                                   mocked_all_available_assignments,
                                                                   stop_if_empty
                                                                   ):
        mocked_available_assignments_now.return_value = None
        mocked_all_available_assignments.return_value = "__MESSAGE__"

        runner = CliRunner()
        result = runner.invoke(cli, self.get_full_use_case_command(stop_if_empty))

        assert result.exit_code == 0
        assert mocked_notifier_creator.call_count == 1
        assert mocked_available_assignments_now.call_count == 1
        assert mocked_all_available_assignments.call_count == 1
        assert mocked_notifier_creator.return_value.notify.call_count == (1 if not stop_if_empty else 0)

    @pytest.mark.parametrize("stop_if_empty", [pytest.param(True, id="stop"), pytest.param(False, id="continue")])
    def test_cli_notify_new_some_available_then_all_none_available(self,
                                                                   mocked_notifier_creator,
                                                                   mocked_available_assignments_now,
                                                                   mocked_all_available_assignments,
                                                                   stop_if_empty
                                                                   ):
        mocked_available_assignments_now.return_value = "__MESSAGE__"
        mocked_all_available_assignments.return_value = None

        runner = CliRunner()
        result = runner.invoke(cli, self.get_full_use_case_command(stop_if_empty))

        assert result.exit_code == 0
        assert mocked_notifier_creator.call_count == 1
        assert mocked_available_assignments_now.call_count == 1
        assert mocked_all_available_assignments.call_count == 1
        assert mocked_notifier_creator.return_value.notify.call_count == (1 if not stop_if_empty else 0)

    @pytest.mark.parametrize("stop_if_empty", [pytest.param(True, id="stop"), pytest.param(False, id="continue")])
    def test_cli_notify_new_some_available_then_all_some_available(self,
                                                                   mocked_notifier_creator,
                                                                   mocked_available_assignments_now,
                                                                   mocked_all_available_assignments,
                                                                   stop_if_empty
                                                                   ):
        mocked_available_assignments_now.return_value = "__MESSAGE__"
        mocked_all_available_assignments.return_value = "__MESSAGE__"

        runner = CliRunner()
        result = runner.invoke(cli, self.get_full_use_case_command(stop_if_empty))

        assert result.exit_code == 0
        assert mocked_notifier_creator.call_count == 1
        assert mocked_available_assignments_now.call_count == 1
        assert mocked_all_available_assignments.call_count == 1
        assert mocked_notifier_creator.return_value.notify.call_count == 1


###################
#  Command tests  #
###################
class TestCommands:
    def test_available_assignments_now(self, mocked_get_available_assignments):
        mocked_get_available_assignments.return_value = AvailableAssignments(1, 2)
        message = available_assignments_now(None, 0)

        assert message == "2 lessons and 1 reviews are now available!"

    def test_no_available_assignements_now(self, mocked_get_available_assignments):
        mocked_get_available_assignments.return_value = AvailableAssignments(0, 0)
        message = available_assignments_now(None, 0)

        assert message is None

    def test_available_assigments(self, mocked_get_available_assignments):
        mocked_get_available_assignments.return_value = AvailableAssignments(2, 1)
        message = all_available_assignments(None)

        assert message == "In total, there are 1 lessons and 2 reviews to do."

    def test_no_available_assignments(self, mocked_get_available_assignments):
        mocked_get_available_assignments.return_value = AvailableAssignments(0, 0)
        message = all_available_assignments(None)

        assert message is None

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
