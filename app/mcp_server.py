"""
MCP Server for Requirements-to-UML Analysis
Exposes NLP extraction and Miro visualization tools to Claude
"""
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from app.file_processor import extract_text_from_file
from app.filter import segment_text
from app.model_builder import build_domain_model
from app.miro_visualizer import visualize_domain_model

import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))


# Initialize MCP server
server = Server("requirements-to-uml")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available tools that Claude can use.
    This tells Claude what capabilities are available.
    """
    return [
        Tool(
            name="analyze_requirements_text",
            description=(
                "Analyze software requirements text and extract domain model. "
                "Identifies classes, attributes, and relationships. "
                "Use this when user provides requirements as plain text."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "requirements_text": {
                        "type": "string",
                        "description": "The requirements document text to analyze"
                    },
                    "document_id": {
                        "type": "string",
                        "description": "Optional identifier for the document",
                        "default": "doc"
                    }
                },
                "required": ["requirements_text"]
            }
        ),
        Tool(
            name="analyze_requirements_file",
            description=(
                "Analyze software requirements from a file (PDF, DOCX, or TXT). "
                "Extracts text from file, then identifies classes, attributes, and relationships. "
                "Use this when user provides a file path."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the requirements file (PDF, DOCX, or TXT)"
                    },
                    "document_id": {
                        "type": "string",
                        "description": "Optional identifier for the document",
                        "default": "doc"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="create_miro_diagram",
            description=(
                "Create a UML class diagram in Miro from a domain model. "
                "Takes the domain model (classes, attributes, relations) and generates "
                "a visual UML diagram with proper layout and multiplicities. "
                "Use this after analyzing requirements to create the visualization."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "domain_model": {
                        "type": "object",
                        "description": "The domain model containing classes and relations"
                    },
                    "board_id": {
                        "type": "string",
                        "description": "Miro board ID where diagram should be created"
                    }
                },
                "required": ["domain_model", "board_id"]
            }
        ),
        Tool(
            name="analyze_and_visualize",
            description=(
                "Complete end-to-end workflow: analyze requirements file and create UML diagram. "
                "This is a convenience tool that combines analysis and visualization. "
                "Use this when user wants both analysis and diagram in one step."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to requirements file"
                    },
                    "board_id": {
                        "type": "string",
                        "description": "Miro board ID"
                    },
                    "document_id": {
                        "type": "string",
                        "description": "Optional document identifier",
                        "default": "doc"
                    }
                },
                "required": ["file_path", "board_id"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Handle tool calls from Claude.
    This is where your actual code gets executed.
    """

    try:
        if name == "analyze_requirements_text":
            # Extract arguments
            requirements_text = arguments["requirements_text"]
            doc_id = arguments.get("document_id", "doc")

            # Process with your existing pipeline
            segments = segment_text(requirements_text, doc_id=doc_id)
            model = build_domain_model(doc_id, segments)

            # Format response
            response = {
                "success": True,
                "document_id": doc_id,
                "summary": {
                    "classes": len(model["classes"]),
                    "relations": len(model["relations"]),
                    "segments_analyzed": len(model["segments"])
                },
                "domain_model": model
            }

            return [TextContent(
                type="text",
                text=f"Analysis complete!\n\n"
                     f"Found {len(model['classes'])} classes and {len(model['relations'])} relationships.\n\n"
                     f"Classes: {', '.join([c['name'] for c in model['classes']])}\n\n"
                     f"Full domain model:\n{response}"
            )]

        elif name == "analyze_requirements_file":
            # Extract arguments
            file_path = arguments["file_path"]
            doc_id = arguments.get("document_id", "doc")

            # Extract text from file
            text = extract_text_from_file(file_path)

            # Process
            segments = segment_text(text, doc_id=doc_id)
            model = build_domain_model(doc_id, segments)

            response = {
                "success": True,
                "file_path": file_path,
                "file_type": Path(file_path).suffix,
                "summary": {
                    "classes": len(model["classes"]),
                    "relations": len(model["relations"]),
                    "segments_analyzed": len(model["segments"])
                },
                "domain_model": model
            }

            return [TextContent(
                type="text",
                text=f"File analysis complete!\n\n"
                     f"File: {file_path}\n"
                     f"Found {len(model['classes'])} classes and {len(model['relations'])} relationships.\n\n"
                     f"Classes: {', '.join([c['name'] for c in model['classes']])}\n\n"
                     f"Full domain model:\n{response}"
            )]

        elif name == "create_miro_diagram":
            # Extract arguments
            domain_model = arguments["domain_model"]
            board_id = arguments["board_id"]

            # Create visualization
            result = visualize_domain_model(board_id, domain_model)

            miro_url = f"https://miro.com/app/board/{board_id}"

            return [TextContent(
                type="text",
                text=f"UML diagram created successfully!\n\n"
                     f"📊 Summary:\n"
                     f"- Classes created: {result['summary']['classes_created']}\n"
                     f"- Relations created: {result['summary']['relations_created']}\n\n"
                     f"🎨 View diagram: {miro_url}\n\n"
                     f"Full result:\n{result}"
            )]

        elif name == "analyze_and_visualize":
            # Extract arguments
            file_path = arguments["file_path"]
            board_id = arguments["board_id"]
            doc_id = arguments.get("document_id", "doc")

            # Step 1: Analyze
            text = extract_text_from_file(file_path)
            segments = segment_text(text, doc_id=doc_id)
            model = build_domain_model(doc_id, segments)

            # Step 2: Visualize
            result = visualize_domain_model(board_id, model)

            miro_url = f"https://miro.com/app/board/{board_id}"

            return [TextContent(
                type="text",
                text=f"Complete analysis and visualization done!\n\n"
                     f"📄 File: {file_path}\n"
                     f"📊 Analysis:\n"
                     f"- Classes: {len(model['classes'])}\n"
                     f"- Relations: {len(model['relations'])}\n\n"
                     f"Classes found: {', '.join([c['name'] for c in model['classes']])}\n\n"
                     f"🎨 UML Diagram: {miro_url}\n\n"
                     f"✅ Created {result['summary']['classes_created']} class boxes "
                     f"and {result['summary']['relations_created']} connectors."
            )]

        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing tool '{name}': {str(e)}\n\n"
                 f"Please check the input parameters and try again."
        )]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
