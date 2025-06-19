from .test_main import *


# Get messages by conversation
def test_get_conversation_messages_404():
    token = get_token_admin()
    response = client.get("/conversations/999/messages", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Gesprek niet gevonden"
    }


def test_get_conversation_messages_404_no_messages():
    token = get_token_admin()
    response = client.get("/conversations/5/messages", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Geen bericht(en) voor dit gesprek"
    }


# Delete conversation
def test_delete_conversation_200():
    token = get_token_admin()
    response = client.delete("/conversations/2", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_delete_conversation_404():
    token = get_token_admin()
    response = client.delete("/conversations/999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Gesprek niet gevonden"
    }


# Create conversation
def test_create_conversation_200():
    token = get_token_admin()
    response = client.post("/conversations", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


# Delete all conversations
def test_delete_all_conversations_200():
    token = get_token_admin()
    response = client.delete("/conversations", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
