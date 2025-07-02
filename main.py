from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from pdfrw import PdfReader, PdfWriter, PdfDict
import io

app = FastAPI(
    title="USCG PDF Form Filler",
    description="Receives JSON data, fills the CG-1258 form, and returns a PDF.",
    version="1.0.0"
)

# Pydantic models representing incoming JSON structure
class Coordinates(BaseModel):
    longitude: float
    latitude: float

class Location(BaseModel):
    fullAddress: str
    country: str
    city: str
    state: str | None
    coordinates: Coordinates

class VesselInfo(BaseModel):
    hullNumber: str
    vesselLength: float
    horsepower: int
    make: str
    year: int
    model: str
    location: Location
    fuelType: str
    vesselType: str
    engineType: str | None
    hullMaterial: str | None

class USCGInfo(BaseModel):
    hailingPort: str
    ssn: str
    newVesselName: str
    uscgOfficialNumber: str

class USARegistrationInfo(BaseModel):
    country: str
    city: str
    state: str
    street: str
    apartment: str | None
    postalCode: str
    stateTitle: str
    stateRegistration: str
    uscg: USCGInfo

class BuyerInfo(BaseModel):
    name: str
    email: str
    phone: str
    fullAddress: str
    country: str
    city: str
    state: str
    zipCode: str

class DealerInfo(BaseModel):
    name: str
    city: str
    state: str | None
    zipCode: str
    ein: str | None

class InputData(BaseModel):
    vesselInfo: VesselInfo
    usaRegistrationInfo: USARegistrationInfo
    buyerInfo: BuyerInfo
    coBuyerInfo: dict | None
    dealerInfo: DealerInfo
    closingDate: str
    purchasePrice: float
    taxCollected: float
    previousOwnerName: str | None

# Mapping from PDF field names to JSON attribute paths
FIELD_MAP = {
    "txtVesselName": "usaRegistrationInfo.uscg.newVesselName",
    "txtOfficialNo": "usaRegistrationInfo.uscg.uscgOfficialNumber",
    "txtHullID": "vesselInfo.hullNumber",
    "txtHailingPort": "usaRegistrationInfo.uscg.hailingPort",
    "txtManagingOwner": "buyerInfo.name",
    "txtEmail": "buyerInfo.email",
    "txtPhoneNo": "buyerInfo.phone",
    "txtSSN": "usaRegistrationInfo.uscg.ssn",
    "txtPhysicalAddress": "buyerInfo.fullAddress",
    "txtMailingAddress": "usaRegistrationInfo.street",
    "txtCity": "usaRegistrationInfo.city",
    "txtState": "usaRegistrationInfo.state",
    "txtPostalCode": "usaRegistrationInfo.postalCode"
}

@app.post("/fill-form", summary="Fill USCG CG-1258 PDF form")
async def fill_form(data: InputData):
    try:
        # Load the PDF template
        template_pdf = PdfReader("uscg.pdf")
        annotations = template_pdf.pages[0]['/Annots']

        # Iterate over the annotations (form fields) and set values
        for annotation in annotations:
            if annotation['/Subtype'] == '/Widget' and annotation.get('/T'):
                field_name = annotation['/T'][1:-1]  # strip parentheses
                if field_name in FIELD_MAP:
                    # Resolve the attribute path
                    attr_path = FIELD_MAP[field_name].split('.')
                    value = data
                    for attr in attr_path:
                        value = getattr(value, attr)
                    # Set the field value
                    annotation.update(
                        PdfDict(V='{}'.format(value), AP=None)
                    )
        # Write filled PDF to memory
        output_stream = io.BytesIO()
        PdfWriter().write(output_stream, template_pdf)
        output_stream.seek(0)

        # Return as downloadable PDF
        return StreamingResponse(
            output_stream,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=filled_cg1258.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# For running via `uvicorn main:app --reload`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)