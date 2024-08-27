from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = Flask(__name__)

def get_share_counts(url):
    # Set up Chrome options to run in headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize the WebDriver with the Chrome options
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Navigate to the website
        driver.get("https://www.shareaholic.com/sharecounter/")

        # Locate the input field using its XPath
        input_field = driver.find_element(By.XPATH, '//*[@id="page_content"]/div/div[3]/div[1]/div/form/div[1]/input')

        # Enter the link into the input field
        input_field.send_keys(url)

        # Wait until the 'Analyze' button is clickable
        analyze_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="submit"]'))
        )

        # Click the button using JavaScript to avoid any interception issues
        driver.execute_script("arguments[0].click();", analyze_button)

        # Wait for the table to load
        time.sleep(5)  # Adjust the sleep time as necessary for your internet speed

        # Locate the table using its XPath
        table = driver.find_element(By.XPATH, '//*[@id="page_content"]/div/div[3]/div[3]/div/table/tbody')

        # Extract rows from the table
        rows = table.find_elements(By.TAG_NAME, "tr")

        # Create a dictionary to store the results
        share_counts = {}

        for row in rows:
            # Get the platform and its counts
            cols = row.find_elements(By.TAG_NAME, "td")
            platform = cols[0].text
            shares = cols[1].text
            
            # Store the results in the dictionary
            share_counts[platform] = shares

    finally:
        # Close the WebDriver
        driver.quit()

    # Prepare the result string
    result = f"""
    Total:         {share_counts.get('Total', 0)}
    Facebook:      {share_counts.get('Facebook', 0)}
    Pinterest:     {share_counts.get('Pinterest', 0)}
    Buffer:        {share_counts.get('Buffer', 0)}
    Odnoklassniki: {share_counts.get('Odnoklassniki', 0)}
    Reddit:        {share_counts.get('Reddit', 0)}
    Tumblr:        {share_counts.get('Tumblr', 0)}
    VK:            {share_counts.get('VK', 0)}
    Yummly:        {share_counts.get('Yummly', 0)}
    """
    return result

@app.route('/get_share_counts', methods=['POST'])
def share_counts():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    # Get the share counts for the provided URL
    share_counts = get_share_counts(url)
    return share_counts

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
