describe('Compliance Check', () => {
  beforeEach(() => {
    cy.intercept('POST', '/api/v1/compliance/verify-customer', {
      statusCode: 200,
      body: {
        pep: {
          status: 'clear',
          matches: [],
          source: 'wikidata',
          timestamp: new Date().toISOString()
        },
        ofac: {
          status: 'matched',
          matches: [
            {
              source: 'ofac',
              source_id: '12345',
              name: 'John Doe',
              match_type: 'name',
              score: 0.95,
              details: {
                program: 'SDN',
                listing_date: '2023-01-15'
              }
            }
          ],
          source: 'ofac',
          timestamp: new Date().toISOString()
        },
        un: {
          status: 'clear',
          matches: [],
          source: 'un',
          timestamp: new Date().toISOString()
        },
        eu: {
          status: 'clear',
          matches: [],
          source: 'eu',
          timestamp: new Date().toISOString()
        },
        verification_id: '123456',
        created_at: new Date().toISOString(),
        enriched_data: {}
      }
    }).as('complianceCheck');

    cy.visit('/#/compliance/verify-customer');
  });

  it('should allow filling out the form for a natural person', () => {
    cy.get('select').select('natural');
    
    cy.get('#customerName').type('John Doe');
    cy.get('#customerCountry').type('US');
    cy.get('#customerDob').type('1980-01-01');
    
    cy.contains('button', 'Continue').click();
    
    cy.contains('button', 'Back').should('be.visible');
    cy.contains('button', 'Run Compliance Check').should('be.visible');
  });

  it('should allow filling out the form for a legal entity with directors and UBOs', () => {
    cy.get('select').select('legal');
    
    cy.get('#customerName').type('Acme Corp');
    cy.get('#customerCountry').type('US');
    
    cy.contains('button', 'Add Director').click();
    
    cy.get('input').eq(2).type('Jane Doe');
    cy.get('input[type="date"]').eq(0).type('1975-05-15');
    cy.get('input').eq(4).type('US');
    
    cy.contains('button', 'Add UBO').click();
    
    cy.get('input').eq(5).type('Jim Smith');
    cy.get('input[type="date"]').eq(1).type('1965-09-30');
    cy.get('input').eq(7).type('US');
    
    cy.contains('button', 'Continue').click();
    
    cy.contains('button', 'Back').should('be.visible');
    cy.contains('button', 'Run Compliance Check').should('be.visible');
  });

  it('should perform a compliance check and display results', () => {
    cy.get('select').select('natural');
    
    cy.get('#customerName').type('John Doe');
    cy.get('#customerCountry').type('US');
    cy.get('#customerDob').type('1980-01-01');
    
    cy.contains('button', 'Continue').click();
    
    cy.contains('button', 'Run Compliance Check').click();
    
    cy.wait('@complianceCheck');
    
    cy.contains('PEP').should('be.visible');
    cy.contains('OFAC').should('be.visible');
    cy.contains('UN').should('be.visible');
    cy.contains('EU').should('be.visible');
    
    cy.contains('Clear').should('be.visible');
    cy.contains('Matched').should('be.visible');
    
    cy.contains('OFAC').click();
    cy.contains('John Doe').should('be.visible');
    cy.contains('Source:').should('be.visible');
    cy.contains('Match Type:').should('be.visible');
    cy.contains('Score:').should('be.visible');
  });
});
