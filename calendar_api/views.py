"""
Calendar Views.
"""

import os

from django.shortcuts import redirect
from django.http import JsonResponse
from django.views import View
from django.http import HttpResponseBadRequest

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

# Client configuration
GOOGLE_CLIENT_CONFIG = {
    "client_id":
    os.environ.get("CLIENT_ID"),
    "client_secret":
    os.environ.get("CLIENT_SECRET"),
    "project_id":
    "calendar-integration-387918",
    "auth_uri":
    "https://accounts.google.com/o/oauth2/auth",
    "token_uri":
    "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url":
    "https://www.googleapis.com/oauth2/v1/certs",
    "redirect_uris": [
        "http://localhost:8000/rest/v1/calendar/redirect/",
        "https://calendarintegration.parthsrivastav4.repl.co/rest/v1/calendar/redirect/"
    ]
}


class GoogleCalendarInitView(View):
    def get(self, request):
        # Create a Flow object using the client configuration and required scopes
        flow = Flow.from_client_config(
            {"installed": GOOGLE_CLIENT_CONFIG},
            scopes=[
                "https://www.googleapis.com/auth/calendar.events.readonly"
            ],
            redirect_uri=request.build_absolute_uri(
                "https://calendarintegration.parthsrivastav4.repl.co/rest/v1/calendar/redirect/"
            ),
        )

        # Generate the authorization URL and state for the OAuth flow
        authorization_url, state = flow.authorization_url(
            access_type="offline", include_granted_scopes="true")

        # Store the state in the session for later use
        request.session["google_auth_state"] = state

        # Redirect the user to the authorization URL to start the OAuth flow
        return redirect(authorization_url)


class GoogleCalendarRedirectView(View):
    def get(self, request):
        # Check if the 'code' parameter is present in the request
        if "code" not in request.GET:
            return HttpResponseBadRequest("Code parameter is missing.")

        # Retrieve the state from the session
        state = request.session.get("google_auth_state")
        if not state:
            return HttpResponseBadRequest("Invalid state.")

        # Create a Flow object using the client configuration and required scopes
        flow = Flow.from_client_config(
            {"installed": GOOGLE_CLIENT_CONFIG},
            scopes=[
                "https://www.googleapis.com/auth/calendar.events.readonly"
            ],
            redirect_uri=request.build_absolute_uri(
                "https://calendarintegration.parthsrivastav4.repl.co/rest/v1/calendar/redirect/"
            ),
        )

        # Fetch the access token using the authorization response and state
        flow.fetch_token(authorization_response=request.build_absolute_uri(),
                         state=state)

        # Get the credentials from the flow object
        credentials = flow.credentials

        # Save or use the credentials as needed
        # For example, you can save them in the database for future use

        # Use the credentials to build the Google Calendar API service
        service = build("calendar",
                        "v3",
                        credentials=credentials,
                        static_discovery=False)

        # Fetch a list of events from the user's primary calendar
        events = service.events().list(calendarId="primary").execute()

        # Return the events as a JSON response
        return JsonResponse(events)
