"""Transform markdown op."""

from typing import Dict, List, TypedDict


class HeaderType(TypedDict):
    """Header type as typed dict."""

    level: int
    name: str
    data: str


class LineType(TypedDict):
    """Line type as typed dict."""

    metadata: Dict[str, str]
    content: str


class SplitMarkdownOp:
    """Transform markdown class."""

    headers_to_split_on_default = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ("####", "Header 4"),
    ]

    def header_splitter(
        self,
        markdown_str: str,
        headers_to_split_on_list: List[tuple] = None,
    ):
        """Split markdown by header."""
        if headers_to_split_on_list is None:
            headers_to_split_on_list = self.headers_to_split_on_default

        # Final output
        lines_with_metadata: List[LineType] = []

        # Content and metadata of the chunk currently being processed
        current_content: List[str] = []
        current_metadata: Dict[str, str] = {}

        # Keep track of the nested header structure
        header_stack: List[HeaderType] = []
        initial_metadata: Dict[str, str] = {}

        markdown_str += "\n# end"
        lines = markdown_str.split("\n")

        for line in lines:
            stripped_line = line.strip()

            for sep, name in headers_to_split_on_list:
                # Ensure the header as metadata
                if not name:
                    break

                # Check if line starts with a header that we intend to split on
                if stripped_line.startswith(sep) and (
                    # Header with no text OR header is followed by space
                    # Both are valid conditions that sep is being used a header
                    len(stripped_line) == len(sep)
                    or stripped_line[len(sep)] == " "
                ):
                    # Get the current header level
                    current_header_level = sep.count("#")

                    # Pop out headers of lower or same level from the stack
                    while (
                        header_stack
                        and header_stack[-1]["level"] >= current_header_level
                    ):
                        # We have encountered a new header
                        # at the same or higher level
                        popped_header = header_stack.pop()
                        # Clear the metadata for the
                        # popped header in initial_metadata
                        if popped_header["name"] in initial_metadata:
                            initial_metadata.pop(popped_header["name"])

                    # Push the current header to the stack
                    header: HeaderType = {
                        "level": current_header_level,
                        "name": name,
                        "data": stripped_line[len(sep) :].strip(),
                    }
                    header_stack.append(header)
                    # Update initial_metadata with the current header
                    initial_metadata[name] = header["data"]

                    # Add the previous line to the lines_with_metadata
                    # only if current_content is not empty
                    if current_content:
                        lines_with_metadata.append(
                            {
                                "content": "\n".join(current_content),
                                "metadata": current_metadata.copy(),
                            }
                        )
                        current_content.clear()

                    break

                if stripped_line:
                    current_content.append(stripped_line)
                    current_metadata = initial_metadata.copy()

        return lines_with_metadata
