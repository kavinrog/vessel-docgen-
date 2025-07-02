from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
from PyPDF2 import PdfReader, PdfWriter

app = FastAPI()

PDF_TEMPLATE_PATH = "uscg.pdf"
FILLED_PDF_PATH = "filled_uscg.pdf"

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
    return {
        'txtVesselName': data.usaRegistrationInfo.uscg.newVesselName,
        'txtOfficialNo': data.usaRegistrationInfo.uscg.uscgOfficialNumber,
        'txtHullID': data.vesselInfo.hullNumber,
        'txtHailingPort': data.usaRegistrationInfo.uscg.hailingPort,
        'txtManagingOwner': data.buyerInfo.name,
        'txtEmail': data.buyerInfo.email,
        'txtPhoneNo': data.buyerInfo.phone,
        'txtSSN': data.usaRegistrationInfo.uscg.ssn,
        'txtPhysicalAddress': data.buyerInfo.fullAddress,
        'txtLength': str(data.vesselInfo.vesselLength),
        'txtDescribe': data.vesselInfo.hullMaterial or '',
        'txtIN': str(data.vesselInfo.year),
        'txtAT': f"{data.vesselInfo.location.city}, {data.vesselInfo.location.country}"
    }

def fill_pdf(input_pdf_path, output_pdf_path, field_data):
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.update_page_form_field_values(writer.pages[0], field_data)

    # Flatten the form (makes filled values permanent)
    for j in range(len(writer.pages)):
        writer.pages[j].compress_content_streams()

    with open(output_pdf_path, "wb") as f:
        writer.write(f)

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
