from fastapi import APIRouter, BackgroundTasks, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from app.services.processing import process_sms_workflow

router = APIRouter()

@router.post("/sms")
async def handle_sms(request: Request, background_tasks: BackgroundTasks):
    """
    Twilio Webhook endpoint for receiving SMS.
    Returns a 200 OK with empty TwiML immediately.
    Schedules the actual processing to run in the background.
    """
    form_data = await request.form()
    
    from_number = form_data.get("From", "")
    sms_body = form_data.get("Body", "")
    
    # Enqueue the background task
    background_tasks.add_task(process_sms_workflow, from_number, sms_body)
    
    # Return 200 OK with TwiML immediately to prevent Twilio timeout
    resp = MessagingResponse()
    # We do not append any message here so we don't automatically text back.
    # We just want to acknowledge receipt.
    return Response(content=str(resp), media_type="application/xml")
