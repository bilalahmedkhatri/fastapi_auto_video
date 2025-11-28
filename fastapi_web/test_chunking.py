import re

text = """Hello world, Welcome back to your daily global update — the top 10 headlines you need to know today in just one minute. Let's dive straight in

Guinea-Bissau swears in a general as transitional president amid election disputes.
Russia Ukraine tensions rise as Moscow threatens new hypersonic strikes.
Israel accuses Hezbollah of breaking the ceasefire deal in Lebanon.
Hong Kong mourns after a deadly blaze claims 65 lives.
France launches a voluntary military service program to boost national defense.
Pope Leo begins his first overseas trip in Turkey, calling for peace and unity.
World leaders strengthen climate pledges under the Paris Agreement.
Breakthroughs in AI, medicine, and space exploration spark global optimism.
US President Donald Trump's new trade and immigration policies reshape global debate.
Peace talks emerge across conflict zones, though skepticism remains high.

And that's your one-minute world roundup. If you found this useful, don't forget to hit like, share with friends, and subscribe for tomorrow's headlines. Stay informed, stay connected see you in the next update!"""

print(f"Original text length: {len(text)} chars\n")

# Normalize whitespace
text = re.sub(r'\n\s*\n+', '\n\n', text)
text = re.sub(r'[ \t]+', ' ', text)

# Split pattern
pattern = r'(?<=[.!?])(?:\s+)(?=[A-Z])|(?:\n\n)|(?:\n)(?=[A-Z])'
sentences = re.split(pattern, text)
sentences = [s.strip() for s in sentences if s.strip()]

print(f"Total sentences: {len(sentences)}\n")

# Chunk logic
chunks = []
current_chunk = ""
max_chunk_size = 400

for sentence in sentences:
    if len(current_chunk) + len(sentence) + 1 > max_chunk_size:
        if current_chunk:
            chunks.append(current_chunk.strip())
        current_chunk = sentence
    else:
        current_chunk += (" " if current_chunk else "") + sentence

if current_chunk:
    chunks.append(current_chunk.strip())

print(f"Total chunks: {len(chunks)}\n")
print("=" * 80)

for i, chunk in enumerate(chunks):
    print(f"\nChunk {i+1} ({len(chunk)} chars):")
    print(chunk)
    print("-" * 80)
