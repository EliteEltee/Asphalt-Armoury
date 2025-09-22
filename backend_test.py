#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for Vehicle Checklist System
Tests all CRUD operations, checklist item management, and photo handling
"""

import requests
import json
import base64
from datetime import datetime
import os
from pathlib import Path

# Load environment variables to get backend URL
def load_env_file(file_path):
    env_vars = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value.strip('"')
    return env_vars

# Get backend URL from frontend .env
frontend_env = load_env_file('/app/frontend/.env')
BACKEND_URL = frontend_env.get('EXPO_PUBLIC_BACKEND_URL', 'http://localhost:8001')
API_BASE_URL = f"{BACKEND_URL}/api"

print(f"Testing backend at: {API_BASE_URL}")

class VehicleChecklistAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.created_checklist_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, message="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'response_data': response_data
        })
        
    def create_sample_vehicle_data(self):
        """Create realistic vehicle data for testing"""
        return {
            "title": "2019 Toyota Camry LE - Pre-Purchase Inspection",
            "vehicle_info": {
                "make": "Toyota",
                "model": "Camry",
                "series": "LE",
                "year": "2019",
                "bodyType": "Sedan",
                "doors": "4",
                "assembly": "Georgetown, KY",
                "licensing": "Passenger",
                "purchaseDate": "2024-01-15",
                "vin": "4T1B11HK5KU123456",
                "buildDate": "2019-03-15",
                "trimCode": "2532",
                "optionCode": "50",
                "odometer": "45000",
                "paintColor": "Midnight Black Metallic",
                "engine": "2.5L 4-Cylinder",
                "transmission": "8-Speed Automatic",
                "drive": "FWD",
                "layout": "FF",
                "rimSize": "17 inch",
                "tyreSize": "215/55R17",
                "weight": "1590 kg",
                "wheelbase": "2825 mm",
                "length": "4885 mm",
                "height": "1445 mm",
                "width": "1840 mm"
            },
            "engine_info": {
                "engineNumber": "2AR-FE-1234567",
                "engineCode": "2AR-FE",
                "description": "2.5L DOHC 16-Valve 4-Cylinder with VVT-i",
                "bore": "90.0 mm",
                "stroke": "98.0 mm",
                "compressionRatio": "11.0:1",
                "power": "203 hp @ 6600 rpm",
                "torque": "184 lb-ft @ 5000 rpm"
            },
            "is_template": False
        }
    
    def create_sample_base64_image(self):
        """Create a small base64 encoded test image"""
        # This is a tiny 1x1 pixel PNG image in base64
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = self.session.get(f"{API_BASE_URL}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("API Root", True, f"API is accessible: {data['message']}")
                    return True
                else:
                    self.log_test("API Root", False, "API response missing message field")
                    return False
            else:
                self.log_test("API Root", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("API Root", False, f"Connection error: {str(e)}")
            return False
    
    def test_create_checklist(self):
        """Test creating a new vehicle checklist"""
        try:
            vehicle_data = self.create_sample_vehicle_data()
            response = self.session.post(
                f"{API_BASE_URL}/checklists",
                json=vehicle_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "title" in data:
                    self.created_checklist_id = data["id"]
                    self.log_test("Create Checklist", True, f"Created checklist with ID: {data['id']}")
                    
                    # Verify all required fields are present
                    required_fields = ["vehicle_info", "engine_info", "tasks", "parts_to_install", "maintenance", "research_items", "photos"]
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        self.log_test("Create Checklist - Data Structure", False, f"Missing fields: {missing_fields}")
                    else:
                        self.log_test("Create Checklist - Data Structure", True, "All required fields present")
                    
                    return True
                else:
                    self.log_test("Create Checklist", False, "Response missing required fields (id, title)")
                    return False
            else:
                self.log_test("Create Checklist", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Checklist", False, f"Error: {str(e)}")
            return False
    
    def test_get_all_checklists(self):
        """Test retrieving all checklists"""
        try:
            response = self.session.get(f"{API_BASE_URL}/checklists")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get All Checklists", True, f"Retrieved {len(data)} checklists")
                    
                    # Verify our created checklist is in the list
                    if self.created_checklist_id:
                        found = any(checklist.get("id") == self.created_checklist_id for checklist in data)
                        if found:
                            self.log_test("Get All Checklists - Find Created", True, "Created checklist found in list")
                        else:
                            self.log_test("Get All Checklists - Find Created", False, "Created checklist not found in list")
                    
                    return True
                else:
                    self.log_test("Get All Checklists", False, "Response is not a list")
                    return False
            else:
                self.log_test("Get All Checklists", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get All Checklists", False, f"Error: {str(e)}")
            return False
    
    def test_get_specific_checklist(self):
        """Test retrieving a specific checklist by ID"""
        if not self.created_checklist_id:
            self.log_test("Get Specific Checklist", False, "No checklist ID available for testing")
            return False
            
        try:
            response = self.session.get(f"{API_BASE_URL}/checklists/{self.created_checklist_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("id") == self.created_checklist_id:
                    self.log_test("Get Specific Checklist", True, f"Retrieved checklist: {data.get('title', 'No title')}")
                    
                    # Verify vehicle info structure
                    vehicle_info = data.get("vehicle_info", {})
                    if len(vehicle_info) >= 20:  # Should have 25+ fields
                        self.log_test("Get Specific Checklist - Vehicle Info", True, f"Vehicle info has {len(vehicle_info)} fields")
                    else:
                        self.log_test("Get Specific Checklist - Vehicle Info", False, f"Vehicle info only has {len(vehicle_info)} fields, expected 25+")
                    
                    # Verify engine info structure
                    engine_info = data.get("engine_info", {})
                    if len(engine_info) >= 7:  # Should have 8 fields
                        self.log_test("Get Specific Checklist - Engine Info", True, f"Engine info has {len(engine_info)} fields")
                    else:
                        self.log_test("Get Specific Checklist - Engine Info", False, f"Engine info only has {len(engine_info)} fields, expected 8")
                    
                    return True
                else:
                    self.log_test("Get Specific Checklist", False, "Retrieved checklist ID doesn't match requested ID")
                    return False
            else:
                self.log_test("Get Specific Checklist", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Specific Checklist", False, f"Error: {str(e)}")
            return False
    
    def test_update_checklist(self):
        """Test updating a checklist"""
        if not self.created_checklist_id:
            self.log_test("Update Checklist", False, "No checklist ID available for testing")
            return False
            
        try:
            update_data = {
                "title": "2019 Toyota Camry LE - Updated Pre-Purchase Inspection"
            }
            
            response = self.session.put(
                f"{API_BASE_URL}/checklists/{self.created_checklist_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("title") == update_data["title"]:
                    self.log_test("Update Checklist", True, f"Successfully updated title to: {data['title']}")
                    return True
                else:
                    self.log_test("Update Checklist", False, "Title was not updated correctly")
                    return False
            else:
                self.log_test("Update Checklist", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Update Checklist", False, f"Error: {str(e)}")
            return False
    
    def test_add_checklist_items(self):
        """Test adding items to different checklist sections"""
        if not self.created_checklist_id:
            self.log_test("Add Checklist Items", False, "No checklist ID available for testing")
            return False
        
        sections_and_items = {
            "tasks": "Check engine oil level and condition",
            "parts_to_install": "Replace air filter",
            "maintenance": "Change transmission fluid",
            "research_items": "Research recall history for this VIN"
        }
        
        success_count = 0
        for section, item_text in sections_and_items.items():
            try:
                # Note: The API expects item_text as a query parameter, not in request body
                response = self.session.post(
                    f"{API_BASE_URL}/checklists/{self.created_checklist_id}/items/{section}",
                    params={"item_text": item_text}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "item" in data and data["item"].get("text") == item_text:
                        self.log_test(f"Add Item to {section}", True, f"Added: {item_text}")
                        success_count += 1
                    else:
                        self.log_test(f"Add Item to {section}", False, "Item not returned correctly in response")
                else:
                    self.log_test(f"Add Item to {section}", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Add Item to {section}", False, f"Error: {str(e)}")
        
        return success_count == len(sections_and_items)
    
    def test_toggle_checklist_items(self):
        """Test toggling completion status of checklist items"""
        if not self.created_checklist_id:
            self.log_test("Toggle Checklist Items", False, "No checklist ID available for testing")
            return False
        
        # First, get the checklist to find item IDs
        try:
            response = self.session.get(f"{API_BASE_URL}/checklists/{self.created_checklist_id}")
            if response.status_code != 200:
                self.log_test("Toggle Checklist Items", False, "Could not retrieve checklist to get item IDs")
                return False
            
            checklist_data = response.json()
            
            # Test toggling items in each section
            sections = ["tasks", "parts_to_install", "maintenance", "research_items"]
            success_count = 0
            
            for section in sections:
                items = checklist_data.get(section, [])
                if items:
                    item_id = items[0]["id"]  # Get first item ID
                    
                    # Toggle the item
                    toggle_response = self.session.put(
                        f"{API_BASE_URL}/checklists/{self.created_checklist_id}/items/{section}/{item_id}/toggle"
                    )
                    
                    if toggle_response.status_code == 200:
                        self.log_test(f"Toggle Item in {section}", True, f"Successfully toggled item {item_id}")
                        success_count += 1
                    else:
                        self.log_test(f"Toggle Item in {section}", False, f"HTTP {toggle_response.status_code}: {toggle_response.text}")
                else:
                    self.log_test(f"Toggle Item in {section}", False, f"No items found in {section} to toggle")
            
            return success_count > 0
            
        except Exception as e:
            self.log_test("Toggle Checklist Items", False, f"Error: {str(e)}")
            return False
    
    def test_add_photo(self):
        """Test adding a photo with base64 data"""
        if not self.created_checklist_id:
            self.log_test("Add Photo", False, "No checklist ID available for testing")
            return False
        
        try:
            photo_data = {
                "base64_data": self.create_sample_base64_image(),
                "description": "Engine bay inspection photo"
            }
            
            response = self.session.post(
                f"{API_BASE_URL}/checklists/{self.created_checklist_id}/photos",
                json=photo_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "photo" in data and data["photo"].get("description") == photo_data["description"]:
                    self.log_test("Add Photo", True, f"Added photo: {data['photo'].get('description')}")
                    
                    # Verify photo has required fields
                    photo = data["photo"]
                    required_fields = ["id", "base64_data", "description", "timestamp"]
                    missing_fields = [field for field in required_fields if field not in photo]
                    if missing_fields:
                        self.log_test("Add Photo - Data Structure", False, f"Photo missing fields: {missing_fields}")
                    else:
                        self.log_test("Add Photo - Data Structure", True, "Photo has all required fields")
                    
                    return True
                else:
                    self.log_test("Add Photo", False, "Photo not returned correctly in response")
                    return False
            else:
                self.log_test("Add Photo", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Add Photo", False, f"Error: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test error handling for missing resources"""
        fake_id = "non-existent-id-12345"
        
        # Test getting non-existent checklist
        try:
            response = self.session.get(f"{API_BASE_URL}/checklists/{fake_id}")
            if response.status_code == 404:
                self.log_test("Error Handling - Get Non-existent Checklist", True, "Correctly returned 404")
            else:
                self.log_test("Error Handling - Get Non-existent Checklist", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Get Non-existent Checklist", False, f"Error: {str(e)}")
        
        # Test updating non-existent checklist
        try:
            response = self.session.put(
                f"{API_BASE_URL}/checklists/{fake_id}",
                json={"title": "Test"},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 404:
                self.log_test("Error Handling - Update Non-existent Checklist", True, "Correctly returned 404")
            else:
                self.log_test("Error Handling - Update Non-existent Checklist", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Update Non-existent Checklist", False, f"Error: {str(e)}")
        
        # Test deleting non-existent checklist
        try:
            response = self.session.delete(f"{API_BASE_URL}/checklists/{fake_id}")
            if response.status_code == 404:
                self.log_test("Error Handling - Delete Non-existent Checklist", True, "Correctly returned 404")
            else:
                self.log_test("Error Handling - Delete Non-existent Checklist", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Delete Non-existent Checklist", False, f"Error: {str(e)}")
        
        # Test adding item to invalid section
        if self.created_checklist_id:
            try:
                response = self.session.post(
                    f"{API_BASE_URL}/checklists/{self.created_checklist_id}/items/invalid_section",
                    params={"item_text": "Test item"}
                )
                if response.status_code == 400:
                    self.log_test("Error Handling - Invalid Section", True, "Correctly returned 400 for invalid section")
                else:
                    self.log_test("Error Handling - Invalid Section", False, f"Expected 400, got {response.status_code}")
            except Exception as e:
                self.log_test("Error Handling - Invalid Section", False, f"Error: {str(e)}")
    
    def test_delete_checklist(self):
        """Test deleting a checklist (run this last)"""
        if not self.created_checklist_id:
            self.log_test("Delete Checklist", False, "No checklist ID available for testing")
            return False
        
        try:
            response = self.session.delete(f"{API_BASE_URL}/checklists/{self.created_checklist_id}")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Delete Checklist", True, f"Successfully deleted: {data['message']}")
                    
                    # Verify checklist is actually deleted
                    verify_response = self.session.get(f"{API_BASE_URL}/checklists/{self.created_checklist_id}")
                    if verify_response.status_code == 404:
                        self.log_test("Delete Checklist - Verification", True, "Checklist confirmed deleted")
                    else:
                        self.log_test("Delete Checklist - Verification", False, "Checklist still exists after deletion")
                    
                    return True
                else:
                    self.log_test("Delete Checklist", False, "Response missing message field")
                    return False
            else:
                self.log_test("Delete Checklist", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Delete Checklist", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("=" * 80)
        print("VEHICLE CHECKLIST API COMPREHENSIVE TESTING")
        print("=" * 80)
        
        # Test sequence
        tests = [
            self.test_api_root,
            self.test_create_checklist,
            self.test_get_all_checklists,
            self.test_get_specific_checklist,
            self.test_update_checklist,
            self.test_add_checklist_items,
            self.test_toggle_checklist_items,
            self.test_add_photo,
            self.test_error_handling,
            self.test_delete_checklist  # Run this last
        ]
        
        for test in tests:
            test()
            print("-" * 40)
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\nFailed Tests:")
        for result in self.test_results:
            if not result['success']:
                print(f"❌ {result['test']}: {result['message']}")
        
        return passed == total

if __name__ == "__main__":
    tester = VehicleChecklistAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! Backend API is working correctly.")
    else:
        print("\n⚠️  SOME TESTS FAILED. Check the details above.")