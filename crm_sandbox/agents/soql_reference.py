"""
Shared SOQL/SOSL Reference Guide

This is appended to the system_description for ALL agentic strategies (ReAct, PaS, Reflexion).
It provides SOQL/SOSL patterns and tips based on the actual CRMArena-Pro schema to improve
query accuracy across all task categories.

Adding guidance here ensures fair comparison — all strategies receive identical help.
"""

SOQL_REFERENCE = """\

# SOQL/SOSL Quick Reference

## SOQL Syntax
SELECT field1, field2 FROM Object WHERE condition ORDER BY field LIMIT n

## Common Patterns

### Count records
SELECT COUNT() FROM Case WHERE Status = 'Open'

### Filter by date range
SELECT Id FROM Case WHERE CreatedDate >= 2025-01-01T00:00:00Z AND CreatedDate <= 2025-03-31T23:59:59Z

### Group and aggregate
SELECT OwnerId, COUNT(Id) total FROM Case GROUP BY OwnerId HAVING COUNT(Id) > 5

### Join via lookup (parent-to-child)
SELECT Id, Account.Name FROM Contact WHERE Account.Industry = 'Technology'

### Use IN clause
SELECT Id, Name FROM User WHERE Id IN ('005xx1', '005xx2', '005xx3')

### SOSL text search
FIND {search term} IN ALL FIELDS RETURNING Case(Id, OwnerId, IssueId__c, Subject)

## SOSL Rules
- Valid search scopes: ALL FIELDS, NAME FIELDS, EMAIL FIELDS, PHONE FIELDS
- DO NOT use: IN DESCRIPTION FIELDS (not valid)
- Syntax: FIND {term} IN ALL FIELDS RETURNING Object(Field1, Field2)
- Use SOSL when you need to search text content across records

## Important Constraints (Salesforce-specific)
- The Description field CANNOT be used in WHERE clauses (not filterable)
- Use SOSL with IN ALL FIELDS to search text content instead of WHERE Description LIKE
- Date format: YYYY-MM-DDThh:mm:ssZ (e.g., 2025-01-01T00:00:00Z)
- String values use single quotes: WHERE Status = 'Closed'
- NULL check: WHERE Field != null
- LIKE operator works on: Subject, Name, Email (NOT on Description, Body, TextBody)
- Relationship fields use dot notation: Account.Name, Owner.Name, Contact.Email
- For User lookups: query User object separately, then use Id in WHERE clause
- CaseHistory__c tracks ownership changes: Field__c = 'Owner Assignment', NewValue__c = User Id
- CANNOT use column aliases in ORDER BY — use the aggregate expression directly
  WRONG: SELECT OwnerId, COUNT(Id) cnt FROM Case GROUP BY OwnerId ORDER BY cnt DESC
  CORRECT: SELECT OwnerId, COUNT(Id) FROM Case GROUP BY OwnerId ORDER BY COUNT(Id) DESC
- SOSL search terms cannot contain hyphens — remove or replace them with spaces

## Key Object Relationships
- Case.OwnerId -> User.Id (current case owner)
- Case.IssueId__c -> Issue__c.Id (issue category)
- Case.OrderItemId__c -> OrderItem.Id -> Product2.Id (product linked to case)
- CaseHistory__c.CaseId__c -> Case.Id (case ownership history)
- CaseHistory__c.NewValue__c -> User.Id (agent assigned)
- Order.AccountId -> Account.Id
- OrderItem.Product2Id -> Product2.Id
- Lead.OwnerId -> User.Id
- Opportunity.OwnerId -> User.Id
- Territory2.Description contains comma-separated state codes
- UserTerritory2Association links User to Territory2

## Task-Specific Hints

### Case Routing: Finding agent expertise
- Find issue expertise: query CaseHistory__c or Case WHERE IssueId__c matches and Status = 'Closed', GROUP BY OwnerId
- Find product expertise: join Case -> OrderItem -> Product2, GROUP BY OwnerId
- Find workload: SELECT OwnerId, COUNT(Id) FROM Case WHERE Status != 'Closed' GROUP BY OwnerId

### Handle Time: Calculating duration
- Handle time = ClosedDate - CreatedDate (query both fields from Case)
- Filter by date range on CreatedDate or ClosedDate

### Transfer Count: Tracking ownership changes
- Use CaseHistory__c WHERE Field__c = 'Owner Assignment' to count transfers
- GROUP BY CaseId__c to get transfer count per case

### Lead Routing: Territory-based assignment
- Territory2.Description contains state codes (e.g., 'CA,IL,AL')
- UserTerritory2Association links agents to territories
- Match lead's state to territory, then find associated agent
"""
