# app/schemas/vote.py
from pydantic import BaseModel, field_validator


class VoteCreate(BaseModel):
    """
    Данные для создания/изменения голоса.
    Все поля опциональны — можно голосовать только по одной оси.
    Например: проголосовать за правдивость но не оценивать срочность.
    """
    is_true:      bool | None = None   # True=правда, False=фейк
    urgency:      int  | None = None   # 1–5
    impact:       int  | None = None   # 1–5
    inconvenience: int | None = None   # 1–5

    @field_validator("urgency", "impact", "inconvenience", mode="before")
    @classmethod
    def validate_scale(cls, v):
        if v is not None and not (1 <= v <= 5):
            raise ValueError("Оценка должна быть от 1 до 5")
        return v

    def is_empty(self) -> bool:
        """Проверяет что хотя бы одно поле заполнено."""
        return all(
            f is None for f in [self.is_true, self.urgency, self.impact, self.inconvenience]
        )


class VotePublic(BaseModel):
    """Публичные данные голоса."""
    entity_id:         int
    version:           int
    problem_entity_id: int
    user_entity_id:    int
    is_true:           bool | None
    urgency:           int  | None
    impact:            int  | None
    inconvenience:     int  | None
    weight:            float
    is_current:        bool

    model_config = {"from_attributes": True}


class VoteStats(BaseModel):
    """
    Агрегированная статистика голосов по проблеме.
    Показывается на странице проблемы.
    """
    total_votes:      int
    true_count:       int    # сколько проголосовали "правда"
    fake_count:       int    # сколько проголосовали "фейк"
    truth_score:      float  # взвешенный 0.0–1.0
    urgency_score:    float
    impact_score:     float
    inconvenience_score: float
    priority_score:   float