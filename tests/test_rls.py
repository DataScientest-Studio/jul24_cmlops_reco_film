import os
from supabase import create_client, Client, ClientOptions
import pytest
import dotenv

dotenv.load_dotenv()

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_KEY")

user1_email = "user1@example.com"
user2_email = "user14@example.com"
password = "azeqsd123"


@pytest.fixture
def supabase_anon() -> Client:
    return create_client(
        SUPABASE_URL, SUPABASE_ANON_KEY, options=ClientOptions(auto_refresh_token=False)
    )


@pytest.fixture
def supabase_user1(supabase_anon) -> Client:
    response = supabase_anon.auth.sign_in_with_password(
        {"email": user1_email, "password": password}
    )
    client = create_client(
        SUPABASE_URL, SUPABASE_ANON_KEY, options=ClientOptions(auto_refresh_token=False)
    )
    client.auth.set_session(
        access_token=response.session.access_token,
        refresh_token=response.session.refresh_token,
    )
    return client


@pytest.fixture
def supabase_user2(supabase_anon) -> Client:
    response = supabase_anon.auth.sign_in_with_password(
        {"email": user2_email, "password": password}
    )
    client = create_client(
        SUPABASE_URL, SUPABASE_ANON_KEY, options=ClientOptions(auto_refresh_token=False)
    )
    client.auth.set_session(
        access_token=response.session.access_token,
        refresh_token=response.session.refresh_token,
    )
    return client


def test_anon_cannot_read_users(supabase_anon):
    """Test qu'un utilisateur anonyme ne peut pas lire les données utilisateur"""
    response = supabase_anon.table("users").select("*").execute()
    assert len(response.data) == 0
    supabase_anon.auth.sign_out()


def test_user_can_read_own_data(supabase_user1):
    """Test qu'un utilisateur peut lire ses propres données"""
    response = supabase_user1.table("users").select("*").execute()
    assert len(response.data) == 1
    assert response.data[0]["authId"] == supabase_user1.auth.get_user().user.id
    supabase_user1.auth.sign_out()


def test_user_cannot_read_other_user_data(supabase_user1, supabase_user2):
    """Test qu'un utilisateur ne peut pas lire les données d'un autre utilisateur"""
    user2_id = supabase_user2.auth.get_user().user.id
    response = (
        supabase_user1.table("users").select("*").eq("authId", user2_id).execute()
    )
    assert len(response.data) == 0
    supabase_user1.auth.sign_out()
    supabase_user2.auth.sign_out()
