Feature: Generate patients' PDF documents
  As a clinician
  I want to print patients' PDF records
  So that I can have the data in case of business continuity contingencies

  Background:
    Given the Trustomer API is running

  Scenario: Generate SEND ward PDF
    Given ward metrics have been generated
    When a request to create a ward report is made
    Then the response is valid
    And the ward report PDF can be retrieved by its location uuid

  Scenario: Generate many SEND ward PDFs
    Given there exist many ward metrics
    When requests to create ward reports are made
    Then the response is valid
