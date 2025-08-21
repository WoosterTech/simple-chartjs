from pydantic_extra_types.color import Color

from src.simple_chartjs.base import LegendLabel


def test_legend_label_defaults():
    label = LegendLabel()
    assert label.box_width == 40
    assert label.padding == 10
    assert label.filter is None
    assert label.font_size == 12
    assert label.font_style == "normal"
    assert label.font_color == Color("#666")
    assert label.use_point_style is False


def test_legend_label_custom_values():
    label = LegendLabel(
        box_width=50,
        padding=20,
        filter="custom",
        font_size=16,
        font_style="italic",
        font_color="#123456",  # pyright: ignore[reportArgumentType]
        use_point_style=True,
    )
    assert label.box_width == 50
    assert label.padding == 20
    assert label.filter == "custom"
    assert label.font_size == 16
    assert label.font_style == "italic"
    assert label.font_color == Color("#123456")
    assert label.use_point_style is True


def test_legend_label_serialization_exclude_defaults():
    label = LegendLabel(font_color=Color("red"), use_point_style=True)
    data = label.model_dump(exclude_defaults=True)
    # Only non-default fields should be present
    assert "font_color" in data
    assert data["font_color"] == Color("red")
    assert "use_point_style" in data
    assert data["use_point_style"] is True
    # Default fields should be excluded
    assert "box_width" not in data
    assert "padding" not in data
    assert "font_size" not in data
    assert "font_style" not in data
    assert "filter" not in data
