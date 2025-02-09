# backend/tests/test_utils.py
import pytest
from backend.utils import generate_svg, upload_to_ipfs, send_email
import os

def test_generate_svg():
    svg_file = generate_svg("test_hash")
    assert os.path.exists(svg_file)
    os.remove(svg_file) #Clean up

#Mocking IPFS for testing
from unittest.mock import patch
@patch('backend.utils.connect')
def test_upload_to_ipfs(mock_connect):
    mock_instance = mock_connect.return_value
    mock_instance.add.return_value = {'Hash': 'test_cid'}
    cid = upload_to_ipfs("dummy_file.txt")
    assert cid == "test_cid"

#Test Email Sending
def test_send_email():
    #This test will only verify that the function runs without errors,
    #not that the email is actually sent (due to credentials).
    #You can extend it to check the return value based on successful/failed login

    result = send_email("test@example.com", "Test Subject", "Test Body")
    assert result is False #Because email is not configured properly