system_message = """
    You are an assistant for a blog author. You are here to create a markdown block organized by categories. Display the result without the ```markdown``` code block.
"""

def generate_prompt(updates, update_count):   
    prompt = f""" 
       List exhaustively and concisely all {update_count} Azure updates ONCE based on the JSON displayed below. Do not omit ANY updates and do not exceed {update_count} entries. 
       Each entry MUST BE NUMBERED and have an existing category. Use ONLY existing Categories which are already sorted alphabetically.
       
       CRITICAL CHECKS:
       - Recheck the entire list for duplicates. If found, remove and replace with a missing update.
       
       Follow this STRICT markdown format for each update:
       ### Category
       1 - UPDATE1
       2 - UPDATE2
       
       ### Category
       3 - UPDATE3
       
       {updates}
             
    """
    return prompt

def generate_prompt_dalle(month):   
    prompt = f""" 
       3D render of an IT newspaper with Azure Updates as title in {month} atmosphere, digital art             
    """
    return prompt