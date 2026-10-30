# Oracle Fusion Purchasing MCP Server

An MCP (Model Context Protocol) server that connects AI assistants to Oracle Fusion Cloud Procurement REST APIs.

This server provides tools to retrieve and search purchasing information, including purchase orders, PO lines, schedules, receipts, invoices, shipments, suppliers and purchase agreements.

## Features

* Retrieve individual purchase orders.
* Search multiple purchase orders using filters.
* Filter purchase orders by supplier, buyer, and other supported attributes.
* Retrieve purchase order lines.
* Retrieve purchase order schedules.
* Retrieve purchase order receipt details.
* Retrieve supplier information and supplier sites.
* Search and retrieve purchase agreements.
* Pagination support for collection-based tools.
* Asynchronous HTTP communication using HTTPX.
* Secure authentication using Oracle Fusion credentials.
* MCP integration using FastMCP.

## Requirements

* Python 3.12 or later.
* Oracle Fusion Cloud Procurement instance.
* Oracle account with appropriate REST API permissions.
* An MCP-compatible client.

## Installation

Install using uv:

```bash
uv tool install ora-fusion-purchasing-mcp
```

Alternatively, run it without a permanent installation:

```bash
uvx --from ora-fusion-purchasing-mcp ora-fusion-purchasing-mcp
```

## Configuration

The server requires Oracle Fusion connection details through environment variables.

Create a `.env` file for local development with the following configuration:

```dotenv
ORA_BASEURL=https://your-oracle-fusion-instance
ORA_USERNAME=your_username
ORA_PASSWORD=your_password

ORA_PO_ENDPOINT=/fscmRestApi/resources/11.13.18.05/purchaseOrders

ORA_PO_LIFECYCLE_ENDPOINT=/fscmRestApi/resources/11.13.18.05/purchaseOrderLifeCycleDetails
```

Replace the placeholder values with your Oracle Fusion instance details.

Never share or publish your actual `.env` file or Oracle credentials.

## MCP Client Configuration

This server uses **stdio transport**.

A generic MCP client configuration example:

```json
{
  "mcpServers": {
    "oracle-fusion-purchasing": {
      "command": "uvx",
      "args": [
        "--from",
        "oracle-mcp",
        "oracle-mcp"
      ],
      "env": {
        "ORA_BASEURL": "https://your-oracle-fusion-instance",
        "ORA_USERNAME": "your_username",
        "ORA_PASSWORD": "your_password",
        "ORA_PO_ENDPOINT": "/fscmRestApi/resources/11.13.18.05/purchaseOrders",
        "ORA_PO_LIFECYCLE_ENDPOINT": "/fscmRestApi/resources/11.13.18.05/purchaseOrderLifeCycleDetails"
      }
    }
  }
}
```

The exact configuration location depends on your MCP client.

## Available Tools

The server currently provides 12 tools covering Oracle Fusion Purchasing operations.

The available capabilities include:

| Module              | Capabilities                                    |
| ------------------- | ----------------------------------------------- |
| Purchase Orders     | Retrieve individual POs and search multiple POs |
| PO Lines            | Retrieve purchase order line details            |
| PO Schedules        | Retrieve delivery schedule information          |
| PO Receipts         | Retrieve receipt information                    |
| Suppliers           | Retrieve supplier details                       |
| Supplier Sites      | Retrieve supplier site information              |
| Purchase Agreements | Search and retrieve purchase agreements         |

Tool names, arguments, filters, and descriptions are exposed through the MCP server.

## Technology Stack

* Python
* FastMCP
* HTTPX
* python-dotenv
* Oracle Fusion Cloud REST APIs
* uv

## Logging

The application uses Python's built-in logging module.

Logs are maintained separately from MCP protocol communication.

Passwords, authentication headers, and other sensitive information should never be written to logs.

## Development Setup

Clone the repository and navigate to the project directory.

Install dependencies:

```bash
uv sync
```

Run the MCP server:

```bash
uv run oracle-mcp
```

## Building the Package

Build the Python distribution files:

```bash
uv build
```

The generated wheel and source distribution will be available inside the `dist/` directory.

## Security Considerations

* Store Oracle credentials securely.
* Never commit `.env` files.
* Use an Oracle integration account with appropriate minimum privileges.
* Avoid logging sensitive purchasing information.
* Ensure the Oracle account has access to the required REST resources.

## Disclaimer

This is an independent integration project and is not affiliated with, endorsed by, or officially supported by Oracle.

Oracle and Oracle Fusion are trademarks of Oracle and/or its affiliates.

## License

License information will be added before the public release.
