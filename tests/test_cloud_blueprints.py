import json
from pathlib import Path

ADF_BLUEPRINT = Path("cloud/adf/pipeline-blueprint.json")
DATABRICKS_BLUEPRINT = Path("cloud/databricks/job-blueprint.json")


def test_adf_blueprint_contains_expected_pipeline_activities() -> None:
    blueprint = _read_json(ADF_BLUEPRINT)
    activity_names = {activity["name"] for activity in blueprint["activities"]}

    assert activity_names == {
        "IngestRawData",
        "BuildBronze",
        "BuildSilver",
        "BuildGold",
        "PublishRunSummary",
    }
    assert blueprint["parameters"]["raw_path"]["defaultValue"].startswith("abfss://")
    assert blueprint["schedule"]["frequency"] == "Day"


def test_adf_blueprint_orders_processing_layers() -> None:
    blueprint = _read_json(ADF_BLUEPRINT)
    activities = {activity["name"]: activity for activity in blueprint["activities"]}

    assert activities["BuildBronze"]["dependsOn"][0]["activity"] == "IngestRawData"
    assert activities["BuildSilver"]["dependsOn"][0]["activity"] == "BuildBronze"
    assert activities["BuildGold"]["dependsOn"][0]["activity"] == "BuildSilver"
    assert activities["PublishRunSummary"]["dependsOn"][0]["activity"] == "BuildGold"


def test_databricks_blueprint_targets_project_runtime() -> None:
    blueprint = _read_json(DATABRICKS_BLUEPRINT)

    assert blueprint["runtime"] == {
        "databricks_runtime": "16.4 LTS",
        "python": "3.12",
        "spark": "3.5.2",
    }


def test_databricks_blueprint_contains_expected_tasks() -> None:
    blueprint = _read_json(DATABRICKS_BLUEPRINT)
    tasks = {task["task_key"]: task for task in blueprint["tasks"]}

    assert set(tasks) == {"build_bronze", "build_silver", "build_gold"}
    assert tasks["build_bronze"]["python_wheel_task"]["entry_point"] == "airline-build-bronze"
    assert tasks["build_silver"]["python_wheel_task"]["entry_point"] == "airline-build-silver"
    assert tasks["build_gold"]["python_wheel_task"]["entry_point"] == "airline-build-gold"
    assert tasks["build_silver"]["depends_on"][0]["task_key"] == "build_bronze"
    assert tasks["build_gold"]["depends_on"][0]["task_key"] == "build_silver"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
