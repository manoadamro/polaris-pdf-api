from behave.model import Feature, Scenario, Step
from behave.runner import Context
from helpers.jwt_helper import get_system_token
from reporting import init_report_portal


def before_all(context: Context) -> None:
    init_report_portal(context)


def before_feature(context: Context, feature: Feature) -> None:
    context.feature_id = context.behave_integration_service.before_feature(feature)


def before_scenario(context: Context, scenario: Scenario) -> None:
    context.scenario_id = context.behave_integration_service.before_scenario(
        scenario, feature_id=context.feature_id
    )
    if not hasattr(context, "system_jwt"):
        context.system_jwt = get_system_token()


def before_step(context: Context, step: Step) -> None:
    context.step_id = context.behave_integration_service.before_step(
        step, scenario_id=context.scenario_id
    )


def after_step(context: Context, step: Step) -> None:
    context.behave_integration_service.after_step(step, step_id=context.step_id)


def after_scenario(context: Context, scenario: Scenario) -> None:
    context.behave_integration_service.after_scenario(
        scenario, scenario_id=context.scenario_id
    )


def after_feature(context: Context, feature: Feature) -> None:
    context.behave_integration_service.after_feature(
        feature, feature_id=context.feature_id
    )


def after_all(context: Context) -> None:
    context.behave_integration_service.after_all(launch_id=context.launch_id)
