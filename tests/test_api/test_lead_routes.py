# tests/test_api/test_lead_routes.py

import math
import pytest
from fastapi.testclient import TestClient
from io import BytesIO
from app.models.lead_state import LeadState


@pytest.mark.integration
class TestCreateLead:
    """Test POST /leads endpoint."""
    
    def test_create_lead_success(self, test_client: TestClient, mock_email_service):
        """Test successful lead creation with file upload."""
        # Create a mock file
        file_content = b"Mock PDF content"
        files = {
            "resume": ("resume.pdf", BytesIO(file_content), "application/pdf")
        }
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
        }
        
        response = test_client.post("/leads", data=data, files=files)
        
        assert response.status_code == 201
        lead_data = response.json()
        assert lead_data["first_name"] == "John"
        assert lead_data["last_name"] == "Doe"
        assert lead_data["email"] == "john.doe@example.com"
        assert lead_data["state"] == LeadState.PENDING
        assert "id" in lead_data
        assert "resume_path" in lead_data
        
        # Verify email service was called
        assert mock_email_service.called
    
    def test_create_lead_missing_fields(self, test_client: TestClient):
        """Test lead creation with missing required fields."""
        file_content = b"Mock PDF content"
        files = {
            "resume": ("resume.pdf", BytesIO(file_content), "application/pdf")
        }
        data = {
            "first_name": "John",
            # Missing last_name and email
        }
        
        response = test_client.post("/leads", data=data, files=files)
        
        assert response.status_code == 422
    
    def test_create_lead_invalid_email(self, test_client: TestClient):
        """Test lead creation with invalid email format."""
        file_content = b"Mock PDF content"
        files = {
            "resume": ("resume.pdf", BytesIO(file_content), "application/pdf")
        }
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "invalid-email",  # Invalid email format
        }
        
        response = test_client.post("/leads", data=data, files=files)
        
        assert response.status_code == 422


@pytest.mark.integration
class TestListLeads:
    """Test GET /leads endpoint."""
    
    def test_list_leads_with_valid_token(self, test_client: TestClient, test_db_session):
        """Test listing leads with valid authentication token."""
        # First create a lead
        from app.models.lead import Lead
        from app.schemas.lead import LeadCreate
        
        lead = Lead(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            resume_path="test_resume.pdf",
            state=LeadState.PENDING,
        )
        test_db_session.add(lead)
        test_db_session.commit()
        test_db_session.refresh(lead)
        
        # List leads with valid token
        headers = {"Authorization": "Bearer test_token_123"}
        response = test_client.get("/leads", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) >= 1
        assert data["items"][0]["email"] == "jane.smith@example.com"
        assert data["total"] >= 1
        assert data["page"] == 1
        assert data["page_size"] == 10
    
    def test_list_leads_without_token(self, test_client: TestClient):
        """Test listing leads without authentication token."""
        response = test_client.get("/leads")
        
        assert response.status_code == 403  # FastAPI HTTPBearer returns 403 for missing token
    
    def test_list_leads_with_invalid_token(self, test_client: TestClient):
        """Test listing leads with invalid authentication token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = test_client.get("/leads", headers=headers)
        
        assert response.status_code == 401
    
    def test_list_leads_empty(self, test_client: TestClient):
        """Test listing leads when database is empty."""
        headers = {"Authorization": "Bearer test_token_123"}
        response = test_client.get("/leads", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total_pages"] == 0
    
    def test_list_leads_pagination(self, test_client: TestClient, test_db_session):
        """Test pagination parameters."""
        from app.models.lead import Lead
        
        # Create multiple leads
        for i in range(15):
            lead = Lead(
                first_name=f"Test{i}",
                last_name="User",
                email=f"test{i}@example.com",
                resume_path=f"test_resume_{i}.pdf",
                state=LeadState.PENDING,
            )
            test_db_session.add(lead)
        test_db_session.commit()
        
        headers = {"Authorization": "Bearer test_token_123"}
        
        # Test first page
        response = test_client.get("/leads?page=1&page_size=5", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert data["total"] >= 15
        assert data["total_pages"] == math.ceil(data["total"] / 5)
        
        # Test second page
        response = test_client.get("/leads?page=2&page_size=5", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
        assert data["page"] == 2
    
    def test_list_leads_pagination_invalid_params(self, test_client: TestClient):
        """Test pagination with invalid parameters."""
        headers = {"Authorization": "Bearer test_token_123"}
        
        # Test negative page
        response = test_client.get("/leads?page=-1", headers=headers)
        assert response.status_code == 422
        
        # Test page_size too large
        response = test_client.get("/leads?page_size=200", headers=headers)
        assert response.status_code == 422
        
        # Test zero page_size
        response = test_client.get("/leads?page_size=0", headers=headers)
        assert response.status_code == 422


@pytest.mark.integration
class TestGetLead:
    """Test GET /leads/{lead_id} endpoint."""
    
    def test_get_lead_success(self, test_client: TestClient, test_db_session):
        """Test getting a single lead with valid ID."""
        from app.models.lead import Lead
        
        lead = Lead(
            first_name="Alice",
            last_name="Johnson",
            email="alice.johnson@example.com",
            resume_path="test_resume.pdf",
            state=LeadState.PENDING,
        )
        test_db_session.add(lead)
        test_db_session.commit()
        test_db_session.refresh(lead)
        
        headers = {"Authorization": "Bearer test_token_123"}
        response = test_client.get(f"/leads/{lead.id}", headers=headers)
        
        assert response.status_code == 200
        lead_data = response.json()
        assert lead_data["id"] == str(lead.id)
        assert lead_data["email"] == "alice.johnson@example.com"
    
    def test_get_lead_not_found(self, test_client: TestClient):
        """Test getting a lead with non-existent ID."""
        headers = {"Authorization": "Bearer test_token_123"}
        response = test_client.get("/leads/00000000-0000-0000-0000-000000000000", headers=headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_lead_without_auth(self, test_client: TestClient, test_db_session):
        """Test getting a lead without authentication."""
        from app.models.lead import Lead
        
        lead = Lead(
            first_name="Bob",
            last_name="Brown",
            email="bob.brown@example.com",
            resume_path="test_resume.pdf",
            state=LeadState.PENDING,
        )
        test_db_session.add(lead)
        test_db_session.commit()
        test_db_session.refresh(lead)
        
        response = test_client.get(f"/leads/{lead.id}")
        
        assert response.status_code == 403


@pytest.mark.integration
class TestUpdateLeadState:
    """Test PATCH /leads/{lead_id}/state endpoint."""
    
    def test_update_lead_state_success(self, test_client: TestClient, test_db_session):
        """Test successfully updating lead state."""
        from app.models.lead import Lead
        
        lead = Lead(
            first_name="Charlie",
            last_name="Davis",
            email="charlie.davis@example.com",
            resume_path="test_resume.pdf",
            state=LeadState.PENDING,
        )
        test_db_session.add(lead)
        test_db_session.commit()
        test_db_session.refresh(lead)
        
        headers = {"Authorization": "Bearer test_token_123"}
        update_data = {"state": LeadState.REACHED_OUT}
        response = test_client.patch(
            f"/leads/{lead.id}/state",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 200
        lead_data = response.json()
        assert lead_data["state"] == LeadState.REACHED_OUT
        assert lead_data["id"] == str(lead.id)
    
    def test_update_lead_state_not_found(self, test_client: TestClient):
        """Test updating state for non-existent lead."""
        headers = {"Authorization": "Bearer test_token_123"}
        update_data = {"state": LeadState.REACHED_OUT}
        response = test_client.patch(
            "/leads/00000000-0000-0000-0000-000000000000/state",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 404
    
    def test_update_lead_state_without_auth(self, test_client: TestClient, test_db_session):
        """Test updating lead state without authentication."""
        from app.models.lead import Lead
        
        lead = Lead(
            first_name="David",
            last_name="Wilson",
            email="david.wilson@example.com",
            resume_path="test_resume.pdf",
            state=LeadState.PENDING,
        )
        test_db_session.add(lead)
        test_db_session.commit()
        test_db_session.refresh(lead)
        
        update_data = {"state": LeadState.REACHED_OUT}
        response = test_client.patch(
            f"/leads/{lead.id}/state",
            json=update_data
        )
        
        assert response.status_code == 403
