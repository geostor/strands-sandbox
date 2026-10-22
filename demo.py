import os

from strands import Agent
from strands.telemetry import StrandsTelemetry

from fake_shell import FakeShell

telemetry = StrandsTelemetry().setup_console_exporter()
if os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
    telemetry.setup_otlp_exporter()

model = None
if os.environ.get("OPENAI_API_KEY"):
    from strands.models.openai import OpenAIModel

    model = OpenAIModel(model_id=os.environ.get("OPENAI_MODEL", "gpt-5-mini"))

agent = Agent(model=model, sandbox=FakeShell(), trace_attributes={"sandbox": "fakeshell"})
agent("Look around this shell, write a short poem into poem.txt, then show me the file.")
