def clean_data(quotes):
    cleaned = []

    for q in quotes:
        if q["text"] and q["author"]:
            q["text"] = q["text"].strip()
            q["author"] = q["author"].strip()
            cleaned.append(q)

    return cleaned