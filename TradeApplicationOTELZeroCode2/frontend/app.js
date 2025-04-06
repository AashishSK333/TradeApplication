document.getElementById('tradeForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    console.log('Form submission started');
    
    const trade = {
        asset_name: document.getElementById('assetName').value,
        quantity: document.getElementById('quantity').value,
        price: document.getElementById('price').value,
        trade_time: document.getElementById('tradeTime').value,
        trader_id: document.getElementById('traderId').value
    };

    console.log('Trade data:', trade);

    try {
        console.log('Submitting trade...');
        await submitTrade(trade);
        console.log('Trade submitted, fetching portfolio...');
        await fetchAndDisplayPortfolio(trade.trader_id);
        console.log('Portfolio fetched and displayed');
    } catch (error) {
        console.error('Error during form submission:', error);
    }
});

async function submitTrade(trade) {
    const response = await fetch('/trades', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(trade)
    });
    
    if (!response.ok) {
        throw new Error(`Failed to submit trade: ${response.statusText}`);
    }
    
    return await response.json();
}

async function fetchAndDisplayPortfolio(traderId) {
    const portfolioDiv = document.getElementById('portfolio');
    portfolioDiv.innerHTML = '<p>Loading portfolio data...</p>';
    
    try {
        // Fetch portfolio data
        const response = await fetch(`/portfolio/${traderId}`);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch portfolio: ${response.statusText}`);
        }
        
        const portfolio = await response.json();
        
        // Display portfolio
        portfolioDiv.innerHTML = '';
        
        const header = document.createElement('h2');
        header.textContent = `Portfolio for Trader ${traderId}`;
        portfolioDiv.appendChild(header);
        
        if (portfolio.positions && portfolio.positions.length > 0) {
            const table = document.createElement('table');
            table.classList.add('portfolio-table');
            
            // Create header row
            const headerRow = table.insertRow();
            ['Symbol', 'Quantity', 'Average Price', 'Current Value'].forEach(text => {
                const th = document.createElement('th');
                th.textContent = text;
                headerRow.appendChild(th);
            });
            
            // Create data rows
            portfolio.positions.forEach(position => {
                const row = table.insertRow();
                
                const symbolCell = row.insertCell();
                symbolCell.textContent = position.symbol;
                
                const quantityCell = row.insertCell();
                quantityCell.textContent = position.quantity;
                
                const priceCell = row.insertCell();
                priceCell.textContent = `$${parseFloat(position.average_price).toFixed(2)}`;
                
                const valueCell = row.insertCell();
                const value = position.quantity * position.average_price;
                valueCell.textContent = `$${value.toFixed(2)}`;
            });
            
            // Add total row
            const totalRow = table.insertRow();
            const totalLabelCell = totalRow.insertCell();
            totalLabelCell.textContent = 'Total Portfolio Value:';
            totalLabelCell.colSpan = 3;
            totalLabelCell.style.textAlign = 'right';
            totalLabelCell.style.fontWeight = 'bold';
            
            const totalValueCell = totalRow.insertCell();
            totalValueCell.textContent = `$${parseFloat(portfolio.total_value).toFixed(2)}`;
            totalValueCell.style.fontWeight = 'bold';
            
            portfolioDiv.appendChild(table);
        } else {
            const message = document.createElement('p');
            message.textContent = 'No positions in portfolio.';
            portfolioDiv.appendChild(message);
        }
    } catch (error) {
        console.error('Error fetching portfolio:', error);
        portfolioDiv.innerHTML = `<p class="error">Error loading portfolio: ${error.message}</p>`;
    }
}