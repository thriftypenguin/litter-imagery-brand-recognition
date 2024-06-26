// Function to fetch data from the API
async function fetchBrandScore(brandName) {
    const proxyUrl = 'https://cors-anywhere.herokuapp.com/';
    const url = `${proxyUrl}https://qbusio98ha.execute-api.us-east-1.amazonaws.com/litter-logo-api?brand_name=${brandName}`;
    
    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('There has been a problem with your fetch operation:', error);
        return null;
    }
}

// Function to display the brand score
function displayBrandScore(data, element) {
    if (data && data.brand_name && data.brand_score) {
        element.innerHTML = `Based on our research, ${data.brand_name}'s brand score is ${data.brand_score}. Find out more about the brand score <a href="#">here</a>.`;
    } else {
        element.innerHTML = `We currently don't have a litter score for this brand but you can learn more about the litter score <a href="#">here</a>.`;
    }
}

// Function to extract brand name from Amazon page
function extractBrandName() {
    const bylineInfo = document.getElementById('bylineInfo');
    console.log('BylineInfo:', bylineInfo);  // Debug output
    if (bylineInfo) {
        let href = bylineInfo.textContent.split(' ');
        if (href[0] === 'Visit') {
            href = href.slice(2, -1);
        } else {
            href = href.slice(1);
        }
        return href.join('_').toLowerCase();
    }
    return null;
}

// Main function to run the extension
async function main() {
    // Check if we've already added the brand score info
    if (document.getElementById('brandScoreInfo')) {
        return;
    }

    const brandName = extractBrandName();
    if (brandName) {
        const bylineInfo = document.getElementById('bylineInfo');
        const scoreElement = document.createElement('div');
        scoreElement.id = 'brandScoreInfo';
        scoreElement.style.marginTop = '10px';
        bylineInfo.parentNode.insertBefore(scoreElement, bylineInfo.nextSibling);

        const data = await fetchBrandScore(brandName);
        displayBrandScore(data, scoreElement);
    }
}

// Function to run main() once the bylineInfo element is available
function waitForBylineInfo() {
    const bylineInfo = document.getElementById('bylineInfo');
    if (bylineInfo) {
        main();
    } else {
        requestAnimationFrame(waitForBylineInfo);
    }
}

// Start waiting for the bylineInfo element as soon as possible
waitForBylineInfo();