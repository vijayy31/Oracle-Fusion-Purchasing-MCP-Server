# Oracle Fusion Purchasing MCP Server

A read-Only MCP server uses STDIO transport that connects AI assistants to Oracle Fusion Cloud Procurement REST APIs.

This server provides tools to retrieve and search purchasing information, including purchase orders, PO lines, schedules, receipts, invoices, shipments, suppliers and purchase agreements.
(solely for Purchasing module)

## Features

* Retrieve individual purchase orders.
* Search multiple purchase orders using filters.
* Filter purchase orders by supplier, buyer, and other supported attributes.
* Retrieve purchase order lines.
* Retrieve purchase order schedules.
* Retrieve purchase order receipt details.
* Retrieve purchase order invoice details.
* Retrieve purchase order shipment details.
* Retrieve supplier information and supplier sites.
* Search and retrieve purchase agreements.
* Secure authentication using Oracle Fusion credentials.
* MCP integration using FastMCP.

## Requirements

* Python 3.12 or later.
* Oracle Fusion Cloud Procurement instance.
* Oracle account with appropriate REST API permissions.
* An MCP-compatible client.

## Installation

Install the Oracle Fusion Purchasing MCP server using uv:

```bash
uv tool install oracle-fusion-purchasing-mcp
```

After installation, the server can be launched using:

```bash
oracle-fusion-purchasing-mcp
```

Alternatively, run the server without permanently installing it:

```bash
uvx --from oracle-fusion-purchasing-mcp oracle-fusion-purchasing-mcp
```

## Configuration

The server requires Oracle Fusion connection details through environment variables.

Create a `.env` file for local development with the following configuration:

```dotenv
ORA_BASEURL=https://your-oracle-fusion-instance
ORA_USERNAME=your_username
ORA_PASSWORD=your_password
ORA_API_VERSION=11.13.18.05
```

Replace the placeholder values with your Oracle Fusion instance details.

Never share or publish your actual `.env` file or Oracle credentials.

## MCP Client Configuration

This server uses **stdio transport**.

A generic MCP client configuration example:

Add the following configuration to your MCP host configuration file (Claude Desktop, VS Code, or another compatible MCP client).

```json

Using uvx

{
 "mcpServers": {
   "oracle-fusion-purchasing": {
     "command": "uvx",
     "args": [
       "--from",
       "oracle-fusion-purchasing-mcp",
       "oracle-fusion-purchasing-mcp"
     ],
     "env": {
       "ORA_BASEURL": "YOUR_ORACLE_BASE_URL",
       "ORA_USERNAME": "YOUR_ORACLE_USERNAME",
       "ORA_PASSWORD": "YOUR_ORACLE_PASSWORD"
     }
   }
 }
}
```

Replace the placeholder values with your Oracle Fusion connection details.

**Note: Ensure uv is installed and available in your system PATH.**

After saving the configuration, restart your MCP host to connect to the Oracle Fusion Purchasing MCP Server.
The exact configuration location depends on your MCP client.

## Available Tools

The server currently provides the following 12 tools covering Oracle Fusion Purchasing
operations:

### Purchase Orders

* `get_one_purchase_order_details` - Retrieve one purchase order by PO number.
* `get_multiple_purchase_orders_details` - Search purchase orders using optional filters.
* `get_purchase_order_line_details` - Retrieve the lines belonging to a purchase order.
* `get_purchase_order_schedule_details` - Retrieve delivery schedules for a purchase order.
* `get_po_receipt_details` - Retrieve receipt details for a purchase order.
* `get_po_invoice_details` - Retrieve invoice details for a purchase order.
* `get_po_shipment_details` - Retrieve shipment details for a purchase order.

### Suppliers

* `get_supplier_details` - Retrieve supplier details by supplier name.
* `get_supplier_sites_details` - Retrieve sites belonging to a supplier.

### Purchase Agreements

* `get_one_purchase_agreement_details` - Retrieve one purchase agreement by agreement number.
* `get_multiple_purchase_agreement_details` - Search purchase agreements using optional filters.
* `get_purchase_agreement_lines_details` - Retrieve the lines belonging to a purchase agreement.

The available capabilities include:

| Module              | Capabilities                                    |
| ------------------- | ----------------------------------------------- |
| Purchase Orders     | Retrieve individual POs and search multiple POs |
| PO Lines            | Retrieve purchase order line details            |
| PO Schedules        | Retrieve delivery schedule information          |
| PO Receipts         | Retrieve receipt information                    |
| PO Invoices         | Retrieve invoice information                   |
| PO Shipments        | Retrieve shipment information                  |
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

Logs are maintained separately from MCP stdio protocol communication.

Log files are stored in the user's home directory:

- Windows: `%USERPROFILE%\.oracle_mcp\oracle_mcp.log`
- Linux/macOS: `~/.oracle_mcp/oracle_mcp.log`


## Development Setup

Clone the repository and navigate to the project directory.

Install dependencies:

```bash
uv sync
```

Run the MCP server:

```bash
uv run oracle-fusion-purchasing-mcp
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

## Author
Vijay


## License
This project is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.
