from pydantic import BaseModel, Field, ConfigDict


class TaskAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)  # Allow both alias and field name

    created_at: int | None = Field(None, alias="createdAt", description="Unix timestamp when task was created")
    completed_at: int | None = Field(None, alias="completedAt", description="Unix timestamp when task was completed")
    crossed_out_at: int | None = Field(None, alias="crossedOutAt", description="Unix timestamp when task was crossed out")
    start_at: int | None = Field(None, alias="startAt", description="Unix timestamp for scheduled start time")
    notify: str | None = Field(None, description="ISO 8601 duration for notification timing (e.g., PT5M)")
    duration: str | None = Field(None, description="ISO 8601 duration for task length (e.g., PT30M, PT1H)")
    repeat: str | None = Field(None, description="Recurrence rule in iCalendar RRULE or ISO 8601 duration format")
    start_rule: str | None = Field(None, alias="startRule", description="ISO 8601 duration offset for start time")
    due_day_part: str | None = Field(None, alias="dueDayPart", description="Part of day for due date (e.g., M for morning)")
    flags: str | None = Field(None, description="Single-character flags combined (I=Important, U=Urgent, D=Delegated)")
    points: float | None = Field(None, description="Point value/score for task")
    points_updated_at: int | None = Field(None, alias="pointsUpdatedAt", description="Unix timestamp when points were updated")
    victory_value: float | None = Field(None, alias="victoryValue", description="Victory/completion value")
    streak_count: int | None = Field(None, alias="streakCount", description="Number of consecutive completions")
    references: list[str] | None = Field(None, description="Array of UUIDs for referenced notes/tasks")
