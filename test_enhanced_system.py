#!/usr/bin/env python3
"""
Test script for the Enhanced AI WiFi Monitoring System
Tests the advanced AI features, alert generation, and dashboard integration
"""

import requests
import json
import time
import random
from datetime import datetime

class EnhancedSystemTester:
    def __init__(self, esp32_ip="192.168.4.1"):
        self.base_url = f"http://{esp32_ip}"
        self.test_results = []
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
    
    def test_basic_endpoints(self):
        """Test basic API endpoints"""
        print("\n🔍 Testing Basic API Endpoints...")
        
        endpoints = [
            ("/status", "Basic status endpoint"),
            ("/advanced-ai", "Advanced AI endpoint"),
            ("/history?days=0", "History endpoint"),
            ("/dashboard.html", "Dashboard page")
        ]
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    self.log_test(f"API: {description}", "PASS", f"Status: {response.status_code}")
                else:
                    self.log_test(f"API: {description}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"API: {description}", "FAIL", f"Error: {str(e)}")
    
    def test_advanced_ai_features(self):
        """Test advanced AI features and alerts"""
        print("\n🤖 Testing Advanced AI Features...")
        
        try:
            response = requests.get(f"{self.base_url}/advanced-ai", timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                # Test required fields
                required_fields = ['stability', 'confidence', 'trend_score', 'alert_type', 'alert_message']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_test("Advanced AI: Required fields", "PASS", "All fields present")
                else:
                    self.log_test("Advanced AI: Required fields", "FAIL", f"Missing: {missing_fields}")
                
                # Test data ranges
                if 0 <= data.get('stability', -1) <= 1:
                    self.log_test("Advanced AI: Stability range", "PASS", f"Value: {data['stability']:.3f}")
                else:
                    self.log_test("Advanced AI: Stability range", "FAIL", f"Value: {data.get('stability', 'N/A')}")
                
                if 0 <= data.get('confidence', -1) <= 1:
                    self.log_test("Advanced AI: Confidence range", "PASS", f"Value: {data['confidence']:.3f}")
                else:
                    self.log_test("Advanced AI: Confidence range", "FAIL", f"Value: {data.get('confidence', 'N/A')}")
                
                # Test alert types
                valid_alert_types = ['interference', 'weak_signal', 'degrading', 'congestion', 'unstable', 'excellent', 'good', 'poor']
                alert_type = data.get('alert_type', '')
                if alert_type in valid_alert_types:
                    self.log_test("Advanced AI: Alert type", "PASS", f"Type: {alert_type}")
                else:
                    self.log_test("Advanced AI: Alert type", "WARN", f"Unexpected type: {alert_type}")
                
                # Test alert message quality
                alert_message = data.get('alert_message', '')
                if len(alert_message) > 10 and any(word in alert_message.lower() for word in ['warning', 'alert', 'excellent', 'good', 'poor']):
                    self.log_test("Advanced AI: Alert message quality", "PASS", f"Message: {alert_message[:50]}...")
                else:
                    self.log_test("Advanced AI: Alert message quality", "WARN", f"Message: {alert_message}")
                
            else:
                self.log_test("Advanced AI: API response", "FAIL", f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Advanced AI: API test", "FAIL", f"Error: {str(e)}")
    
    def test_dashboard_integration(self):
        """Test dashboard integration"""
        print("\n🖥️ Testing Dashboard Integration...")
        
        try:
            response = requests.get(f"{self.base_url}/dashboard.html", timeout=5)
            if response.status_code == 200:
                content = response.text
                
                # Check for enhanced AI elements
                ai_elements = [
                    'current-ai-alert',
                    'alert-icon',
                    'alert-title',
                    'alert-confidence',
                    'alert-message',
                    'alert-solution'
                ]
                
                missing_elements = [elem for elem in ai_elements if elem not in content]
                if not missing_elements:
                    self.log_test("Dashboard: AI elements", "PASS", "All AI elements present")
                else:
                    self.log_test("Dashboard: AI elements", "FAIL", f"Missing: {missing_elements}")
                
                # Check for CSS classes
                css_classes = ['ai-alert-card', 'alert-header', 'alert-solution']
                missing_css = [cls for cls in css_classes if cls not in content]
                if not missing_css:
                    self.log_test("Dashboard: CSS classes", "PASS", "All CSS classes present")
                else:
                    self.log_test("Dashboard: CSS classes", "WARN", f"Missing: {missing_css}")
                
            else:
                self.log_test("Dashboard: Page load", "FAIL", f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Dashboard: Integration test", "FAIL", f"Error: {str(e)}")
    
    def test_alert_scenarios(self):
        """Test different alert scenarios by analyzing current data"""
        print("\n🚨 Testing Alert Scenarios...")
        
        try:
            # Get current status
            response = requests.get(f"{self.base_url}/status", timeout=5)
            if response.status_code == 200:
                status_data = response.json()
                
                # Get AI analysis
                ai_response = requests.get(f"{self.base_url}/advanced-ai", timeout=5)
                if ai_response.status_code == 200:
                    ai_data = ai_response.json()
                    
                    # Analyze alert logic
                    rssi = status_data.get('rssi', 0)
                    noise = status_data.get('noise', -95)
                    snr = status_data.get('snr', 0)
                    channel_util = status_data.get('channel_util', 0)
                    
                    # Test weak signal detection
                    if rssi < -80:
                        expected_alert = 'weak_signal'
                        if ai_data.get('alert_type') == expected_alert:
                            self.log_test("Alert Logic: Weak signal", "PASS", f"RSSI: {rssi}dBm")
                        else:
                            self.log_test("Alert Logic: Weak signal", "WARN", f"Expected {expected_alert}, got {ai_data.get('alert_type')}")
                    
                    # Test interference detection
                    if abs(noise) > -85 and channel_util > 70:
                        expected_alert = 'interference'
                        if ai_data.get('alert_type') == expected_alert:
                            self.log_test("Alert Logic: Interference", "PASS", f"Noise: {noise}dBm, Util: {channel_util}%")
                        else:
                            self.log_test("Alert Logic: Interference", "WARN", f"Expected {expected_alert}, got {ai_data.get('alert_type')}")
                    
                    # Test excellent performance
                    if rssi > -60 and snr > 25 and channel_util < 30:
                        expected_alert = 'excellent'
                        if ai_data.get('alert_type') == expected_alert:
                            self.log_test("Alert Logic: Excellent", "PASS", f"RSSI: {rssi}dBm, SNR: {snr}dB")
                        else:
                            self.log_test("Alert Logic: Excellent", "WARN", f"Expected {expected_alert}, got {ai_data.get('alert_type')}")
                    
                    self.log_test("Alert Scenarios: Analysis complete", "PASS", f"Current alert: {ai_data.get('alert_type')}")
                    
                else:
                    self.log_test("Alert Scenarios: AI data", "FAIL", f"Status: {ai_response.status_code}")
            else:
                self.log_test("Alert Scenarios: Status data", "FAIL", f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Alert Scenarios: Test", "FAIL", f"Error: {str(e)}")
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*60)
        print("🎯 ENHANCED AI WIFI MONITOR TEST REPORT")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warned_tests = len([r for r in self.test_results if r['status'] == 'WARN'])
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Warnings: {warned_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"   - {result['test']}: {result['details']}")
        
        if warned_tests > 0:
            print(f"\n⚠️ Warnings:")
            for result in self.test_results:
                if result['status'] == 'WARN':
                    print(f"   - {result['test']}: {result['details']}")
        
        print("\n🎉 Enhanced AI WiFi Monitor testing complete!")
        
        # Save detailed report
        with open('test_report.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print("📄 Detailed report saved to: test_report.json")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Enhanced AI WiFi Monitor System Tests...")
        print(f"🎯 Target: {self.base_url}")
        
        self.test_basic_endpoints()
        self.test_advanced_ai_features()
        self.test_dashboard_integration()
        self.test_alert_scenarios()
        self.generate_report()

if __name__ == "__main__":
    # You can change the IP address to match your ESP32
    tester = EnhancedSystemTester("192.168.4.1")  # Default AP mode IP
    tester.run_all_tests()
