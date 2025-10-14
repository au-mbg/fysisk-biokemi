import yaml
import re
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass
from shutil import copyfile

@dataclass
class Exercise:
    title: str
    categories: Optional[list[str]]
    topics: Optional[list[str]]
    datasets: Optional[list[str]] = None
    filepath: Path = None

def read_yaml_metadata(file_path: str) -> Exercise:
    """
    Read YAML frontmatter from a Quarto (.qmd) file.
    
    Args:
        file_path: Path to the .qmd file
        
    Returns:
        Dictionary containing the YAML metadata, or None if no metadata found
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Check if file starts with YAML frontmatter (---)
        if not content.startswith('---'):
            return None
        
        # Find the closing --- delimiter
        # Pattern: start with ---, capture everything until next --- on its own line
        pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(pattern, content, re.DOTALL)
        
        if not match:
            return None
        
        yaml_content = match.group(1)

        
        # Parse YAML
        metadata = yaml.safe_load(yaml_content)

        # Add file path to metadata
        file_path_obj = Path(file_path).resolve()
        metadata['filepath'] = file_path_obj
        return Exercise(**metadata)
        
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML in {file_path}: {e}")
        return None
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None
    
def generate_filename_part(title: str) -> str:
    """Generate a clean, readable filename part from exercise title."""
    
    # Convert to lowercase and replace special chars with spaces
    clean_title = re.sub(r'[^\w\s-]', ' ', title.lower())
    
    # Split into words and filter out short/common words
    stop_words = {'a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 'and', 'or', 'but'}
    words = [word.strip() for word in clean_title.split() if word.strip()]
    
    # Keep important words, truncate long ones intelligently
    filename_parts = []
    for word in words:
        if word in stop_words and len(filename_parts) > 0:
            continue  # Skip stop words unless it's the first word
        
        if len(word) <= 4:
            filename_parts.append(word)
        elif len(word) <= 8:
            filename_parts.append(word[:6])  # Keep more of medium words
        else:
            # For long words, try to find a good break point
            if '-' in word:
                filename_parts.append(word.split('-')[0][:6])
            else:
                filename_parts.append(word[:5])
    
    # Limit total length and join
    filename_parts = filename_parts[:4]  # Max 4 parts
    return '-'.join(filename_parts)


def strip_metadata(filepath):
    """Remove YAML frontmatter from a .qmd file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if not content.startswith('---'):
            return  # No frontmatter to strip
        
        pattern = r'^---\s*\n(.*?)\n---\s*\n'
        new_content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(new_content)
            
    except Exception as e:
        print(f"Error stripping metadata from {filepath}: {e}")


if __name__ == "__main__":

    files = Path.cwd().glob('old/week*/*.qmd')

    titles = []
    exercises = []

    for file in files:
        data = read_yaml_metadata(file)

        if data:
            if data.title not in titles:
                titles.append(data.title)
            else:                    
                print(f"Duplicate title found: {data.title}")
            exercises.append(data)


    directory = Path.cwd()
    for exercise in exercises: 
        human_title = generate_filename_part(exercise.title)
        categories = exercise.categories if exercise.categories else []
        # Sort categories to ensure consistent naming
        categories.sort()

        category_title = '-'.join(categories).lower() if categories else 'uncategorized'


        new_filename = f"{category_title}_{human_title}.qmd"
        print(f"{exercise.filepath.name}  -->  {new_filename}")

        new_path = directory / new_filename
        if new_path.exists():
            print(f"File already exists: {new_path}, skipping...")
            continue
        else:
            copyfile(exercise.filepath, new_path)
            strip_metadata(new_path)
