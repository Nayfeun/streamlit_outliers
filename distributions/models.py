from pydantic import BaseModel, Field
from typing import ClassVar
import pandas as pd


class Formula(BaseModel):
    METHODS: ClassVar[str] = ['MAD', 'IQR', 'SD', 'Adjusted MAD']
    adjusted_mad_weight: float = Field(default=0.0)
    mad_weight: float = Field(default=0.0)
    iqr_weight: float = Field(default=0.0)
    sd_weight: float = Field(default=0.0)
    adjusted_mad_constant: float = Field(default=0.0)
    mad_constant: float = Field(default=0.0)
    iqr_constant: float = Field(default=0.0)
    sd_constant: float = Field(default=0.0)


class Distribution(BaseModel):
    DISTRIBUTION_SHAPES: ClassVar[str] = ['normal', 'asymmetrical', 'bimodal', 'sharp', 'flat']
    OUTLIERS_SHAPES: ClassVar[str] = ['outlier_1_side_centered_extreme', 'outlier_1_side_centered_close',
                                      'outlier_1_side_dispersed_extreme', 'outlier_1_side_dispersed_close',
                                      'outlier_2_side_centered_extreme', 'outlier_2_side_centered_close',
                                      'outlier_2_side_dispersed_extreme', 'outlier_2_side_dispersed_close']
    data: pd.DataFrame = Field(default=None)
    distribution_shape: str = Field(default=None)
    distribution_size: int = Field(default=None)
    outliers_shape: str = Field(default=None)
    outliers_rate: float = Field(default=None)

    class Config:
        arbitrary_types_allowed = True
