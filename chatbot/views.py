
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
    throttle_classes,
)

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import UserRateThrottle

from .models import ChatMessage
from .serializers import ChatMessageSerializer

# Import AI service
from .ai_service import generate_ai_response


# ---------------------------------
# CHAT API RATE LIMITING
# ---------------------------------

class ChatRateThrottle(UserRateThrottle):
    scope = "chat"


# ---------------------------------
# CUSTOMER CHAT API
# ---------------------------------

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@throttle_classes([ChatRateThrottle])
def chat_message(request):

    message = request.data.get("message", "")

    # Validate message
    if not isinstance(message, str) or not message.strip():
        return Response(
            {
                "error": "Message is required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    message = message.strip()

    # Validate message length
    if len(message) > 5000:
        return Response(
            {
                "error": "Message must not exceed 5000 characters."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:

        # Generate AI reply using Ollama
        ai_reply = generate_ai_response(message)

        if not isinstance(ai_reply, str) or not ai_reply.strip():
            raise ValueError("AI returned an empty response.")

        # Save customer message and AI reply
        chat = ChatMessage.objects.create(
            user=request.user,
            message=message,
            response=ai_reply
        )

        serializer = ChatMessageSerializer(chat)

        return Response(
            {
                "message": "AI reply generated successfully!",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    except Exception as e:

        # Print error in Django Terminal
        print(
            "AI ERROR:",
            type(e).__name__,
            str(e)
        )

        return Response(
            {
                "error": (
                    "AI service is currently unavailable. "
                    "Please try again."
                )
            },
            status=status.HTTP_502_BAD_GATEWAY
        )


# ---------------------------------
# CUSTOMER CHAT HISTORY API
# ---------------------------------

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def chat_history(request):

    chats = ChatMessage.objects.filter(
        user=request.user
    ).order_by("-created_at")

    serializer = ChatMessageSerializer(
        chats,
        many=True
    )

    return Response(
        {
            "message": "Chat history retrieved successfully!",
            "data": serializer.data
        },
        status=status.HTTP_200_OK
    )
