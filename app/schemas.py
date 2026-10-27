from pydantic import BaseModel, Field

class HouseFeatures(BaseModel):
    MedInc: float = Field(gt=0, description="Median income of neighborhood")
    HouseAge: float = Field(gt=0, description="House age of neighborhood")
    AveRooms: float = Field(gt=0, description="Average rooms of neighborhood")
    AveBedrms: float = Field(gt=0, description="Average bedrooms of neighborhood")
    Population: float = Field(gt=0, description="Population of neighborhood")
    AveOccup: float = Field(gt=0, description="Average occupancy of neighborhood")
    Latitude: float = Field(description="Latitude of neighborhood")
    Longitude: float = Field(description="Longitude of neighborhood")