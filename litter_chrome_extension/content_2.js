// Function to extract brand name from the page
function extractBrandName() {
    const brandElement = document.querySelector('span.a-size-base.po-break-word');
    if (brandElement) {
        return brandElement.textContent.trim();
    } else {
        console.log('Brand element not found');
        return null;
    }
}

// Function to fetch data from the API
async function fetchBrandScore(brandName) {
    const formattedBrandName = brandName.replace(/\s+/g, '');
    const url = `https://qbusio98ha.execute-api.us-east-1.amazonaws.com/litter-logo-api?brand_name=${formattedBrandName}`;
    
    try {
        const response = await fetch(url);
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
function displayBrandScore(data, element, brandName) {
    // Function to format brand name: capitalize first letter of each word and remove symbols
    function formatBrandName(name) {
        return name
            .replace(/[_,]/g, ' ')  // Replace underscores and commas with spaces
            .replace(/\s+/g, ' ')   // Replace multiple spaces with a single space
            .trim()                 // Remove leading and trailing whitespace
            .split(' ')             // Split into words
            .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())  // Capitalize first letter of each word
            .join(' ');             // Join words back together
    }

    if (data && data.brand_name) {
        const formattedBrandName = formatBrandName(data.brand_name);
        element.innerHTML = `Based on the images collected by environmentalists across the country through Open Litter Map US, ${formattedBrandName} ranks as the ${data.brand_rank}th most polluting brand. 
        This ranking reflects the significant environmental impact of their waste, with a lower ranking indicating higher pollution levels. 
        We identified ${data.brand_im_count} images of ${formattedBrandName} litter out of a total of ${data.tot_im_count} collected. Our model estimates this with ${data.coconfidence}.
        <br>Join the initiative to combat plastic pollution by capturing and uploading pictures of litter you encounter. Your contribution can make a difference. Upload your images <a href="https://openlittermaplitterlog.streamlit.app/" target="_blank">here</a>.`;
    } else {
        const formattedBrandName = formatBrandName(brandName);
        element.innerHTML = `We currently don't have enough data on ${formattedBrandName} to determine its pollution impact. 
        You can help change that by joining our initiative to combat plastic pollution.
        Capture and upload pictures of litter you encounter to make a difference. Upload your images <a href="https://openlittermaplitterlog.streamlit.app/" target="_blank">here</a>.`;
    }
}

// Main function to run the extension
async function main() {
    if (document.getElementById('brandScoreInfo')) {
        return;
    }
    const brandName = extractBrandName();
    if (brandName) {
        console.log('Extracted brand name:', brandName);
        const productTitle = document.querySelector('#productTitle');
        if (productTitle) {
            const scoreElement = document.createElement('div');
            scoreElement.id = 'brandScoreInfo';
            //scoreElement.style.cssText = 'width: 1000px; background-color: white; border: 2px solid green; padding: 10px; overflow-y: auto; margin-top: 10px;';
            productTitle.parentNode.insertBefore(scoreElement, productTitle.nextSibling);
            
            try {
                const response = await fetch(`https://qbusio98ha.execute-api.us-east-1.amazonaws.com/litter-logo-api?brand_name=${brandName.replace(/\s+/g, '_')}`);
                const data = await response.json();
                displayBrandScore(data, scoreElement);
            } catch (error) {
                console.error('Fetch error:', error);
                scoreElement.innerHTML = 'An error occurred while fetching brand information.';
            }
        } else {
            console.log('Product title element not found');
        }
    } else {
        console.log('Brand name could not be extracted');
    }
}

// Run the main function when the page is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', main);
} else {
    main();
}