# For RSS feed
import feedparser
from datetime import datetime, timedelta
import sys
import os
# For Azure OpenAI
from openai import AzureOpenAI
from dotenv import load_dotenv
import prompts
import json
# For Jinja2
from jinja2 import Template
import random
# Dalle
import requests



def fetch_rss_feed(url):
    return feedparser.parse(url)

def is_specific_month(entry_date, year, month):
    first_day_of_specific_month = datetime(year, month, 1)
    if month == 12:
        first_day_of_next_month = datetime(year + 1, 1, 1)
    else:
        first_day_of_next_month = datetime(year, month + 1, 1)
    last_day_of_specific_month = first_day_of_next_month - timedelta(days=1)
    
    return first_day_of_specific_month <= entry_date <= last_day_of_specific_month

def get_month_word(month):
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    if 1 <= month <= 12:
        return months[month - 1]
    else:
        raise ValueError("Month must be between 1 and 12")

def main(date_str):
    rss_url = "https://www.microsoft.com/releasecommunications/api/v2/azure/rss"
    feed = fetch_rss_feed(rss_url)
    
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")       
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        sys.exit(1)
    
    year = date.year
    month = date.month
    update_count = 0
    entries_str = ""  
    
    # Keep only the first Category
    entries_list = []

    for entry in feed.entries:
        entry_date = datetime(*entry.published_parsed[:6])
        if is_specific_month(entry_date, year, month):
            categories = [category.term for category in entry.tags if 'tags' in entry and category.term not in ['Launched', 'In preview', 'In development']]
            first_category = categories[0] if categories else 'N/A'
            entry_info = {
                "Published": entry.published,
                "Link": entry.link,
                "Title": entry.title,
                "Category": first_category
            }
            entries_list.append(entry_info)

    entries_str = json.dumps(entries_list, indent=4)
    # Remove duplicates based on title
    seen_titles = set()
    unique_entries_list = []
    for entry in entries_list:
        if entry["Title"] not in seen_titles:
            unique_entries_list.append(entry)
            seen_titles.add(entry["Title"])

    entries_str = json.dumps(unique_entries_list, indent=4)
    
    # Modify the JSON to replace Title with Link in the format [Title](Link)
    for entry in unique_entries_list:
        entry["Link"] = f"[{entry.pop('Title')}]({entry['Link']})"

    entries_str = json.dumps(unique_entries_list, indent=4)
    
    # Sort entries by category names
    unique_entries_list.sort(key=lambda x: x["Category"])

    # Convert the sorted list back to JSON string
    entries_str = json.dumps(unique_entries_list, indent=4)
    
    # print(entries_str)
    update_count = len(unique_entries_list)
   
    # Get configuration settings
    load_dotenv()
    azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
    azure_oai_key = os.getenv("AZURE_OAI_KEY")
    azure_oai_deployment = os.getenv("AZURE_OAI_DEPLOYMENT")

    # Initialize the Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint=azure_oai_endpoint,
        api_key=azure_oai_key,
        api_version="2024-02-15-preview"
    )

    # Generate the prompt
    system_message = prompts.system_message
    prompt = prompts.generate_prompt(entries_str, update_count)

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ]

    # print("Prompt: " + prompt)
    # print("Number of updates: " + str(update_count))
    
    # Send request to Azure OpenAI model
    response = client.chat.completions.create(
        model=azure_oai_deployment,
        temperature=0,
        max_tokens=16384,
        top_p=1,
        messages=messages
    )
    generated_text = response.choices[0].message.content

    # # Print the response
    # print("Response: " + generated_text + "\n")

    # Remove characters in the beginning of each line until the first "-" but keep the "-" and the space after it
    cleaned_text = "\n".join("- " + line.split("-", 1)[-1].strip() if "-" in line else line for line in generated_text.split("\n"))

    # Print the cleaned response
    print("Cleaned Response: " + cleaned_text + "\n")
   
    # Load the Markdown template
    with open("scripts/azure-monthly-updates-template.j2", "r") as template_file:
        template_content = template_file.read()
    template = Template(template_content)
    
    print("Rendering template...")
    rendered_template = template.render(MonthYear=get_month_word(month), Links=cleaned_text, RandomImage=random.randint(1, 55))
    print("Template rendered successfully.")
    
    #########
    # Dalle #
    #########
    dalle_client = AzureOpenAI(
        azure_endpoint=azure_oai_endpoint,
        api_key=azure_oai_key,
        api_version="2024-02-15-preview"
    )

    result = dalle_client.images.generate(
        model="Dalle3", # the name of your DALL-E 3 deployment
        prompt=prompts.generate_prompt_dalle(get_month_word(month)),
        size="1024x1024",
        n=1
    )
    
    json_response = json.loads(result.model_dump_json())

    # Set the directory for the stored image
    image_dir = os.curdir

    # Initialize the image path (note the filetype should be png)
    image_path = os.path.join(image_dir, 'cover.png')

    # Retrieve the generated image
    image_url = json_response["data"][0]["url"]  # extract image URL from response
    generated_image = requests.get(image_url).content  # download the image
    with open(image_path, "wb") as image_file:
        image_file.write(generated_image)
        
    image_url = json.loads(result.model_dump_json())['data'][0]['url']
    
    print("Image URL: " + image_url)
    
    # Check if the blog directory already exists, otherwise create it
    blog_dir = "blog/"

    # Check if the file already exists in the blog directory
    matching_dirs = [d for d in os.listdir(blog_dir) if 
                    os.path.isdir(os.path.join(blog_dir, d)) and 
                    f"azure_updates_{month}" in d]

    # If a directory already exists for this month, use it
    if matching_dirs:
        existing_dir = matching_dirs[0]
        existing_prefix = existing_dir.split("_")[0]
        output_dir = os.path.join(blog_dir, existing_dir)
    else:
        # If no directory exists for this month, create a new one
        # Get all existing numeric prefixes (XXX_)
        existing_prefixes = []
        for d in os.listdir(blog_dir):
            if os.path.isdir(os.path.join(blog_dir, d)) and len(d) >= 4:
                prefix = d.split('_')[0]
                if prefix.isdigit() and len(prefix) == 3:
                    existing_prefixes.append(int(prefix))
        
        # Increment the highest prefix found
        highest_prefix = max(existing_prefixes) if existing_prefixes else 0
        new_prefix = str(highest_prefix + 1).zfill(3)
        output_dir = os.path.join(blog_dir, f"{new_prefix}_azure_updates_{month}_{year}")
        os.makedirs(output_dir)
        existing_prefix = new_prefix

    # Write the content to a Markdown file in the output directory
    output_file_path = os.path.join(output_dir, f"{existing_prefix}_azure_updates_{month}_{year}.md")
    print(f"Writing content to Markdown file: {output_file_path}")
    with open(output_file_path, "w") as output_file:
        output_file.write(rendered_template)
    print("Content written to Markdown file successfully.")

    # Move the generated image cover.png into the output directory
    new_image_path = os.path.join(output_dir, 'cover.png')
    os.rename(image_path, new_image_path)
    print(f"Image moved to: {new_image_path}")

    # Create the index.md file in the output directory
    index_file_path = os.path.join(output_dir, "index.md")
    print(f"Creating index file: {index_file_path}")
    with open(index_file_path, "w") as index_file:
        index_file.write("---\n# skip this file to not create an empty blog with the name of the folder\nskip_file: yes\n---\n")
    print("Index file created successfully.")
    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python rss_to_markdown-new.py <YYYY-MM-DD>")
        sys.exit(1)
    
    date_str = sys.argv[1]
    main(date_str)


