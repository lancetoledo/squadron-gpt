import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding
import json
import random
from sklearn.model_selection import train_test_split

# Load spaCy model
nlp = spacy.blank("en")

# Create text classifier
textcat = nlp.add_pipe("textcat", last=True)
textcat.add_label("relationship_inquiry")
textcat.add_label("friend_inquiry")
textcat.add_label("general_inquiry")
textcat.add_label("feedback")  # Added new label

# Load training data
with open("training/training_data.json", "r") as file:
    TRAINING_DATA = json.load(file)

# Split data into training and validation sets
train_data, val_data = train_test_split(TRAINING_DATA, test_size=0.2, random_state=42)

# Format training data for spaCy
def format_data(data):
    formatted_data = []
    for item in data:
        doc = nlp.make_doc(item["text"])
        cats = {"relationship_inquiry": 0, "friend_inquiry": 0, "general_inquiry": 0, "feedback": 0}  # Updated categories
        cats[item["label"]] = 1
        formatted_data.append(Example.from_dict(doc, {"cats": cats}))
    return formatted_data

train_examples = format_data(train_data)
val_examples = format_data(val_data)

# Train the model
optimizer = nlp.begin_training()
optimizer.learn_rate = 0.0005  # Adjusted learning rate
best_loss = float('inf')
no_improvement_epochs = 0
patience = 20  # Adjusted patience for early stopping
n_epochs = 100  # Total number of epochs
dropout_rate = 0.6  # Increased dropout rate

for epoch in range(n_epochs):
    random.shuffle(train_examples)
    losses = {}
    batches = minibatch(train_examples, size=compounding(4.0, 32.0, 1.001))
    for batch in batches:
        nlp.update(batch, drop=dropout_rate, losses=losses, sgd=optimizer)

    # Calculate validation loss
    val_loss = 0
    for example in val_examples:
        prediction = nlp(example.reference.text)
        scores = prediction.cats
        truths = example.reference.cats
        val_loss += sum((scores[label] - truths[label]) ** 2 for label in truths)

    val_loss /= len(val_examples)

    print(f"Epoch {epoch} - Training Loss: {losses['textcat']}, Validation Loss: {val_loss}")

    # Early stopping
    if val_loss < best_loss:
        best_loss = val_loss
        no_improvement_epochs = 0
        # Save the best model
        nlp.to_disk("models/best_relationship_inquiry_model")
    else:
        no_improvement_epochs += 1

    if no_improvement_epochs >= patience:
        print("Early stopping due to no improvement.")
        break

# Save the final model
nlp.to_disk("models/relationship_inquiry_model")
