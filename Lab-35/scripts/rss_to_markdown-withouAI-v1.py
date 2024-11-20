import os
import feedparser
import random
from datetime import datetime, timedelta
from jinja2 import Template
from sys import argv


def fetch_rss(previous_month):
    # RSS feed URL
    #rss_url = "https://azurecomcdn.azureedge.net/en-us/updates/feed/?category=featured%2Cai-machine-learning%2Canalytics%2Cblockchain%2Ccompute%2Ccontainers%2Cdatabases%2Cdeveloper-tools%2Cdevops%2Chybrid-multicloud%2Cidentity%2Cintegration%2Ciot%2Cmanagement-tools%2Cmedia%2Cmigration%2Cmixed-reality%2Cmobile%2Cnetworking%2Csecurity%2Cstorage%2Cwindows-virtual-desktop%2Cweb&status=nowavailable%2Cinpreview%2Cindevelopment"
    rss_url = "https://www.microsoft.com/releasecommunications/api/v2/azure/rss"

    # Fetching the RSS feed
    print("Fetching RSS feed...")
    feed = feedparser.parse(rss_url)
    print("RSS feed fetched successfully.")

    # Getting the current date and the previous month
    print("Previous month:", previous_month)

    # Convert the month to full format (ex: "April" instead of "Apr")
    previous_month_str = previous_month.strftime("%B %Y")

    # Load the Markdown template
    with open("scripts/azure-monthly-updates-template.j2", "r") as template_file:
        template_content = template_file.read()
    template = Template(template_content)

    # Initialize a dictionary to store links by category
    links_by_category = {}

    # Iterate through the entries in the RSS feed
    for entry in feed.entries:
        # Convert the publication date to a datetime object
        pub_date = datetime.strptime(entry.published[:-2], "%a, %d %b %Y %H:%M:%S")
        # Check if the article was published in the previous month
        if pub_date.year == previous_month.year and pub_date.month == previous_month.month:
            # Identify the category of the article
            title_lower = entry.title.lower()
            category = None
            if any(keyword in title_lower for keyword in ["aks", "kubernetes", "openshift"]):
                category = "AKS"
            elif any(keyword in title_lower for keyword in ["acr", "azure container registry"]):
                category = "ACR"
            elif any(keyword in title_lower for keyword in ["azure container apps"]):
                category = "ACA"
            elif any(keyword in title_lower for keyword in ["azure key vault"]):
                category = "Key Vault"
            elif any(keyword in title_lower for keyword in ["azure functions"]):
                category = "Functions"
            elif any(keyword in title_lower for keyword in ["monitor", "prometheus"]):
                category = "Monitoring"
            elif any(keyword in title_lower for keyword in ["azure container storage", "azure files", "azure blob storage", "azure storage", "azure data box", "ultra disk storage"]):
                category = "Storage"
            elif any(keyword in title_lower for keyword in ["expressroute", "application gateway", "virtual network"]):
                category = "Networking"
            elif any(keyword in title_lower for keyword in ["virtual machine", "vms"]):
                category = "Compute"
            elif any(keyword in title_lower for keyword in ["openai", "machine learning", "virtual private network"]):
                category = "AI"
            elif any(keyword in title_lower for keyword in ["appservice", "app service"]):
                category = "App Service"
            elif any(keyword in title_lower for keyword in ["cosmos", "sql"]):
                category = "Database"
            else:
                category = "Others"

            # Add the link to the corresponding list in the dictionary
            if category in links_by_category:
                links_by_category[category].append(f"- [{entry.title}]({entry.link})")
            else:
                links_by_category[category] = [f"### {category}\n- [{entry.title}]({entry.link})"]

    # Build the links section with categories
    sorted_categories = sorted(links_by_category.keys(), key=lambda x: x.lower() if x != "Others" else "zzz")
    links_section = ""
    for category in sorted_categories:
        links_section += "\n".join(links_by_category[category]) + "\n"

    # Replace {# MonthYear #} in the template with the previous month and year
    # Replace {# Links #} in the template with the links
    print("Rendering template...")
    rendered_template = template.render(MonthYear=previous_month_str, Links=links_section, RandomImage=random.randint(1, 55))
    print("Template rendered successfully.")

    # Check if the blog directory already exists, otherwise create it
    blog_dir = "blog/"

    # Check if the file already exists in the blog directory
    matching_dirs = [d for d in os.listdir(blog_dir) if 
                    os.path.isdir(os.path.join(blog_dir, d)) and 
                    f"azure_updates_{previous_month.strftime('%m_%Y')}" in d]

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
        output_dir = os.path.join(blog_dir, f"{new_prefix}_azure_updates_{previous_month.strftime('%m_%Y')}")
        os.makedirs(output_dir)
        existing_prefix = new_prefix

    # Write the content to a Markdown file in the output directory
    output_file_path = os.path.join(output_dir, f"{existing_prefix}_azure_updates_{previous_month.strftime('%m_%Y')}.md")
    print(f"Writing content to Markdown file: {output_file_path}")
    with open(output_file_path, "w") as output_file:
        output_file.write(rendered_template)
    print("Content written to Markdown file successfully.")

    # Create the index.md file in the output directory
    index_file_path = os.path.join(output_dir, "index.md")
    print(f"Creating index file: {index_file_path}")
    with open(index_file_path, "w") as index_file:
        index_file.write("---\n# skip this file to not create an empty blog with the name of the folder\nskip_file: yes\n---\n")
    print("Index file created successfully.")

if __name__ == "__main__":
    # Check if a date was provided as an argument
    if len(argv) > 1:
        previous_month = datetime.strptime(argv[1], "%Y-%m-%d")
    else:
        # Use the previous date by default
        current_date = datetime.now()
        previous_month = current_date.replace(day=1) - timedelta(days=1)
    fetch_rss(previous_month)