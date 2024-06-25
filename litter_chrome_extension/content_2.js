document.addEventListener('DOMContentLoaded', async () => {
    const bylineInfo = document.querySelector('#bylineInfo');
    console.log('BylineInfo:', bylineInfo);

    if (bylineInfo) {
        let hrefArray = bylineInfo.textContent.trim().split(' ');

        if (hrefArray[0] === 'Visit') {
            hrefArray = hrefArray.slice(2, -1);
        } else {
            hrefArray = hrefArray.slice(1);
        }

        const href = hrefArray.join('_');
        console.log('Brand Name:', href);

        // Call the function to fetch and display the brand score
        fetchBrandScore(href);
    } else {
        console.log('Byline info not found');
        displayError('Byline info not found');
    }

    // Function to fetch data from the API
    async function fetchBrandScore(brandName) {
        const proxyUrl = 'https://cors-anywhere.herokuapp.com/';
        const url = `${proxyUrl}https://qbusio98ha.execute-api.us-east-1.amazonaws.com/litter-logo-api?brand_name=${brandName}`;
        
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            displayBrandScore(data);
        } catch (error) {
            console.error('There has been a problem with your fetch operation:', error);
            displayNoScore(brandName);
        }
    }

    // Function to display the brand score
    function displayBrandScore(data) {
        const { brand_name, brand_score } = data;
        let resultDiv = document.getElementById('result');
        if (!resultDiv) {
            resultDiv = document.createElement('div');
            resultDiv.id = 'result';
            resultDiv.style.cssText = 'margin-top: 10px;';
            document.body.appendChild(resultDiv);
        }
        if (brand_name && brand_score) {
            resultDiv.innerHTML = `Based on our research, ${brand_name}'s brand score is ${brand_score}. Find out more about the brand score <a href="#">here</a>.`;
        } else {
            displayNoScore(brand_name);
        }
    }

    // Function to display a message when there is no score
    function displayNoScore(brandName) {
        let resultDiv = document.getElementById('result');
        if (!resultDiv) {
            resultDiv = document.createElement('div');
            resultDiv.id = 'result';
            resultDiv.style.cssText = 'margin-top: 10px;';
            document.body.appendChild(resultDiv);
        }
        resultDiv.innerHTML = `We currently don't have a litter score for ${brandName} but you can learn more about the litter score <a href="#">here</a>.`;
    }

    // Function to display an error message
    function displayError(message) {
        let resultDiv = document.getElementById('result');
        if (!resultDiv) {
            resultDiv = document.createElement('div');
            resultDiv.id = 'result';
            resultDiv.style.cssText = 'margin-top: 10px;';
            document.body.appendChild(resultDiv);
        }
        resultDiv.innerHTML = message;
    }
});

