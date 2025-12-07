# tests/test_services/test_lead_service.py

import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session

from app.services.lead_service import LeadService
from app.models.lead import Lead
from app.models.lead_state import LeadState
from app.schemas.lead import LeadCreate


@pytest.mark.unit
class TestLeadServiceCreateLead:
    """Test LeadService.create_lead method."""
    
    def test_create_lead_success(self, test_db_session: Session, mock_email_service):
        """Test successfully creating a lead."""
        lead_data = LeadCreate(
            first_name="Test",
            last_name="User",
            email="test.user@example.com",
        )
        resume_path = "test_uploads/resume.pdf"
        
        lead = LeadService.create_lead(
            db=test_db_session,
            data=lead_data,
            resume_path=resume_path
        )
        
        assert lead is not None
        assert lead.first_name == "Test"
        assert lead.last_name == "User"
        assert lead.email == "test.user@example.com"
        assert lead.resume_path == resume_path
        assert lead.state == LeadState.PENDING
        assert lead.id is not None
        
        # Verify lead was persisted
        db_lead = test_db_session.query(Lead).filter(Lead.id == lead.id).first()
        assert db_lead is not None
        assert db_lead.email == "test.user@example.com"
        
        # Verify email service was called (twice - to prospect and company)
        assert mock_email_service.call_count == 2
    
    def test_create_lead_sets_initial_state(self, test_db_session: Session, mock_email_service):
        """Test that created lead has PENDING state."""
        lead_data = LeadCreate(
            first_name="State",
            last_name="Test",
            email="state.test@example.com",
        )
        
        lead = LeadService.create_lead(
            db=test_db_session,
            data=lead_data,
            resume_path="test.pdf"
        )
        
        assert lead.state == LeadState.PENDING


@pytest.mark.unit
class TestLeadServiceGetAllLeads:
    """Test LeadService.get_all_leads method."""
    
    def test_get_all_leads_returns_leads(self, test_db_session: Session):
        """Test getting all leads returns leads in descending order."""
        # Create multiple leads
        lead1 = Lead(
            first_name="First",
            last_name="Lead",
            email="first@example.com",
            resume_path="resume1.pdf",
            state=LeadState.PENDING,
        )
        lead2 = Lead(
            first_name="Second",
            last_name="Lead",
            email="second@example.com",
            resume_path="resume2.pdf",
            state=LeadState.REACHED_OUT,
        )
        test_db_session.add(lead1)
        test_db_session.add(lead2)
        test_db_session.commit()
        
        leads = LeadService.get_all_leads(test_db_session)
        
        assert len(leads) == 2
        # Should be ordered by created_at desc, so second lead should be first
        assert leads[0].email == "second@example.com"
        assert leads[1].email == "first@example.com"
    
    def test_get_all_leads_empty_database(self, test_db_session: Session):
        """Test getting all leads when database is empty."""
        leads = LeadService.get_all_leads(test_db_session)
        
        assert isinstance(leads, list)
        assert len(leads) == 0


@pytest.mark.unit
class TestLeadServiceGetLeadById:
    """Test LeadService.get_lead_by_id method."""
    
    def test_get_lead_by_id_success(self, test_db_session: Session):
        """Test getting a lead by valid ID."""
        lead = Lead(
            first_name="Get",
            last_name="Test",
            email="get.test@example.com",
            resume_path="resume.pdf",
            state=LeadState.PENDING,
        )
        test_db_session.add(lead)
        test_db_session.commit()
        test_db_session.refresh(lead)
        
        result = LeadService.get_lead_by_id(test_db_session, str(lead.id))
        
        assert result is not None
        assert result.id == lead.id
        assert result.email == "get.test@example.com"
    
    def test_get_lead_by_id_not_found(self, test_db_session: Session):
        """Test getting a lead with non-existent ID."""
        import uuid
        non_existent_id = str(uuid.uuid4())
        
        result = LeadService.get_lead_by_id(test_db_session, non_existent_id)
        
        assert result is None
    
    def test_get_lead_by_id_invalid_uuid(self, test_db_session: Session):
        """Test getting a lead with invalid UUID format."""
        result = LeadService.get_lead_by_id(test_db_session, "invalid-uuid")
        
        assert result is None


@pytest.mark.unit
class TestLeadServiceUpdateState:
    """Test LeadService.update_state method."""
    
    def test_update_state_success(self, test_db_session: Session):
        """Test successfully updating lead state."""
        lead = Lead(
            first_name="Update",
            last_name="Test",
            email="update.test@example.com",
            resume_path="resume.pdf",
            state=LeadState.PENDING,
        )
        test_db_session.add(lead)
        test_db_session.commit()
        test_db_session.refresh(lead)
        
        updated = LeadService.update_state(
            db=test_db_session,
            lead_id=lead.id,
            new_state=LeadState.REACHED_OUT
        )
        
        assert updated is not None
        assert updated.state == LeadState.REACHED_OUT
        assert updated.id == lead.id
        
        # Verify state was persisted
        db_lead = test_db_session.query(Lead).filter(Lead.id == lead.id).first()
        assert db_lead.state == LeadState.REACHED_OUT
    
    def test_update_state_not_found(self, test_db_session: Session):
        """Test updating state for non-existent lead."""
        import uuid
        non_existent_id = uuid.uuid4()
        
        result = LeadService.update_state(
            db=test_db_session,
            lead_id=non_existent_id,
            new_state=LeadState.REACHED_OUT
        )
        
        assert result is None
