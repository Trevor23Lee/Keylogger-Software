import re
from collections import Counter

# Function to read the raw log file
def read_log_file(file_path):
    with open(file_path, "r") as file:
        return file.readlines()


# Function to remove timestamps and clean up lines
def clean_log_lines(log_lines):
    cleaned_lines = []
    
    first_line = log_lines[0].strip()  

    for line in log_lines[1:]:
        # Remove timestamp pattern 
        cleaned_line = re.sub(r".*?-", "", line).strip() 
        cleaned_lines.append(cleaned_line)
    
    return cleaned_lines, first_line


# Function to reconstruct the keystrokes into words
def reconstruct_text(cleaned_lines):
    text = ""
    for line in cleaned_lines:
        if line.startswith("Key.space"):
            text += " "
        elif line.startswith("Key.backspace"):
            text = text[:-1]
        elif line.startswith("Key.") or line == "Key.enter":  # Skip special keys
            continue
        else:
            text += line  # Add the valid keypresses (letters,numbers,punctuation)
    return text


# Function to extract words from the reconstructed text - also making sure URLs and emails stay constructed
def extract_words_and_urls(text):
    valid_domains = ['com', 'org', 'net', 'gov', 'edu', 'io', 'co', 'me', 'us']
    
    # Email pattern with regex: [words]@[words].[words]
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    
    # Modify the regex to match words, punctuation, and URLs
    words_and_urls = []
    words = re.findall(r"\b\w+\b|[.,!?;()/@&*^%#$~=+]", text)

    # Combine URLs as well as domains
    i = 0
    while i < len(words):
        if i + 2 < len(words) and words[i].isalpha() and words[i + 1] == "." and words[i + 2] in valid_domains:
            # This is a domain, treat it as a URL
            words_and_urls.append(words[i] + "." + words[i + 2])
            i += 3  

        elif i + 2 < len(words) and words[i].isalpha() and words[i + 1] == "@" and words[i + 2].isalpha():
            # This is an email, treat it as such
            words_and_urls.append(words[i] + "@" + words[i + 2])
            i += 3  
            
        else:
            words_and_urls.append(words[i])
            i += 1


    if i == len(words) - 1:  
        words_and_urls.append(words[i])

    return words_and_urls, emails


def get_only_words(text):
    # Extract words consisting of letters, digits, or underscores
    STOP_WORDS = {"a", "an", "and", "the", "is", "are", "of", "to", "in", "on", "for", "it", "with", "at", "by", "this"}
    words_only = re.findall(r'\b\w+\b', text)
    filtered_words = [word for word in words_only if word.lower() not in STOP_WORDS]
    return filtered_words

# Function to detect the most common word with it's count
def detect_most_common_word(words):
    
    word_counts = Counter(words)
    most_common_word, count = word_counts.most_common(1)[0]  
    return most_common_word, count


# Function to detect URLs
def detect_urls(words):
    # URL pattern without the '@' symbol, allowing for domains like example.com
    url_pattern = re.compile(r'\b(?:[a-zA-Z0-9-]+\.)+(?:com|org|net|gov|edu|io|co|me|us)\b')

    urls = []
    for word in words:
        # Exclude words containing '@' to prevent emails from being detected as URLs
        if '@' not in word and url_pattern.match(word):
            urls.append(word)
    
    return urls


# Function to detect passwords (odd letters combined with numbers and special characters)
def detect_passwords(text):
    password_pattern = r"\b[A-Za-z0-9!@#$%^&*()_+={}\[\]:;'\"<>,.?/\\|-]*\d+[A-Za-z0-9!@#$%^&*()_+={}\[\]:;'\"<>,.?/\\|-]+\b"
    passwords = [word for word in text.split() if re.match(password_pattern, word)]
    return passwords


# Function to output the extracted words to a file
def output_to_file(words, first_line, output_file, most_common_word, count, urls, passwords, emails):
    with open(output_file, "w") as file:
        # Write the first line (timestamp)
        file.write(first_line + "\n\n")
        
        # Write the reconstructed words at the top
        file.write(" ".join(words) + "\n")
        file.write("---------------------------------------------------------------\n\n")
        
        # Most common word
        file.write(f"Most common word: '{most_common_word}' (appears {count} times)\n")
        file.write("---------------------------------------------------------------\n\n")        
        # URLs section
        if urls:
            file.write(f"URLs Found: {urls}\n")
        else:
            file.write("No URLs Found.\n")
        file.write("---------------------------------------------------------------\n\n")        
        # Passwords section
        if passwords:
            file.write(f"Potential Passwords found: {passwords}\n")
        else:
            file.write("No Passwords detected.\n")
        file.write("---------------------------------------------------------------\n\n")        
        # Emails section
        if emails:
            file.write(f"Emails Found: {emails}\n")
        else:
            file.write("No Emails Found.\n")
        file.write("---------------------------------------------------------------\n\n")




def main():
    input_file = "raw_log.txt"  
    output_file = "extracted_words.txt"  

    log_lines = read_log_file(input_file)
    
    cleaned_lines, first_line = clean_log_lines(log_lines)

    reconstructed_text = reconstruct_text(cleaned_lines)

    passwords = detect_passwords(reconstructed_text)

    all_words,emails = extract_words_and_urls(reconstructed_text)

    cleaned_words = get_only_words(reconstructed_text)

    most_common_word, count = detect_most_common_word(cleaned_words)

    urls = detect_urls(all_words)

    output_to_file(all_words, first_line, output_file, most_common_word, count, urls, passwords, emails)
    print(f"Words have been output to {output_file}")

if __name__ == "__main__":
    main()
