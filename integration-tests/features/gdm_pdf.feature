Feature: Generate patients' PDF documents
  As a clinician
  I want to print patients' PDF records
  So that I can have the data in case of business continuity contingencies
  
  Scenario: Generate GDM patient's PDF
    Given the Trustomer API is running
    And there exists a GDM patient
    When a request to create a PDF document for GDM patient is made
    Then the response is valid
    And the GDM patient PDF can be retrieved by patient uuid
