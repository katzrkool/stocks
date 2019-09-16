const SEC_FEE_PER_DOLLAR = parseFloat(document.getElementById('sec_fee').textContent);

async function update_current_price(stock_id, button) {
    const stock_container = document.getElementById(stock_id)
    const ticker = stock_container.querySelector('.ticker').textContent;

    // Hit my api to get latest data
    // And any viewers, please don't use my API, i've got a small rate limit
    // Instead, check out AlphaVantage! They've got a free API key, and good real time data
    // They're what I'm using
    let path_name = window.location.pathname.replace('/demo', '');
    if (path_name == '/') path_name = '';

    const response = await fetch(`${path_name}/price?ticker=${ticker}`);
    if (response.status == 503) {
        window.alert('Sorry! I\'ve used up my limit on fetching stock data! Refresh and try again in 60 seconds. :)');
        return false;
    }
    button.style.display = 'none';
    const price = parseFloat((await response.json()).price);

    // Get the element that holds the current price data. 
    const price_element = stock_container.querySelector('.current_price');
    // const previous_price = price_element.textContent;

    // Updating the last updated text
    stock_container.querySelector('.last_updated').textContent = 
        `(as of ${(new Date()).toLocaleString()})`;

    // Updating the current price
    price_element.textContent = '$' + price;

    // Get if the position is long or short
    const position = stock_container.querySelector('.position').textContent;

    // Now for gains/losses, so start by getting purchase price
    const purchase_price = parseFloat(stock_container.querySelector('.purchase_price').textContent)

    let difference = price - purchase_price;

    // Make the difference negative of what it is if we are short
    if (position.toLowerCase().trim() == 'short') difference = -difference;

    const difference_percent = (price / purchase_price - 1)

    const formatted_difference_percent = String((difference_percent * 100).toFixed(3)).replace('-', '');

    // Update the color of gains/losses
    stock_container.querySelector('.gainslosses').className = 
        `gainslosses ${difference < 0 ? "negative" : "positive"}`;

    // Update the part that says up or down
    stock_container.querySelector('.updown').textContent = difference_percent < 0 ? "down": "up";

    // Update the percentage
    stock_container.querySelector('.gainslosses_percent').textContent = formatted_difference_percent;

    // Update the part that says profit or loss
    stock_container.querySelector('.profit_loss').textContent = difference < 0 ? "loss": "profit";

    // Get shares owned
    const shares_owned = parseFloat(stock_container.querySelector('.shares_owned').textContent)

    // Update the part that says in dollars how much we've profited / lost
    stock_container.querySelector('.profit_total').textContent = '$' + String((price * shares_owned * difference_percent).toFixed(2)).replace('-', '')

    // Update the part with Fees
    stock_container.querySelector('.profit_loss_sold').textContent = 
        ((price * shares_owned * difference_percent * (difference < 0 ? -1 : 1)) - ((SEC_FEE_PER_DOLLAR * shares_owned * price) + 10)).toFixed(2).replace('-', '');
}
