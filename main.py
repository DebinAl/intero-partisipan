from typing import Union, Annotated
from contextlib import asynccontextmanager
from fastapi import FastAPI, Header, Response
from mongoengine import *
import bson
from datetime import datetime
import json

@asynccontextmanager
async def lifespan(app: FastAPI):
    connect(host="mongodb+srv://iniUser:WjYh5RtjZbscH9wK@cluster0.0rsk1.mongodb.net/db_ventix?retryWrites=true&w=majority&appName=Cluster0")
    yield

app = FastAPI(lifespan=lifespan)


class EventCategories(EmbeddedDocument):  # Changed to EmbeddedDocument
    _id = ObjectIdField()
    type = StringField()
    price = IntField()
    stock = IntField()
    statusTicketCategories = BooleanField()


class Events(Document):
    title = StringField()
    date = DateTimeField()
    about = StringField()
    tagline = StringField()
    keyPoint = ListField(field=StringField(), default=[])  # Added default
    venueName = StringField()
    statusEvent = StringField()
    tickets = ListField(field=EmbeddedDocumentField(EventCategories), default=[])  # Fixed
    image = ObjectIdField()
    category = ObjectIdField()
    talent = ObjectIdField()
    createdAt = DateTimeField(default=datetime.utcnow)  # Auto-populate
    updatedAt = DateTimeField(default=datetime.utcnow)  # Auto-populate
    __v = IntField()

    meta = {
        'strict': False  # Ignore fields not defined in the model, such as __v
    }

class CheckoutEvents(Document):
    user_id = ObjectIdField(required=True)  # Added required=True
    event = ObjectIdField(required=True)
    payment_status = BooleanField(required=True)
    createdAt = DateTimeField(default=datetime.utcnow)  # Auto-populate
    updatedAt = DateTimeField(default=datetime.utcnow)


class User(Document):
    username = StringField(required=True)
    email = StringField(required=True)
    hashed_password = StringField(required=True)
    disabled = BooleanField(required=True)
    role = StringField(required=True)


@app.get("/participant")
def read_root():
    return {"Hello": "World"}


@app.post("/participant/checkout-event/{id}")
def checkout_event(id, user: Annotated[str | None, Header()] = None): #6744b64c213cd4f6afb497fd
    event = Events.objects(id=bson.ObjectId(id)).first()
    print(event)
    if not event:
        return Response(
                content=f"event doesnt exists",
                status_code=404
            )

    selected_user = User.objects(id=bson.ObjectId(user)).first()

    if not selected_user:
        return Response(
                content=f"user doesnt exists",
                status_code=404
            )
    
    result = CheckoutEvents(user_id=bson.ObjectId(user), event=bson.ObjectId(id), payment_status=False).save()
    return json.loads(result.to_json())


@app.get("/participant/get-event")
def get_event():
    return json.loads(Events.objects.to_json())


@app.get("/participant/get-event/{id}")
def get_event_by_id(id):
    event = Events.objects(id=bson.ObjectId(id)).first()

    if not event:
        return Response(
                content=f"event doesnt exists",
                status_code=404
            )
    
    return json.loads(event.to_json())


@app.get("/participant/get-dashboard")
def get_dashboard():
    return json.loads(CheckoutEvents.objects.to_json())


@app.get("/participant/get-dashboard/{id}")
def get_dashboard(id):
    checkout_event = CheckoutEvents.objects(id=bson.ObjectId(id)).first()

    if not checkout_event:
        return Response(
                content=f"checkout event doesnt exists",
                status_code=404
            )
    
    return json.loads(checkout_event.to_json())