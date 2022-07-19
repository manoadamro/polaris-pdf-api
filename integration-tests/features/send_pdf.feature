Feature: Generate patients' PDF documents
  As a clinician
  I want to print patients' PDF records
  So that I can have the data in case of business continuity contingencies
  
  Scenario: Generate SEND patient's PDF
    Given the Trustomer API is running
    And there exists a SEND patient
    When a request to create a PDF document for SEND patient is made
    Then the response is valid
    And the SEND patient PDF can be retrieved by its encounter uuid
