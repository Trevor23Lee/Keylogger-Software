import re
from collections import Counter

# Function to read the raw log file
def read_log_file(file_path):
    with open(file_path, "r") as file:
        return file.readlines()

# Function to remove timestamps and clean up lines
def clean_log_lines(log_lines):
    cleaned_lines = []
    
    first_line = log_lines[0].strip()  # Timestamp line

    for line in log_lines[1:]:
        # Remove timestamp pattern (assuming timestamps are at the start of each line)
        cleaned_line = re.sub(r".*?-", "", line).strip()  # Timestamp regex
        cleaned_lines.append(cleaned_line)
    
    return cleaned_lines, first_line

# Function to reconstruct the keystrokes into words
def reconstruct_text(cleaned_lines):
    text = ""
    for line in cleaned_lines:
        if line.startswith("Key.space"):
            text += " "
        elif line.startswith("Key.") or line == "Key.enter":  # Skip special keys
            continue
        else:
            text += line  # Add the valid keypresses (letters/numbers/punctuation)
    return text

# Function to extract words from the reconstructed text
def extract_words_and_urls(text):
    # List of valid domain extensions we are interested in
    valid_domains = ['com', 'org', 'net', 'gov', 'edu', 'io', 'co', 'me', 'us']
    
    # Modify the regex to match words, punctuation, and URLs (even when split by space)
    words_and_urls = []
    words = re.findall(r"\b\w+\b|[.,!?;()/@]", text)
    
    # Combine "word . com", "word . org", etc., into one single word if it's a valid domain
    i = 0
    while i < len(words) - 1:
        if words[i].isalpha() and words[i + 1] == "." and i + 2 < len(words) and words[i + 2] in valid_domains:
            # Join word + valid domain as a single URL
            words_and_urls.append(words[i] + "." + words[i + 2])
            i += 3  # Skip the next two items (the dot and the domain extension)
        else:
            words_and_urls.append(words[i])
            i += 1
    if i == len(words) - 1:  # If there's only one word left, add it to the list
        words_and_urls.append(words[i])

    return words_and_urls

# Function to detect the most common word
def detect_most_common_word(words):
    word_counts = Counter(words)
    most_common_word, count = word_counts.most_common(1)[0]  # Get the most common word and its count
    return most_common_word, count

# Function to detect URLs
def detect_urls(words):
    # List of valid domain extensions we are interested in
    valid_domains = ['com', 'org', 'net', 'gov', 'edu', 'io', 'co', 'me', 'us']
    
    urls = []
    for word in words:
        # Check if the word contains any valid domain
        for domain in valid_domains:
            if domain in word:
                urls.append(word)
                break  # If a valid domain is found, no need to check further
    
    return urls


# Function to detect passwords (odd letters combined with numbers and special characters)
def detect_passwords(text):
    # Detect potential passwords in raw text, including special characters
    password_pattern = r"\b[A-Za-z0-9!@#$%^&*()_+={}\[\]:;'\"<>,.?/\\|-]*\d+[A-Za-z0-9!@#$%^&*()_+={}\[\]:;'\"<>,.?/\\|-]+\b"
    passwords = [word for word in text.split() if re.match(password_pattern, word)]
    return passwords

# Function to output the extracted words to a file
def output_to_file(words, first_line, output_file, most_common_word, count, urls, passwords):
    with open(output_file, "w") as file:
        file.write(first_line + "\n\n")  # Write the first line separately
        file.write(" ".join(words))  # Join the words with a space between them and write to the file
        file.write("\n----------------------------------------\n\n")

        file.write(f"Most common word: '{most_common_word}' (appears {count} times)")

        file.write("\n----------------------------------------\n\n")

        if urls:
            file.write(f"URLs Found: {urls}")
        else:
            file.write("No URLs Found.")

        file.write("\n----------------------------------------\n\n")

        if passwords:
            file.write(f"Potential Passwords found: {passwords}")
        else:
            file.write("No Passwords detected.")

# Main program
def main():
    input_file = "raw_log.txt"  # Path to your raw log file
    output_file = "extracted_words.txt"  # Output file to store the extracted words

    log_lines = read_log_file(input_file)
    
    # Step 1: Clean log lines by removing timestamps
    cleaned_lines, first_line = clean_log_lines(log_lines)

    # Step 2: Reconstruct the text from keystrokes
    reconstructed_text = reconstruct_text(cleaned_lines)

    # Step 3: Detect passwords from the raw reconstructed text
    passwords = detect_passwords(reconstructed_text)

    # Step 4: Extract words from the reconstructed text
    all_words = extract_words_and_urls(reconstructed_text)

    # Step 5: Detect the most common word
    most_common_word, count = detect_most_common_word(all_words)

    # Step 6: Detect any URLs
    urls = detect_urls(all_words)

    # Step 7: Output the words to a file
    output_to_file(all_words, first_line, output_file, most_common_word, count, urls, passwords)
    print(f"Words have been output to {output_file}")

if __name__ == "__main__":
    main()
