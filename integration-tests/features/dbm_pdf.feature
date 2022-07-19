Feature: Generate patients' PDF documents
  As a clinician
  I want to print patients' PDF records
  So that I can have the data in case of business continuity contingencies
  
  Scenario: Generate DBM patient's PDF
    Given there exists a DBM patient with hba1c
    When a request to create a PDF document for DBM patient is made
    Then the response is valid
    And the DBM patient PDF with hba1c can be retrieved by patient uuid

  Scenario: Generate DBM patient's PDF without HBA1C
    Given there exists a DBM patient without hba1c
    When a request to create a PDF document for DBM patient is made
    Then the response is valid
    And the DBM patient PDF without hba1c can be retrieved by patient uuid
