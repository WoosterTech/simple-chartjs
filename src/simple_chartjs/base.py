import abc
import enum
from collections.abc import Callable
from decimal import Decimal
from enum import auto as autoenum
from typing import Annotated, Any, Generic, TypeVar, override

from attrmagic import ClassBase, SimpleDict, SimpleListRoot
from caseconverter.camel import camelcase
from pydantic import AliasChoices, AliasGenerator, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_extra_types.color import Color

# class ChartType(BaseModel):
#     attribute: str

# class ChartTypes(ChartType, enum.Enum):
#     LINE = ChartType(attribute="line")


class ChartType(enum.StrEnum):
    @override
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[str]) -> str:
        """
        Return the camel-case version of the enum name.
        """
        return camelcase(name)

    LINE = autoenum()
    BAR = autoenum()
    PIE = autoenum()
    DOUGHNUT = autoenum()
    RADAR = autoenum()
    POLAR_AREA = autoenum()
    HORIZONTAL_BAR = autoenum()
    MIXED = "bar"
    BUBBLE = autoenum()


class Position(enum.StrEnum):
    TOP = "top"
    LEFT = "left"
    BOTTOM = "bottom"
    RIGHT = "right"


def create_alias_choices(field_name: str) -> AliasChoices:
    return AliasChoices(field_name, to_camel(field_name))


class General(ClassBase, abc.ABC):  # pyright: ignore[reportUnsafeMultipleInheritance]
    model_config: ConfigDict = ConfigDict(  # pyright: ignore[reportIncompatibleVariableOverride]
        alias_generator=AliasGenerator(
            validation_alias=lambda x: create_alias_choices(x),
            serialization_alias=lambda x: to_camel(x),
        )
    )

    def to_json(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        return self.model_dump(mode="json", exclude_defaults=True, by_alias=True)


class Title(General):
    text: str = "My Chart"
    display: bool = True
    position: Position = Position.TOP
    padding: int = 10


class Layout(General):
    padding: int = 0


_T = TypeVar("_T")


class LegendLabel(General):
    box_width: int = 40
    padding: int = 10
    filter: str | None = None
    font_size: int = 12
    font_style: str = "normal"
    font_color: Color = Color("#666")
    use_point_style: bool = False

    # @field_serializer(
    #     "box_width", "padding", "font_size", "font_style", "font_color", return_type=_T | None
    # )
    # def default_to_none(self, value: _T, info: FieldSerializationInfo) -> _T | None:
    #     cls = self.__class__
    #     field_info = cls.model_fields[info.field_name]
    #     field_default = field_info.default  # pyright: ignore[reportAny]
    #     field_type = field_info.annotation  # pyright: ignore[reportAny]
    #     if field_type is None:
    #         raise TypeError(f"Field '{info.field_name}' must have a type annotation.")
    #     if field_default is None or not isinstance(field_default, field_type):
    #         msg = f"Field '{info.field_name}' must have an {field_type} default value, not {field_default}."
    #         raise TypeError(msg)

    #     if value == field_default:
    #         return None
    #     return value


class Legend(General):
    display: bool = True
    position: Position = Position.TOP
    full_width: bool = True
    reverse: bool = False
    labels: str = "default"


class DefaultColor(Color, enum.Enum):
    pass


_BaseT = TypeVar("_BaseT")


class DatasetData(SimpleListRoot[_BaseT], Generic[_BaseT]):
    pass


class PrimitiveData(DatasetData[float | Decimal]):
    pass


class ArrayData(DatasetData[tuple[int, float | Decimal | None]]):
    pass


class DataObject(ClassBase):
    x: float | Decimal | str
    y: float | Decimal | None


class ObjectData(DatasetData[DataObject]):
    pass


class GenericObjectData(DatasetData[dict[str, Any]]):  # pyright: ignore[reportExplicitAny]
    pass


class Dataset(General):
    label: str | None = None
    border_color: Color = Color((0, 0, 0, 0.1))
    border_cap_style: str = "butt"
    background_color: Color = Color((0, 0, 0, 0.1))
    border_dash: list[int] = []
    border_dash_offset: float = 0.0
    data: PrimitiveData | ArrayData | ObjectData | GenericObjectData
    fill: bool | None = None
    tension: Decimal = Decimal("0")


class Datasets(SimpleListRoot[Dataset]):
    pass


class Data(General):
    datasets: Datasets
    labels: list[str] | None = None


class Plugins(SimpleDict[str, Legend | Title]):
    pass


class Options(General):
    responsive: bool = True
    maintain_aspect_ratio: bool = True
    aspect_ratio: Decimal = Decimal("2")
    on_resize: Callable[..., None] | None = None
    resize_delay: Annotated[int, Field(description="Delay in milliseconds before resizing")] = 0
    plugins: Plugins


class Defaults(General):
    background_color: Color = Color((0, 0, 0, 0.1))
    border_color: Color = Color((0, 0, 0, 0.1))
    color: Annotated[Color, Field(description="Font color")] = Color("#666")


class BaseChart(ClassBase):  # pyright: ignore[reportUnsafeMultipleInheritance]
    type: ChartType = ChartType.BAR
    data: Data
    options: Options | None = None

    def get_datasets(self) -> Datasets:
        return self.data.datasets


if __name__ == "__main__":
    from rich.pretty import pprint
    # print(ChartType.POLAR_AREA)

    # legend_label = LegendLabel(font_color="red", use_point_style=True)  # pyright: ignore[reportArgumentType]

    # print(legend_label.font_color)

    # print(legend_label.model_dump(exclude_defaults=True))

    class DefaultDataset(Dataset):  # pyright: ignore[reportUninitializedInstanceVariable]
        fill: bool | None = False
        tension: Decimal = Decimal("0.1")

    datasets = Datasets.empty()

    datasets.append(
        DefaultDataset(
            label="Anxiety",
            data=PrimitiveData.model_validate([0, 1, 2, 3]),
            border_color="red",  # pyright: ignore[reportArgumentType]
        )
    )
    datasets.append(
        DefaultDataset(
            label="Energy",
            data=PrimitiveData.model_validate([5, 6, 7, 8]),
            border_color="blue",  # pyright: ignore[reportArgumentType]
        )
    )
    plugins = {
        "legend": Legend(position=Position.TOP),
        "title": Title(display=True, text="Test Chart"),
    }
    options = Options(responsive=True, plugins=Plugins.model_validate(plugins))

    # rprint(options.model_dump_json(indent=2))

    test_chart = BaseChart(
        type=ChartType.LINE,
        data=Data(datasets=datasets, labels=["0", "1", "2", "3"]),
        options=options,
    )

    pprint(test_chart.model_dump(exclude_defaults=True, mode="json", by_alias=True))

    datasets_dict = {
        "Anxiety": [{"date": "2025-08-11", "value": 2}, {"date": "2025-08-11", "value": 6}],
        "Energy": [{"date": "2025-08-11", "value": 5}, {"date": "2025-08-11", "value": 91}],
    }
