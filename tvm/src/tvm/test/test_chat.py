from .test_main import *

# Get all conversations
# def test_get_user_conversations_200():
#     token = get_token_admin()
#     response = client.get("/conversations", headers={"Authorization": f"Bearer {token}"})
#     assert response.status_code == 200
#
#     expected_data = [
#         # Because of the created_at-field, this can't really be tested consistently.
#     ]
#     assert response.json() == expected_data
#
# # Get all messages of a conversation
# def test_get_conversation_messages_200():
#     token = get_token_admin()
#     response = client.get("/conversations/1/messages", headers={"Authorization": f"Bearer {token}"})
#     assert response.status_code == 200
#
#     expected_data = [
#         # Because of the created_at-field, this can't really be tested consistently.
#     ]
#     assert response.json() == expected_data


def test_get_conversation_messages_404():
    token = get_token_admin()
    response = client.get("/conversations/999/messages", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Gesprek niet gevonden"
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