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

        // Fetch data from the brand score API
        const proxyUrl = 'https://cors-anywhere.herokuapp.com/';
        const brandScoreUrl = `${proxyUrl}https://qbusio98ha.execute-api.us-east-1.amazonaws.com/litter-logo-api?brand_name=${href}`;

        try {
            const brandResponse = await fetch(brandScoreUrl);
            const brandResponseText = await brandResponse.text();
            if (!brandResponse.ok) {
                throw new Error(`Brand Score API response was not ok: ${brandResponse.statusText}`);
            }

            try {
                const brandData = JSON.parse(brandResponseText);
                const { brand_name, brand_score } = brandData;

                // Display brand score
                let resultDiv = document.getElementById('result');
                if (!resultDiv) {
                    resultDiv = document.createElement('div');
                    resultDiv.id = 'result';
                    resultDiv.style.cssText = 'margin-top: 10px;';
                    document.body.appendChild(resultDiv);
                }
                if (brand_name) {
                    resultDiv.innerHTML = `Based on our research, ${brand_name}'s brand score is ${brand_score}. Find out more about the brand score <a href="#">here</a>.`;
                } else {
                    resultDiv.innerHTML = `We currently don't have a litter score for ${brand_name} but you can learn more about the litter score <a href="#">here</a>.`;
                }
            } catch (jsonError) {
                console.error('JSON parse error:', jsonError);
                console.log('Brand Response Text:', brandResponseText);
                displayError('Failed to parse brand data.');
            }

        } catch (error) {
            console.error('Fetch error:', error.message);
            displayError(`An error occurred while fetching brand data: ${error.message}`);
        }
    } else {
        console.log('Byline info not found');
        displayError('Byline info not found');
    }

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

