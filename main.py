from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import tempfile
import shutil
import os
from pdfrw import PdfReader, PdfWriter, PageMerge
from pdfrw import PdfDict, PdfName, PdfObject

app = FastAPI()

PDF_TEMPLATE_PATH = "vessel-docgen-/uscg.pdf"
FILLED_PDF_PATH = "vessel-docgen-/filled_uscg.pdf"

class Coordinates(BaseModel):
    longitude: float
    latitude: float

class Location(BaseModel):
    fullAddress: str
    country: str
    city: str
    state: Optional[str]
    coordinates: Coordinates

class VesselInfo(BaseModel):
    hullNumber: str
    vesselLength: float
    horsepower: float
    make: str
    year: int
    model: str
    location: Location
    fuelType: str
    vesselType: str
    engineType: Optional[str]
    hullMaterial: Optional[str]

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
    apartment: Optional[str]
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
    state: Optional[str]
    zipCode: str
    ein: Optional[str]

class RequestModel(BaseModel):
    vesselInfo: VesselInfo
    usaRegistrationInfo: USARegistrationInfo
    buyerInfo: BuyerInfo
    coBuyerInfo: Optional[dict]
    dealerInfo: DealerInfo
    closingDate: str
    purchasePrice: float
    taxCollected: float
    previousOwnerName: Optional[str]

def map_fields(data: RequestModel):
    annotations = {
        'txtVesselName[0]': data.usaRegistrationInfo.uscg.newVesselName,
        'txtOfficialNo[0]': data.usaRegistrationInfo.uscg.uscgOfficialNumber,
        'txtHullID[0]': data.vesselInfo.hullNumber,
        'txtHailingPort[0]': data.usaRegistrationInfo.uscg.hailingPort,
        'txtManagingOwner[0]': data.buyerInfo.name,
        'txtEmail[0]': data.buyerInfo.email,
        'txtPhoneNo[0]': data.buyerInfo.phone,
        'txtSSN[0]': data.usaRegistrationInfo.uscg.ssn,
        'txtPhysicalAddress[0]': data.buyerInfo.fullAddress,
        'txtLength[0]': str(data.vesselInfo.vesselLength),
        'txtDescribe[0]': data.vesselInfo.hullMaterial or '',
        'txtIN[0]': str(data.vesselInfo.year),
        'txtAT[0]': f"{data.vesselInfo.location.city}, {data.vesselInfo.location.country}"
    }
    return annotations

def fill_pdf(input_pdf_path, output_pdf_path, field_data):
    template_pdf = PdfReader(input_pdf_path)
    for page in template_pdf.pages:
        annotations = page.Annots
        if annotations:
            for annotation in annotations:
                if annotation.Subtype == PdfName.Widget and annotation.T:
                    key = annotation.T.to_unicode()
                    if key in field_data:
                        annotation.V = PdfObject(str(field_data[key]))
                        annotation.AP = PdfDict()
    PdfWriter(output_pdf_path, trailer=template_pdf).write()

@app.post("/fill-pdf")
def fill_form(data: RequestModel):
    try:
        field_data = map_fields(data)
        fill_pdf(PDF_TEMPLATE_PATH, FILLED_PDF_PATH, field_data)
        return FileResponse(FILLED_PDF_PATH, media_type='application/pdf', filename='filled_uscg.pdf')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/")
def read_root():
    return {"message": "Go to /docs to use the PDF fill API"}