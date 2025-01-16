import re
import logging
from xml_source import given_xml
from translate_word import translate_string

logging.basicConfig(
    filename="app.log",  # Log file name
    level=logging.INFO,  # Log level (INFO in this case)
    format="%(message)s",  # Only log the message itself
)


class Message:
    def __init__(self, source, translation_tag, translation, full_message):
        self.source = source
        self.translation_tag = translation_tag
        self.translation = translation
        self.full_message = full_message  # Keep the original message structure

    def set_translation(self, translation):
        """Set the translation of the message and remove 'unfinished' if present."""
        self.translation = translation
        # Remove the 'unfinished' type attribute from the translation tag
        self.translation_tag = self.translation_tag.replace(' type="unfinished"', "")

    def update_full_message(self):
        """Update the full message with the new translation."""
        # Replace the old translation with the new one in the full message
        return re.sub(
            r"(<translation.*?>)(.*?)(</translation>)",
            rf"\1{self.translation}\3",
            self.full_message,
        )


class MessageIterator:
    def __init__(self, xml_string):
        self.xml_string = xml_string
        # Regular expression to find each <message> block
        message_pattern = re.compile(r"<message.*?</message>", re.DOTALL)
        # Find all <message> blocks in the XML
        self.messages = message_pattern.findall(xml_string)
        self.index = 0  # Current index of message
        self.parsed_messages = self._parse_messages(self.messages)

    def _parse_messages(self, messages):
        """Parse the raw XML messages into Message objects."""
        parsed = []
        for message in messages:
            # Extract the <source> and <translation> values
            source_match = re.search(r"<source>(.*?)</source>", message)
            translation_match = re.search(
                r"<translation(.*?)>(.*?)</translation>", message
            )

            if source_match and translation_match:
                source = source_match.group(1)
                translation = translation_match.group(2)
                translation_tag = translation_match.group(
                    1
                )  # e.g., ' type="unfinished"'

                # Create a Message object, keeping the full message for structure
                parsed.append(Message(source, translation_tag, translation, message))
        return parsed

    def __iter__(self):
        return self

    def __next__(self):
        """Return the next message in the sequence."""
        if self.index < len(self.parsed_messages):
            message = self.parsed_messages[self.index]
            self.index += 1
            return message
        else:
            raise StopIteration  # No more messages


# Example XML string

# Create an iterator from the XML
iterator = MessageIterator(given_xml)

# Store the modified messages
modified_messages = []


#########################################################
#### Magic going on below here.
#########################################################

# Iterate through messages and modify translations
for message in iterator:
    # message.set_translation("dog" if message.source == "Sun" else "cat")
    # message.source
    print("Source: ", message.source)
    translated = translate_string(message.source, "es")
    # translated = message.source

    print(message.source, " -> ", translated)
    message.set_translation(translated)
    modified_messages.append(
        message.update_full_message()
    )  # Update and store the full message
    # print(message.update_full_message())  # Print the updated message
    # print()  # For better readability

# Rebuild the XML with the modified messages
modified_xml = given_xml
for original, updated in zip(iterator.parsed_messages, modified_messages):
    modified_xml = modified_xml.replace(original.full_message, updated)

# Output the final modified XML
# print("Modified XML:")
new_modified_xml = modified_xml.replace('type="unfinished"', "")
logging.info(new_modified_xml)
